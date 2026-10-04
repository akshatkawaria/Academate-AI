"""
Decision Agent — Analyzes performance and adaptively adjusts scheduling mode.
"""
from typing import Optional


def decide_mode(summary: dict, user: dict) -> dict:
    # Use completion_rate (0–100) as proxy for productivity
    avg_score = summary.get("completion_rate", summary.get("avg_productivity", 50))
    missed = summary.get("total_missed", 0)
    completed = summary.get("total_completed", 0)
    consistency = summary.get("consistency", "fair")
    goal = user.get("placement_goal", "").lower()
    hours = user.get("available_hours", 4)

    mode = "balanced"
    actions = []
    priority_focus = []

    # Placement season logic (if goal mentions companies)
    if any(kw in goal for kw in ["google", "amazon", "microsoft", "faang", "product", "sde"]):
        mode = "placement"
        priority_focus.append("DSA practice (LeetCode medium/hard)")
        priority_focus.append("System design concepts")
        actions.append("🎯 High-target company detected — boosting placement focus.")

    # Low productivity
    if avg_score < 40:
        actions.append("⚠️ Low productivity detected. Reducing daily task count by 20%.")
        hours = max(hours - 1, 2)
    elif avg_score > 80:
        actions.append("🚀 High productivity! Slightly increasing challenge level.")

    # High missed tasks
    if missed > completed and completed + missed > 0:
        actions.append("📋 Too many missed tasks. Simplifying schedule structure.")
        mode = "academic"  # Focus on fewer, more manageable tasks

    # Declining consistency
    if consistency == "poor" or consistency == "needs improvement":
        actions.append("📉 Consistency is low. Adding more break time and review sessions.")

    # Build recommendation
    if mode == "placement":
        priority_focus = priority_focus or ["LeetCode DSA", "Mock interviews", "Resume polish"]
    elif mode == "academic":
        priority_focus = ["Exam-focused revision", "Assignment deadlines", "Concept clearing"]
    else:
        priority_focus = ["Balanced study + DSA", "Project work", "Weekly self-assessment"]

    return {
        "recommended_mode": mode,
        "adjusted_hours": hours,
        "actions_taken": actions,
        "priority_focus": priority_focus,
        "explanation": _build_explanation(mode, avg_score, consistency)
    }


def _build_explanation(mode: str, score: float, consistency: str) -> str:
    if mode == "placement":
        return f"Placement focus active. Score: {score}%, consistency: {consistency}."
    elif mode == "academic":
        return f"Academic tasks prioritized. Score: {score}%, consistency: {consistency}."
    else:
        return f"Balanced approach. Score: {score}%, consistency: {consistency}."


def detect_urgent_tasks(schedules: list, today: str) -> list:
    """Find overdue or high-priority tasks."""
    urgent = []
    for task in schedules:
        if task.get("status") == "pending" and task.get("date") < today:
            urgent.append({
                "task_name": task.get("task_name"),
                "date": task.get("date"),
                "priority": task.get("priority"),
                "message": f"⚡ Overdue: '{task.get('task_name')}' was scheduled for {task.get('date')}"
            })
        elif task.get("priority") == "high" and task.get("status") == "pending":
            urgent.append({
                "task_name": task.get("task_name"),
                "date": task.get("date"),
                "priority": "high",
                "message": f"🔴 High priority pending: '{task.get('task_name')}'"
            })
    return urgent
