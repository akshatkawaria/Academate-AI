"""
Progress Analytics Engine
Computes all scores, behavior analysis, burnout detection, and adaptive insights.
Pure deterministic logic — no AI calls needed.
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def extract_academic_subject(task_name: str) -> str:
    name_lower = task_name.lower()
    
    # 1. Match common subjects by keywords first
    if "dbms" in name_lower or "database" in name_lower:
        return "DBMS"
    if "operating system" in name_lower or "os" in name_lower:
        words = name_lower.replace(":", " ").replace("-", " ").split()
        if "os" in words or "operating" in words or "systems" in words:
            return "Operating Systems"
    if "network" in name_lower or "cn" in name_lower.replace(":", " ").split():
        return "Computer Networks"
    if "oop" in name_lower or "object oriented" in name_lower:
        return "OOP"
    if "software engineering" in name_lower or "se" in name_lower.replace(":", " ").split():
        return "Software Engineering"
    if "compiler" in name_lower:
        return "Compiler Design"
    if "toc" in name_lower or "theory of computation" in name_lower or "automata" in name_lower:
        return "Theory of Computation"
    if "math" in name_lower or "discrete" in name_lower:
        return "Mathematics"

    # 2. Split by colon if present
    if ":" in task_name:
        parts = [p.strip() for p in task_name.split(":", 1)]
        prefix, suffix = parts[0], parts[1]
        
        generic_verbs = ["deep revision", "concept study", "exam preparation", "exam prep", "practice", "active recall", "core", "study"]
        if prefix.lower() in generic_verbs:
            return suffix.split("-")[0].split("—")[0].strip().title()
        else:
            clean_prefix = prefix
            for v in generic_verbs:
                clean_prefix = clean_prefix.replace(v.title(), "").replace(v, "").strip()
            if clean_prefix:
                return clean_prefix.title()
            return suffix.title()

    # 3. Fallback
    return "Core Coursework"


def categorize_placement_task(name: str) -> str:
    name_lower = name.lower()
    if "array" in name_lower or "string" in name_lower:
        return "DSA: Arrays & Strings"
    if "sliding window" in name_lower or "two-pointer" in name_lower or "two pointer" in name_lower:
        return "DSA: Sliding Window & Two-Pointer"
    if "tree" in name_lower or "graph" in name_lower or "bst" in name_lower:
        return "DSA: Trees & Graphs"
    if "dp" in name_lower or "dynamic programming" in name_lower or "greedy" in name_lower:
        return "DSA: Dynamic Programming"
    if "system design" in name_lower:
        return "System Design"
    if "resume" in name_lower or "ats" in name_lower:
        return "Resume & ATS Optimization"
    if "project" in name_lower or "portfolio" in name_lower:
        return "Project Portfolio Building"
    if "dsa" in name_lower:
        return "DSA Practice"
    
    # Extract from "Domain Skill: {domain} — Concepts & Practice"
    if "domain skill" in name_lower:
        if ":" in name:
            parts = name.split(":", 1)[1].split("—", 1)
            return f"Domain Skill: {parts[0].strip()}"
            
    return "Core Placement Skills"


# ─────────────────────────────────────────────
# SCORE CALCULATORS
# ─────────────────────────────────────────────

def productivity_score(records: List[dict]) -> int:
    """
    Weighted score (0-100) based on:
    - Task completion rate (50%)
    - Study hour consistency (30%)
    - Streak bonus (20%)
    """
    if not records:
        return 0

    completed = sum(r.get("completed_tasks", 0) for r in records)
    missed = sum(r.get("missed_tasks", 0) for r in records)
    total_tasks = completed + missed
    task_rate = (completed / total_tasks) if total_tasks > 0 else 0

    avg_hours = sum(r.get("study_hours", 0) for r in records) / len(records)
    hour_rate = min(avg_hours / 4.0, 1.0)

    streak = _streak(records)
    streak_bonus = min(streak / 7.0, 1.0)

    score = (task_rate * 0.5 + hour_rate * 0.3 + streak_bonus * 0.2) * 100
    return round(score)


def exam_readiness_score(records: List[dict], completed_tasks: int, missed_tasks: int) -> int:
    """
    Based on recent academic task completion rate and study consistency.
    """
    if not records:
        return 0
    total = completed_tasks + missed_tasks
    if total == 0:
        return 50  # No data — neutral
    rate = completed_tasks / total
    # Weight consistency of recent week more
    recent = records[-7:] if len(records) >= 7 else records
    recent_score = productivity_score(recent)
    score = (rate * 0.6 + recent_score / 100 * 0.4) * 100
    return min(100, round(score))


def placement_readiness_score(records: List[dict]) -> int:
    """
    Derived from placement-specific patterns in study data.
    Uses productivity score as a proxy since we don't have separate placement tracking.
    """
    if len(records) < 3:
        return 30  # Insufficient data
    recent = records[-14:] if len(records) >= 14 else records
    score = productivity_score(recent)
    # Placement readiness tends to lag — discount by ~20%
    return max(10, round(score * 0.8))


# ─────────────────────────────────────────────
# BEHAVIOR ANALYSIS
# ─────────────────────────────────────────────

def analyze_behavior(records: List[dict]) -> Dict[str, Any]:
    """
    Detects behavioral patterns from progress history.
    """
    if not records:
        return {"trend": "no_data", "strongest_day": None, "weakest_day": None, "avg_daily_hours": 0}

    # Trend: compare last 3 vs previous 3
    trend = "stable"
    if len(records) >= 6:
        recent_avg = sum(r.get("productivity_score", 0) for r in records[-3:]) / 3
        prev_avg = sum(r.get("productivity_score", 0) for r in records[-6:-3]) / 3
        if recent_avg > prev_avg + 10:
            trend = "improving"
        elif recent_avg < prev_avg - 10:
            trend = "declining"

    # Best/worst day
    sorted_recs = sorted(records, key=lambda r: r.get("productivity_score", 0))
    weakest = sorted_recs[0] if sorted_recs else None
    strongest = sorted_recs[-1] if sorted_recs else None

    avg_hours = round(sum(r.get("study_hours", 0) for r in records) / len(records), 1)
    avg_tasks = round(sum(r.get("completed_tasks", 0) for r in records) / len(records), 1)

    return {
        "trend": trend,
        "strongest_day": strongest.get("date") if strongest else None,
        "weakest_day": weakest.get("date") if weakest else None,
        "avg_daily_hours": avg_hours,
        "avg_daily_tasks": avg_tasks,
        "total_days_logged": len(records),
    }


# ─────────────────────────────────────────────
# BURNOUT DETECTION
# ─────────────────────────────────────────────

def detect_burnout(records: List[dict]) -> Dict[str, Any]:
    """
    Detects burnout risk using multiple signals.
    Risk levels: none, low, medium, high
    """
    if len(records) < 3:
        return {"risk": "none", "signals": [], "recommendation": "Keep logging daily to enable burnout monitoring."}

    recent = records[-7:] if len(records) >= 7 else records
    signals = []
    score = 0

    # Signal 1: Declining productivity score
    if len(recent) >= 3:
        recent_scores = [r.get("productivity_score", 0) for r in recent]
        if recent_scores[-1] < recent_scores[0] - 20:
            signals.append("Productivity has dropped significantly in the last few days.")
            score += 2

    # Signal 2: Low completion rate
    completed = sum(r.get("completed_tasks", 0) for r in recent)
    missed = sum(r.get("missed_tasks", 0) for r in recent)
    total = completed + missed
    if total > 0 and (missed / total) > 0.5:
        signals.append("More than half of tasks are being missed.")
        score += 2

    # Signal 3: Declining study hours
    if len(recent) >= 4:
        early_hours = sum(r.get("study_hours", 0) for r in recent[:len(recent)//2])
        late_hours = sum(r.get("study_hours", 0) for r in recent[len(recent)//2:])
        if late_hours < early_hours * 0.6:
            signals.append("Study hours have declined by more than 40% recently.")
            score += 1

    # Signal 4: Very low average score
    avg_score = sum(r.get("productivity_score", 0) for r in recent) / len(recent)
    if avg_score < 35:
        signals.append("Average productivity is critically low.")
        score += 2

    # Determine risk level
    if score >= 4:
        risk = "high"
        recommendation = "🚨 High burnout risk detected. Take a recovery day, reduce workload, and prioritize rest."
    elif score >= 2:
        risk = "medium"
        recommendation = "⚠️ Medium burnout risk. Reduce task load by 30% and add more breaks today."
    elif score >= 1:
        risk = "low"
        recommendation = "😌 Low burnout risk. Maintain current pace but monitor your energy levels."
    else:
        risk = "none"
        recommendation = "✅ No burnout detected. You're maintaining a healthy study rhythm."

    return {"risk": risk, "signals": signals, "recommendation": recommendation, "score": score}


# ─────────────────────────────────────────────
# AI INSIGHTS GENERATOR (rule-based)
# ─────────────────────────────────────────────

def generate_insights(records: List[dict], behavior: dict, burnout: dict) -> List[Dict[str, str]]:
    """
    Generates actionable, personalized insights from behavioral analysis.
    Returns list of {type, title, message} objects.
    """
    insights = []
    if not records:
        insights.append({
            "type": "info",
            "title": "Start Logging",
            "message": "Log your first study session to activate the adaptive intelligence system."
        })
        return insights

    trend = behavior.get("trend", "stable")
    avg_hours = behavior.get("avg_daily_hours", 0)
    avg_tasks = behavior.get("avg_daily_tasks", 0)

    # Trend insight
    if trend == "improving":
        insights.append({
            "type": "success",
            "title": "📈 You're Improving!",
            "message": f"Your productivity has increased over the last few days. Averaging {avg_hours}h/day. Keep this momentum going."
        })
    elif trend == "declining":
        insights.append({
            "type": "warning",
            "title": "📉 Declining Trend Detected",
            "message": "Your productivity has dropped over the last few days. Consider reducing workload or adjusting your study schedule."
        })

    # Burnout insight
    if burnout["risk"] in ["medium", "high"]:
        insights.append({
            "type": "danger" if burnout["risk"] == "high" else "warning",
            "title": f"🔥 Burnout Risk: {burnout['risk'].capitalize()}",
            "message": burnout["recommendation"]
        })

    # Low hours insight
    if avg_hours < 2 and len(records) >= 3:
        insights.append({
            "type": "warning",
            "title": "⏱️ Low Study Hours",
            "message": f"You're averaging only {avg_hours}h/day. Try to gradually increase to at least 3-4 hours for meaningful progress."
        })

    # High missed tasks insight
    recent = records[-7:] if len(records) >= 7 else records
    total_missed = sum(r.get("missed_tasks", 0) for r in recent)
    total_completed = sum(r.get("completed_tasks", 0) for r in recent)
    total = total_missed + total_completed
    if total > 0 and (total_missed / total) > 0.4:
        insights.append({
            "type": "warning",
            "title": "📋 Too Many Missed Tasks",
            "message": "You're missing 40%+ of planned tasks. Your planner will automatically generate lighter schedules to build consistency."
        })

    # Streak insight
    streak = _streak(records)
    if streak >= 5:
        insights.append({
            "type": "success",
            "title": f"🔥 {streak}-Day Streak!",
            "message": "Excellent consistency! You've been productive for multiple days in a row. Consistency beats intensity."
        })

    # Positive baseline
    if not insights:
        insights.append({
            "type": "success",
            "title": "✅ Looking Good",
            "message": f"You're maintaining steady progress with {avg_hours}h/day and {avg_tasks} tasks completed on average."
        })

    return insights


# ─────────────────────────────────────────────
# PLANNER ADAPTATION PARAMETERS
# ─────────────────────────────────────────────

def get_planner_adaptation(records: List[dict], burnout: dict, behavior: dict, sched_dicts: List[dict] = None) -> Dict[str, Any]:
    """
    Returns suggested adjustments to the planner based on progress data AND exact task history.
    This is the core feedback loop that connects Progress → Planner.
    """
    adaptations = []
    adjustments = {}
    sched_dicts = sched_dicts or []

    if not records and not sched_dicts:
        return {"adjustments": {}, "adaptations": ["No data yet — planner using default settings."]}

    # Analyze exact skipped tasks from schedule history (last 7 days)
    recent_sched = sched_dicts[-50:] # approximate last week of tasks
    missed_morning = 0
    missed_dsa = 0
    completed_dsa = 0
    
    for s in recent_sched:
        if "am" in str(s.get("start_time", "")).lower() and s.get("status") in ["missed", "pending"]:
            missed_morning += 1
        if "dsa" in str(s.get("task_name", "")).lower():
            if s.get("status") == "completed":
                completed_dsa += 1
            else:
                missed_dsa += 1

    # Apply behavioral logic based on exact task skips
    if missed_morning >= 3:
        adjustments["shift_schedule_to_evening"] = True
        adaptations.append("Repeatedly missed morning tasks detected. Planner will shift difficult tasks to the afternoon/evening.")
        
    if missed_dsa >= 3:
        adjustments["reduce_dsa_length"] = True
        adaptations.append("Low DSA consistency detected. Planner will generate shorter, more manageable DSA sessions.")
    elif completed_dsa >= 3:
        adjustments["increase_dsa_difficulty"] = True
        adaptations.append("Strong DSA consistency detected. Planner will increase DSA session length and difficulty.")

    # Generate Subject and Placement specific analytics for the frontend
    subject_completion = {}
    placement_completion = {}
    for s in recent_sched:
        name = s.get("task_name", "")
        status = s.get("status")
        t_type = s.get("task_type", "")
        
        if t_type == "academic":
            subj = extract_academic_subject(name)
            if subj not in subject_completion:
                subject_completion[subj] = {"completed": 0, "total": 0}
            subject_completion[subj]["total"] += 1
            if status == "completed":
                subject_completion[subj]["completed"] += 1
                
        if t_type == "placement":
            cat_name = categorize_placement_task(name)
            if cat_name not in placement_completion:
                placement_completion[cat_name] = {"completed": 0, "total": 0}
            placement_completion[cat_name]["total"] += 1
            if status == "completed":
                placement_completion[cat_name]["completed"] += 1

    subject_analytics = {
        "weakest_subject": min(subject_completion.keys(), key=lambda k: subject_completion[k]["completed"]/subject_completion[k]["total"]) if subject_completion else "Not enough data",
        "strongest_subject": max(subject_completion.keys(), key=lambda k: subject_completion[k]["completed"]/subject_completion[k]["total"]) if subject_completion else "Not enough data",
        "breakdown": subject_completion
    }
    
    # Only classify as avoided if they actually missed/pending tasks in that topic
    avoided_topics = [k for k, v in placement_completion.items() if v["completed"] < v["total"]]
    most_avoided = "Not enough data"
    if avoided_topics:
        most_avoided = min(avoided_topics, key=lambda k: placement_completion[k]["completed"]/placement_completion[k]["total"])
    elif placement_completion:
        most_avoided = "Not enough data"
        
    placement_analytics = {
        "most_avoided": most_avoided,
        "breakdown": placement_completion
    }

    recent = records[-7:] if len(records) >= 7 else records
    avg_hours = behavior.get("avg_daily_hours", 4)
    trend = behavior.get("trend", "stable")
    burnout_risk = burnout.get("risk", "none")

    # Adjust recommended study hours based on actual behavior
    if avg_hours < 2 and records:
        adjustments["suggested_hours"] = max(2, avg_hours + 0.5)
        adaptations.append(f"Actual study hours are low ({avg_hours}h). Planner will generate lighter schedules.")
    elif avg_hours > 6 and records:
        adjustments["suggested_hours"] = min(8, avg_hours)
        adaptations.append(f"Strong study hours ({avg_hours}h/day). Planner can schedule more ambitious tasks.")

    # Burnout adaptations
    if burnout_risk == "high":
        adjustments["reduce_workload"] = True
        adjustments["increase_breaks"] = True
        adjustments["max_task_duration"] = 0.75
        adaptations.append("High burnout: planner will reduce task load and add more recovery time.")
    elif burnout_risk == "medium":
        adjustments["increase_breaks"] = True
        adjustments["max_task_duration"] = 1.0
        adaptations.append("Medium burnout: planner will increase break frequency.")

    # Trend-based adaptations
    if trend == "declining":
        adjustments["simplify_tasks"] = True
        adaptations.append("Declining trend: planner will generate simpler, shorter tasks.")
    elif trend == "improving":
        adjustments["can_increase_difficulty"] = True
        adaptations.append("Improving trend: planner can introduce more challenging tasks.")

    return {"adjustments": adjustments, "adaptations": adaptations, "subject_analytics": subject_analytics, "placement_analytics": placement_analytics}


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _streak(records: List[dict]) -> int:
    """Counts consecutive days with productivity_score >= 40."""
    streak = 0
    for r in reversed(records):
        if r.get("productivity_score", 0) >= 40:
            streak += 1
        else:
            break
    return streak


def build_full_analytics(records: List[dict], sched_dicts: List[dict] = None) -> Dict[str, Any]:
    """
    Master function: runs all engines and returns the complete analytics payload.
    """
    sched_dicts = sched_dicts or []
    rec_dicts = [
        {
            "date": r.get("date", ""),
            "study_hours": r.get("study_hours", 0),
            "completed_tasks": r.get("completed_tasks", 0),
            "missed_tasks": r.get("missed_tasks", 0),
            "productivity_score": r.get("productivity_score", 0),
        }
        for r in records
    ]

    total_completed = sum(r["completed_tasks"] for r in rec_dicts)
    total_missed = sum(r["missed_tasks"] for r in rec_dicts)
    total_hours = round(sum(r["study_hours"] for r in rec_dicts), 1)
    days_logged = len(rec_dicts)
    avg_prod = round(sum(r["productivity_score"] for r in rec_dicts) / days_logged, 1) if days_logged else 0
    streak = _streak(rec_dicts)

    behavior = analyze_behavior(rec_dicts)
    burnout = detect_burnout(rec_dicts)
    insights = generate_insights(rec_dicts, behavior, burnout)
    adaptation = get_planner_adaptation(rec_dicts, burnout, behavior, sched_dicts)

    prod_score = productivity_score(rec_dicts)
    exam_score = exam_readiness_score(rec_dicts, total_completed, total_missed)
    placement_score = placement_readiness_score(rec_dicts)

    logger.info(f"[Analytics] prod={prod_score} exam={exam_score} placement={placement_score} burnout={burnout['risk']}")

    return {
        # Headline stats
        "avg_productivity": avg_prod,
        "total_study_hours": total_hours,
        "total_completed_tasks": total_completed,
        "total_missed_tasks": total_missed,
        "days_logged": days_logged,
        "current_streak": streak,
        # Scores
        "productivity_score": prod_score,
        "exam_readiness_score": exam_score,
        "placement_readiness_score": placement_score,
        # Deep analytics
        "behavior": behavior,
        "burnout": burnout,
        "insights": insights,
        "planner_adaptation": adaptation,
        "subject_analytics": adaptation.get("subject_analytics", {}),
        "placement_analytics": adaptation.get("placement_analytics", {}),
        # Compatibility fields
        "completion_rate": int(total_completed / (total_completed + total_missed) * 100) if (total_completed + total_missed) > 0 else 0,
        "weekly_streak": streak,
        "consistency": behavior.get("trend", "stable"),
        "avg_hours": round(total_hours / days_logged, 1) if days_logged else 0,
    }
