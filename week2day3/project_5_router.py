"""
project_5_router.py — Project 5: Mini Router Agent.

Run with:  python project_5_router.py

THE BIG ONE. The model no longer just produces content — it DECIDES what to do.
It returns a structured decision (which action + the argument), and YOUR Python
code runs the matching function. That decide-then-act pattern is the seed of a
real agent. Tomorrow (Day 4) the "actions" become real tools.
"""

import os
from typing import Literal
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_TOKEN"))
MODEL = "gpt-4o-mini"


# ---------- 1) The model's decision is structured ----------
class Decision(BaseModel):
    action: Literal["calculate", "reverse_text", "word_count", "chitchat"]
    argument: str = Field(description="the input the chosen action needs")
    reasoning: str = Field(description="one short sentence on why this action")


# ---------- 2) Our "tools" are just plain Python functions ----------
def calculate(expr: str) -> str:
    try:
        return f"= {eval(expr)}"          # ok for a teaching demo; never eval untrusted input in production
    except Exception:
        return "couldn't compute that"

def reverse_text(text: str) -> str:
    return text[::-1]

def word_count(text: str) -> str:
    return f"{len(text.split())} words"

def chitchat(text: str) -> str:
    return ask_plain(text)               # fall back to a normal model reply

def ask_plain(prompt: str) -> str:
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return r.choices[0].message.content


TOOLS = {
    "calculate": calculate,
    "reverse_text": reverse_text,
    "word_count": word_count,
    "chitchat": chitchat,
}


# ---------- 3) The loop: decide, then act ----------
def route(user_input: str) -> None:
    completion = client.chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Choose the single best action for the user's request."},
            {"role": "user", "content": user_input},
        ],
        response_format=Decision,
    )
    decision = completion.choices[0].message.parsed
    print(f"  🤔 action={decision.action} ({decision.reasoning})")
    result = TOOLS[decision.action](decision.argument)   # YOUR code runs the tool
    print(f"  ➡️  {result}")


if __name__ == "__main__":
    for request in [
        "what is 23 * 19 + 7?",
        "reverse the word 'agents'",
        "how many words are in 'beginners build their first AI agent'?",
        "tell me a fun fact about Kazakhstan",
    ]:
        print(f"\nUSER: {request}")
        route(request)
