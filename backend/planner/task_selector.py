"""
Task Selector — Decides WHAT tasks the student should do based on priority analysis.
RESPONSIBILITY: Pure task selection. No time slots. No breaks. No scheduling.
"""

def select_tasks(user_data: dict, analysis: dict) -> list:
    """
    Returns an ordered list of tasks with duration and priority.
    Each task is a dict: {name, type, duration_hours, priority, reason}
    """
    tasks = []
    remaining_academic = analysis["adjusted_hours"] * (analysis["academic_weight"] / 100.0)
    remaining_placement = analysis["adjusted_hours"] * (analysis["placement_weight"] / 100.0)
    max_dur = analysis["max_task_duration"]

    # ── ACADEMIC TASK SELECTION ───────────────────────────────────────────────
    # Rule: Weak subjects get priority and extra time
    weak_subjects = user_data.get("weak_subjects", [])
    subjects = user_data.get("subjects", [])
    upcoming_exams = user_data.get("upcoming_exams", [])
    skill = analysis["skill"]

    if weak_subjects and remaining_academic > 0:
        dur = min(max_dur, remaining_academic, 1.5)
        tasks.append({
            "name": f"Deep Revision: {weak_subjects[0]}",
            "type": "academic",
            "duration_hours": round(dur, 1),
            "priority": "high",
            "reason": f"Prioritizing {weak_subjects[0]} as a weak subject to close fundamental gaps."
        })
        remaining_academic -= dur

    # Rule: Upcoming exams get dedicated slot
    if analysis["exams_near"] and remaining_academic > 0:
        target = upcoming_exams[0] if upcoming_exams else (subjects[0] if subjects else "Core Subject")
        dur = min(max_dur, remaining_academic, 2.0)
        tasks.append({
            "name": f"Exam Preparation: {target}",
            "type": "academic",
            "duration_hours": round(dur, 1),
            "priority": "high",
            "reason": f"Focused preparation for the upcoming {target} exam."
        })
        remaining_academic -= dur

    # Remaining academic hours → regular coursework or second weak subject
    if remaining_academic > 0.5:
        second_subj = weak_subjects[1] if len(weak_subjects) > 1 else (subjects[0] if subjects else "Core Coursework")
        dur = min(max_dur, remaining_academic, 1.5)
        tasks.append({
            "name": f"Concept Study: {second_subj}",
            "type": "academic",
            "duration_hours": round(dur, 1),
            "priority": "medium",
            "reason": "Steady coursework progression to maintain CGPA."
        })
        remaining_academic -= dur

    # ── PLACEMENT TASK SELECTION ──────────────────────────────────────────────
    placement_priority = analysis["placement_priority"]
    domain = user_data.get("interested_domain", "DSA")
    goal = user_data.get("placement_goal", "Product Company")

    dsa_level_map = {
        "beginner": "Easy LeetCode problems (Arrays, Strings)",
        "intermediate": "Medium LeetCode problems (Sliding Window, Two Pointers)",
        "advanced": "Hard LeetCode + System Design concepts"
    }
    dsa_task = dsa_level_map.get(skill, dsa_level_map["intermediate"])

    # Adaptive overrides
    adapt = user_data.get("_progress_analytics", {}).get("planner_adaptation", {}).get("adjustments", {})
    if adapt.get("increase_dsa_difficulty"):
        dsa_task = dsa_level_map.get("advanced", dsa_task) # force harder
    if adapt.get("reduce_dsa_length"):
        max_dur = min(max_dur, 0.75) # Cap DSA at 45 mins if consistency is low

    # DSA is always the primary placement task
    if remaining_placement > 0:
        dur = min(max_dur, remaining_placement, 1.5)
        tasks.append({
            "name": f"DSA Practice: {dsa_task}",
            "type": "placement",
            "duration_hours": round(dur, 1),
            "priority": "high" if placement_priority == "high" else "medium",
            "reason": f"Core problem-solving skills essential for {goal} interviews."
        })
        remaining_placement -= dur

    # Resume / Project if remaining time allows
    resume_status = user_data.get("resume_status", "")
    projects = int(user_data.get("projects_completed", 0))

    if remaining_placement > 0.5:
        if "update" in resume_status.lower() or "needs" in resume_status.lower():
            tasks.append({
                "name": "Resume Polishing & ATS Optimization",
                "type": "placement",
                "duration_hours": round(min(1.0, remaining_placement), 1),
                "priority": "medium",
                "reason": "Resume needs updating before applying to companies."
            })
        elif projects < 2:
            tasks.append({
                "name": f"Project Building: {domain}",
                "type": "placement",
                "duration_hours": round(min(max_dur, remaining_placement), 1),
                "priority": "medium",
                "reason": "Building portfolio projects strengthens interview credibility."
            })
        else:
            tasks.append({
                "name": f"Domain Skill: {domain} — Concepts & Practice",
                "type": "placement",
                "duration_hours": round(min(max_dur, remaining_placement), 1),
                "priority": "medium",
                "reason": f"Domain-specific knowledge boosts targeting {goal} roles."
            })

    # Filter any tasks with near-zero duration
    return [t for t in tasks if t["duration_hours"] >= 0.25]
