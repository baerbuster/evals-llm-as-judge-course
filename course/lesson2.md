# Judging the Judge

## A judge grades what no rule can count

Some of what you want from a poem cannot be counted. Whether the poem is about this person's situation, and not about any situation, is one of those things. That is a qualitative criterion: something an output should do that code cannot check. To check it, you can use LLM-as-judge, which means asking a language model for a pass/fail verdict on that criterion. The judge drops into your grader where a rule goes. It takes one output and returns one verdict. The difference is that the check is a sentence you wrote, not a line of Python.

That sentence lives in the judge prompt: the instructions you hand the judge, holding the criterion and the poem to grade. The poem tool has three criteria. Specific: the poem names a concrete detail from the situation, not just a generic feeling. Mood: the poem's mood fits the situation, no cheerful poem for a loss. No advice: the poem does not tell the person what to do.

Here is specific, working. Run 5, output 4, for the situation about a landlord who kept a whole deposit over one scuff on the baseboard:

"A thumb of scuff, and there goes all the money, / how delicately he declines to lift the phone. / O admirable man, O flawless shining baseboard, / may his next tenants be exactly like himself."

The scuff, the baseboard, the phone he will not lift. Suppose the judge says PASS, its reason naming the scuff and the baseboard. You labeled it pass too, so nothing is in dispute.

Now the case no rule reaches. Run 5, output 0, for Rufus and the collar in the hall:

"Here is a poem for you: / The house has grown too large by one small absence, / and the quiet has a shape it did not have. / Something that made a sound makes none at all, / and every room is heavier for it."

Nothing in it names the dog, the collar, or the hall. Swap in any loss and the poem still fits. Suppose the judge says FAIL, reason: no detail from the situation appears. You labeled it fail. Four code rules ran over this poem in lesson 1, and none of them could see that.

For your code to use the reply, ask for structured output: a fixed shape, such as a verdict line and a reason line. Then parse it, turning the judge's text into a verdict and a reason you can store beside the rule verdicts. Save each raw reply as it arrives. That is record and replay: live mode calls the model, replay mode reads the saved files, so the same eval gives the same verdicts tomorrow without paying twice.

You can now write a judge prompt that returns a pass/fail verdict for a criterion no code rule can check. The judge is a model, so it can be wrong. The next two sections measure how often.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 350" width="100%">
  <rect x="0" y="0" width="800" height="350" fill="#ffffff"/>
  <text x="40" y="36" font-family="sans-serif" font-size="22" fill="#000000">run 5, output 0</text>
  <rect x="40" y="52" width="720" height="60" fill="#ffffff" stroke="#000000"/>
  <text x="56" y="90" font-family="sans-serif" font-size="18" fill="#000000">the quiet has a shape it did not have</text>
  <line x1="250" y1="112" x2="250" y2="166" stroke="#000000"/>
  <path d="M 250,178 L 244,164 L 256,164 Z" fill="#000000"/>
  <line x1="560" y1="112" x2="560" y2="166" stroke="#000000"/>
  <path d="M 560,178 L 554,164 L 566,164 Z" fill="#000000"/>
  <rect x="60" y="180" width="380" height="140" fill="#ffffff" stroke="#000000"/>
  <text x="80" y="212" font-family="sans-serif" font-size="18" fill="#000000">4 code rules</text>
  <text x="80" y="244" font-family="sans-serif" font-size="18" fill="#000000">shape, line_length,</text>
  <text x="80" y="270" font-family="sans-serif" font-size="18" fill="#000000">no_preamble, no_copy</text>
  <text x="80" y="303" font-family="sans-serif" font-size="18" fill="#000000">cannot check specific</text>
  <rect x="470" y="180" width="290" height="140" fill="#ffffff" stroke="#000000"/>
  <text x="490" y="212" font-family="sans-serif" font-size="18" fill="#000000">judge: specific</text>
  <text x="490" y="248" font-family="sans-serif" font-size="18" fill="#c62828">FAIL</text>
  <text x="490" y="284" font-family="sans-serif" font-size="18" fill="#000000">no detail from</text>
  <text x="490" y="308" font-family="sans-serif" font-size="18" fill="#000000">the situation</text>
</svg>
The four code rules from lesson 1 run over run 5, output 0 and none of them can see that the poem never names the dog, while the judge fails it on specific.

## Sort the judge's mistakes by direction

Measuring the judge uses the machinery you already built. Run it over the labeled set, and put its verdict next to your label for the same output and the same criterion. Counting agreements alone hides what you need, so split the results by direction instead. The judge exists to find bad poems, so FAIL is the positive class: the outcome being detected and counted. All four names follow from that.

A true positive is the judge saying FAIL where you said FAIL. Run 5, output 0 on specific is one: you failed it, and suppose the judge fails it. A true negative is both saying PASS, like output 4 on specific. Those two cases need nothing from you.

A false positive is the judge saying FAIL where you said PASS. The judge was too strict. Run 5, output 14, for a best friend moving to Auckland:

"The bowl scraped out, the freezer humming cold, / and half a world of salt water laid between, / her morning starting while our street is dark, / and the kitchen keeping one more empty chair."

You labeled specific pass, because the scraped bowl, the humming freezer, and the empty chair all come out of the situation. Suppose the judge fails it, with the reason that the poem never names Priya or Auckland. It flagged a poem you were happy with, and reading that flag costs you time.

