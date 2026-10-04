from datetime import datetime, timedelta
import re

def parse_time(time_str: str) -> datetime:
    """Parses a time string like '09:00 AM' or '11:00 PM' into a datetime object for today."""
    try:
        dt = datetime.strptime(time_str.strip(), "%I:%M %p")
        now = datetime.now()
        return dt.replace(year=now.year, month=now.month, day=now.day)
    except ValueError:
        # Fallback if unparseable
        return datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)

def format_time(dt: datetime) -> str:
    """Formats a datetime object back into '09:00 AM'."""
    return dt.strftime("%I:%M %p")

def build_core_schedule(user_data: dict) -> dict:
    """
    The new backend scheduling engine.
    Calculates weights, allocates hours, selects tasks, and generates time slots dynamically.
    """
    # 1. Analyze Priorities & Weights
    academic_weight = 50
    placement_weight = 50
    reason_parts = []
    
    exams = user_data.get("upcoming_exams", [])
    exams_near = len(exams) > 0 or user_data.get("exam_dates", "") != ""
    placement_priority = user_data.get("placement_priority", "medium").lower()
    burnout = user_data.get("burnout_level", "low").lower()
    
    if exams_near:
        academic_weight = 70
        placement_weight = 30
        reason_parts.append("Exams are approaching, prioritizing academics.")
    elif placement_priority == "high":
        academic_weight = 40
        placement_weight = 60
        reason_parts.append("High placement priority requires DSA and project focus.")
    else:
        reason_parts.append("Balanced normal schedule.")
        
    if burnout == "high":
        reason_parts.append("Burnout is high, reducing intensity and adding breaks.")
        
    # 2. Allocate Hours
    total_hours = user_data.get("available_study_hours", 4)
    if burnout == "high":
        total_hours = max(2, total_hours - 2)
        
    academic_hours = total_hours * (academic_weight / 100.0)
    placement_hours = total_hours * (placement_weight / 100.0)
    
    # 3. Task Selection
    tasks_to_schedule = []
    
    # Academic tasks
    weak_subjects = user_data.get("weak_subjects", [])
    subjects = user_data.get("subjects", [])
    
    if weak_subjects:
        tasks_to_schedule.append({
            "name": f"Revise {weak_subjects[0]} (Weak Subject)",
            "type": "academic",
            "priority": "high",
            "hours": min(1.5, academic_hours),
            "reason": "Prioritizing weak subject to improve fundamentals."
        })
        academic_hours -= min(1.5, academic_hours)
        
    if exams_near and academic_hours > 0:
        target = exams[0] if exams else (subjects[0] if subjects else "Core Subject")
        tasks_to_schedule.append({
            "name": f"Exam Prep: {target}",
            "type": "academic",
            "priority": "high",
            "hours": min(2.0, academic_hours),
            "reason": "Upcoming exam preparation."
        })
    elif academic_hours > 0 and subjects:
        tasks_to_schedule.append({
            "name": f"Study {subjects[0]}",
            "type": "academic",
            "priority": "medium",
            "hours": academic_hours,
            "reason": "Regular coursework progression."
        })

    # Placement tasks
    goal = user_data.get("placement_goal", "Placement Prep")
    domain = user_data.get("interested_domain", "DSA")
    
    if placement_hours > 0:
        tasks_to_schedule.append({
            "name": f"DSA Practice ({goal})",
            "type": "placement",
            "priority": "high" if placement_priority == "high" else "medium",
            "hours": min(1.5, placement_hours),
            "reason": "Essential problem-solving skills for interviews."
        })
        placement_hours -= min(1.5, placement_hours)
        
    if placement_hours > 0:
        tasks_to_schedule.append({
            "name": f"Project Work: {domain}",
            "type": "placement",
            "priority": "medium",
            "hours": placement_hours,
            "reason": "Building practical skills and portfolio."
        })
        
    # Filter out empty tasks
    tasks_to_schedule = [t for t in tasks_to_schedule if t["hours"] > 0]
    
    # 4. Generate Time Slots
    preferred_time = user_data.get("preferred_study_time", "Morning").lower()
    
    if "morning" in preferred_time:
        current_time = parse_time(user_data.get("wake_up_time", "08:00 AM")) + timedelta(hours=1)
    elif "night" in preferred_time:
        current_time = parse_time("08:00 PM")
    else:
        current_time = parse_time("02:00 PM")
        
    schedule = []
    
    for t in tasks_to_schedule:
        task_minutes = int(t["hours"] * 60)
        end_time = current_time + timedelta(minutes=task_minutes)
        
        schedule.append({
            "start_time": format_time(current_time),
            "end_time": format_time(end_time),
            "task_name": t["name"],
            "task_type": t["type"],
            "priority": t["priority"],
            "reason": t["reason"]
        })
        
        # Add a 15 min break after each task (30 min if burnout is high)
        break_duration = 30 if burnout == "high" else 15
        current_time = end_time + timedelta(minutes=break_duration)
        
    return {
        "plan_summary": {
            "academic_focus": academic_weight,
            "placement_focus": placement_weight,
            "reason": " ".join(reason_parts)
        },
        "schedule": schedule,
        "productivity_advice": [
            f"Since your biggest distraction is {user_data.get('biggest_distraction', 'your phone')}, try the Pomodoro technique.",
            f"Burnout is {burnout}, so stick strictly to the scheduled breaks."
        ]
    }
