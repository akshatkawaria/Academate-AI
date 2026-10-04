"""
Dashboard Intelligence — aggregates live data from all agents into
three dashboard-ready payloads:

  GET /api/dashboard/full/{user_id}
      → { notifications, placement_summary, recommendations }

  GET /api/dashboard/notifications/{user_id}
  GET /api/dashboard/placement-summary/{user_id}
  GET /api/dashboard/recommendations/{user_id}
"""
from datetime import date, datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.models import (
    User, Schedule, Progress,
    Skill, RoadmapStep, Resource, PlacementProgress, LearningPath
)

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard Intelligence"])


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 1 — Smart Notifications
# ──────────────────────────────────────────────────────────────────────────────

def _smart_notifications(user_id: str, db: Session) -> list:
    """Generate live, contextual notifications from all agent data."""
    today = date.today().isoformat()
    notifs = []

    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        return []

    # ── Planner notifications ──────────────────────────────────────────────
    today_tasks = db.query(Schedule).filter_by(user_id=user_id, date=today).all()
    pending   = [t for t in today_tasks if t.status == "pending"]
    completed = [t for t in today_tasks if t.status == "completed"]
    overdue   = db.query(Schedule).filter(
        Schedule.user_id == user_id,
        Schedule.status == "pending",
        Schedule.date < today
    ).count()

    if overdue > 0:
        notifs.append({"icon": "⚡", "title": f"{overdue} Overdue Task(s)",
                       "message": "You have tasks from previous days still pending. Mark them done or missed.",
                       "type": "alert", "priority": "high"})

    if today_tasks:
        pct = round(len(completed) / len(today_tasks) * 100) if today_tasks else 0
        if pct == 100:
            notifs.append({"icon": "🎉", "title": "All Tasks Completed!",
                           "message": "Amazing — you've completed every planned task for today!",
                           "type": "tip", "priority": "low"})
        elif pct < 50 and len(today_tasks) > 0:
            notifs.append({"icon": "⚠️", "title": f"Only {pct}% Done Today",
                           "message": f"{len(pending)} task(s) still pending. Push through — you're almost there!",
                           "type": "alert", "priority": "medium"})
        elif pending:
            notifs.append({"icon": "📅", "title": f"{len(pending)} Task(s) Remaining",
                           "message": f"Keep going! {len(pending)} task(s) left today.",
                           "type": "reminder", "priority": "medium"})
    else:
        notifs.append({"icon": "🗓️", "title": "No Plan For Today",
                       "message": "Generate today's AI plan from the AI Planner to get started.",
                       "type": "reminder", "priority": "medium"})

    # ── Progress notifications ─────────────────────────────────────────────
    recent = db.query(Progress).filter_by(user_id=user_id).order_by(Progress.date.desc()).limit(7).all()
    if len(recent) >= 2:
        delta = recent[0].productivity_score - recent[1].productivity_score
        if delta >= 15:
            notifs.append({"icon": "📈", "title": "Productivity Surge!",
                           "message": f"Your score improved by {round(delta)}% compared to yesterday. Keep it up!",
                           "type": "tip", "priority": "low"})
        elif delta <= -15:
            notifs.append({"icon": "📉", "title": "Productivity Dip Detected",
                           "message": "Your score dropped. Consider taking a short break and re-planning.",
                           "type": "alert", "priority": "medium"})

    if len(recent) >= 7:
        streak = all(r.completed_tasks > 0 for r in recent)
        if streak:
            notifs.append({"icon": "🔥", "title": "7-Day Consistency Streak!",
                           "message": "You've logged activity every day this week. Incredible discipline!",
                           "type": "tip", "priority": "low"})

    # ── Placement notifications ────────────────────────────────────────────
    placement_recs = db.query(PlacementProgress).filter_by(student_id=user_id).all()
    total_steps_done = sum(len(p.completed_steps or []) for p in placement_recs)
    if total_steps_done > 0:
        # Find most recently updated skill
        active = max(placement_recs, key=lambda p: p.completion_percentage, default=None)
        if active and active.completion_percentage > 0:
            skill = db.query(Skill).filter_by(id=active.skill_id).first()
            if skill:
                pct = round(active.completion_percentage)
                notifs.append({"icon": "🚀", "title": f"{skill.name} Progress: {pct}%",
                               "message": f"You're {pct}% through the {skill.name} roadmap. Keep the momentum!",
                               "type": "tip", "priority": "low"})

    # Sort by priority
    order = {"high": 0, "medium": 1, "low": 2}
    notifs.sort(key=lambda n: order.get(n.get("priority", "low"), 2))
    return notifs[:6]  # cap at 6


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 2 — Placement Preparation Summary
# ──────────────────────────────────────────────────────────────────────────────

