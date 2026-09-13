"""The orchestration. One command per stage, typed from baer-buster:

    python -m agent.run examples
    python -m agent.run sections 1
    python -m agent.run diagrams 1
    python -m agent.run buildalong 1
    python -m agent.run assemble 1

Lesson 2 has two more stages, neither of which calls the course-writing model:

    python -m agent.run live 2      the reference runs: both build-alongs on every saved run,
                                    oldest first, the judge live, so every raw reply is recorded
                                    under build/judge/responses/, each history CSV gets its rows,
                                    and both are copied to their seeds before the labeled run
    python -m agent.run reference   both build-alongs run offline from a fresh copy of their
                                    seeds, everything they print saved under output/ (step 24)
    python -m agent.run verify      run them offline again and confirm they print what output/
                                    says they printed, history table aside (step 25)
    python -m agent.run fill 1      run build-along 1 step by step from the seeded state and make
    python -m agent.run fill 2      every text block what really printed (lesson 2 from the
                                    recordings), then assemble that lesson (plan step 22b)

Or every stage in order, examples first, then each lesson from sections to assemble:

    python -m agent.run all

It stops at the first stage that still fails after its retries, so what is already written
stays. To pick the run up from that stage, name it with --from (with its lesson number, except
for examples), and every earlier stage is skipped:

    python -m agent.run all --from buildalong 1

Add --replay to reuse the saved raw reply instead of calling the model (for testing the
pipeline itself). The loop for every model stage is:

    build the prompt from the design files plus only the context this stage is allowed to see
    call the model, save the raw reply
    split the reply into files
    run the checks; if any fail, send the failures back and let the model rewrite
    stop after MAX_RETRIES

See pipeline.md for why it is shaped this way.
"""

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import anthropic

from agent import checks, config

MODEL_STAGES = ("examples", "sections", "diagrams", "buildalong")
STAGES = MODEL_STAGES + ("assemble", "live", "fill", "reference", "verify")

# The order `all` runs in. Examples first because every later stage reads the fixtures, and
# lesson 1 in full before lesson 2 because lesson 2's stages read lesson 1's finished output.
# After the live stage has made the recordings and the seeds, both build-alongs are filled with
# what they really print from that state, then assembled.
ALL_STEPS = [
    ("examples", None),
    ("sections", 1), ("diagrams", 1), ("buildalong", 1),
    ("sections", 2), ("diagrams", 2), ("buildalong", 2),
    ("live", 2),
    ("fill", 1), ("assemble", 1),
    ("fill", 2), ("assemble", 2),
    ("reference", None),
]


# ---------------------------------------------------------------- entry point

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("stage", choices=STAGES + ("all",))
    parser.add_argument("lesson", nargs="?", type=int, help="1 or 2 (not used by examples or all)")
    parser.add_argument("--replay", action="store_true", help="reuse the saved raw reply instead of calling the model")
    parser.add_argument("--from", dest="start", choices=STAGES, metavar="STAGE",
                        help="with all: skip every stage before this one (give its lesson number as the lesson argument)")
    args = parser.parse_args()

    if args.stage == "all":
        if args.start is None:
            if args.lesson is not None:
                sys.exit("all takes no lesson number unless --from names a stage")
            run_all(args.replay)
            return
        first = (args.start, args.lesson)
        if first not in ALL_STEPS:
            options = ", ".join(stage + (f" {lesson}" if lesson else "") for stage, lesson in ALL_STEPS)
            sys.exit(f"--from {args.start}" + (f" {args.lesson}" if args.lesson is not None else "")
                     + f" is not a stage all runs; it is one of: {options}")
        run_all(args.replay, first)
        return

    if args.start is not None:
        sys.exit("--from only goes with all")

    if args.stage in ("examples", "reference", "verify") and args.lesson is not None:
        sys.exit(f"{args.stage} takes no lesson number; it covers every build-along")
    if args.stage not in ("examples", "reference", "verify") and args.lesson not in range(1, config.LESSONS + 1):
        sys.exit(f"{args.stage} needs a lesson number from 1 to {config.LESSONS}")
    if args.stage == "live" and args.lesson != 2:
        sys.exit("live is a lesson 2 stage; lesson 1 has no judge")

    run_stage(args.stage, args.lesson, args.replay)


