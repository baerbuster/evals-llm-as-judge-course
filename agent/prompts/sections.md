# Sections stage

## Content

You are writing the five sections of one lesson. The lesson number is given below. Lesson 1 teaches checkpoints 1 to 3 and lesson 2 teaches checkpoints 4 to 6, as assigned in checkpoints.md. Each section is one idea.

The five sections map onto the lesson's three checkpoints like this:

- Lesson 1: checkpoint 1 gets sections 1 and 2, checkpoint 2 gets section 3, checkpoint 3 gets sections 4 and 5.
- Lesson 2: checkpoint 4 gets section 1, checkpoint 5 gets sections 2 and 3, checkpoint 6 gets sections 4 and 5.

The checkpoint that gets one section is the mechanical one; the build-along carries the rest of it. The checkpoints that get two are the ones with a concept the learner has to hold before the code makes sense.

Each checkpoint came from a breaking point in breaking_points.md. Do not quote or narrate the breaking point in the sections. Treat it as the question the sections must answer: by the end of a checkpoint's sections, a learner who had that exact confusion no longer has it, because the teaching resolved it. The breaking point is your test for whether the section did its job, not its content.

Every example in every section uses the poem tool from tool.md. A rule is one of its four code rules. A criterion is one of its three judge criteria. A failure category is one of its six. When a section needs an output to point at, it is a four-line poem about a situation. The learner should never have to translate from an abstract example to the thing the build-along makes them build.

For lesson 2, the finished text of lesson 1's sections is given below. Two rules follow from it:

- Never re-teach. Anything lesson 1 explained is referred to by name, such as "the history table from lesson 1," and not explained again.
- Never lean on anything lesson 1 did not teach. If lesson 2 needs a concept, it is either in lesson 1's text or lesson 2 teaches it itself before using it.

Use the industry's terms, never your own. These are the terms the course uses, with the definition to give in plain words the first time each appears. Never coin a name for something that already has one below. If you need a term not listed, use the standard industry term for it.

Lesson 1 terms:

- eval: a repeatable way of measuring whether an AI tool's outputs are good, so the answer is the same no matter who runs it.
- output: one thing the tool produced for one input. Here, one poem for one situation.
- run: one batch of outputs from one version of the tool, saved to a file.
- rule (also code rule, deterministic check): a pass/fail check written in code, so it gives the same verdict every time.
- verdict: the pass or fail a rule or judge gives one output.
- human label (also label): the pass or fail a person gave an output by hand.
- ground truth: the human labels, treated as the correct answer that everything else is measured against.
- labeled set: the outputs that have human labels.
- agreement and disagreement: whether a rule's verdict matches the human label for the same output.
- pass rate: the share of outputs that passed, as a number between 0 and 1 or a percentage.
- failure category (also failure mode): a named bucket that a failing output is sorted into by what went wrong.
- error analysis: reading through failures and sorting them into failure categories to see what kind of problem is most common.
- regression: the tool getting worse than it used to be.
- trend: the direction a number moves across runs, oldest to newest.
- fixture: data shipped with the course so a run can be repeated exactly; here the saved runs and the labels.

Lesson 2 terms:

- qualitative criterion (also criterion): something an output should do that code cannot check, such as fitting the mood of the situation.
- LLM-as-judge (also judge): using a language model to give a pass/fail verdict on a qualitative criterion.
- judge prompt: the instructions given to the judge, including the criterion and the output to grade.
- structured output (also fixed format): making the judge answer in a fixed shape, such as a verdict line and a reason line, so code can parse it.
- parse: turning the judge's text reply into a verdict and a reason the code can use.
- positive class: the outcome being detected and counted. Here it is FAIL, because the judge is a defect detector.
- true positive: the judge said FAIL and the human said FAIL.
- false positive: the judge said FAIL and the human said PASS. The judge was too strict.
- false negative: the judge said PASS and the human said FAIL. The judge was too lenient.
- true negative: the judge said PASS and the human said PASS.
- confusion counts (also confusion matrix): the four counts above, laid out together.
- precision: of the outputs the judge failed, the share the human also failed. True positives divided by true positives plus false positives.
- recall: of the outputs the human failed, the share the judge caught. True positives divided by true positives plus false negatives.
- record and replay: saving the judge's raw replies during a live run so a later run can reuse them without calling the model.
- live mode and replay mode: whether the judge's replies come from the model or from the saved files.

