"""
Placement Agent API Routes
GET  /api/placement/skills                    — all skills
GET  /api/placement/skills/{slug}             — skill detail + roadmap + resources + projects
GET  /api/placement/progress/{user_id}        — user's placement progress across all skills
POST /api/placement/progress/{user_id}/{slug} — update progress for a skill
GET  /api/placement/readiness/{user_id}       — placement readiness score (0-100)
POST /api/placement/learning-path             — generate AI weekly learning path
GET  /api/placement/dashboard/{user_id}       — full placement dashboard summary
"""
import os, json, logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from backend.database.database import get_db
from backend.database.models import Skill, RoadmapStep, Resource, Project, PlacementProgress, LearningPath, User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/placement", tags=["Placement Agent"])


# ── Schemas ────────────────────────────────────────────────────────────────────

class ProgressUpdate(BaseModel):
    completion_percentage: float
    completed_steps: Optional[List[str]] = []
    completed_courses: Optional[List[str]] = []
    completed_projects: Optional[List[str]] = []
    notes: Optional[str] = ""

class LearningPathRequest(BaseModel):
    user_id: str
    skill_slug: str
    skill_level: str = "beginner"
    available_hours: float = 2.0
    regenerate: bool = False


# ── Helper ─────────────────────────────────────────────────────────────────────

def _skill_to_dict(skill: Skill) -> dict:
    return {
        "id": skill.id,
        "name": skill.name,
        "slug": skill.slug,
        "icon": skill.icon,
        "color": skill.color,
        "description": skill.description,
        "category": skill.category,
    }

def _roadmap_steps(skill: Skill) -> list:
    return [{"id": s.id, "order": s.step_order, "name": s.step_name,
             "description": s.description, "estimated_days": s.estimated_days}
            for s in skill.roadmap_steps]

def _resources_by_type(skill: Skill) -> dict:
    out: dict = {}
    for r in skill.resources:
        bucket = out.setdefault(r.resource_type, [])
        bucket.append({"id": r.id, "title": r.title, "description": r.description,
                       "level": r.level, "platform": r.platform, "url": r.url,
                       "thumbnail": r.thumbnail, "is_free": r.is_free})
    return out

def _projects_by_difficulty(skill: Skill) -> dict:
    out: dict = {}
    for p in skill.projects:
        bucket = out.setdefault(p.difficulty, [])
        bucket.append({"id": p.id, "title": p.title, "description": p.description,
                       "skills_required": p.skills_required, "github_url": p.github_url,
                       "learning_outcomes": p.learning_outcomes})
    return out

def _get_or_create_progress(db: Session, user_id: str, skill_id: str) -> PlacementProgress:
    rec = db.query(PlacementProgress).filter_by(student_id=user_id, skill_id=skill_id).first()
    if not rec:
        rec = PlacementProgress(student_id=user_id, skill_id=skill_id)
        db.add(rec); db.commit(); db.refresh(rec)
    return rec

def _compute_readiness(progress_list: list, user: User, db: Session = None) -> dict:
    """Compute placement readiness 0-100 dynamically from actual DB progress."""
    skills_with_progress = [p for p in progress_list if p.completion_percentage > 0]
    avg_skill = (sum(p.completion_percentage for p in skills_with_progress) / len(skills_with_progress)
                 if skills_with_progress else 0)

    # Resolve DSA progress by looking up the skill name — skill_id is a UUID not 'dsa'
    dsa_prog = 0
    if db:
        from backend.database.models import Skill as SkillModel
        dsa_skill = db.query(SkillModel).filter(SkillModel.slug == "dsa").first()
        if dsa_skill:
            dsa_rec = next((p for p in progress_list if p.skill_id == dsa_skill.id), None)
            dsa_prog = dsa_rec.completion_percentage if dsa_rec else 0

    proj_done   = sum(len(p.completed_projects or []) for p in progress_list)
    course_done = sum(len(p.completed_courses or []) for p in progress_list)
    steps_done  = sum(len(p.completed_steps or []) for p in progress_list)

    dsa_score       = min(dsa_prog * 0.30, 30)
    project_score   = min(proj_done * 5, 20)
    resume_score    = 10 if user and user.placement_goal else 5
    interview_score = min(course_done * 2, 15)
    skill_score     = min(avg_skill * 0.10, 10)
    opps_score      = min(steps_done * 0.5, 10) if steps_done > 0 else 0

    total = dsa_score + project_score + resume_score + interview_score + skill_score + opps_score
    total = min(round(total), 100)

    if total >= 80:   status = "Excellent – Placement Ready! 🚀"
    elif total >= 60: status = "Good Progress – Keep Going! 💪"
    elif total >= 40: status = "On Track – Stay Consistent! 📈"
    else:             status = "Getting Started – Build Momentum! 🌱"

    return {
        "score": total,
        "status": status,
        "breakdown": {
            "dsa": round(dsa_score),
            "projects": round(project_score),
            "resume": round(resume_score),
            "interview_prep": round(interview_score),
            "skill_completion": round(skill_score),
            "opportunities": round(opps_score),
        }
    }



# ── Routes ─────────────────────────────────────────────────────────────────────

@router.get("/skills")
def list_skills(db: Session = Depends(get_db)):
    """All active skills."""
    skills = db.query(Skill).filter(Skill.is_active == True).all()
    return [_skill_to_dict(s) for s in skills]


@router.get("/skills/{slug}")
def get_skill(slug: str, db: Session = Depends(get_db)):
    """Full skill detail: roadmap, resources grouped by type, projects by difficulty."""
    skill = db.query(Skill).filter(Skill.slug == slug).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return {
        **_skill_to_dict(skill),
        "roadmap": _roadmap_steps(skill),
        "resources": _resources_by_type(skill),
        "projects": _projects_by_difficulty(skill),
    }


