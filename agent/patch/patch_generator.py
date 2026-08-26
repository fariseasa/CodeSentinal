import json
import os

from dotenv import load_dotenv
from groq import Groq

from shared.schemas import (
    Hypothesis,
    IssueTask,
    Patch,
    RetrievedCode,
)


load_dotenv()


class PatchGenerator:

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

    def generate(
        self,
        issue: IssueTask,
        hypothesis: Hypothesis,
        retrieved_code: list[RetrievedCode],
    ) -> Patch:

        evidence = "\n\n".join(
            [
                (
                    f"FILE: {item.file_path}\n"
                    f"CODE:\n{item.content}"
                )
                for item in retrieved_code
            ]
        )

        prompt = f"""
You are a Patch Generation Agent in an
AI software debugging system.

Your task is to generate the smallest safe
code change that fixes the identified bug.

================ ISSUE ================

{issue.issue_description}

================ HYPOTHESIS ================

Explanation:
{hypothesis.explanation}

Confidence:
{hypothesis.confidence}

Suspected Files:
{hypothesis.suspected_files}

================ RETRIEVED CODE ================

{evidence}

================ REQUIREMENTS ================

1. Fix the identified root cause.
2. Make the smallest possible change.
3. Preserve existing behavior for valid inputs.
4. Do not modify tests.
5. Do not modify unrelated files.
6. Do not rewrite the entire file.
7. The patch must be a valid unified diff.
8. Return only one file patch.
9. The file path must be one of the suspected files.
10. Do not invent files or functions.

For this Python project, use Python-specific
error terminology and reasoning.

Return ONLY valid JSON:

{{
    "file_path": "calculator.py",
    "diff": "unified diff here"
}}

Do not include markdown.
Do not include explanations outside the JSON.
"""

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0,
        )

        content = response.choices[0].message.content.strip()

        # Remove Markdown code fences if the LLM adds them
        if content.startswith("```json"):
            content = content[len("```json"):].strip()

        elif content.startswith("```"):
            content = content[len("```"):].strip()

        if content.endswith("```"):
            content = content[:-3].strip()

        try:
            data = json.loads(content)

        except json.JSONDecodeError as error:

            raise ValueError(
                f"LLM returned invalid JSON: {content}"
            ) from error

        return Patch(**data)