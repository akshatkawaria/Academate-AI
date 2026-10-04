import logging
from backend.planner.logic_engine import build_core_schedule
from backend.planner.prompt_builder import build_planner_prompt
from backend.planner.gemini_service import get_planner_ai_response

logger = logging.getLogger(__name__)

def generate_schedule(user_data: dict, target_date: str) -> dict:
    """
    Core function of the Planner Agent with new architecture:
    User Inputs -> Priority Engine -> Hour Allocation -> Time Slot Generation -> Gemini Enhancement -> Final JSON
    """
    try:
        # Step 1-6: Backend Deterministic Scheduling Engine
        core_schedule = build_core_schedule(user_data)
        
        # Step 7: Gemini Enhancement
        prompt = build_planner_prompt(user_data, core_schedule, target_date)
        ai_response = get_planner_ai_response(prompt)
        
        if ai_response and validate_planner_response(ai_response):
            return ai_response
            
    except Exception as e:
        logger.error(f"Planner Agent error during scheduling or AI enhancement: {e}")
        
    # Fallback: Just return the deterministic core schedule! It's already fully formed.
    logger.warning("Planner Agent falling back to deterministic core schedule.")
    
    # We might need the core_schedule here even if an exception occurred earlier. 
    # Let's ensure we can generate it independently.
    try:
        return build_core_schedule(user_data)
    except Exception as e:
        logger.error(f"Fallback generation failed: {e}")
        # Ultimate fail-safe
        return {
            "plan_summary": {"academic_focus": 50, "placement_focus": 50, "reason": "Ultimate fallback."},
            "schedule": [],
            "productivity_advice": ["Take it easy today, system encountered an error."]
        }

def validate_planner_response(response: dict) -> bool:
    """Strict validation to ensure the response has the required structure."""
    if not isinstance(response, dict): return False
    if "plan_summary" not in response or "schedule" not in response: return False
    if not isinstance(response["schedule"], list): return False
    
    # Check if schedule items have required fields
    for item in response["schedule"]:
        if not all(k in item for k in ["start_time", "end_time", "task_name", "task_type", "priority", "reason"]):
            return False
            
    return True
