# GitSense — AI-Powered Code Review Bot

GitSense is a GitHub App that automatically reviews Pull Requests using a large language model. When a developer opens a PR, GitSense analyzes the code diff and posts a structured comment with bugs, security vulnerabilities, improvements, and unit test suggestions.

## Features

- Automatic detection of critical bugs with explanation and fix suggestion
- Security vulnerability analysis with risk levels (Critical / High / Medium)
- Code quality improvement suggestions
- Unit test recommendations
- Clear PR summary in plain language
- Zero manual intervention — fully automated pipeline

## Architecture

```
GitHub PR Opened
      ↓
GitHub Webhook
      ↓
FastAPI Server (Render)
      ↓
Groq API — llama-3.3-70b-versatile
      ↓
GitHub PR Comment
```

## Tech Stack

- **FastAPI** — Webhook server
- **PyGithub** — GitHub App integration
- **Groq API** — LLM inference (llama-3.3-70b-versatile)
- **Docker** — Containerization
- **Render** — Cloud deployment (free tier)
- **UptimeRobot** — Uptime monitoring

## Local Setup

### Prerequisites

- Python 3.11+
- A GitHub App with Pull Request read/write permissions
- A Groq API key (free at console.groq.com)

### Installation

```bash
git clone https://github.com/DD542/GitSense.git
cd GitSense
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file at the root:

```
GROQ_API_KEY=your_groq_api_key
GITHUB_APP_ID=your_github_app_id
GITHUB_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----
GITHUB_WEBHOOK_SECRET=your_webhook_secret
```

### Running Locally

```bash
uvicorn app.main:app --reload --port 8000
```

Expose the local server with ngrok:

```bash
ngrok http 8000
```

Update the Webhook URL in your GitHub App settings with the ngrok URL + `/webhook`.

## Deployment

The project is production-ready with Docker and Render.

```bash
docker build -t gitsense .
docker run -p 8000:8000 gitsense
```

For Render deployment, connect the GitHub repository and add the environment variables in the Render dashboard. The `render.yaml` file handles the rest.

## Project Structure

```
gitsense/
├── app/
│   ├── main.py              # FastAPI webhook handler
│   ├── config.py            # Environment settings
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   └── services/
│       ├── github_service.py  # GitHub API integration
│       └── ai_service.py      # LLM inference via Groq
├── Dockerfile
├── render.yaml
└── requirements.txt
```

## Example Output

When a Pull Request is opened, GitSense automatically posts:

**GitSense AI Code Review**

**Critical Bugs**
- The function concatenates user input directly into a SQL query, which will cause a TypeError. Use parameterized queries to fix this.

**Security Vulnerabilities**
- SQL Injection (Critical): Direct string concatenation in SQL query allows attackers to inject malicious code. Use parameterized queries or prepared statements.
- Hardcoded password (High): Sensitive credentials must be stored in environment variables or a secrets manager.

**Suggested Improvements**
- Add try-except blocks to handle database exceptions gracefully.
- Validate input types before processing.

**Suggested Unit Tests**
- Test with a valid id to verify correct data retrieval.
- Test with a SQL injection payload to verify protection.

**PR Summary**
This PR introduces a user retrieval function with critical security vulnerabilities that must be addressed before merging.

## License

MIT
