# Setup Guide

Step-by-step instructions for getting the AI Job Search framework running.

## 1. Prerequisites

### AI Assistant

You need one of:

- **[OpenCode](https://opencode.ai)** (recommended) — free, works with any model (local via Ollama, OpenAI, Groq, Together, etc.)
- **Python 3.10+** with `pip install openai requests` — standalone orchestrator using any OpenAI-compatible API

### Python

Python 3.10+ is required for the salary lookup tool and the orchestration script. Check with:

```bash
python3 --version
```

On Windows, `py --version` is often the most reliable check. If your system exposes Python as `python` instead of `python3`, use `python` in the commands below.

### Bun (for job search tools)

The job portal CLIs (four Danish portals plus the country-agnostic `linkedin-search` and `freehire-search` tools) are written in TypeScript and run with Bun.

- macOS/Linux:

```bash
curl -fsSL https://bun.sh/install | bash
```

- Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -c "irm https://bun.sh/install.ps1 | iex"
```

If you prefer a package manager, `winget install Oven-sh.Bun` also works on Windows.

### LaTeX (for compiling CVs and cover letters)

Install a LaTeX distribution to compile the generated `.tex` files to PDF:

- **Windows:** [MiKTeX](https://miktex.org/download)
- **macOS:** [MacTeX](https://tug.org/mactex/)
- **Linux:** `sudo apt install texlive-full` or `sudo dnf install texlive-scheme-full`

The CV compiles with `lualatex` (pdflatex often fails on modern MiKTeX installs with `fontawesome5` font-expansion errors). The cover letter compiles with `xelatex` because `cover.cls` requires `fontspec` for its custom Lato/Raleway fonts.

#### Minimal TeX install: TinyTeX/BasicTeX

Full TeX distributions work out of the box, but minimal distributions need a few extra packages before the stock templates compile.

On macOS, a user-level TinyTeX install avoids a system-wide installer and does not require `sudo`:

```bash
curl -fsSL https://yihui.org/tinytex/install-bin-unix.sh -o /tmp/tinytex-install-bin-unix.sh
sh /tmp/tinytex-install-bin-unix.sh /tmp --no-path
export PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH"
```

Then install the template dependencies:

```bash
tlmgr install \
  moderncv fontawesome5 fontawesome6 academicons import luatexbase pgf \
  titlesec textpos xltxtra xunicode cite realscripts needspace
```

For BasicTeX/MacTeX, make sure the TeX binary directory is on `PATH` first (for example via `/Library/TeX/texbin`), then run the same `tlmgr install ...` command.

Quick smoke tests after setup:

```bash
cd cv && lualatex -interaction=nonstopmode -halt-on-error main_example.tex && cd ..

SMOKE_DIR="$(mktemp -d /tmp/ai-job-cover-smoke.XXXXXX)"
cp -R cover_letters/cover.cls cover_letters/OpenFonts "$SMOKE_DIR/"
cat >"$SMOKE_DIR/cover_smoke.tex" <<'EOF'
\documentclass[]{cover}
\begin{document}
\namesection{Test}{Candidate}{test@example.com}
\companyname{Example Company}
\companyaddress{123 Hiring Street\\Example City}
\currentdate{\today}
\lettercontent{Dear Hiring Manager,}
\lettercontent{This smoke test verifies that xelatex can load cover.cls and the bundled fonts.}
\closing{Sincerely,}
\signature{Test Candidate}
\end{document}
EOF
(cd "$SMOKE_DIR" && xelatex -interaction=nonstopmode -halt-on-error cover_smoke.tex)
```

### Optional: pdftotext (for the ATS check)

`/apply` runs an ATS parseability check on the compiled CV: it extracts the PDF's text layer and verifies contact details, reading order, and keyword coverage the way an applicant-tracking system sees them. This uses `pdftotext` from [poppler](https://poppler.freedesktop.org/), which is not part of TeX distributions:

- **macOS:** `brew install poppler`
- **Debian/Ubuntu:** `sudo apt install poppler-utils`
- **Windows:** `choco install poppler`

If `pdftotext` is missing, `/apply` skips the mechanical check with a warning and falls back to a visual keyword review — everything else works normally.

## 2. Fork and clone

```bash
gh repo fork MadsLorentzen/ai-job-search --clone
cd ai-job-search
```

Or manually: fork on GitHub, then clone your fork.

## 3. Install job search CLI dependencies
Run these from the repository root.

- PowerShell:

```powershell
$tools = @("linkedin-search", "freehire-search")
foreach ($tool in $tools) {
  Set-Location ".agents/skills/$tool/cli"
  bun install
  Set-Location "..\..\..\.."
}
```

- Bash / zsh / Git Bash:
```bash
for tool in linkedin-search freehire-search; do
  cd .agents/skills/$tool/cli && bun install && cd ../../../..
done
```

For `linkedin-search` and `freehire-search` the install is optional: both have zero runtime dependencies and run with plain `bun`; `bun install` only pulls TypeScript dev types.

If you're outside Denmark, you can generate an equivalent search skill for your local job board with `/add-portal` — it scaffolds the same CLI structure for any public portal and test-runs a live query before registering. See the "Job search tools" section in the README.

## 4. Set up your profile

**Option A: Edit CLAUDE.md directly**

Open `CLAUDE.md` and fill in your profile information. Replace the `[PLACEHOLDER]` tokens with your actual data.

**Option B: Use OpenCode**

```bash
opencode
# Then describe what you want:
# "Help me set up my job application profile"
# "I want to fill in my profile from my CV"
```

OpenCode reads `CLAUDE.md` as project instructions and loads the skills automatically.

**Option C: Use the Python orchestrator**

```bash
pip install openai requests
export OPENAI_BASE_URL=https://api.openai.com/v1   # or your provider
export OPENAI_API_KEY=your-key
export OPENAI_MODEL=gpt-4o-mini
```

Then edit `CLAUDE.md` directly, or use the orchestrator to generate tailored documents from your profile.

### What gets populated

| File | Content |
|------|---------|
| `CLAUDE.md` | Your full candidate profile |
| `01-candidate-profile.md` | Structured education, experience, skills |
| `02-behavioral-profile.md` | Behavioral assessment |
| `04-job-evaluation.md` | Personalized skill match areas and career goals |
| `05-cv-templates.md` | Profile statement templates for your background |
| `07-interview-prep.md` | STAR examples from your experience |
| `cv/main_example.tex` | Your LaTeX CV with actual details |
| `search-queries.md` | Job search queries for job search |

### Re-running setup

You can update specific sections later by editing the files directly, or by asking your AI assistant:

- "Update my skills section to include [new skill]"
- "Update my job search queries to focus on [new criteria]"
- "Add my new certification to my profile"

## 5. Optional: Set up salary benchmarking

If you have salary data (from a union, salary survey, Glassdoor, or personal research):

1. **Option A:** Create `salary_data.json` manually in the repo root (see `tools/README_SALARY_TOOL.md` for the format)
2. **Option B:** Convert from Excel:
   ```bash
   pip install openpyxl
   python3 tools/convert_salary_excel.py path/to/salary-data.xlsx --source "My Salary Data 2025"
   ```

This creates `salary_data.json` which the `/apply` workflow uses for salary benchmarking. If you skip this step, salary lookup is simply omitted.

## 6. Test the workflow

Find a job posting you're interested in, then:

**With OpenCode:**

```
"Evaluate this job posting and draft a CV and cover letter for it: https://linkedin.com/jobs/view/123456789"
```

Or paste the job description directly:

```
"Evaluate this job posting and draft a CV and cover letter for it: [paste job posting text here]"
```

**With the Python orchestrator:**

```bash
python tools/orchestrate.py apply "https://linkedin.com/jobs/view/123456789"
```

Or paste the job description directly:

```bash
python tools/orchestrate.py apply "[paste job posting text here]"
```

The workflow will:
1. Evaluate the fit against your profile
2. Draft a tailored CV and cover letter
3. Compile the LaTeX files to PDF
4. Verify the PDF output

## 7. Compile your documents

After the workflow creates the LaTeX files:

```bash
# Bash / zsh / Git Bash
cd cv && lualatex main_<company>.tex && cd ..
cd cover_letters && xelatex cover_<company>_<role>.tex && cd ..
```

```powershell
# PowerShell
Set-Location cv; lualatex main_<company>.tex; Set-Location ..
Set-Location cover_letters; xelatex cover_<company>_<role>.tex; Set-Location ..
```

Or use the orchestrator:

```bash
python tools/orchestrate.py compile cv/main_<company>.tex
python tools/orchestrate.py compile cover_letters/cover_<company>_<role>.tex
```

These commands apply to the stock templates (moderncv CV, `cover.cls` cover letter). If you'd rather use your own LaTeX template, update the guidance in `05-cv-templates.md` and `06-cover-letter-templates.md`.

## Troubleshooting

### "salary_data.json not found"
This is expected if you haven't set up salary benchmarking. The `/apply` workflow skips this step automatically.

### Job search CLI tools not working
Make sure Bun is installed and you ran `bun install` in each CLI directory. The tools require network access to fetch job listings.

### LaTeX compilation errors
- CV: uses `lualatex` (pdflatex often fails on modern MiKTeX with `fontawesome5` font-expansion errors; lualatex handles the same sources cleanly)
- Cover letter: uses `xelatex` (for custom fonts in `OpenFonts/fonts/`)
- Make sure your LaTeX distribution includes the `moderncv` package

### Fonts not found in cover letter
The cover letter template expects fonts in `cover_letters/OpenFonts/fonts/`. Make sure this directory exists and contains the Lato and Raleway font files.

### Stale `.claude/settings.local.json` from an older clone
If it exists from an older clone, delete it — its broad permissions override the scoped `settings.json`:

```bash
rm .claude/settings.local.json
```
