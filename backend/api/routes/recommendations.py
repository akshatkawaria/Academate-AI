from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.models import User
from backend.services.orchestrator import orchestrator

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])

@router.get("/{user_id}")
def get_user_recommendations(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user_dict = {
        "name": user.name,
        "placement_goal": user.placement_goal or "",
        "skills": user.skills or [],
        "year": user.year or 2,
        "interests": user.interests or []
    }
    return orchestrator.run_placement(user_dict)
