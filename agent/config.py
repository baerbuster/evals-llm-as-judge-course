"""Every number, name, and path the pipeline uses. Nothing else in agent/ hardcodes these.

The API key is read from the environment by the Anthropic SDK itself (ANTHROPIC_API_KEY).
Importing this module first loads baer-buster/.env into the environment, so a key kept there
counts as exported. It is never stored here or in any file that ships.
"""

from pathlib import Path

from dotenv import load_dotenv

# Models
PIPELINE_MODEL = "claude-opus-5"   # writes the course
JUDGE_MODEL = "claude-sonnet-5"    # the LLM-as-judge inside build-along 2

# Lesson shape (from the email and lesson_format.md)
LESSONS = 2
SECTIONS_PER_LESSON = 5
SECTION_MIN_WORDS = 300
SECTION_MAX_WORDS = 500

# Generate, check, feed back
MAX_RETRIES = 3
MAX_OUTPUT_TOKENS = 64000
EFFORT = "high"

# Build-along shape and how long one step's code may run before the check gives up
MAX_STEPS = 8
STEP_TIMEOUT_SECONDS = 60

# The criteria the fake tool is graded on (see tool.md). Column names in labels.csv and history CSVs.
CODE_RULES = ["shape", "line_length", "no_preamble", "no_copy"]
JUDGE_CRITERIA = ["specific", "mood", "no_advice"]

# Fixture data the examples stage invents (see tool.md)
SAVED_RUNS = 5
OUTPUTS_PER_RUN = 20
LABELED_RUN = 5  # the newest run; all of its outputs get human labels

# Paths, resolved from this file so every command works from baer-buster
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")  # no-op if the file is missing; never overrides a shell export
AGENT_DIR = ROOT / "agent"
PROMPTS_DIR = AGENT_DIR / "prompts"
SCRATCH_DIR = ROOT / "scratch"
COURSE_DIR = ROOT / "course"
OUTPUT_DIR = ROOT / "output"   # the reference run's saved output (plan step 24)
BUILD_DIR = ROOT / "build"
GRADER_DIR = BUILD_DIR / "grader"
JUDGE_DIR = BUILD_DIR / "judge"
JUDGE_RESPONSES_DIR = JUDGE_DIR / "responses"
FIXTURES_DIR = BUILD_DIR / "fixtures"
RUNS_DIR = FIXTURES_DIR / "runs"
LABELS_FILE = FIXTURES_DIR / "labels.csv"

# Design files every stage's prompt is built from, in the order they are sent
DESIGN_FILES = [
    AGENT_DIR / "breaking_points.md",
    AGENT_DIR / "checkpoints.md",
    AGENT_DIR / "capstone_spec.md",
    AGENT_DIR / "lesson_format.md",
    AGENT_DIR / "build_layout.md",
    AGENT_DIR / "record_replay.md",
    AGENT_DIR / "tool.md",
]


def scratch_for(lesson: int) -> Path:
    return SCRATCH_DIR / f"lesson{lesson}"


def course_file(lesson: int) -> Path:
    return COURSE_DIR / f"lesson{lesson}.md"


def check_run_file() -> Path:
    """The saved run the checks grade against. The labeled one, so the code rules meet the labels."""
    return RUNS_DIR / f"run{LABELED_RUN}.json"
