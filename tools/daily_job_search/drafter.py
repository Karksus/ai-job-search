import json
import subprocess
import logging
import re
from pathlib import Path
from openai import OpenAI
from config import (
    OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL,
    CV_TEMPLATE, COVER_LETTER_TEMPLATE, LUALATEX, XELATEX,
    REPO_ROOT,
)

log = logging.getLogger(__name__)
client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

NO_DASH_RULE = "CRITICAL RULE: NEVER use em-dashes (--- or --) in any text. Use commas, periods, or restructure sentences instead."
NO_PHONE_RULE = "Do NOT include any phone number in the documents."
NO_FABRICATION_RULE = "Every claim must match the candidate profile exactly. Do NOT fabricate skills, experience, or achievements."
LATEX_BULLET_RULE = 'For the "bullets" field, return plain text strings. Do NOT include LaTeX commands like \\item or \\textbf. Just return the label and description separated by a colon. Example: "Pipeline validation: Reduced variant calling time from hours to minutes"'


def _call_llm(prompt: str, max_tokens: int = 4000) -> str:
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


def _parse_json(raw: str) -> dict | list:
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    raw = re.sub(r'\\(?![nrtuU"\\\/bfn])', r'\\\\', raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        log.error(f"JSON parse error: {e}")
        log.error(f"Raw content (first 500): {raw[:500]}")
        raise


def _sanitize_latex(text: str) -> str:
    text = text.replace("\\", "\\textbackslash{}")
    text = text.replace("&", "\\&")
    text = text.replace("%", "\\%")
    text = text.replace("#", "\\#")
    text = text.replace("_", "\\_")
    text = text.replace("~", "\\textasciitilde{}")
    text = text.replace("^", "\\textasciicircum{}")
    return text


def _sanitize_bullet(text: str) -> str:
    text = re.sub(r'\\(?![nrtuU"\\\/bfn])', r'\\\\', text)
    text = text.replace("&", "\\&")
    text = text.replace("%", "\\%")
    text = text.replace("#", "\\#")
    text = text.replace("~", "\\textasciitilde{}")
    return text


def generate_cv_content(job: dict, profile: str) -> dict:
    title = job.get("title", "Unknown Role")
    company = job.get("company", "Unknown Company")
    url = job.get("url", "")
    job_summary = f"Job: {title} at {company}\nURL: {url}"

    prompt = f"""Generate tailored CV content for this job application.

{NO_DASH_RULE}
{NO_PHONE_RULE}
{NO_FABRICATION_RULE}

CANDIDATE PROFILE:
{profile}

TARGET JOB:
{job_summary}

Return a JSON object with these fields:
- "profile_statement": 2-3 sentence profile summary tailored to this role
- "competencies": array of 5 strings, each in format "Category: Skill1, Skill2, Skill3" (tailored to job keywords)
- "experience": array of objects, each with "role", "company", "location", "dates", "bullets" (array of 3-4 strings)
  - Only include roles from the profile. Rewrite bullets to emphasize relevance to this job.
  - Do NOT fabricate any experience or skills not in the profile.
  - Bullets should be plain text, no LaTeX formatting.
- "education": array of objects, each with "degree", "institution", "location", "dates", "detail" (1 sentence, plain text)

Return ONLY the JSON object, no markdown fencing, no explanation."""

    content = _call_llm(prompt, max_tokens=6000)
    return _parse_json(content)


def generate_cover_letter_content(job: dict, profile: str) -> dict:
    title = job.get("title", "Unknown Role")
    company = job.get("company", "Unknown Company")
    url = job.get("url", "")
    job_summary = f"Job: {title} at {company}\nURL: {url}"

    prompt = f"""Generate a tailored cover letter for this job application.

{NO_DASH_RULE}
{NO_PHONE_RULE}
{NO_FABRICATION_RULE}
{LATEX_BULLET_RULE}

WRITING RULES:
- No cliches ("I am writing to express my strong interest", "I am passionate about")
- Lead with a direct value proposition, not a formulaic opening
- Be forward-looking: what will you do for the employer, not just what you've done
- Frame gaps positively, never admit weaknesses
- Be specific to the company, never generic
- 5 paragraphs max to fit 1 page

CANDIDATE PROFILE:
{profile}

TARGET JOB:
{job_summary}

Return a JSON object with these fields:
- "salutation": "Dear Hiring Manager," or a specific name if known
- "opening_paragraph": 2-3 sentences. Lead with value proposition. No cliche openings.
- "body_paragraph": 2-3 sentences. Most relevant experience mapped to job requirements.
- "bullets": array of 3 strings. Each is "Label: description" (plain text, no LaTeX).
- "company_paragraph": 2-3 sentences. Why this company specifically. Reference verified specifics.
- "closing_paragraph": 2-3 sentences. Forward-looking, what you'll contribute.

Return ONLY the JSON object, no markdown fencing, no explanation."""

    content = _call_llm(prompt, max_tokens=4000)
    return _parse_json(content)


def _build_cv_latex(content: dict) -> str:
    template = CV_TEMPLATE.read_text()

    profile = content.get("profile_statement", "")
    template = template.replace("{{PROFILE_STATEMENT}}", _sanitize_latex(profile))

    comps = []
    for c in content.get("competencies", []):
        comps.append(f"\\item \\textbf{{{_sanitize_latex(c)}}}")
    template = template.replace("{{COMPETENCIES}}", "\n".join(comps))

    exp_blocks = []
    for role in content.get("experience", []):
        title = _sanitize_latex(role.get("role", ""))
        company = _sanitize_latex(role.get("company", ""))
        location = _sanitize_latex(role.get("location", ""))
        dates = _sanitize_latex(role.get("dates", ""))
        bullets = role.get("bullets", [])

        bullet_lines = []
        for b in bullets:
            if ":" in b:
                label, desc = b.split(":", 1)
                bullet_lines.append(f"    \\item \\textbf{{{_sanitize_latex(label.strip())}:}} {_sanitize_latex(desc.strip())}")
            else:
                bullet_lines.append(f"    \\item {_sanitize_latex(b.strip())}")

        bullet_text = "\n".join(bullet_lines)
        block = f"""\\needspace{{5\\baselineskip}}
\\item{{\\cventry{{{dates}}}{{{title}}}{{{company}}}{{{location}}}{{}}{{\\vspace{{1pt}}
\\begin{{itemize}}
{bullet_text}
\\end{{itemize}}}}}}"""
        exp_blocks.append(block)

    template = template.replace("{{EXPERIENCE}}", "\n\n".join(exp_blocks))

    edu_blocks = []
    for edu in content.get("education", []):
        degree = _sanitize_latex(edu.get("degree", ""))
        inst = _sanitize_latex(edu.get("institution", ""))
        loc = _sanitize_latex(edu.get("location", ""))
        dates = _sanitize_latex(edu.get("dates", ""))
        detail = _sanitize_latex(edu.get("detail", ""))
        block = f"""\\item{{\\cventry{{{dates}}}{{{degree}}}{{{inst}}}{{{loc}}}{{}}{{{detail}}}}}"""
        edu_blocks.append(block)

    template = template.replace("{{EDUCATION}}", "\n\n".join(edu_blocks))

    return template


def _build_cover_letter_latex(content: dict) -> str:
    template = COVER_LETTER_TEMPLATE.read_text()

    template = template.replace("{{SALUTATION}}", content.get("salutation", "Dear Hiring Manager,"))
    template = template.replace("{{OPENING_PARAGRAPH}}", _sanitize_latex(content.get("opening_paragraph", "")))
    template = template.replace("{{BODY_PARAGRAPH}}", _sanitize_latex(content.get("body_paragraph", "")))

    raw_bullets = content.get("bullets", [])
    latex_bullets = []
    for b in raw_bullets:
        b = _sanitize_bullet(b)
        if ":" in b:
            label, desc = b.split(":", 1)
            latex_bullets.append(f"\\item \\textbf{{{_sanitize_latex(label.strip())}:}} {_sanitize_latex(desc.strip())}")
        else:
            latex_bullets.append(f"\\item {_sanitize_latex(b.strip())}")
    template = template.replace("{{BULLETS}}", "\n".join(latex_bullets))

    template = template.replace("{{COMPANY_PARAGRAPH}}", _sanitize_latex(content.get("company_paragraph", "")))
    template = template.replace("{{CLOSING_PARAGRAPH}}", _sanitize_latex(content.get("closing_paragraph", "")))

    return template


COVER_CLS = REPO_ROOT / "cover_letters" / "cover.cls"
COVER_FONTS = REPO_ROOT / "cover_letters" / "OpenFonts"


def _ensure_cover_fonts(output_dir: Path):
    link = output_dir / "OpenFonts"
    if not link.exists():
        try:
            link.symlink_to(COVER_FONTS)
        except Exception as e:
            log.warning(f"Could not symlink OpenFonts: {e}")


def _compile_latex(tex_path: Path, engine: str) -> bool:
    env = {"TEXINPUTS": f".:{COVER_CLS.parent}:{COVER_FONTS.parent}:", "PATH": "/usr/bin:/bin"}

    cmd = [engine, "-interaction=nonstopmode", "-halt-on-error", tex_path.name]
    log.info(f"Compiling: {' '.join(cmd)} in {tex_path.parent}")

    try:
        result = subprocess.run(
            cmd,
            cwd=str(tex_path.parent),
            capture_output=True,
            text=True,
            timeout=120,
            env={**dict(__import__('os').environ), **env},
        )
        if result.returncode != 0:
            log.error(f"LaTeX error:\n{result.stdout[-1500:]}")
            return False
        return True
    except subprocess.TimeoutExpired:
        log.error("LaTeX compilation timed out")
        return False


def _check_page_count(pdf_path: Path, expected: int) -> bool:
    try:
        result = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            capture_output=True, text=True, timeout=10,
        )
        for line in result.stdout.splitlines():
            if line.startswith("Pages:"):
                pages = int(line.split(":")[1].strip())
                return pages == expected
    except Exception:
        pass

    try:
        result = subprocess.run(
            ["pdftotext", str(pdf_path), "-"],
            capture_output=True, text=True, timeout=10,
        )
        form_feed_count = result.stdout.count("\f")
        return form_feed_count + 1 == expected
    except Exception:
        return False


