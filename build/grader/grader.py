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