def run_stage(stage: str, lesson: int | None, replay: bool) -> None:
    if stage == "assemble":
        assemble(lesson)
    elif stage == "live":
        live(lesson, replay)
    elif stage == "fill":
        fill(lesson)
    elif stage == "reference":
        reference()
    elif stage == "verify":
        verify()
    else:
        generate(stage, lesson, replay)


def run_all(replay: bool, first: tuple[str, int | None] = ALL_STEPS[0]) -> None:
    """Every stage in ALL_STEPS order, starting at `first`. A failed stage exits from inside
    generate(), so the run stops there with everything earlier already on disk."""
    steps = ALL_STEPS[ALL_STEPS.index(first):]
    skipped = len(ALL_STEPS) - len(steps)
    if skipped:
        print(f"skipping the first {skipped} of {len(ALL_STEPS)} stages, already on disk")
    for n, (stage, lesson) in enumerate(steps, start=skipped + 1):
        print(f"===== {n}/{len(ALL_STEPS)}: {stage}" + (f" {lesson}" if lesson else "") + " =====")
        run_stage(stage, lesson, replay)
        print()
    print(f"{len(steps)} of {len(ALL_STEPS)} stages done")


# ---------------------------------------------------------- the main loop

def generate(stage: str, lesson: int | None, replay: bool) -> None:
    raw_path = raw_file(stage, lesson)
    print(f"stage: {stage}" + (f" lesson {lesson}" if lesson else ""))
    print(f"mode: {'replay' if replay else 'model'}")

    if replay and not raw_path.exists():
        sys.exit(f"no saved reply at {raw_path.relative_to(config.ROOT)}; run once without --replay")

    system = design_context()
    messages = [{"role": "user", "content": stage_prompt(stage, lesson)}]

    for attempt in range(1, config.MAX_RETRIES + 1):
        if replay:
            reply = raw_path.read_text()
        else:
            reply = call_model(system, messages)
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            raw_path.write_text(reply)

        written = SPLITTERS[stage](reply, lesson)
        failures = checks.run(stage, lesson, written, replay)

        print(f"attempt {attempt}/{config.MAX_RETRIES}: {len(failures)} check failures")
        for failure in failures:
            print(f"  - {failure}")

        if not failures:
            for path in written:
                print(f"wrote {path.relative_to(config.ROOT)}")
            return

        if replay:
            sys.exit("replay cannot rewrite; fix the checks or run without --replay")

        # Feed the failures back and let the model rewrite the whole stage.
        messages.append({"role": "assistant", "content": reply})
        messages.append({"role": "user", "content": feedback_message(failures)})

    sys.exit(f"gave up after {config.MAX_RETRIES} attempts; the failures above are still open")


def feedback_message(failures: list[str]) -> str:
    lines = "\n".join(f"- {f}" for f in failures)
    return (
        "Your last reply failed these checks:\n"
        f"{lines}\n\n"
        "Return the complete corrected reply in the same format. "
        "Do not explain the changes and do not return only the changed part."
    )


# ------------------------------------------------------------ the model call

def call_model(system: str, messages: list[dict]) -> str:
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
    with client.messages.stream(
        model=config.PIPELINE_MODEL,
        max_tokens=config.MAX_OUTPUT_TOKENS,
        # The design files never change between calls, so they go first and get cached.
        system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
        messages=messages,
        thinking={"type": "adaptive"},
        output_config={"effort": config.EFFORT},
    ) as stream:
        message = stream.get_final_message()

    if message.stop_reason == "refusal":
        sys.exit(f"the model refused: {message.stop_details}")
    if message.stop_reason == "max_tokens":
        sys.exit(f"the reply hit the {config.MAX_OUTPUT_TOKENS} token cap; raise MAX_OUTPUT_TOKENS in config")

    usage = message.usage
    print(f"  tokens: in {usage.input_tokens}, cached {usage.cache_read_input_tokens}, out {usage.output_tokens}")

    text = "".join(block.text for block in message.content if block.type == "text")
    return strip_outer_fence(text)


