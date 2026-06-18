# From Zero to Your First Agent — 5 Projects Explained

> A beginner's guide to five small Python programs that each ask an LLM (a large
> language model) to do one useful job. Read them in order: each project adds
> **one new idea** on top of the previous one.
>
> The journey:
> **1. Classify → 2. Extract → 3. Generate → 4. Plan → 5. Decide & Act (a baby agent).**

---

## Part 0 — The stuff that is the same in every file

Before we look at any single project, let's understand the lines that appear at
the **top of all five files**. Once you get these, four-fifths of the "scary"
code disappears, because the rest is just variations.

```python
import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_TOKEN"))
MODEL = "gpt-4o-mini"
```

Line by line:

- **`import os`** — `os` lets your program talk to the operating system. Here we
  only use it to read a secret value (your API key) from the environment.

- **`from dotenv import load_dotenv`** and **`load_dotenv()`** — Your API key is a
  secret password. You should *never* type it directly into your code (someone
  could see it on GitHub). Instead you put it in a hidden file called `.env`:

  ```
  OPENAI_TOKEN=sk-your-secret-key-here
  ```

  `load_dotenv()` reads that file and loads its contents so your program can find
  them. Think of it as "open the secrets file and remember what's inside."

- **`client = OpenAI(api_key=os.getenv("OPENAI_TOKEN"))`** — This creates your
  *connection to OpenAI*. `os.getenv("OPENAI_TOKEN")` fetches the secret you just
  loaded. From now on, `client` is the object you use to send requests to the
  model. (Whenever you see `client.something(...)`, that means "ask OpenAI to do
  something.")

- **`MODEL = "gpt-4o-mini"`** — Which brain to use. `gpt-4o-mini` is a small,
  cheap, fast model — perfect for learning. Storing it in a variable means if you
  ever want a bigger model, you change it in **one** place.

### The two big concepts you'll see everywhere

**Concept A — Pydantic models (the "shape" of the answer).**
Normally an LLM replies with a paragraph of free text. That's hard for code to
use — you'd have to hunt through the words. Instead, we *describe the exact shape*
of the answer we want, using a class:

```python
class Classification(BaseModel):
    sentiment: Literal["positive", "negative", "neutral", "mixed"]
    confidence: float = Field(description="0 to 1")
```

- `BaseModel` comes from a library called **Pydantic**. Inheriting from it
  (`class Classification(BaseModel)`) turns your class into a strict template.
- Each line is a **field**: a name, a colon, and a type.
  `sentiment: str` means "there must be a field called `sentiment`, and it must
  be text."
- `Field(description=...)` adds a human-readable hint. This hint is actually sent
  to the model so it understands what you mean — it's like a comment that the AI
  can read.

**Concept B — `.parse(...)` with `response_format` (getting structured answers).**

```python
completion = client.chat.completions.parse(
    model=MODEL,
    messages=[
        {"role": "system", "content": "Classify customer feedback."},
        {"role": "user", "content": feedback},
    ],
    response_format=Classification,
)
return completion.choices[0].message.parsed
```

What's happening:

- **`messages`** is the conversation you send. Two common roles:
  - `system` = the instructions / the model's job description ("You are a
    classifier.").
  - `user` = the actual input from the person.
- **`response_format=Classification`** is the magic line. It tells OpenAI:
  *"Don't reply with a paragraph. Reply with data that exactly matches this
  template."* OpenAI guarantees the answer fits your Pydantic model.
- **`completion.choices[0].message.parsed`** digs out the result. The reply comes
  wrapped in layers (a list of `choices`, each with a `message`); `.parsed` hands
  you a ready-made `Classification` object, not text. So you can immediately write
  `result.sentiment` and `result.confidence`.

That's the whole trick that makes all five projects possible: **you define a
shape, and the model fills it in.**

---

## Project 1 — Feedback Classifier

**File:** `project_1_classifier.py`
**New idea:** Turn messy text into clean *labels* your code can act on.

### What it does
You give it a customer's free-text complaint or praise. It hands back a tidy
record: is the feedback positive or negative, how sure is it, what topics it
mentions, and whether it's urgent.

### The shape we ask for
```python
class Classification(BaseModel):
    sentiment: Literal["positive", "negative", "neutral", "mixed"]
    confidence: float = Field(description="0 to 1")
    topics: list[str] = Field(description="2-4 short topic tags")
    urgent: bool = Field(description="true if the customer needs a fast response")
```

- **`Literal[...]`** is important and new. It means "this value is *only allowed*
  to be one of these four words." The model can't invent "angry" or "happy" — it
  must pick from your list. This is how you keep an AI's output predictable.
- **`confidence: float`** — a decimal number (e.g. `0.92`).
- **`topics: list[str]`** — a list of text tags, like `["crashes", "data loss"]`.
- **`urgent: bool`** — `True` or `False`, nothing else.

### The function
```python
def classify(feedback: str) -> Classification:
```
Read this as: "a function named `classify` that takes one piece of text
(`feedback`) and gives back a `Classification`." The bit after `->` is just a
*promise* about what comes out — helpful documentation.

### The demo (`if __name__ == "__main__":`)
That phrase means "only run this part if I run *this* file directly" (not if
someone imports it). Inside, we loop over two sample messages and print them:

```python
flag = "🚨" if c.urgent else "  "
print(f"{flag} [{c.sentiment} {c.confidence:.0%}] topics={c.topics}")
```
- `c.urgent` is the `bool` field — if `True`, we show a siren emoji.
- `{c.confidence:.0%}` formats `0.92` as `92%`. The `f"..."` is an *f-string*: a
  string where anything in `{ }` gets replaced by the value of that variable.

### Try it yourself
- Add a new field, e.g. `language: str`, and watch the model fill it in.
- Feed it a sarcastic message and see whether it picks `mixed`.

---

## Project 2 — Information Extractor

**File:** `project_2_extractor.py`
**New idea:** Pull a clean *record* out of a rambling human message.
This is the single most common real-world use of structured output.

### What it does
You paste a casual message like *"let's sync next Tuesday at 3pm in room 412…"*
and it returns an organized meeting record: title, date, time, who's invited,
where, and the to-do items.

### The shape we ask for
```python
class Meeting(BaseModel):
    title: str
    date: Optional[str] = Field(description="ISO date YYYY-MM-DD if mentioned, else null")
    time: Optional[str] = Field(description="e.g. '15:00' if mentioned, else null")
    participants: list[str]
    location: Optional[str]
    action_items: list[str] = Field(description="things someone must do afterwards")
```

The new piece here is **`Optional[str]`**. It means "this field is either a
string **or** nothing (`None`)." Real messages don't always include a date or a
room number, so we tell the model: *"if it's not mentioned, leave it empty
instead of making something up."* This prevents the model from inventing fake
details — a beginner mistake to watch for.

### Why this matters
Imagine 500 emails arriving. Reading each by hand is slow. This function converts
every email into the *same* tidy structure, so the rest of your program can drop
them into a calendar, a database, or a dashboard without any messy text parsing.

### The demo
```python
m = extract(msg)
print("Date / time :", m.date, m.time)
print("To do       :", m.action_items)
```
Notice you access the results with a simple dot: `m.title`, `m.date`,
`m.action_items`. No searching through text — the data is already organized.
(The sample even mixes Cyrillic "Aя" with Latin "Aya"; a good moment to check
whether the model normalizes names sensibly.)

### Try it yourself
- Remove the time from the message and confirm `time` comes back empty.
- Add a `duration_minutes: Optional[int]` field.

---

## Project 3 — Quiz Generator

**File:** `project_3_quiz.py`
**New idea:** *Nested* structures (a list of objects inside another object) and
using the result to run a real interactive program.

### What it does
You give it a topic and a number of questions; it generates a full
multiple-choice quiz, then runs it in your terminal and scores you.

### The shape — note the nesting
```python
class Question(BaseModel):
    question: str
    options: list[str] = Field(description="exactly 4 options")
    correct_index: int = Field(description="0-based index of the correct option")
    explanation: str

class Quiz(BaseModel):
    topic: str
    questions: list[Question]
```

This is the new concept: **`questions: list[Question]`** means a `Quiz` *contains
a list of `Question` objects*. One box that holds many smaller boxes. Pydantic
handles this nesting automatically, and so does OpenAI — it fills the whole tree
in one go.

- **`correct_index: int`** is *0-based*. In programming, counting usually starts
  at 0, so the **first** option is index `0`, the second is `1`, and so on. Worth
  saying out loud to beginners because it trips everyone up at first.

### The interactive part
```python
def run_quiz(quiz: Quiz) -> None:
    score = 0
    for i, q in enumerate(quiz.questions, 1):
        print(f"\nQ{i}. {q.question}")
        for j, opt in enumerate(q.options):
            print(f"   {j}. {opt}")
        answer = input("Your answer (number): ").strip()
        if answer.isdigit() and int(answer) == q.correct_index:
            ...
```

- **`enumerate(quiz.questions, 1)`** loops over the questions *and* gives a
  counter starting at 1 (so it prints "Q1, Q2…"). Without the `1`, it would start
  at 0.
- **`input(...)`** pauses and waits for the user to type. It always returns text,
  so `answer.isdigit()` checks it's actually a number, and `int(answer)` converts
  the text `"2"` into the number `2` before comparing.
- **`-> None`** on the function means "this does work (printing) but doesn't
  return a value."

### Why this is a step up
For the first time the structured output is *fed directly into another program*.
Because `correct_index` is a real integer, the scoring logic is trivial — no
fragile text matching.

### Try it yourself
- Change `difficulty="easy"` to `"hard"` in the last line.
- Make `make_quiz` accept a different topic from your own field of study.

---

## Project 4 — Goal Planner

**File:** `project_4_planner.py`
**New idea:** **Task decomposition** — breaking one big, vague goal into small,
ordered, realistic steps. This is your first real *agent skill*.

### What it does
You hand it a fuzzy goal ("prepare a 10-minute presentation…") and it returns an
ordered plan: a summary plus numbered tasks, each with a priority and a time
estimate.

### The shape
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

Same nesting idea as the quiz (`Plan` holds a `list[Task]`), and `Literal` again
forces priorities into exactly three buckets. Nothing technically new — and
**that's the point**. Once you learn a pattern, you reuse it. The *novelty* here
is conceptual: the model is now doing **reasoning about a process**, not just
labeling or copying text.

### The demo
```python
total = 0
for t in plan.tasks:
    print(f"  {t.step}. [{t.priority:6}] {t.title}  (~{t.estimated_minutes} min)")
    total += t.estimated_minutes
print(f"\nEstimated total: {total} minutes")
```
- `[{t.priority:6}]` — the `:6` pads the word to 6 characters wide so the columns
  line up neatly. A small cosmetic touch.
- We add up `estimated_minutes` as we go to show a grand total. Because each value
  is a real `int`, ordinary math just works.

### Why this matters for agents
"Decompose a goal into steps" is exactly what an autonomous agent must do before
it can act. You've now taught the model to *plan*. The next project teaches it to
*choose and act*.

### Try it yourself
- Give it your own goal ("learn the basics of vLLM in a weekend").
- Add a `depends_on: Optional[int]` field so tasks can reference earlier steps.

---

## Project 5 — Mini Router Agent ⭐ The Big One

**File:** `project_5_router.py`
**New idea:** The model stops *producing content* and starts *deciding what to
do*. It returns a **decision**, and **your Python code runs the matching action.**
This decide-then-act loop is the seed of every real agent.

### The mental model
Up to now, the model's output *was* the answer. Here, the model's output is an
*instruction to your program*: "run the calculator on this input." Your code then
actually does the work. Two brains working together — the model chooses, your
code executes.

### Step 1 — The decision is structured
```python
class Decision(BaseModel):
    action: Literal["calculate", "reverse_text", "word_count", "chitchat"]
    argument: str = Field(description="the input the chosen action needs")
    reasoning: str = Field(description="one short sentence on why this action")
```
- **`action`** is a `Literal` of exactly four choices — the model must pick one of
  the four tools you offer, and nothing else. (This is why `Literal` keeps mattering:
  it makes the model's choice safe to plug into code.)
- **`argument`** is the input that tool needs (e.g. `"23 * 19 + 7"`).
- **`reasoning`** is a short explanation — useful for debugging and for *seeing the
  model think*.

### Step 2 — The "tools" are just normal Python functions
```python
def calculate(expr: str) -> str:
    try:
        return f"= {eval(expr)}"   # ok for a teaching demo; never eval untrusted input in production
    except Exception:
        return "couldn't compute that"

def reverse_text(text: str) -> str:
    return text[::-1]

def word_count(text: str) -> str:
    return f"{len(text.split())} words"
```
There is **no AI inside these functions** — they're plain Python. A "tool" is
simply a function the agent is allowed to call.
- `eval(expr)` runs a string as a Python expression. The comment is a serious
  warning: `eval` will run *any* code, so it's dangerous with untrusted input.
  Fine for a classroom demo; never in production.
- `text[::-1]` is a Python trick that reverses a string.
- `text.split()` breaks text into words by spaces; `len(...)` counts them.

```python
TOOLS = {
    "calculate": calculate,
    "reverse_text": reverse_text,
    "word_count": word_count,
    "chitchat": chitchat,
}
```
This **dictionary** maps each action *name* (text) to the actual *function*.
It's the lookup table that connects the model's decision to real code. (Notice
the keys here are exactly the words in the `Literal` above — they must match.)

### Step 3 — The loop: decide, then act
```python
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
```
The key line is:
```python
result = TOOLS[decision.action](decision.argument)
```
Read it inside-out:
1. `TOOLS[decision.action]` — look up the function the model chose (say,
   `calculate`).
2. `(decision.argument)` — call that function with the argument the model
   provided.

So if the model returns `action="calculate", argument="23 * 19 + 7"`, this line
becomes `calculate("23 * 19 + 7")` and runs it. **The model decided; your code
acted.** That's an agent in miniature.

### The fallback
`chitchat` calls `ask_plain`, which sends a normal request to the model (using
`.create` instead of `.parse`, because here we *want* a free-text reply, not a
structured one). So when none of the real tools fit ("tell me a fun fact"), the
agent just talks normally.

### Why this is the climax
You now have the full pattern: **structured decision → tool lookup → execution.**
Real agents only add more and better tools (search the web, read a file, call an
API) and a loop that repeats until the goal is done. The file's own note says it:
*"Tomorrow the actions become real tools."*

### Try it yourself
- Add a fifth tool, e.g. `def to_upper(text): return text.upper()`, remember to
  add it to **both** the `Literal` and the `TOOLS` dictionary.
- Print `decision.argument` to see what the model decided to pass in.

---

## The big picture — how the five fit together

| Project | New idea | Agent skill it teaches |
|---|---|---|
| 1. Classifier | Labels with `Literal` | Perceive / categorize input |
| 2. Extractor | `Optional` fields, clean records | Read messy reality into structure |
| 3. Quiz | Nested `list[Object]` + use the output | Produce structured content for other code |
| 4. Planner | Task decomposition | Break a goal into steps (planning) |
| 5. Router | Decide-then-act with tools | Choose an action and execute it (agency) |

Every project is the *same two tricks* — **a Pydantic shape** + **`.parse` with
`response_format`** — applied to a slightly bigger ambition. By Project 5 you're
not just getting answers out of a model; you're letting it *drive* your program.
That is the doorway to real agents.

---

## A few beginner gotchas worth repeating

1. **Your `.env` file must exist** and contain `OPENAI_TOKEN=...`, or
   `os.getenv` returns nothing and you'll get an authentication error.
2. **Indexes start at 0** — the first quiz option is option `0`.
3. **`Optional` ≠ optional to send.** The field is always present in the result;
   it's just allowed to be `None` (empty). Tell the model when to leave it empty.
4. **`Literal` is your safety belt.** Any value the model must hand back to your
   code (especially an action name) should be a `Literal`, so it can't surprise you.
5. **Never `eval` real user input.** Project 5 uses it only because it's a
   sandboxed teaching demo.
