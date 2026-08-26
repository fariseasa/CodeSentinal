import json
import os

from dotenv import load_dotenv
from groq import Groq

from shared.schemas import IssueTask


load_dotenv()


class IssueUnderstandingAgent:

    def __init__(self):

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not set"
            )

        self.client = Groq(
        api_key=api_key,
        timeout=120.0,
        )

    def understand(
        self,
        issue_description: str
    ) -> IssueTask:

        prompt = f"""
You are an issue understanding agent
for an AI software debugging system.

Analyze the following bug report.

BUG REPORT:
{issue_description}

Return ONLY valid JSON.

The JSON must contain exactly these fields:

{{
    "issue_description": "clear description of the problem",
    "goals": [
        "investigation goal 1",
        "investigation goal 2"
    ],
    "suspected_files": []
}}

Do not include markdown.
Do not include explanations outside the JSON.
"""

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        content = response.choices[0].message.content

        try:
            data = json.loads(content)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"LLM returned invalid JSON: {content}"
            ) from error

        return IssueTask(**data)