"""Nutrition helpers (optional).

Provides a built-in fallback tip so the result page still shows advice
when the Gemini Flash call fails or no API key is configured.
"""

_FALLBACK_TIPS = {
    "weight": "Build most meals around lean protein and vegetables, and drink a glass of water before eating. It keeps you fuller for longer without much effort.",
    "fat": "Build most meals around lean protein and vegetables, and drink a glass of water before eating. It keeps you fuller for longer without much effort.",
    "muscle": "Include a good protein source (chicken, eggs, fish, beans or Greek yogurt) in your post-workout meal to support muscle repair and growth.",
    "gain": "Include a good protein source (chicken, eggs, fish, beans or Greek yogurt) in your post-workout meal to support muscle repair and growth.",
    "flex": "Stay hydrated and get enough sleep. Well-hydrated muscles and joints move more freely and recover faster.",
}

_DEFAULT_TIP = "Drink water throughout the day, eat a balanced plate with protein, carbs and healthy fats, and aim for 7-9 hours of sleep to help your body recover."


def fallback_tip(goal: str) -> str:
    goal = (goal or "").lower()
    for keyword, tip in _FALLBACK_TIPS.items():
        if keyword in goal:
            return tip
    return _DEFAULT_TIP