A false negative is the judge saying PASS where you said FAIL. The judge was too lenient. Run 5, output 6, for burning the first pancake the way a grandmother always did, while the smoke alarm goes off:

"The blue enamel pan, the seven o'clock light, / and the first one always going to the fire. / Nothing is wasted that was made in a warm room, / and the butter waits, gold in its yellow dish."

You labeled specific fail, because the pan and the butter are the poem's own invention. The grandmother and the alarm never appear. Suppose the judge passes it, reason: the poem names the blue enamel pan. This is the more expensive mistake, because a poem you consider bad now enters your table as a good one.

The four counts together are the confusion counts, sometimes called the confusion matrix. Eighteen right out of twenty sounds the same whichever two are wrong, but a strict judge and a lenient judge cause different trouble, and you want to know which one you have.

This section gave you four buckets for the judge's verdicts. The next one turns them into two numbers you can compare across judge prompts and across runs.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 330" width="100%">
  <rect x="0" y="0" width="800" height="330" fill="#ffffff"/>
  <text x="40" y="36" font-family="sans-serif" font-size="22" fill="#000000">run 5, specific</text>
  <text x="370" y="82" font-family="sans-serif" font-size="18" fill="#000000" text-anchor="middle">you: FAIL</text>
  <text x="630" y="82" font-family="sans-serif" font-size="18" fill="#000000" text-anchor="middle">you: PASS</text>
  <text x="230" y="150" font-family="sans-serif" font-size="18" fill="#000000" text-anchor="end">judge: FAIL</text>
  <text x="230" y="250" font-family="sans-serif" font-size="18" fill="#000000" text-anchor="end">judge: PASS</text>
  <rect x="240" y="95" width="260" height="100" fill="#ffffff" stroke="#000000"/>
  <rect x="500" y="95" width="260" height="100" fill="#ffffff" stroke="#000000"/>
  <rect x="240" y="195" width="260" height="100" fill="#ffffff" stroke="#000000"/>
  <rect x="500" y="195" width="260" height="100" fill="#ffffff" stroke="#000000"/>
  <text x="370" y="140" font-family="sans-serif" font-size="18" fill="#2e7d32" text-anchor="middle">true positive</text>
  <text x="370" y="170" font-family="sans-serif" font-size="18" fill="#000000" text-anchor="middle">output 0</text>
  <text x="630" y="140" font-family="sans-serif" font-size="18" fill="#c62828" text-anchor="middle">false positive</text>
  <text x="630" y="170" font-family="sans-serif" font-size="18" fill="#000000" text-anchor="middle">output 14</text>
  <text x="370" y="240" font-family="sans-serif" font-size="18" fill="#c62828" text-anchor="middle">false negative</text>
  <text x="370" y="270" font-family="sans-serif" font-size="18" fill="#000000" text-anchor="middle">output 6</text>
  <text x="630" y="240" font-family="sans-serif" font-size="18" fill="#2e7d32" text-anchor="middle">true negative</text>
  <text x="630" y="270" font-family="sans-serif" font-size="18" fill="#000000" text-anchor="middle">output 4</text>
</svg>
The judge's verdict crossed with your label on specific gives four buckets, with run 5 outputs 0, 14, 6 and 4 falling into one each.

## Two numbers: precision and recall

The four counts collapse into two numbers, and each answers a different question about the judge.

Precision is, of the outputs the judge failed, the share you also failed. True positives divided by true positives plus false positives. Recall is, of the outputs you failed, the share the judge caught. True positives divided by true positives plus false negatives.

Work it on specific in run 5. You failed 11 of the 20 poems on that criterion. Suppose the judge fails 10 poems, and 9 of them are poems you also failed. That is 9 true positives, 1 false positive, 2 false negatives, and 8 true negatives. Precision is 9 divided by 10, or 0.90. Recall is 9 divided by 11, or 0.82.

Now say them in plain words. Precision 0.90: when this judge fails a poem, nine times out of ten you would have failed it too, so its complaints are worth your attention. Recall 0.82: of the eleven poems you consider bad, it finds nine, and two go past unremarked.

Recall is the number that speaks to the question you walked in with. A judge with low recall lets a regression stay invisible. The poems drift, the judge keeps passing them, and the specific column in your table sits flat while the tool gets worse. Precision protects something else: your time, and your willingness to keep reading what the grader tells you.

Here is why you keep both. Suppose you rewrite the judge prompt to be harsher, and now it fails 18 of the 20 poems. It catches all 11 of yours, so recall is 1.00, a perfect score. Precision is 11 divided by 18, or 0.61. Seven of its complaints are about poems you were happy with, including output 4 and output 14. That judge has stopped measuring the tool and started measuring its own strictness. Either number alone can be pushed to look good. The pair cannot.

Recompute both on the same labeled set every time you touch the judge prompt, and write down what they were before. They are cheap to recompute, because the labels are fixtures and do not move.

