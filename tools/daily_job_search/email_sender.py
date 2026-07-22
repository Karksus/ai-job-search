import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.nonmultipart import MIMENonMultipart
from email import encoders
from email.header import Header
from datetime import date
log = logging.getLogger(__name__)

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def send_daily_email(
    ranked_jobs: list[dict],
    drafted: list[dict],
    output_dir: str,
    recipient_email: str,
    profile_name: str = "",
    smtp_email: str = "",
    smtp_password: str = "",
) -> bool:
    if not smtp_email or not smtp_password:
        log.error("SMTP credentials not configured for this profile")
        return False

    if not recipient_email:
        log.error("No recipient email configured for this profile")
        return False

    today = date.today().isoformat()
    name_label = f" ({profile_name})" if profile_name else ""
    subject = f"Daily Job Search{name_label} - {today} - {len(ranked_jobs)} jobs found"

    strong = [j for j in ranked_jobs if j.get("fit") == "strong"]
    medium = [j for j in ranked_jobs if j.get("fit") == "medium"]
    low = [j for j in ranked_jobs if j.get("fit") == "low"]

    html_parts = [
        f"<h2>Daily Job Search Report{name_label} - {today}</h2>",
        f"<p><strong>{len(ranked_jobs)} jobs found</strong>: "
        f"{len(strong)} strong, {len(medium)} medium, {len(low)} low fit</p>",
    ]

    if strong:
        html_parts.append("<h3>Strong Fit</h3><ul>")
        for j in strong:
            score = j.get("score", "?")
            title = j.get("title", "Unknown")
            company = j.get("company", "Unknown")
            location = j.get("location", "Unknown")
            url = j.get("url", "#")
            reason = j.get("reason", "")
            html_parts.append(
                f'<li><a href="{url}"><strong>{title}</strong></a> at {company} ({location}) '
                f'- Score: {score}/100<br>'
                f'<em>{reason}</em></li>'
            )
        html_parts.append("</ul>")

    if medium:
        html_parts.append("<h3>Medium Fit</h3><ul>")
        for j in medium:
            score = j.get("score", "?")
            title = j.get("title", "Unknown")
            company = j.get("company", "Unknown")
            location = j.get("location", "Unknown")
            url = j.get("url", "#")
            reason = j.get("reason", "")
            html_parts.append(
                f'<li><a href="{url}"><strong>{title}</strong></a> at {company} ({location}) '
                f'- Score: {score}/100<br>'
                f'<em>{reason}</em></li>'
            )
        html_parts.append("</ul>")

    if low:
        html_parts.append(f"<h3>Low Fit ({len(low)} jobs)</h3><ul>")
        for j in low:
            title = j.get("title", "Unknown")
            company = j.get("company", "Unknown")
            url = j.get("url", "#")
            html_parts.append(f'<li><a href="{url}">{title}</a> at {company}</li>')
        html_parts.append("</ul>")

    drafted_strong = [d for d in drafted if d.get("cv_compiled")]
    if drafted_strong:
        html_parts.append("<h3>Personalized Documents</h3><p>CV and cover letter PDFs are attached for the top-matched roles.</p>")

    html_parts.append(f"<p><em>Output saved to: {output_dir}</em></p>")
    html_body = "\n".join(html_parts)

    text_parts = [
        f"Daily Job Search Report{name_label} - {today}",
        f"{len(ranked_jobs)} jobs found: {len(strong)} strong, {len(medium)} medium, {len(low)} low",
        "",
    ]
    for label, group in [("STRONG", strong), ("MEDIUM", medium)]:
        if group:
            text_parts.append(f"\n--- {label} FIT ---")
            for j in group:
                text_parts.append(
                    f"  {j.get('score', '?')}/100 - {j.get('title', '?')} at {j.get('company', '?')} ({j.get('location', '?')})"
                )
                text_parts.append(f"  {j.get('url', '')}")
                text_parts.append(f"  {j.get('reason', '')}")
                text_parts.append("")
    text_body = "\n".join(text_parts)

    msg = MIMEMultipart()
    msg["From"] = smtp_email
    msg["To"] = recipient_email
    msg["Subject"] = Header(subject, "utf-8")
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    msg.attach(MIMEText(text_body, "plain", "utf-8"))

    for d in drafted:
        for key in ["cv_path", "cover_letter_path"]:
            path = d.get(key)
            if path:
                try:
                    with open(path, "rb") as f:
                        part = MIMEBase("application", "pdf")
                        part.set_payload(f.read())
                    encoders.encode_base64(part)
                    filename = path.name if hasattr(path, "name") else str(path).split("/")[-1]
                    part.add_header("Content-Disposition", f"attachment; filename={filename}")
                    msg.attach(part)
                except Exception as e:
                    log.error(f"Failed to attach {path}: {e}")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.send_message(msg)
        log.info(f"Email sent from {smtp_email} to {recipient_email}")
        return True
    except Exception as e:
        log.error(f"Email send failed: {e}")
        return False
