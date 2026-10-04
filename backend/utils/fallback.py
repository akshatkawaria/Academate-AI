def get_planner_fallback() -> list[dict]:
    return [
        {
            "task_name": "Practice DSA",
            "task_type": "placement",
            "duration_hours": 1.0,
            "priority": "high",
            "notes": "Deterministic fallback task."
        }
    ]

def get_progress_fallback(progress_records: list) -> dict:
    completed = sum(r.get("completed_tasks", 0) for r in progress_records)
    missed = sum(r.get("missed_tasks", 0) for r in progress_records)
    total = completed + missed
    rate = int((completed / total * 100)) if total > 0 else 0
    return {
        "completion_rate": rate,
        "weekly_streak": 0,
        "consistency": "fair" if rate >= 50 else "needs improvement"
    }

def get_placement_fallback() -> dict:
    return {
        "readiness_score": 50,
        "missing_skills": ["Review Core Concepts"],
        "recommended_focus": ["DSA"]
    }

def get_opportunity_fallback() -> dict:
    return {
        "opportunities": [
            {
                "type": "hackathon",
                "title": "General College Hackathon"
            }
        ]
    }