You can now compute the judge's precision and recall against a set of human labels, and say in one sentence how much of what the judge reports you should believe.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 300" width="100%">
  <rect x="0" y="0" width="800" height="300" fill="#ffffff"/>
  <text x="40" y="40" font-family="sans-serif" font-size="22" fill="#000000">run 5, specific</text>
  <text x="60" y="85" font-family="sans-serif" font-size="18" fill="#000000">judge FAIL: 10</text>
  <rect x="60" y="95" width="405" height="40" fill="#2e7d32"/>
  <rect x="465" y="95" width="45" height="40" fill="#c62828"/>
  <rect x="60" y="95" width="450" height="40" fill="none" stroke="#000000"/>
  <text x="262" y="160" font-family="sans-serif" font-size="18" fill="#000000" text-anchor="middle">TP 9</text>
  <text x="487" y="160" font-family="sans-serif" font-size="18" fill="#000000" text-anchor="middle">FP 1</text>
  <text x="535" y="122" font-family="sans-serif" font-size="18" fill="#000000">precision 9/10 = 0.90</text>
  <text x="60" y="190" font-family="sans-serif" font-size="18" fill="#000000">you FAIL: 11</text>
  <rect x="60" y="200" width="405" height="40" fill="#2e7d32"/>
  <rect x="465" y="200" width="90" height="40" fill="#c62828"/>
  <rect x="60" y="200" width="495" height="40" fill="none" stroke="#000000"/>
  <text x="262" y="265" font-family="sans-serif" font-size="18" fill="#000000" text-anchor="middle">TP 9</text>
  <text x="510" y="265" font-family="sans-serif" font-size="18" fill="#000000" text-anchor="middle">FN 2</text>
  <text x="580" y="227" font-family="sans-serif" font-size="18" fill="#000000">recall 9/11 = 0.82</text>
</svg>
Precision divides the nine agreements by the ten poems the judge failed, and recall divides the same nine by the eleven poems you failed.

## Too strict and too lenient need different fixes

Precision and recall tell you how much to trust the judge. To improve it, go back to the two lists behind those numbers and read them separately, each disagreement showing the judge's reason next to your label. False positives and false negatives are two different problems and they pull the judge prompt in opposite directions.

Start with the false positive. Output 14, Priya and the empty chair, where you said specific pass and the judge said FAIL because the poem never names Priya or Auckland. The judge's bar sits higher than yours. It wants a proper noun; you accept any concrete detail from the situation. That is a definition problem, not a model problem, and the fix is in your own sentence: say what counts as a concrete detail, and put this poem in the judge prompt as an example that passes. A false positive fix narrows the judge's idea of failure.

Now the false negative. Output 6, the blue enamel pan, where you said specific fail and the judge said PASS because the poem names the pan. The judge saw something concrete and stopped. It never asked where the detail came from. The fix is to name the miss out loud in the prompt: the detail has to come from the situation, not from the poem's own invention, and the grandmother and the smoke alarm are what the situation gave it. A false negative fix widens the judge's idea of failure.

Because the two fixes push opposite ways, one can undo the other. Tighten the prompt to catch output 6 and you may start failing output 14. This is why you rerun the judge on the same labeled set after every edit and compare the pair of numbers to what they were. Recall went up, and did precision hold? That question is answerable in seconds once the counts are printing.

A judge you have measured and adjusted is a judge whose verdicts you can put in front of someone else. It is still a model and it can still be wrong, but now you know roughly how often and in which direction, and you can say so out loud.

You can now separate the judge's false positives from its false negatives and name a different fix for each. The last section puts this judge to work on the question you came here with.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 340" width="100%">
  <rect x="0" y="0" width="800" height="340" fill="#ffffff"/>
  <text x="40" y="36" font-family="sans-serif" font-size="22" fill="#000000">two pulls on one prompt</text>
  <rect x="290" y="50" width="220" height="60" fill="#ffffff" stroke="#000000"/>
  <text x="400" y="88" font-family="sans-serif" font-size="18" fill="#000000" text-anchor="middle">judge prompt</text>
  <line x1="200" y1="168" x2="330" y2="110" stroke="#000000"/>
  <path d="M 330,110 L 319.6,121.2 L 314.8,110.2 Z" fill="#000000"/>
  <line x1="600" y1="168" x2="470" y2="110" stroke="#000000"/>
  <path d="M 470,110 L 480.4,121.2 L 485.2,110.2 Z" fill="#000000"/>
  <text x="185" y="132" font-family="sans-serif" font-size="18" fill="#000000">narrow</text>
  <text x="560" y="132" font-family="sans-serif" font-size="18" fill="#000000">widen</text>
  <rect x="30" y="170" width="330" height="140" fill="#ffffff" stroke="#000000"/>
  <text x="50" y="205" font-family="sans-serif" font-size="18" fill="#c62828">false positive</text>
  <text x="50" y="235" font-family="sans-serif" font-size="18" fill="#000000">output 14</text>
  <text x="50" y="263" font-family="sans-serif" font-size="18" fill="#000000">judge FAIL, you PASS</text>
  <text x="50" y="295" font-family="sans-serif" font-size="18" fill="#000000">fix: narrow FAIL</text>
  <rect x="440" y="170" width="330" height="140" fill="#ffffff" stroke="#000000"/>
  <text x="460" y="205" font-family="sans-serif" font-size="18" fill="#c62828">false negative</text>
  <text x="460" y="235" font-family="sans-serif" font-size="18" fill="#000000">output 6</text>
  <text x="460" y="263" font-family="sans-serif" font-size="18" fill="#000000">judge PASS, you FAIL</text>
  <text x="460" y="295" font-family="sans-serif" font-size="18" fill="#000000">fix: widen FAIL</text>
</svg>
Output 14 asks you to narrow what counts as a failure and output 6 asks you to widen it, so the two fixes pull the same judge prompt in opposite directions.

## A second table, and the answer you came for