def strip_outer_fence(text: str) -> str:
    """Models sometimes wrap the whole reply in one ``` fence. Remove it if so."""
    text = text.strip()
    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()
        return "\n".join(lines[1:-1]).strip() + "\n"
    return text + "\n"


# ------------------------------------------------- what the model gets to see

def design_context() -> str:
    """Every design file, in config order, with a header naming each. Same bytes every call."""
    parts = []
    for path in config.DESIGN_FILES:
        parts.append(f"===== {path.name} =====\n{path.read_text().strip()}\n")
    return "\n".join(parts)


def stage_prompt(stage: str, lesson: int | None) -> str:
    """The stage's prompt file, followed by only the context this stage is allowed to see.

    Prerequisite order by construction: a lesson 1 stage never sees lesson 2, and lesson 2's
    stages see lesson 1's finished output so they build on what was actually taught.
    """
    prompt_path = config.PROMPTS_DIR / f"{stage}.md"
    if not prompt_path.exists():
        sys.exit(f"missing prompt file {prompt_path.relative_to(config.ROOT)}")

    parts = [prompt_path.read_text().strip()]
    if lesson:
        parts.append(f"===== this run =====\nLesson number: {lesson}")

    for label, path in context_files(stage, lesson):
        if not path.exists():
            sys.exit(f"{stage} needs {path.relative_to(config.ROOT)} but it does not exist yet")
        parts.append(f"===== {label} =====\n{path.read_text().strip()}")

    return "\n\n".join(parts) + "\n"


def context_files(stage: str, lesson: int | None) -> list[tuple[str, Path]]:
    """Which earlier outputs each stage may read. Order is what the model sees."""
    if stage == "examples":
        return []

    here = config.scratch_for(lesson)
    files: list[tuple[str, Path]] = []

    if stage == "sections":
        for n in range(1, config.SAVED_RUNS + 1):
            files.append((f"fixture run {n}", config.RUNS_DIR / f"run{n}.json"))
        files.append(("fixture labels", config.LABELS_FILE))
        if lesson == 2:
            files.append(("lesson 1 sections (what has already been taught)", config.scratch_for(1) / "sections.md"))

    elif stage == "diagrams":
        files.append((f"lesson {lesson} sections", here / "sections.md"))

    elif stage == "buildalong":
        files.append((f"lesson {lesson} sections", here / "sections.md"))
        for n in range(1, config.SAVED_RUNS + 1):
            files.append((f"fixture run {n}", config.RUNS_DIR / f"run{n}.json"))
        files.append(("fixture labels", config.LABELS_FILE))
        if lesson == 2:
            files.append(("lesson 1 sections (what has already been taught)", config.scratch_for(1) / "sections.md"))
            files.append(("lesson 1 build-along text", config.scratch_for(1) / "buildalong.md"))
            files.append(("lesson 1 grader.py (import from this, never copy it)", config.GRADER_DIR / "grader.py"))

    return files


# ---------------------------------------------- turning a reply into files

def raw_file(stage: str, lesson: int | None) -> Path:
    if stage == "examples":
        return config.SCRATCH_DIR / "raw" / "examples.txt"
    return config.scratch_for(lesson) / "raw" / f"{stage}.txt"


def split_examples(reply: str, lesson: int | None) -> list[Path]:
    """Reply is one JSON object:
        {"runs": [[{"situation": ..., "poem": ...} x OUTPUTS_PER_RUN] x SAVED_RUNS],
         "labels": [{"output": i, <criterion>: "pass"|"fail", ...} x OUTPUTS_PER_RUN]}
    Writes one JSON file per run and one labels CSV.
    """
    data = json.loads(reply)
    config.RUNS_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    changed = False

    for n, run in enumerate(data["runs"], start=1):
        path = config.RUNS_DIR / f"run{n}.json"
        changed |= write_if_different(path, json.dumps(run, indent=2, ensure_ascii=False) + "\n")
        written.append(path)

    columns = ["output"] + config.CODE_RULES + config.JUDGE_CRITERIA
    rows = [",".join(str(label[column]) for column in columns) for label in data["labels"]]
    changed |= write_if_different(config.LABELS_FILE, "\r\n".join([",".join(columns)] + rows) + "\r\n")
    written.append(config.LABELS_FILE)

    if changed:
        clear_derived_from_fixtures()
    return written


