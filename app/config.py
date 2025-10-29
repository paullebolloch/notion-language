from pathlib import Path
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
DB_FLASHCARDS = os.getenv("NOTION_DB_FLASHCARDS", "")
DB_SESSIONS  = os.getenv("NOTION_DB_SESSIONS", "")
DB_LANGUAGES = os.getenv("NOTION_DB_LANGUAGES", "")
BASE_URL     = os.getenv("BASE_URL", "http://localhost:8000")
