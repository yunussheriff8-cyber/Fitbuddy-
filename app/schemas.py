"""Pydantic models used to validate request data."""
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class UserInput(BaseModel):
    user_id: int = Field(..., ge=1)
    username: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=10, le=100)
    weight: float = Field(..., gt=20, lt=400, description="Weight in kg")
    goal: str = Field(..., min_length=2, max_length=200)
    intensity: Literal["low", "medium", "high"]

    @field_validator("intensity", mode="before")
    @classmethod
    def normalise_intensity(cls, value):
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("username", "goal")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class WorkoutRequest(BaseModel):
    goal: str = Field(..., min_length=2, max_length=200)
    intensity: Literal["low", "medium", "high"]

    @field_validator("intensity", mode="before")
    @classmethod
    def normalise_intensity(cls, value):
        return value.strip().lower() if isinstance(value, str) else value


class FeedbackRequest(BaseModel):
    feedback: str = Field(..., min_length=3, max_length=1000)
