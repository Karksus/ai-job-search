import json
import logging
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import MAX_JOBS, REPO_ROOT
from searcher import search_all
from analyzer import evaluate_jobs, rank_jobs, select_top_for_drafting
from drafter import draft_documents
from email_sender import send_daily_email
from job_db import filter_new_jobs, mark_sent, get_stats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).resolve().parent / "last_run.log"),
    ],
)
log = logging.getLogger("daily_job_search")


def run():
    today = date.today().isoformat()
    output_dir = Path.home() / "Downloads" / "job_applications" / today
    output_dir.mkdir(parents=True, exist_ok=True)
    log.info(f"Output directory: {output_dir}")

    log.info("Step 1: Searching job portals...")
    jobs = search_all()
    if not jobs:
        log.warning("No jobs found. Exiting.")
        return

    before = len(jobs)
    jobs = filter_new_jobs(jobs)
    log.info(f"Filtered {before} → {len(jobs)} new jobs (skipped {before - len(jobs)} already seen)")
    if not jobs:
        log.warning("No new jobs after dedup. Exiting.")
        return

    log.info(f"Step 2: Evaluating {len(jobs)} jobs with LLM...")
    evaluated = evaluate_jobs(jobs)
    if not evaluated:
        log.error("Evaluation failed. Exiting.")
        return

    ranked = rank_jobs(evaluated)
    log.info(f"Ranked {len(ranked)} jobs")

    timestamp = datetime.now().strftime("%H%M")
    report_path = output_dir / f"ranking_{timestamp}.json"
    report_data = [
        {k: v for k, v in j.items() if k != "job"}
        for j in ranked
    ]
    report_path.write_text(json.dumps(report_data, indent=2, ensure_ascii=False))
    log.info(f"Ranking saved to {report_path}")

    top_jobs = select_top_for_drafting(ranked)
    log.info(f"Step 3: Drafting CV and cover letter for top {len(top_jobs)} jobs...")

    drafted = []
    for item in top_jobs:
        job = item.get("job", item)
        company = job.get("company", "unknown")
        title = job.get("title", "role")
        log.info(f"  Drafting for: {title} at {company}")

        result = draft_documents(job, output_dir)
        drafted.append(result)

    log.info("Step 4: Sending email report...")
    email_ok = send_daily_email(ranked, drafted, str(output_dir))
    if email_ok:
        log.info("Email sent successfully")
        for j in ranked:
            score = j.get("score")
            fit = j.get("fit")
            mark_sent([j.get("job", j)], score=score, fit=fit)
    else:
        log.warning("Email failed (check Mailgun config)")

    db_stats = get_stats()
    summary = {
        "date": today,
        "total_jobs": len(jobs),
        "evaluated": len(evaluated),
        "strong": len([j for j in ranked if j.get("fit") == "strong"]),
        "medium": len([j for j in ranked if j.get("fit") == "medium"]),
        "low": len([j for j in ranked if j.get("fit") == "low"]),
        "drafted": len([d for d in drafted if d.get("cv_compiled")]),
        "email_sent": email_ok,
        "output_dir": str(output_dir),
        "db_total_tracked": db_stats["total_tracked"],
        "db_total_sent": db_stats["total_sent"],
    }
    log.info(f"Summary: {json.dumps(summary, indent=2)}")
    return summary


if __name__ == "__main__":
    run()
