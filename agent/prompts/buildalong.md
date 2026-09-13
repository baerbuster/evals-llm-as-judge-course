# Build-along stage

## Content

You are writing the build-along for one lesson. The lesson number is given below. Lesson 1's build-along reaches checkpoints 1 to 3 and lesson 2's reaches checkpoints 4 to 6, as assigned in checkpoints.md.

A build-along is a list of steps. In each step the learner adds a small amount of code to one file, runs it, and sees something print. The three "Test:" lines of the lesson's three checkpoints are three of those printed outputs, and they happen in checkpoint order. You choose the steps between them. No more than eight steps in total.

The learner writes one file, per build_layout.md: `build/grader/grader.py` in lesson 1, `build/judge/judge.py` in lesson 2. Lesson 2's file begins with one import line, `from build.grader.grader import ...`, and uses lesson 1's functions. It never copies them and never edits grader.py.

Each step's code is appended to the end of that file. A step can only add lines. It can never change or remove a line from an earlier step. So write every step so that the file, as it stands after that step, runs from the top and prints that step's output. Functions defined in earlier steps are called, not redefined.

Because the file prints everything from every step each time it runs, a step's expected-output block shows only the lines that step adds, not the lines from earlier steps. The pipeline checks it by running the file before and after the step and comparing the difference.

The files the code reads and writes, exactly:

- The run to grade is the one file path given on the command line: `python -m build.grader.grader build/fixtures/runs/run5.json`. It is a JSON list of objects, each with a `situation` string and a `poem` string. The poem's lines are separated by newline characters.
- Every other path is built from the code file's own location with `Path(__file__).resolve().parent`, never from the current directory, so the same command works on any machine.
- `build/fixtures/labels.csv` has a header row: `output`, then the four code rules, then the three judge criteria, in the order tool.md lists them. `output` is the poem's index in run 5, starting at 0. Every other cell is the string `pass` or `fail`.
- `history.csv` sits next to the code file. The code appends one row per run and reads the whole file back to print the table. It never rewrites or removes an existing row. The row is labeled by the run file's name, such as `run5`, never by the date or time. The code never invents rows: if `history.csv` is missing, the code creates it with the header line only, and every row in the table comes from a run the code was actually pointed at. There is no seed table typed into the code. The shipped history is made by pointing the code at run1, run2, run3, and run4 in order before the reader points it at run5, so while you trace the steps the table holds only the run being graded, and the trend line reads accordingly.
- Lesson 2 only: `labels.csv` covers run 5 and no other run. The steps that compare the judge to the labels, the confusion counts, precision, recall, and the two disagreement lists, run only when the run on the command line is the labeled one. For any other run the code still asks the judge, records the replies, counts the failures, appends the row, and prints the table, and it says in one line that this run has no labels so the judge is not scored on it.
- Lesson 2 only: the judge's raw replies live in `build/judge/responses/`, one file per reply, named `<run>_output<i>_<criterion>.txt`. Live mode writes them; replay mode reads them and stops with the missing path if one is absent.

Lesson 2 only, the judge:

- The judge model is `claude-sonnet-5`, called through the `anthropic` package with `anthropic.Anthropic()`, which reads the API key from the environment. Nothing else is imported for it.
- A reply's `content` is a list of blocks and the first one is not always the text, because the model can return a thinking block first. Read the text with `"".join(block.text for block in message.content if block.type == "text")`, never `message.content[0].text`. Give the call enough `max_tokens` that a reply which thinks first still has room to print both lines; 2000 is plenty for a two-line answer.
- The judge is asked about one poem and one criterion per call, and at most once per poem and criterion in a whole run. When an early step asks about one poem to show a single verdict and a later step asks about every poem, the later step reuses the reply the early step already recorded instead of asking again, so a reply file is written once per run and live mode and replay mode print the same reason for that poem. Its prompt gives the situation, the poem, and the criterion's pass condition from tool.md, and tells it to answer in exactly this shape and nothing else:

```
VERDICT: PASS
REASON: <one sentence>
```

  with `FAIL` in place of `PASS` when the criterion is not met.

- The parser reads those two lines and nothing else. A reply that does not match the shape is a parse failure, printed as such, not silently treated as a pass.
- Replay is the default and needs no key. `--live` calls the model and writes each raw reply to its response file before parsing it. Both modes run the same parser on the same text. The first line printed is `mode: replay` or `mode: live`, per record_replay.md.

The closing line's arithmetic is fixed so every learner gets the same answer from the same table:

- "Grew the most" (lesson 1) or "trending down the most" (lesson 2) is the column with the largest increase in failure count between the oldest row and the newest row. Ties go to the column that comes first in the table.
- "Getting worse" is true when the newest row's pass rate is lower than the oldest row's.

A learner can check both by eye against the printed table.

The code must print the same bytes on every machine, every run. So it never:

