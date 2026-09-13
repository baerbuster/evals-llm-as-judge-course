# Build Layout

Topic: Evals and LLM-as-Judge
Learner: someone who shipped an AI feature and cannot tell if it is getting worse
Capstone: a working grader printing real precision and recall

This file fixes where the build-along code lives, how it is run, and how build-along 2 uses build-along 1. The generator prompts for both build-alongs and the README follow it.

## Folders

One folder per build-along, named with words so Python can import them.

```
baer-buster/
  build/
    grader/              build-along 1 (lesson 1, checkpoints 1 to 3)
      grader.py          the one file the learner writes
      history.seed.csv   shipped seed, code-rule columns only, never run against in place
      history.csv        the grader appends one row per run; starts as a copy of the seed
    judge/               build-along 2 (lesson 2, checkpoints 4 to 6)
      judge.py           the one file the learner writes
      history.seed.csv   shipped seed, code-rule and judge columns, never run against in place
      history.csv        the judge appends one row per run; starts as a copy of the seed
      responses/         cached judge replies from the live run, read in replay mode
    fixtures/            data both build-alongs read and neither writes
      runs/              saved outputs of the tool, one file per run
      labels.csv         human pass/fail labels on a subset of outputs, per criterion
```

The learner writes exactly one file per build-along. Everything else is shipped data.

## Running

Every command is typed from baer-buster, never from inside a build folder. The README says so once.

```
python -m build.grader.grader <run file>
python -m build.judge.judge <run file>
```

No `__init__.py` files are needed. Python 3.12 imports the folders as they are.

All file paths inside the code are resolved from the running file's own location, never from the current directory, so the same command produces the same output on any machine.

## How build-along 2 uses build-along 1

judge.py imports from grader.py with one normal import line:

```
from build.grader.grader import ...
```

It imports the grader loop, the code rules, the failure categories, the label loader, and the history append/read/trend code. It never copies them and never edits grader.py.

grader.py is frozen the moment lesson 1 ends. Running build-along 1 again after finishing lesson 2 produces the same output it did before.

The first step of build-along 2 imports the grader, runs it on a saved run, and prints the same history table build-along 1 printed. That printed check is the proof the artifacts compound.