def draft_documents(job: dict, output_dir: Path) -> dict:
    profile = (Path(__file__).parent.parent.parent / "CLAUDE.md").read_text()
    company_slug = re.sub(r"[^a-z0-9]+", "_", job.get("company", "unknown").lower()).strip("_")
    role_slug = re.sub(r"[^a-z0-9]+", "_", job.get("title", "role").lower()).strip("_")

    if not company_slug:
        company_slug = "unknown"
    if not role_slug:
        role_slug = "role"

    result = {
        "job": job,
        "cv_path": None,
        "cover_letter_path": None,
        "cv_compiled": False,
        "cover_letter_compiled": False,
    }

    try:
        cv_content = generate_cv_content(job, profile)
        cv_tex = _build_cv_latex(cv_content)
        cv_tex_path = output_dir / f"cv_{company_slug}_{role_slug}.tex"
        cv_tex_path.write_text(cv_tex)

        if _compile_latex(cv_tex_path, LUALATEX):
            pdf_path = cv_tex_path.with_suffix(".pdf")
            if pdf_path.exists():
                result["cv_path"] = str(pdf_path)
                result["cv_compiled"] = True
                result["cv_content"] = cv_content
                log.info(f"CV compiled: {pdf_path}")
            else:
                log.error("CV PDF not found after compilation")
        else:
            log.error("CV compilation failed")
    except Exception as e:
        log.error(f"CV generation error: {e}")

    try:
        cl_content = generate_cover_letter_content(job, profile)
        cl_tex = _build_cover_letter_latex(cl_content)
        cl_tex_path = output_dir / f"cl_{company_slug}_{role_slug}.tex"
        cl_tex_path.write_text(cl_tex)

        _ensure_cover_fonts(output_dir)

        if _compile_latex(cl_tex_path, XELATEX):
            pdf_path = cl_tex_path.with_suffix(".pdf")
            if pdf_path.exists():
                result["cover_letter_path"] = str(pdf_path)
                result["cover_letter_compiled"] = True
                result["cover_letter_content"] = cl_content
                log.info(f"Cover letter compiled: {pdf_path}")
            else:
                log.error("Cover letter PDF not found after compilation")
        else:
            log.error("Cover letter compilation failed")
    except Exception as e:
        log.error(f"Cover letter generation error: {e}")

    return result