The judge's verdicts go into a history table shaped exactly like the one from lesson 1. One row per run, labeled by the saved run's name, one column per criterion, pass rate at the end, oldest first, appended once per run and kept as CSV. This is a second file. The lesson 1 table stays as it is, and no row already written is ever recomputed.

What is new is the columns. The four code rules keep theirs, and specific, mood, and no_advice join them, with three more failure categories to sort their failures into: generic when specific fails, wrong_mood when mood fails, advice when no_advice fails.

Print the judge's confusion counts, precision, and recall directly above the table. Anyone reading a judge column, including you in six months, needs to know how much that column is worth. A column fed by a judge with recall 0.82 can move for two reasons: the tool changed, or the judge missed a few. Having the number in front of you keeps you from over-reading a small wobble, and tells you when a large move is real.

Now read the table down the columns. The specific column is nearly clean in runs 1 and 2, climbs in run 3 where the prompt was trimmed, climbs again in run 4, and stays high in run 5. The no_preamble column is clean for four straight runs and then breaks open in run 5. The advice column shows its first failures in run 4. The overall pass rate falls run over run. The two criteria trending down the most are specific and no_preamble, and the tool is getting worse overall.

That sentence has a run number in it, a criterion name in it, and a trust number behind it. It points at two separate causes: the trimmed prompt cost the poems their details, and whatever changed before run 5 brought the preambles back.

You can now separate the judge's false positives from its false negatives, name a different fix for each, and append the judge's verdicts to a run-by-criterion history table that says whether the tool is getting worse and where. You walked in with a hunch. You are leaving as the person the rest of the team asks.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 360" width="100%">
  <rect x="0" y="0" width="800" height="360" fill="#ffffff"/>
  <text x="40" y="40" font-family="sans-serif" font-size="22" fill="#000000">history table</text>
  <text x="460" y="40" font-family="sans-serif" font-size="18" fill="#000000">judge: precision 0.90, recall 0.82</text>
  <text x="240" y="76" font-family="sans-serif" font-size="18" fill="#000000" text-anchor="middle">specific</text>
  <text x="410" y="76" font-family="sans-serif" font-size="18" fill="#000000" text-anchor="middle">no_preamble</text>
  <text x="560" y="76" font-family="sans-serif" font-size="18" fill="#000000" text-anchor="middle">advice</text>
  <text x="690" y="76" font-family="sans-serif" font-size="18" fill="#000000" text-anchor="middle">pass rate</text>
  <rect x="60" y="86" width="700" height="225" fill="none" stroke="#000000"/>
  <line x1="60" y1="131" x2="760" y2="131" stroke="#000000"/>
  <line x1="60" y1="176" x2="760" y2="176" stroke="#000000"/>
  <line x1="60" y1="221" x2="760" y2="221" stroke="#000000"/>
  <line x1="60" y1="266" x2="760" y2="266" stroke="#000000"/>
  <line x1="160" y1="86" x2="160" y2="311" stroke="#000000"/>
  <line x1="320" y1="86" x2="320" y2="311" stroke="#000000"/>
  <line x1="500" y1="86" x2="500" y2="311" stroke="#000000"/>
  <line x1="620" y1="86" x2="620" y2="311" stroke="#000000"/>
  <text x="76" y="116" font-family="sans-serif" font-size="18" fill="#000000">run 1</text>
  <text x="76" y="161" font-family="sans-serif" font-size="18" fill="#000000">run 2</text>
  <text x="76" y="206" font-family="sans-serif" font-size="18" fill="#000000">run 3</text>
  <text x="76" y="251" font-family="sans-serif" font-size="18" fill="#000000">run 4</text>
  <text x="76" y="296" font-family="sans-serif" font-size="18" fill="#000000">run 5</text>
  <text x="240" y="116" font-family="sans-serif" font-size="18" fill="#2e7d32" text-anchor="middle">clean</text>
  <text x="240" y="161" font-family="sans-serif" font-size="18" fill="#2e7d32" text-anchor="middle">clean</text>
  <text x="240" y="206" font-family="sans-serif" font-size="18" fill="#c62828" text-anchor="middle">fails</text>
  <text x="240" y="251" font-family="sans-serif" font-size="18" fill="#c62828" text-anchor="middle">fails</text>
  <text x="240" y="296" font-family="sans-serif" font-size="18" fill="#c62828" text-anchor="middle">fails</text>
  <text x="410" y="116" font-family="sans-serif" font-size="18" fill="#2e7d32" text-anchor="middle">clean</text>
  <text x="410" y="161" font-family="sans-serif" font-size="18" fill="#2e7d32" text-anchor="middle">clean</text>
  <text x="410" y="206" font-family="sans-serif" font-size="18" fill="#2e7d32" text-anchor="middle">clean</text>
  <text x="410" y="251" font-family="sans-serif" font-size="18" fill="#2e7d32" text-anchor="middle">clean</text>
  <text x="410" y="296" font-family="sans-serif" font-size="18" fill="#c62828" text-anchor="middle">fails</text>
  <text x="560" y="116" font-family="sans-serif" font-size="18" fill="#2e7d32" text-anchor="middle">clean</text>
  <text x="560" y="161" font-family="sans-serif" font-size="18" fill="#2e7d32" text-anchor="middle">clean</text>
  <text x="560" y="206" font-family="sans-serif" font-size="18" fill="#2e7d32" text-anchor="middle">clean</text>
  <text x="560" y="251" font-family="sans-serif" font-size="18" fill="#c62828" text-anchor="middle">fails</text>
  <text x="560" y="296" font-family="sans-serif" font-size="18" fill="#c62828" text-anchor="middle">fails</text>
  <rect x="630" y="100" width="120" height="16" fill="#2e7d32"/>
  <rect x="630" y="145" width="108" height="16" fill="#2e7d32"/>
  <rect x="630" y="190" width="92" height="16" fill="#2e7d32"/>
  <rect x="630" y="235" width="76" height="16" fill="#2e7d32"/>
  <rect x="630" y="280" width="60" height="16" fill="#2e7d32"/>
