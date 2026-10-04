from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.database.database import Base
from datetime import datetime
import uuid

def gen_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    branch = Column(String, default="")
    year = Column(Integer, default=1)
    cgpa = Column(Float, default=0.0)
    subjects = Column(JSON, default=list)
    placement_goal = Column(String, default="")
    target_companies = Column(JSON, default=list)
    available_hours = Column(Float, default=4.0)
    interests = Column(JSON, default=list)
    skills = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    schedules = relationship("Schedule", back_populates="user", cascade="all, delete")
    progress = relationship("Progress", back_populates="user", cascade="all, delete")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete")


class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    date = Column(String, nullable=False)
    task_name = Column(String, nullable=False)
    task_type = Column(String, default="academic")  # academic | placement | break
    duration_hours = Column(Float, default=1.0)
    priority = Column(String, default="medium")  # high | medium | low
    status = Column(String, default="pending")  # pending | done | missed
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="schedules")


class Progress(Base):
    __tablename__ = "progress"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    date = Column(String, nullable=False)
    study_hours = Column(Float, default=0.0)
    completed_tasks = Column(Integer, default=0)
    missed_tasks = Column(Integer, default=0)
    productivity_score = Column(Float, default=0.0)
    notes = Column(Text, default="")

    user = relationship("User", back_populates="progress")


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notif_type = Column(String, default="reminder")  # reminder | alert | tip
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")


# ── Placement Agent Models ─────────────────────────────────────────────────────

class Skill(Base):
    """Represents a top-level skill category (DSA, AI/ML, Web Dev, etc.)"""
    __tablename__ = "skills"
    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False, unique=True)   # e.g. "AI/ML"
    slug = Column(String, nullable=False, unique=True)   # e.g. "aiml"
    category = Column(String, default="tech")             # tech | core
    icon = Column(String, default="💡")                   # emoji icon
    color = Column(String, default="#3b82f6")             # hex color
    description = Column(Text, default="")
    is_active = Column(Boolean, default=True)

    roadmap_steps = relationship("RoadmapStep", back_populates="skill", cascade="all, delete", order_by="RoadmapStep.step_order")
    resources    = relationship("Resource",    back_populates="skill", cascade="all, delete")
    projects     = relationship("Project",     back_populates="skill", cascade="all, delete")
    progress     = relationship("PlacementProgress", back_populates="skill", cascade="all, delete")


class RoadmapStep(Base):
    """An ordered step inside a skill's learning roadmap."""
    __tablename__ = "roadmap_steps"
    id = Column(String, primary_key=True, default=gen_uuid)
    skill_id   = Column(String, ForeignKey("skills.id"), nullable=False)
    step_order = Column(Integer, nullable=False)
    step_name  = Column(String, nullable=False)
    description = Column(Text, default="")
    estimated_days = Column(Integer, default=7)

    skill = relationship("Skill", back_populates="roadmap_steps")


class Resource(Base):
    """A learning resource (course, video, article) linked to a skill."""
    __tablename__ = "resources"
    id          = Column(String, primary_key=True, default=gen_uuid)
    skill_id    = Column(String, ForeignKey("skills.id"), nullable=False)
    title       = Column(String, nullable=False)
    description = Column(Text, default="")
    resource_type = Column(String, default="course")   # course | youtube | article | practice
    level       = Column(String, default="beginner")   # beginner | intermediate | advanced
    platform    = Column(String, default="")
    url         = Column(String, default="")
    thumbnail   = Column(String, default="")
    is_free     = Column(Boolean, default=True)

    skill = relationship("Skill", back_populates="resources")


class Project(Base):
    """A project recommendation linked to a skill."""
    __tablename__ = "projects"
    id = Column(String, primary_key=True, default=gen_uuid)
    skill_id   = Column(String, ForeignKey("skills.id"), nullable=False)
    title      = Column(String, nullable=False)
    description = Column(Text, default="")
    difficulty = Column(String, default="beginner")   # beginner | intermediate | advanced
    skills_required = Column(JSON, default=list)
    github_url = Column(String, default="")
    learning_outcomes = Column(JSON, default=list)

    skill = relationship("Skill", back_populates="projects")


class PlacementProgress(Base):
    """Tracks a student's progress within a particular skill."""
    __tablename__ = "placement_progress"
    id = Column(String, primary_key=True, default=gen_uuid)
    student_id = Column(String, ForeignKey("users.id"), nullable=False)
    skill_id   = Column(String, ForeignKey("skills.id"), nullable=False)
    completion_percentage = Column(Float, default=0.0)
    completed_steps = Column(JSON, default=list)   # list of RoadmapStep IDs
    completed_courses = Column(JSON, default=list)
    completed_projects = Column(JSON, default=list)
    notes = Column(Text, default="")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    skill = relationship("Skill", back_populates="progress")


class LearningPath(Base):
    """AI-generated personalised weekly learning path for a student & skill."""
    __tablename__ = "learning_paths"
    id = Column(String, primary_key=True, default=gen_uuid)
    student_id     = Column(String, ForeignKey("users.id"), nullable=False)
    skill_id       = Column(String, ForeignKey("skills.id"), nullable=False)
    skill_level    = Column(String, default="beginner")
    available_hours = Column(Float, default=2.0)
    current_week   = Column(Integer, default=1)
    path_data      = Column(JSON, default=dict)   # {week_1: {...}, week_2: {...}, ...}
    generated_at   = Column(DateTime, default=datetime.utcnow)
