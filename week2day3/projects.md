# Day 3 — Practice Projects (Build These Yourself)

No code is given. You already know the recipe from this morning: **design a schema → call `.parse()` → read `.parsed` → act on the typed object.** Apply it. Write your schema on paper first, then code. Difficulty: 🟢 warm-up · 🟡 core · 🔴 challenge.

---

## Project 1 — Recipe Generator 🟢

**What you'll build:** ask for a dish, get back a fully structured recipe you could drop into an app.

**New skill:** nested models — a list of *objects*, not just a list of strings.

**Design your schema:**
- An ingredient object: a name, an amount (a *number*, not text), and a unit (grams, cups, pieces…).
- A `Recipe`: title, servings (integer), total minutes (integer), a difficulty that can only be `easy` / `medium` / `hard`, an `ingredients` field that is a **list of ingredient objects**, and a `steps` field that is a list of strings.

**Steps:**
1. On paper, write out both models and their field types.
2. Define the small ingredient model, then the `Recipe` model that contains a list of it.
3. Make the call with `.parse()` and `response_format` set to your `Recipe` model.
4. Read `.parsed`.
5. Loop over the ingredients to print a clean shopping list, then print the numbered steps.
6. Test with two dishes, including one unusual request.

**Hints & gotchas:** the model will try to write `amount` as a word like "two" — describe the field clearly so it returns a number. Add a `Field` description to the unit to keep it consistent.

**Stretch:** scale the servings in Python (double every amount). Add a dietary constraint like "vegetarian". Generate the recipe in Kazakh.

**Done when:** you can print a tidy ingredient checklist and numbered steps straight from the parsed object, with no string parsing.

---

## Project 2 — Answer Grader 🟡

**What you'll build:** an LLM-as-judge. Give it a question, a reference answer, and a student's answer; get back a structured grade against a rubric.

**New skill:** using the model to **evaluate** instead of generate — the core of benchmarking and eval work.

**Design your schema:**
- A per-criterion object: the criterion name, a score (e.g. 0–5), and a short comment.
- A `Grade`: an overall score, a list of those criterion objects, written feedback, and a boolean `passed`.

**Steps:**
1. Decide your rubric criteria (for example: accuracy, completeness, clarity).
2. Define the per-criterion model and the `Grade` model.
3. Put the rubric in the **system prompt** and tell the model to be strict and justify each score.
4. Pass the question, the reference answer, and the student answer in the user message.
5. Set `temperature` to 0.
6. Parse and print the grade.
7. Run the exact same input twice and confirm the scores are identical.

**Hints & gotchas:** without `temperature=0` the grades drift and become useless. Models grade too generously — push back in the prompt. If you don't give the reference answer, it will just guess.

**Stretch:** grade a list of answers in a loop and compute the average. Then grade three answers yourself and compare — do you agree with the model?

**Done when:** the same input always gives the same scores, and the feedback names what was actually missing.

---

## Project 3 — Researcher → Writer Chain 🟡

**What you'll build:** two calls where the output of the first feeds the second. Call 1 turns a topic into a structured outline; call 2 turns that outline into a finished short article.

**New skill:** prompt chaining — the most important pattern after routing. Real agents are mostly small structured calls feeding each other.

**Design your schema:**
- An `Outline` containing a list of `Section` objects, each with a heading and a list of key points.
- For call 2 you can return plain text (the article), or an `Article` model with a title and body if you want to stay structured.

**Steps:**
1. Define the `Section` and `Outline` models.
2. Make call 1: topic → `Outline`, using `.parse()`.
3. Turn the parsed outline back into a JSON string (find the Pydantic method that dumps a model to JSON).
4. Make call 2: put that JSON inside the prompt and ask the model to write the article *following that outline*.
5. Print the outline, then the article.
6. Change only the topic and confirm both regenerate end-to-end.

**Hints & gotchas:** keep each call doing one job — outlining and writing are deliberately separate. If you merge them into one prompt you lose the whole point of the chain.

**Stretch:** add a third "editor" call that takes the article and returns structured suggestions (what to cut, what to clarify).

**Done when:** changing the topic regenerates outline and article, and the article visibly follows the outline.

---

## Project 4 — Smart Router with Clarification 🟡

**What you'll build:** an upgrade of this morning's router that knows when it *doesn't* know. If the request is ambiguous, it asks a question instead of guessing.

**New skill:** graceful uncertainty — an agent that acts confidently on a bad guess is worse than one that asks.

**Design your schema:**
- A `Decision` like the morning's router, but add `ask_user` as one of the allowed actions, plus a `confidence` number (0–1) and an optional `clarifying_question`.

**Steps:**
1. Define the `Decision` model with the extra `ask_user` action, `confidence`, and `clarifying_question`.
2. In the system prompt, tell the model to choose `ask_user` when the request is vague or missing information.
3. Make the call and parse the decision.
4. In your Python, branch three ways: if the action is `ask_user` **or** confidence is below your threshold (say 0.6), print the clarifying question and stop; otherwise run the chosen tool.
5. Test one clear request and one deliberately vague request.

