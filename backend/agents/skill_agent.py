"""
Skill Agent — Generates personalized learning roadmaps.
Architecture:
  Supabase Data (skill + resources + student) → Prompt Builder → Gemini (shared) → Structured JSON

IMPORTANT: This agent reuses the shared Gemini client from planner/gemini_service.py.
           No separate Gemini clients or API keys are created.
"""
import logging
from typing import Optional, Dict, Any

from backend.services.skill_service import get_skill
from backend.services.resource_service import get_resources
from backend.services.student_service import get_student
from backend.planner.gemini_service import generate_json_response

logger = logging.getLogger(__name__)

REQUIRED_KEYS = ["learning_plan", "projects", "placement_tips"]
REQUIRED_NEW_SKILL_KEYS = ["skill_metadata", "resources", "learning_plan", "projects", "placement_tips"]



# ── Prompt Builder ────────────────────────────────────────────────────────────

def _build_skill_prompt(skill: dict, resources: list, student: dict) -> str:
    """
    Builds a structured prompt for the Skill Agent.
    Requests the exact JSON schema the frontend expects.
    """
    resource_text = "\n".join([
        f"- {r['title']} ({r['url']})"
        for r in resources
    ]) if resources else "No curated resources available."

    return f"""You are AcadMate's AI Career Mentor — an expert in tech skill development and placement preparation.

=== STUDENT PROFILE ===
Name: {student.get('name', 'Student')}
Year: {student.get('year', 'Unknown')}
Target Role: {student.get('target_role', 'SDE')}
Daily Study Hours: {student.get('daily_hours', 2)}

=== SKILL TO LEARN ===
Skill: {skill.get('skill_name', 'Unknown')}
Difficulty: {skill.get('difficulty', 'Intermediate')}
Estimated Duration: {skill.get('estimated_duration', '4 weeks')}
Prerequisites: {skill.get('prerequisites', 'None')}
Roadmap: {skill.get('roadmap', 'Not available')}
Project Ideas: {skill.get('project_ideas', 'Not available')}
Career Benefits: {skill.get('career_benefits', 'Not available')}

=== CURATED RESOURCES ===
{resource_text}

=== ADAPTATION RULES ===
You MUST adapt the week-by-week learning plan, recommended projects, and placement/interview tips to fit the student's background:
1. YEAR OF STUDY ADAPTATION:
   - If the student is in their "1st Year": Keep the pace slower, focus heavily on core fundamentals first, and avoid overwhelming them with advanced concepts too early.
   - If the student is in their "Final Year": Accelerate the pace, make it highly project-heavy, and skew the placement tips toward technical interview preparation, coding rounds, and portfolio presentation.
   - For other years, provide a balanced pacing.

2. DAILY STUDY HOURS ADAPTATION:
   - If daily study hours are low (e.g., 2 hours/day or less): The weekly learning plan should have smaller, bite-sized tasks.
   - If daily study hours are high (e.g., 5-6 hours/day or more): Make the weekly tasks more intensive, extensive, and project-oriented, covering more advanced areas quickly.

3. TARGET ROLE ADAPTATION:
   - If the target role is "AI Engineer" or similar: The project ideas must be GenAI/ML-centric (e.g., LLM fine-tuning, RAG, multi-agent systems, prompt flows).
   - If the target role is "Software Engineer" / "Fullstack Developer" / "SDE": The projects should focus on building robust, scalable software, API architecture, databases, or system design.
   - Tailor the projects and interview tips to align exactly with this career goal.

=== YOUR TASK ===
Create a personalized, week-by-week learning plan for this student to master the skill above.
Include practical project recommendations and placement preparation tips.

=== CRITICAL RULES ===
- Return ONLY valid JSON. No markdown. No code blocks. No comments inside JSON.
- The learning_plan must have at least 2 weeks.
- Projects must be specific and actionable, not vague.
- Placement tips must relate to the skill being learned.

=== REQUIRED JSON STRUCTURE ===
{{
  "learning_plan": [
    {{
      "week": 1,
      "focus": "Clear description of what to study this week",
      "tasks": ["Specific task 1", "Specific task 2"],
      "resources": ["Relevant resource or topic"]
    }}
  ],
  "projects": [
    {{
      "name": "Specific project name",
      "difficulty": "Beginner, Intermediate, or Advanced",
      "description": "Brief description of the project"
    }}
  ],
  "placement_tips": [
    "Actionable placement tip related to this skill"
  ]
}}"""


