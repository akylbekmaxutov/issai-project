"""
02_different_calls.py — Part 2: Different kinds of calls.

Run with:  python 02_different_calls.py

Shows three knobs you control:
  A) the system prompt (personality / instructions)
  B) temperature (focused vs creative)
  C) memory (a growing list of messages)
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_TOKEN"))
MODEL = "gpt-4o-mini"


# ---------- A) The system prompt changes behavior ----------
def with_persona(persona: str, question: str) -> str:
    r = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": persona},
            {"role": "user", "content": question},
        ],
    )
    return r.choices[0].message.content


print("PIRATE :", with_persona("You are a pirate. Answer like a pirate.", "How's the weather?"))
print("TEACHER:", with_persona("You are a strict math teacher.", "How's the weather?"))


# ---------- B) Temperature: focused vs creative ----------
def name_a_cafe(temperature: float) -> str:
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "Invent a name for a coffee shop. Just the name."}],
        temperature=temperature,
    )
    return r.choices[0].message.content

print("\nTEMP 0.0:", name_a_cafe(0.0))
print("TEMP 1.5:", name_a_cafe(1.5))


# ---------- C) Memory is just a list you keep appending to ----------
messages = [{"role": "system", "content": "You are a friendly assistant."}]

def chat_turn(user_text: str) -> str:
    messages.append({"role": "user", "content": user_text})
    r = client.chat.completions.create(model=MODEL, messages=messages)
    reply = r.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})  # <-- save reply = memory
    return reply

print("\nTurn 1:", chat_turn("My name is Akylbek."))
print("Turn 2:", chat_turn("What is my name?"))  # it remembers, because we resent the list
