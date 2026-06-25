from github import GithubIntegration
from app.config import get_settings

settings = get_settings()

def _get_github_for_installation(installation_id: int):
    integration = GithubIntegration(
        integration_id=int(settings.github_app_id),
        private_key=settings.github_private_key.replace('\\n', '\n')
    )
    return integration.get_github_for_installation(installation_id)

def get_pr_diff(installation_id: int, repo_name: str, pr_number: int):
    gh = _get_github_for_installation(installation_id)
    repo = gh.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    diff_files = []
    for file in pr.get_files():
        diff_files.append({
            "filename": file.filename,
            "patch": file.patch,
            "status": file.status
        })
    return diff_files

def post_comment(installation_id: int, repo_name: str, pr_number: int, body: str):
    gh = _get_github_for_installation(installation_id)
    repo = gh.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(body)