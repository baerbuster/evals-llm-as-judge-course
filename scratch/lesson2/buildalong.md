From a grader to a judge: measure the thing that measures your tool

You are writing one file, `build/judge/judge.py`. Every step appends to the bottom of it. It never edits `grader.py`; it imports it. Run it from the `baer-buster` folder:

`python -m build.judge.judge build/fixtures/runs/run5.json`

Add `--live` to call the model. Without it the judge reads the replies already recorded in `build/judge/responses/`.

**Step 1: import the grader and read the history it wrote**

The first line imports lesson 1's file. Importing it runs it on the same run file you passed, so lesson 1's whole output prints first: that is the proof nothing was lost. It appends its own row once and never twice. Then the judge prints its mode and reads lesson 1's `history.csv` back, and you should see the same table lesson 1 printed.

```python
from build.grader.grader import (
    OUTPUTS, RUN, RULES, VERDICTS, CATEGORIES, CATEGORY_OF_RULE,
    LABELED_RUN, LABELS_PATH, HISTORY_PATH, HEADER,
    print_verdict, print_table, read_history,
)
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIVE = "--live" in sys.argv

if LIVE:
    print("mode: live")
else:
    print("mode: replay")

print("== judge step 1: the grader, imported ==")
print("run: " + RUN)
print("outputs: " + str(len(OUTPUTS)))
print("lesson 1 history:")
print_table(HEADER, read_history(HISTORY_PATH))
print()
```

```text
== step 1: load the run ==
run: run5
outputs: 20

== step 2: one rule, two outputs ==
output 13  shape  PASS  4 non-empty lines
output 5  shape  FAIL  5 non-empty lines, expected 4

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

== step 4: rules against the labels ==
agreements: 78
disagreements: 2
output 8  line_length  FAIL  human says pass: a line has 12 words, limit is 11
output 15  line_length  FAIL  human says pass: a line has 12 words, limit is 11

== step 5: sort every failure into a bucket ==
wrong_shape: 7  outputs 0, 5, 7, 8, 10, 15, 18
preamble: 2  outputs 3, 11
copied: 1  outputs 12
passed all rules: 10
pass rate: 0.50

== step 6: one row per run, oldest first ==
run   wrong_shape  preamble  copied  pass_rate
run1  0            0         0       1.00
run2  0            0         0       1.00
run3  0            0         0       1.00
run4  0            0         0       1.00
run5  7            2         1       0.50

== step 7: the trend across the history ==
runs in history: 5
grew the most: wrong_shape +7  pass rate 1.00 -> 0.50  getting worse: yes

mode: replay
== judge step 1: the grader, imported ==
run: run5
outputs: 20
lesson 1 history:
run   wrong_shape  preamble  copied  pass_rate
run1  0            0         0       1.00
run2  0            0         0       1.00
run3  0            0         0       1.00
run4  0            0         0       1.00
run5  7            2         1       0.50
```

**Step 2: the prompt the judge answers and the parser that reads it**

The criterion is a sentence, not a line of Python, so it goes in the prompt. The reply has to come back in a fixed shape or your code cannot use it, so the parser accepts exactly two lines and calls anything else a parse error. No model is called yet: this step parses one well-formed reply and one badly formed one so you can see both paths.

