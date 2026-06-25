from pydantic import BaseModel
from typing import Optional, List

class GitHubWebhookPayload(BaseModel):
    action: str
    pull_request: dict
    repository: dict

class ReviewResult(BaseModel):
    bugs: List[str]
    security: List[str]
    improvements: List[str]
    unit_test_suggestions: List[str]
    summary_description: str