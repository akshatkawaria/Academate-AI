"""
Apify Unstop Hackathon Scraper Integration
Fetches live hackathon/internship data from Unstop via Apify.
Falls back gracefully if Apify is unavailable.
"""
import os
import re
import hashlib
from datetime import datetime, timedelta
from typing import List
from dotenv import load_dotenv

load_dotenv()

# City normalization map for consistent location data
CITY_NORMALIZE = {
    "bengaluru": "Bangalore", "bangalore": "Bangalore",
    "hyderabad": "Hyderabad", "secunderabad": "Hyderabad",
    "chennai": "Chennai", "madras": "Chennai",
    "delhi": "Delhi NCR", "new delhi": "Delhi NCR", "noida": "Delhi NCR",
    "gurgaon": "Delhi NCR", "gurugram": "Delhi NCR",
    "mumbai": "Mumbai", "bombay": "Mumbai", "navi mumbai": "Mumbai",
    "pune": "Pune",
    "kolkata": "Kolkata", "calcutta": "Kolkata",
}


def _normalize_location(raw: str) -> str:
    """Normalize a raw location string to a standard city name."""
    if not raw:
        return "Online"
    lower = raw.strip().lower()
    if "online" in lower or "virtual" in lower or "remote" in lower:
        return "Online"
    for keyword, city in CITY_NORMALIZE.items():
        if keyword in lower:
            return city
    # If it has "India" / "IN" but no recognized city, return the raw cleaned
    return raw.strip().title() if len(raw.strip()) < 40 else "Online"


def _extract_deadline(item: dict) -> str:
    """
    Try to extract a real deadline from multiple possible Apify fields.
    Falls back to hash-based generation only as a last resort.
    """
    today = datetime.today().date()

    # Try known Apify fields for deadline/end date
    for field in ("deadline", "endDate", "end_date", "registrationEndDate",
                  "registration_deadline", "lastDate", "last_date"):
        raw = item.get(field)
        if not raw:
            continue
        for fmt in ("%Y-%m-%d", "%d %b %Y", "%d-%m-%Y", "%Y-%m-%dT%H:%M:%S",
                    "%d/%m/%Y", "%B %d, %Y", "%b %d, %Y"):
            try:
                parsed = datetime.strptime(str(raw).strip()[:19], fmt).date()
                if parsed > today:
                    return parsed.isoformat()
            except ValueError:
                continue

    # Try to extract a date from the rawText
    raw_text = item.get("rawText", "") or ""
    date_patterns = [
        r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})',
        r'(\d{4}-\d{2}-\d{2})',
    ]
    for pat in date_patterns:
        match = re.search(pat, raw_text, re.IGNORECASE)
        if match:
            for fmt in ("%d %B %Y", "%d %b %Y", "%Y-%m-%d"):
                try:
                    parsed = datetime.strptime(match.group(1).strip(), fmt).date()
                    if parsed > today:
                        return parsed.isoformat()
                except ValueError:
                    continue

    # Fallback: deterministic but varied offset based on title hash
    title = item.get("title", "untitled")
    h = int(hashlib.md5(title.encode("utf-8")).hexdigest(), 16)
    days_offset = 7 + (h % 120)  # 7 to 126 days from today
    return (today + timedelta(days=days_offset)).isoformat()


def _extract_skills(item: dict) -> List[str]:
    """Extract skill tags from Apify item data."""
    skills = []
    # Check for explicit skill/tag fields
    for field in ("skills", "tags", "eligibility"):
        val = item.get(field)
        if isinstance(val, list):
            skills.extend(val)
        elif isinstance(val, str) and val:
            skills.extend([s.strip() for s in val.split(",")])

    if not skills:
        # Infer from title/description
        text = (item.get("title", "") + " " + (item.get("rawText", "") or "")).lower()
        skill_keywords = {
            "python": "Python", "java": "Java", "javascript": "JavaScript",
            "react": "React", "machine learning": "ML", "ml": "ML",
            "ai": "AI", "blockchain": "Blockchain", "web3": "Web3",
            "data science": "Data Science", "cloud": "Cloud",
            "android": "Android", "ios": "iOS", "flutter": "Flutter",
            "cybersecurity": "Cybersecurity", "iot": "IoT",
            "devops": "DevOps", "design": "Design",
        }
        for kw, label in skill_keywords.items():
            if kw in text and label not in skills:
                skills.append(label)

    return skills[:5] if skills else ["Coding", "Problem Solving"]


ACTOR_ID = "trusted_offshoot/unstop-hackathon-scraper"
RUN_INPUT = {
    "startUrls": [
        {"url": "https://unstop.com/hackathons"},
        {"url": "https://unstop.com/internships"}
    ]
}

# Prize pool options for fallback
PRIZE_POOL = [
    "₹50,000", "₹1,00,000", "₹2,50,000", "₹5,00,000",
    "Swag & PPIs", "Job Offer", "₹10,000", "₹3,00,000"
]


