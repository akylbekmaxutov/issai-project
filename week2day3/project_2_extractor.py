"""
project_2_extractor.py — Project 2: Information Extractor.

Run with:  python project_2_extractor.py

Turn a messy human message into a clean structured record — the single most
common real-world use of structured output.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_TOKEN"))
MODEL = "gpt-4o-mini"


class Meeting(BaseModel):
    title: str
    date: Optional[str] = Field(description="ISO date YYYY-MM-DD if mentioned, else null")
    time: Optional[str] = Field(description="e.g. '15:00' if mentioned, else null")
    participants: list[str]
    location: Optional[str]
    action_items: list[str] = Field(description="things someone must do afterwards")


def extract(message: str) -> Meeting:
    completion = client.chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Extract the meeting details from the message."},
            {"role": "user", "content": message},
        ],
        response_format=Meeting,
    )
    return completion.choices[0].message.parsed


if __name__ == "__main__":
    msg = (
        "Hey, let's sync on the Kazakh benchmark paper next Tuesday at 3pm in room 412. "
        "Aя, Dana and I should be there. Aya, please bring the latest results table, "
        "and someone needs to email the reviewers before then."
    )
    m = extract(msg)
    print("Title       :", m.title)
    print("Date / time :", m.date, m.time)
    print("Who         :", m.participants)
    print("Where       :", m.location)
    print("To do       :", m.action_items)
