import json
import os
from typing import List

from dotenv import load_dotenv
from groq import Groq

from shared.schemas import (
    Hypothesis,
    IssueTask,
    RepoMap,
    RetrievedCode,
)


load_dotenv()


class InvestigationAgent:

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

    def investigate(
        self,
        issue: IssueTask,
        repo_map: RepoMap,
        retrieved_code: List[RetrievedCode],
    ) -> Hypothesis:

        evidence = "\n\n".join(
            [
                (
                    f"FILE: {item.file_path}\n"
                    f"RELEVANCE: "
                    f"{item.relevance_score:.4f}\n"
                    f"CODE:\n{item.content}"
                )
                for item in retrieved_code
            ]
        )

        repository_context = f"""
FILES:
{repo_map.files}

MODULES:
{repo_map.modules}

DEPENDENCIES:
{repo_map.dependencies}

FUNCTIONS:
{repo_map.functions}

CLASSES:
{repo_map.classes}
"""

        prompt = f"""
You are the Investigation Agent in an
AI software debugging system.

Your job is to identify the most likely
root cause of the reported bug.

IMPORTANT:
You must reason ONLY from the repository
context and retrieved code provided below.

Do not invent files, functions, or behavior.

================ ISSUE ================

Description:
{issue.issue_description}

Investigation Goals:
{issue.goals}

================ REPOSITORY MAP ================

{repository_context}

================ RETRIEVED CODE ================

{evidence}

================ TASK ================

Determine:

1. What is the most likely root cause?
2. Which file(s) are responsible?
3. Why does the code produce the reported behavior?
4. How confident are you?

Return ONLY valid JSON:

{{
    "explanation": "detailed root-cause explanation",
    "confidence": 0.0,
    "suspected_files": [
        "file.py"
    ]
}}

The confidence must be a number between 0 and 1.

Do not include markdown.
Do not include text outside the JSON.
"""

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
        )

        content = response.choices[0].message.content

        try:
            data = json.loads(content)

        except json.JSONDecodeError as error:

            raise ValueError(
                f"LLM returned invalid JSON: {content}"
            ) from error

        return Hypothesis(**data)