def write_if_different(path: Path, content: str) -> bool:
    """Write the file only if its bytes would change. Returns whether they did."""
    if path.exists():
        with path.open(newline="") as handle:
            if handle.read() == content:
                return False
    with path.open("w", newline="") as handle:
        handle.write(content)
    return True


DERIVED_FROM_FIXTURES = ("history.csv", "history.seed.csv")


def clear_derived_from_fixtures(why: str = "fixtures changed") -> None:
    """New fixtures make everything computed from the old ones wrong: the recorded judge replies
    are about poems that no longer exist, and every history row was counted on them. Remove them
    so a stale file can never be replayed or copied into a table by mistake."""
    removed = []
    for folder in (config.GRADER_DIR, config.JUDGE_DIR):
        for name in DERIVED_FROM_FIXTURES:
            path = folder / name
            if path.exists():
                path.unlink()
                removed.append(path)
    for path in sorted(config.JUDGE_RESPONSES_DIR.glob("*.txt")):
        path.unlink()
        removed.append(path)
    replies = sum(1 for p in removed if p.suffix == ".txt")
    tables = [str(p.relative_to(config.ROOT)) for p in removed if p.suffix == ".csv"]
    print(f"{why}: cleared {replies} recorded judge replies" + (", " + ", ".join(tables) if tables else ""))


def split_sections(reply: str, lesson: int | None) -> list[Path]:
    """Reply is the lesson title line and the five ## sections, per lesson_format.md. Saved as is."""
    path = config.scratch_for(lesson) / "sections.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(reply)
    return [path]


DIAGRAM_BLOCK = re.compile(r"^SECTION:\s*(\d+)\s*$", re.MULTILINE)


def split_diagrams(reply: str, lesson: int | None) -> list[Path]:
    """Reply is one or more blocks, each:
        SECTION: <n>
        <svg ...>...</svg>
        optional one-line caption
    Each block is saved as diagrams/section<n>.md and assemble appends it to that section.
    """
    out_dir = config.scratch_for(lesson) / "diagrams"
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []

    pieces = DIAGRAM_BLOCK.split(reply)  # ['', n, block, n, block, ...]
    for n, block in zip(pieces[1::2], pieces[2::2]):
        path = out_dir / f"section{n}.md"
        path.write_text(block.strip() + "\n")
        written.append(path)
    return written


PYTHON_FENCE = re.compile(r"```python\n(.*?)```", re.DOTALL)


def split_buildalong(reply: str, lesson: int | None) -> list[Path]:
    """Reply is the build-along text per lesson_format.md. Saved as is, and every python fence
    is concatenated in order into the one file the learner ends up holding.
    """
    text_path = config.scratch_for(lesson) / "buildalong.md"
    text_path.parent.mkdir(parents=True, exist_ok=True)
    text_path.write_text(reply)

    code_path = config.GRADER_DIR / "grader.py" if lesson == 1 else config.JUDGE_DIR / "judge.py"
    code_path.parent.mkdir(parents=True, exist_ok=True)
    code = "\n\n".join(fence.strip() for fence in PYTHON_FENCE.findall(reply))
    code_path.write_text(code + "\n")

    return [text_path, code_path]


SPLITTERS = {
    "examples": split_examples,
    "sections": split_sections,
    "diagrams": split_diagrams,
    "buildalong": split_buildalong,
}


# ------------------------------------------------- the live run and the fill (22b)

def buildalong_command(lesson: int, run_n: int, live_mode: bool = False) -> list[str]:
    module = "build.grader.grader" if lesson == 1 else "build.judge.judge"
    command = [sys.executable, "-m", module, f"build/fixtures/runs/run{run_n}.json"]
    if live_mode:
        command.append("--live")
    return command


