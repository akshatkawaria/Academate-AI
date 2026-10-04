"""
Opportunities Agent — Fetches, filters, and ranks opportunities.

Sources:
  1. Local dataset (datasets/opportunities.json) — always available (fallback)
  2. Smart cache — automatically refreshed from Apify every 24 hours

Cache Strategy:
  - On first request: triggers background Apify scrape, returns static data
  - Once cached: returns cached data instantly (< 1ms)
  - Every 24 hours: triggers a fresh background scrape automatically
  - If scrape fails: falls back to existing cache or static dataset

Filtering:
  - Removes expired events (deadline <= today)
  - Filters by type (hackathon/internship/all)
  - Filters by mode (online/offline/hybrid/all)
  - Filters by level (undergraduate/postgraduate/all)
  - Filters by location with nearby-city expansion
  - Matches interests/skills against skills, domain, and tags fields

Sorting:
  - Nearest deadline first
"""
import json
import os
from datetime import datetime, date
from typing import List, Optional

DATASET_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "datasets", "opportunities.json"
)

# Nearby city clusters — selecting one city also shows its neighbors + Online
NEARBY_CITIES = {
    "Bangalore": ["Bangalore", "Hyderabad", "Chennai", "Online"],
    "Hyderabad": ["Hyderabad", "Bangalore", "Chennai", "Online"],
    "Chennai": ["Chennai", "Bangalore", "Hyderabad", "Online"],
    "Delhi NCR": ["Delhi NCR", "Noida", "Gurgaon", "Gurugram", "Online"],
    "Mumbai": ["Mumbai", "Pune", "Online"],
    "Pune": ["Pune", "Mumbai", "Online"],
    "Kolkata": ["Kolkata", "Online"],
}


def load_local_opportunities() -> List[dict]:
    """Load the static fallback dataset."""
    try:
        with open(DATASET_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[OpportunityAgent] Failed to load local dataset: {e}")
        return []


def load_cached_opportunities() -> List[dict]:
    """
    Load live scraped data using the smart cache system.
    - Returns cached data if fresh (< 24h old)
    - Triggers background Apify scrape if cache is stale
    - Never blocks the API request
    """
    try:
        from backend.services.opportunity_cache import refresh_cache_if_needed
        return refresh_cache_if_needed()
    except Exception as e:
        print(f"[OpportunityAgent] Cache system failed: {e}")
        return []


def parse_deadline(deadline_str: str) -> Optional[date]:
    """Parse a deadline string into a date object."""
    if not deadline_str:
        return None
    for fmt in ("%Y-%m-%d", "%d %b %Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(deadline_str.strip(), fmt).date()
        except ValueError:
            continue
    return None


def get_opportunities(
    interests: List[str],
    opp_type: str = "all",
    mode: str = "all",
    level: str = "all",
    location: str = "all",
    include_live: bool = False,
) -> List[dict]:
    """
    Main entry point for the Opportunity Agent.
    Returns a FLAT LIST of filtered, sorted opportunity dicts.

    When include_live=True:
      - Uses the smart cache (auto-refreshed from Apify every 24h)
      - Merges cached live data with the static dataset
      - Deduplicates by title

    When include_live=False:
      - Uses only the static dataset (fast, no external calls)
    """
    # 1. Load static fallback data (always available)
    all_opps = load_local_opportunities()

    if include_live:
        # Smart cache: returns cached Apify data or triggers background refresh
        live_opps = load_cached_opportunities()

        # Deduplicate by title (case-insensitive)
        existing_titles = {o.get("title", "").lower() for o in all_opps}
        for opp in live_opps:
            if opp.get("title", "").lower() not in existing_titles:
                all_opps.append(opp)
                existing_titles.add(opp.get("title", "").lower())

    today = date.today()
    results = []

    # Build the allowed location set for filtering
    allowed_locations = None
    if location and location.lower() != "all":
        loc_title = location.strip().title()
        # Expand to nearby cities
        if loc_title in NEARBY_CITIES:
            allowed_locations = {c.lower() for c in NEARBY_CITIES[loc_title]}
        else:
            allowed_locations = {loc_title.lower(), "online"}

    for opp in all_opps:
        # 2. Filter expired events
        deadline = parse_deadline(opp.get("deadline", ""))
        if deadline is None or deadline <= today:
            continue

        # 3. Filter by type
        if opp_type != "all" and opp.get("type", "").lower() != opp_type.lower():
            continue

        # 4. Filter by mode
        if mode != "all" and opp.get("mode", "").lower() != mode.lower():
            continue

        # 5. Filter by level
        opp_level = opp.get("level", "all").lower()
        if level != "all" and opp_level != "all" and opp_level != level.lower():
            continue

        # 6. Filter by location
        if allowed_locations:
            opp_location = (opp.get("location", "") or "").lower()
            if opp_location not in allowed_locations:
                continue

        # 7. Filter by interests/skills
        if interests:
            # Build a searchable set from skills, domain, and tags
            searchable = set()
            for field in ("skills", "domain", "tags"):
                vals = opp.get(field, [])
                if isinstance(vals, list):
                    searchable.update(v.lower() for v in vals)
                elif isinstance(vals, str):
                    searchable.add(vals.lower())

            # Check if ANY interest matches
            interests_lower = [i.strip().lower() for i in interests if i.strip()]
            if interests_lower and not any(i in searchable for i in interests_lower):
                continue

        # 8. Add computed fields
        opp_copy = dict(opp)
        opp_copy["days_left"] = (deadline - today).days
        results.append(opp_copy)

    # 9. Sort by nearest deadline
    results.sort(key=lambda x: x.get("deadline", "9999-12-31"))

    return results
