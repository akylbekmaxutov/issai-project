# Day 3 — Student Helper (Read This When You Build)

> This is your **field guide**, not a solution sheet. There is **no code here on
> purpose**. If you want code, the morning examples are your reference. This page
> exists to help you *think*, *get unstuck*, and *check your own work*.
>
> Keep it open in a second tab while you build.

---

## How to use this helper

1. Start each project by reading its short section here **before** you touch the
   keyboard.
2. Do the **schema-on-paper ritual** (below). Always.
3. When you get stuck, go to the **"I'm stuck" checklist** before asking a mentor.
4. When you think you're done, run the **self-check** for that project.

A mentor's job today is to ask you *"what does your schema look like?"* — not to
hand you code. So this guide trains you to answer that question yourself.

---

## The one recipe (it never changes)

Every single project is the same four moves. If you internalize this, you can
build all seven:

1. **Design a schema** — decide the exact shape of the data you want back.
2. **Call `.parse()`** — send your messages with `response_format` set to that schema.
3. **Read `.parsed`** — you get back a real typed object, not text.
4. **Act on the typed object** — loop it, print it, count it, or use it to decide
   what to do next.

If a project feels overwhelming, find which of these four steps you're stuck on.
It's almost always step 1.

---

## The schema-first ritual (non-negotiable)

Before writing any code, on **paper** (or a comment block), write:

- Every field name.
- Its type: text, number (whole or decimal?), true/false, a list, or another object.
- Is it **always present**, or **optional** (might be unknown / not mentioned)?
- If it's a list, a list **of what** — strings, or smaller objects?
- If the value must be one of a few fixed choices, **write those choices down**.

If you can describe the shape clearly in words, the code is almost mechanical.
If you can't, no amount of clever prompting will save you. The bug is in the shape.

---

## Six ideas you'll reach for today

Quick mental refreshers — when a project introduces a "new skill," it's usually one of these.

**1. A schema is a contract.** You're telling the model: *"fill in exactly this,
nothing more, nothing less."* The clearer the contract, the better the output.

**2. Required vs optional.** A required field must always come back. An optional
field is *allowed to be empty* when the information isn't there. Use optional
whenever reality might not supply the value — and tell the model to leave it empty
instead of inventing something.

**3. Closed choices (the "only these values" type).** When a field can only be one
of a small set — `easy/medium/hard`, an action name, `passed: yes/no` — lock it
down. This is what makes the model's output *safe to plug into your code*.

**4. Nesting.** A field can be a list of *objects*, not just a list of strings.
A recipe holds a list of ingredients; an outline holds a list of sections; a grade
holds a list of criteria. Build the small object first, then the big one that
contains a list of it.

**5. Determinism (`temperature`).** Temperature controls randomness. For anything
where you want the **same input to give the same output** — grading, deciding,
evaluating — set it to **0**. For creative generation, a little randomness is fine.

**6. Memory across turns (state) and the loop.** Some projects span several
messages or several steps. The rule: **whatever the model needs to remember, you
must pass back in every time.** The model has no memory of its own — *you* are its
memory.

---

## Project-by-project: questions to ask yourself

For each project: the *real* hurdle, the questions to answer before coding, the
spot it usually breaks, and a self-check beyond the assignment's "done when."

### Project 1 — Recipe Generator 🟢
- **Real hurdle:** your first *nested* model (a list of ingredient objects).
- **Ask yourself:** Is `amount` a number or text? What happens if I forget to
  describe it clearly? What's the difference between my ingredient object and the
  recipe that contains a list of them?
- **Where it breaks:** the model writes `"two"` instead of `2`. Fix it in the
  field description, not by editing the output afterward.
- **Self-check:** can you print a shopping list **and** numbered steps using only
  dot-access on the parsed object, with zero string splitting?

### Project 2 — Answer Grader 🟡
- **Real hurdle:** using the model to **judge**, not create — and making it
  *repeatable*.
- **Ask yourself:** Where does the rubric belong — system or user message? What do
  I pass in so the model isn't just guessing the correct answer? What's my
  threshold for `passed`?
