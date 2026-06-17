"""
project_1_classifier.py — Project 1: Feedback Classifier.

Run with:  python project_1_classifier.py

An agent component that turns free-text feedback into structured labels
your code (or a dashboard) can use directly.
"""

import os
from typing import Literal
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_TOKEN"))
MODEL = "gpt-4o-mini"


class Classification(BaseModel):
    sentiment: Literal["positive", "negative", "neutral", "mixed"]
    confidence: float = Field(description="0 to 1")
    topics: list[str] = Field(description="2-4 short topic tags")
    urgent: bool = Field(description="true if the customer needs a fast response")


def classify(feedback: str) -> Classification:
    completion = client.chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Classify customer feedback."},
            {"role": "user", "content": feedback},
        ],
        response_format=Classification,
    )
    return completion.choices[0].message.parsed


if __name__ == "__main__":
    samples = [
        "App keeps crashing when I open my profile, I've lost work twice today!!!",
        "Good price and nice design, delivery was a bit slow though.",
    ]
    for f in samples:
        c = classify(f)
        flag = "🚨" if c.urgent else "  "
        print(f"{flag} [{c.sentiment} {c.confidence:.0%}] topics={c.topics}")