</svg>
The run-by-criterion table with the judge's precision and recall printed above it: specific breaks at run 3, advice at run 4, no_preamble at run 5, and the pass rate falls every run.

---

From a grader to a judge: measure the thing that measures your tool

You are writing one file, `build/judge/judge.py`. Every step appends to the bottom of it. It never edits `grader.py`; it imports it. Run it from the `baer-buster` folder:

`python -m build.judge.judge build/fixtures/runs/run5.json`

Add `--live` to call the model. Without it the judge reads the replies already recorded in `build/judge/responses/`.

**Step 1: import the grader and read the history it wrote**

The first line imports lesson 1's file. Importing it runs it on the same run file you passed, so lesson 1's whole output prints first: that is the proof nothing was lost. It appends its own row once and never twice. Then the judge prints its mode and reads lesson 1's `history.csv` back, and you should see the same table lesson 1 printed.

```python
from build.grader.grader import (
    OUTPUTS, RUN, RULES, VERDICTS, CATEGORIES, CATEGORY_OF_RULE,
    LABELED_RUN, LABELS_PATH, HISTORY_PATH, HEADER,
    print_verdict, print_table, read_history,
)
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIVE = "--live" in sys.argv

if LIVE:
    print("mode: live")
else:
    print("mode: replay")

print("== judge step 1: the grader, imported ==")
print("run: " + RUN)
print("outputs: " + str(len(OUTPUTS)))
print("lesson 1 history:")
print_table(HEADER, read_history(HISTORY_PATH))
print()
```

```text
== step 1: load the run ==
run: run5
outputs: 20

== step 2: one rule, two outputs ==
output 13  shape  PASS  4 non-empty lines
output 5  shape  FAIL  5 non-empty lines, expected 4

== step 3: all four rules on every output ==
output 0  shape  FAIL  5 non-empty lines, expected 4
output 0  no_preamble  FAIL  first line is a lead-in: Here is a poem for you:
output 3  no_preamble  FAIL  first line is a lead-in: Sure! Here you go:
output 5  shape  FAIL  5 non-empty lines, expected 4
output 7  shape  FAIL  5 non-empty lines, expected 4
output 7  no_preamble  FAIL  first line is a lead-in: Here is a poem about your daughter:
output 8  line_length  FAIL  a line has 12 words, limit is 11
output 10  line_length  FAIL  a line has 14 words, limit is 11
output 11  no_preamble  FAIL  first line is a lead-in: Here is your poem:
output 12  no_copy  FAIL  poem repeats: I have never been so glad to see a jetway
output 15  line_length  FAIL  a line has 12 words, limit is 11
output 18  shape  FAIL  5 non-empty lines, expected 4
output 18  no_preamble  FAIL  first line is a lead-in: Sure, here you go:
checks run: 80
failed checks: 13

== step 4: rules against the labels ==
agreements: 78
disagreements: 2
output 8  line_length  FAIL  human says pass: a line has 12 words, limit is 11
output 15  line_length  FAIL  human says pass: a line has 12 words, limit is 11

== step 5: sort every failure into a bucket ==
wrong_shape: 7  outputs 0, 5, 7, 8, 10, 15, 18
preamble: 2  outputs 3, 11
copied: 1  outputs 12
passed all rules: 10
pass rate: 0.50

== step 6: one row per run, oldest first ==
run   wrong_shape  preamble  copied  pass_rate
run1  0            0         0       1.00
run2  0            0         0       1.00
run3  0            0         0       1.00
run4  0            0         0       1.00
run5  7            2         1       0.50

== step 7: the trend across the history ==
runs in history: 5
grew the most: wrong_shape +7  pass rate 1.00 -> 0.50  getting worse: yes

mode: replay
== judge step 1: the grader, imported ==
run: run5
outputs: 20
lesson 1 history:
run   wrong_shape  preamble  copied  pass_rate
run1  0            0         0       1.00
run2  0            0         0       1.00
run3  0            0         0       1.00
run4  0            0         0       1.00
run5  7            2         1       0.50
```

**Step 2: the prompt the judge answers and the parser that reads it**

The criterion is a sentence, not a line of Python, so it goes in the prompt. The reply has to come back in a fixed shape or your code cannot use it, so the parser accepts exactly two lines and calls anything else a parse error. No model is called yet: this step parses one well-formed reply and one badly formed one so you can see both paths.