- prints a date, time, or duration;
- uses random numbers or anything seeded by time;
- prints the contents of a set without sorting them first, since set order changes between runs;
- prints a float without a fixed number of decimals, such as `f"{x:.2f}"`;
- lists files from a folder without sorting the names;
- depends on the current directory, environment variables, or the operating system.

## View

The prose between steps uses the same voice as the sections: second person, one reader, short sentences, plain words, no jokes, no exclamation points, no cheerleading. Directives are allowed here and expected: "add this," "run it," "you should see." Each step's prose is a few sentences at most: what this step adds, why, and what to look for in the output.

The code is written to be typed in by a learner and read at a glance:

- Plain Python 3.12. Standard library only, except the `anthropic` package in lesson 2.
- Small functions with names that say what they do, such as `load_run`, `check_shape`, `append_history`.
- No classes, no type hints, no decorators, no comprehensions nested inside comprehensions.
- A comment only where a line would otherwise be a mystery, one line long.
- Every step's code block is short enough to type without scrolling, roughly 25 lines at most.

What the code prints, since output/ is the first thing the reviewer reads:

- One fact per line.
- A verdict line is `output <i>  <rule or criterion>  <PASS|FAIL>  <reason>`, two spaces between fields, in that order.
- A table has a header row and every column padded with spaces so the columns line up when read in a terminal.
- A count or a rate is on its own line with a label, such as `precision: 0.83`. Rates have two decimals.
- Each step's output starts with a line naming the step, such as `== step 3: apply the rule to every output ==`, and ends with a blank line, so the reader can see where one step's output ends.
- Lesson 2's first printed line, before anything else, is the mode.

Return the build-along text and nothing else, in the shape lesson_format.md fixes for everything below the `---`. Do not include the `---` itself; the pipeline adds it. The reply is:

````
<one plain title line for the build-along>

**Step 1: <what this step adds>**

<a few sentences of prose>

```python
<the code the learner appends in this step>
```

```text
<only the new lines this step prints>
```

**Step 2: ...**
````

Steps are numbered 1, 2, 3 with no gaps, no more than 8. Every step has exactly one python block and exactly one text block, in that order. No text block is empty. No `#` or `##` headings anywhere in the reply.

## Controller

Work in this order:

1. List the steps. The three checkpoint "Test:" prints are milestones, in order. Fill in the steps between them. Eight at most.
2. Write the whole final file, top to bottom, as it will stand after the last step. Make it run.
3. Cut it into the steps. Check that the file as it stands after each step runs on its own from the top, with nothing referenced before it is defined.
4. For each step, trace the code by hand against the actual fixture data given below and write down exactly what it prints. The expected output comes from the code and the data, never from what you meant the code to do. Count the real poems, apply the real rules, read the real labels.
5. Write the prose around each step last.

Lesson 2 only: any step whose printed output depends on what the judge says, its verdicts, its reasons, the confusion counts, precision, recall, the false positive and false negative lists, and the judge columns of the history table, cannot be traced by hand, because the judge has not been called yet. For those steps, write the text block as your best guess at the shape and mark it by making its first line `(judge-dependent; filled in from the live run)`. The pipeline replaces those blocks with the real output after the live run. Steps that depend only on the code rules and the fixtures are traced exactly, as in lesson 1.

Before you return, check your own work:

- Steps are numbered 1 to N with no gaps, and N is at most 8.
- The lesson's three checkpoint "Test:" prints are present, in checkpoint order, each as some step's output.
- Every step has exactly one python block and exactly one text block, in that order, and no text block is empty.
- The file as it stands after each step runs from the top: nothing is used before it is defined, and no step redefines an earlier function.
- Nothing from the determinism list appears anywhere in the code.
- Lesson 2's first code block begins with the import from `build.grader.grader` and the first step's output is the same history table lesson 1 printed. That step only reads and prints lesson 1's history CSV. It never appends to it; lesson 2 appends only to its own history CSV next to judge.py.
- Every text block that does not depend on the judge was traced against the real fixtures, poem by poem.
- Every judge-dependent text block carries the marker line.
- Every file path and column name matches the list in the content section exactly.

When things conflict:

- The step cap wins over the line cap. If reaching the checkpoints needs more code than eight steps of 25 lines, let a step's code block run longer. Never add a ninth step and never drop a checkpoint.
- The print house style decides the shape of a line; the checkpoint's test decides what the line must contain. When the test says "print PASS and FAIL with the reason," the line is a verdict line in the fixed field order, and the reason is in it.

If you receive a list of failures after your reply, return the complete corrected build-along, every step, in the same shape. Keep everything that was not named in the failures. No explanation, no partial reply.

One failure is special. When the pipeline ran your code and a step's real output did not match its text block, the failure quotes both. Decide which one is wrong and fix that one. If the code did what the step meant, fix the text. If the code is wrong, fix the code and retrace the text. Never change the text to match code that is broken.