**Hints & gotchas:** set the confidence threshold in your **code**, not the prompt — that's your control. Be explicit in the system prompt about what counts as "too vague".

**Stretch:** make it a loop — after the user answers the clarifying question, feed the answer back and route again.

**Done when:** a clear request acts immediately, and a vague one produces a sensible clarifying question.

---

## Project 5 — Slot-Filling Booking Assistant 🔴

**What you'll build:** an assistant that collects every field needed to book something (a meeting: title, date, time, attendees) across **several turns**, asking only for what's still missing, and stopping when it has everything.

**New skill:** stateful multi-turn collection (slot filling) — the backbone of booking, onboarding, and form-filling assistants.

**Design your schema:**
- A `BookingState` where every field is **optional** (it might not be known yet), plus a `missing_fields` list of field names and a boolean `is_complete`.

**Steps:**
1. Define `BookingState` with all-optional fields plus `missing_fields` and `is_complete`.
2. Keep two things across turns: the conversation messages and the current known state.
3. Each turn, send the user's new message *and* the current state to the model, and get an updated `BookingState`.
4. Ask the user for the first item in `missing_fields`.
5. Loop until `is_complete` is true.
6. Test by spreading the details across several messages and confirm it never re-asks something you already gave.

**Hints & gotchas:** the main trap is the bot re-asking for what it already knows. Fix it by passing the current state into **every** prompt so the model only fills gaps. Let the model report `missing_fields` itself first; compare with your own logic later.

**Stretch:** read the full booking back for confirmation before finalizing. Handle a mid-flow change like "actually, make it Thursday".

**Done when:** over a few messages it gathers all fields, never repeats a question, and announces it's complete.

---

## Project 6 — Batch Analyzer + Report 🟡

**What you'll build:** feed in a list of ~15 customer reviews, classify each with structured output, then print an aggregate report: counts per sentiment, the most common topics, and the percentage marked urgent.

**New skill:** structured output **at scale** plus aggregating many results — the muscle you use to build datasets and benchmarks.

**Design your schema:** reuse the classifier model from this morning for each single item. The report itself is computed in plain Python from the list of parsed objects.

**Steps:**
1. Hard-code a list of ~15 reviews (or read them from a small text file).
2. Loop over the reviews and parse each into a structured record.
3. Wrap each call in `try/except` so one failure doesn't stop the whole batch.
4. Collect every record into a list.
5. Use a `Counter` to tally sentiments and topics, and compute the percentage marked urgent.
6. Print the report.

**Hints & gotchas:** print progress (`12/15…`) so a slow batch doesn't look frozen. A single malformed item should be skipped with a warning, not crash the run.

**Stretch:** read the reviews from a real CSV file. Save all structured records to a JSON file. Sort the output so urgent negative reviews come first.

**Done when:** you hand it the reviews and get back one clean summary plus a saved file of structured records.

---

## Project 7 — Mini Multi-Step Agent 🔴 (capstone)

**What you'll build:** a small agent that solves a task needing **more than one step**. Given a task, it repeatedly decides the next action, runs that tool, feeds the result back, and loops — until it produces a final answer.

**New skill:** the agent loop — *decide → act → observe → repeat*, with a stopping condition. This is the real thing, and it's the bridge to Day 5.

**Design your schema:**
- A `Step` with a short `thought`, an `action` that is one of your tools **or** the special value `final_answer`, and an `argument`.

**Steps:**
1. Write 2–3 simple tools (a calculator, a text utility, a fake lookup).
2. Define the `Step` model.
3. Keep a "scratchpad" string that records what has happened so far.
4. Loop: ask the model for the next `Step` (pass it the scratchpad) → run the chosen tool → append the result to the scratchpad → repeat.
5. Stop when the action is `final_answer` and print the answer.
6. Add a maximum-steps limit (for example 6) so the agent can never loop forever.
7. Test with a task that needs at least two tool calls in sequence.

**Hints & gotchas:** the maximum-steps limit is not optional — a confused agent looping forever is the number-one beginner bug. Use `temperature` 0 for steady decisions, and feed every observation back in or the agent forgets what it just learned.

**Stretch:** give it a two-part word problem that forces it to use the calculator twice.

**Done when:** it solves a task needing two or more tool calls, finishes on its own, and respects the step limit.

---

## Mentor notes — running a self-directed block

- **Don't give code.** When someone's stuck, ask "what does your schema look like?" — the bug is almost always there. Point them at the matching morning example, not a solution.
- **Schema-first on paper** is non-negotiable. Walk the room and check paper schemas before anyone starts typing.
- **Priority order:** Projects 1–3 are the must-dos (nesting, evaluation, chaining). Projects 4–6 are the core agent patterns. Project 7 is a reach goal — celebrate anyone who lands it, and tell the rest it's literally Day 5's topic.
- **Pre-warn the common bugs:** numbers returned as strings (fix with clear field descriptions), the slot-filler re-asking known fields (pass state into every prompt), and the agent loop running forever (max-steps limit).
- For pairs who finish early, the best stretch is "now make it work in Kazakh" — it forces real thought about prompting and validation, not just copied logic.