```python
CRITERIA = ["specific", "mood", "no_advice"]
CONDITIONS = {
    "specific": "The poem names at least one concrete detail from the situation, not just a generic feeling.",
    "mood": "The poem's mood fits the situation: no cheerful poem for a loss, no mournful poem for good news.",
    "no_advice": "The poem does not tell the person what to do.",
}
SAMPLE = "VERDICT: FAIL\nREASON: No detail from the situation appears in the poem.\n"


def build_prompt(item, criterion):
    return ("Grade one poem against one criterion.\n\n"
            + "SITUATION:\n" + item["situation"] + "\n\n"
            + "POEM:\n" + item["poem"] + "\n\n"
            + "CRITERION " + criterion + ": " + CONDITIONS[criterion] + "\n\n"
            + "Answer in exactly this shape and nothing else:\n"
            + "VERDICT: PASS\n"
            + "REASON: <one sentence>\n\n"
            + "Write FAIL in place of PASS when the criterion is not met.")


def parse_reply(reply):
    verdict = ""
    reason = ""
    for line in reply.strip().split("\n"):
        text = line.strip()
        if text.startswith("VERDICT:"):
            verdict = text[len("VERDICT:"):].strip()
        if text.startswith("REASON:"):
            reason = text[len("REASON:"):].strip()
    if verdict not in ("PASS", "FAIL") or reason == "":
        return "PARSE_ERROR", "reply did not match the two-line shape"
    return verdict, reason


print("== judge step 2: the prompt and the parser ==")
print("criteria: " + ", ".join(CRITERIA))
print("prompt ends: " + build_prompt(OUTPUTS[0], "specific").split("\n")[-1])
verdict, reason = parse_reply(SAMPLE)
print("sample reply  " + verdict + "  " + reason)
verdict, reason = parse_reply("Sure, the poem is fine.")
print("junk reply  " + verdict + "  " + reason)
print()
```

```text
== judge step 2: the prompt and the parser ==
criteria: specific, mood, no_advice
prompt ends: Write FAIL in place of PASS when the criterion is not met.
sample reply  FAIL  No detail from the situation appears in the poem.
junk reply  PARSE_ERROR  reply did not match the two-line shape
```

**Step 3: ask the judge about one poem**

Live mode calls the model and writes the raw reply to its own file before parsing it. Replay reads that file. Both hand the same text to the same parser, so both print the same verdict. A reply is fetched once per poem and criterion and kept in memory, so a later step never asks again. Output 0 is the Rufus poem that never names Rufus.

```python
REPLIES = {}  # one reply per poem and criterion, so no step asks twice


def response_path(i, criterion):
    return HERE / "responses" / (RUN + "_output" + str(i) + "_" + criterion + ".txt")


def ask_model(prompt):
    import anthropic  # only live mode needs the package, so it is imported here
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in message.content if block.type == "text")


def ask_judge(i, criterion):
    if (i, criterion) in REPLIES:
        return REPLIES[(i, criterion)]
    path = response_path(i, criterion)
    if LIVE:
        reply = ask_model(build_prompt(OUTPUTS[i], criterion))
        path.parent.mkdir(exist_ok=True)
        path.write_text(reply)
    elif path.exists():
        reply = path.read_text()
    else:
        print("missing reply: " + str(path))
        sys.exit(1)
    REPLIES[(i, criterion)] = reply
    return reply


def judge_one(i, criterion):
    return parse_reply(ask_judge(i, criterion))


def print_judge_verdict(i, criterion, verdict, reason):
    if verdict == "PARSE_ERROR":
        print("output " + str(i) + "  " + criterion + "  PARSE_ERROR  " + reason)
    else:
        print_verdict(i, criterion, verdict == "PASS", reason)


print("== judge step 3: one poem, one criterion ==")
verdict, reason = judge_one(0, "specific")
print_judge_verdict(0, "specific", verdict, reason)
print()
```

```text
== judge step 3: one poem, one criterion ==
output 0  specific  FAIL  The poem uses abstract phrasing about absence and quiet but never mentions Rufus, the collar, or the hall specifically.
```

**Step 4: judge every poem on every criterion**

Sixty verdicts, three per output. Only the failures print, the same way the code rules did, because sixty lines would bury them. Output 0's reply is reused from step 3 rather than asked again, so its reason is word for word what you already read.

```python
def judge_run():
    results = {}
    for i in range(len(OUTPUTS)):
        for criterion in CRITERIA:
            results[(i, criterion)] = judge_one(i, criterion)
    return results


JUDGED = judge_run()

print("== judge step 4: three criteria on every output ==")
failures = 0
for i in range(len(OUTPUTS)):
    for criterion in CRITERIA:
        verdict, reason = JUDGED[(i, criterion)]
        if verdict != "PASS":
            print_judge_verdict(i, criterion, verdict, reason)
            failures = failures + 1
print("judge verdicts: " + str(len(JUDGED)))
print("judge failures: " + str(failures))
print()
```

