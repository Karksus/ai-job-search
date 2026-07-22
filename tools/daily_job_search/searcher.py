import json
import subprocess
import logging
from pathlib import Path
from config import PORTALS, GLOBAL_IGNORED_EMPLOYERS

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


def search_all(queries: dict, ignored_employers: list[str] | None = None) -> list[dict]:
    seen_ids = set()
    all_jobs = []

    for q in queries.get("linkedin", []):
        data = run_cli("linkedin", q["args"])
        if data and "results" in data:
            for job in data["results"]:
                jid = job.get("url") or job.get("id", "")
                if jid not in seen_ids:
                    seen_ids.add(jid)
                    job["source"] = "linkedin"
                    all_jobs.append(job)

    for q in queries.get("freehire", []):
        data = run_cli("freehire", q["args"])
        if data and "results" in data:
            for job in data["results"]:
                jid = job.get("url") or job.get("id", "")
                if jid not in seen_ids:
                    seen_ids.add(jid)
                    job["source"] = "freehire"
                    all_jobs.append(job)

    combined_ignore = set(GLOBAL_IGNORED_EMPLOYERS)
    if ignored_employers:
        combined_ignore.update(e.lower() for e in ignored_employers)

    if combined_ignore:
        before = len(all_jobs)
        all_jobs = [
            j for j in all_jobs
            if (j.get("company") or "").lower() not in combined_ignore
        ]
        log.info(f"Filtered {before} -> {len(all_jobs)} jobs (ignored employers: {combined_ignore})")

    log.info(f"Total unique jobs found: {len(all_jobs)}")
    return all_jobs
