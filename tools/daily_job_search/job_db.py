import sqlite3
import hashlib
from datetime import date
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "seen_jobs.db"


def _init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS seen_jobs (
            url_hash TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            title TEXT,
            company TEXT,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            sent_email INTEGER DEFAULT 0,
            score INTEGER,
            fit TEXT
        )"""
    )
    conn.commit()
    return conn


def _hash_url(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def filter_new_jobs(jobs: list[dict]) -> list[dict]:
    conn = _init_db()
    today = date.today().isoformat()
    new_jobs = []

    for job in jobs:
        url = job.get("url", "")
        if not url:
            new_jobs.append(job)
            continue

        url_hash = _hash_url(url)
        row = conn.execute(
            "SELECT url_hash FROM seen_jobs WHERE url_hash = ?", (url_hash,)
        ).fetchone()

        if row is None:
            new_jobs.append(job)
            conn.execute(
                "INSERT INTO seen_jobs (url_hash, url, title, company, first_seen, last_seen) VALUES (?, ?, ?, ?, ?, ?)",
                (url_hash, url, job.get("title", ""), job.get("company", ""), today, today),
            )
        else:
            conn.execute(
                "UPDATE seen_jobs SET last_seen = ? WHERE url_hash = ?",
                (today, url_hash),
            )

    conn.commit()
    conn.close()
    return new_jobs


def mark_sent(jobs: list[dict], score: int = None, fit: str = None):
    conn = _init_db()
    today = date.today().isoformat()

    for job in jobs:
        url = job.get("url", "")
        if not url:
            continue
        url_hash = _hash_url(url)
        conn.execute(
            "UPDATE seen_jobs SET sent_email = 1, score = ?, fit = ?, last_seen = ? WHERE url_hash = ?",
            (score, fit, today, url_hash),
        )

    conn.commit()
    conn.close()


def get_stats() -> dict:
    conn = _init_db()
    total = conn.execute("SELECT COUNT(*) FROM seen_jobs").fetchone()[0]
    sent = conn.execute("SELECT COUNT(*) FROM seen_jobs WHERE sent_email = 1").fetchone()[0]
    conn.close()
    return {"total_tracked": total, "total_sent": sent}