```text
== judge step 4: three criteria on every output ==
output 0  specific  FAIL  The poem uses abstract phrasing about absence and quiet but never mentions Rufus, the collar, or the hall specifically.
output 1  mood  FAIL  The poem undercuts the joyful acceptance news with ominous, mournful imagery like "the sea keeps everything it takes at last," creating a mood mismatched to good news.
output 2  mood  FAIL  The poem presumes grief and loss ("practice her absence") rather than capturing the anxious uncertainty of awaiting unknown biopsy results.
output 3  specific  FAIL  The poem uses only abstract imagery like "hours lie flat and yellow" without mentioning any concrete details such as the chair number, the DMV, or the waiting number.
output 5  specific  FAIL  The poem uses only generic imagery ("great noise," "everything still standing," "sky rinsed clean") without naming any concrete detail like the tornado, the oak tree, or the two streets.
output 7  specific  FAIL  The poem uses generic imagery about first steps and joy but never mentions the kitchen tile, the dog, or the water bowl from the actual situation.
output 8  no_advice  FAIL  The line "Let it turn there, sweet and green, for a stranger" is an imperative instruction telling the person what to do with the air freshener.
output 10  specific  FAIL  The poem uses only generic imagery like "grey" and "weather" without naming specific concrete details from the situation, such as the rain, the library book, or the repeated page.
output 10  no_advice  FAIL  The lines "Put it down. Go out and walk in the weather." directly instruct the person on what to do.
output 11  specific  FAIL  The poem uses only abstract imagery ("a hand in the dark," "the hot thing rising") without naming any concrete detail like the car, the key, the parking lot, or the milk.
output 13  specific  FAIL  The poem stays abstract and never mentions the five dollar bill, the movie ticket, or the winter coat pocket.
output 15  specific  FAIL  The poem uses only generic imagery (warmth, rising, gold) without naming any concrete detail like "bakery," "job," or "Monday" from the actual situation.
output 17  specific  FAIL  The poem uses only vague, generic language ("small complaining thing," "such mending") without naming the gate, olive oil, or WD-40 from the situation.
output 17  no_advice  FAIL  The line "Fix the next one too; it costs you nothing" directly instructs the person on what to do.
output 18  no_advice  FAIL  The lines "Speak up next Tuesday. Put your name on it." directly instruct the person on what actions to take.
output 19  specific  FAIL  The poem uses only abstract imagery (dark, cold, grief) without naming any concrete detail from the situation like the cat, four nights, thinness, or the sweater.
output 19  mood  FAIL  The situation describes the cat's relieved, mundane return, but the poem treats it as a permanent, mournful loss, mismatching the actual mood.
judge verdicts: 60
judge failures: 17
```

**Step 5: score the judge against your labels**

`labels.csv` holds the pass or fail you gave each output of run 5 on all seven criteria, and it covers run 5 and no other run. FAIL is the positive class, so a true positive is the judge failing something you failed. Precision is how much of what it flags you agree with. Recall is how much of what you flag it finds.

```python
import csv


def load_judge_labels(path):
    labels = {}
    with open(path, newline="") as handle:
        for row in csv.DictReader(handle):
            for criterion in CRITERIA:
                labels[(int(row["output"]), criterion)] = row[criterion]
    return labels


def confusion(results, labels, count):
    tp = 0
    fp = 0
    fn = 0
    tn = 0
    for i in range(count):
        for criterion in CRITERIA:
            judge_fails = results[(i, criterion)][0] != "PASS"
            human_fails = labels[(i, criterion)] == "fail"
            if judge_fails and human_fails:
                tp = tp + 1
            elif judge_fails:
                fp = fp + 1
            elif human_fails:
                fn = fn + 1
            else:
                tn = tn + 1
    return tp, fp, fn, tn


def divide(top, bottom):
    if bottom == 0:
        return 0.0
    return top / bottom


print("== judge step 5: the judge against your labels ==")
if RUN == LABELED_RUN:
    JUDGE_LABELS = load_judge_labels(LABELS_PATH)
    TP, FP, FN, TN = confusion(JUDGED, JUDGE_LABELS, len(OUTPUTS))
    PRECISION = divide(TP, TP + FP)
    RECALL = divide(TP, TP + FN)
    print("true positives: " + str(TP))
    print("false positives: " + str(FP))
    print("false negatives: " + str(FN))
    print("true negatives: " + str(TN))
    print("precision: " + f"{PRECISION:.2f}")
    print("recall: " + f"{RECALL:.2f}")
else:
    print("no labels for " + RUN + ", so the judge is not scored on this run")
print()
```

