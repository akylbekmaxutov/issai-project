# Day 3 — Build Your First AI Agent

**AI Agents Track · Beginner Cohort · ~2.5–3 hours**

> Yesterday you wrote Python. Today you make Python *think* — call a model, control it, force it to give you clean structured data, and then build five small tools that already behave like agents. By the last project, the model won't just *talk*; it will **decide what to do**, and your code will do it.

---

## The plan (and the time budget)

| Part | What you learn | Time |
|---|---|---|
| 0 | Setup — `.env`, `OPENAI_TOKEN`, install | 10 min |
| 1 | Basic usage — your first call | 20 min |
| 2 | Different calls — persona, temperature, memory | 30 min |
| 3 | **Structured output** — JSON, then Pydantic | 35 min |
| 4 | **5 mini-projects** built on structured output | 75 min |
| 5 | Wrap-up + bridge to Day 4 | 10 min |

**The one idea today:** a model call is just a function that takes a list of messages and returns data. Once that data is *structured* (a typed object, not a paragraph), your Python can act on it — and that is what turns a chatbot into an agent.

All runnable code is in the **`day3_code/`** folder. Each file runs on its own with `python <file>.py`.

---

## Part 0 — Setup

```bash
pip install -r requirements.txt      # openai, python-dotenv, pydantic
```

Create a file called **`.env`** next to your code (copy `.env.example`) and put your key in it:

```
OPENAI_TOKEN=sk-your-real-key-here
```

> ⚠️ **Never** put the key directly in your `.py` files, and never commit `.env` to git. Add `.env` to your `.gitignore` today.

Because we named our variable `OPENAI_TOKEN` (not the SDK's default `OPENAI_API_KEY`), we load it ourselves and pass it in:

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()                                      # reads the .env file
client = OpenAI(api_key=os.getenv("OPENAI_TOKEN")) # pass our key explicitly
```

> **Mentor note:** Have everyone run `python llm.py` first. If they see a one-line greeting, their key, environment, and internet all work — debug this *now*, not in the middle of Project 3.

---

## Part 1 — Basic usage  → `01_basic.py`

The whole API is one function. You give it a model and a list of messages; it returns a response object. The text lives at `response.choices[0].message.content`.

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Explain what an LLM is in one sentence."}
    ],
)
print(response.choices[0].message.content)
```

The response also tells you *which* model answered, *why* it stopped (`finish_reason`), and *how many tokens* it cost (`response.usage.total_tokens`) — useful later for watching agent cost.

**Try it:**
1. Run `01_basic.py` and read the reply.
2. `print(response)` once to see how nested the object is, then find where the text lives.
3. Change the question to ask for an explanation in Kazakh or Russian.
4. Write a helper `ask(prompt)` that returns *just* the text, so you stop typing the long path every time. (See `llm.py` for the clean version.)

---

## Part 2 — Different kinds of calls  → `02_different_calls.py`

Three knobs control the model. Master these and you control its behavior.

**A) The system prompt** sets personality and rules. Same question, different system prompt → completely different answer.

```python
messages = [
    {"role": "system", "content": "You are a strict math teacher."},
    {"role": "user",   "content": "How's the weather?"},
]
```

**B) Temperature** controls randomness. `0` = focused and repeatable (use this for decisions and tool-calling). `~1.5` = creative and varied (use this for brainstorming).

```python
client.chat.completions.create(model="gpt-4o-mini", messages=msgs, temperature=0)
```

**C) Memory is just a list.** The model itself remembers *nothing*. You create memory by keeping the message list and appending every turn — both the user's message and the model's reply — then resending the whole list.

```python
messages.append({"role": "user", "content": user_text})
reply = client.chat.completions.create(model=MODEL, messages=messages).choices[0].message.content
messages.append({"role": "assistant", "content": reply})   # <- saving the reply IS the memory
```

**Try it:**
5. Run `02_different_calls.py`. Watch the persona, temperature, and memory effects.
6. Make a fresh conversation, tell it your name, then in turn 2 ask "what's my name?" — confirm it remembers.
7. **Break it:** ask "what's my name?" with an *empty* history. It has no idea. This proves the model is stateless and *you* own the memory.

> **Mentor note:** The break-then-fix in task 7 is the conceptual peak of the morning. Don't skip it — feeling the model forget makes "memory = a list" stick for good.

---

## Part 3 — Structured output  → `03_structured_output.py`

This is the most important part of the day. So far the model returns **sentences**. To build software you need **data** — fields with known names and types. There are three levels:

**Level 1 — Plain text (fragile).** `"This review is mostly positive..."` To use it you'd have to search the string with `if "positive" in text`. It breaks the moment the model phrases things differently.

**Level 2 — JSON mode.** Force the model to return valid JSON, then `json.loads` it into a dict. Better — but nothing guarantees the keys exist or the types are right.

```python
raw = client.chat.completions.create(
    model=MODEL,
    response_format={"type": "json_object"},   # the word "JSON" must appear in your prompt
    messages=[{"role": "user", "content": "Return JSON with keys 'sentiment' and 'reason' ..."}],
).choices[0].message.content
data = json.loads(raw)        # a real dict, but unvalidated
```

**Level 3 — Pydantic (the clean way).** You define the exact shape with a Pydantic class. You hand the class to `.parse()`. You get back a **validated, typed Python object** — the model is *forced* to match your schema.

```python
from pydantic import BaseModel, Field

class ReviewAnalysis(BaseModel):
    sentiment: str = Field(description="positive, negative, or mixed")
    confidence: float = Field(description="a number between 0 and 1")
    pros: list[str]
    cons: list[str]

completion = client.chat.completions.parse(   # .parse(), not .create()
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Analyze the product review."},
        {"role": "user", "content": review},
    ],
    response_format=ReviewAnalysis,            # hand it the class
)

result = completion.choices[0].message.parsed # a real ReviewAnalysis object
print(result.sentiment, result.confidence, result.pros)
```

