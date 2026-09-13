# Pipeline

Topic: Evals and LLM-as-Judge
Learner: someone who shipped an AI feature and cannot tell if it is getting worse
Capstone: a working grader printing real precision and recall

This file fixes how the course is generated: the stages, the commands, where things land, which models are used, and how raw replies are kept. It is the design for plan step 10. Plan step 11 adds the checks.

## Stages

One command per stage. Each stage is one job for the model, except assemble, which calls no model.

| Stage | Plan step | What the model does | Where it lands |
|---|---|---|---|
| examples | 12 | Invents the fake tool's outputs, one file per saved run, and the human pass/fail labels. When the fixtures change, everything computed from the old ones is cleared: the recorded judge replies and both history CSVs with their seeds | `build/fixtures/` |
| sections | 13, 17 | Writes one lesson's sections, exactly 5, 300 to 500 words each | `scratch/lessonN/sections.md` |
| diagrams | 14, 18 | Draws the SVG diagrams for that lesson's sections | `scratch/lessonN/diagrams/sectionN.md`, one per diagram |
| buildalong | 15, 19 | Writes that lesson's build-along steps, the code, and what each step prints | text to `scratch/lessonN/buildalong.md`, code to `build/grader/` or `build/judge/` |
| assemble | 21 | No model. Glues sections, diagrams, and build-along text into one file per lesson_format.md | `course/lessonN.md` |
| live | 22, 23 | Lesson 2 only. No course-writing model. The reference runs: starting clean, for every saved run oldest first, build-along 1 grades it and build-along 2 judges it live, recording every raw reply, each build-along appending its own row to its own history CSV. Before the labeled run it copies each history CSV to its seed, the state the reviewer's first run starts from | `build/judge/responses/`, `build/grader/history.csv` and `history.seed.csv`, `build/judge/history.csv` and `history.seed.csv` |
| fill | 22b | No model. Runs one lesson's build-along step by step from the seeded history files (lesson 2 also replaying the recorded judge replies) and makes every text block what that step really printed: the judge-dependent guesses in lesson 2, and in both lessons the tables traced before the seeds existed. Then assembles that lesson again | `scratch/lessonN/buildalong.md`, `course/lessonN.md` |

## Commands

Every command is typed from baer-buster.

```
python -m agent.run examples
python -m agent.run sections 1
python -m agent.run diagrams 1
python -m agent.run buildalong 1
python -m agent.run assemble 1
```

Lesson 2 uses the same commands with 2.

Two more stages come after both build-alongs: `live 2` records the judge, then `fill 1` and `fill 2` replace each build-along's text blocks with what the code really printed and assemble again. Running `buildalong N --replay` re-splits the raw reply and so restores the unfilled blocks; `fill N` puts them back.

One command runs every stage in order, examples first, then lesson 1 from sections to assemble, then lesson 2 through live and fill:

```
python -m agent.run all
```

It stops at the first stage that still fails after its retries. Everything earlier is already on disk, so the run is picked up again from that stage, either with the single-stage command or by naming the stage:

```
python -m agent.run all --from buildalong 1
```

## Folders

- `agent/` holds only what the email names: the orchestration code, the prompts, and the config. Nothing generated lands here.
- `scratch/` holds each stage's raw model reply under `raw/` and the pieces the splitter made of it, which assemble glues into `course/`. It ships in the zip so the reviewer can see what the model actually returned. The pieces match their raw replies byte for byte, except the build-along text blocks, which the fill stage replaced with what the code really printed.
- `course/`, `build/`, and `build/fixtures/` hold only finished, shipped files.

## Inputs every stage reads

breaking_points.md, checkpoints.md, capstone_spec.md, lesson_format.md, build_layout.md, record_replay.md. The prompt for each stage tells the model which of these it must follow.

## Models

- The pipeline, which writes the course: Claude Opus 5, model ID `claude-opus-5`.
- The judge inside build-along 2: Claude Sonnet 5, model ID `claude-sonnet-5`. Cheaper, and the build-along can say a real project would put a judge on a cheaper model.

Both are set in the config file, never in the prompts or the code.

## Raw replies

Every model reply is saved raw before the pipeline touches it, at `scratch/lessonN/raw/<stage>.txt` (the examples stage at `scratch/raw/examples.txt`).

By default a stage calls the model and overwrites the saved reply, on every attempt, so the file holds the last reply, the one that passed its checks. `--replay` on the command reads the saved reply instead of calling the model.

Why: `--replay` is for testing the pipeline itself. The same reply goes through the splitter and the checks again, so a fix to them can be judged on its own without a new draft. Real runs never use it.

## Prompts

One Markdown file per stage in `agent/prompts/`, read by the orchestration code at run time. The reviewer reads them as they are.

## Config

One file, `agent/config.py`, holding the model IDs, word limits, section count (5), retry limit (3), and paths. Nothing else in agent/ hardcodes any of those.

## Orchestration in run.py

run.py is the file the reviewer reads to judge how the model was worked with. It is one plain loop with the retries visible. No frameworks, no planner agent, no agents talking to each other. The stages are fixed above; run.py does not decide them.

Five things it does, in order of how much they earn:

1. **Generate, check, feed back.** The model writes a stage. The checks from plan step 11 run on the result. Every failure goes back to the model as a specific message, such as "section 3 is 612 words, cut it to under 500," and the model rewrites. Up to a fixed number of tries from config, then the stage stops and prints what still fails. This is what makes the word counts, the marker rules, and the no-quiz rule actually hold.

2. **Run the generated code.** For the buildalong stage, run.py executes the generated grader step by step and compares what each step actually printed against the text fence the model claimed it would print. A mismatch goes back to the model like any other check failure. The build-along is proven to work before anyone follows it.

3. **Prerequisite order by construction.** Each stage is given only the inputs it is allowed to know. Lesson 2's sections get lesson 1's finished sections as context so the model can see what was taught. Lesson 1's stages never see anything from lesson 2. Prerequisite order is enforced by what goes into the prompt, not by hoping.

4. **A judge inside the pipeline.** Two checks are model calls. One asks "does this lesson 2 section use any concept that lesson 1's sections did not teach?" The other runs the course's own judge on the labeled run of the fixtures and requires it to disagree with the human labels a few times in each direction, so the capstone's false positive and false negative lists are never empty. The course teaches LLM-as-judge and the pipeline that wrote it uses one on itself. Each verdict goes back to the model like any other failure.

5. **Prompt caching.** The files every call reads unchanged (breaking_points, checkpoints, capstone_spec, lesson_format, build_layout, record_replay) go first in every request and are marked cacheable. The part that changes per stage goes last.
