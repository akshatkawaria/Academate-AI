"""
Notification Agent — Generates smart alerts and reminders for the student.
"""
from datetime import datetime, date
from typing import List


def generate_notifications(user: dict, schedules: list, progress_records: list) -> List[dict]:
    """Build a list of notification dicts based on current state."""
    notifs = []
    today = date.today().isoformat()

    # Welcome notification for new users
    notifs.append({
        "title": "👋 Welcome to AcadMate AI!",
        "message": f"Hi {user.get('name', 'Student')}! Your AI co-pilot is ready. Start by generating today's schedule.",
        "notif_type": "tip"
    })

    # Overdue tasks
    overdue = [s for s in schedules if s.get("status") == "pending" and s.get("date") < today]
    if overdue:
        notifs.append({
            "title": "⚡ Overdue Tasks Detected",
            "message": f"You have {len(overdue)} overdue task(s). Reschedule or mark them as missed to keep your tracker clean.",
            "notif_type": "alert"
        })

    # Today's tasks reminder
    today_tasks = [s for s in schedules if s.get("date") == today and s.get("status") == "pending"]
    if today_tasks:
        notifs.append({
            "title": "📅 Today's Schedule Ready",
            "message": f"You have {len(today_tasks)} tasks planned for today. Stay focused and mark them complete as you go!",
            "notif_type": "reminder"
        })

    # Low productivity warning
    if progress_records:
        latest = progress_records[-1]
        score = latest.get("productivity_score", 0)
        if score < 40:
            notifs.append({
                "title": "📉 Productivity Alert",
                "message": f"Your productivity score is {score}%. Don't worry — let's recalibrate your schedule for a better tomorrow.",
                "notif_type": "alert"
            })
        elif score >= 80:
            notifs.append({
                "title": "🔥 You're on Fire!",
                "message": f"Incredible! Productivity score of {score}%. Keep this energy going!",
                "notif_type": "tip"
            })

    # Study hours reminder
    available = user.get("available_hours", 4)
    notifs.append({
        "title": "⏰ Daily Study Reminder",
        "message": f"Remember to log your {available} study hours today. Consistency is the key to success!",
        "notif_type": "reminder"
    })

    # Placement tip
    goal = user.get("placement_goal", "")
    if goal:
        notifs.append({
            "title": "🎯 Placement Tip of the Day",
            "message": f"Working towards {goal}? Solve at least 2 LeetCode problems today and read one system design article.",
            "notif_type": "tip"
        })

    return notifs
