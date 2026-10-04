from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from backend.database.database import get_db
from backend.database.models import User, Schedule
from backend.models.schemas import ScheduleCreate, ScheduleUpdate, ScheduleResponse, GenerateScheduleRequest
router = APIRouter(prefix="/api/schedule", tags=["Schedule"])

from backend.services.orchestrator import orchestrator

@router.get("/generate/{user_id}", response_model=list[ScheduleResponse])
def generate_schedule_get(user_id: str, date: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    db.query(Schedule).filter(
        Schedule.user_id == user_id,
        Schedule.date == date,
        Schedule.status == "pending"
    ).delete()

    user_dict = {
        "name": user.name,
        "subjects": user.subjects or [],
        "placement_goal": user.placement_goal or "",
        "available_hours": user.available_hours or 4,
        "skills": user.skills or []
    }
    
    tasks = orchestrator.run_planner(user_dict, date)

    created = []
    for t in tasks:
        task = Schedule(
            user_id=user_id,
            date=date,
            task_name=t.get("task_name", "Task"),
            task_type=t.get("task_type", "academic"),
            duration_hours=float(t.get("duration_hours", 1.0)),
            priority=t.get("priority", "medium"),
            notes=t.get("notes", ""),
            status="pending"
        )
        db.add(task)
        created.append(task)
    db.commit()
    for t in created:
        db.refresh(t)
    return created

@router.post("/generate", response_model=list[ScheduleResponse])
def generate_schedule(req: GenerateScheduleRequest, db: Session = Depends(get_db)):
    return generate_schedule_get(req.user_id, req.date, db)



@router.get("/{user_id}", response_model=list[ScheduleResponse])
def get_schedule(user_id: str, date_filter: str = None, db: Session = Depends(get_db)):
    query = db.query(Schedule).filter(Schedule.user_id == user_id)
    if date_filter:
        query = query.filter(Schedule.date == date_filter)
    return query.order_by(Schedule.date, Schedule.created_at).all()

@router.patch("/{task_id}", response_model=ScheduleResponse)
def update_task(task_id: str, data: ScheduleUpdate, db: Session = Depends(get_db)):
    task = db.query(Schedule).filter(Schedule.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Schedule).filter(Schedule.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    db.delete(task)
    db.commit()
    return {"message": "Task deleted."}
