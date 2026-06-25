from openai import AsyncOpenAI
import json
from app.config import get_settings
from app.models.schemas import ReviewResult

settings = get_settings()

client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=settings.groq_api_key
)

def construct_prompt(diff_files: list) -> str:
    formatted_files = []
    for file in diff_files:
        formatted_files.append(
            f"File: {file['filename']}\nStatus: {file['status']}\nChanges:\n{file.get('patch', 'No patch')}"
        )
    return "\n\n---\n\n".join(formatted_files)

async def review_code_diff(diff_files: list) -> ReviewResult:
    prompt = construct_prompt(diff_files)

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert senior software engineer and security specialist with 15 years of experience. "
                    "Your code reviews are thorough, precise, and actionable. "
                    "For each issue you find, always explain: what the problem is, why it is dangerous, and how to fix it concretely. "
                    "Analyze the provided git diff and return a JSON object with these exact keys:\n"
                    "- bugs: list of strings, each describing a bug with explanation and fix suggestion\n"
                    "- security: list of strings, each describing a security vulnerability with its risk level (Critical/High/Medium) and concrete remediation\n"
                    "- improvements: list of strings, each describing a code quality improvement with rationale\n"
                    "- unit_test_suggestions: list of strings, each describing a specific test case with the scenario and expected behavior\n"
                    "- summary_description: a single string with a clear, concise summary of what this PR does and its overall quality assessment\n"
                    "Return only raw JSON, no markdown, no explanation outside the JSON."
                )
            },
            {
                "role": "user",
                "content": f"Please review this code diff:\n\n{prompt}"
            }
        ]
    )

    content = response.choices[0].message.content
    clean = content.replace("```json", "").replace("```", "").strip()
    data = json.loads(clean)

    summary = data.get("summary_description", "No summary generated.")
    if isinstance(summary, list):
        summary = " ".join(summary)

    return ReviewResult(
        bugs=data.get("bugs", []),
        security=data.get("security", []),
        improvements=data.get("improvements", []),
        unit_test_suggestions=data.get("unit_test_suggestions", []),
        summary_description=summary
    )