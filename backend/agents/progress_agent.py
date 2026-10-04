"""
Progress Agent — RULE-BASED ONLY. No AI calls.
Computes analytics deterministically from DB records.
"""
from typing import List


def compute_productivity_score(study_hours: float, completed: int, missed: int, target_hours: float = 4.0) -> float:
    if completed + missed == 0:
        task_rate = 0.0
    else:
        task_rate = completed / (completed + missed)
    hour_rate = min(study_hours / max(target_hours, 1), 1.0)
    return round((task_rate * 0.6 + hour_rate * 0.4) * 100, 1)


def get_weekly_summary(records: List[dict]) -> dict:
    if not records:
        return {"completion_rate": 0, "weekly_streak": 0, "consistency": "poor", "avg_hours": 0}

    completed = sum(r.get("completed_tasks", 0) for r in records)
    missed = sum(r.get("missed_tasks", 0) for r in records)
    total = completed + missed
    rate = int(completed / total * 100) if total > 0 else 0

    # Streak — consecutive days with score >= 50
    streak = 0
    for r in reversed(records):
        if r.get("productivity_score", 0) >= 50:
            streak += 1
        else:
            break

    avg_hours = round(sum(r.get("study_hours", 0) for r in records) / len(records), 1)
    consistency = "excellent" if rate >= 80 else "good" if rate >= 60 else "fair" if rate >= 40 else "poor"

    return {
        "completion_rate": rate,
        "weekly_streak": streak,
        "consistency": consistency,
        "avg_hours": avg_hours,
        "total_completed": completed,
        "total_missed": missed,
    }
