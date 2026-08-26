import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


buggy_code = """
def calculate_discount(price, discount):
    return price - (price * discount)


def get_final_price(price, discount):
    if discount is None:
        return calculate_discount(price, discount)

    return calculate_discount(price, discount)
"""


issue = """
The application crashes when discount is None.
Find the root cause and propose a minimal fix.
Do not change unrelated behavior.
"""


prompt = f"""
You are a Python debugging agent.

Analyze the following issue.

ISSUE:
{issue}

CODE:
{buggy_code}

Return your answer using exactly these sections:

ROOT CAUSE:
FIX:
EXPLANATION:
"""


response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0
)


print(response.choices[0].message.content)