Three things to teach explicitly here:

- **`BaseModel`** = the blueprint of the data you want.
- **`Field(description=...)`** = a hint to the model about what each field means. Use it generously; it dramatically improves results.
- **`.parsed`** = a normal Python object. `result.pros` is a genuine `list[str]` — autocomplete works, types are guaranteed, no string-searching ever again.

**Try it:**
8. Run `03_structured_output.py` and compare all three levels on the same review.
9. Add a field `recommend: bool` to `ReviewAnalysis` and re-run. Notice you changed *one line* and the model filled it in.
10. Make the model fail gracefully: wrap the `.parse()` call in `try/except` and print a friendly message if validation fails.

> **Mentor note:** The sentence to repeat: *"A Pydantic model is a contract. We tell the model the exact shape, and we get that shape back — guaranteed."* This is the foundation of every project below, and of tool-calling tomorrow.

---

## Part 4 — Five mini-projects

Each project is the same recipe — **define a schema → call `.parse()` → use the typed object** — applied to a different job. They get more agent-like as you go. Budget ~15 minutes each.

### Project 1 — Feedback Classifier  → `project_1_classifier.py`

Turn free-text feedback into labels a dashboard can use: sentiment, confidence, topic tags, and an `urgent` flag. Uses `Literal[...]` to lock `sentiment` to a fixed set of allowed values.

```python
class Classification(BaseModel):
    sentiment: Literal["positive", "negative", "neutral", "mixed"]
    confidence: float
    topics: list[str]
    urgent: bool
```

**Extend it:** add a `language` field; sort a list of feedback so urgent items come first; classify ten messages in a loop.

---

### Project 2 — Information Extractor  → `project_2_extractor.py`

The most common real use of structured output: messy human message → clean record. Note `Optional[str]` for fields that might be missing, and a nested list of `action_items`.

```python
class Meeting(BaseModel):
    title: str
    date: Optional[str]
    time: Optional[str]
    participants: list[str]
    location: Optional[str]
    action_items: list[str]
```

**Extend it:** extract from an email instead; add a `Person` sub-model with name + role and make `participants: list[Person]` (this is *nested* models — very powerful).

---

### Project 3 — Quiz Generator  → `project_3_quiz.py`

Generate a full multiple-choice quiz and run it in the terminal. Because the output is structured, it drops straight into a UI or grader — no parsing. This one maps directly onto an education product.

```python
class Question(BaseModel):
    question: str
    options: list[str]          # 4 options
    correct_index: int
    explanation: str

class Quiz(BaseModel):
    topic: str
    questions: list[Question]   # a model inside a model
```

**Extend it:** add a `difficulty` field; generate the quiz in Kazakh; save the quiz to a JSON file with `model_dump_json()` and reload it later.

---

### Project 4 — Goal Planner  → `project_4_planner.py`

Give a vague goal, get an ordered plan with priorities and time estimates. This is your first real **agent skill: task decomposition** — breaking a big goal into steps.

```python
class Task(BaseModel):
    step: int
    title: str
    priority: Literal["low", "medium", "high"]
    estimated_minutes: int

class Plan(BaseModel):
    goal: str
    summary: str
    tasks: list[Task]
```

**Extend it:** sum the estimated minutes; let the user type their own goal with `input()`; ask the model to flag which tasks could be done in parallel.

---

### Project 5 — Mini Router Agent  → `project_5_router.py`  ⭐

The big one. The model stops *answering* and starts *deciding*. It returns a structured **decision** — which action to run and the argument for it — and **your Python code runs the matching function.** That decide-then-act pattern is the seed of every agent.

```python
class Decision(BaseModel):
    action: Literal["calculate", "reverse_text", "word_count", "chitchat"]
    argument: str
    reasoning: str

# our "tools" are just plain Python functions
TOOLS = {"calculate": calculate, "reverse_text": reverse_text,
         "word_count": word_count, "chitchat": chitchat}

decision = completion.choices[0].message.parsed
result = TOOLS[decision.action](decision.argument)   # the model chose; your code acts
```

**Extend it:** add a new action (e.g. `uppercase`) — notice you add it in *two* places: the `Literal` and the `TOOLS` dict; put the whole thing in a `while True:` loop so it becomes an interactive assistant; have it print `decision.reasoning` so you can see *why* it chose each action.

> **Mentor note:** Stop the room on Project 5 and say it out loud: *"This is an agent in miniature. The only thing missing is letting it loop and call several tools in a row to finish a task — that's literally Day 5."*

---

## Part 5 — Wrap-up and the bridge to Day 4

Today you learned the full recipe and used it five times:

> **define a schema → `.parse()` → act on the typed object.**

You also met the pattern that makes an agent an agent: in Project 5 the model **decided** and your code **acted**.

Tomorrow (Day 4) we make one upgrade. Instead of *you* writing the `TOOLS` dictionary and matching by hand, we hand the function descriptions to the model using OpenAI's **tool calling** feature, and the model returns a structured request to call a specific tool with specific arguments — exactly the `Decision` object from Project 5, but built into the API. Then on Day 5 we put that in a **loop**, so the agent can call several tools in a row until the task is done.

Everything you'll do for the rest of the program stands on what you built today.

---

## File index (`day3_code/`)

- `requirements.txt`, `.env.example` — setup
- `llm.py` — shared client + `ask()` helper (the clean, reusable version)
- `01_basic.py` — Part 1
- `02_different_calls.py` — Part 2
- `03_structured_output.py` — Part 3 (text → JSON → Pydantic)
- `project_1_classifier.py` … `project_5_router.py` — the five projects
