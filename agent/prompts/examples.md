# Examples stage

## Content

You are building test data for a course that teaches people to grade an AI tool's outputs. You are not the tool. You are writing what the tool would have produced across five versions, and most of the flaws in the later versions are deliberate. Most deliberate flaws must be clean enough that a reader can name which rule or criterion in tool.md they break. The exception is the small set of borderline poems in run 5 described below; those are meant to be arguable, and they are the point.

The tool, its code rules, its judge criteria, its failure categories, and the degradation story are all in tool.md. Follow it exactly; nothing here overrides it.

The counts: 5 saved runs, 20 outputs in every run, the same 20 situations in every run, and every output of run 5 labeled on all 7 criteria.

The situations: 20 of them, one or two sentences each, written in the first person by someone describing a moment in their life. Spread the moods so no single one dominates: loss, joy, anxiety, boredom, anger, relief, and small everyday things all appear. Every situation carries at least one concrete detail, such as a name, an object, a place, or a number, so the specific criterion has something to catch. No real people.

How many poems fail in each run is your call. The shape of the story in tool.md is not: run 1 is nearly clean, each run is worse than the one before, and by run 5 the two criteria that have fallen the most are specific and no_preamble.

Run 5 also needs four to six poems that sit right on the edge of a judge criterion, so that a judge can reasonably get them wrong in either direction. After you reply, the course's own judge (a language model given tool.md's pass condition, the situation, and the poem) is run on every output of run 5 and its verdicts are compared to your labels. It has to disagree with your labels on two to five cells, with at least one disagreement in each direction, or the reply comes back to you with the judge's full verdict list. So both directions are needed:

- A false positive: a poem that passes on a strict reading of tool.md but looks like a failure at a glance. A detail from the situation named only obliquely, so the judge does not spot it. A mood that fits but is understated, or sardonic where the situation is anger. A hopeful wish such as "may your dark hours sit kindly down" that a hasty reader takes for advice.
- A false negative: a poem that fails on a strict reading but looks fine at a glance. A concrete-sounding detail that is not actually from the situation. A mood that fits until its closing line turns it wrong. Advice softened into a question or a "perhaps".

For these, the label follows the exact wording of the criterion in tool.md, read strictly against the poem as written. The labels are ground truth; they are never wrong on purpose, and they are never moved to create a disagreement. If the judge agrees with every label, the fix is harder poems, not different labels.

Run 5 also needs two or three poems where a code rule and a person disagree. A dedication line such as "for Sam" above the poem, which a person reads as part of the poem but the no_preamble rule flags. A line of exactly twelve words that reads short to a person but fails line_length. For these, the label is the person's judgment, not the rule's.

Every poem is original. No borrowed or famous lines.

## View

The tool's voice is a Romantic poet who ran with Lord Byron and John Keats, famous for color and sound. Rich hues, the ring and hush of things, feeling carried by the senses. That voice is the tool at its best, and it still writes in that voice when it is failing; the flaws are in what the poem does, not in who is speaking.

Each poem is one string, with newline characters between its lines, exactly as the tool would have returned it. Not a list of lines.

Outputs are numbered from 0, in the order they appear in the run, so the number is the poem's index in the run's list.

Return one JSON object and nothing else. No prose before or after it, no code fence around it. This exact shape:

```
{
  "runs": [
    [ {"situation": "...", "poem": "line\nline\nline\nline"}, ... 20 of these ],
    ... 5 runs, oldest first
  ],
  "labels": [
    {"output": 0, "shape": "pass", "line_length": "pass", "no_preamble": "pass", "no_copy": "pass",
     "specific": "pass", "mood": "pass", "no_advice": "pass"},
    ... 20 of these, one per output of run 5, in order
  ]
}
```

Every label value is the string "pass" or "fail". The same 20 situations appear in the same order in all 5 runs.

## Controller

Work in this order:

1. Write the 20 situations.
2. Write run 1, the clean baseline. Every poem should pass every rule and criterion, or very nearly.
3. Write runs 2, 3, 4, and 5 in turn, each degraded from the run before it according to the story in tool.md. A poem that was fine in the previous run can stay fine; a flaw introduced in one run tends to persist or worsen in the next.
4. Label run 5 last, by reading each finished poem against each rule and criterion in tool.md. Label what is on the page, not what you intended to write.

When you introduce a clean flaw on purpose, make it this way. The borderline poems in run 5 are the one exception to every "not subtle" line below; they are meant to be subtle.

- shape: five lines, or three, or a blank line inside the poem. Not a subtle one.
- line_length: one line that clearly runs long, fourteen words or more, unless it is one of the borderline exactly-twelve cases.
- no_preamble: a whole line before the poem, such as "Here is a poem for you:" or "Sure, here you go." Never a half-line folded into line one.
- no_copy: one full sentence from the situation dropped into the poem word for word.
- specific: the voice stays, but every concrete detail from the situation is gone. A poem that could have been written for any sad day, any good news.
- mood: the mood plainly wrong for the situation. Bright for a loss, mournful for good news. Not a subtle mismatch.
- no_advice: the poem tells the person what to do in a plain imperative, such as "Go call your mother" or "Let it go." A hopeful wish is not advice.

Before you return, check your own work:

- 5 runs, 20 poems in each, and the same 20 situations in the same order in every run.
- 20 label rows, output numbered 0 to 19, every value "pass" or "fail", all 7 criteria present in each row.
- Every label matches the poem as written. Reread the poem, not your plan for it.
- Run 5 has four to six judge-borderline poems, with at least one false positive and one false negative under a strict reading, and the rule-versus-person poems asked for.
- The JSON parses. No trailing commas, newlines inside poems written as \n.

When things conflict:

- The rules win over the voice. If a line in a poem meant to be clean runs past eleven words to sound right, cut it. The voice has to live inside the tool's spec.
- Run 1 is the clean baseline. If a run 1 poem breaks a rule by accident, fix the poem rather than labeling the accident.

If you receive a list of failures after your reply, return the complete corrected JSON object in the same shape. Keep everything that was not named in the failures. No explanation, no partial object. If the failures include the judge's verdict list, read where it agreed with you on the poems you meant to be borderline, and rewrite those poems in run 5 until a few are genuinely arguable; the labels stay the strict reading of whatever is now on the page.