- **Where it breaks:** scores drift between runs (you forgot `temperature=0`), or
  the model is too generous (you didn't tell it to be strict and justify each score).
- **Self-check:** run the *exact same input twice* — are the scores identical? Does
  the feedback name what was actually missing, or is it vague praise?

### Project 3 — Researcher → Writer Chain 🟡
- **Real hurdle:** the **output of call 1 becomes the input of call 2** (chaining).
- **Ask yourself:** How do I hand a structured outline to the second call? (Look
  for the Pydantic method that turns a model into a JSON string.) Why keep
  outlining and writing as two separate calls instead of one big prompt?
- **Where it breaks:** people merge the two steps to "save a call" — and lose the
  entire point of the exercise. Keep each call doing one job.
- **Self-check:** change *only* the topic. Do both the outline and the article
  regenerate? Does the article visibly follow the outline's sections?

### Project 4 — Smart Router with Clarification 🟡
- **Real hurdle:** teaching the agent to **admit it doesn't know** and ask instead
  of guessing.
- **Ask yourself:** Where does the confidence threshold live — in the prompt or in
  my Python? (It must be in your **code**; that's your control, not the model's.)
  What exactly counts as "too vague"?
- **Where it breaks:** the model acts confidently on a bad guess. A good agent that
  asks one clarifying question beats a confident wrong one every time.
- **Self-check:** a clear request acts immediately; a deliberately vague one
  produces a sensible, specific clarifying question.

### Project 5 — Slot-Filling Booking Assistant 🔴
- **Real hurdle:** **state across turns** — gathering fields over several messages.
- **Ask yourself:** Which fields start out unknown (so, optional)? What two things
  must I carry from turn to turn? How does the model know what's *still* missing?
- **Where it breaks:** the bot re-asks for something you already gave it. The cure
  is always the same: **pass the current known state into every prompt** so the
  model only fills the gaps.
- **Self-check:** spread the details across several messages — does it ever repeat
  a question? Does it correctly announce when it's complete?

### Project 6 — Batch Analyzer + Report 🟡
- **Real hurdle:** structured output **at scale** + aggregating many results in
  plain Python.
- **Ask yourself:** What happens to my whole run if item #7 fails? How do I tally
  sentiments and topics once I have a list of parsed records? Which part is the
  model's job and which part is plain Python? (The report is pure Python.)
- **Where it breaks:** one malformed item crashes the entire batch. Wrap each call
  so a single failure is skipped with a warning, not fatal. And print progress so
  a slow run doesn't look frozen.
- **Self-check:** hand it the reviews → get one clean summary **and** a saved file
  of structured records, even if one item misbehaved.

### Project 7 — Mini Multi-Step Agent 🔴 (capstone)
- **Real hurdle:** the real agent loop — **decide → act → observe → repeat**, with
  a way to stop.
- **Ask yourself:** What does the model need to *see* to choose its next step?
  (A running record of what's happened — the "scratchpad.") What's the special
  action that means "I'm finished"? What stops an infinite loop?
- **Where it breaks:** the agent loops forever, or it "forgets" what it just
  learned. Fix: **a maximum-steps limit (not optional)** and **feed every
  observation back into the scratchpad.** Use temperature 0 for steady decisions.
- **Self-check:** it solves a task needing **two or more** tool calls in sequence,
  finishes on its own, and respects the step limit.

---

## The "I'm stuck" checklist (try these before asking)

Work down the list — the answer is usually in the first three:

1. **Look at your schema.** Re-read it out loud. Wrong type? Missing field? A field
   that should be optional but isn't? ~80% of bugs live here.
2. **Read the actual error message.** It names the file and line. Don't skim it.
3. **Print the parsed object** and look at what *actually* came back versus what
   you expected.
4. **Check your `.env`** — is the key loaded? A "missing key / auth" error means
   the secret didn't load.
5. **Is randomness the problem?** If results change run-to-run and shouldn't, set
   temperature to 0.
6. **Did the model lose context?** In multi-turn projects, confirm you're passing
   state/scratchpad back in *every* call.
7. **Find the morning example that matches** and compare its *structure* to yours —
   not to copy, but to spot the missing piece.

---

## Five classic beginner bugs (pre-warned)

- **Numbers come back as words** (`"two"`). → Describe the field clearly as a number.
- **Scores/decisions drift between runs.** → Set temperature to 0.
- **The assistant re-asks what it already knows.** → Pass current state into every prompt.
- **One bad item crashes the whole batch.** → Handle failures per-item; skip with a warning.
- **The agent loops forever.** → Add a maximum-steps limit. Always.

---

## How to know you're *really* done

For any project, you're done when **all** of these are true:

- You access every result with simple dot-access — **no string hunting**.
- The output would survive being fed straight into the next program (a UI, a file,
  a database) without cleanup.
- You tested at least **two** inputs, including one awkward/edge case.
- You can explain *why* each field in your schema has the type it has.

---

## Mindset

- **Paper first, keyboard second.** The students who sketch their schema finish faster.
- **A failed run is information, not a setback.** Read the message; it's telling you the fix.
- **Stuck for 15 minutes?** Re-check your schema, then ask a mentor a *specific*
  question ("my `amount` keeps coming back as text" beats "it doesn't work").
- **Finished early?** Take the best stretch goal: make it work **in Kazakh**. That
  forces real thinking about prompting and validation, not just copied logic.

You already know the recipe. Design the shape, ask for it, read it, act on it.
Everything today is a variation on that. Go build.