```text
== judge step 5: the judge against your labels ==
true positives: 16
false positives: 1
false negatives: 1
true negatives: 42
precision: 0.94
recall: 0.94
```

**Step 6: the two disagreement lists, kept apart**

The same counts, now as two lists you can read. A false positive is the judge too strict: it failed something you passed, and the fix narrows its idea of failure. A false negative is the judge too lenient: it passed something you failed, and the fix widens it. Each line carries the judge's reason next to your label, which is what tells you which sentence in the prompt to change.

```python
def disagreements(results, labels, count, want):
    rows = []
    for i in range(count):
        for criterion in CRITERIA:
            verdict, reason = results[(i, criterion)]
            judge_fails = verdict != "PASS"
            human_fails = labels[(i, criterion)] == "fail"
            if want == "fp" and judge_fails and not human_fails:
                rows.append((i, criterion, reason))
            if want == "fn" and human_fails and not judge_fails:
                rows.append((i, criterion, reason))
    return rows


print("== judge step 6: where the judge and you disagree ==")
if RUN == LABELED_RUN:
    print("false positives, judge too strict:")
    for i, criterion, reason in disagreements(JUDGED, JUDGE_LABELS, len(OUTPUTS), "fp"):
        print_verdict(i, criterion, False, "human says pass: " + reason)
    print("false negatives, judge too lenient:")
    for i, criterion, reason in disagreements(JUDGED, JUDGE_LABELS, len(OUTPUTS), "fn"):
        print_verdict(i, criterion, True, "human says fail: " + reason)
else:
    print("no labels for " + RUN + ", nothing to disagree with")
print()
```

```text
== judge step 6: where the judge and you disagree ==
false positives, judge too strict:
output 8  no_advice  FAIL  human says pass: The line "Let it turn there, sweet and green, for a stranger" is an imperative instruction telling the person what to do with the air freshener.
false negatives, judge too lenient:
output 6  specific  PASS  human says fail: The poem includes concrete details like "the first one always going to the fire," echoing the burned first pancake from the situation.
```

**Step 7: sort every failure, then append the row**

Every failing output goes to the bucket of the first criterion it failed, in the order shape, line_length, no_preamble, no_copy, specific, mood, no_advice. The table has one column per criterion, the four code rules and the three judge criteria together, and the pass rate counts outputs that passed all seven. The precision and recall print directly above it so nobody reads a judge column without knowing what it is worth. This is a second CSV; lesson 1's file is not touched.

