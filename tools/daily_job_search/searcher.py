import json
import subprocess
import logging
from pathlib import Path
from config import PORTALS

log = logging.getLogger(__name__)


def run_cli(portal: str, args: list[str]) -> dict | None:
    cfg = PORTALS.get(portal)
    if not cfg:
        log.warning(f"Unknown portal: {portal}")
        return None

    cmd = ["bun", "run", cfg["entry"], "search", *args, "--format", "json"]
    log.info(f"[{portal}] {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            cwd=str(cfg["cwd"]),
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            log.error(f"[{portal}] stderr: {result.stderr.strip()}")
            return None
        return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
        log.error(f"[{portal}] {e}")
        return None


LINKEDIN_QUERIES = [
    {"args": ["-q", "bioinformatics", "-l", "Sao Paulo, Brazil", "--jobage", "14"]},
    {"args": ["-q", "bioinformatics", "-l", "Remote", "--jobage", "14"]},
    {"args": ["-q", "genomics", "-l", "Sao Paulo, Brazil", "--jobage", "14"]},
    {"args": ["-q", "bioinformatics engineer", "-l", "Remote", "--jobage", "14"]},
    {"args": ["-q", "cloud engineer", "-l", "Sao Paulo, Brazil", "--jobage", "14"]},
    {"args": ["-q", "AWS", "-l", "Sao Paulo, Brazil", "--jobage", "14", "--remote"]},
    {"args": ["-q", "data engineer", "-l", "Sao Paulo, Brazil", "--jobage", "14"]},
    {"args": ["-q", "NGS", "-l", "Remote", "--jobage", "14"]},
    {"args": ["-q", "bioinformatics", "-l", "Brazil", "--jobage", "14"]},
    {"args": ["-q", "precision medicine", "-l", "Remote", "--jobage", "14"]},
]

FREEHIRE_QUERIES = [
    {"args": ["-q", "bioinformatics", "--jobage", "14", "--limit", "25"]},
    {"args": ["-q", "genomics", "--jobage", "14", "--limit", "25"]},
    {"args": ["-q", "bioinformatics", "--remote", "--jobage", "14", "--limit", "25"]},
    {"args": ["-q", "NGS pipeline", "--jobage", "14", "--limit", "25"]},
    {"args": ["-q", "cloud engineer", "--category", "ml_ai", "--jobage", "14", "--limit", "25"]},
    {"args": ["-q", "AWS life sciences", "--jobage", "14", "--limit", "25"]},
]


def search_all() -> list[dict]:
    seen_ids = set()
    all_jobs = []

    for q in LINKEDIN_QUERIES:
        data = run_cli("linkedin", q["args"])
        if data and "results" in data:
            for job in data["results"]:
                jid = job.get("url") or job.get("id", "")
                if jid not in seen_ids:
                    seen_ids.add(jid)
                    job["source"] = "linkedin"
                    all_jobs.append(job)

    for q in FREEHIRE_QUERIES:
        data = run_cli("freehire", q["args"])
        if data and "results" in data:
            for job in data["results"]:
                jid = job.get("url") or job.get("id", "")
                if jid not in seen_ids:
                    seen_ids.add(jid)
                    job["source"] = "freehire"
                    all_jobs.append(job)

    log.info(f"Total unique jobs found: {len(all_jobs)}")
    return all_jobs