```python
CRITERIA = ["specific", "mood", "no_advice"]
CONDITIONS = {
    "specific": "The poem names at least one concrete detail from the situation, not just a generic feeling.",
    "mood": "The poem's mood fits the situation: no cheerful poem for a loss, no mournful poem for good news.",
    "no_advice": "The poem does not tell the person what to do.",
}
SAMPLE = "VERDICT: FAIL\nREASON: No detail from the situation appears in the poem.\n"


def build_prompt(item, criterion):
    return ("Grade one poem against one criterion.\n\n"
            + "SITUATION:\n" + item["situation"] + "\n\n"
            + "POEM:\n" + item["poem"] + "\n\n"
            + "CRITERION " + criterion + ": " + CONDITIONS[criterion] + "\n\n"
            + "Answer in exactly this shape and nothing else:\n"
            + "VERDICT: PASS\n"
            + "REASON: <one sentence>\n\n"
            + "Write FAIL in place of PASS when the criterion is not met.")


def parse_reply(reply):
    verdict = ""
    reason = ""
    for line in reply.strip().split("\n"):
        text = line.strip()
        if text.startswith("VERDICT:"):
            verdict = text[len("VERDICT:"):].strip()
        if text.startswith("REASON:"):
            reason = text[len("REASON:"):].strip()
    if verdict not in ("PASS", "FAIL") or reason == "":
        return "PARSE_ERROR", "reply did not match the two-line shape"
    return verdict, reason


print("== judge step 2: the prompt and the parser ==")
print("criteria: " + ", ".join(CRITERIA))
print("prompt ends: " + build_prompt(OUTPUTS[0], "specific").split("\n")[-1])
verdict, reason = parse_reply(SAMPLE)
print("sample reply  " + verdict + "  " + reason)
verdict, reason = parse_reply("Sure, the poem is fine.")
print("junk reply  " + verdict + "  " + reason)
print()
```

```text
== judge step 2: the prompt and the parser ==
criteria: specific, mood, no_advice
prompt ends: Write FAIL in place of PASS when the criterion is not met.
sample reply  FAIL  No detail from the situation appears in the poem.
junk reply  PARSE_ERROR  reply did not match the two-line shape
```

**Step 3: ask the judge about one poem**

Live mode calls the model and writes the raw reply to its own file before parsing it. Replay reads that file. Both hand the same text to the same parser, so both print the same verdict. A reply is fetched once per poem and criterion and kept in memory, so a later step never asks again. Output 0 is the Rufus poem that never names Rufus.

```python
REPLIES = {}  # one reply per poem and criterion, so no step asks twice


def response_path(i, criterion):
    return HERE / "responses" / (RUN + "_output" + str(i) + "_" + criterion + ".txt")


def ask_model(prompt):
    import anthropic  # only live mode needs the package, so it is imported here
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in message.content if block.type == "text")


def ask_judge(i, criterion):
    if (i, criterion) in REPLIES:
        return REPLIES[(i, criterion)]
    path = response_path(i, criterion)
    if LIVE:
        reply = ask_model(build_prompt(OUTPUTS[i], criterion))
        path.parent.mkdir(exist_ok=True)
        path.write_text(reply)
    elif path.exists():
        reply = path.read_text()
    else:
        print("missing reply: " + str(path))
        sys.exit(1)
    REPLIES[(i, criterion)] = reply
    return reply


def judge_one(i, criterion):
    return parse_reply(ask_judge(i, criterion))


def print_judge_verdict(i, criterion, verdict, reason):
    if verdict == "PARSE_ERROR":
        print("output " + str(i) + "  " + criterion + "  PARSE_ERROR  " + reason)
    else:
        print_verdict(i, criterion, verdict == "PASS", reason)


print("== judge step 3: one poem, one criterion ==")
verdict, reason = judge_one(0, "specific")
print_judge_verdict(0, "specific", verdict, reason)
print()
```

```text
== judge step 3: one poem, one criterion ==
output 0  specific  FAIL  The poem uses abstract phrasing about absence and quiet but never mentions Rufus, the collar, or the hall specifically.
```

**Step 4: judge every poem on every criterion**

Sixty verdicts, three per output. Only the failures print, the same way the code rules did, because sixty lines would bury them. Output 0's reply is reused from step 3 rather than asked again, so its reason is word for word what you already read.

```python
def judge_run():
    results = {}
    for i in range(len(OUTPUTS)):
        for criterion in CRITERIA:
            results[(i, criterion)] = judge_one(i, criterion)
    return results


JUDGED = judge_run()

print("== judge step 4: three criteria on every output ==")
failures = 0
for i in range(len(OUTPUTS)):
    for criterion in CRITERIA:
        verdict, reason = JUDGED[(i, criterion)]
        if verdict != "PASS":
            print_judge_verdict(i, criterion, verdict, reason)
            failures = failures + 1
print("judge verdicts: " + str(len(JUDGED)))
print("judge failures: " + str(failures))
print()
```

