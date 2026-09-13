# Prerequisite judge

This is not a stage. It is one check the pipeline runs on lesson 2's sections, and it is a model
call because no code can read prose and decide whether a concept was taught. `checks.py` reads this
file and sends it with both lessons' sections attached.

The course teaches LLM-as-judge. The pipeline that writes the course uses one on itself, on the one
thing the email grades that only reading can settle: prerequisite order.

## What you are deciding

You are given lesson 1's finished sections and lesson 2's draft sections.

Decide one thing: **does lesson 2 use any concept that lesson 1 never taught and lesson 2 never
teaches itself before using it?**

A concept counts as taught if lesson 1 explained it in plain words, or if lesson 2 explains it in
plain words at or before the first place lesson 2 leans on it. A term defined in a later section than
the one that uses it is not taught in time.

These do not count as untaught, and are not failures:

- Anything a person who has shipped an AI feature already knows: what a prompt is, what a model is,
  running a command, reading a CSV, basic Python.
- A word used in its ordinary English sense rather than as a technical term.
- Lesson 1 material referred to by name without being re-explained. That is required, not a failure.

## What to look for

Read lesson 2 in order, sentence by sentence. At each technical term or idea it leans on, ask where
the reader learned it. If the answer is "nowhere yet," that is the failure.

The common ones on this topic: using precision or recall before the positive class is fixed; using
false positive or false negative before the confusion counts are laid out; leaning on the history
table, the failure categories, the human labels, or the labeled set as if lesson 1 had covered them
when it did not; assuming the reader knows what replay mode is.

Judge what is on the page, not what the lesson clearly meant to say.

## Answer

Answer in exactly this shape and nothing else:

```
VERDICT: PASS
REASON: <one sentence>
```

`PASS` means every concept lesson 2 uses was taught, by lesson 1 or by lesson 2 in time.

`FAIL` means at least one was not. Write `FAIL` in place of `PASS`, and make the reason name the
concept and the section of lesson 2 that used it early, so the writer knows what to fix. One
sentence, the clearest offender if there are several.