# ── Fallback ──────────────────────────────────────────────────────────────────

def _generate_fallback(skill_name: str, skill: Optional[dict] = None, resources: Optional[list] = None) -> dict:
    """
    Deterministic fallback if Gemini fails — constructs a structured plan
    using existing prefetched roadmap, projects, and resources from Supabase.
    """
    logger.info(f"[Skill Agent Fallback] Building fallback using database data for '{skill_name}'...")
    
    # 1. Parse pre-existing roadmap phases
    roadmap_str = skill.get('roadmap') if skill else None
    steps = []
    if roadmap_str:
        if "→" in roadmap_str:
            steps = [s.strip() for s in roadmap_str.split("→") if s.strip()]
        elif "," in roadmap_str:
            steps = [s.strip() for s in roadmap_str.split(",") if s.strip()]
        else:
            steps = [roadmap_str.strip()]
            
    learning_plan = []
    if steps:
        for i, step in enumerate(steps):
            learning_plan.append({
                "week": i + 1,
                "focus": step,
                "tasks": [f"Learn the core concepts of {step}", f"Implement a hands-on exercise for {step}"],
                "resources": [r['title'] for r in resources[:2]] if resources else ["Official documentation"]
            })
    else:
        # Default 4-week structure
        learning_plan = [
            {"week": 1, "focus": f"Fundamentals of {skill_name}", "tasks": [f"Research {skill_name} basics", "Set up development environment"], "resources": ["Official documentation"]},
            {"week": 2, "focus": f"Hands-on practice with {skill_name}", "tasks": ["Build a small project", "Solve practice problems"], "resources": ["YouTube tutorials"]},
            {"week": 3, "focus": f"Advanced {skill_name} concepts", "tasks": ["Study advanced patterns", "Read case studies"], "resources": ["Technical blogs"]},
            {"week": 4, "focus": f"Portfolio & interview prep", "tasks": ["Complete a portfolio project", "Practice interview questions"], "resources": ["LeetCode / mock interviews"]},
        ]

    # 2. Parse projects
    project_ideas_str = skill.get('project_ideas') if skill else None
    projects_raw = []
    if project_ideas_str:
        if ";" in project_ideas_str:
            projects_raw = [p.strip() for p in project_ideas_str.split(";") if p.strip()]
        else:
            projects_raw = [p.strip() for p in project_ideas_str.split(",") if p.strip()]
    else:
        projects_raw = [
            f"Build a mini-project demonstrating {skill_name} fundamentals",
            f"Create a portfolio piece using {skill_name} with a real-world use case"
        ]
    
    projects = []
    for i, p in enumerate(projects_raw):
        diff = "Beginner" if i == 0 else ("Advanced" if i == len(projects_raw)-1 else "Intermediate")
        projects.append({
            "name": p.split(":")[0] if ":" in p else f"Project {i+1}",
            "difficulty": diff,
            "description": p.split(":")[1].strip() if ":" in p else p
        })

    # 3. Create placement tips
    tips = [
        f"Be ready to explain {skill_name} concepts in interviews with real examples.",
        "Practice whiteboard coding for related problem types.",
        f"Add your {skill_name} projects to GitHub with clear README files."
    ]
    if skill and skill.get('difficulty'):
        tips.append(f"Highlight your understanding of {skill_name} as an {skill.get('difficulty')} level skill.")

    return {
        "learning_plan": learning_plan,
        "projects": projects,
        "placement_tips": tips,
        "is_fallback": True
    }


# ── Main Entry Point ─────────────────────────────────────────────────────────