```text
== judge step 4: three criteria on every output ==
output 0  specific  FAIL  The poem uses abstract phrasing about absence and quiet but never mentions Rufus, the collar, or the hall specifically.
output 1  mood  FAIL  The poem undercuts the joyful acceptance news with ominous, mournful imagery like "the sea keeps everything it takes at last," creating a mood mismatched to good news.
output 2  mood  FAIL  The poem presumes grief and loss ("practice her absence") rather than capturing the anxious uncertainty of awaiting unknown biopsy results.
output 3  specific  FAIL  The poem uses only abstract imagery like "hours lie flat and yellow" without mentioning any concrete details such as the chair number, the DMV, or the waiting number.
output 5  specific  FAIL  The poem uses only generic imagery ("great noise," "everything still standing," "sky rinsed clean") without naming any concrete detail like the tornado, the oak tree, or the two streets.
output 7  specific  FAIL  The poem uses generic imagery about first steps and joy but never mentions the kitchen tile, the dog, or the water bowl from the actual situation.
output 8  no_advice  FAIL  The line "Let it turn there, sweet and green, for a stranger" is an imperative instruction telling the person what to do with the air freshener.
output 10  specific  FAIL  The poem uses only generic imagery like "grey" and "weather" without naming specific concrete details from the situation, such as the rain, the library book, or the repeated page.
output 10  no_advice  FAIL  The lines "Put it down. Go out and walk in the weather." directly instruct the person on what to do.
output 11  specific  FAIL  The poem uses only abstract imagery ("a hand in the dark," "the hot thing rising") without naming any concrete detail like the car, the key, the parking lot, or the milk.
output 13  specific  FAIL  The poem stays abstract and never mentions the five dollar bill, the movie ticket, or the winter coat pocket.
output 15  specific  FAIL  The poem uses only generic imagery (warmth, rising, gold) without naming any concrete detail like "bakery," "job," or "Monday" from the actual situation.
output 17  specific  FAIL  The poem uses only vague, generic language ("small complaining thing," "such mending") without naming the gate, olive oil, or WD-40 from the situation.
output 17  no_advice  FAIL  The line "Fix the next one too; it costs you nothing" directly instructs the person on what to do.
output 18  no_advice  FAIL  The lines "Speak up next Tuesday. Put your name on it." directly instruct the person on what actions to take.
output 19  specific  FAIL  The poem uses only abstract imagery (dark, cold, grief) without naming any concrete detail from the situation like the cat, four nights, thinness, or the sweater.
output 19  mood  FAIL  The situation describes the cat's relieved, mundane return, but the poem treats it as a permanent, mournful loss, mismatching the actual mood.
judge verdicts: 60
judge failures: 17
```

**Step 5: score the judge against your labels**

`labels.csv` holds the pass or fail you gave each output of run 5 on all seven criteria, and it covers run 5 and no other run. FAIL is the positive class, so a true positive is the judge failing something you failed. Precision is how much of what it flags you agree with. Recall is how much of what you flag it finds.

```python
import csv


def load_judge_labels(path):
    labels = {}
    with open(path, newline="") as handle:
        for row in csv.DictReader(handle):
            for criterion in CRITERIA:
                labels[(int(row["output"]), criterion)] = row[criterion]
    return labels


def confusion(results, labels, count):
    tp = 0
    fp = 0
    fn = 0
    tn = 0
    for i in range(count):
        for criterion in CRITERIA:
            judge_fails = results[(i, criterion)][0] != "PASS"
            human_fails = labels[(i, criterion)] == "fail"
            if judge_fails and human_fails:
                tp = tp + 1
            elif judge_fails:
                fp = fp + 1
            elif human_fails:
                fn = fn + 1
            else:
                tn = tn + 1
    return tp, fp, fn, tn


def divide(top, bottom):
    if bottom == 0:
        return 0.0
    return top / bottom


print("== judge step 5: the judge against your labels ==")
if RUN == LABELED_RUN:
    JUDGE_LABELS = load_judge_labels(LABELS_PATH)
    TP, FP, FN, TN = confusion(JUDGED, JUDGE_LABELS, len(OUTPUTS))
    PRECISION = divide(TP, TP + FP)
    RECALL = divide(TP, TP + FN)
    print("true positives: " + str(TP))
    print("false positives: " + str(FP))
    print("false negatives: " + str(FN))
    print("true negatives: " + str(TN))
    print("precision: " + f"{PRECISION:.2f}")
    print("recall: " + f"{RECALL:.2f}")
else:
    print("no labels for " + RUN + ", so the judge is not scored on this run")
print()
```

```text
== judge step 5: the judge against your labels ==
true positives: 16
false positives: 1
false negatives: 1
true negatives: 42
precision: 0.94
recall: 0.94
```

**Step 6: the two disagreement lists, kept apart**

The same counts, now as two lists you can read. A false positive is the judge too strict: it failed something you passed, and the fix narrows its idea of failure. A false negative is the judge too lenient: it passed something you failed, and the fix widens it. Each line carries the judge's reason next to your label, which is what tells you which sentence in the prompt to change.

```python
def disagreements(results, labels, count, want):
    rows = []
    for i in range(count):
        for criterion in CRITERIA:
            verdict, reason = results[(i, criterion)]
            judge_fails = verdict != "PASS"
            human_fails = labels[(i, criterion)] == "fail"
            if want == "fp" and judge_fails and not human_fails:
                rows.append((i, criterion, reason))
            if want == "fn" and human_fails and not judge_fails:
                rows.append((i, criterion, reason))
    return rows


print("== judge step 6: where the judge and you disagree ==")
if RUN == LABELED_RUN:
    print("false positives, judge too strict:")
    for i, criterion, reason in disagreements(JUDGED, JUDGE_LABELS, len(OUTPUTS), "fp"):
        print_verdict(i, criterion, False, "human says pass: " + reason)
    print("false negatives, judge too lenient:")
    for i, criterion, reason in disagreements(JUDGED, JUDGE_LABELS, len(OUTPUTS), "fn"):
        print_verdict(i, criterion, True, "human says fail: " + reason)
else:
    print("no labels for " + RUN + ", nothing to disagree with")
print()
```

