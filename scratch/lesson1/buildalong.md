From a hunch to a grader: build the file one rule at a time

You are writing one file, `build/grader/grader.py`. Every step appends to the bottom of it. Nothing you have already typed is ever edited. Run it from the `baer-buster` folder with the run file as the only argument:

`python -m build.grader.grader build/fixtures/runs/run5.json`

**Step 1: load the run the command line points at**

The grader has to be pointed at one saved run and told nothing else. This step reads that file and prints what it found, so you know the path worked before you write a single rule. The run's name comes from the file name, not the clock, so the same file always produces the same name.

```python
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_run(path):
    return json.loads(Path(path).read_text())


def run_name(path):
    return Path(path).stem


RUN_PATH = sys.argv[1]
OUTPUTS = load_run(RUN_PATH)
RUN = run_name(RUN_PATH)

print("== step 1: load the run ==")
print("run: " + RUN)
print("outputs: " + str(len(OUTPUTS)))
print()
```

```text
== step 1: load the run ==
run: run5
outputs: 20
```

**Step 2: the shape rule, and two verdicts you can check by hand**

This is the rule from the first section: exactly four non-empty lines. The function returns the verdict and the reason together, because a verdict with no reason is not something you can argue with. Run it on output 13 and output 5 and count the lines yourself. You should get the same two answers it does.

```python
def poem_lines(poem):
    lines = []
    for line in poem.split("\n"):
        if line.strip():
            lines.append(line.strip())
    return lines


def check_shape(poem):
    lines = poem_lines(poem)
    if len(lines) == 4:
        return True, "4 non-empty lines"
    return False, str(len(lines)) + " non-empty lines, expected 4"


def print_verdict(i, rule, ok, reason):
    if ok:
        mark = "PASS"
    else:
        mark = "FAIL"
    print("output " + str(i) + "  " + rule + "  " + mark + "  " + reason)


print("== step 2: one rule, two outputs ==")
for index in [13, 5]:
    passed, why = check_shape(OUTPUTS[index]["poem"])
    print_verdict(index, "shape", passed, why)
print()
```

```text
== step 2: one rule, two outputs ==
output 13  shape  PASS  4 non-empty lines
output 5  shape  FAIL  5 non-empty lines, expected 4
```

**Step 3: the other three rules, run over every output**

Now the rest of the rules from the second section, each written as a countable condition. Then one loop that applies all four to all twenty outputs and keeps every verdict. The step prints only the failures, plus the two counts, because eighty passing lines would bury them.

```python
LEAD_INS = ("here is", "here's", "sure")
RULES = ["shape", "line_length", "no_preamble", "no_copy"]


def check_line_length(poem):
    for line in poem_lines(poem):
        if len(line.split()) >= 12:
            return False, "a line has " + str(len(line.split())) + " words, limit is 11"
    return True, "every line under 12 words"


def check_no_preamble(poem):
    first = poem_lines(poem)[0]
    if first.endswith(":") or first.lower().startswith(LEAD_INS):
        return False, "first line is a lead-in: " + first
    return True, "starts on the poem"


def sentences(situation):
    parts = []
    for part in situation.replace("!", ".").replace("?", ".").split("."):
        if len(part.split()) >= 4:
            parts.append(part.strip())
    return parts


def check_no_copy(situation, poem):
    low = poem.lower()
    for sentence in sentences(situation):
        if sentence.lower() in low:
            return False, "poem repeats: " + sentence
    return True, "no sentence copied"


def check_rule(rule, item):
    if rule == "shape":
        return check_shape(item["poem"])
    if rule == "line_length":
        return check_line_length(item["poem"])
    if rule == "no_preamble":
        return check_no_preamble(item["poem"])
    return check_no_copy(item["situation"], item["poem"])


def grade_run(outputs):
    verdicts = {}
    for i, item in enumerate(outputs):
        for rule in RULES:
            verdicts[(i, rule)] = check_rule(rule, item)
    return verdicts


VERDICTS = grade_run(OUTPUTS)

print("== step 3: all four rules on every output ==")
failed = 0
for i in range(len(OUTPUTS)):
    for rule in RULES:
        passed, why = VERDICTS[(i, rule)]
        if not passed:
            print_verdict(i, rule, passed, why)
            failed = failed + 1
print("checks run: " + str(len(VERDICTS)))
print("failed checks: " + str(failed))
print()
```

