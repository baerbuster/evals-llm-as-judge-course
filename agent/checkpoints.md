# Checkpoints

Topic: Evals and LLM-as-Judge
Learner: someone who shipped an AI feature and cannot tell if it is getting worse
Capstone: a working grader printing real precision and recall

A checkpoint is something the learner can now do and could not before. Each one below maps one-to-one to a breaking point in breaking_points.md, is phrased as an action, and has a visible test the build-along can print.

## Lesson 1 Checkpoints

### Checkpoint 1 (from breaking point 1: intuition vs evidence)

**Can write a pass/fail rule for a single output that a second person could apply and reach the same verdict.**

Before: "correct" is a feeling they cannot hand to anyone.
After: they hold a written rule with a concrete condition, and they can show one output that passes it and one that fails it.
Test: apply the rule to two outputs and print PASS and FAIL with the reason.

### Checkpoint 2 (from breaking point 2: raw evidence that disagrees with intuition)

**Can run their rules over a set of outputs and list every case where the rule's verdict disagrees with their own label.**

Before: they have rules but no way to use them on more than one output at a time.
After: they have a loop that grades a set, compares each verdict to a human label, and prints the disagreements.
Test: print the count of agreements and disagreements, then each disagreement with the rule's verdict next to the human label.

### Checkpoint 3 (from breaking point 3: what the final grade means)

**Can sort every failure into a named bucket, append the run to a history of every past run, and read a run-by-category table to state whether the tool is getting worse and in which bucket.**

Before: they see a pass rate and stop. A single number from a single run cannot tell them if anything changed, and two runs can only show a blip, not a trend.
After: they have a small set of failure categories, every failure is assigned to one, and every run is appended to a history file. The history is a table with one row per run and one column per category, plus overall pass rate. It is saved in a plain format such as CSV so they can drop it into a spreadsheet or plotting library if they want to.
Test: print the full history table, one row per run and one column per category with pass rate at the end, oldest run first. Then print a single line naming which category grew the most across the history and whether the overall pass rate is trending down.

## Lesson 2 Checkpoints

### Checkpoint 4 (from breaking point 4: qualitative criteria)

**Can write a judge prompt that returns a pass/fail verdict for a criterion no code rule can check.**

Before: their grader only handles conditions they can express in code.
After: they have a prompt that takes an output and a criterion such as politeness and returns a verdict in a fixed format their grader can parse.
Test: run the judge on one output and print the parsed verdict and the judge's reason.

### Checkpoint 5 (from breaking point 5: judging the judge)

**Can compute the judge's precision and recall against a set of human labels.**

Before: they have no number for how much to trust the judge.
After: they treat the human labels as ground truth with FAIL as the positive class, count true positives (judge failed, human failed), false positives (judge failed, human passed), and false negatives (judge passed, human failed), and compute both metrics. Precision is the share of the judge's failures a human agreed with. Recall is the share of the human's failures the judge caught.
Test: print the confusion counts, precision, and recall for the judge on the labeled set.

### Checkpoint 6 (from breaking point 6: error analysis on the judge)

**Can separate the judge's false positives from its false negatives, name a different fix for each, and then append the judge's verdicts to a run-by-criterion history table that states whether the tool is getting worse.**

Before: they have a precision and recall number and no idea what to do with it, and they still have not answered the question they started with.
After: they read the two kinds of disagreement as two different problems: a false positive means the judge is too strict (it failed something a human passed), a false negative means the judge is too lenient (it passed something a human failed), and they can say which prompt change addresses each. With a judge they trust, the grader appends its row to a second history table of the same shape as checkpoint 3's, with the judge columns added. Checkpoint 3's table is left untouched; no earlier row is recomputed. The new table has one row per run and one column per criterion, both the code rules from checkpoint 3 and the qualitative criteria from checkpoint 4, plus overall pass rate. It stays in a plain format such as CSV so it can be plotted directly.
Test: print the false positives and false negatives in two separate lists, each with the judge's reason beside the human label. Then print the judge's confusion counts, precision, and recall so the reader knows how much to trust every judge column before reading them. Then print the full history table, one row per run and one column per criterion with pass rate at the end, oldest run first. End with a single line naming which criterion is trending down the most and whether the tool is getting worse overall.

---

Count: 6 checkpoints. At 1 to 3 per lesson, two lessons hold all six at 3 each.
Order: each checkpoint uses only what the ones before it produced. Checkpoint 6 completes the capstone.