def _normalize_items(items, token: str) -> List[dict]:
    """
    Shared normalization logic for raw Apify dataset items.
    Returns a list of cleaned opportunity dicts.
    """
    results = []
    for item in items:
        try:
            title = item.get("title")
            if not title:
                continue

            link_url = item.get("link") or item.get("url") or "#"
            is_internship = "internship" in link_url.lower() or "intern" in title.lower()

            # Extract real deadline
            deadline = _extract_deadline(item)

            # Extract real location
            raw_loc = item.get("location") or item.get("city") or item.get("venue") or ""
            location = _normalize_location(raw_loc)

            # Determine mode from location
            if location == "Online":
                mode = "online"
            elif "hybrid" in (item.get("mode", "") or "").lower():
                mode = "hybrid"
            else:
                mode = "offline"

            # Extract skills
            skills = _extract_skills(item)

            # Prize
            prize = item.get("prize") or item.get("reward") or ""
            if not prize:
                h = int(hashlib.md5(title.encode("utf-8")).hexdigest(), 16)
                prize = PRIZE_POOL[h % len(PRIZE_POOL)]

            # Registration count (extract or generate)
            reg_count = item.get("registrations") or item.get("participants")
            if not reg_count:
                h = int(hashlib.md5(title.encode("utf-8")).hexdigest(), 16)
                reg_count = 500 + (h % 40000)

            results.append({
                "id": f"apify-{title.replace(' ', '-')[:30].lower()}",
                "type": "internship" if is_internship else "hackathon",
                "title": title,
                "organizer": item.get("organizer") or "Unstop",
                "deadline": deadline,
                "mode": mode,
                "location": location,
                "skills": skills,
                "domain": ["General"],
                "tags": ["apify", "live"],
                "prize": prize,
                "link": link_url,
                "description": item.get("rawText") or "Live opportunity — click Apply to learn more.",
                "level": "all",
                "source": "apify",
                "registrations": int(reg_count) if str(reg_count).isdigit() else reg_count,
                "team_size": item.get("team_size") or "See Details",
            })

        except Exception as e:
            print(f"[Scraper] Skipping item: {e}")
            continue

    return results


def fetch_from_apify_fresh() -> List[dict]:
    """
    Trigger a FRESH Apify actor run and return normalized opportunity objects.
    This always starts a new scrape — used by the cache manager for 24h refresh.
    Returns [] on any failure.
    """
    token = os.getenv("APIFY_API_TOKEN", "")
    if not token:
        print("[Scraper] APIFY_API_TOKEN not set — skipping live scrape.")
        return []

    try:
        from apify_client import ApifyClient
        client = ApifyClient(token)

        print("[Scraper] Triggering fresh Apify actor run...")
        run_info = client.actor(ACTOR_ID).call(run_input=RUN_INPUT, memory_mbytes=2048)

        if not run_info:
            print("[Scraper] Failed to start a fresh run on Apify.")
            return []

        dataset_id = run_info.get("defaultDatasetId") if isinstance(run_info, dict) else (getattr(run_info, "default_dataset_id", None) or getattr(run_info, "defaultDatasetId", None))
        items = list(client.dataset(dataset_id).iterate_items())
        results = _normalize_items(items, token)

        print(f"[Scraper] Fresh scrape complete — {len(results)} opportunities.")
        return results

    except ImportError:
        print("[Scraper] apify-client not installed — skipping live scrape.")
        return []
    except Exception as e:
        print(f"[Scraper] Fresh Apify scrape failed: {e}")
        return []


def fetch_from_apify() -> List[dict]:
    """
    [DEPRECATED] Use the cache manager instead.
    Fetches from the last Apify run (may be stale).
    Kept for backward compatibility.
    """
    token = os.getenv("APIFY_API_TOKEN", "")
    if not token:
        print("[Scraper] APIFY_API_TOKEN not set — skipping live scrape.")
        return []

    try:
        from apify_client import ApifyClient
        client = ApifyClient(token)

        # Use the last run to get data instantly (may be stale!)
        run_info = client.actor(ACTOR_ID).last_run().get()
        if not run_info:
            print("[Scraper] No previous run found. Triggering a live scrape...")
            run_info = client.actor(ACTOR_ID).call(run_input=RUN_INPUT, memory_mbytes=2048)

        if not run_info:
            print("[Scraper] Failed to get data from Apify.")
            return []

        dataset_id = run_info.get("defaultDatasetId") if isinstance(run_info, dict) else (getattr(run_info, "default_dataset_id", None) or getattr(run_info, "defaultDatasetId", None))
        items = list(client.dataset(dataset_id).iterate_items())
        results = _normalize_items(items, token)

        print(f"[Scraper] Fetched {len(results)} live opportunities from Apify.")
        return results

    except ImportError:
        print("[Scraper] apify-client not installed — skipping live scrape.")
        return []
    except Exception as e:
        print(f"[Scraper] Apify call failed: {e}")
        return []