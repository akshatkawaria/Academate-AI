"""
Smart Cache Manager for Opportunity Scraping

Handles:
  - Local file-based caching of scraped opportunities
  - 24-hour TTL with automatic refresh detection
  - Thread-safe read/write with reentrant locking
  - Background scrape triggering (non-blocking for API requests)
  - Graceful fallback to static dataset on failure
"""
import os
import json
import time
import threading
from datetime import datetime, timezone
from typing import List, Optional, Tuple

# Cache file sits alongside the static dataset
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "datasets")
CACHE_FILE = os.path.join(CACHE_DIR, "opportunities_cache.json")

# 24 hours in seconds
CACHE_TTL_SECONDS = 24 * 60 * 60

# Reentrant lock for safe concurrent access (RLock allows same thread to re-acquire)
_cache_lock = threading.RLock()

# Flag to prevent multiple simultaneous scrape triggers
_scrape_in_progress = False
_scrape_lock = threading.Lock()


def _read_cache_raw() -> Optional[dict]:
    """
    Read the cache file WITHOUT locking. Internal use only.
    Caller must hold _cache_lock.
    """
    try:
        if not os.path.exists(CACHE_FILE):
            return None
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "opportunities" not in data:
            return None
        return data
    except (json.JSONDecodeError, IOError, OSError) as e:
        print(f"[Cache] Failed to read cache: {e}")
        return None


def _read_cache() -> Optional[dict]:
    """
    Read the cache file (thread-safe).
    Returns the full cache envelope or None.
    """
    with _cache_lock:
        return _read_cache_raw()


def _write_cache(opportunities: List[dict]) -> bool:
    """
    Write opportunities to the cache file with metadata.
    Returns True on success.
    """
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)

        with _cache_lock:
            # Read existing to increment scrape count (inside same lock)
            existing = _read_cache_raw()
            prev_count = existing.get("scrape_count", 0) if existing else 0

            now = datetime.now(timezone.utc)
            envelope = {
                "last_scraped_at": now.isoformat(),
                "last_scraped_unix": int(now.timestamp()),
                "scrape_count": prev_count + 1,
                "item_count": len(opportunities),
                "opportunities": opportunities,
            }

            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(envelope, f, indent=2, ensure_ascii=False)

        print(f"[Cache] Saved {len(opportunities)} opportunities to cache. "
              f"Scrape #{prev_count + 1}")
        return True

    except (IOError, OSError) as e:
        print(f"[Cache] Failed to write cache: {e}")
        return False


def is_cache_stale() -> Tuple[bool, Optional[str]]:
    """
    Check if the cache is stale (older than 24 hours or missing).
    Returns (is_stale: bool, last_scraped_at: str | None).
    """
    cache = _read_cache()
    if cache is None:
        return True, None

    last_unix = cache.get("last_scraped_unix", 0)
    if last_unix == 0:
        return True, None

    age_seconds = time.time() - last_unix
    last_scraped = cache.get("last_scraped_at", "unknown")

    if age_seconds > CACHE_TTL_SECONDS:
        hours_ago = round(age_seconds / 3600, 1)
        print(f"[Cache] Cache is stale — last scraped {hours_ago}h ago ({last_scraped})")
        return True, last_scraped

    hours_ago = round(age_seconds / 3600, 1)
    print(f"[Cache] Cache is fresh — {hours_ago}h old ({last_scraped})")
    return False, last_scraped


def get_cached_opportunities() -> List[dict]:
    """
    Return cached opportunities if available, else empty list.
    """
    cache = _read_cache()
    if cache is None:
        return []
    return cache.get("opportunities", [])


def get_cache_status() -> dict:
    """
    Return full cache status info for the API.
    """
    cache = _read_cache()
    if cache is None:
        return {
            "has_cache": False,
            "is_stale": True,
            "last_scraped_at": None,
            "age_hours": None,
            "item_count": 0,
            "scrape_count": 0,
            "scrape_in_progress": _scrape_in_progress,
        }

    last_unix = cache.get("last_scraped_unix", 0)
    age_seconds = time.time() - last_unix if last_unix else 0
    is_stale = age_seconds > CACHE_TTL_SECONDS

    return {
        "has_cache": True,
        "is_stale": is_stale,
        "last_scraped_at": cache.get("last_scraped_at"),
        "age_hours": round(age_seconds / 3600, 2),
        "item_count": cache.get("item_count", 0),
        "scrape_count": cache.get("scrape_count", 0),
        "scrape_in_progress": _scrape_in_progress,
    }


def refresh_cache_if_needed() -> List[dict]:
    """
    Main entry point for smart caching.

    Logic:
      1. If cache is fresh (< 24h) → return cached data immediately
      2. If cache is stale or missing → trigger background scrape,
         return existing cached data (or empty) in the meantime
      3. Background scrape saves new data to cache on completion

    This keeps the API fast — never blocks on a scrape.
    """
    stale, last_scraped = is_cache_stale()

    if not stale:
        # Cache is fresh, return it
        return get_cached_opportunities()

    # Cache is stale — trigger background refresh
    _trigger_background_scrape()

    # Return whatever we have cached right now (may be stale but usable)
    cached = get_cached_opportunities()
    if cached:
        print(f"[Cache] Returning {len(cached)} stale-but-usable cached items "
              f"while background scrape runs.")
    return cached


def _trigger_background_scrape():
    """
    Launch an Apify scrape in a background thread.
    Only one scrape runs at a time (guarded by _scrape_in_progress flag).
    """
    global _scrape_in_progress

    with _scrape_lock:
        if _scrape_in_progress:
            print("[Cache] Background scrape already in progress — skipping.")
            return
        _scrape_in_progress = True

    thread = threading.Thread(target=_do_scrape, daemon=True)
    thread.start()
    print("[Cache] Background scrape thread started.")


def _do_scrape():
    """
    Perform the actual Apify scrape and save results to cache.
    Runs in a background thread.
    """
    global _scrape_in_progress
    try:
        from backend.services.opportunity_scraper import fetch_from_apify_fresh
        results = fetch_from_apify_fresh()

        if results:
            _write_cache(results)
            print(f"[Cache] Background scrape complete — {len(results)} items cached.")
        else:
            print("[Cache] Background scrape returned 0 items — keeping existing cache.")

    except Exception as e:
        print(f"[Cache] Background scrape failed: {e}")

    finally:
        with _scrape_lock:
            _scrape_in_progress = False


def force_refresh() -> dict:
    """
    Force a synchronous cache refresh. Used for manual/admin triggers.
    Blocks until the scrape completes.
    """
    global _scrape_in_progress

    with _scrape_lock:
        if _scrape_in_progress:
            return {
                "status": "already_running",
                "message": "A scrape is already in progress. Please wait."
            }
        _scrape_in_progress = True

    try:
        from backend.services.opportunity_scraper import fetch_from_apify_fresh
        results = fetch_from_apify_fresh()

        if results:
            _write_cache(results)
            return {
                "status": "success",
                "message": f"Scraped and cached {len(results)} opportunities.",
                "item_count": len(results),
            }
        else:
            return {
                "status": "empty",
                "message": "Scrape returned 0 items. Existing cache preserved.",
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Scrape failed: {e}",
        }

    finally:
        with _scrape_lock:
            _scrape_in_progress = False
