import json
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent.parent

load_dotenv(REPO_ROOT / ".env")
load_dotenv(ROOT / ".env")

SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL_NAME", os.getenv("OPENAI_MODEL", "gpt-4o"))
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
MAX_JOBS = int(os.getenv("MAX_JOBS", "10"))

GLOBAL_IGNORED_EMPLOYERS = [
    name.strip().lower()
    for name in os.getenv("IGNORED_EMPLOYERS", "").split(",")
    if name.strip()
]

CV_TEMPLATE = ROOT / "templates" / "cv_template.tex"
COVER_LETTER_TEMPLATE = ROOT / "templates" / "cover_letter_template.tex"
WRITING_STYLE = REPO_ROOT / ".claude" / "skills" / "job-application-assistant" / "03-writing-style.md"

PORTALS = {
    "linkedin": {
        "cwd": REPO_ROOT / ".agents" / "skills" / "linkedin-search" / "cli",
        "entry": "src/cli.ts",
    },
    "freehire": {
        "cwd": REPO_ROOT / ".agents" / "skills" / "freehire-search" / "cli",
        "entry": "src/cli.ts",
    },
}

LUALATEX = "lualatex"
XELATEX = "xelatex"

PROFILES_CONFIG = ROOT / "profiles.json"


def load_profiles() -> dict:
    if not PROFILES_CONFIG.exists():
        return {}
    return json.loads(PROFILES_CONFIG.read_text())


def get_profile_config(profile_name: str) -> dict | None:
    profiles = load_profiles()
    return profiles.get(profile_name)


def get_profile_text(profile_name: str) -> str:
    cfg = get_profile_config(profile_name)
    if not cfg:
        raise ValueError(f"Profile '{profile_name}' not found in profiles.json")
    profile_path = ROOT / cfg["profile_path"]
    if not profile_path.exists():
        raise FileNotFoundError(f"Profile file not found: {profile_path}")
    return profile_path.read_text()


def get_profile_queries(profile_name: str) -> dict:
    cfg = get_profile_config(profile_name)
    if not cfg:
        raise ValueError(f"Profile '{profile_name}' not found in profiles.json")
    queries_path = ROOT / cfg["search_queries_path"]
    if not queries_path.exists():
        raise FileNotFoundError(f"Search queries file not found: {queries_path}")
    return json.loads(queries_path.read_text())


def get_profile_recipient(profile_name: str) -> str:
    cfg = get_profile_config(profile_name)
    if not cfg:
        return ""
    return cfg.get("recipient_email", "")


def get_profile_smtp(profile_name: str) -> tuple[str, str]:
    cfg = get_profile_config(profile_name)
    if not cfg:
        return ("", "")
    smtp_email = cfg.get("smtp_email", "")
    smtp_password = cfg.get("smtp_password", "")
    if smtp_email and smtp_password:
        return (smtp_email, smtp_password)
    return (SMTP_EMAIL, SMTP_PASSWORD)


def get_profile_language(profile_name: str) -> str:
    cfg = get_profile_config(profile_name)
    if not cfg:
        return "en"
    return cfg.get("language", "en")


def list_profile_names() -> list[str]:
    return list(load_profiles().keys())