## View

Talk to one person, in the second person. The learner shipped a tool and cannot tell if it is getting worse. Every sentence is addressed to them.

- **Say the idea as clearly as possible in the simplest words.** One idea per section. A poem is the example. If a sentence needs a second reading, rewrite it.
- **Say it positively.** Say what a good rule does before saying what intuition fails to do. Say what the learner can do, not what they cannot.
- **Remove false certainty.** A judge can miss problems, not will. A trend can mean the tool is worse, not proves. Say "can" and "often" where "will" and "always" are not true.
- **Remove what does not apply to every learner.** Do not assume a team, a budget, a big dataset, or prior knowledge beyond what the previous sections taught. The poem tool is the shared ground everyone stands on.
- **Give a reason to care.** Each idea comes with one sentence of why it matters to someone whose tool might be getting worse.
- **Name the growth.** The last sentences of a checkpoint's final section say plainly what the learner can now do that they could not before, in the words of that checkpoint in checkpoints.md.

The learner is becoming the person who can tell. Never send them to an authority for the answer; the section makes them the authority.

Pass and fail are judgments and the course is about making them explicit. Use them plainly.

Sentences are short. No jokes, no exclamation points, no cheerleading. Warmth comes from clarity and from taking the learner's problem seriously.

The shape is fixed by lesson_format.md: one `#` title line, then exactly five `##` sections, 300 to 500 words each. No `###` or deeper, no `---`, no bold lines starting with Step, no SVG. Diagrams and the build-along are added by later stages.

## Controller

Every section moves in this order:

1. Say the idea plainly, in a sentence or two.
2. Show it working on an example. The case where it works comes first. In lesson 1 that is a poem a rule passes; in lesson 2 it is a verdict the judge gets right.
3. Show why it matters with the failure. In lesson 1 that is a poem the rule fails; in lesson 2 it is a verdict the judge gets wrong. The error is the reason to care: this is what you would have missed, or what you can now catch.
4. Close on the checkpoint. If this is the last section of a checkpoint, say in that checkpoint's own words what the learner can now do. If it is the first of a pair, say what this section gave them and what the next one adds.

Every example poem and situation is taken word for word from the fixture runs given below. Never write a fresh poem. Name which run it came from, such as "run 5, output 12," so the learner can find it again in the build-along. Where a section needs a failing poem, pick one whose failure is the flaw being taught, and where it needs a passing one, pick one that passes cleanly.

In lesson 2 the judge does not exist yet, so any judge verdict in a section is an illustration. Write it as "suppose the judge says," never as a fact. The poem and the human label are real; the verdict is hypothetical.

Before you return, check your own work:

- One `#` title line, then exactly five `##` sections, and nothing else structural.
- Each section is between 300 and 500 words.
- Each section holds one idea and moves through the four steps above.
- Every example poem exists in the fixtures at the run and output you cited, word for word.
- Every term from the glossary is defined in plain words the first time it appears.
- For lesson 2: nothing is used that lesson 1's sections did not teach, and nothing lesson 1 taught is explained again.

When things conflict:

- The word cap wins. If the four moves want more than 500 words, tighten every move rather than dropping one.
- A glossary term is defined in the sentence where it first appears or in the next one, always within the same paragraph.

If you receive a list of failures after your reply, return the complete corrected lesson, all five sections, in the same shape. Keep everything that was not named in the failures. No explanation, no partial reply.
