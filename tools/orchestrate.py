#!/usr/bin/env python3
"""Job Application Orchestrator — standalone tool using any OpenAI-compatible API.

No paid subscription required. Works with OpenAI, Ollama, Groq, Together,
Fireworks, or any other provider that exposes an OpenAI-compatible endpoint.

Setup:
    pip install openai requests
    export OPENAI_API_KEY=your-key
    export OPENAI_BASE_URL=https://api.openai.com/v1
    export OPENAI_MODEL=gpt-4o-mini

Usage:
    python tools/orchestrate.py evaluate <url-or-text>
    python tools/orchestrate.py cv <url-or-text> [-o cv/main_company.tex]
    python tools/orchestrate.py cover <url-or-text> [-o cover_letters/cover_company_role.tex]
    python tools/orchestrate.py apply <url-or-text>
    python tools/orchestrate.py compile cv/main_company.tex
    python tools/orchestrate.py verify cv/main_company.pdf
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# LLM client
# ---------------------------------------------------------------------------

def _get_client():
    try:
        import openai
    except ImportError:
        sys.exit("Requires: pip install openai")

    base_url = os.environ.get("OPENAI_BASE_URL") or os.environ.get("OPENAI_API_BASE")
    api_key = os.environ.get("OPENAI_API_KEY", "")

    if not base_url:
        sys.exit(
            "Set OPENAI_BASE_URL (or OPENAI_API_BASE) to your provider's endpoint.\n"
            "Examples:\n"
            "  export OPENAI_BASE_URL=http://localhost:11434/v1   # Ollama\n"
            "  export OPENAI_BASE_URL=https://api.openai.com/v1   # OpenAI\n"
            "  export OPENAI_BASE_URL=https://api.groq.com/openai  # Groq\n"
        )

    return openai.OpenAI(base_url=base_url, api_key=api_key)


def _get_model():
    return os.environ.get("OPENAI_MODEL") or os.environ.get("OPENAI_MODEL_NAME", "gpt-4o-mini")


def llm(system: str, user: str, temperature: float = 0.7) -> str:
    client = _get_client()
    resp = client.chat.completions.create(
        model=_get_model(),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
    )
    return resp.choices[0].message.content


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

def load_profile() -> str:
    p = ROOT / "CLAUDE.md"
    if not p.exists():
        sys.exit("CLAUDE.md not found — are you in the repo root?")
    return p.read_text(encoding="utf-8")


def load_skill(name: str) -> str:
    p = ROOT / ".claude" / "skills" / name / "SKILL.md"
    return p.read_text(encoding="utf-8") if p.exists() else ""


def load_reference(name: str) -> str:
    """Load a reference file from the job-application-assistant skill directory."""
    d = ROOT / ".claude" / "skills" / "job-application-assistant"
    p = d / name
    return p.read_text(encoding="utf-8") if p.exists() else ""


def fetch_url(url: str) -> str:
    try:
        import requests
    except ImportError:
        sys.exit("Requires: pip install requests")
    resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    return resp.text


def extract_job_text(target: str) -> str:
    if target.startswith("http://") or target.startswith("https://"):
        return fetch_url(target)
    return target


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s]+", "-", text)
    return text.strip("-")[:40]


def extract_company_role(target: str) -> tuple[str, str]:
    """Best-effort extraction from the target string."""
    company = slugify(target.split()[0] if len(target.split()) > 1 else "target")
    role = "role"
    return company, role


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_evaluate(args):
    profile = load_profile()
    job_text = extract_job_text(args.target)
    eval_framework = load_reference("04-job-evaluation.md")

    system = (
        "You are an expert career advisor. Evaluate job fit honestly and "
        "specifically. Do not fabricate skills or experience."
    )
    prompt = f"""Evaluate this job posting against the candidate profile.
Be honest about gaps — never claim the candidate has a skill they lack.

## Evaluation Framework
{eval_framework}

## Candidate Profile
{profile}

## Job Posting
{job_text}