def _placement_summary(user_id: str, db: Session) -> dict:
    """Return a live placement prep summary for the dashboard card."""
    placement_recs = db.query(PlacementProgress).filter_by(student_id=user_id).all()

    # Find the most active skill (highest completion %)
    active_rec = max(placement_recs, key=lambda p: p.completion_percentage, default=None) if placement_recs else None

    if not active_rec or active_rec.completion_percentage == 0:
        # No progress yet — show DSA as default
        dsa_skill = db.query(Skill).filter_by(slug="dsa").first()
        if dsa_skill:
            return {
                "active_skill": dsa_skill.name,
                "active_skill_slug": dsa_skill.slug,
                "active_skill_icon": dsa_skill.icon,
                "active_skill_color": dsa_skill.color,
                "completion_percentage": 0,
                "readiness_score": 0,
                "completed_steps": [],
                "current_step": dsa_skill.roadmap_steps[0].step_name if dsa_skill.roadmap_steps else "Arrays",
                "next_step": dsa_skill.roadmap_steps[1].step_name if len(dsa_skill.roadmap_steps) > 1 else "Strings",
                "total_steps": len(dsa_skill.roadmap_steps),
                "recommended_problems": _get_recommended_problems("dsa", 0),
                "roadmap_visual": _roadmap_visual(dsa_skill, []),
            }
        return {}

    skill = db.query(Skill).filter_by(id=active_rec.skill_id).first()
    if not skill:
        return {}

    steps = skill.roadmap_steps  # already ordered
    done_ids = set(active_rec.completed_steps or [])
    done_steps = [s for s in steps if s.id in done_ids]
    todo_steps = [s for s in steps if s.id not in done_ids]
    current_step = todo_steps[0].step_name if todo_steps else (done_steps[-1].step_name if done_steps else "—")
    next_step    = todo_steps[1].step_name if len(todo_steps) > 1 else "Completed!"

    # Compute readiness
    from backend.api.routes.placement import _compute_readiness
    user = db.query(User).filter_by(id=user_id).first()
    readiness = _compute_readiness(placement_recs, user, db=db)

    return {
        "active_skill": skill.name,
        "active_skill_slug": skill.slug,
        "active_skill_icon": skill.icon,
        "active_skill_color": skill.color,
        "completion_percentage": round(active_rec.completion_percentage),
        "readiness_score": readiness["score"],
        "completed_steps": [s.step_name for s in done_steps],
        "current_step": current_step,
        "next_step": next_step,
        "total_steps": len(steps),
        "done_count": len(done_steps),
        "recommended_problems": _get_recommended_problems(skill.slug, len(done_steps)),
        "roadmap_visual": _roadmap_visual(skill, done_ids),
    }


def _roadmap_visual(skill: Skill, done_ids: set) -> list:
    """Return a 3-item visual: [completed, current, upcoming]."""
    steps = skill.roadmap_steps
    done  = [s.step_name for s in steps if s.id in done_ids]
    todo  = [s.step_name for s in steps if s.id not in done_ids]
    return [
        {"label": "Completed", "items": done[-3:] if done else ["—"], "state": "completed"},
        {"label": "Current",   "items": [todo[0]] if todo else ["All Done!"], "state": "current"},
        {"label": "Upcoming",  "items": todo[1:3] if len(todo) > 1 else ["—"], "state": "upcoming"},
    ]


