import json
from backend.services.gemini_client import get_ai_response

_FALLBACK = [
    {"task_name": "Practice DSA", "task_type": "placement", "duration_hours": 1.0, "priority": "high", "notes": ""},
    {"task_name": "Core Subject Revision", "task_type": "academic", "duration_hours": 1.0, "priority": "medium", "notes": ""},
]

def generate_daily_schedule(user: dict, target_date: str) -> list[dict]:
    hours = user.get("available_hours", 4)
    goal = user.get("placement_goal", "")
    skills = user.get("skills", [])
    subjects = user.get("subjects", [])

    # Short prompt to minimize token usage
    prompt = f"""You are a student planner. Return ONLY a JSON array of tasks.
Date: {target_date}. Total hours available: {hours}.
Goal: {goal or "general"}.
Subjects: {", ".join(subjects) if subjects else "general"}.
Skills: {", ".join(skills) if skills else "none"}.
Rules: total duration <= {hours}h, include 1 break, mix academic+placement.
Each task: {{"task_name":"...","task_type":"academic|placement|break","duration_hours":0.5,"priority":"high|medium|low","notes":"..."}}"""

    result = get_ai_response(prompt)
    if result and isinstance(result, list) and len(result) > 0:
        return result

    # Deterministic fallback — never crashes
    return [
        {
            "task_name": f"Study {subjects[0]}" if subjects else "Core Revision",
            "task_type": "academic",
            "duration_hours": min(2, hours * 0.5),
            "priority": "high",
            "notes": "Fallback task"
        },
        {
            "task_name": "DSA Practice",
            "task_type": "placement",
            "duration_hours": min(1, hours * 0.25),
            "priority": "high" if goal else "low",
            "notes": ""
        }
    ]
