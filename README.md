# FitBuddy - AI Fitness Plan Generator using Gemini Models

FitBuddy is a web app that generates a personalized **7-day workout plan** and a **nutrition/recovery tip** from a user's age, weight, goal and preferred intensity. Users can send feedback ("more cardio", "add rest days") and the plan is revised by AI. An admin page lists every user with their original and updated plans.

Built with **FastAPI**, **Google Gemini** (Pro for plans, Flash for tips), **SQLite + SQLAlchemy** and **Jinja2** templates.

## Features

- Personalized 7-day plan: warm-up, main workout, cooldown for each day (Gemini Pro)
- Nutrition / recovery tip for the chosen goal (Gemini Flash, with a built-in fallback tip)
- Feedback loop: revise the plan; the original is kept next to the updated version
- Admin dashboard at `/view-all-users` (view and delete users)
- HTML interface plus JSON API endpoints (interactive docs at `/docs`)

## Project structure

```
fitbuddy/
├── requirements.txt
├── .env.example              # copy to .env and add your key
├── app/
│   ├── main.py               # FastAPI entry point
│   ├── routes.py             # web pages + API routes
│   ├── database.py           # SQLAlchemy models and DB functions
│   ├── schemas.py            # Pydantic validation models
│   ├── config.py             # .env loading, Gemini client helper
│   ├── gemini_generator.py   # Gemini Pro - workout plan
│   ├── gemini_flash_generator.py  # Gemini Flash - nutrition tip
│   ├── updated_plan.py       # feedback-based plan updater
│   ├── nutrition.py          # fallback nutrition tips
│   ├── templates/            # index.html, result.html, all_users.html
│   └── static/               # css/style.css, images/ (add gym-bg.jpg here)
└── fitbuddy.db               # created automatically on first run
```

## Setup

1. Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).

2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Add your key:

   ```bash
   cp .env.example .env            # Windows: copy .env.example .env
   ```

   Then edit `.env` and set `GOOGLE_API_KEY`.

4. Run the server from the project root:

   ```bash
   uvicorn app.main:app --reload
   ```

5. Open http://127.0.0.1:8000 for the app and http://127.0.0.1:8000/docs for the API docs.

### Choosing models

The models are set in `.env` (`GEMINI_PRO_MODEL`, `GEMINI_FLASH_MODEL`). Google retires older model names over time, so if you get a "model not found" error, check Google's documentation for the current names and update `.env`.

### Optional background image

Put a gym photo at `app/static/images/gym-bg.jpg` for a themed background. Without it the app uses a plain dark background.

## Pages and endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/` | Input form |
| POST | `/generate-workout` | Form: generate plan + tip, save, show result |
| POST | `/submit-feedback` | Form: revise plan from feedback |
| GET | `/view-all-users` | Admin dashboard |
| POST | `/delete-user/{user_id}` | Admin: delete a user |
| POST | `/generate-workout/gemini` | API: plan from goal + intensity |
| GET | `/nutrition-tip?goal=...` | API: nutrition tip |
| POST | `/generate-plan` | API: save user and generate plan (JSON) |
| POST | `/update-plan/{user_id}` | API: update plan from feedback (JSON) |

## Uploading to GitHub

```bash
cd fitbuddy
git init
git add .
git commit -m "Initial commit: FitBuddy AI fitness plan generator"
git branch -M main
git remote add origin https://github.com/<your-username>/fitbuddy.git
git push -u origin main
```

Create the empty `fitbuddy` repository on GitHub first. `.gitignore` already keeps `.env` (your API key) and the local database out of the repo.

## Disclaimer

Plans and tips are AI-generated and are not medical advice. Consult a doctor before starting a new exercise routine.