def generate_learning_plan(skill_name: str, student_id) -> Dict[str, Any]:
    """
    Generates a personalized learning roadmap for a given skill.

    1. Fetches skill metadata from Supabase
    2. Fetches learning resources from Supabase
    3. Fetches student profile from Supabase
    4. Builds prompt and calls shared Gemini service
    5. Returns structured JSON

    Args:
        skill_name: The skill to learn (e.g. "RAG", "Docker", "System Design")
        student_id: Student ID for profile lookup in Supabase
    """
    TAG = "Skill Agent"

    # ── Stage 1: Fetch skill data ──
    logger.info(f"[{TAG}] Fetching skill data for '{skill_name}'...")
    skill_data = get_skill(skill_name)
    if not skill_data:
        logger.error(f"[{TAG}] Skill '{skill_name}' not found in Supabase.")
        return {"error": f"Skill '{skill_name}' not found in database."}
    skill = skill_data[0]
    logger.info(f"[{TAG}] ✅ Skill found: {skill.get('skill_name')} (difficulty: {skill.get('difficulty')})")

    # ── Stage 2: Fetch resources ──
    logger.info(f"[{TAG}] Fetching resources for '{skill_name}'...")
    resources = get_resources(skill_name) or []
    logger.info(f"[{TAG}] ✅ Found {len(resources)} resources.")

    # ── Stage 3: Fetch student profile ──
    logger.info(f"[{TAG}] Fetching student profile (id={student_id})...")
    student_data = get_student(student_id)
    if not student_data:
        logger.error(f"[{TAG}] Student id={student_id} not found in Supabase.")
        return {"error": f"Student profile not found for id={student_id}."}
    student = student_data[0]
    logger.info(f"[{TAG}] ✅ Student: {student.get('name')} | Target: {student.get('target_role')}")

    # ── Stage 4: Build prompt ──
    logger.info(f"[{TAG}] Building prompt...")
    prompt = _build_skill_prompt(skill, resources, student)

    # ── Stage 5: Call shared Gemini service ──
    logger.info(f"[{TAG}] Calling shared Gemini service...")
    result = generate_json_response(
        prompt=prompt,
        required_keys=REQUIRED_KEYS,
        tag=TAG,
        retries=1,
        max_tokens=4096,
    )

    if result:
        logger.info(f"[{TAG}] ✅ Learning plan generated — {len(result.get('learning_plan', []))} weeks, "
                     f"{len(result.get('projects', []))} projects, {len(result.get('placement_tips', []))} tips.")
        result["is_fallback"] = False
        return result

    # ── Fallback ──
    logger.warning(f"[{TAG}] ⚠️  Gemini failed — returning database-driven fallback.")
    return _generate_fallback(skill_name, skill, resources)


# ── AI Generation for New Skills (Not in Database) ─────────────────────────

