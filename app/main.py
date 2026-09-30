"""FitBuddy - FastAPI entry point.

Run from the project root:
    uvicorn app.main:app --reload
"""
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import app.config  # noqa: F401  (loads .env before anything else)
from app.database import init_db
from app.routes import router

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(
    title="FitBuddy - AI Fitness Plan Generator",
    description="Personalized 7-day workout plans and nutrition tips powered by Google Gemini.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

init_db()
app.include_router(router)