_PROBLEM_MAP = {
    "dsa": [
        {"title": "LeetCode #206 – Reverse Linked List", "url": "https://leetcode.com/problems/reverse-linked-list/", "difficulty": "Easy"},
        {"title": "LeetCode #141 – Linked List Cycle",   "url": "https://leetcode.com/problems/linked-list-cycle/",   "difficulty": "Easy"},
        {"title": "LeetCode #21 – Merge Two Sorted Lists","url": "https://leetcode.com/problems/merge-two-sorted-lists/","difficulty": "Easy"},
        {"title": "LeetCode #102 – Binary Tree Level Order","url": "https://leetcode.com/problems/binary-tree-level-order-traversal/","difficulty": "Medium"},
        {"title": "LeetCode #200 – Number of Islands",   "url": "https://leetcode.com/problems/number-of-islands/",   "difficulty": "Medium"},
        {"title": "LeetCode #70 – Climbing Stairs",      "url": "https://leetcode.com/problems/climbing-stairs/",     "difficulty": "Easy"},
        {"title": "LeetCode #322 – Coin Change",         "url": "https://leetcode.com/problems/coin-change/",         "difficulty": "Medium"},
    ],
    "aiml": [
        {"title": "Kaggle Titanic (Beginner ML)",         "url": "https://www.kaggle.com/c/titanic",                   "difficulty": "Beginner"},
        {"title": "House Price Prediction",               "url": "https://www.kaggle.com/c/house-prices-advanced-regression-techniques", "difficulty": "Beginner"},
        {"title": "Image Classification (MNIST)",         "url": "https://www.kaggle.com/c/digit-recognizer",          "difficulty": "Intermediate"},
    ],
    "webdev": [
        {"title": "Build a Portfolio Site",              "url": "https://www.theodinproject.com/paths/foundations",    "difficulty": "Beginner"},
        {"title": "REST API with Node.js",               "url": "https://github.com/topics/rest-api-nodejs",           "difficulty": "Intermediate"},
    ],
}

def _get_recommended_problems(skill_slug: str, done_count: int) -> list:
    """Return 2-3 contextual problems based on skill and progress."""
    problems = _PROBLEM_MAP.get(skill_slug, _PROBLEM_MAP["dsa"])
    start = min(done_count, max(0, len(problems) - 3))
    return problems[start: start + 3]


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 3 — Learning Recommendations
# ──────────────────────────────────────────────────────────────────────────────

def _learning_recommendations(user_id: str, db: Session) -> list:
    """Return 4 smart resource recommendations based on user's active roadmap stage."""
    placement_recs = db.query(PlacementProgress).filter_by(student_id=user_id).all()
    active_rec = max(placement_recs, key=lambda p: p.completion_percentage, default=None) if placement_recs else None

    # Default to DSA if no placement progress
    if not active_rec or active_rec.completion_percentage == 0:
        skill = db.query(Skill).filter_by(slug="dsa").first()
    else:
        skill = db.query(Skill).filter_by(id=active_rec.skill_id).first()

    if not skill:
        return []

    done_count = len(active_rec.completed_steps or []) if active_rec else 0
    # Level: beginner if <30% done, intermediate if 30-70%, advanced otherwise
    level = "beginner" if done_count < 3 else ("intermediate" if done_count < 7 else "advanced")

    # Fetch resources from DB, prioritise by level
    resources = db.query(Resource).filter_by(skill_id=skill.id).all()
    # Score: same level = 10pts, adjacent = 5pts
    level_scores = {"beginner": 0, "intermediate": 1, "advanced": 2}
    target_lvl = level_scores.get(level, 0)

    def score(r):
        r_lvl = level_scores.get(r.level, 0)
        return 10 - abs(r_lvl - target_lvl) * 5

    resources.sort(key=score, reverse=True)

    result = []
    seen = set()
    for r in resources:
        if r.title in seen:
            continue
        seen.add(r.title)
        result.append({
            "id": r.id,
            "title": r.title,
            "description": r.description or f"Learn {skill.name} — {r.level} level",
            "url": r.url,
            "platform": r.platform,
            "type": r.resource_type,
            "level": r.level,
            "is_free": r.is_free,
            "skill": skill.name,
            "skill_icon": skill.icon,
            "skill_color": skill.color,
        })
        if len(result) >= 4:
            break

    return result


# ──────────────────────────────────────────────────────────────────────────────
# API Routes
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/notifications/{user_id}")
def get_dashboard_notifications(user_id: str, db: Session = Depends(get_db)):
    return _smart_notifications(user_id, db)


@router.get("/placement-summary/{user_id}")
def get_placement_summary(user_id: str, db: Session = Depends(get_db)):
    return _placement_summary(user_id, db)


@router.get("/recommendations/{user_id}")
def get_recommendations(user_id: str, db: Session = Depends(get_db)):
    return _learning_recommendations(user_id, db)


@router.get("/full/{user_id}")
def get_full_dashboard(user_id: str, db: Session = Depends(get_db)):
    """Single call that returns all three dashboard intelligence payloads."""
    return {
        "notifications":     _smart_notifications(user_id, db),
        "placement_summary": _placement_summary(user_id, db),
        "recommendations":   _learning_recommendations(user_id, db),
    }
