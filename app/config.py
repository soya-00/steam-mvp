import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'gals.db'}")

SECRET_KEY = os.getenv("SECRET_KEY", "gals-demo-secret-doi-khi-deploy")
SESSION_COOKIE = "gals_session"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "").strip()

GEMINI_MODEL_PREFERENCE = (
    "gemini-flash-latest",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
)

MAX_MESSAGES_PER_SESSION = 30

STEAM_FIELDS = (
    {"key": "khoa_hoc", "name": "Khoa học", "letter": "S", "accent": "teal"},
    {"key": "cong_nghe", "name": "Công nghệ", "letter": "T", "accent": "indigo"},
    {"key": "ky_thuat", "name": "Kỹ thuật", "letter": "E", "accent": "slate"},
    {"key": "nghe_thuat", "name": "Nghệ thuật", "letter": "A", "accent": "amber"},
    {"key": "toan", "name": "Toán", "letter": "M", "accent": "plum"},
)

FIELD_NAME_BY_KEY = {f["key"]: f["name"] for f in STEAM_FIELDS}
FIELD_KEY_BY_NAME = {f["name"]: f["key"] for f in STEAM_FIELDS}

PROJECT_CATEGORIES = (
    {"key": "nghe_thuat", "label": "Nghệ thuật"},
    {"key": "ky_thuat", "label": "Kỹ thuật"},
    {"key": "ca_hai", "label": "Cả hai"},
)


def gemini_enabled() -> bool:
    return bool(GEMINI_API_KEY)