```text
== step 3: all four rules on every output ==
output 0  shape  FAIL  5 non-empty lines, expected 4
output 0  no_preamble  FAIL  first line is a lead-in: Here is a poem for you:
output 3  no_preamble  FAIL  first line is a lead-in: Sure! Here you go:
output 5  shape  FAIL  5 non-empty lines, expected 4
output 7  shape  FAIL  5 non-empty lines, expected 4
output 7  no_preamble  FAIL  first line is a lead-in: Here is a poem about your daughter:
output 8  line_length  FAIL  a line has 12 words, limit is 11
output 10  line_length  FAIL  a line has 14 words, limit is 11
output 11  no_preamble  FAIL  first line is a lead-in: Here is your poem:
output 12  no_copy  FAIL  poem repeats: I have never been so glad to see a jetway
output 15  line_length  FAIL  a line has 12 words, limit is 11
output 18  shape  FAIL  5 non-empty lines, expected 4
output 18  no_preamble  FAIL  first line is a lead-in: Sure, here you go:
checks run: 80
failed checks: 13
```

**Step 4: put the rules next to your own labels**

`labels.csv` holds the pass or fail you gave each output of run 5 by hand, one column per rule. This step loads them, compares them cell by cell, and prints only where the two of you differ. The labels cover run 5 and nothing else, so the comparison is skipped for any other run. Two disagreements come out, both on the twelve-word edge, and both are the decision the third section asked you to make once.

```python
LABELS_PATH = HERE.parent / "fixtures" / "labels.csv"
LABELED_RUN = "run5"  # labels.csv covers run5 and no other run


def load_labels(path):
    labels = {}
    with open(path, newline="") as handle:
        for row in csv.DictReader(handle):
            for rule in RULES:
                labels[(int(row["output"]), rule)] = row[rule]
    return labels


def compare_to_labels(verdicts, labels, count):
    agreed = 0
    disagreed = []
    for i in range(count):
        for rule in RULES:
            passed, why = verdicts[(i, rule)]
            if passed:
                mine = "pass"
            else:
                mine = "fail"
            theirs = labels[(i, rule)]
            if mine == theirs:
                agreed = agreed + 1
            else:
                disagreed.append((i, rule, mine, theirs, why))
    return agreed, disagreed


print("== step 4: rules against the labels ==")
if RUN == LABELED_RUN:
    LABELS = load_labels(LABELS_PATH)
    AGREED, DISAGREED = compare_to_labels(VERDICTS, LABELS, len(OUTPUTS))
    print("agreements: " + str(AGREED))
    print("disagreements: " + str(len(DISAGREED)))
    for i, rule, mine, theirs, why in DISAGREED:
        print_verdict(i, rule, mine == "pass", "human says " + theirs + ": " + why)
else:
    print("no labels for " + RUN + ", skipping the comparison")
print()
```

```text
== step 4: rules against the labels ==
agreements: 78
disagreements: 2
output 8  line_length  FAIL  human says pass: a line has 12 words, limit is 11
output 15  line_length  FAIL  human says pass: a line has 12 words, limit is 11
```

**Step 5: sort every failure into one named bucket**

Each failing output goes to the bucket of the first rule it failed, in the order the rules are listed. Output 0 fails shape and no_preamble; shape comes first, so it lands in `wrong_shape` and stays there for good. The pass rate at the bottom counts only outputs that passed all four rules.

```python
CATEGORY_OF_RULE = {
    "shape": "wrong_shape",
    "line_length": "wrong_shape",
    "no_preamble": "preamble",
    "no_copy": "copied",
}
CATEGORIES = ["wrong_shape", "preamble", "copied"]


def categorize(verdicts, count):
    buckets = {}
    for name in CATEGORIES:
        buckets[name] = []
    passed_all = 0
    for i in range(count):
        first_failed = None
        for rule in RULES:
            passed, why = verdicts[(i, rule)]
            if not passed and first_failed is None:
                first_failed = rule
        if first_failed is None:
            passed_all = passed_all + 1
        else:
            buckets[CATEGORY_OF_RULE[first_failed]].append(i)
    return buckets, passed_all


BUCKETS, PASSED = categorize(VERDICTS, len(OUTPUTS))
PASS_RATE = PASSED / len(OUTPUTS)

print("== step 5: sort every failure into a bucket ==")
for name in CATEGORIES:
    members = BUCKETS[name]
    numbers = []
    for i in members:
        numbers.append(str(i))
    print(name + ": " + str(len(members)) + "  outputs " + ", ".join(numbers))
print("passed all rules: " + str(PASSED))
print("pass rate: " + f"{PASS_RATE:.2f}")
print()
```

