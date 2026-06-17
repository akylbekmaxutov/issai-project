"""
project_3_quiz.py — Project 3: Quiz Generator.

Run with:  python project_3_quiz.py

Generate a ready-to-use multiple-choice quiz. The structured output means you
can feed it straight into a UI, a grader, or a database — no string parsing.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_TOKEN"))
MODEL = "gpt-4o-mini"


class Question(BaseModel):
    question: str
    options: list[str] = Field(description="exactly 4 options")
    correct_index: int = Field(description="0-based index of the correct option")
    explanation: str


class Quiz(BaseModel):
    topic: str
    questions: list[Question]


def make_quiz(topic: str, n: int, difficulty: str = "easy") -> Quiz:
    completion = client.chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "system", "content": f"Create a {difficulty} multiple-choice quiz."},
            {"role": "user", "content": f"Make {n} questions about: {topic}"},
        ],
        response_format=Quiz,
    )
    return completion.choices[0].message.parsed


def run_quiz(quiz: Quiz) -> None:
    """A tiny interactive quiz in the terminal."""
    score = 0
    for i, q in enumerate(quiz.questions, 1):
        print(f"\nQ{i}. {q.question}")
        for j, opt in enumerate(q.options):
            print(f"   {j}. {opt}")
        answer = input("Your answer (number): ").strip()
        if answer.isdigit() and int(answer) == q.correct_index:
            print("✅ Correct!")
            score += 1
        else:
            print(f"❌ Correct answer: {q.correct_index} — {q.explanation}")
    print(f"\nScore: {score}/{len(quiz.questions)}")


if __name__ == "__main__":
    quiz = make_quiz("the basics of how an LLM works", n=3, difficulty="easy")
    run_quiz(quiz)
