"""Shared configuration and Gemini client helper."""
import os

from dotenv import load_dotenv

load_dotenv()

GEMINI_PRO_MODEL = os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro")
GEMINI_FLASH_MODEL = os.getenv("GEMINI_FLASH_MODEL", "gemini-2.5-flash")


class GeminiError(Exception):
    """Raised when a Gemini call cannot be completed."""


_configured = False


def get_model(model_name: str):
    """Return a Gemini model, configuring the SDK on first use.

    The client is created lazily so the app can start (and serve the
    pages) even before an API key has been added.
    """
    global _configured
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise GeminiError(
            "GOOGLE_API_KEY is not set. Add it to your .env file and restart the server."
        )

    import google.generativeai as genai

    if not _configured:
        genai.configure(api_key=api_key)
        _configured = True
    return genai.GenerativeModel(model_name)


def run_prompt(model_name: str, prompt: str) -> str:
    """Send a prompt to Gemini and return the stripped text response."""
    model = get_model(model_name)
    try:
        response = model.generate_content(prompt)
        text = (response.text or "").strip()
    except GeminiError:
        raise
    except Exception as exc:  # network errors, blocked content, quota, etc.
        raise GeminiError(f"Gemini request failed: {exc}") from exc
    if not text:
        raise GeminiError("Gemini returned an empty response.")
    return text