Provide a structured evaluation table with scores (0-100) for each dimension,
then a verdict: APPLY / CONSIDER / SKIP with a one-paragraph justification.
"""
    print(llm(system, prompt))


def cmd_cv(args):
    profile = load_profile()
    job_text = extract_job_text(args.target)
    cv_template = load_reference("05-cv-templates.md")
    example_tex = (ROOT / "cv" / "main_example.tex").read_text(encoding="utf-8")

    system = (
        "You are an expert LaTeX CV writer using the moderncv package (banking style, blue). "
        "Output ONLY valid LaTeX code, nothing else. Never use pdflatex — always target lualatex. "
        "The CV must compile to exactly 2 pages. Use \\needspace before each \\cventry."
    )
    prompt = f"""Generate a tailored LaTeX CV for this job application.

## LaTeX Template Structure (follow this exactly)
{example_tex}

## Tailoring Guide
{cv_template}

## Candidate Profile
{profile}

## Job Posting
{job_text}

Rules:
- Use moderncv banking style, blue color scheme
- Include the \\renewcommand color overrides from the template
- Include \\usepackage{needspace} and add \\needspace{{5\\baselineskip}} before each \\cventry
- Profile statement must be tailored to this specific role
- Skills reordered to match job requirements
- Experience bullets reframed toward the posting's keywords
- Exactly 2 pages when compiled with lualatex
- Output ONLY the LaTeX .tex content
"""
    result = llm(system, prompt)

    # Strip markdown fences if present
    result = re.sub(r"^```(?:latex)?\s*\n", "", result)
    result = re.sub(r"\n```\s*$", "", result)

    out = Path(args.output) if args.output else ROOT / "cv" / f"main_{slugify(args.target)}.tex"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(result, encoding="utf-8")
    print(f"CV written to {out}")
    print(f"Compile: cd cv && lualatex -interaction=nonstopmode -halt-on-error {out.name}")


def cmd_cover(args):
    profile = load_profile()
    job_text = extract_job_text(args.target)
    cover_template = load_reference("06-cover-letter-templates.md")
    example_tex = (ROOT / "cover_letters" / "cover_example.tex").read_text(encoding="utf-8")

    system = (
        "You are an expert cover letter writer using a custom LaTeX class (cover.cls) "
        "with Lato and Raleway fonts. Output ONLY valid LaTeX code. "
        "The letter must compile to exactly 1 page with xelatex."
    )
    prompt = f"""Generate a tailored LaTeX cover letter for this job application.

## LaTeX Template Structure (follow this exactly)
{example_tex}

## Tailoring Guide
{cover_template}

## Candidate Profile
{profile}

## Job Posting
{job_text}

CRITICAL RULES:
- Use \\documentclass{{cover}} and follow the exact structure from the template
- \\lettercontent{{}} MUST NOT wrap \\begin{{itemize}}...\\end{{itemize}}
- Instead: close \\lettercontent{{}} first, then wrap the list in:
  {{\\raggedright\\fontspec[Path = OpenFonts/fonts/raleway/]{{Raleway-Medium}}\\fontsize{{11pt}}{{13pt}}\\selectfont \\begin{{itemize}}...\\end{{itemize}}\\par}}
