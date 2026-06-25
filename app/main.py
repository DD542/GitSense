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

    if review.bugs:
        sections.append("**Critical Bugs Detected**")
        sections.extend([f"- {bug}" for bug in review.bugs])
    else:
        sections.append("**Critical Bugs:** None detected.")

    if review.security:
        sections.append("\n**Security Vulnerabilities**")
        sections.extend([f"- {issue}" for issue in review.security])
    else:
        sections.append("\n**Security:** No issues found.")

    if review.improvements:
        sections.append("\n**Suggested Improvements**")
        sections.extend([f"- {imp}" for imp in review.improvements])

    if review.unit_test_suggestions:
        sections.append("\n**Suggested Unit Tests**")
        sections.extend([f"- {test}" for test in review.unit_test_suggestions])

    sections.append(f"\n**PR Summary:** {review.summary_description}")

    return "\n".join(sections)