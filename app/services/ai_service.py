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
        temperature=0.3,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a senior software engineer specialized in code quality and security. "
                    "Analyze the provided git diff. "
                    "Return a JSON object with the following exact keys: "
                    "bugs, security, improvements, unit_test_suggestions, summary_description. "
                    "Each key except summary_description must contain a list of strings. "
                    "summary_description must be a single string. "
                    "Return only raw JSON, no markdown, no explanation."
                )
            },
            {
                "role": "user",
                "content": f"Here is the diff:\n\n{prompt}"
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