def run_buildalong(lesson: int, run_n: int, live_mode: bool = False) -> None:
    """Run a finished build-along on one saved run from the real build/ directory, the way the
    reviewer will. Exits with the traceback's tail if it fails."""
    name = "grader" if lesson == 1 else "judge, live" if live_mode else "judge"
    print(f"{name}, run{run_n}")
    finished = subprocess.run(buildalong_command(lesson, run_n, live_mode), cwd=config.ROOT, capture_output=True, text=True)
    if finished.returncode != 0:
        tail = finished.stderr.strip().splitlines()[-8:]
        sys.exit(f"build-along {lesson} failed on run{run_n}:\n" + "\n".join("    " + line for line in tail))


def live(lesson: int, replay: bool) -> None:
    """Plan steps 22 and 23. The reference runs, from the real build/ directory, the way the
    reviewer will run them: for each saved run, oldest first, build-along 1 grades it and then
    build-along 2 judges it live, so every raw reply lands under build/judge/responses/ and each
    build-along appends its own row to its own history CSV. Before the labeled run, both history
    files are copied to their seeds. Starts from a clean slate, so the recordings, the rows, and
    the seeds always come from the same pass. No course-writing model is called."""
    if lesson != 2:
        sys.exit("live is a lesson 2 stage; lesson 1 has no judge")
    if replay:
        print("skipped: --replay makes no model calls, and live is nothing but model calls")
        return
    for lesson_n, name in ((1, "grader.py"), (2, "judge.py")):
        folder = config.GRADER_DIR if lesson_n == 1 else config.JUDGE_DIR
        if not (folder / name).exists():
            sys.exit(f"{(folder / name).relative_to(config.ROOT)} does not exist yet; run buildalong {lesson_n} first")

    clear_derived_from_fixtures("starting clean")
    for run_n in range(1, config.SAVED_RUNS + 1):
        if run_n == config.LABELED_RUN:
            # Plan step 23. The history files as they stand now, rows for every earlier run and
            # none for the labeled one, are the seeds: the state the reviewer's first run starts
            # from, so their run appends the same row the reference run is about to append.
            for folder in (config.GRADER_DIR, config.JUDGE_DIR):
                shutil.copyfile(folder / "history.csv", folder / "history.seed.csv")
                print(f"seed saved: {(folder / 'history.seed.csv').relative_to(config.ROOT)}")
        run_buildalong(1, run_n)
        run_buildalong(2, run_n, live_mode=True)
    replies = sorted(config.JUDGE_RESPONSES_DIR.glob("*.txt"))
    print(f"{len(replies)} replies recorded under {config.JUDGE_RESPONSES_DIR.relative_to(config.ROOT)}")


def fill(lesson: int) -> None:
    """Plan step 22b. Runs the build-along's file as it stands after each step, in replay mode
    from a scratch copy of build/ as the live stage left it, exactly as the build-along check
    does, and takes what each step added to the output. Every text block is replaced with those
    real lines, the judge-dependent marker dropped where there was one. The marked blocks were
    guesses. The unmarked ones were traced before the history files and seeds existed, so their
    tables are shorter than what the reviewer, starting from the seeds, will see. Then the lesson
    is assembled again. Nothing is typed by a person: the text becomes what the program printed."""
    path = config.scratch_for(lesson) / "buildalong.md"
    if not path.exists():
        sys.exit(f"{path.relative_to(config.ROOT)} does not exist yet; run buildalong {lesson} first")

    text = path.read_text()
    steps, failures = checks.split_steps(text)
    if failures:
        sys.exit("the build-along is not in the step shape:\n" + "\n".join("  - " + f for f in failures))

    marked = [step["n"] for step in steps if step["text"].splitlines()[:1] == [checks.JUDGE_MARKER]]
    if not (config.GRADER_DIR / "history.seed.csv").exists():
        sys.exit("no history seed under build/grader/; run live 2 first, the fill traces from the seeded state")
    if lesson == 2 and not any(config.JUDGE_RESPONSES_DIR.glob("*.txt")):
        sys.exit("no recorded judge replies under build/judge/responses/; run live 2 first")

    added_by_step = printed_by_step(lesson, steps)

    # Replace from the last step backwards so earlier character offsets stay valid.
    matches = list(checks.STEP_LINE.finditer(text))
    for i in reversed(range(len(matches))):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body_start = matches[i].end()
        fences = list(checks.FENCE.finditer(text, body_start, end))
        text_fence = fences[1]  # split_steps already proved: one python fence, then one text fence
        real = "\n".join(added_by_step[i]) + "\n"
        text = text[: text_fence.start(2)] + real + text[text_fence.end(2):]
        was = "was a judge-dependent guess" if steps[i]["n"] in marked else "was traced before the seeds existed"
        print(f"step {steps[i]['n']}: now {len(added_by_step[i])} printed lines ({was})")

    path.write_text(text)
    print(f"wrote {path.relative_to(config.ROOT)} ({len(steps)} blocks filled, {len(marked)} of them judge-dependent)")
    assemble(lesson)


