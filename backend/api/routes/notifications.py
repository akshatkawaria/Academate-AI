from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.models import User, Schedule, Progress, Notification
from backend.models.schemas import NotificationResponse
from backend.agents.notification_agent import generate_notifications
from backend.agents.decision_agent import decide_mode, detect_urgent_tasks

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

@router.post("/{user_id}/generate")
def generate_user_notifications(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    schedules = db.query(Schedule).filter(Schedule.user_id == user_id).all()
    progress = db.query(Progress).filter(Progress.user_id == user_id).order_by(Progress.date).all()

    sched_dicts = [{"task_name": s.task_name, "date": s.date, "status": s.status, "priority": s.priority} for s in schedules]
    prog_dicts = [{"date": p.date, "study_hours": p.study_hours, "completed_tasks": p.completed_tasks,
                   "missed_tasks": p.missed_tasks, "productivity_score": p.productivity_score} for p in progress]
    user_dict = {"name": user.name, "placement_goal": user.placement_goal, "available_hours": user.available_hours}

    notif_list = generate_notifications(user_dict, sched_dicts, prog_dicts)

    # Clear old unread notifs and insert new ones
    db.query(Notification).filter(Notification.user_id == user_id, Notification.is_read == False).delete()
    created = []
    for n in notif_list:
        notif = Notification(user_id=user_id, title=n["title"], message=n["message"], notif_type=n["notif_type"])
        db.add(notif)
        created.append(notif)
    db.commit()
    for n in created:
        db.refresh(n)
    return created

@router.get("/{user_id}", response_model=list[NotificationResponse])
def get_notifications(user_id: str, db: Session = Depends(get_db)):
    return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()

@router.patch("/{notif_id}/read")
def mark_read(notif_id: str, db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found.")
    notif.is_read = True
    db.commit()
    return {"message": "Marked as read."}

@router.get("/{user_id}/adaptive")
def get_adaptive_plan(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    progress = db.query(Progress).filter(Progress.user_id == user_id).order_by(Progress.date).all()
    schedules = db.query(Schedule).filter(Schedule.user_id == user_id).all()
    prog_dicts = [{"date": p.date, "study_hours": p.study_hours, "completed_tasks": p.completed_tasks,
                   "missed_tasks": p.missed_tasks, "productivity_score": p.productivity_score} for p in progress]
    sched_dicts = [{"task_name": s.task_name, "date": s.date, "status": s.status, "priority": s.priority} for s in schedules]
    from backend.agents.progress_agent import get_weekly_summary
    summary = get_weekly_summary(prog_dicts[-7:])
    user_dict = {"placement_goal": user.placement_goal or "", "available_hours": user.available_hours}
    decision = decide_mode(summary, user_dict)
    from datetime import date
    urgent = detect_urgent_tasks(sched_dicts, date.today().isoformat())
    return {"decision": decision, "urgent_tasks": urgent, "summary": summary}