@router.get("/progress/{user_id}")
def get_user_progress(user_id: str, db: Session = Depends(get_db)):
    """All skill progress records for a user."""
    records = db.query(PlacementProgress).filter_by(student_id=user_id).all()
    skills  = {s.id: s.name for s in db.query(Skill).all()}
    return [
        {
            "skill_id": r.skill_id,
            "skill_name": skills.get(r.skill_id, "Unknown"),
            "completion_percentage": r.completion_percentage,
            "completed_steps": r.completed_steps,
            "completed_courses": r.completed_courses,
            "completed_projects": r.completed_projects,
        }
        for r in records
    ]


@router.post("/progress/{user_id}/{slug}")
def update_progress(user_id: str, slug: str, data: ProgressUpdate, db: Session = Depends(get_db)):
    """Create or update progress for a user's skill."""
    skill = db.query(Skill).filter(Skill.slug == slug).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    rec = _get_or_create_progress(db, user_id, skill.id)
    rec.completion_percentage = data.completion_percentage
    rec.completed_steps    = data.completed_steps
    rec.completed_courses  = data.completed_courses
    rec.completed_projects = data.completed_projects
    rec.notes = data.notes or ""
    db.commit(); db.refresh(rec)
    return {"message": "Progress updated", "completion": rec.completion_percentage}


@router.get("/readiness/{user_id}")
def get_readiness(user_id: str, db: Session = Depends(get_db)):
    """Compute and return placement readiness score."""
    user    = db.query(User).filter_by(id=user_id).first()
    records = db.query(PlacementProgress).filter_by(student_id=user_id).all()
    return _compute_readiness(records, user, db=db)


@router.post("/learning-path")
def generate_learning_path(req: LearningPathRequest, db: Session = Depends(get_db)):
    """Generate (or retrieve cached) a personalised weekly learning path using Gemini."""
    skill = db.query(Skill).filter(Skill.slug == req.skill_slug).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    # Return cached path if exists and not forcing regeneration
    existing = db.query(LearningPath).filter_by(
        student_id=req.user_id, skill_id=skill.id
    ).first()
    if existing and not req.regenerate:
        return {"skill": skill.name, "path": existing.path_data,
                "current_week": existing.current_week, "cached": True}

    # Build path using roadmap steps
    steps = skill.roadmap_steps
    weeks_per_step = max(1, round(7 / max(req.available_hours, 1)))
    path: dict = {}
    week = 1
    for step in steps:
        num_weeks = max(1, round(step.estimated_days / 7))
        for w in range(num_weeks):
            path[f"week_{week}"] = {
                "week": week,
                "topic": step.step_name,
                "description": step.description,
                "focus": f"Study {step.step_name}" + (" fundamentals" if w == 0 else " — deeper practice"),
                "daily_hours": req.available_hours,
                "goal": f"Complete {step.step_name} {'basics' if w == 0 else 'advanced topics'}",
            }
            week += 1
            if week > 12:
                break
        if week > 12:
            break

    # Try Gemini enhancement
    try:
        from backend.planner.gemini_service import enhance_schedule as gemini_call
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_PLANNER_API_KEY", ""))
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = (
            f"You are a career coach. Create a {len(path)}-week personalised learning roadmap for a student "
            f"learning {skill.name} at {req.skill_level} level with {req.available_hours} hours/day available.\n"
            f"Base plan: {json.dumps(path, indent=2)}\n\n"
            f"Return ONLY valid JSON with keys week_1, week_2, ... Each week must have: "
            f"week(int), topic(str), description(str), focus(str), daily_hours(float), goal(str). "
            f"Do NOT include markdown or explanation. JSON only."
        )
        resp = model.generate_content(prompt)
        text = resp.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        enhanced = json.loads(text)
        if isinstance(enhanced, dict) and "week_1" in enhanced:
            path = enhanced
    except Exception as e:
        logger.warning(f"[LearningPath] Gemini enhancement skipped: {e}")

    # Save / update
    if existing:
        existing.path_data = path
        existing.skill_level = req.skill_level
        existing.available_hours = req.available_hours
        db.commit(); db.refresh(existing)
    else:
        lp = LearningPath(student_id=req.user_id, skill_id=skill.id,
                          skill_level=req.skill_level, available_hours=req.available_hours,
                          path_data=path)
        db.add(lp); db.commit(); db.refresh(lp)
        existing = lp

    return {"skill": skill.name, "path": path, "current_week": existing.current_week, "cached": False}


@router.get("/dashboard/{user_id}")
def placement_dashboard(user_id: str, db: Session = Depends(get_db)):
    """Full placement dashboard summary."""
    user    = db.query(User).filter_by(id=user_id).first()
    records = db.query(PlacementProgress).filter_by(student_id=user_id).all()
    skills_map = {s.id: s for s in db.query(Skill).all()}
    readiness = _compute_readiness(records, user, db=db)
    skill_progress = [
        {"skill_name": skills_map[r.skill_id].name if r.skill_id in skills_map else "?",
         "slug": skills_map[r.skill_id].slug if r.skill_id in skills_map else "",
         "icon": skills_map[r.skill_id].icon if r.skill_id in skills_map else "💡",
         "color": skills_map[r.skill_id].color if r.skill_id in skills_map else "#3b82f6",
         "completion": r.completion_percentage}
        for r in records if r.completion_percentage > 0
    ]
    return {
        "readiness": readiness,
        "skill_progress": sorted(skill_progress, key=lambda x: x["completion"], reverse=True),
        "active_skills": len([r for r in records if r.completion_percentage > 0]),
        "total_skills": db.query(Skill).count(),
    }
