import json
from backend.services.gemini_client import get_ai_response
from backend.utils import cache

def analyze_placement_readiness(user: dict) -> dict:
    goal = user.get("placement_goal", "SDE")
    skills = ", ".join(user.get("skills", [])) or "none"
    year = user.get("year", 2)

    # Cache keyed by goal+skills to avoid repeated Gemini calls
    cache_key = f"placement:{goal}:{skills}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    prompt = f"""You are a placement advisor. Return ONLY a JSON object.
Goal: {goal}. Year: {year}. Current skills: {skills}.
Return: {{"readiness_score":72,"missing_skills":["OS","DBMS"],"recommended_focus":["DSA","Projects"]}}"""

    result = get_ai_response(prompt)
    if result and isinstance(result, dict) and "readiness_score" in result:
        cache.set(cache_key, result, ttl_seconds=300)  # Cache 5 mins
        return result

    fallback = {
        "readiness_score": 50,
        "missing_skills": ["Review Core Concepts"],
        "recommended_focus": ["DSA", "Projects"]
    }
    return fallback