```text
== step 5: sort every failure into a bucket ==
wrong_shape: 7  outputs 0, 5, 7, 8, 10, 15, 18
preamble: 2  outputs 3, 11
copied: 1  outputs 12
passed all rules: 10
pass rate: 0.50
```

**Step 6: append this run to the history and print the table**

One row per run, written once. If `history.csv` is missing the grader creates it with the header line and nothing else, so every row in the table comes from a run you actually pointed it at. The row is labeled with the run's name. Grading the same run twice does not write it twice.

```python
HISTORY_PATH = HERE / "history.csv"
HEADER = ["run"] + CATEGORIES + ["pass_rate"]


def read_history(path):
    if not path.exists():
        return []
    rows = []
    with open(path, newline="") as handle:
        reader = csv.reader(handle)
        next(reader, None)  # drop the header line
        for row in reader:
            rows.append(row)
    return rows


def history_row(run, buckets, pass_rate):
    row = [run]
    for name in CATEGORIES:
        row.append(str(len(buckets[name])))
    row.append(f"{pass_rate:.2f}")
    return row


def append_history(path, row):
    if not path.exists():
        with open(path, "w", newline="") as handle:
            csv.writer(handle).writerow(HEADER)
    for old in read_history(path):
        if old[0] == row[0]:
            return  # this run is already in the history; never write it twice
    with open(path, "a", newline="") as handle:
        csv.writer(handle).writerow(row)


def print_table(header, rows):
    widths = []
    for col in range(len(header)):
        width = len(header[col])
        for row in rows:
            if len(row[col]) > width:
                width = len(row[col])
        widths.append(width)
    for line in [header] + rows:
        cells = []
        for col in range(len(line)):
            cells.append(line[col].ljust(widths[col]))
        print("  ".join(cells).rstrip())


append_history(HISTORY_PATH, history_row(RUN, BUCKETS, PASS_RATE))
HISTORY = read_history(HISTORY_PATH)

print("== step 6: one row per run, oldest first ==")
print_table(HEADER, HISTORY)
print()
```

```text
== step 6: one row per run, oldest first ==
run   wrong_shape  preamble  copied  pass_rate
run1  0            0         0       1.00
run2  0            0         0       1.00
run3  0            0         0       1.00
run4  0            0         0       1.00
run5  7            2         1       0.50
```

**Step 7: read the trend off the table**

The closing line does arithmetic you can check by eye: the category with the largest rise in failures from the oldest row to the newest, ties going to the leftmost column, and whether the newest pass rate is below the oldest. Your history holds one row so far, so the oldest and the newest row are the same row and the line reads flat. Point the grader at `run1.json` through `run4.json`, oldest first, then at run 5 again, and the table fills out and the line starts naming the regression.

```python
def trend_line(rows):
    oldest = rows[0]
    newest = rows[-1]
    best_name = CATEGORIES[0]
    best_growth = None
    for col, name in enumerate(CATEGORIES, start=1):
        growth = int(newest[col]) - int(oldest[col])
        if best_growth is None or growth > best_growth:
            best_growth = growth
            best_name = name
    old_rate = float(oldest[-1])
    new_rate = float(newest[-1])
    if new_rate < old_rate:
        worse = "yes"
    else:
        worse = "no"
    return ("grew the most: " + best_name + " " + f"{best_growth:+d}"
            + "  pass rate " + f"{old_rate:.2f}" + " -> " + f"{new_rate:.2f}"
            + "  getting worse: " + worse)


print("== step 7: the trend across the history ==")
print("runs in history: " + str(len(HISTORY)))
print(trend_line(HISTORY))
print()
```

```text
== step 7: the trend across the history ==
runs in history: 5
grew the most: wrong_shape +7  pass rate 1.00 -> 0.50  getting worse: yes
```
