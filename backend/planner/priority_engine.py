"""
Priority Engine — Analyzes user profile and computes weights/constraints.
RESPONSIBILITY: Understand the student. Output WHAT matters, not WHEN.
"""
from datetime import datetime

def analyze(user_data: dict) -> dict:
    """
    Returns a priority analysis dict that drives all downstream decisions.
    """
    # ── Defaults ─────────────────────────────────────────────────────────────
    academic_w = 50
    placement_w = 50
    reason_parts = []
    tags = []

    # ── Exam Proximity ────────────────────────────────────────────────────────
    exam_dates_str = user_data.get("exam_dates", "")
    exams_near = False
    days_to_exam = None

    if exam_dates_str:
        try:
            first_date = exam_dates_str.strip().split(",")[0].strip()
            exam_dt = datetime.strptime(first_date, "%Y-%m-%d")
            days_to_exam = (exam_dt.date() - datetime.now().date()).days
            if 0 <= days_to_exam <= 5:
                exams_near = True
        except ValueError:
            pass

    upcoming_exams = user_data.get("upcoming_exams", [])
    if upcoming_exams and not exams_near:
        exams_near = True  # No date provided but exams listed — treat as near

    if exams_near:
        gap = f" in {days_to_exam} day(s)" if days_to_exam is not None else ""
        academic_w = 70
        placement_w = 30
        reason_parts.append(f"Exams are near{gap}, increasing academic focus.")
        tags.append("exam_mode")

    # ── Placement Priority ────────────────────────────────────────────────────
    placement_priority = user_data.get("placement_priority", "medium").lower()
    if placement_priority == "high" and not exams_near:
        placement_w = 60
        academic_w = 40
        reason_parts.append("High placement priority — increasing DSA and project time.")
        tags.append("placement_mode")
    elif placement_priority == "low":
        academic_w = min(90, academic_w + 10)
        placement_w = max(10, placement_w - 10)
        reason_parts.append("Low placement priority — maintaining academic focus.")

    # ── Burnout ───────────────────────────────────────────────────────────────
    burnout = user_data.get("burnout_level", "low").lower()
    total_hours = int(user_data.get("available_study_hours", 4))

    if burnout == "high":
        total_hours = max(2, total_hours - 2)
        reason_parts.append("High burnout detected — workload reduced and breaks increased.")
        tags.append("high_burnout")
    elif burnout == "medium":
        total_hours = max(2, total_hours - 1)
        tags.append("medium_burnout")

    # ── Consistency ───────────────────────────────────────────────────────────
    consistency = user_data.get("consistency_level", "medium").lower()
    max_task_duration = 2.0  # hours

    if consistency == "low" or burnout == "high":
        max_task_duration = 1.0
        reason_parts.append("Low consistency — generating smaller, achievable tasks.")
        tags.append("low_consistency")
    elif consistency == "high":
        max_task_duration = 2.0
        tags.append("high_consistency")

    # ── Skill Level ───────────────────────────────────────────────────────────
    skill = user_data.get("current_skill_level", "Intermediate").lower()
    tags.append(f"skill_{skill.replace(' ', '_')}")

    # ── Stress ────────────────────────────────────────────────────────────────
    stress = user_data.get("stress_level", "medium").lower()
    if stress == "high":
        max_task_duration = min(max_task_duration, 1.0)
        tags.append("high_stress")

    # ── Final Bounds ──────────────────────────────────────────────────────────
    academic_w = max(10, min(90, academic_w))
    placement_w = 100 - academic_w

    if not reason_parts:
        reason_parts.append("Balanced schedule for steady progress in academics and placement.")

    return {
        "academic_weight": academic_w,
        "placement_weight": placement_w,
        "adjusted_hours": total_hours,
        "max_task_duration": max_task_duration,
        "burnout": burnout,
        "consistency": consistency,
        "skill": skill,
        "exams_near": exams_near,
        "placement_priority": placement_priority,
        "reason": " ".join(reason_parts),
        "tags": tags,
    }
