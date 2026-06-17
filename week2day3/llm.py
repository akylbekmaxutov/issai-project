"""
llm.py — our shared connection to the model.

Every other file can do:
    from llm import client, MODEL
and reuse the same configured client instead of repeating setup.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load the .env file so OPENAI_TOKEN becomes available via os.getenv(...)
load_dotenv()

# Note: we use OPENAI_TOKEN (our chosen name), NOT the SDK's default OPENAI_API_KEY,
# so we must pass the key explicitly.
client = OpenAI(api_key=os.getenv("OPENAI_TOKEN"))

# Cheap, fast, supports structured outputs. Swap for a newer model anytime.
MODEL = "gpt-4o-mini"


def ask(prompt: str, system: str = "You are a helpful assistant.") -> str:
    """Send one prompt, get plain text back."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    # Quick smoke test: `python llm.py`
    print(ask("Say hello to the AI agents interns in one short sentence."))
