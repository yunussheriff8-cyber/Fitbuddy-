"""Core route handlers: web pages (HTML forms) and JSON API endpoints."""
import os

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app.config import GeminiError
from app.database import (
    delete_user,
    get_all_plans,
    get_all_users,
    get_current_plan,
    get_original_plan,
    get_user,
    save_plan,
    save_user,
    update_plan,
)
from app.gemini_flash_generator import generate_nutrition_tip_with_flash
from app.gemini_generator import generate_workout_gemini
from app.nutrition import fallback_tip
from app.schemas import FeedbackRequest, UserInput, WorkoutRequest
from app.updated_plan import update_workout_plan

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

router = APIRouter()


# ------------------------------------------------------------------ helpers
def _tip_for(goal: str) -> str:
    """Nutrition tip from Gemini Flash, falling back to a built-in tip."""
    try:
        return generate_nutrition_tip_with_flash(goal)
    except GeminiError:
        return fallback_tip(goal)


def _form_error(request: Request, message: str, status_code: int, values: dict | None = None):
    return templates.TemplateResponse(
        request, "index.html", {"error": message, "values": values or {}}, status_code=status_code
    )


def _validation_message(exc: ValidationError) -> str:
    first = exc.errors()[0]
    field = str(first["loc"][-1]).replace("_", " ")
    return f"Check the {field} field: {first['msg']}."


# ------------------------------------------------------------- web: pages
@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Home page: the user input form."""
    return templates.TemplateResponse(request, "index.html", {"values": {}})


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: int = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
):
    """Validate the form, generate plan + tip, store them, show result.html."""
    raw = {
        "username": username, "user_id": user_id, "age": age,
        "weight": weight, "goal": goal, "intensity": intensity,
    }
    try:
        user = UserInput(**raw)
    except ValidationError as exc:
        return _form_error(request, _validation_message(exc), 422, raw)

    try:
        plan = generate_workout_gemini(
            {"goal": user.goal, "intensity": user.intensity, "age": user.age, "weight": user.weight}
        )
    except GeminiError as exc:
        return _form_error(request, str(exc), 502, raw)

    nutrition_tip = _tip_for(user.goal)

    save_user(user.user_id, user.username, user.age, user.weight, user.goal, user.intensity)
    save_plan(user.user_id, plan)

    return templates.TemplateResponse(
        request,
        "result.html",
        {
            "username": user.username,
            "user_id": user.user_id,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity.capitalize(),
            "workout_plan": plan,
            "nutrition_tip": nutrition_tip,
            "updated": False,
            "message": None,
        },
    )


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(request: Request, user_id: int = Form(...), feedback: str = Form(...)):
    """Revise the user's plan using their feedback and re-render result.html."""
    user = get_user(user_id)
    current = get_current_plan(user_id)
    if not user or not current:
        return _form_error(
            request, f"No plan found for User ID {user_id}. Generate a plan first.", 404
        )

    try:
        FeedbackRequest(feedback=feedback)
    except ValidationError as exc:
        return _form_error(request, _validation_message(exc), 422)

    try:
        revised = update_workout_plan(current, feedback.strip())
    except GeminiError as exc:
        return _form_error(request, str(exc), 502)

    update_plan(user_id, revised)

    return templates.TemplateResponse(
        request,
        "result.html",
        {
            "username": user.name,
            "user_id": user.id,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity.capitalize(),
            "workout_plan": revised,
            "nutrition_tip": _tip_for(user.goal),
            "updated": True,
            "message": "Your plan has been updated based on your feedback!",
        },
    )


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request):
    """Admin dashboard: every user with original and updated plans."""
    plans = {plan.user_id: plan for plan in get_all_plans()}
    user_data = []
    for user in get_all_users():
        plan = plans.get(user.id)
        user_data.append(
            {
                "id": user.id,
                "name": user.name,
                "age": user.age,
                "weight": user.weight,
                "goal": user.goal,
                "intensity": user.intensity,
                "original_plan": plan.original_plan if plan else "N/A",
                "updated_plan": plan.updated_plan if plan and plan.updated_plan else "Not updated",
            }
        )
    return templates.TemplateResponse(request, "all_users.html", {"users": user_data})


@router.post("/delete-user/{user_id}")
def remove_user(user_id: int):
    """Admin action: delete a user and their plans."""
    delete_user(user_id)
    return RedirectResponse("/view-all-users", status_code=303)


# --------------------------------------------------------------- JSON API
@router.post("/generate-workout/gemini")
def generate_gemini_workout(request: WorkoutRequest):
    """API: generate a workout using Gemini Pro (nothing is stored)."""
    try:
        result = generate_workout_gemini({"goal": request.goal, "intensity": request.intensity})
        return {"model": "gemini-pro", "workout_plan": result}
    except GeminiError as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@router.get("/nutrition-tip")
def get_flash_tip(goal: str):
    """API: generate a nutrition tip using Gemini Flash."""
    try:
        tip = generate_nutrition_tip_with_flash(goal)
    except GeminiError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    return {"goal": goal, "nutrition_tip": tip}


@router.post("/generate-plan")
def generate_plan(user_data: UserInput):
    """API: save user info and generate + store a plan."""
    try:
        plan = generate_workout_gemini(
            {
                "goal": user_data.goal,
                "intensity": user_data.intensity,
                "age": user_data.age,
                "weight": user_data.weight,
            }
        )
    except GeminiError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    save_user(
        user_id=user_data.user_id,
        name=user_data.username,
        age=user_data.age,
        weight=user_data.weight,
        goal=user_data.goal,
        intensity=user_data.intensity,
    )
    save_plan(user_data.user_id, plan)
    return {"message": "Workout plan generated and saved successfully!", "workout_plan": plan}


@router.post("/update-plan/{user_id}", response_model=dict)
def update_user_plan(user_id: int, data: FeedbackRequest):
    """API: update a user's workout plan based on feedback."""
    current = get_current_plan(user_id)
    if not current:
        raise HTTPException(status_code=404, detail="Original plan not found for this user.")
    try:
        updated = update_workout_plan(current, data.feedback)
    except GeminiError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    update_plan(user_id, updated)
    return {"updated_plan": updated, "original_plan": get_original_plan(user_id)}
