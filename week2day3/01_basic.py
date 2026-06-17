"""
01_basic.py — Part 1: Basic usage.

Run with:  python 01_basic.py

Goal: make your first call and pull the text out of the response.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_TOKEN"))

# 1. The simplest possible call.
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Explain what an LLM is in one sentence."}
    ],
)

# 2. The text lives deep inside the response object.
print("REPLY:", response.choices[0].message.content)

# 3. The response also carries useful metadata.
print("MODEL:", response.model)
print("FINISH REASON:", response.choices[0].finish_reason)
print("TOKENS USED:", response.usage.total_tokens)
