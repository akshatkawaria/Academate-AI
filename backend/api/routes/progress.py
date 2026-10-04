from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date as dt_date
from backend.database.database import get_db
from backend.database.models import User, Progress, Schedule
from backend.models.schemas import ProgressCreate, ProgressResponse
from backend.agents.progress_agent import compute_productivity_score
from backend.agents.progress_analytics import build_full_analytics

router = APIRouter(prefix="/api/progress", tags=["Progress"])


@router.get("/analytics/{user_id}")
def get_analytics(user_id: str, db: Session = Depends(get_db)):
    """Full adaptive analytics — all scores, burnout, behavior, insights, planner adaptation."""
    records = db.query(Progress).filter(Progress.user_id == user_id).order_by(Progress.date).all()
    schedule_records = db.query(Schedule).filter(Schedule.user_id == user_id).order_by(Schedule.date).all()

    rec_dicts = [{"date": r.date, "study_hours": r.study_hours, "completed_tasks": r.completed_tasks,
                  "missed_tasks": r.missed_tasks, "productivity_score": r.productivity_score} for r in records]
    sched_dicts = [{"date": s.date, "task_name": s.task_name, "task_type": s.task_type,
                    "status": s.status, "start_time": s.notes or "09:00 AM"} for s in schedule_records]

    return build_full_analytics(rec_dicts, sched_dicts)


@router.get("/today-tasks/{user_id}")
def get_today_tasks(user_id: str, db: Session = Depends(get_db)):
    """
    Returns today's AI Planner tasks from the Schedule table.
    This feeds the 'Today's AI Tasks' checklist on the Progress page.
    """
    today = str(dt_date.today())
    tasks = db.query(Schedule).filter(
        Schedule.user_id == user_id,
        Schedule.date == today
    ).order_by(Schedule.created_at).all()

    return [
        {
            "id": t.id,
            "task_name": t.task_name,
            "task_type": t.task_type,
            "priority": t.priority,
            "duration_hours": t.duration_hours,
            "status": t.status,
            "notes": t.notes,
        }
        for t in tasks
    ]


@router.post("/auto-log/{user_id}")
def auto_log_from_tasks(user_id: str, db: Session = Depends(get_db)):
    """
    Auto-computes today's progress from actual task completions in the Schedule table.
    Eliminates the need for a manual 'Log Session' form.
    Calling this endpoint triggers a full re-sync of today's Progress record.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    today = str(dt_date.today())
    tasks = db.query(Schedule).filter(
        Schedule.user_id == user_id,
        Schedule.date == today
    ).all()

    if not tasks:
        return {"message": "No AI tasks found for today. Generate a plan from the AI Planner first.", "synced": False}

    completed = sum(1 for t in tasks if t.status == "completed")
    missed = len(tasks) - completed
    # Estimate study hours from completed task durations
    study_hours = round(sum(t.duration_hours for t in tasks if t.status == "completed"), 1)

    score = compute_productivity_score(study_hours, completed, missed, user.available_hours or 4.0)

    existing = db.query(Progress).filter(Progress.user_id == user_id, Progress.date == today).first()
    if existing:
        existing.study_hours = study_hours
        existing.completed_tasks = completed
        existing.missed_tasks = missed
        existing.productivity_score = score
        existing.notes = "auto-synced"
        db.commit()
        db.refresh(existing)
    else:
        record = Progress(user_id=user_id, date=today, study_hours=study_hours,
                         completed_tasks=completed, missed_tasks=missed,
                         productivity_score=score, notes="auto-synced")
        db.add(record)
        db.commit()
        db.refresh(record)

    return {
        "message": f"Auto-synced: {completed} completed, {missed} missed, {study_hours}h studied, score={score}",
        "synced": True,
        "completed": completed,
        "missed": missed,
        "study_hours": study_hours,
        "score": score
    }


@router.post("/{user_id}", response_model=ProgressResponse)
def log_progress(user_id: str, data: ProgressCreate, db: Session = Depends(get_db)):
    """Log or update a daily study session."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    score = compute_productivity_score(
        data.study_hours, data.completed_tasks, data.missed_tasks,
        user.available_hours or 4.0
    )

    existing = db.query(Progress).filter(
        Progress.user_id == user_id, Progress.date == data.date
    ).first()

    if existing:
        existing.study_hours = data.study_hours
        existing.completed_tasks = data.completed_tasks
        existing.missed_tasks = data.missed_tasks
        existing.productivity_score = score
        existing.notes = data.notes or ""
        db.commit()
        db.refresh(existing)
        return existing

    record = Progress(
        user_id=user_id,
        date=data.date,
        study_hours=data.study_hours,
        completed_tasks=data.completed_tasks,
        missed_tasks=data.missed_tasks,
        productivity_score=score,
        notes=data.notes or ""
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{user_id}", response_model=list[ProgressResponse])
def get_progress(user_id: str, days: int = 30, db: Session = Depends(get_db)):
    """Returns raw progress history (most recent `days` records)."""
    records = db.query(Progress).filter(
        Progress.user_id == user_id
    ).order_by(Progress.date.desc()).limit(days).all()
    return list(reversed(records))
