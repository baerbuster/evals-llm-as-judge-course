"""The checks run.py runs on every model reply.

run() gets the stage name, the lesson number, the files the splitter just wrote, and whether this
is a --replay run. It returns a list of failure messages. An empty list means the stage passed.
Every message goes straight back to the model as feedback, so each one says exactly what is wrong
and what would fix it, like "section 3 is 612 words, cut it to under 500".

Two kinds of check live here and the difference is the whole design.

A deterministic check reads what the model wrote and decides on its own. Counts, word limits,
markers, well-formed SVG, and the four code rules from tool.md are all deterministic: the same
input gives the same verdict every time, and the check costs nothing to run.

A judge check asks a model, because no code can settle it. There are three, and all are skipped
on a --replay run so the deterministic checks can be re-tested without an API key.

The first is on lesson 2's sections, asking whether lesson 2 leans on a concept lesson 1 never
taught.

The second is on either lesson's sections, asking whether every technical term in it is the
industry's rather than one the writer coined. Both of these read prose, which is why neither is
code.

The second is on the examples stage. tool.md says the judge should be right most of the time but
not always, so checkpoints 5 and 6 have false positives and false negatives to show. No code can
tell whether a poem is hard to judge, so this check runs the course's own judge (the judge model
from config, given tool.md's pass condition, the situation, and the poem) on every output of the
labeled run and counts where it disagrees with the labels. Too few disagreements, or none in one
direction, and the fixtures go back to the model with every verdict attached. The judge criteria
in runs 1 to 4 are still not checked: they carry no labels, and a judge measured against nothing
is circular. That half of the degradation story first becomes visible when the capstone prints
its history table.
"""

import ast
import csv
import json
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ElementTree
from pathlib import Path

from agent import config


def run(stage: str, lesson: int | None, written: list[Path], replay: bool = False) -> list[str]:
    if stage == "examples":
        return check_examples(replay)
    if stage == "sections":
        return check_sections(lesson, replay)
    if stage == "diagrams":
        return check_diagrams(lesson, written)
    if stage == "buildalong":
        return check_buildalong(lesson)
    return [f"no checks are defined for the stage {stage}"]


# ----------------------------------------------------------------- shared bits

# An SVG block plus the caption line under it, so section word counts ignore both.
SVG_AND_CAPTION = re.compile(r"<svg\b.*?</svg>[^\n]*\n?[^\n]*", re.DOTALL | re.IGNORECASE)

