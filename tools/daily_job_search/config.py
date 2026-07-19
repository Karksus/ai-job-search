import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent.parent

load_dotenv(REPO_ROOT / ".env")
load_dotenv(ROOT / ".env")

SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL_NAME", os.getenv("OPENAI_MODEL", "gpt-4o"))
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
MAX_JOBS = int(os.getenv("MAX_JOBS", "10"))

IGNORED_EMPLOYERS = [
    name.strip().lower()
    for name in os.getenv("IGNORED_EMPLOYERS", "").split(",")
    if name.strip()
]

CV_TEMPLATE = ROOT / "templates" / "cv_template.tex"
COVER_LETTER_TEMPLATE = ROOT / "templates" / "cover_letter_template.tex"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
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
