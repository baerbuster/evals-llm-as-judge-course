# Capstone Spec

Topic: Evals and LLM-as-Judge
Learner: someone who shipped an AI feature and cannot tell if it is getting worse
Capstone (from the brief): a working grader printing real precision and recall

This file says what the learner is holding when the last build-along finishes, what it takes in, what it prints, and what "real" means. It is synthesized from checkpoints.md. Checkpoint 6 completes it.

## The question the capstone answers

"Is my AI tool getting worse, and if so, where?"

The learner answers it with two things they did not have before: a grader they can trust, and a number that says how much to trust it.

## The two pieces

The capstone is cut into two pieces, one per lesson, following the checkpoint order. Each is useful on its own. The second takes the first as its input.

### Piece 1: the deterministic grader (lesson 1, checkpoints 1 to 3)

What the learner holds: a command-line grader that loads a saved run, applies code rules to every output, prints each verdict, lists where a rule disagrees with a human label, sorts every failure into a named category, appends one row per run to its own history CSV (code-rule columns only), and prints the history table with a trend line.

Why it stands alone: a learner with only code rules can already answer "is it getting worse, and in which category" for every criterion a rule can check, which is the question they walked in with.

### Piece 2: the LLM-as-judge (lesson 2, checkpoints 4 to 6)

What the learner holds: the same grader, now with a judge that returns a parsed pass/fail verdict and reason for each qualitative criterion, its precision and recall computed against human labels, its false positives and false negatives listed separately, and a second history CSV of the same shape as piece 1's, one column per criterion, code rules and judge criteria together.

Why it is built second: the judge is only worth adding once the learner has a history table shape to put its columns into and human labels to measure it against, both of which piece 1 produced.

### How they compound

Piece 2 takes the grader loop, the code rules, the failure categories, the human labels, and the append/read/trend code from piece 1 as its inputs. What it does not take is piece 1's rows. The two pieces write two separate history CSVs, one per artifact level. Piece 1's CSV has code-rule columns only. Piece 2's CSV has the same shape with the judge columns added. Neither piece opens the other's file, so no row is ever recreated or recomputed.

## What the learner is holding

One grader, run from the command line, that does all of the following in a single run:

1. Loads one saved run of the tool's outputs, the one it is pointed at (checkpoint 3 and 6).
2. Applies code rules to each output and records a pass/fail verdict per rule (checkpoint 1 and 2).
3. Applies an LLM judge to each output for each qualitative criterion and parses a pass/fail verdict plus a reason from a fixed format (checkpoint 4).
4. Sorts every failure into a named failure category (checkpoint 3).
5. Compares the judge's verdicts to human labels on the labeled subset and computes true positives, false positives, false negatives, precision, and recall (checkpoint 5).
6. Lists the judge's false positives and false negatives separately, each with the judge's reason beside the human label (checkpoint 6).
7. Appends one row for this run to the piece 2 history CSV, one column per criterion (code rules and judge criteria together), pass rate at the end. Each row is labeled by the saved run's name (the file it was loaded from), never by wall-clock time, so the same run appended on any machine produces the same row. Earlier rows came from earlier invocations and are never recomputed (checkpoint 3 and 6).
8. States, in one line, which criterion is trending down the most and whether the tool is getting worse overall (checkpoint 6).

## Inputs

- Saved runs: a set of the tool's outputs, one file per run. Fixture data, shipped in the zip.
- History CSVs: two files, one per piece, each holding the rows from previous invocations of that piece. Each is fixture data, shipped in the zip as a seed that has never been run against in place. Piece 1's seed has code-rule columns only. Piece 2's seed has code-rule and judge columns; its earlier rows were produced once during the authoring live run and frozen, so the judge trend has depth from the reviewer's first run. Each grader appends one row per invocation to its own file and reads it back to print the table and the trend line. Earlier rows are never recomputed. The first run of either build-along from a fresh unzip appends one row and matches output/ exactly; each later run adds one more row.
- Human labels: a pass/fail label from a person on a subset of outputs, per criterion. This is the ground truth the judge is measured against. Fixture data, shipped in the zip.
- Criteria: a small set of code rules (checkable in Python) and a small set of qualitative criteria (only checkable by a judge, such as politeness).
- Judge responses: in live mode, from the API. In replay mode, from cached fixtures recorded during a live run. The mode is printed at start.

## What it prints

The final run prints, in this order:

1. The mode (live or replay).
2. Per-step visible checks as each stage runs, so the reviewer can see the grader being built up rather than dropped in finished.
3. The judge's false positives, as a list, each with judge reason and human label.
4. The judge's false negatives, as a separate list, same columns.
5. The confusion counts, precision, and recall for the judge.
6. The full history table read back from the piece 2 CSV, oldest run first, one column per criterion, pass rate last.
7. One closing line: the criterion trending down the most, and whether the tool is getting worse overall.

## What "real" means

Precision and recall are computed from actual judge verdicts compared against actual human labels on the fixture set. They are never hardcoded, never estimated, and never taken from a single example. The same code path produces them in live and replay mode. The only difference between the modes is where the judge's responses come from. Each history CSV is written the same way in both modes and is the one output expected to differ between invocations, by exactly one row per run.

## The positive class

The judge is a defect detector, so FAIL is the positive class. Checkpoint 5 and 6 both use it.

- True positive: the judge fails an output a human also failed.
- False positive: the judge fails an output a human passed (a strict judge).
- False negative: the judge passes an output a human failed (a lenient judge).
- Precision: of the outputs the judge failed, the share a human also failed.
- Recall: of the outputs a human failed, the share the judge caught.

Recall is the number that answers "is the judge missing problems," which is the learner's question. Pass rate in checkpoints 1 to 3 is a separate figure: a count of passes, not a precision or recall number.

## Out of scope

- No UI. Command line only.
- No live API call required to review. Replay mode runs the full capstone from fixtures.
- No quizzes, flashcards, or assessments. The only checks are the ones the grader prints.
- No plotting. The history CSVs are left in a form that can be plotted, but the capstone does not draw them.

## Done when

A reviewer who follows both build-alongs, runs the final command in replay mode, and reads the output can answer "is this tool getting worse, and where" and "how much should I trust the judge that told me" without reading any code.
