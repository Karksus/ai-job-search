import argparse
import json
import logging
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import (
    MAX_JOBS, get_profile_config, get_profile_text,
    get_profile_queries, get_profile_recipient, get_profile_smtp,
    get_profile_language, list_profile_names,
)
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


def run_profile(profile_name: str) -> dict | None:
    cfg = get_profile_config(profile_name)
    if not cfg:
        log.error(f"Profile '{profile_name}' not found in profiles.json")
        return None

    today = date.today().isoformat()
    output_dir = Path.home() / "Downloads" / "job_applications" / profile_name / today
    output_dir.mkdir(parents=True, exist_ok=True)
    log.info(f"=== Running profile: {profile_name} ({cfg.get('name', '')}) ===")
    log.info(f"Output directory: {output_dir}")

    log.info("Step 1: Searching job portals...")
    try:
        queries = get_profile_queries(profile_name)
    except Exception as e:
        log.error(f"Failed to load search queries: {e}")
        return None

    jobs = search_all(queries)
    if not jobs:
        log.warning("No jobs found. Exiting.")
        return None

    before = len(jobs)
    jobs = filter_new_jobs(jobs, profile_name)
    log.info(f"Filtered {before} -> {len(jobs)} new jobs (skipped {before - len(jobs)} already seen)")
    if not jobs:
        log.warning("No new jobs after dedup. Exiting.")
        return None

    log.info(f"Step 2: Evaluating {len(jobs)} jobs with LLM...")
    try:
        profile_text = get_profile_text(profile_name)
    except Exception as e:
        log.error(f"Failed to load profile: {e}")
        return None

    evaluated = evaluate_jobs(jobs, profile_text)
    if not evaluated:
        log.error("Evaluation failed. Exiting.")
        return None

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

    language = get_profile_language(profile_name)
    log.info(f"Document language: {language}")

    drafted = []
    for item in top_jobs:
        job = item.get("job", item)
        company = job.get("company", "unknown")
        title = job.get("title", "role")
        log.info(f"  Drafting for: {title} at {company}")

        result = draft_documents(job, output_dir, profile_text, language)
        drafted.append(result)

    log.info("Step 4: Sending email report...")
    recipient = get_profile_recipient(profile_name)
    smtp_email, smtp_password = get_profile_smtp(profile_name)
    email_ok = send_daily_email(
        ranked, drafted, str(output_dir), recipient, profile_name,
        smtp_email=smtp_email, smtp_password=smtp_password,
    )
    if email_ok:
        log.info("Email sent successfully")
        for j in ranked:
            score = j.get("score")
            fit = j.get("fit")
            mark_sent([j.get("job", j)], profile_name, score=score, fit=fit)
    else:
        log.warning("Email failed (check SMTP config)")

    db_stats = get_stats(profile_name)
    summary = {
        "profile": profile_name,
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


def main():
    parser = argparse.ArgumentParser(description="Daily job search pipeline")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--profile", type=str, help="Run for a specific profile name")
    group.add_argument("--all", action="store_true", help="Run for all profiles")
    group.add_argument("--list", action="store_true", help="List available profiles")
    args = parser.parse_args()

    if args.list:
        names = list_profile_names()
        if not names:
            print("No profiles found in profiles.json")
        else:
            print("Available profiles:")
            for name in names:
                cfg = get_profile_config(name)
                print(f"  {name}: {cfg.get('name', '')} ({cfg.get('recipient_email', 'no email')})")
        return

    if args.profile:
        summary = run_profile(args.profile)
        if summary:
            print(json.dumps(summary, indent=2))
        else:
            print(f"Profile '{args.profile}' failed or found no jobs")
            sys.exit(1)

    elif args.all:
        names = list_profile_names()
        if not names:
            log.error("No profiles found in profiles.json")
            sys.exit(1)

        results = []
        for name in names:
            summary = run_profile(name)
            if summary:
                results.append(summary)

        print(f"\n=== All profiles complete: {len(results)}/{len(names)} successful ===")
        for r in results:
            print(f"  {r['profile']}: {r['strong']} strong, {r['medium']} medium, {r['drafted']} drafted")


if __name__ == "__main__":
    main()
