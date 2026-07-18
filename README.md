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
2. **Deduplicate** — SQLite database (`seen_jobs.db`) tracks all previously seen jobs, skips duplicates
3. **Evaluate** — LLM scores each job for fit (strong/medium/low)
4. **Draft** — generates tailored CV + cover letter (LaTeX → PDF) for top matches
5. **Email** — sends HTML report with ranked jobs + attached PDFs via Gmail SMTP

**Output:** `~/Downloads/job_applications/YYYY-MM-DD/`

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
# Gmail SMTP (free, no domain needed)
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password

# LLM
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1
```

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
cd tools/daily_job_search && python3 main.py
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

- Every job is hashed by URL and stored in `seen_jobs.db`
- On each run, previously seen jobs are skipped
- Jobs are marked as "sent" after successful email delivery
- The database tracks: title, company, score, fit, first/last seen, email sent status

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
├── job_db.py            # SQLite deduplication database
├── config.py            # Loads .env configuration
├── run_daily.sh.example # Template for cron wrapper (copy to run_daily.sh)
├── run_daily.sh         # Shell wrapper for cron (gitignored, your local copy)
├── seen_jobs.db         # Job dedup database (gitignored)
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