# A line that opens a quiz, flashcard, exercise, or assessment block. The word starts the line,
# optionally as a heading, a bold line, or a numbered label, and is followed by nothing, a closing
# **, or a colon or dash and a title. Ordinary prose using the word ("try this exercise now",
# "exercises are boring") has no separator after it and is safe.
BANNED_BLOCK = re.compile(
    r"^\s*(?:#{1,6}\s*|\*\*\s*|\d+[.)]\s*)?"
    r"(quiz|quizzes|flash ?cards?|exercises?|assessments?|worksheets?|self.?tests?)\b"
    r"(?:\s*\*\*)?(?:\s*[:\-—].*)?\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def word_count(text: str) -> int:
    """Words in a section body, with any SVG block and its caption line removed first."""
    return len(SVG_AND_CAPTION.sub(" ", text).split())


def banned_blocks(text: str, where: str) -> list[str]:
    found = sorted({m.group(1).lower() for m in BANNED_BLOCK.finditer(text)})
    return [
        f"{where} opens a {name} block; the course has no quizzes, flashcards, exercises, "
        f"or assessments anywhere, remove it"
        for name in found
    ]


def split_sections(text: str) -> list[tuple[str, str]]:
    """Every '## ' heading with its body, in order."""
    parts = re.split(r"^## (.*)$", text, flags=re.MULTILINE)
    return list(zip(parts[1::2], parts[2::2]))


def quoted(lines: list[str]) -> str:
    return "\n".join(f"        {line}" for line in lines) if lines else "        (nothing)"


def without_trailing_blanks(lines: list[str]) -> list[str]:
    out = list(lines)
    while out and not out[-1].strip():
        out.pop()
    return out


# ------------------------------------------------- the four code rules (tool.md)
#
# These are the checker's own copies, used only to verify the fixtures tell the story tool.md
# describes. They are not grader.py, which the model writes later and which teaches the same four
# rules to the learner. The two do not have to be identical implementations; they only have to
# agree about run 5, and tool.md:17 deliberately wants a few poems where a rule and a person do
# not agree, so a crude rule here is correct rather than a shortcoming.

# "here" alone is not a lead-in; poems open with it. It only counts followed by is / 's / you go.
LEAD_IN = re.compile(
    r"^(sure|here is|here's|here you (go|are)|of course|certainly|okay|ok|alright)\b",
    re.IGNORECASE,
)
DEDICATION = re.compile(r"^(for|to)\s+\w+[.,]?$", re.IGNORECASE)


def poem_lines(poem: str) -> list[str]:
    return [line.strip() for line in poem.splitlines() if line.strip()]


def rule_shape(situation: str, poem: str) -> bool:
    """Exactly 4 non-empty lines."""
    return len(poem_lines(poem)) == 4


def rule_line_length(situation: str, poem: str) -> bool:
    """Every line is under 12 words."""
    return all(len(line.split()) < 12 for line in poem_lines(poem))


def rule_no_preamble(situation: str, poem: str) -> bool:
    """No title line and no lead-in before the poem."""
    lines = poem_lines(poem)
    if not lines:
        return False
    first = lines[0]
    return not (first.endswith(":") or LEAD_IN.match(first) or DEDICATION.match(first))


def rule_no_copy(situation: str, poem: str) -> bool:
    """No sentence from the situation appears verbatim in the poem."""
    flat = " ".join(poem.split()).lower()
    for sentence in re.split(r"(?<=[.!?])\s+", situation.strip()):
        cleaned = " ".join(sentence.split()).lower().strip(" .!?,;:")
        if len(cleaned.split()) >= 4 and cleaned in flat:
            return False
    return True


CODE_RULES = {
    "shape": rule_shape,
    "line_length": rule_line_length,
    "no_preamble": rule_no_preamble,
    "no_copy": rule_no_copy,
}


# ------------------------------------------------------------------- examples

RUN1_FAILURE_BUDGET = 2   # tool.md:52, "nearly everything passes"
MIN_DISAGREEMENTS = 2     # tool.md:17, "two or three poems"
MAX_DISAGREEMENTS = 5     # more than this means a rule here is wrong, not the fixtures


def check_examples(replay: bool = False) -> list[str]:
    failures: list[str] = []

    runs: dict[int, list] = {}
    for n in range(1, config.SAVED_RUNS + 1):
        path = config.RUNS_DIR / f"run{n}.json"
        if not path.exists():
            failures.append(f"run {n} is missing; write exactly {config.SAVED_RUNS} runs")
            continue
        try:
            runs[n] = json.loads(path.read_text())
        except json.JSONDecodeError as error:
            failures.append(f"run {n} is not valid JSON: {error}")

    if len(runs) != config.SAVED_RUNS:
        return failures

    for n, run_data in runs.items():
        if not isinstance(run_data, list) or len(run_data) != config.OUTPUTS_PER_RUN:
            size = len(run_data) if isinstance(run_data, list) else "not a list"
            failures.append(f"run {n} holds {size} outputs, write exactly {config.OUTPUTS_PER_RUN}")
            continue
        for i, output in enumerate(run_data):
            for key in ("situation", "poem"):
                value = output.get(key) if isinstance(output, dict) else None
                if not isinstance(value, str) or not value.strip():
                    failures.append(f"run {n}, output {i} has no {key}; every output needs both")

    if failures:
        return failures

    # The same 20 situations, in the same order, in every run.
    baseline = [output["situation"] for output in runs[1]]
    for n in range(2, config.SAVED_RUNS + 1):
        theirs = [output["situation"] for output in runs[n]]
        for i, (want, got) in enumerate(zip(baseline, theirs)):
            if want != got:
                failures.append(
                    f"run {n}, output {i} has a different situation from run 1; the same "
                    f"{config.OUTPUTS_PER_RUN} situations must appear in the same order in every run. "
                    f"run 1 has {want!r}, run {n} has {got!r}"
                )
                break

    labels, label_failures = read_labels()
    failures += label_failures
    if label_failures:
        return failures

    failures += check_degradation(runs, labels)

    # The judge is the expensive check, so it only runs once everything cheaper has passed.
    if not failures and not replay:
        failures += judge_disagreement(runs[config.LABELED_RUN], labels)
    return failures


def read_labels() -> tuple[list[dict], list[str]]:
    path = config.LABELS_FILE
    expected = ["output"] + config.CODE_RULES + config.JUDGE_CRITERIA

    if not path.exists():
        return [], [f"{path.name} is missing"]

    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames or []
        rows = list(reader)

    if columns != expected:
        return [], [f"{path.name} has the columns {columns}, it needs exactly {expected} in that order"]

    failures = []
    if len(rows) != config.OUTPUTS_PER_RUN:
        failures.append(
            f"{path.name} has {len(rows)} rows, it needs one per output of run "
            f"{config.LABELED_RUN}, so exactly {config.OUTPUTS_PER_RUN}"
        )

    for i, row in enumerate(rows):
        if row["output"] != str(i):
            failures.append(f"{path.name} row {i} has output {row['output']!r}, rows run 0 to {config.OUTPUTS_PER_RUN - 1} in order")
        for column in expected[1:]:
            if row[column] not in ("pass", "fail"):
                failures.append(f"{path.name} row {i} has {column}={row[column]!r}; every label is the string pass or fail")

    return rows, failures


def check_degradation(runs: dict[int, list], labels: list[dict]) -> list[str]:
    """The code-rule half of tool.md's degradation story. The judge-criteria half is not
    checkable here; see this module's docstring."""
    failures = []

    counts = {}
    for n, run_data in runs.items():
        counts[n] = {name: 0 for name in CODE_RULES}
        for output in run_data:
            for name, rule in CODE_RULES.items():
                if not rule(output["situation"], output["poem"]):
                    counts[n][name] += 1

    totals = {n: sum(counts[n].values()) for n in counts}
    newest = config.SAVED_RUNS

    if totals[1] > RUN1_FAILURE_BUDGET:
        failures.append(
            f"run 1 breaks a code rule {totals[1]} times ({describe(counts[1])}); it is the clean "
            f"baseline, so fix those poems until it breaks at most {RUN1_FAILURE_BUDGET}"
        )

    for n in range(2, config.SAVED_RUNS + 1):
        if totals[n] < totals[n - 1]:
            failures.append(
                f"run {n} breaks code rules {totals[n]} times but run {n - 1} breaks them "
                f"{totals[n - 1]} times; every run is worse than the one before it, never better"
            )

    for name in ("no_preamble", "shape"):
        if counts[newest][name] <= counts[1][name]:
            failures.append(
                f"{name} fails {counts[newest][name]} times in run {newest} and "
                f"{counts[1][name]} times in run 1; run {newest} is the model swap where preambles "
                f"appear and line counts break, so {name} has to be plainly worse there"
            )

    disagreements = []
    for i, row in enumerate(labels):
        output = runs[newest][i]
        for name, rule in CODE_RULES.items():
            verdict = "pass" if rule(output["situation"], output["poem"]) else "fail"
            if verdict != row[name]:
                disagreements.append(f"output {i} ({name}: the rule says {verdict}, the label says {row[name]})")

    if len(disagreements) < MIN_DISAGREEMENTS:
        failures.append(
            f"only {len(disagreements)} output of run {newest} has a code rule disagreeing with its "
            f"human label; checkpoint 2 needs at least {MIN_DISAGREEMENTS}, such as a dedication line "
            f"a person reads as part of the poem, or a line of exactly twelve words"
        )
    elif len(disagreements) > MAX_DISAGREEMENTS:
        failures.append(
            f"{len(disagreements)} code-rule verdicts disagree with the human labels in run {newest}, "
            f"which is more than the two or three tool.md asks for: {', '.join(disagreements)}"
        )

    return failures


def describe(counts: dict[str, int]) -> str:
    return ", ".join(f"{name} {n}" for name, n in counts.items() if n)


# --------------------------------------------------- the judge on the labeled run

MIN_JUDGE_DISAGREEMENTS = 2   # tool.md, "a few false positives and a few false negatives"
MAX_JUDGE_DISAGREEMENTS = 5   # more than this and the judge is not "right most of the time"

# The pass conditions from tool.md's judge-criteria table, word for word. Build-along 2 builds
# its judge prompt from the same table, so the judge this check runs is the judge the capstone
# runs. If tool.md's wording changes, change it here too.
PASS_CONDITIONS = {
    "specific": "The poem names at least one concrete detail from the situation, not just a generic feeling.",
    "mood": "The poem's mood fits the situation; no cheerful poem for a loss, no mournful poem for good news.",
    "no_advice": "The poem does not tell the person what to do.",
}


def judge_prompt(situation: str, poem: str, criterion: str) -> str:
    return (
        "Grade one poem against one criterion.\n"
        f"Criterion: {criterion}\n"
        f"Pass condition: {PASS_CONDITIONS[criterion]}\n"
        "Judge this criterion only. Ignore everything else about the poem.\n"
        "\n"
        f"Situation: {situation}\n"
        "\n"
        f"Poem:\n{poem}\n"
        "\n"
        "Answer in exactly this shape and nothing else:\n"
        "VERDICT: PASS\n"
        "REASON: <one sentence>\n"
        "Write FAIL in place of PASS when the pass condition is not met."
    )


def judge_disagreement(labeled_run: list[dict], labels: list[dict]) -> list[str]:
    """The judge check on the fixtures. Runs the judge on every judge-criteria cell of the labeled
    run and requires it to disagree with the labels a few times, in both directions. Otherwise the
    capstone's disagreement lists print 'none' and checkpoints 5 and 6 teach nothing."""
    import anthropic

    cells = len(labeled_run) * len(config.JUDGE_CRITERIA)
    print(f"  asking the judge about run {config.LABELED_RUN} ({cells} calls to {config.JUDGE_MODEL})")
    client = anthropic.Anthropic()

    verdicts: list[tuple[int, str, str, str, str]] = []   # output, criterion, judge, label, reason
    unreadable: list[str] = []
    for i, output in enumerate(labeled_run):
        for criterion in config.JUDGE_CRITERIA:
            # Same model, same token cap, same single user message as build-along 2's judge.
            message = client.messages.create(
                model=config.JUDGE_MODEL,
                max_tokens=2000,
                messages=[{"role": "user", "content": judge_prompt(output["situation"], output["poem"], criterion)}],
            )
            if message.stop_reason == "refusal":
                unreadable.append(f"output {i} {criterion} (the judge refused: {message.stop_details})")
                continue
            reply = "".join(block.text for block in message.content if block.type == "text")
            verdict = VERDICT_LINE.search(reply)
            reason = REASON_LINE.search(reply)
            if not verdict or not reason:
                unreadable.append(f"output {i} {criterion} (it said: {reply.strip()[:120]!r})")
                continue
            verdicts.append((i, criterion, verdict.group(1), labels[i][criterion].upper(), reason.group(1)))

    failures: list[str] = []
    if unreadable:
        failures.append(
            f"the judge did not answer in the VERDICT and REASON shape on {len(unreadable)} cells, so "
            f"those could not be scored: {'; '.join(unreadable)}"
        )

    false_positives = [v for v in verdicts if v[2] == "FAIL" and v[3] == "PASS"]
    false_negatives = [v for v in verdicts if v[2] == "PASS" and v[3] == "FAIL"]
    total = len(false_positives) + len(false_negatives)
    summary = (
        f"the judge ({config.JUDGE_MODEL}) disagrees with the human labels on {total} of {cells} "
        f"judge-criteria cells in run {config.LABELED_RUN}: {len(false_positives)} false positives "
        f"(judge FAIL, label pass) and {len(false_negatives)} false negatives (judge PASS, label fail)"
    )

    if total < MIN_JUDGE_DISAGREEMENTS or not false_positives or not false_negatives:
        failures.append(
            f"{summary}. tool.md needs a few of each, between {MIN_JUDGE_DISAGREEMENTS} and "
            f"{MAX_JUDGE_DISAGREEMENTS} in total with at least one in each direction, so that checkpoints 5 "
            f"and 6 have something to show. Fix this by making some of run {config.LABELED_RUN}'s poems "
            f"harder to judge, never by moving a label: every label stays the strict reading of tool.md "
            f"against the poem as written. A false positive needs a poem that passes on a strict reading "
            f"but looks like a failure at a glance (a detail from the situation named only obliquely, a "
            f"fitting mood that is understated or sardonic, a hopeful wish that is not an instruction). A "
            f"false negative needs a poem that fails on a strict reading but looks fine at a glance (a "
            f"concrete detail that is not actually from the situation, a mood that turns wrong only in "
            f"its last line, advice softened into a question or a 'perhaps'). Here is every verdict the "
            f"judge gave, with its reason, so you can see what it catches and what it lets through:\n"
            + "\n".join(
                f"    output {i}  {criterion}  judge {judge}  label {label}  {reason}"
                for i, criterion, judge, label, reason in verdicts
            )
        )
    elif total > MAX_JUDGE_DISAGREEMENTS:
        failures.append(
            f"{summary}, which is more than the {MAX_JUDGE_DISAGREEMENTS} that still leaves the judge "
            f"right most of the time. Make a few of the borderline poems plainer, keeping the labels the "
            f"strict reading of tool.md: "
            + "; ".join(
                f"output {i} {criterion} (judge {judge}, label {label}: {reason})"
                for i, criterion, judge, label, reason in false_positives + false_negatives
            )
        )

    return failures


# ------------------------------------------------------------------- sections

CITATION = re.compile(r"run (\d+), output (\d+)")


def check_sections(lesson: int, replay: bool) -> list[str]:
    path = config.scratch_for(lesson) / "sections.md"
    if not path.exists():
        return [f"{path.name} was not written"]

    text = path.read_text()
    failures: list[str] = []
    lines = text.splitlines()

    titles = [i for i, line in enumerate(lines) if re.match(r"^# ", line)]
    first_filled = next((i for i, line in enumerate(lines) if line.strip()), None)
    if len(titles) != 1:
        failures.append(f"there are {len(titles)} lines starting with '# '; the lesson needs exactly one title line")
    elif titles[0] != first_filled:
        failures.append(f"the '# ' title is on line {titles[0] + 1}; it has to be the first line of the file")

    sections = split_sections(text)
    if len(sections) != config.SECTIONS_PER_LESSON:
        failures.append(
            f"the lesson has {len(sections)} '## ' sections, write exactly {config.SECTIONS_PER_LESSON}"
        )

    for marker, message in (
        (r"^#{3,} ", "a '###' or deeper heading"),
        (r"^-{3,}\s*$", "a '---' line"),
        (r"<svg", "an SVG block"),
        (r"^\*\*Step\b", "a bold line starting with Step"),
    ):
        hits = [i + 1 for i, line in enumerate(lines) if re.search(marker, line)]
        if hits:
            failures.append(
                f"line {hits[0]} has {message}; the sections hold none of those. "
                f"diagrams and the build-along are added by later stages"
            )

    for n, (heading, body) in enumerate(sections, start=1):
        count = word_count(body)
        if count < config.SECTION_MIN_WORDS:
            failures.append(f"section {n} ({heading.strip()}) is {count} words, bring it up over {config.SECTION_MIN_WORDS}")
        elif count > config.SECTION_MAX_WORDS:
            failures.append(f"section {n} ({heading.strip()}) is {count} words, cut it to under {config.SECTION_MAX_WORDS}")

    failures += banned_blocks(text, "the lesson")

    for match in CITATION.finditer(text):
        run_n, output_i = int(match.group(1)), int(match.group(2))
        if not 1 <= run_n <= config.SAVED_RUNS:
            failures.append(f"the lesson cites {match.group(0)}, but the runs are numbered 1 to {config.SAVED_RUNS}")
        elif not 0 <= output_i < config.OUTPUTS_PER_RUN:
            failures.append(
                f"the lesson cites {match.group(0)}, but a run's outputs are numbered 0 to "
                f"{config.OUTPUTS_PER_RUN - 1}"
            )

    if not replay:
        failures += terminology_judge(text)
        if lesson == 2:
            earlier = config.scratch_for(1) / "sections.md"
            if earlier.exists():
                failures += prereq_judge(earlier.read_text(), text)

    return failures


VERDICT_LINE = re.compile(r"^VERDICT:\s*(PASS|FAIL)\s*$", re.MULTILINE)
REASON_LINE = re.compile(r"^REASON:\s*(\S.*?)\s*$", re.MULTILINE)


def prereq_judge(lesson_one: str, lesson_two: str) -> list[str]:
    """The one judge check. Asks whether lesson 2 leans on anything lesson 1 never taught."""
    import anthropic

    prompt = (config.PROMPTS_DIR / "prereq_judge.md").read_text()
    question = (
        f"{prompt}\n\n"
        f"===== lesson 1 sections (what has already been taught) =====\n{lesson_one.strip()}\n\n"
        f"===== lesson 2 sections (the draft you are judging) =====\n{lesson_two.strip()}\n"
    )

    print("  asking the prerequisite judge")
    client = anthropic.Anthropic()
    message = client.messages.create(
        model=config.PIPELINE_MODEL,
        max_tokens=8000,
        messages=[{"role": "user", "content": question}],
        output_config={"effort": config.EFFORT},
    )

    if message.stop_reason == "refusal":
        return [f"the prerequisite judge refused: {message.stop_details}"]

    reply = "".join(block.text for block in message.content if block.type == "text")
    verdict = VERDICT_LINE.search(reply)
    reason = REASON_LINE.search(reply)

    if not verdict or not reason:
        return [
            "the prerequisite judge did not answer in the VERDICT and REASON shape, so its verdict "
            f"could not be read. it said: {reply.strip()[:300]}"
        ]

    if verdict.group(1) == "FAIL":
        return [f"lesson 2 uses something lesson 1 never taught: {reason.group(1)}"]
    return []


def ask_judge_prompt(name: str, question: str, opening: str) -> tuple[str, str] | list[str]:
    """Send one of the prose judges and read its VERDICT and REASON. Returns the pair on a clean
    answer, or a list of failure messages when the model refused or answered off-shape."""
    import anthropic

    print(f"  asking the {name}")
    client = anthropic.Anthropic()
    message = client.messages.create(
        model=config.PIPELINE_MODEL,
        max_tokens=8000,
        messages=[{"role": "user", "content": question}],
        output_config={"effort": config.EFFORT},
    )

    if message.stop_reason == "refusal":
        return [f"the {name} refused: {message.stop_details}"]

    reply = "".join(block.text for block in message.content if block.type == "text")
    verdict = VERDICT_LINE.search(reply)
    reason = REASON_LINE.search(reply)
    if not verdict or not reason:
        return [
            f"the {name} did not answer in the VERDICT and REASON shape, so its verdict could not "
            f"be read. it said: {reply.strip()[:300]}"
        ]
    return verdict.group(1), reason.group(1)


def terminology_judge(sections: str) -> list[str]:
    """The terminology check. Asks whether every technical term in the lesson is the industry's.
    The approved list lives in the sections prompt, so it is sent rather than copied here, and the
    two can never drift apart."""
    prompt = (config.PROMPTS_DIR / "terminology_judge.md").read_text()
    approved = (config.PROMPTS_DIR / "sections.md").read_text()
    question = (
        f"{prompt}\n\n"
        f"===== the approved term list (from the prompt the sections were written against) =====\n"
        f"{approved.strip()}\n\n"
        f"===== the lesson you are judging =====\n{sections.strip()}\n"
    )

    answer = ask_judge_prompt("terminology judge", question, "")
    if isinstance(answer, list):
        return answer
    verdict, reason = answer
    if verdict == "FAIL":
        return [f"the lesson uses a term that is not the industry's: {reason}"]
    return []


# ------------------------------------------------------------------- diagrams

SVG_NAMESPACE = "{http://www.w3.org/2000/svg}"
ALLOWED_TAGS = {"svg", "rect", "circle", "line", "path", "text"}
ALLOWED_COLOURS = {
    "#2e7d32", "#c62828", "#000", "#000000", "black", "#fff", "#ffffff", "white", "none",
}
FORBIDDEN_SVG = ("<script", "<style", "<image", "<filter", "gradient", "foreignobject")


def check_diagrams(lesson: int, written: list[Path]) -> list[str]:
    failures: list[str] = []
    out_dir = config.scratch_for(lesson) / "diagrams"
    expected = {f"section{n}.md" for n in range(1, config.SECTIONS_PER_LESSON + 1)}
    actual = {path.name for path in written}

    for extra in sorted(actual - expected):
        failures.append(
            f"there is a block for {extra.removesuffix('.md')}, but the lesson has sections 1 to "
            f"{config.SECTIONS_PER_LESSON}; return one block per section, SECTION: 1 through "
            f"SECTION: {config.SECTIONS_PER_LESSON}"
        )

    for n in range(1, config.SECTIONS_PER_LESSON + 1):
        path = out_dir / f"section{n}.md"
        if not path.exists():
            failures.append(f"section {n} has no diagram; every section gets exactly one")
            continue
        failures += check_one_diagram(n, path.read_text())

    return failures


def check_one_diagram(n: int, text: str) -> list[str]:
    failures = []
    closing = text.lower().rfind("</svg>")
    if closing == -1:
        return [f"the diagram for section {n} has no closing </svg> tag"]

    svg_text = text[: closing + len("</svg>")]
    after = text[closing + len("</svg>"):]

    lowered = svg_text.lower()
    for banned in FORBIDDEN_SVG:
        if banned in lowered:
            failures.append(
                f"the diagram for section {n} uses {banned.strip('<')}; diagrams use only rect, "
                f"circle, line, path, and text, with every attribute set inline"
            )

    try:
        root = ElementTree.fromstring(svg_text)
    except ElementTree.ParseError as error:
        return failures + [
            f"the diagram for section {n} is not well-formed XML ({error}); close every tag, quote "
            f"every attribute, and write & as &amp; inside text"
        ]

    height = None
    view_box = root.get("viewBox", "")
    match = re.fullmatch(r"0 0 800 (\d+)", view_box.strip())
    if not match:
        failures.append(
            f'the diagram for section {n} has viewBox="{view_box}"; it must be "0 0 800 H" with H '
            f"the height, so every diagram in the lesson lines up"
        )
    else:
        height = int(match.group(1))
        if not 200 <= height <= 500:
            failures.append(f"the diagram for section {n} is {height} units tall; keep the height between 200 and 500")

    if root.get("width") != "100%":
        failures.append(f'the diagram for section {n} has width="{root.get("width")}"; it must be width="100%"')

    children = list(root)
    if not children or strip_namespace(children[0].tag) != "rect":
        failures.append(
            f"the first element inside the diagram for section {n} is not a rect; it must be the "
            f"white background rectangle covering the whole viewBox"
        )
    elif height is not None:
        background = children[0]
        covers = (
            background.get("x", "0") in ("0", "0.0")
            and background.get("y", "0") in ("0", "0.0")
            and background.get("width") in ("800", "100%")
            and background.get("height") in (str(height), "100%")
        )
        if not covers:
            failures.append(
                f"the background rect in the diagram for section {n} does not cover the whole "
                f'viewBox; it needs x="0" y="0" width="800" height="{height}"'
            )

    for element in root.iter():
        tag = strip_namespace(element.tag)
        if tag not in ALLOWED_TAGS:
            failures.append(
                f"the diagram for section {n} uses <{tag}>; only rect, circle, line, path, and text are allowed"
            )
        for attribute in ("fill", "stroke"):
            value = element.get(attribute)
            if value is not None and value.strip().lower() not in ALLOWED_COLOURS:
                failures.append(
                    f'the diagram for section {n} uses {attribute}="{value}"; the only colours are '
                    f"black, white, green #2e7d32 for PASS, and red #c62828 for FAIL"
                )

    caption_lines = after.splitlines()
    if not caption_lines or caption_lines[0].strip():
        failures.append(f"the caption for section {n} must sit on its own line directly under </svg>")
    else:
        body = [line for line in caption_lines[1:] if line.strip()]
        if not body:
            failures.append(f"the diagram for section {n} has no caption; every diagram gets one plain sentence under it")
        elif len(body) > 1:
            failures.append(f"the caption for section {n} runs to {len(body)} lines; it is one plain sentence")
        elif body[0].lstrip()[:1] in ("#", "*", "-", ">", "`", "_"):
            failures.append(f"the caption for section {n} starts with Markdown formatting; it is a plain sentence")

    return failures


def strip_namespace(tag: str) -> str:
    return tag.removeprefix(SVG_NAMESPACE)


# ----------------------------------------------------------------- buildalong

STEP_LINE = re.compile(r"^\*\*Step (\d+):.*\*\*\s*$", re.MULTILINE)
FENCE = re.compile(r"^```(\w*)[ \t]*\n(.*?)^```[ \t]*$", re.DOTALL | re.MULTILINE)
NON_DETERMINISM = re.compile(r"\b(random|datetime|uuid)\b|\btime\.\w+|os\.environ|os\.getcwd|getenv")
JUDGE_MARKER = "(judge-dependent; filled in from the live run)"


def outside_fences(text: str) -> str:
    """The text with every fenced block blanked, line count unchanged, so a prose check never
    sees code or printed output. A '# comment' inside a python fence is not a heading."""
    return FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def check_buildalong(lesson: int) -> list[str]:
    path = config.scratch_for(lesson) / "buildalong.md"
    if not path.exists():
        return [f"{path.name} was not written"]

    text = path.read_text()
    failures: list[str] = []

    prose = outside_fences(text)
    headings = [i + 1 for i, line in enumerate(prose.splitlines()) if re.match(r"^#{1,6} ", line)]
    if headings:
        failures.append(f"line {headings[0]} is a Markdown heading; the build-along uses bold Step lines, not headings")

    failures += banned_blocks(text, "the build-along")

    steps, step_failures = split_steps(text)
    failures += step_failures
    if not steps:
        return failures

    code = "\n\n".join(step["python"] for step in steps)
    try:
        ast.parse(code)
    except SyntaxError as error:
        failures.append(f"the build-along's code does not parse: line {error.lineno}, {error.msg}")
        return failures

    drift = NON_DETERMINISM.search(code)
    if drift:
        failures.append(
            f"the code uses {drift.group(0)!r}, so two runs can print different bytes; the "
            f"build-along must print the same output on every machine, every run"
        )

    if lesson == 2:
        first = steps[0]["python"].strip().splitlines()
        opening = next((line for line in first if line.strip()), "")
        if not opening.startswith("from build.grader.grader import"):
            failures.append(
                f"step 1 opens with {opening!r}; lesson 2's first line imports lesson 1's grader, "
                f"'from build.grader.grader import ...', so the two build-alongs compound"
            )

    failures += run_steps(lesson, steps)
    return failures


def split_steps(text: str) -> tuple[list[dict], list[str]]:
    matches = list(STEP_LINE.finditer(text))
    failures = []

    if not matches:
        return [], ["the build-along has no '**Step 1: ...**' lines"]
    if len(matches) > config.MAX_STEPS:
        failures.append(f"the build-along has {len(matches)} steps; {config.MAX_STEPS} is the most it may have")

    steps = []
    for i, match in enumerate(matches):
        number = int(match.group(1))
        if number != i + 1:
            failures.append(f"the step after step {i} is numbered {number}; steps count 1, 2, 3 with no gaps")
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[match.end():end]

        blocks = [(m.group(1), m.group(2)) for m in FENCE.finditer(body)]
        tags = [tag for tag, _ in blocks]
        if tags != ["python", "text"]:
            failures.append(
                f"step {number} has the code blocks {tags}; every step has exactly one python "
                f"block then one text block, in that order"
            )
            continue

        printed = blocks[1][1]
        if not printed.strip():
            failures.append(f"step {number}'s text block is empty; it shows exactly what the terminal prints")
            continue

        steps.append({"n": number, "python": blocks[0][1], "text": printed})

    return steps, failures


def run_steps(lesson: int, steps: list[dict]) -> list[str]:
    """Run the file as it stands after each step and compare what it printed against the block
    that says what that step prints."""
    if not config.FIXTURES_DIR.exists():
        return ["the fixtures are missing; run the examples stage before the build-along"]

    module = "build.grader.grader" if lesson == 1 else "build.judge.judge"
    relative = Path("build/grader/grader.py") if lesson == 1 else Path("build/judge/judge.py")
    run_argument = f"build/fixtures/runs/run{config.LABELED_RUN}.json"

    failures: list[str] = []
    printed_so_far: list[str] = []

    for index, step in enumerate(steps):
        number = step["n"]
        expected = step["text"].splitlines()

        if expected and expected[0].strip() == JUDGE_MARKER:
            # Everything from here needs judge replies that are recorded in the live run, so these
            # steps cannot be run yet. The marker is the contract; the real output arrives later.
            for later in steps[index:]:
                first = later["text"].splitlines()[:1]
                if not first or first[0].strip() != JUDGE_MARKER:
                    failures.append(
                        f"step {later['n']} comes after the judge starts answering, so its output "
                        f"cannot be known until the live run; make its text block begin with the "
                        f"line {JUDGE_MARKER}"
                    )
            return failures

        source = "\n\n".join(earlier["python"] for earlier in steps[: index + 1])

        with tempfile.TemporaryDirectory() as workspace:
            root = Path(workspace)
            shutil.copytree(config.BUILD_DIR, root / "build")
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source + "\n")

            try:
                finished = subprocess.run(
                    [sys.executable, "-m", module, run_argument],
                    cwd=root,
                    capture_output=True,
                    text=True,
                    timeout=config.STEP_TIMEOUT_SECONDS,
                )
            except subprocess.TimeoutExpired:
                return failures + [
                    f"step {number} did not finish within {config.STEP_TIMEOUT_SECONDS} seconds; "
                    f"the build-along reads fixtures and prints, it never waits on anything"
                ]

        if finished.returncode != 0:
            tail = finished.stderr.strip().splitlines()[-6:]
            return failures + [
                f"the file does not run after step {number}. every step has to leave the file "
                f"working from the top. it failed with:\n{quoted(tail)}"
            ]

        actual = finished.stdout.splitlines()
        if actual[: len(printed_so_far)] != printed_so_far:
            return failures + [
                f"step {number} changed what an earlier step printed. a step only adds lines, it "
                f"never changes or removes one from an earlier step"
            ]

        added = without_trailing_blanks(actual[len(printed_so_far):])
        if added != without_trailing_blanks(expected):
            failures.append(
                f"step {number} prints something different from its text block.\n"
                f"    it really printed:\n{quoted(added)}\n"
                f"    its text block says:\n{quoted(without_trailing_blanks(expected))}\n"
                f"    decide which one is wrong. if the code did what the step meant, fix the text "
                f"block. if the code is wrong, fix the code and work out the text block again."
            )

        printed_so_far = actual

    return failures
