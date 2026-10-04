"""
Opportunities API Routes

GET  /api/opportunities/          — list & filter opportunities (uses smart cache)
GET  /api/opportunities/featured  — top 5 nearest-deadline opportunities
POST /api/opportunities/filter    — filter with JSON body
GET  /api/opportunities/live      — fetch + merge live cached data
GET  /api/opportunities/cache     — check cache status (age, freshness, counts)
POST /api/opportunities/refresh   — force a synchronous cache refresh
"""
from fastapi import APIRouter, Query
from backend.agents.opportunities_agent import get_opportunities
from backend.services.opportunity_cache import get_cache_status, force_refresh
from typing import Optional, List

router = APIRouter(prefix="/api/opportunities", tags=["Opportunities"])


@router.get("/")
def list_opportunities(
    interests: Optional[str] = Query(None, description="Comma-separated interests/skills"),
    type: str = Query("all", description="hackathon | internship | all"),
    mode: str = Query("all", description="online | offline | hybrid | all"),
    level: str = Query("all", description="undergraduate | postgraduate | all"),
    location: str = Query("all", description="Bangalore | Hyderabad | Chennai | Delhi NCR | Mumbai | Pune | Online | all"),
):
    """
    Returns a FLAT JSON array of upcoming opportunities.
    Uses smart cache: automatically refreshes Apify data every 24 hours.
    Filters out expired events automatically.
    Location filter expands to nearby cities (e.g., Bangalore also shows Hyderabad, Chennai).
    """
    interest_list = [i.strip() for i in interests.split(",") if i.strip()] if interests else []
    return get_opportunities(interest_list, type, mode, level, location, include_live=True)


@router.get("/featured")
def featured_opportunities():
    """Top 5 nearest-deadline opportunities across all types."""
    results = get_opportunities([], "all", "all", "all", "all", include_live=False)
    return results[:5]


@router.get("/cache")
def cache_status():
    """
    Check the current cache status.
    Returns:
      - has_cache: whether a cache file exists
      - is_stale: whether the cache is older than 24 hours
      - last_scraped_at: ISO timestamp of last scrape
      - age_hours: how old the cache is in hours
      - item_count: number of cached opportunities
      - scrape_count: total scrapes performed
      - scrape_in_progress: whether a background scrape is running
    """
    return get_cache_status()


@router.post("/refresh")
def refresh_cache():
    """
    Force a synchronous cache refresh.
    Triggers a fresh Apify scrape and waits for completion.
    Use sparingly — this blocks until the scrape finishes (~30-60s).
    """
    return force_refresh()


@router.get("/live")
def live_opportunities(
    interests: Optional[str] = Query(None),
    type: str = Query("all"),
    location: str = Query("all"),
):
    """Fetch live data from smart cache + merge with local dataset."""
    interest_list = [i.strip() for i in interests.split(",") if i.strip()] if interests else []
    return get_opportunities(interest_list, type, "all", "all", location, include_live=True)


@router.post("/filter")
def filter_opportunities(req: dict):
    """Filter with a JSON body: {interests: [...], type: "...", mode: "...", level: "...", location: "..."}"""
    return get_opportunities(
        req.get("interests", []),
        req.get("type", "all"),
        req.get("mode", "all"),
        req.get("level", "all"),
        req.get("location", "all"),
        include_live=req.get("include_live", False),
    )
