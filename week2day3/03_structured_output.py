"""
03_structured_output.py — Part 3: Getting structured data out.

Run with:  python 03_structured_output.py

The journey:
  1) Plain text   -> fragile, you'd have to parse it by hand.
  2) JSON mode    -> a JSON string you json.loads() into a dict. Better, but no type safety.
  3) Pydantic     -> a validated, typed Python object. The clean way. <-- use this.
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_TOKEN"))
MODEL = "gpt-4o-mini"

review = "The delivery was super fast and the phone is great, but the box was damaged."


# ---------- 1) Plain text (fragile) ----------
text = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": f"Is this review positive or negative? {review}"}],
).choices[0].message.content
print("1) PLAIN TEXT:", text, "\n")
# Problem: this is a sentence. To use it in code you'd have to search the string. Brittle.


# ---------- 2) JSON mode (a dict, but no validation) ----------
raw = client.chat.completions.create(
    model=MODEL,
    response_format={"type": "json_object"},  # forces valid JSON (word "JSON" must appear in prompt)
    messages=[{
        "role": "user",
        "content": f"Return JSON with keys 'sentiment' and 'reason' for this review: {review}",
    }],
).choices[0].message.content
data = json.loads(raw)            # now it's a real Python dict
print("2) JSON MODE:", data["sentiment"], "->", data["reason"], "\n")
print("3) JSON OUTPUT: ", data, "\n")
# Problem: nothing guarantees the keys or types are what you expect.


# ---------- 3) Pydantic (typed + validated) ----------
class ReviewAnalysis(BaseModel):
    sentiment: str = Field(description="positive, negative, or mixed")
    confidence: float = Field(description="a number between 0 and 1")
    pros: list[str]
    cons: list[str]

completion = client.chat.completions.parse(   # note: .parse(), not .create()
    model=MODEL,
    messages=[
        {"role": "system", "content": "Analyze the product review."},
        {"role": "user", "content": review},
    ],
    response_format=ReviewAnalysis,           # <-- hand it the Pydantic class
)

result = completion.choices[0].message.parsed  # <-- a real ReviewAnalysis object
print("4) PYDANTIC:")
print("   sentiment :", result.sentiment)
print("   confidence:", result.confidence)
print("   pros      :", result.pros)
print("   cons      :", result.cons)
# Now result.pros is a real list[str]. Autocomplete works. Types are guaranteed.
