# AGENTS.md

## What this repo is

AI-powered job application framework. Users fork it, fill in their profile, and use an AI assistant (OpenCode, or the standalone Python orchestrator) to search jobs, evaluate fit, tailor CVs, write cover letters, and prep for interviews. **The markdown specs in `.claude/` ARE the implementation** — there is no separate codebase. `CLAUDE.md` is the candidate profile + workflow rules; `.claude/skills/` are the AI skill definitions.

## Prerequisites

- Python 3.10+ (salary lookup tool, orchestrator)
- Bun (job portal CLIs)
- LaTeX: `lualatex` (CV), `xelatex` (cover letter — cover.cls requires fontspec)
- Optional: `pdftotext` from poppler (ATS parseability check)
- For AI assistant: [OpenCode](https://opencode.ai) (free) or Python with `pip install openai requests`

## Key commands

### CI / verification (run before committing)

```bash
python tools/lint_skills.py          # lint skills, commands, settings.json
python tools/security_guards.py      # security guards (permissions, gitignore, manifests)
python -m unittest discover -s tests -t . -v   # Python tests

# Per-CLI typecheck (run in each .agents/skills/<name>/cli/):
bun run typecheck
bun test
```

### LaTeX compilation

```bash
cd cv && lualatex -interaction=nonstopmode -halt-on-error main_example.tex
cd cover_letters && xelatex -interaction=nonstopmode -halt-on-error cover_example.tex
```

### PDF verification

```bash
python3 tools/verify_pdf.py cv/main_example.pdf --min-chars 100
python3 tools/verify_pdf.py cover_letters/cover_example.pdf --min-chars 100
```

## File structure (what matters)

| Path | Purpose | Tracked? |
|------|---------|----------|
| `CLAUDE.md` | Candidate profile + workflow rules | Yes (must keep `[YOUR_NAME]` placeholders) |
| `.claude/commands/*.md` | Slash command definitions | Yes |
| `.claude/skills/*/` | AI skill definitions | Yes |
| `.claude/settings.json` | AI assistant permissions | Yes |
| `.agents/skills/*/cli/` | Job portal CLIs (TypeScript/Bun) | Yes |
| `cv/main_example.tex` | Stock CV template | Yes |
| `cv/main_*.tex` | Personalized CVs | **No** (gitignored) |
| `cover_letters/cover_example.tex` | Stock cover letter example | Yes |
| `cover_letters/cover_*.tex` | Personalized cover letters | **No** (gitignored) |
| `cover_letters/cover.cls` | Custom cover letter LaTeX class | Yes |
| `cover_letters/OpenFonts/` | Lato + Raleway fonts | Yes |
| `documents/` | Career source materials | Only README + folder structure |
| `job_scraper/seen_jobs.json` | Scraper dedup state | **No** (gitignored) |
| `salary_data.json` | Salary benchmarking data | **No** (gitignored) |
| `templates/` | Custom templates via /add-template | Only README.md |
| `upskill/*.md` | Upskill reports | **No** (gitignored) |

## LaTeX gotchas

- **CV engine:** `lualatex`. pdflatex fails on modern MiKTeX with fontawesome5 font-expansion errors.
- **Cover letter engine:** `xelatex` (cover.cls requires fontspec for custom fonts).
- **Orphaned titles:** Always add `\needspace{5\baselineskip}` before each `\cventry` to prevent a job title sitting at page bottom with bullets spilling to the next page.
- **Trailing spill:** Use `\enlargethispage{2-3\baselineskip}` to rescue a section that barely overflows.
- **Bullet font mismatch:** `\lettercontent{}` must NOT wrap `\begin{itemize}...\end{itemize}` — the command's trailing `\\` errors on `\end{itemize}`. Close `\lettercontent{}` first, then wrap the list in `{\raggedright\fontspec[Path = OpenFonts/fonts/raleway/]{Raleway-Medium}\fontsize{11pt}{13pt}\selectfont \begin{itemize}...\end{itemize}\par}`.
- **Page counts:** CV must be exactly 2 pages; cover letter exactly 1 page. "Looks fine in the .tex" is not acceptable — compile and read the PDF.

## Workflow conventions

- **Fit evaluation first.** Before drafting anything, evaluate the job posting against the profile and present the verdict to the user.
- **Drafter-reviewer separation.** A second agent critiques drafts; the drafter revises. This is the core `/apply` workflow.
- **All claims must be verified.** No fabricated skills, experience, or achievements. Company-specific claims must be independently verified via WebFetch/WebSearch — do not trust the reviewer agent's research without checking.
- **ATS verification.** After compiling the CV, extract the PDF text layer with `pdftotext -layout` and verify what an ATS parser sees — contact details as literal text, sane reading order, keyword coverage.
- **Markdown specs are the source of truth.** Do not create duplicate orchestration layers, wrapper commands, or alternative implementations. If a markdown spec exists, it IS the implementation.

## Contributing rules

- **Universal template.** Upstream stays market-agnostic, person-agnostic. Market-specific portal skills go in forks.
- **Personal profile data never committed.** CI enforces placeholder integrity on CLAUDE.md, cv/main_example.tex, cover_letters/cover_example.tex, and key skill files.
- **New commands face a high bar.** Must operationalize something error-prone that already exists in the framework (documented machinery nothing executes, data something writes but nothing reads).
- **One concern per PR.** Kitchen-sink PRs get asked to split.
- **Portal-skill contract:** `search`/`detail` commands, `--format json|table|plain`, stderr JSON errors with exit 1, backoff on 429/5xx, zero runtime dependencies by default.
- **LaTeX changes:** Both templates must compile and hold their exact page counts. CI smoke-checks this.

## Agent-specific notes

- **OpenCode sessions:** CLAUDE.md is loaded as project instructions. Skills in `.claude/skills/` are triggered by keyword matches. Slash commands in `.claude/commands/` are user-invoked.
- **Job portal CLIs** live in `.agents/skills/<name>/cli/`. Each has its own `package.json` and `tsconfig.json`. They output JSON to stdout, errors to stderr as `{"error": "...", "code": "..."}` with exit 1.
- **Permissions:** `.claude/settings.json` pre-approves `bun run`, `python salary_lookup.py`, `python3 salary_lookup.py`, and `pdftotext`. If you need broader permissions, ask the user.
- **Stale `.claude/settings.local.json`:** If it exists from an older clone, delete it — its broad permissions override the scoped `settings.json`.
- **Standalone orchestrator:** `tools/orchestrate.py` works with any OpenAI-compatible API. Set `OPENAI_BASE_URL`, `OPENAI_API_KEY`, and `OPENAI_MODEL` environment variables.
