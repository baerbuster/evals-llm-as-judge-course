# The Tool Being Graded

Topic: Evals and LLM-as-Judge
Learner: someone who shipped an AI feature and cannot tell if it is getting worse
Capstone: a working grader printing real precision and recall

This file fixes the fake AI tool the course grades. The examples stage invents its outputs from this, and both build-alongs grade against the rules and criteria named here.

## What the tool does

A person writes a short situation from their life, one or two sentences. The tool returns a four-line poem about it.

Input example: "My dog died last week and the house is too quiet."
Output: four lines of poem, nothing else.

## Code rules (lesson 1, checked in Python)

Each is pass or fail, and a second person applying it reaches the same verdict.

| Rule | Pass condition |
|---|---|
| shape | Exactly 4 non-empty lines |
| line_length | Every line is under 12 words |
| no_preamble | No title line and no lead-in such as "Here is a poem" or "Sure" before the poem |
| no_copy | No sentence from the situation appears verbatim in the poem |

## Judge criteria (lesson 2, only a judge can check)

Each is concrete and yes-or-no, so human labels and the judge can disagree only for real reasons.

| Criterion | Pass condition |
|---|---|
| specific | The poem names at least one concrete detail from the situation, not just a generic feeling |
| mood | The poem's mood fits the situation; no cheerful poem for a loss, no mournful poem for good news |
| no_advice | The poem does not tell the person what to do |

## Failure categories (checkpoint 3)

Every failure is sorted into exactly one of these.

- wrong_shape: shape or line_length failed
- preamble: no_preamble failed
- copied: no_copy failed
- generic: specific failed
- wrong_mood: mood failed
- advice: no_advice failed

## The degradation story

Five saved runs, oldest to newest. Twenty situations each, the same twenty in every run so runs are comparable.

- Run 1: the original prompt. Nearly everything passes.
- Run 2: same, small drift. One or two new failures.
- Run 3: someone trimmed the prompt to save tokens. Poems go generic and start losing the situation's details.
- Run 4: generic gets worse, and a few poems start offering advice.
- Run 5: a model swap on top of the trimmed prompt. Preambles appear and line counts break. This is the run the learner is asked to diagnose.

The trend the capstone should surface: specific and no_preamble are the criteria trending down the most, and the tool is getting worse overall.

## Human labels

All twenty outputs of run 5 are labeled pass or fail on every criterion, the four code rules and the three judge criteria. The code-rule labels are what checkpoint 2 compares the rules against. The judge-criteria labels are the ground truth for precision and recall. The labels are shipped with the course; the lesson frames them as labels the learner made earlier.

The judge should be right most of the time but not always. A few false positives and a few false negatives are needed so checkpoints 5 and 6 have something to show.
