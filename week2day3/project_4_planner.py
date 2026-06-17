"""
project_4_planner.py — Project 4: Goal Planner.

Run with:  python project_4_planner.py

Give the model a vague goal; get back an ordered, structured plan. This is your
first taste of an agent skill: TASK DECOMPOSITION (breaking a big goal into steps).
"""

import os
from typing import Literal
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_TOKEN"))
MODEL = "gpt-4o-mini"


class Task(BaseModel):
    step: int
    title: str
    priority: Literal["low", "medium", "high"]
    estimated_minutes: int


class Plan(BaseModel):
    goal: str
    summary: str
    tasks: list[Task]


def make_plan(goal: str) -> Plan:
    completion = client.chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Break the user's goal into a short, ordered, realistic plan."},
            {"role": "user", "content": goal},
        ],
        response_format=Plan,
    )
    return completion.choices[0].message.parsed


if __name__ == "__main__":
    plan = make_plan("Prepare a 10-minute presentation about our Kazakh NLP project for beginners.")
    print("GOAL:", plan.goal)
    print("PLAN:", plan.summary, "\n")
    total = 0
    for t in plan.tasks:
        print(f"  {t.step}. [{t.priority:6}] {t.title}  (~{t.estimated_minutes} min)")
        total += t.estimated_minutes
    print(f"\nEstimated total: {total} minutes")
