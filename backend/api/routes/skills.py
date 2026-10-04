from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.agents.skill_agent import generate_learning_plan, generate_new_skill_and_roadmap
from backend.services.skill_service import get_skill, add_skill
from backend.services.resource_service import get_resources, add_resources
from backend.services.student_service import get_student, update_student

router = APIRouter(prefix="/api/skills", tags=["skills"])

class SkillGenerateRequest(BaseModel):
    skill_name: str
    student_id: int

class StudentProfileUpdateRequest(BaseModel):
    name: str
    year: str
    target_role: str
    daily_hours: int

@router.get("/profile/{student_id}")
def get_student_profile(student_id: int):
    student_data = get_student(student_id)
    if not student_data:
        raise HTTPException(status_code=404, detail=f"Student profile not found for id={student_id}.")
    return student_data[0]

@router.put("/profile/{student_id}")
def update_student_profile(student_id: int, request: StudentProfileUpdateRequest):
    updated_data = update_student(student_id, request.model_dump())
    if not updated_data:
        raise HTTPException(status_code=404, detail=f"Student profile not found for id={student_id}.")
    return updated_data[0]

@router.get("/check/{skill_name}")
def check_skill_exists(skill_name: str):
    skill_data = get_skill(skill_name)
    return {"exists": len(skill_data) > 0}

@router.post("/generate")
def generate_skills(request: SkillGenerateRequest):
    student_data = get_student(request.student_id)
    if not student_data:
        raise HTTPException(status_code=404, detail=f"Student profile not found for id={request.student_id}.")
    student = student_data[0]

    # 1. Search skill in Supabase Skills table
    skill_data = get_skill(request.skill_name)
    
    if skill_data:
        # Existing Skill Flow
        skill = skill_data[0]
        raw_resources = get_resources(request.skill_name) or []
        resources = []
        for r in raw_resources:
            resources.append({
                "title": r.get("title", "Resource"),
                "type": r.get("resource_type") or r.get("type", "Documentation"),
                "url": r.get("url", "https://google.com"),
                "difficulty": r.get("difficulty", "Intermediate")
            })
        
        plan = generate_learning_plan(request.skill_name, request.student_id)
        if "error" in plan:
            raise HTTPException(status_code=500, detail=plan["error"])
            
        return {
            "student": student,
            "skill": skill,
            "resources": resources,
            "learning_plan": plan.get("learning_plan", []),
            "projects": plan.get("projects", []),
            "placement_tips": plan.get("placement_tips", []),
            "is_fallback": plan.get("is_fallback", False)
        }
    else:
        # New Skill - Generate via Gemini & Save to Supabase
        ai_data = generate_new_skill_and_roadmap(request.skill_name, request.student_id)
        if not ai_data or "skill_metadata" not in ai_data:
            # Gemini failed and skill not in Supabase -> raise fallback error
            raise HTTPException(
                status_code=503, 
                detail="Unable to generate roadmap right now. Please try again later."
            )
            
        generated_metadata = ai_data["skill_metadata"]
        generated_resources = ai_data["resources"]
        
        # Save newly generated skill metadata into Supabase Skills table
        try:
            skill_insert_data = {
                "skill_name": request.skill_name,
                "category": generated_metadata.get("category", "General"),
                "difficulty": generated_metadata.get("difficulty", "Intermediate"),
                "estimated_duration": generated_metadata.get("estimated_duration", "4 weeks"),
                "prerequisites": generated_metadata.get("prerequisites", ""),
                "roadmap": generated_metadata.get("roadmap", ""),
                "project_ideas": generated_metadata.get("project_ideas", ""),
                "career_benefits": generated_metadata.get("career_benefits", "")
            }
            add_skill(skill_insert_data)
        except Exception as e:
            print(f"[API Warning] Failed to save generated skill to Supabase: {e}")
            
        # Save newly generated resources into Supabase skill_resources table
        saved_resources = []
        try:
            resource_insert_data = []
            for r in generated_resources:
                resource_insert_data.append({
                    "skill_name": request.skill_name,
                    "title": r.get("title", "Resource"),
                    "resource_type": r.get("type", "Documentation"),
                    "url": r.get("url", "https://google.com"),
                    "difficulty": r.get("difficulty", "Intermediate")
                })
            if resource_insert_data:
                saved_resources = add_resources(resource_insert_data)
        except Exception as e:
            print(f"[API Warning] Failed to save generated resources to Supabase: {e}")
            saved_resources = resource_insert_data # fallback to raw list
            
        # Format resources to map resource_type to type for frontend consumption
        formatted_resources = []
        for r in (saved_resources or resource_insert_data):
            formatted_resources.append({
                "title": r.get("title", "Resource"),
                "type": r.get("resource_type") or r.get("type", "Documentation"),
                "url": r.get("url", "https://google.com"),
                "difficulty": r.get("difficulty", "Intermediate")
            })
            
        return {
            "student": student,
            "skill": generated_metadata,
            "resources": formatted_resources,
            "learning_plan": ai_data.get("learning_plan", []),
            "projects": ai_data.get("projects", []),
            "placement_tips": ai_data.get("placement_tips", []),
            "is_fallback": False
        }