def printed_by_step(lesson: int, steps: list[dict]) -> list[list[str]]:
    """What each step adds to the output, by running the file as it stands after that step.
    Same scratch copy of build/, same command, same cumulative comparison as the check."""
    module = "build.grader.grader" if lesson == 1 else "build.judge.judge"
    relative = Path("build/grader/grader.py") if lesson == 1 else Path("build/judge/judge.py")
    run_argument = f"build/fixtures/runs/run{config.LABELED_RUN}.json"

    added_by_step: list[list[str]] = []
    printed_so_far: list[str] = []
    for index in range(len(steps)):
        source = "\n\n".join(step["python"] for step in steps[: index + 1])
        with tempfile.TemporaryDirectory() as workspace:
            root = Path(workspace)
            shutil.copytree(config.BUILD_DIR, root / "build")
            (root / relative).write_text(source + "\n")
            finished = subprocess.run(
                [sys.executable, "-m", module, run_argument],
                cwd=root, capture_output=True, text=True, timeout=config.STEP_TIMEOUT_SECONDS,
            )
        if finished.returncode != 0:
            tail = finished.stderr.strip().splitlines()[-8:]
            sys.exit(f"the file does not run after step {steps[index]['n']}:\n" + "\n".join("    " + l for l in tail))
        actual = finished.stdout.splitlines()
        if actual[: len(printed_so_far)] != printed_so_far:
            sys.exit(f"step {steps[index]['n']} changed what an earlier step printed; the fill cannot be trusted")
        added_by_step.append(checks.without_trailing_blanks(actual[len(printed_so_far):]))
        printed_so_far = actual
    return added_by_step


def reference() -> None:
    """Plan step 24. The reference run: put each history CSV back to a fresh copy of its seed,
    then run each build-along offline on the labeled run, the way the reviewer will, and save
    everything it printed under output/. The API key is stripped from the environment first, so
    a run that needed one would fail here rather than quietly pass. These files are the yardstick
    step 25 checks a replay against and step 34 checks the unzipped copy against."""
    for lesson_n, folder, name in ((1, config.GRADER_DIR, "grader.py"), (2, config.JUDGE_DIR, "judge.py")):
        if not (folder / name).exists():
            sys.exit(f"{(folder / name).relative_to(config.ROOT)} does not exist yet; run buildalong {lesson_n} first")
        seed = folder / "history.seed.csv"
        if not seed.exists():
            sys.exit(f"{seed.relative_to(config.ROOT)} does not exist yet; run live 2 first, it writes the seeds")

    # Both seeds go back before either build-along runs: build-along 2 reads lesson 1's history,
    # so it has to see the same starting state the reviewer's copy will be in.
    for folder in (config.GRADER_DIR, config.JUDGE_DIR):
        shutil.copyfile(folder / "history.seed.csv", folder / "history.csv")
        print(f"history restored from seed: {(folder / 'history.csv').relative_to(config.ROOT)}")

    offline = {key: value for key, value in os.environ.items() if key != "ANTHROPIC_API_KEY"}
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for lesson_n in range(1, config.LESSONS + 1):
        finished = subprocess.run(
            buildalong_command(lesson_n, config.LABELED_RUN),
            cwd=config.ROOT, capture_output=True, text=True, env=offline,
        )
        if finished.returncode != 0:
            tail = finished.stderr.strip().splitlines()[-8:]
            sys.exit(f"build-along {lesson_n} failed offline on run{config.LABELED_RUN}:\n"
                     + "\n".join("    " + line for line in tail))
        path = config.OUTPUT_DIR / f"buildalong{lesson_n}.txt"
        path.write_text(finished.stdout)
        print(f"wrote {path.relative_to(config.ROOT)} ({len(finished.stdout.splitlines())} lines)")