```python
CATEGORY_OF = {"specific": "generic", "mood": "wrong_mood", "no_advice": "advice"}
for rule in RULES:
    CATEGORY_OF[rule] = CATEGORY_OF_RULE[rule]
ALL_CATEGORIES = CATEGORIES + ["generic", "wrong_mood", "advice"]
COLUMNS = RULES + CRITERIA
JUDGE_HISTORY_PATH = HERE / "history.csv"
JUDGE_HEADER = ["run"] + COLUMNS + ["pass_rate"]


def failed_criteria(i):
    names = []
    for rule in RULES:
        if not VERDICTS[(i, rule)][0]:
            names.append(rule)
    for criterion in CRITERIA:
        if JUDGED[(i, criterion)][0] != "PASS":
            names.append(criterion)
    return names


def tally(count):
    counts = {}
    for name in COLUMNS:
        counts[name] = 0
    buckets = {}
    for name in ALL_CATEGORIES:
        buckets[name] = 0
    clean = 0
    for i in range(count):
        names = failed_criteria(i)
        if not names:
            clean = clean + 1
        else:
            first = CATEGORY_OF[names[0]]
            buckets[first] = buckets[first] + 1
        for name in names:
            counts[name] = counts[name] + 1
    return counts, buckets, clean


def append_row(path, header, row):
    if not path.exists():
        with open(path, "w", newline="") as handle:
            csv.writer(handle).writerow(header)
    for old in read_history(path):
        if old[0] == row[0]:
            return  # this run is already in the history; never write it twice
    with open(path, "a", newline="") as handle:
        csv.writer(handle).writerow(row)


COUNTS, BUCKETS, CLEAN = tally(len(OUTPUTS))
JUDGE_PASS_RATE = CLEAN / len(OUTPUTS)
ROW = [RUN]
for name in COLUMNS:
    ROW.append(str(COUNTS[name]))
ROW.append(f"{JUDGE_PASS_RATE:.2f}")
append_row(JUDGE_HISTORY_PATH, JUDGE_HEADER, ROW)
JUDGE_HISTORY = read_history(JUDGE_HISTORY_PATH)

print("== judge step 7: every failure in a bucket, and the row it makes ==")
for name in ALL_CATEGORIES:
    print(name + ": " + str(BUCKETS[name]))
print("passed every check: " + str(CLEAN))
print("pass rate: " + f"{JUDGE_PASS_RATE:.2f}")
if RUN == LABELED_RUN:
    print("judge trust  tp " + str(TP) + "  fp " + str(FP) + "  fn " + str(FN))
    print("precision: " + f"{PRECISION:.2f}")
    print("recall: " + f"{RECALL:.2f}")
else:
    print("no labels for " + RUN + ", the judge columns below are unscored")
print_table(JUDGE_HEADER, JUDGE_HISTORY)
print()
```

```text
== judge step 7: every failure in a bucket, and the row it makes ==
wrong_shape: 7
preamble: 2
copied: 1
generic: 3
wrong_mood: 2
advice: 0
passed every check: 5
pass rate: 0.25
judge trust  tp 16  fp 1  fn 1
precision: 0.94
recall: 0.94
run   shape  line_length  no_preamble  no_copy  specific  mood  no_advice  pass_rate
run1  0      0            0            0        0         0     0          1.00
run2  0      0            0            0        1         0     1          0.90
run3  0      0            0            0        7         0     1          0.60
run4  0      0            0            0        9         0     3          0.40
run5  4      3            5            1        10        3     4          0.25
```

**Step 8: read the answer off the table**

The arithmetic is lesson 1's: the column with the largest rise in failures from the oldest row to the newest, ties going to the leftmost, and whether the newest pass rate is below the oldest. Your history holds one row, so oldest and newest are the same row and the line reads flat. Point the judge at `run1.json` through `run4.json`, oldest first, then at run 5 again. The table fills out, `specific` climbs from run 3 and `no_preamble` breaks open in run 5, and the closing line names the regression with a number behind it.

```python
def judge_trend(rows):
    oldest = rows[0]
    newest = rows[-1]
    best_name = COLUMNS[0]
    best_growth = None
    for col, name in enumerate(COLUMNS, start=1):
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
    return ("trending down the most: " + best_name + " " + f"{best_growth:+d}"
            + "  pass rate " + f"{old_rate:.2f}" + " -> " + f"{new_rate:.2f}"
            + "  getting worse: " + worse)


print("== judge step 8: the answer you came for ==")
print("runs in history: " + str(len(JUDGE_HISTORY)))
print(judge_trend(JUDGE_HISTORY))
print()
```

```text
== judge step 8: the answer you came for ==
runs in history: 5
trending down the most: specific +10  pass rate 1.00 -> 0.25  getting worse: yes
```