```text
== judge step 6: where the judge and you disagree ==
false positives, judge too strict:
output 8  no_advice  FAIL  human says pass: The line "Let it turn there, sweet and green, for a stranger" is an imperative instruction telling the person what to do with the air freshener.
false negatives, judge too lenient:
output 6  specific  PASS  human says fail: The poem includes concrete details like "the first one always going to the fire," echoing the burned first pancake from the situation.
```

**Step 7: sort every failure, then append the row**

Every failing output goes to the bucket of the first criterion it failed, in the order shape, line_length, no_preamble, no_copy, specific, mood, no_advice. The table has one column per criterion, the four code rules and the three judge criteria together, and the pass rate counts outputs that passed all seven. The precision and recall print directly above it so nobody reads a judge column without knowing what it is worth. This is a second CSV; lesson 1's file is not touched.

```python
CATEGORY_OF = {"specific": "generic", "mood": "wrong_mood", "no_advice": "advice"}
for rule in RULES:
    CATEGORY_OF[rule] = CATEGORY_OF_RULE[rule]
ALL_CATEGORIES = CATEGORIES + ["generic", "wrong_mood", "advice"]
COLUMNS = RULES + CRITERIA
JUDGE_HISTORY_PATH = HERE / "history.csv"
JUDGE_HEADER = ["run"] + COLUMNS + ["pass_rate"]


def failed_criteria(i):
    names = []
    for rule in RULES:
        if not VERDICTS[(i, rule)][0]:
            names.append(rule)
    for criterion in CRITERIA:
        if JUDGED[(i, criterion)][0] != "PASS":
            names.append(criterion)
    return names


def tally(count):
    counts = {}
    for name in COLUMNS:
        counts[name] = 0
    buckets = {}
    for name in ALL_CATEGORIES:
        buckets[name] = 0
    clean = 0
    for i in range(count):
        names = failed_criteria(i)
        if not names:
            clean = clean + 1
        else:
            first = CATEGORY_OF[names[0]]
            buckets[first] = buckets[first] + 1
        for name in names:
            counts[name] = counts[name] + 1
    return counts, buckets, clean


def append_row(path, header, row):
    if not path.exists():
        with open(path, "w", newline="") as handle:
            csv.writer(handle).writerow(header)
    for old in read_history(path):
        if old[0] == row[0]:
            return  # this run is already in the history; never write it twice
    with open(path, "a", newline="") as handle:
        csv.writer(handle).writerow(row)


COUNTS, BUCKETS, CLEAN = tally(len(OUTPUTS))
JUDGE_PASS_RATE = CLEAN / len(OUTPUTS)
ROW = [RUN]
for name in COLUMNS:
    ROW.append(str(COUNTS[name]))
ROW.append(f"{JUDGE_PASS_RATE:.2f}")
append_row(JUDGE_HISTORY_PATH, JUDGE_HEADER, ROW)
JUDGE_HISTORY = read_history(JUDGE_HISTORY_PATH)

print("== judge step 7: every failure in a bucket, and the row it makes ==")
for name in ALL_CATEGORIES:
    print(name + ": " + str(BUCKETS[name]))
print("passed every check: " + str(CLEAN))
print("pass rate: " + f"{JUDGE_PASS_RATE:.2f}")
if RUN == LABELED_RUN:
    print("judge trust  tp " + str(TP) + "  fp " + str(FP) + "  fn " + str(FN))
    print("precision: " + f"{PRECISION:.2f}")
    print("recall: " + f"{RECALL:.2f}")
else:
    print("no labels for " + RUN + ", the judge columns below are unscored")
print_table(JUDGE_HEADER, JUDGE_HISTORY)
print()
```

```text
== judge step 7: every failure in a bucket, and the row it makes ==
wrong_shape: 7
preamble: 2
copied: 1
generic: 3
wrong_mood: 2
advice: 0
passed every check: 5
pass rate: 0.25
judge trust  tp 16  fp 1  fn 1
precision: 0.94
recall: 0.94
run   shape  line_length  no_preamble  no_copy  specific  mood  no_advice  pass_rate
run1  0      0            0            0        0         0     0          1.00
run2  0      0            0            0        1         0     1          0.90
run3  0      0            0            0        7         0     1          0.60
run4  0      0            0            0        9         0     3          0.40
run5  4      3            5            1        10        3     4          0.25
```

**Step 8: read the answer off the table**

The arithmetic is lesson 1's: the column with the largest rise in failures from the oldest row to the newest, ties going to the leftmost, and whether the newest pass rate is below the oldest. Your history holds one row, so oldest and newest are the same row and the line reads flat. Point the judge at `run1.json` through `run4.json`, oldest first, then at run 5 again. The table fills out, `specific` climbs from run 3 and `no_preamble` breaks open in run 5, and the closing line names the regression with a number behind it.

```python
def judge_trend(rows):
    oldest = rows[0]
    newest = rows[-1]
    best_name = COLUMNS[0]
    best_growth = None
    for col, name in enumerate(COLUMNS, start=1):
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
    return ("trending down the most: " + best_name + " " + f"{best_growth:+d}"
            + "  pass rate " + f"{old_rate:.2f}" + " -> " + f"{new_rate:.2f}"
            + "  getting worse: " + worse)


print("== judge step 8: the answer you came for ==")
print("runs in history: " + str(len(JUDGE_HISTORY)))
print(judge_trend(JUDGE_HISTORY))
print()
```

```text
== judge step 8: the answer you came for ==
runs in history: 5
trending down the most: specific +10  pass rate 1.00 -> 0.25  getting worse: yes
```