# A history table line: the header "run   shape  ..." and each row "run1  0  ...". Plus the line
# that counts the rows. These are the log, which grows by one row per run and is not held fixed.
HISTORY_TABLE_LINE = re.compile(r"^run\d*\s{2,}")
HISTORY_COUNT_LINE = re.compile(r"^runs in history: \d+$")


def without_history_table(lines: list[str]) -> list[str]:
    return [l for l in lines if not HISTORY_TABLE_LINE.match(l) and not HISTORY_COUNT_LINE.match(l)]


def verify() -> None:
    """Plan step 25. Runs each build-along offline again and compares what it prints against the
    reference output saved under output/. The judge's verdicts, its two disagreement lists, and
    its precision and recall all have to come out identical. The history table is left out of the
    comparison: it is a log that grows by one row per run, not a fixed artifact. The full text is
    compared too, and reported separately, because in practice it should also match."""
    offline = {key: value for key, value in os.environ.items() if key != "ANTHROPIC_API_KEY"}
    failures = []
    for lesson_n in range(1, config.LESSONS + 1):
        saved_path = config.OUTPUT_DIR / f"buildalong{lesson_n}.txt"
        if not saved_path.exists():
            sys.exit(f"{saved_path.relative_to(config.ROOT)} does not exist yet; run the reference stage first")

        finished = subprocess.run(
            buildalong_command(lesson_n, config.LABELED_RUN),
            cwd=config.ROOT, capture_output=True, text=True, env=offline,
        )
        if finished.returncode != 0:
            tail = finished.stderr.strip().splitlines()[-8:]
            failures.append(f"build-along {lesson_n} did not run offline:\n" + "\n".join("    " + l for l in tail))
            continue

        saved = saved_path.read_text().splitlines()
        now = finished.stdout.splitlines()
        whole = "same" if now == saved else "DIFFERENT"
        apart = "same" if without_history_table(now) == without_history_table(saved) else "DIFFERENT"
        print(f"build-along {lesson_n}: everything but the history table is {apart}; the whole output is {whole}")

        if without_history_table(now) != without_history_table(saved):
            import difflib
            diff = list(difflib.unified_diff(
                without_history_table(saved), without_history_table(now),
                str(saved_path.relative_to(config.ROOT)), "this run", lineterm="",
            ))
            failures.append(f"build-along {lesson_n} printed something different from the reference run:\n"
                            + "\n".join("    " + l for l in diff[:40]))

    if failures:
        sys.exit("\n".join(failures))
    print("replay matches the reference output")


# ------------------------------------------------------------------ assemble

SECTION_HEADING = re.compile(r"^## ", re.MULTILINE)


def assemble(lesson: int) -> None:
    """No model. Glue sections, diagrams, and build-along text into course/lessonN.md."""
    here = config.scratch_for(lesson)
    sections_text = (here / "sections.md").read_text()
    buildalong_text = (here / "buildalong.md").read_text()

    title, *rest = sections_text.split("\n", 1)
    bodies = SECTION_HEADING.split(rest[0] if rest else "")[1:]  # drop text before the first ##

    parts = [title.strip(), ""]
    for n, body in enumerate(bodies, start=1):
        parts.append("## " + body.strip())
        diagram = here / "diagrams" / f"section{n}.md"
        if diagram.exists():
            parts.append("")
            parts.append(diagram.read_text().strip())
        parts.append("")

    parts += ["---", "", buildalong_text.strip(), ""]

    out = config.course_file(lesson)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(parts))
    print(f"wrote {out.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
