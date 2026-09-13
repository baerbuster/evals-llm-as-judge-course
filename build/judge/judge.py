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
