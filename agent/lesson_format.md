# Lesson File Format

Topic: Evals and LLM-as-Judge
Learner: someone who shipped an AI feature and cannot tell if it is getting worse
Capstone: a working grader printing real precision and recall

This file fixes the shape of every file in course/. The generator prompts emit exactly this shape, the pipeline checks parse it, and the assembly step concatenates by it. One file per lesson.

## File type

Markdown. Diagrams are inline SVG. No HTML diagrams, no Mermaid, no raster images.

## Markers

Four markers, and nothing else is structural.

| Marker | Meaning |
|---|---|
| `#` | Lesson title. Once, first line of the file. |
| `##` | Section. Exactly 5 per lesson. Everything until the next `##` or the `---` is that section's body. |
| `<svg> ... </svg>` | Diagram. Lives inside the section it belongs to. No heading, no marker of its own. An optional caption is a plain line of text directly under the closing tag. |
| `---` | End of sections, start of the build-along. Exactly once per file. Everything below it is the build-along. |

Rules the generator must obey:

- Never use `---` anywhere except as the one build-along separator.
- Never use `###` or deeper headings anywhere in the file.
- Never use a bold line starting with `Step` outside the build-along.

## Sections

- 300 to 500 words each, one idea each.
- Word count excludes any `<svg>` block and its caption line.
- The `##` heading text is the section name.

## Build-along

Below the `---`. It may open with a plain line of text as a title; that line is not a heading.

Each step is three things in this order:

1. A bold line: `**Step N: <what this step adds>**`, where N counts 1, 2, 3 with no gaps.
2. One fenced code block tagged `python`: the code the learner adds in this step.
3. One fenced code block tagged `text`: exactly what the terminal prints when they run it. Never empty.

Plain prose may sit between the bold line and the python block. Nothing else appears inside a step.

## What the checks verify

- Exactly one `#` line, and it is the first line.
- Exactly 5 `##` sections above the `---`.
- Each section's word count, with SVG blocks and captions removed, is between 300 and 500.
- Exactly one `---`.
- Below it, Step lines are numbered consecutively from 1.
- Each step has exactly one python fence and exactly one text fence, in that order, before the next Step line.
- No text fence is empty.
- No quiz, flashcard, or exercise block anywhere in the file.
