import asyncio
import hmac
import hashlib
from fastapi import FastAPI, Request, HTTPException
from app.config import get_settings
from app.services.github_service import get_pr_diff, post_comment
from app.services.ai_service import review_code_diff
from app.models.schemas import ReviewResult

settings = get_settings()
app = FastAPI(title="GitSense AI Code Reviewer")

def verify_signature(payload: bytes, signature: str) -> bool:
    expected = hmac.new(
        key=settings.github_webhook_secret.encode(),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)

@app.post("/webhook")
async def webhook_handler(request: Request):
    payload_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")

    if not signature or not verify_signature(payload_body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event = request.headers.get("X-GitHub-Event")
    data = await request.json()

    if event == "pull_request" and data.get("action") == "opened":
        installation_id = data["installation"]["id"]
        repo_name = data["repository"]["full_name"]
        pr_number = data["pull_request"]["number"]

        diff_files = await asyncio.to_thread(get_pr_diff, installation_id, repo_name, pr_number)
        review: ReviewResult = await review_code_diff(diff_files)

        comment_body = build_comment_body(review)
        await asyncio.to_thread(post_comment, installation_id, repo_name, pr_number, comment_body)

        return {"status": "review_completed", "pr": pr_number}

    return {"status": "ignored"}

def build_comment_body(review: ReviewResult) -> str:
    sections = []

    sections.append("## GitSense AI Code Review")
    sections.append("")

    if review.bugs:
        sections.append("### Critical Bugs")
        for bug in review.bugs:
            sections.append(f"- {bug}")
    else:
        sections.append("### Critical Bugs")
        sections.append("- No critical bugs detected.")

    sections.append("")

    if review.security:
        sections.append("### Security Vulnerabilities")
        for issue in review.security:
            sections.append(f"- {issue}")
    else:
        sections.append("### Security Vulnerabilities")
        sections.append("- No security issues found.")

    sections.append("")

    if review.improvements:
        sections.append("### Suggested Improvements")
        for imp in review.improvements:
            sections.append(f"- {imp}")

    sections.append("")

    if review.unit_test_suggestions:
        sections.append("### Suggested Unit Tests")
        for test in review.unit_test_suggestions:
            sections.append(f"- {test}")

    sections.append("")
    sections.append("### PR Summary")
    sections.append(review.summary_description)

    return "\n".join(sections)