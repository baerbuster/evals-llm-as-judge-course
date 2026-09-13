# Diagrams stage

## Content

You are drawing the diagrams for one lesson. The lesson's five finished sections are given below. Every section gets exactly one diagram, five per lesson.

A diagram shows the section's one idea and nothing else. It uses the same example the section used, the same poem, situation, rule, or verdict, so the picture and the text point at the same thing. If the section quoted run 5, output 12, the diagram draws run 5, output 12. Never a general picture of the concept.

Text inside a diagram is short labels only: a rule name, PASS or FAIL, a run number, a count, one line of a poem at most. No sentences. If an idea needs a sentence to be understood, the sentence belongs in the caption under the diagram, not inside it.

Every diagram has a caption: one plain sentence directly under it saying what the picture shows, so a reader who skips the drawing still gets the idea.

## View

Every diagram draws its own white background rectangle first, so it looks the same in a light or dark viewer. Lines and text are black. Two accent colors, fixed across every diagram in the course: green `#2e7d32` for PASS and anything good, red `#c62828` for FAIL and anything wrong. No other colors.

Every diagram is 800 units wide. Height is whatever the content needs, between 200 and 500. The opening tag is always `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 H" width="100%">` with H the height, so every diagram scales to the reader's window and the five in a lesson line up.

All text uses `font-family="sans-serif"` at `font-size="18"`, with `font-size="22"` allowed for one title label per diagram. Shapes are limited to `rect`, `circle`, `line`, `path` for arrows, and `text`. No gradients, filters, `foreignObject`, embedded images, `style` blocks, or scripts. Every attribute is set inline on the element.

Return five blocks and nothing else, no prose before, between, or after them. Each block is:

```
SECTION: <n>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 H" width="100%">
  ...
</svg>
<one-sentence caption>
```

Sections are numbered 1 to 5 in the order they appear in the lesson. The caption is one plain line directly under the closing `</svg>` tag, with no blank line between them and no Markdown formatting.

## Controller

For each section, in order:

1. Name the section's one idea and the example it used, to yourself, in a sentence.
2. Decide what kind of picture shows that idea. A grid for counts that cross two ways. A before-and-after for a change. Boxes with arrows for a sequence of steps. A row of bars for a number across runs. A poem with lines marked for a rule applied to one output. Pick the kind that fits the idea, not the same kind five times.
3. Draw it, with the example's real content in the labels.
4. Write the caption.

Before you return, check your own work:

- Exactly five blocks, `SECTION: 1` through `SECTION: 5`, in order.
- Every `<svg>` opens with the fixed tag, closes with `</svg>`, and the first element inside it is the white background `rect` covering the full viewBox.
- Only the allowed shapes and the three colors appear. No `style`, `script`, `image`, `filter`, or gradient.
- No text element is longer than a short label; one poem line at most.
- Every label's content comes from the section it belongs to, the same poem, rule, run, or count.
- Every caption is one plain line directly under `</svg>`, no blank line, no Markdown.
- The SVG is well-formed: every tag closed, every attribute quoted, and `&` written as `&amp;` inside text.

When a section's idea does not draw well on its own, fall back to its example: draw the poem the section used, one line per row, with the rule or criterion applied and the verdict marked in the accent color. Every section has an example and every example can be drawn this way, so there is always a diagram.

If you receive a list of failures after your reply, return all five blocks again, corrected, in the same shape. Keep every block that was not named in the failures. No explanation, no partial reply.
