from backend.agents.planner_agent import generate_daily_schedule
from backend.agents.progress_agent import get_weekly_summary
from backend.agents.placement_agent import analyze_placement_readiness
from backend.agents.opportunities_agent import get_opportunities

class AgentOrchestrator:
    """
    Central Orchestrator to ensure:
    - Only the required agent is called.
    - Agents do not communicate directly.
    - Gemini API calls are strictly sequential to protect the Free Tier.
    """
    
    @staticmethod
    def run_planner(user_profile: dict, target_date: str) -> list:
        # Strictly run Planner
        return generate_daily_schedule(user_profile, target_date)
        
    @staticmethod
    def run_progress(progress_records: list) -> dict:
        # Strictly run Progress analysis
        return get_weekly_summary(progress_records)
        
    @staticmethod
    def run_placement(user_profile: dict) -> dict:
        # Strictly run Placement analysis
        return analyze_placement_readiness(user_profile)
        
    @staticmethod
    def run_opportunities(interests: list, opp_type: str = "all", mode: str = "all", level: str = "all", include_live: bool = False) -> list:
        # Strictly run Opportunities search
        return get_opportunities(interests, opp_type, mode, level, include_live)

orchestrator = AgentOrchestrator()
