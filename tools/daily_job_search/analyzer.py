import json
import logging
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL, CLAUDE_MD, WRITING_STYLE, MAX_JOBS

log = logging.getLogger(__name__)

client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

PROFILE = CLAUDE_MD.read_text()
WRITING_RULES = WRITING_STYLE.read_text() if WRITING_STYLE.exists() else ""


def _build_search_summary(jobs: list[dict]) -> str:
    lines = []
    for i, j in enumerate(jobs, 1):
        title = j.get("title", "Unknown")
        company = j.get("company", "Unknown")
        location = j.get("location", "Unknown")
        url = j.get("url", "N/A")
        source = j.get("source", "unknown")
        lines.append(f"{i}. [{source}] {title} at {company} ({location}) - {url}")
    return "\n".join(lines)


def evaluate_jobs(jobs: list[dict]) -> list[dict]:
    if not jobs:
        return []

    if len(jobs) > 50:
        log.info(f"Truncating from {len(jobs)} to 50 most recent jobs")
        jobs = jobs[:50]

    all_results = []
    batch_size = 25

    for i in range(0, len(jobs), batch_size):
        batch = jobs[i:i + batch_size]
        batch_results = _evaluate_batch(batch, i, jobs)
        all_results.extend(batch_results)

    return all_results


def _evaluate_batch(jobs: list[dict], offset: int, all_jobs: list[dict]) -> list[dict]:
    summary = _build_search_summary(jobs)

    prompt = f"""You are a job fit evaluator. Below is the candidate's profile and a list of job postings.

CANDIDATE PROFILE:
{PROFILE}

JOB LISTINGS:
{summary}

For EACH job (1 through {len(jobs)}), evaluate fit and return a JSON array with one object per job. Each object must have:
- "index": the job number (1-based, starting from {offset + 1})
- "title": job title
- "company": company name
- "location": location
- "url": job URL
- "source": "linkedin" or "freehire"
- "fit": "strong", "medium", or "low"
- "score": numeric 0-100
- "reason": 1-2 sentence explanation of the fit rating
- "keywords": list of 3-5 key requirements from the posting that match or gap the profile

Rules:
- "strong" = score 75-100, clear alignment with skills and experience
- "medium" = score 50-74, partial alignment, some gaps
- "low" = score below 50, significant gaps or misalignment
- Be honest about gaps. Do not inflate scores.
- Focus on: bioinformatics, NGS, AWS/cloud, Python/R/Bash, pipeline development, data engineering
- Consider location: Brazil and international remote are preferred. On-site far from Sao Paulo is a negative.
- CRITICAL: The candidate is based in São Paulo, Brazil and does NOT have US work authorization. Jobs requiring "legally authorized to work in the USA", "without sponsorship", "US work authorization required", or similar visa/legal restrictions must be rated "low" with score below 30. This is a hard dealbreaker — the candidate cannot relocate to the US without visa sponsorship.
- Return ONLY the JSON array, no markdown, no explanation outside the array.

Return the JSON array now:"""

    log.info(f"Sending {len(jobs)} jobs to LLM for evaluation...")

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=8000,
    )

    content = response.choices[0].message.content.strip()

    if content.startswith("```"):
        content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    try:
        results = json.loads(content)
    except json.JSONDecodeError:
        log.error(f"Failed to parse LLM response as JSON:\n{content[:500]}")
        return []

    for r in results:
        idx = r.get("index", 0) - 1
        if 0 <= idx < len(all_jobs):
            r["job"] = all_jobs[idx]

    return results


def rank_jobs(evaluated: list[dict]) -> list[dict]:
    return sorted(evaluated, key=lambda x: x.get("score", 0), reverse=True)


def select_top_for_drafting(ranked: list[dict], max_count: int = None) -> list[dict]:
    if max_count is None:
        max_count = MAX_JOBS
    strong = [j for j in ranked if j.get("fit") == "strong"]
    medium = [j for j in ranked if j.get("fit") == "medium"]
    selected = strong[:max_count]
    remaining = max_count - len(selected)
    if remaining > 0:
        selected.extend(medium[:remaining])
    return selected[:max_count]
