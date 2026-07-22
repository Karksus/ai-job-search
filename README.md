<p align="center">
  <img src="assets/mascot/pip_flight_loop.gif" alt="Pip, the courier bird" width="200">
</p>

# AI Job Search (Pedro's Fork)


> **This is a fork of [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search).** The upstream project provides the core AI-powered job application framework (profile setup, fit evaluation, CV/cover letter drafting). This fork adds **daily automation, email notifications, and job deduplication** — all vibecoded with AI assistance (OpenCode).



## What's different from upstream

| Feature | Upstream | This Fork |
|---------|----------|-----------|
| Profile-based job evaluation | ✅ | ✅ |
| CV/cover letter drafting (LaTeX) | ✅ | ✅ |
| Job portal CLIs (LinkedIn, Freehire, etc.) | ✅ | ✅ |
| **Daily automated job search** | ❌ | ✅ |
| **Email reports with ranked jobs + attached PDFs** | ❌ | ✅ |
| **SQLite job deduplication** | ❌ | ✅ |
| **Cron-based scheduling** | ❌ | ✅ |
| **Gmail SMTP integration** | ❌ | ✅ |

## New features (vibecoded)

### Daily Job Search (`tools/daily_job_search/`)

Automated pipeline that runs daily via cron:

1. **Search** — queries LinkedIn and Freehire portals for jobs matching your profile
2. **Deduplicate** — SQLite database (`seen_jobs_<person>.db`) tracks all previously seen jobs per profile
3. **Evaluate** — LLM scores each job for fit (strong/medium/low)
4. **Draft** — generates tailored CV + cover letter (LaTeX → PDF) for top matches
5. **Email** — sends HTML report with ranked jobs + attached PDFs via Gmail SMTP

**Output:** `~/Downloads/job_applications/<profile>/YYYY-MM-DD/`

**Multi-profile:** Run for all profiles (`--all`), a specific profile (`--profile pedro`), or list profiles (`--list`).

### Setup

1. **Install dependencies:**

```bash
pip install python-dotenv requests openai
```

