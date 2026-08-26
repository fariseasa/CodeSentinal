import json
import os

from dotenv import load_dotenv
from groq import Groq

from shared.schemas import (
    CriticVerdict,
    Hypothesis,
    Patch,
    TestResult,
)


load_dotenv()


class CriticAgent:

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

    def evaluate(
    self,
    hypothesis: Hypothesis,
    patch: Patch,
    test_result: TestResult,
    test_code: str = "",
) -> CriticVerdict:

        prompt = f"""
You are the Critic Agent in an AI
software debugging system.

Your job is to determine whether the generated
patch successfully fixes the identified bug.

================ HYPOTHESIS ================

Explanation:
{hypothesis.explanation}

Confidence:
{hypothesis.confidence}

Suspected Files:
{hypothesis.suspected_files}

================ PATCH ================

File:
{patch.file_path}

Diff:
{patch.diff}

================ TEST RESULT ================

Passed:
{test_result.passed}

Logs:
{test_result.logs}

================ RELEVANT TEST CODE ================

{test_code}

================ DECISION RULES ================

1. APPROVE when the patch fixes the identified
   root cause and the tests pass.

2. REJECT when the tests fail.

3. Existing tests are the strongest evidence of
   the intended behavior of the application.

4. Do not invent requirements that are not present
   in the issue, retrieved code, or tests.

5. A patch does not need to preserve an internal
   implementation detail if it preserves the
   behavior required by the tests.

6. For this issue, discount=None is explicitly
   expected to return the original price if the
   relevant test demonstrates that behavior.

7. If tests pass and the patch directly addresses
   the root cause while preserving tested behavior,
   approve the patch.

8. If rejected and another patch could reasonably
   fix the problem, set retry to true.

9. If the patch is fundamentally invalid and retrying
   would not help, set retry to false.

Return ONLY valid JSON:

{{
    "approved": true,
    "reasoning": "The patch fixes the root cause and all tests pass.",
    "retry": false
}}

Do not include Markdown.
Do not include code fences.
Do not include additional fields.
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

        # Handle occasional Markdown code fences.
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

        return CriticVerdict(**data)