"""Workout plan generation with Gemini Pro."""
from app.config import GEMINI_PRO_MODEL, run_prompt


def generate_workout_gemini(user_input: dict) -> str:
    """Generate a structured 7-day workout plan.

    user_input needs "goal" and "intensity"; "age" and "weight" are
    used too when provided.
    """
    profile = ""
    if user_input.get("age"):
        profile += f"- Age: {user_input['age']}\n"
    if user_input.get("weight"):
        profile += f"- Weight: {user_input['weight']} kg\n"

    prompt = f"""
You are a professional fitness trainer.

Create a personalized, structured 7-day workout plan for someone with the goal of **{user_input['goal']}**, and who prefers **{user_input['intensity']}** intensity workouts.
{('About the person:' + chr(10) + profile) if profile else ''}
Each day must include:
- A warm-up (5-10 mins)
- Main workout (targeted exercises, sets & reps)
- Cooldown or recovery tip

Include rest or active-recovery days where appropriate for the intensity level.
End with a short "Important Notes" section (progressive overload, form, hydration, consulting a doctor before starting).

Format:
Day 1:
Warm-up: ...
Main Workout: ...
Cooldown: ...
(Repeat for Day 2-7)
"""
    return run_prompt(GEMINI_PRO_MODEL, prompt)