def _build_new_skill_prompt(skill_name: str, student: dict) -> str:
    """
    Builds a combined prompt asking Gemini to act as a career mentor,
    generate the skill profile metadata, curate resources, and design a personalized roadmap.
    Uses aggressive adaptation rules to ensure genuinely different roadmaps per student profile.
    """
    year = student.get('year', 'Unknown')
    hours = student.get('daily_hours', 2)
    role = student.get('target_role', 'SDE')
    name = student.get('name', 'Student')

    return f"""You are AcadMate's AI Career Mentor — an expert in tech skill development and placement preparation.
You are analyzing a skill that is NOT currently in our database: "{skill_name}".
Your job is to generate the complete skill profile, recommend high-quality resources, and design a DEEPLY PERSONALIZED learning roadmap.

=== STUDENT PROFILE (USE THIS TO PERSONALIZE EVERYTHING) ===
Name: {name}
Year of Study: {year}
Target Career Role: {role}
Daily Study Hours Available: {hours} hours/day

=== MANDATORY PERSONALIZATION RULES ===
The roadmap you generate MUST be fundamentally different based on the student profile above.
Two students with different profiles searching for the same skill should receive COMPLETELY DIFFERENT roadmaps.

** RULE 1 — YEAR OF STUDY DRIVES DEPTH & PACE **
- "1st Year": 
  → Start with absolute fundamentals and prerequisites. Assume minimal prior knowledge.
  → Spread the plan over MORE weeks (6-8+ weeks). Each week covers ONE small topic.
  → Projects should be simple (guided tutorials, mini-exercises).
  → Placement tips should focus on building foundations, NOT interviews.
- "2nd Year":
  → Assume basic CS knowledge. Move faster through fundamentals.
  → 4-6 week plan. Mix theory with hands-on practice.
  → Projects should be small-to-medium scope.
- "3rd Year":
  → Assume solid CS fundamentals. Skip basics, go to intermediate/advanced.
  → 4-5 week plan. More hands-on, fewer reading tasks.
  → Projects should be portfolio-worthy. Mention GitHub showcase.
- "Final Year":
  → SKIP ALL BASICS. Jump straight into practical, advanced usage.
  → 3-4 week ACCELERATED plan. Every week is project-heavy.
  → Projects must be production-grade, interview-demo-ready.
  → Placement tips MUST include specific interview questions, system design prep, and mock interview strategies.

** RULE 2 — DAILY HOURS DRIVES TASK VOLUME **
- {hours} hours/day is the student's available time. Use this to compute task load:
  → If {hours} <= 2: Each week should have 2-3 SHORT tasks (reading, watching a video, tiny exercise). Do NOT overload.
  → If {hours} == 3-4: Each week should have 3-5 tasks mixing theory and practice.
  → If {hours} >= 5: Each week should have 5-7 INTENSIVE tasks including building projects, solving problems, and reading papers. Push the student hard.
- The total number of weeks should also adapt: fewer hours = more weeks to cover the same material.

** RULE 3 — TARGET ROLE DRIVES CONTENT FOCUS **
The student's target role is "{role}". This changes EVERYTHING about which projects, resources, and tips you recommend:
- "AI Engineer" / "ML Engineer" / "Data Scientist" → Projects must involve ML models, GenAI pipelines, data processing, LLM fine-tuning, RAG systems. Tips should cover ML system design interviews.
- "Software Engineer" / "SDE" / "Backend Developer" → Projects must involve API design, databases, system architecture, scalability. Tips should cover DSA, LLD/HLD interviews.
- "Frontend Developer" / "Fullstack Developer" → Projects must involve UI/UX, responsive design, state management, API integration. Tips should cover frontend system design.
- "DevOps" / "Cloud Engineer" / "Platform Engineer" → Projects must involve CI/CD, containerization, cloud deployment, monitoring. Tips should cover infrastructure design.
- For any other role: infer the closest match and tailor accordingly.

=== CRITICAL RULES ===
- Return ONLY valid JSON. No markdown. No code blocks. No explanatory text.
- The learning_plan MUST have at least 3 weeks.
- Generate at least 3 resources with realistic URLs (official docs, YouTube, Coursera, etc.).
- Generate at least 2 specific project ideas.
- Generate at least 3 placement tips specific to "{role}" and "{skill_name}".

=== REQUIRED JSON STRUCTURE ===
Return ONLY valid JSON matching this exact structure:
{{
  "skill_metadata": {{
    "skill_name": "{skill_name}",
    "category": "Main technology category (e.g. AI / ML, DevOps, Frontend, Backend, Database)",
    "difficulty": "Beginner, Intermediate, or Advanced",
    "estimated_duration": "Estimated time to master (e.g. 2-3 Months)",
    "prerequisites": "Prerequisites separated by commas",
    "career_benefits": "Why learning this skill is beneficial for a {role}",
    "roadmap": "High-level learning path phases separated by →",
    "project_ideas": "2-3 project names separated by semicolons"
  }},
  "resources": [
    {{
      "title": "Resource title",
      "type": "Documentation, Video, Course, or Tutorial",
      "url": "Realistic URL",
      "difficulty": "Beginner, Intermediate, or Advanced"
    }}
  ],
  "learning_plan": [
    {{
      "week": 1,
      "focus": "Clear focus for this week",
      "tasks": ["Specific task 1", "Specific task 2"],
      "resources": ["Relevant resource name"]
    }}
  ],
  "projects": [
    {{
      "name": "Project Name tailored to {role}",
      "difficulty": "Beginner, Intermediate, or Advanced",
      "description": "Detailed project description"
    }}
  ],
  "placement_tips": [
    "Interview/placement tip for {role} related to {skill_name}"
  ]
}}"""


def generate_new_skill_and_roadmap(skill_name: str, student_id) -> Optional[Dict[str, Any]]:
    """
    Generates a full skill profile + personalized roadmap for a skill not in the database.
    """
    TAG = "Skill Agent AI Generator"

    # 1. Fetch student profile
    logger.info(f"[{TAG}] Fetching student profile (id={student_id})...")
    student_data = get_student(student_id)
    if not student_data:
        logger.error(f"[{TAG}] Student id={student_id} not found in Supabase.")
        return None
    student = student_data[0]

    # 2. Build combined prompt
    prompt = _build_new_skill_prompt(skill_name, student)

    # 3. Call Gemini
    logger.info(f"[{TAG}] Calling shared Gemini to generate new skill metadata and roadmap...")
    result = generate_json_response(
        prompt=prompt,
        required_keys=REQUIRED_NEW_SKILL_KEYS,
        tag=TAG,
        retries=1,
        max_tokens=4096,
    )

    if result:
        result["is_fallback"] = False
        
    return result