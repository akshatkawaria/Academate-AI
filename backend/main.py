"""
AcadMate AI — FastAPI Backend Entry Point
"""
import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.database import init_db
from backend.api.routes import (
    profile,
    schedule,
    progress,
    recommendations,
    opportunities,
    notifications,
    skills,
    placement,
    dashboard
)

app = FastAPI(
    title="AcadMate AI API",
    description="Multi-agent AI platform for academic and placement management",
    version="1.0.0"
)


# CORS — allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.planner import planner_controller

# Register all routers
app.include_router(profile.router)
app.include_router(schedule.router)
app.include_router(progress.router)
app.include_router(recommendations.router)
app.include_router(opportunities.router)
app.include_router(notifications.router)
app.include_router(planner_controller.router)
app.include_router(skills.router)
app.include_router(placement.router)
app.include_router(dashboard.router)

@app.on_event("startup")
def on_startup():
    init_db()
    print("AcadMate AI backend started. Database initialized.")
    # Seed placement skill data
    try:
        from backend.database.database import SessionLocal
        from backend.agents.placement_seed import seed_placement_data
        db = SessionLocal()
        seed_placement_data(db)
        db.close()
    except Exception as e:
        print(f"[Startup] Placement seed skipped: {e}")

    # Warm the opportunity cache — triggers background Apify scrape if stale
    try:
        from backend.services.opportunity_cache import is_cache_stale, _trigger_background_scrape
        stale, last_scraped = is_cache_stale()
        if stale:
            print("[Startup] Opportunity cache is stale or missing — triggering background refresh...")
            _trigger_background_scrape()
        else:
            print(f"[Startup] Opportunity cache is fresh (last scraped: {last_scraped})")
    except Exception as e:
        print(f"[Startup] Cache warmup skipped: {e}")


@app.get("/")
def root():
    return {
        "app": "AcadMate AI",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}