- Use \\closing{{Kind regards,}} with NO trailing \\\\
- 250-300 words of body text maximum (not counting LaTeX markup)
- Address the letter to a specific person if identifiable, otherwise "Dear [Company] hiring team,"
- Reference specific company products, priorities, or values
- Output ONLY the LaTeX .tex content
"""
    result = llm(system, prompt)

    result = re.sub(r"^```(?:latex)?\s*\n", "", result)
    result = re.sub(r"\n```\s*$", "", result)

    company, role = extract_company_role(args.target)
    out = Path(args.output) if args.output else ROOT / "cover_letters" / f"cover_{company}_{role}.tex"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(result, encoding="utf-8")
    print(f"Cover letter written to {out}")
    print(f"Compile: cd cover_letters && xelatex -interaction=nonstopmode -halt-on-error {out.name}")


def cmd_apply(args):
    profile = load_profile()
    job_text = extract_job_text(args.target)
    eval_framework = load_reference("04-job-evaluation.md")
    cv_template = load_reference("05-cv-templates.md")
    cover_template = load_reference("06-cover-letter-templates.md")
    example_cv = (ROOT / "cv" / "main_example.tex").read_text(encoding="utf-8")
    example_cover = (ROOT / "cover_letters" / "cover_example.tex").read_text(encoding="utf-8")

    # --- Step 1: Evaluate fit ---
    print("=" * 60)
    print("STEP 1: Evaluating fit")
    print("=" * 60)
    fit = llm(
        "You are an expert career advisor. Evaluate honestly.",
        f"## Evaluation Framework\n{eval_framework}\n\n## Profile\n{profile}\n\n## Job\n{job_text}\n\nProvide scores and verdict: APPLY / CONSIDER / SKIP.",
    )
    print(fit)

    verdict = fit.upper()
    if "SKIP" in verdict and "APPLY" not in verdict:
        print("\nVerdict: SKIP — not recommended to proceed.")
        return

    # --- Step 2: Generate CV ---
    print("\n" + "=" * 60)
    print("STEP 2: Generating CV")
    print("=" * 60)
    cv = llm(
        "You are an expert LaTeX CV writer using moderncv banking style. Output ONLY valid LaTeX.",
        f"## Template\n{example_cv}\n\n## Tailoring Guide\n{cv_template}\n\n## Profile\n{profile}\n\n## Job\n{job_text}\n\n"
        "Rules: moderncv banking, blue, \\needspace before each \\cventry, exactly 2 pages, output ONLY .tex content.",
    )
    cv = re.sub(r"^```(?:latex)?\s*\n", "", cv)
    cv = re.sub(r"\n```\s*$", "", cv)

    company_slug = slugify(args.target)
    cv_path = ROOT / "cv" / f"main_{company_slug}.tex"
    cv_path.parent.mkdir(parents=True, exist_ok=True)
    cv_path.write_text(cv, encoding="utf-8")
    print(f"CV saved to {cv_path}")

    # --- Step 3: Generate cover letter ---
    print("\n" + "=" * 60)
    print("STEP 3: Generating cover letter")
    print("=" * 60)
    cover = llm(
        "You are an expert cover letter writer using cover.cls with xelatex. Output ONLY valid LaTeX.",
        f"## Template\n{example_cover}\n\n## Tailoring Guide\n{cover_template}\n\n## Profile\n{profile}\n\n## Job\n{job_text}\n\n"
        "CRITICAL: \\lettercontent must NOT wrap itemize. Use fontspec wrapper for bullets. "
        "\\closing has no \\\\. 250-300 words max. Output ONLY .tex content.",
    )
    cover = re.sub(r"^```(?:latex)?\s*\n", "", cover)
    cover = re.sub(r"\n```\s*$", "", cover)

    company, role = extract_company_role(args.target)
    cover_path = ROOT / "cover_letters" / f"cover_{company}_{role}.tex"
    cover_path.parent.mkdir(parents=True, exist_ok=True)
    cover_path.write_text(cover, encoding="utf-8")
    print(f"Cover letter saved to {cover_path}")

    # --- Step 4: Compile ---
    print("\n" + "=" * 60)
    print("STEP 4: Compiling PDFs")
    print("=" * 60)
    _compile(cv_path, "lualatex")
    _compile(cover_path, "xelatex")

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)


def cmd_compile(args):
    tex_path = Path(args.tex_file)
    if not tex_path.exists():
        sys.exit(f"File not found: {tex_path}")

    engine = "lualatex" if "cover" not in tex_path.name else "xelatex"
    if args.engine:
        engine = args.engine

    _compile(tex_path, engine)


def _compile(tex_path: Path, engine: str):
    """Compile a .tex file and report result."""
    print(f"\nCompiling {tex_path.name} with {engine}...")
    result = subprocess.run(
        [engine, "-interaction=nonstopmode", "-halt-on-error", tex_path.name],
        cwd=str(tex_path.parent),
        capture_output=True,
        text=True,
        timeout=120,
    )
    pdf_path = tex_path.with_suffix(".pdf")
    if pdf_path.exists():
        print(f"OK — {pdf_path}")
    else:
        print(f"FAILED — no PDF produced")
        if result.returncode != 0:
            # Show last few lines of log
            log_path = tex_path.with_suffix(".log")
            if log_path.exists():
                log = log_path.read_text(encoding="utf-8", errors="replace")
                errors = [l for l in log.splitlines() if l.startswith("!")]
                for e in errors[:5]:
                    print(f"  {e}")


def cmd_verify(args):
    """Run the PDF verification tool."""
    pdf_path = Path(args.pdf_file)
    if not pdf_path.exists():
        sys.exit(f"File not found: {pdf_path}")

    verify_script = ROOT / "tools" / "verify_pdf.py"
    if not verify_script.exists():
        sys.exit("tools/verify_pdf.py not found")

    cmd = [sys.executable, str(verify_script), str(pdf_path)]
    if args.min_chars:
        cmd += ["--min-chars", str(args.min_chars)]
    if args.pages:
        cmd += ["--pages", str(args.pages)]
    for c in args.contains or []:
        cmd += ["--contains", c]

    result = subprocess.run(cmd, capture_output=False)
    sys.exit(result.returncode)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Job Application Orchestrator (any OpenAI-compatible API)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Environment variables:
  OPENAI_BASE_URL  API endpoint (required). Examples:
                     http://localhost:11434/v1  (Ollama)
                     https://api.openai.com/v1  (OpenAI)
                     https://api.groq.com/openai (Groq)
  OPENAI_API_KEY   API key (required by most providers, omit for Ollama)
  OPENAI_MODEL     Model name (default: gpt-4o-mini)

Examples:
  python tools/orchestrate.py evaluate "https://linkedin.com/jobs/view/123456789"
  python tools/orchestrate.py apply "Senior ML Engineer at Acme Corp ..."
  python tools/orchestrate.py cv "Job description pasted here" -o cv/main_acme.tex
""",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # evaluate
    p = sub.add_parser("evaluate", help="Evaluate job fit against profile")
    p.add_argument("target", help="Job URL or pasted job description text")

    # cv
    p = sub.add_parser("cv", help="Generate tailored CV (.tex)")
    p.add_argument("target", help="Job URL or pasted job description text")
    p.add_argument("-o", "--output", help="Output .tex path")

    # cover
    p = sub.add_parser("cover", help="Generate tailored cover letter (.tex)")
    p.add_argument("target", help="Job URL or pasted job description text")
    p.add_argument("-o", "--output", help="Output .tex path")

    # apply
    p = sub.add_parser("apply", help="Full workflow: evaluate + CV + cover + compile")
    p.add_argument("target", help="Job URL or pasted job description text")

    # compile
    p = sub.add_parser("compile", help="Compile a .tex file to PDF")
    p.add_argument("tex_file", help="Path to .tex file")
    p.add_argument("-e", "--engine", choices=["lualatex", "xelatex", "pdflatex"])

    # verify
    p = sub.add_parser("verify", help="Verify a PDF (page count, content)")
    p.add_argument("pdf_file", help="Path to .pdf file")
    p.add_argument("--min-chars", type=int, default=100)
    p.add_argument("--pages", type=int)
    p.add_argument("--contains", action="append", default=[])

    args = parser.parse_args()
    {
        "evaluate": cmd_evaluate,
        "cv": cmd_cv,
        "cover": cmd_cover,
        "apply": cmd_apply,
        "compile": cmd_compile,
        "verify": cmd_verify,
    }[args.command](args)


if __name__ == "__main__":
    main()
