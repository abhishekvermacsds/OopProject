"""Central configuration. All secrets come from environment variables / a local .env file."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv is optional; real env vars still work
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

API_KEY = os.getenv("NLPCLOUD_API_KEY", "").strip()
USE_GPU = os.getenv("NLPCLOUD_GPU", "false").strip().lower() == "true"

NER_MODEL = os.getenv("NER_MODEL", "en_core_web_lg")
LANGDETECT_MODEL = os.getenv("LANGDETECT_MODEL", "python-langdetect")
SENTIMENT_MODEL = os.getenv("SENTIMENT_MODEL", "distilbert-base-uncased-emotion")

USERS_FILE = Path(os.getenv("USERS_FILE", BASE_DIR / "data" / "users.json"))
