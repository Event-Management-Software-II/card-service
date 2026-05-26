import os
from pathlib import Path
from dotenv import load_dotenv

# Load root .env if available (local dev only – provides HOST_IP for expansion).
# In Docker the path is too shallow, so we catch IndexError gracefully.
try:
    _root_env = Path(__file__).resolve().parents[3] / ".env"
    if _root_env.exists():
        load_dotenv(dotenv_path=_root_env, override=False)
except IndexError:
    pass

# Load service .env – ${HOST_IP} is expanded from process environment when present
load_dotenv(override=False)


class Config:
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