2. **Configure environment** — copy `.env.example` to `.env` in the repo root:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Gmail SMTP (global fallback if profile doesn't define its own)
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password

# LLM
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o
OPENAI_BASE_URL=https://api.openai.com/v1
```

3. **Set up profiles** — create a profile directory and add your profile:

```bash
mkdir -p tools/daily_job_search/profiles/yourname
```

Create `tools/daily_job_search/profiles/yourname/profile.md` with your candidate profile (see existing examples).

Create `tools/daily_job_search/profiles/yourname/search_queries.json` with your search queries.

Configure `tools/daily_job_search/profiles.json`:

```json
{
  "yourname": {
    "language": "en",
    "recipient_email": "your-email@gmail.com",
    "queries_path": "profiles/yourname/search_queries.json",
    "smtp_email": "",
    "smtp_password": ""
  }
}
```

If `smtp_email`/`smtp_password` are empty, falls back to `.env` credentials.

**Getting a Gmail App Password:**
1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Enable **2-Step Verification**
3. Search for **App Passwords** → generate one for "Mail"
4. Use the 16-character password in `SMTP_PASSWORD`

### Running manually

```bash
# First time: copy the example script and adjust paths
cp tools/daily_job_search/run_daily.sh.example tools/daily_job_search/run_daily.sh
# Edit run_daily.sh if needed (paths are auto-detected via dirname)

bash tools/daily_job_search/run_daily.sh
```

Or run the Python script directly:

```bash
cd tools/daily_job_search

# Run for all profiles
python3 main.py --all

# Run for a specific profile
python3 main.py --profile pedro

# List available profiles
python3 main.py --list
```

### Setting up the cron job

```bash
crontab -e
```

Add this line to run daily at 9pm (adjust path to your repo):

```
0 21 * * * /your/path/to/ai-job-search/tools/daily_job_search/run_daily.sh
```

**Important:** The `run_daily.sh` script exports the PATH to include `bun` — without this, cron can't find the `bun` binary and all searches fail silently.

### How deduplication works

- Every job is hashed by URL and stored in `seen_jobs_<person>.db` per profile
- On each run, previously seen jobs are skipped
- Jobs are marked as "sent" after successful email delivery
- The database tracks: title, company, score, fit, first/last seen, email sent status

### Ignoring employers

Add a comma-separated list of employer names to ignore in `.env`:

```env
IGNORED_EMPLOYERS="Crossing Hurdles,Another Agency"
```

Jobs from these employers are filtered out before evaluation, saving LLM calls. Matching is case-insensitive.

### Email format

The daily email includes:
- **HTML report** with jobs grouped by fit (strong/medium/low)
- **PDF attachments** — tailored CV + cover letter for each top-matched role
- **Plain text fallback** for email clients that don't render HTML

## Original upstream features

The core framework from [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search) includes:

- **Profile setup** — fill in your education, experience, skills, and career goals
- **Fit evaluation** — AI scores job postings against your profile
- **CV tailoring** — LaTeX CVs customized for each role
- **Cover letter writing** — targeted letters using custom LaTeX templates
- **Interview preparation** — STAR examples and talking points
- **Salary benchmarking** — optional tool for compensation research

See the [upstream README](https://github.com/MadsLorentzen/ai-job-search/blob/main/README.md) for the full original documentation.

## Prerequisites

- Python 3.10+
- [Bun](https://bun.sh) (for job search CLI tools)
- LaTeX: `lualatex` (CV), `xelatex` (cover letter)
- Optional: `pdftotext` from [poppler](https://poppler.freedesktop.org/) (ATS check)

## Quick start

### 1. Clone

```bash
git clone https://github.com/Karksus/ai-job-search.git
cd ai-job-search
```

### 2. Install job search tools

```bash
for tool in linkedin-search freehire-search; do
  cd .agents/skills/$tool/cli && bun install && cd ../../../..
done
```

### 3. Configure

```bash
cp .env.example .env
# Edit .env with your Gmail app password and OpenAI API key
```

### 4. Set up your profile

Edit `CLAUDE.md` with your personal information, or use OpenCode:

```bash
opencode
# Then: "Set up my job application profile"
```

### 5. Run

```bash
# First time only: create your local run script
cp tools/daily_job_search/run_daily.sh.example tools/daily_job_search/run_daily.sh

bash tools/daily_job_search/run_daily.sh
```

## File structure (what's new)

```
tools/daily_job_search/
├── main.py              # Orchestrator — runs the full pipeline
├── searcher.py          # Queries LinkedIn + Freehire portals
├── analyzer.py          # LLM-based job evaluation and ranking
├── drafter.py           # Generates CV + cover letter LaTeX → PDF
├── email_sender.py      # Gmail SMTP email with PDF attachments
├── job_db.py            # SQLite deduplication database (per-profile)
├── config.py            # Loads .env and profiles.json configuration
├── run_daily.sh.example # Template for cron wrapper (copy to run_daily.sh)
├── run_daily.sh         # Shell wrapper for cron (gitignored, your local copy)
├── seen_jobs_*.db       # Per-profile job dedup databases (gitignored)
├── profiles.json        # Profile registry with SMTP/recipients (gitignored)
├── profiles/            # Candidate profiles (gitignored)
│   ├── pedro/
│   │   ├── profile.md
│   │   └── search_queries.json
│   └── ana/
│       ├── profile.md
│       └── search_queries.json
├── last_run.log         # Latest run log
└── templates/           # LaTeX templates (use [YOUR_NAME] placeholders, fill from CLAUDE.md)
```

## Contributing

Thinking about a PR? Read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## Acknowledgements

- [Mads Lorentzen](https://github.com/MadsLorentzen) — original framework
- [Mikkel Krogholm](https://github.com/mikkelkrogsholm) — job search CLI skills

## License

MIT
