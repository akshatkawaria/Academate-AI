"""
Scheduler Engine — Decides WHEN tasks happen.
RESPONSIBILITY: Pure time allocation. Receives tasks, produces timetable.
No planning logic. No task selection. Only time management.
"""
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def _parse_time(time_str: str) -> datetime:
    """Parses '07:00 AM', '09:00', etc. into a datetime for today."""
    now = datetime.now()
    for fmt in ("%I:%M %p", "%I:%M%p", "%H:%M"):
        try:
            dt = datetime.strptime(time_str.strip(), fmt)
            return dt.replace(year=now.year, month=now.month, day=now.day)
        except ValueError:
            continue
    # Hard fallback if unparseable
    return now.replace(hour=9, minute=0, second=0, microsecond=0)


def _fmt(dt: datetime) -> str:
    return dt.strftime("%I:%M %p")


def _get_session_start(user_data: dict) -> datetime:
    """Determines the first study slot based on preferred study time, wake-up time, and AI adaptations."""
    preferred = user_data.get("preferred_study_time", "Morning").lower()
    wake_str = user_data.get("wake_up_time", "07:00 AM")
    wake_dt = _parse_time(wake_str)
    
    # Adaptive override from progress analytics
    adapt = user_data.get("_progress_analytics", {}).get("planner_adaptation", {}).get("adjustments", {})
    if adapt.get("shift_schedule_to_evening"):
        preferred = "evening"

    if "morning" in preferred:
        # Start 30–60 min after waking
        return wake_dt + timedelta(minutes=45)
    elif "afternoon" in preferred:
        return wake_dt.replace(hour=14, minute=0)
    elif "night" in preferred or "evening" in preferred:
        return wake_dt.replace(hour=18, minute=0)
    else:
        return wake_dt + timedelta(minutes=45)


def _break_duration(burnout: str) -> int:
    """Returns break time in minutes based on burnout level."""
    return {
        "high": 30,
        "medium": 20,
        "low": 15
    }.get(burnout, 15)


def _focus_block_limit(user_data: dict, burnout: str) -> float:
    """Returns max continuous study minutes before a mandatory break."""
    focus = user_data.get("focus_capacity", "60 mins").lower()
    if "30" in focus:
        cap = 30
    elif "45" in focus:
        cap = 45
    elif "90" in focus or "1.5" in focus:
        cap = 90
    else:
        cap = 60  # default

    if burnout == "high":
        cap = min(cap, 45)

    return cap


def build_timetable(tasks: list, user_data: dict, analysis: dict) -> list:
    """
    Core scheduler: receives selected tasks, allocates real time slots.
    
    Scheduling rules:
    - High priority tasks go first (peak energy)
    - Add breaks between sessions
    - Insert a long break every 90 min of accumulated work
    - Respect focus capacity
    - Respect sleep time
    """
    if not tasks:
        return []

    burnout = analysis.get("burnout", "low")
    current_time = _get_session_start(user_data)
    break_dur = _break_duration(burnout)
    focus_cap_min = _focus_block_limit(user_data, burnout)
    
    # Parse sleep time to avoid scheduling beyond it
    sleep_str = user_data.get("sleep_time", "11:00 PM")
    sleep_dt = _parse_time(sleep_str)
    if sleep_dt < current_time:
        sleep_dt += timedelta(hours=24)

    # Sort: high priority first, then by type (academic before placement during exam mode)
    priority_order = {"high": 0, "medium": 1, "low": 2}
    sorted_tasks = sorted(tasks, key=lambda t: (
        priority_order.get(t["priority"], 1),
        0 if t["type"] == "academic" and analysis.get("exams_near") else 1
    ))

    scheduled = []
    accumulated_work_min = 0

    for task in sorted_tasks:
        task_total_min = int(task["duration_hours"] * 60)

        # Split long tasks into focus blocks with breaks inside
        remaining_min = task_total_min
        first_slice = True

        while remaining_min > 0:
            # Check we haven't hit sleep time
            if current_time >= sleep_dt - timedelta(minutes=30):
                logger.info("Reached sleep boundary, stopping scheduling.")
                break

            # Mandatory long break after accumulated 90 min
            if accumulated_work_min >= 90:
                current_time += timedelta(minutes=30)  # 30-min long break
                accumulated_work_min = 0
                logger.info("Inserted 30-min long break after 90 min of work.")

            slice_min = min(remaining_min, focus_cap_min)
            end_time = current_time + timedelta(minutes=slice_min)

            task_name = task["name"]
            if not first_slice:
                task_name += " (continued)"

            scheduled.append({
                "start_time": _fmt(current_time),
                "end_time": _fmt(end_time),
                "task_name": task_name,
                "task_type": task["type"],
                "priority": task["priority"],
                "reason": task["reason"]
            })

            accumulated_work_min += slice_min
            remaining_min -= slice_min
            current_time = end_time

            if remaining_min > 0:
                # Break between slices of same task
                current_time += timedelta(minutes=break_dur)
                accumulated_work_min = 0  # Reset after break

            first_slice = False

        # Short break after each task (unless we're about to do a long break)
        if accumulated_work_min < 90 and accumulated_work_min > 0:
            current_time += timedelta(minutes=break_dur)

    logger.info(f"Scheduler produced {len(scheduled)} time slots.")
    return scheduled
