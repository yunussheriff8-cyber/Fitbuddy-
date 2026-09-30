"""Feedback-based plan updating with Gemini Pro."""
from app.config import GEMINI_PRO_MODEL, run_prompt


def update_workout_plan(original_plan: str, user_feedback: str) -> str:
    """Use Gemini Pro to update the workout plan based on user feedback."""
    prompt = f"""
You are a professional fitness trainer assistant.

Here's the original 7-day workout plan:
{original_plan}

User Feedback:
"{user_feedback}"

Based on the feedback, revise the relevant parts of the workout plan. Keep the format and rest of the plan unchanged if not needed.
Return the complete updated 7-day plan.
"""
    return run_prompt(GEMINI_PRO_MODEL, prompt)
