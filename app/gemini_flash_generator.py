"""Nutrition / recovery tips with Gemini Flash."""
from app.config import GEMINI_FLASH_MODEL, run_prompt


def generate_nutrition_tip_with_flash(goal: str) -> str:
    """Generate a nutrition or recovery tip using Gemini Flash based on the user's fitness goal.

    Args:
        goal (str): User's fitness goal - e.g. "weight loss", "muscle gain", or "general fitness".

    Returns:
        str: Generated tip.
    """
    prompt = (
        f"Give one clear, helpful nutrition or recovery tip for someone focused on '{goal}'. "
        "The tip should be practical, friendly, and easy to understand. "
        "Keep it to two or three sentences."
    )
    return run_prompt(GEMINI_FLASH_MODEL, prompt)
