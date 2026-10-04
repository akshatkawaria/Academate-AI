from pydantic import BaseModel, EmailStr
from typing import List, Optional, Any
from datetime import datetime

# ── User ──────────────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    name: str
    email: str
    branch: Optional[str] = ""
    year: Optional[int] = 1
    cgpa: Optional[float] = 0.0
    subjects: Optional[List[str]] = []
    placement_goal: Optional[str] = ""
    target_companies: Optional[List[str]] = []
    available_hours: Optional[float] = 4.0
    interests: Optional[List[str]] = []
    skills: Optional[List[str]] = []

class UserUpdate(BaseModel):
    name: Optional[str] = None
    branch: Optional[str] = None
    year: Optional[int] = None
    cgpa: Optional[float] = None
    subjects: Optional[List[str]] = None
    placement_goal: Optional[str] = None
    target_companies: Optional[List[str]] = None
    available_hours: Optional[float] = None
    interests: Optional[List[str]] = None
    skills: Optional[List[str]] = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    branch: str
    year: int
    cgpa: float
    subjects: List[str]
    placement_goal: str
    target_companies: List[str]
    available_hours: float
    interests: List[str]
    skills: List[str]
    created_at: datetime

    class Config:
        from_attributes = True

# ── Schedule ──────────────────────────────────────────────────────────────────
class ScheduleCreate(BaseModel):
    date: str
    task_name: str
    task_type: Optional[str] = "academic"
    duration_hours: Optional[float] = 1.0
    priority: Optional[str] = "medium"
    notes: Optional[str] = ""

class ScheduleUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class ScheduleResponse(BaseModel):
    id: str
    user_id: str
    date: str
    task_name: str
    task_type: str
    duration_hours: float
    priority: str
    status: str
    notes: str
    created_at: datetime

    class Config:
        from_attributes = True

class GenerateScheduleRequest(BaseModel):
    user_id: str
    date: str  # YYYY-MM-DD
    mode: Optional[str] = "balanced"  # balanced | academic | placement

# ── Progress ──────────────────────────────────────────────────────────────────
class ProgressCreate(BaseModel):
    date: str
    study_hours: float
    completed_tasks: int
    missed_tasks: int
    notes: Optional[str] = ""

class ProgressResponse(BaseModel):
    id: str
    user_id: str
    date: str
    study_hours: float
    completed_tasks: int
    missed_tasks: int
    productivity_score: float
    notes: str

    class Config:
        from_attributes = True

# ── Notification ──────────────────────────────────────────────────────────────
class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    notif_type: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ── Agent Outputs ──────────────────────────────────────────────────────────────
class RecommendationResponse(BaseModel):
    dsa_roadmap: List[str]
    project_ideas: List[str]
    resume_tips: List[str]
    learning_resources: List[dict]
    weekly_focus: str

class OpportunityFilter(BaseModel):
    interests: Optional[List[str]] = []
    opp_type: Optional[str] = "all"  # hackathon | internship | all
