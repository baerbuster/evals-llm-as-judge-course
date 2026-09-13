# From a Hunch to a Grader

## A rule is your intuition, written down

You think your tool is getting worse, and that thought is worth taking seriously. It is also worth turning into something you can check twice. An eval is a repeatable way of measuring whether an AI tool's outputs are good, so the answer comes out the same no matter who runs it. The smallest piece of one is a rule: a pass/fail check written in code, which gives the same verdict on the same output every time. A verdict is the pass or the fail itself. An output is one thing the tool made for one input, which here means one poem for one situation.

Start with the plainest thing you expect from the poem tool: four lines, nothing else. Written as a condition, that is the shape rule. A poem passes when it has exactly four non-empty lines. Now apply it to one output. A run is one batch of outputs from one version of the tool, saved to a file. In run 1, output 5, the situation was "The tornado passed two streets over and our oak tree is still standing," and the poem came back:

"Two streets over, the sky went black and roaring, / and here our oak still holds its thousand hands. / The air comes back, green-washed and strangely sweet. / We are still here. The leaves are still here."

Count the lines: four. Verdict: pass. Anyone you hand that rule to counts the same four.

The same situation shows up in run 5, output 5, and the tool answered:

"The great noise went by and did not choose us, / and everything still standing that was standing, / and the sky rinsed clean and letting go, / and the air comes back sweet into our mouths, / and nothing, nothing of ours is broken."

Five lines. Verdict: fail. Same situation, same rule, different answer, and the difference is not a matter of taste. You do not have to argue that the second poem feels loose. You can say it has five lines where four were expected, and anyone can check you.

That is the whole move. The feeling "this got worse" stays in your head. The sentence "exactly four non-empty lines" leaves your head, and a person or a machine can apply it without asking you what you meant. This section gave you one rule and two verdicts you can point at. The next one sharpens a rule until a second person reading it lands on your verdict every time.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 330" width="100%">
  <rect x="0" y="0" width="800" height="330" fill="#ffffff"/>
  <text x="400" y="34" font-family="sans-serif" font-size="22" fill="#000000" text-anchor="middle">shape: exactly 4 non-empty lines</text>
  <text x="40" y="72" font-family="sans-serif" font-size="18" fill="#000000">run 1 output 5</text>
  <text x="420" y="72" font-family="sans-serif" font-size="18" fill="#000000">run 5 output 5</text>
  <rect x="40" y="86" width="300" height="30" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <rect x="40" y="124" width="300" height="30" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <rect x="40" y="162" width="300" height="30" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <rect x="40" y="200" width="300" height="30" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <text x="54" y="107" font-family="sans-serif" font-size="18" fill="#000000">line 1</text>
  <text x="54" y="145" font-family="sans-serif" font-size="18" fill="#000000">line 2</text>
  <text x="54" y="183" font-family="sans-serif" font-size="18" fill="#000000">line 3</text>
  <text x="54" y="221" font-family="sans-serif" font-size="18" fill="#000000">line 4</text>
  <rect x="420" y="86" width="300" height="30" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <rect x="420" y="124" width="300" height="30" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <rect x="420" y="162" width="300" height="30" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <rect x="420" y="200" width="300" height="30" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <rect x="420" y="238" width="300" height="30" fill="#ffffff" stroke="#c62828" stroke-width="3"/>
  <text x="434" y="107" font-family="sans-serif" font-size="18" fill="#000000">line 1</text>
  <text x="434" y="145" font-family="sans-serif" font-size="18" fill="#000000">line 2</text>
  <text x="434" y="183" font-family="sans-serif" font-size="18" fill="#000000">line 3</text>
  <text x="434" y="221" font-family="sans-serif" font-size="18" fill="#000000">line 4</text>
  <text x="434" y="259" font-family="sans-serif" font-size="18" fill="#c62828">line 5</text>
  <text x="40" y="302" font-family="sans-serif" font-size="18" fill="#2e7d32">4 lines PASS</text>
  <text x="420" y="302" font-family="sans-serif" font-size="18" fill="#c62828">5 lines FAIL</text>
</svg>
The same situation graded by the shape rule passes in run 1 with four lines and fails in run 5 with five.

## Make the rule so a second person gets the same verdict

A rule is finished when someone else can apply it to the same poem and reach the verdict you would have reached. That test is easy to run in your head: would a careful stranger, holding only your sentence and the poem, agree with you? Adjectives fail this test. "The lines should not ramble" is a feeling wearing a rule's clothes. Conditions with something countable in them pass it, because there is nothing left to interpret.

Take the second rule for the poem tool: every line is under twelve words. Here is run 5, output 13, for the situation about finding a five dollar bill in a coat pocket:

"The year gives back a little of its luck, / unlooked for, out of the dark of something old. / Small mercies keep their places and their patience, / and the plain hour goes suddenly to gold."

Nine words, nine, eight, eight. Verdict: pass. You did not decide it was pleasant. You counted.

Now run 5, output 10, for the situation about six days of rain. Its second line is:

"and the mind slides off whatever it is given and will not take hold,"

Fourteen words. Verdict: fail. The stranger counts fourteen too, and the two of you never have to discuss whether the line rambles. That is the point of the countable condition: it moved the disagreement from taste to arithmetic, where it can be settled.

Two more rules for this tool need the same treatment. No preamble: the poem starts at the first line of the poem, with no title line and no lead-in such as "Here is a poem" before it. No copy: no sentence from the situation appears word for word in the poem. Neither is as clean as counting words, and both will cost you a little arguing later, which is fine. Write each one as the tightest sentence you can, then look for the poem that sits right on its edge.

You can now write a pass/fail rule for a single output that a second person could apply and reach the same verdict as you. You have four of them, and for each one you can hold up an output that passes it and an output that fails it. That is the unit everything else in this course is built out of.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 300" width="100%">
  <rect x="0" y="0" width="800" height="300" fill="#ffffff"/>
  <text x="400" y="32" font-family="sans-serif" font-size="22" fill="#000000" text-anchor="middle">line_length: every line under 12 words</text>
  <line x1="550" y1="74" x2="550" y2="256" stroke="#000000" stroke-width="2" stroke-dasharray="6 6"/>
  <text x="550" y="276" font-family="sans-serif" font-size="18" fill="#000000" text-anchor="middle">12</text>
  <text x="40" y="68" font-family="sans-serif" font-size="18" fill="#000000">run 5 output 13</text>
  <text x="40" y="97" font-family="sans-serif" font-size="18" fill="#000000">line 1</text>
  <text x="40" y="127" font-family="sans-serif" font-size="18" fill="#000000">line 2</text>
  <text x="40" y="157" font-family="sans-serif" font-size="18" fill="#000000">line 3</text>
  <text x="40" y="187" font-family="sans-serif" font-size="18" fill="#000000">line 4</text>
  <rect x="190" y="80" width="270" height="22" fill="#2e7d32"/>
  <rect x="190" y="110" width="270" height="22" fill="#2e7d32"/>
  <rect x="190" y="140" width="240" height="22" fill="#2e7d32"/>
  <rect x="190" y="170" width="240" height="22" fill="#2e7d32"/>
  <text x="470" y="97" font-family="sans-serif" font-size="18" fill="#000000">9</text>
  <text x="470" y="127" font-family="sans-serif" font-size="18" fill="#000000">9</text>
  <text x="440" y="157" font-family="sans-serif" font-size="18" fill="#000000">8</text>
  <text x="440" y="187" font-family="sans-serif" font-size="18" fill="#000000">8</text>
  <text x="655" y="145" font-family="sans-serif" font-size="18" fill="#2e7d32">PASS</text>
  <text x="40" y="212" font-family="sans-serif" font-size="18" fill="#000000">run 5 output 10</text>
  <text x="40" y="241" font-family="sans-serif" font-size="18" fill="#000000">line 2</text>
  <rect x="190" y="224" width="420" height="22" fill="#c62828"/>
  <text x="618" y="241" font-family="sans-serif" font-size="18" fill="#000000">14</text>
  <text x="655" y="241" font-family="sans-serif" font-size="18" fill="#c62828">FAIL</text>
</svg>
Word counts per line in run 5 turn the rule into arithmetic: output 13 stays under twelve, output 10's second line runs to fourteen.

## Run the rules against your own labels

A rule earns your trust when you run it over a whole run and check its verdicts against your own judgment. So read run 5 yourself, poem by poem, and write down pass or fail for every rule. That is a human label: the pass or fail a person gave an output by hand. Treat those labels as ground truth, the correct answer that everything else is measured against, and call the outputs that have them your labeled set. Run 5 comes to you already labeled, along with all five saved runs. Data shipped so a run can be repeated exactly is a fixture, and that is what these are.

Then run the rules and set the two columns side by side. Agreement means the rule's verdict matches your label for that output. Disagreement means it does not. Run 5, output 12, is an agreement. The situation ended with "I have never been so glad to see a jetway," and the poem's second line is that sentence word for word. The no_copy rule fails it, you labeled it fail, and the two of you are done.

The disagreements are more useful. Run 5, output 8, has this second line:

"and the small tree still turns on its string in the car,"

Twelve words exactly. The line_length rule says under twelve, so it fails. You labeled it pass, because it reads fine. Output 15's last line does the same thing: "and the days ahead are rising up gold and full of it," twelve again, rule fail, label pass.

Nothing is broken here. You found the edge of your own rule, which is the only place a rule can be wrong. Decide it once: either twelve words is acceptable and the rule becomes twelve or fewer, or twelve is too long and those two labels were generous. Both answers are defensible. What is not defensible is leaving it undecided, because then your grader and your judgment drift apart without either of you noticing.

You can now run your rules over a set of outputs and list every case where the rule's verdict disagrees with your own label. The list is short, it is specific, and each line on it is a decision you get to make once.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 250" width="100%">
  <rect x="0" y="0" width="800" height="250" fill="#ffffff"/>
  <text x="400" y="36" font-family="sans-serif" font-size="22" fill="#000000" text-anchor="middle">run 5: rule verdict vs my label</text>
  <rect x="40" y="56" width="720" height="154" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <line x1="200" y1="56" x2="200" y2="210" stroke="#000000" stroke-width="2"/>
  <line x1="400" y1="56" x2="400" y2="210" stroke="#000000" stroke-width="2"/>
  <line x1="580" y1="56" x2="580" y2="210" stroke="#000000" stroke-width="2"/>
  <line x1="40" y1="96" x2="760" y2="96" stroke="#000000" stroke-width="2"/>
  <line x1="40" y1="134" x2="760" y2="134" stroke="#000000" stroke-width="2"/>
  <line x1="40" y1="172" x2="760" y2="172" stroke="#000000" stroke-width="2"/>
  <text x="54" y="84" font-family="sans-serif" font-size="18" fill="#000000">output</text>
  <text x="212" y="84" font-family="sans-serif" font-size="18" fill="#000000">rule</text>
  <text x="412" y="84" font-family="sans-serif" font-size="18" fill="#000000">my label</text>
  <text x="592" y="84" font-family="sans-serif" font-size="18" fill="#000000">match</text>
  <text x="54" y="122" font-family="sans-serif" font-size="18" fill="#000000">12</text>
  <text x="212" y="122" font-family="sans-serif" font-size="18" fill="#c62828">no_copy FAIL</text>
  <text x="412" y="122" font-family="sans-serif" font-size="18" fill="#c62828">FAIL</text>
  <text x="592" y="122" font-family="sans-serif" font-size="18" fill="#000000">agree</text>
  <text x="54" y="160" font-family="sans-serif" font-size="18" fill="#000000">8</text>
  <text x="212" y="160" font-family="sans-serif" font-size="18" fill="#c62828">line_length FAIL</text>
  <text x="412" y="160" font-family="sans-serif" font-size="18" fill="#2e7d32">PASS</text>
  <text x="592" y="160" font-family="sans-serif" font-size="18" fill="#c62828">disagree</text>
  <text x="54" y="198" font-family="sans-serif" font-size="18" fill="#000000">15</text>
  <text x="212" y="198" font-family="sans-serif" font-size="18" fill="#c62828">line_length FAIL</text>
  <text x="412" y="198" font-family="sans-serif" font-size="18" fill="#2e7d32">PASS</text>
  <text x="592" y="198" font-family="sans-serif" font-size="18" fill="#c62828">disagree</text>
</svg>
Setting the rule's verdict beside the human label on run 5 shows one agreement and two disagreements, both on twelve-word lines.

## Sort every failure into a named bucket

A pass rate tells you how much broke. It does not tell you what broke. The pass rate is the share of outputs that passed, a number between 0 and 1, and on its own it is one of the least actionable numbers you can look at. Reading each failure and sorting it into a named bucket is what turns it into something you can act on. That bucket is a failure category, and the reading-and-sorting is error analysis.

For the poem tool, three categories cover everything the code rules can catch. A failure goes to wrong_shape if shape or line_length failed, to preamble if no_preamble failed, and to copied if no_copy failed.

Start with the easy one. Run 5, output 11, for the situation about someone keying a car in the grocery store lot, begins:

"Here is your poem: / Something was taken from you in a small way, / a hand in the dark that did not wait to answer, / and the hot thing rising that has nowhere to go."

One rule failed, no_preamble, so this output goes in the preamble bucket. Nothing to decide.

Run 5, output 0, is the case that needs a decision. It opens with "Here is a poem for you:" and then runs four more lines, so it fails no_preamble and it fails shape, five lines where four were expected. Two rules, one output, and a category has to hold it. Pick an order for your rules and put the failure in the bucket for the first one it failed. With shape first, output 0 lands in wrong_shape. The order itself barely matters. What matters is that it never changes, so the same failure lands in the same bucket today and next month, and the counts you compare are counts of the same thing.

Without the buckets you are left saying "half of run 5 failed" and staring at it. With them you can say which half, and go look at the part of your prompt that produces opening lines. Some things you care about have no rule behind them yet, so their buckets come later.

This section gave you the categories. The next one gives you the row of numbers they go into, and the history that makes the row mean something.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 320" width="100%">
  <rect x="0" y="0" width="800" height="320" fill="#ffffff"/>
  <text x="400" y="36" font-family="sans-serif" font-size="22" fill="#000000" text-anchor="middle">run 5 failures into buckets</text>
  <rect x="40" y="80" width="250" height="64" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <text x="56" y="106" font-family="sans-serif" font-size="18" fill="#000000">output 11</text>
  <text x="56" y="132" font-family="sans-serif" font-size="18" fill="#c62828">no_preamble FAIL</text>
  <rect x="40" y="180" width="250" height="90" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <text x="56" y="206" font-family="sans-serif" font-size="18" fill="#000000">output 0</text>
  <text x="56" y="232" font-family="sans-serif" font-size="18" fill="#c62828">shape FAIL</text>
  <text x="56" y="258" font-family="sans-serif" font-size="18" fill="#c62828">no_preamble FAIL</text>
  <rect x="520" y="70" width="240" height="50" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <text x="540" y="102" font-family="sans-serif" font-size="18" fill="#000000">wrong_shape</text>
  <rect x="520" y="150" width="240" height="50" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <text x="540" y="182" font-family="sans-serif" font-size="18" fill="#000000">preamble</text>
  <rect x="520" y="230" width="240" height="50" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <text x="540" y="262" font-family="sans-serif" font-size="18" fill="#000000">copied</text>
  <line x1="290" y1="112" x2="508" y2="172" stroke="#000000" stroke-width="2"/>
  <path d="M516,175 L498,174 L504,160 Z" fill="#000000"/>
  <line x1="290" y1="225" x2="508" y2="101" stroke="#000000" stroke-width="2"/>
  <path d="M516,97 L498,98 L505,112 Z" fill="#000000"/>
  <text x="400" y="305" font-family="sans-serif" font-size="18" fill="#000000" text-anchor="middle">shape is first</text>
</svg>
Output 11 fails one rule and lands in preamble, while output 0 fails two and lands in the bucket of the first rule in the fixed order.

## One row per run, forever

One run's pass rate is a number with nothing to compare it to. Two runs can be a blip. What answers your original question is a history: one row per run, written once, kept forever. Make it a table with the run's name first, one column per failure category, and the overall pass rate at the end, oldest run first. Keep it as a CSV so you can open it in a spreadsheet or plot it later without touching the grader.

Every time your grader runs, it appends one row and then reads the whole file back. It never recomputes an old row. The row is labeled by the saved run's name, not by the clock, so the same run produces the same row on anyone's machine, and a row written last month still says what you saw last month.

Now read the columns down instead of across. For the poem tool, runs 1 through 4 have zeros in every bucket and a pass rate of 1.00, 1.00, 1.00, 1.00. Run 5 has numbers in wrong_shape and in preamble, and a pass rate well below the four before it. The trend is the direction a number moves across runs, oldest to newest, and this one moves one way. A regression is the tool getting worse than it used to be. You are looking at one, and the buckets say where: two categories that were empty for four straight runs are not empty now, so whatever changed between run 4 and run 5 is the thing to go read.

That is a different sentence from "it feels worse lately." It has a run number in it and a category name in it, and it survives being repeated to someone who was not there.

You can now sort every failure into a named bucket, append each run to a history of every past run, and read a run-by-category table to say whether your tool is getting worse and in which bucket.

What the table cannot tell you yet is whether run 5's Rufus poem, which never mentions Rufus or his collar, is still about the person's dog at all. No rule counts that. Lesson 2 is how you grade it anyway.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 320" width="100%">
  <rect x="0" y="0" width="800" height="320" fill="#ffffff"/>
  <text x="400" y="36" font-family="sans-serif" font-size="22" fill="#000000" text-anchor="middle">history: one row per run</text>
  <rect x="40" y="56" width="720" height="230" fill="#ffffff" stroke="#000000" stroke-width="2"/>
  <line x1="160" y1="56" x2="160" y2="286" stroke="#000000" stroke-width="2"/>
  <line x1="340" y1="56" x2="340" y2="286" stroke="#000000" stroke-width="2"/>
  <line x1="500" y1="56" x2="500" y2="286" stroke="#000000" stroke-width="2"/>
  <line x1="630" y1="56" x2="630" y2="286" stroke="#000000" stroke-width="2"/>
  <line x1="40" y1="96" x2="760" y2="96" stroke="#000000" stroke-width="2"/>
  <line x1="40" y1="134" x2="760" y2="134" stroke="#000000" stroke-width="2"/>
  <line x1="40" y1="172" x2="760" y2="172" stroke="#000000" stroke-width="2"/>
  <line x1="40" y1="210" x2="760" y2="210" stroke="#000000" stroke-width="2"/>
  <line x1="40" y1="248" x2="760" y2="248" stroke="#000000" stroke-width="2"/>
  <text x="52" y="84" font-family="sans-serif" font-size="18" fill="#000000">run</text>
  <text x="172" y="84" font-family="sans-serif" font-size="18" fill="#000000">wrong_shape</text>
  <text x="352" y="84" font-family="sans-serif" font-size="18" fill="#000000">preamble</text>
  <text x="512" y="84" font-family="sans-serif" font-size="18" fill="#000000">copied</text>
  <text x="642" y="84" font-family="sans-serif" font-size="18" fill="#000000">pass rate</text>
  <text x="52" y="122" font-family="sans-serif" font-size="18" fill="#000000">run 1</text>
  <text x="172" y="122" font-family="sans-serif" font-size="18" fill="#000000">0</text>
  <text x="352" y="122" font-family="sans-serif" font-size="18" fill="#000000">0</text>
  <text x="512" y="122" font-family="sans-serif" font-size="18" fill="#000000">0</text>
  <text x="642" y="122" font-family="sans-serif" font-size="18" fill="#2e7d32">1.00</text>
  <text x="52" y="160" font-family="sans-serif" font-size="18" fill="#000000">run 2</text>
  <text x="172" y="160" font-family="sans-serif" font-size="18" fill="#000000">0</text>
  <text x="352" y="160" font-family="sans-serif" font-size="18" fill="#000000">0</text>
  <text x="512" y="160" font-family="sans-serif" font-size="18" fill="#000000">0</text>
  <text x="642" y="160" font-family="sans-serif" font-size="18" fill="#2e7d32">1.00</text>
  <text x="52" y="198" font-family="sans-serif" font-size="18" fill="#000000">run 3</text>
  <text x="172" y="198" font-family="sans-serif" font-size="18" fill="#000000">0</text>
  <text x="352" y="198" font-family="sans-serif" font-size="18" fill="#000000">0</text>
  <text x="512" y="198" font-family="sans-serif" font-size="18" fill="#000000">0</text>
  <text x="642" y="198" font-family="sans-serif" font-size="18" fill="#2e7d32">1.00</text>
  <text x="52" y="236" font-family="sans-serif" font-size="18" fill="#000000">run 4</text>
  <text x="172" y="236" font-family="sans-serif" font-size="18" fill="#000000">0</text>
  <text x="352" y="236" font-family="sans-serif" font-size="18" fill="#000000">0</text>
  <text x="512" y="236" font-family="sans-serif" font-size="18" fill="#000000">0</text>
  <text x="642" y="236" font-family="sans-serif" font-size="18" fill="#2e7d32">1.00</text>
  <text x="52" y="274" font-family="sans-serif" font-size="18" fill="#000000">run 5</text>
  <text x="172" y="274" font-family="sans-serif" font-size="18" fill="#c62828">&gt; 0</text>
  <text x="352" y="274" font-family="sans-serif" font-size="18" fill="#c62828">&gt; 0</text>
  <text x="512" y="274" font-family="sans-serif" font-size="18" fill="#000000">0</text>
  <line x1="670" y1="256" x2="670" y2="272" stroke="#c62828" stroke-width="3"/>
  <path d="M670,280 L661,266 L679,266 Z" fill="#c62828"/>
</svg>
Reading the history down its columns shows four runs of empty buckets and a full pass rate, then run 5 filling wrong_shape and preamble while the pass rate drops.

---

From a hunch to a grader: build the file one rule at a time

You are writing one file, `build/grader/grader.py`. Every step appends to the bottom of it. Nothing you have already typed is ever edited. Run it from the `baer-buster` folder with the run file as the only argument:

`python -m build.grader.grader build/fixtures/runs/run5.json`

**Step 1: load the run the command line points at**

The grader has to be pointed at one saved run and told nothing else. This step reads that file and prints what it found, so you know the path worked before you write a single rule. The run's name comes from the file name, not the clock, so the same file always produces the same name.

```python
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_run(path):
    return json.loads(Path(path).read_text())


def run_name(path):
    return Path(path).stem


RUN_PATH = sys.argv[1]
OUTPUTS = load_run(RUN_PATH)
RUN = run_name(RUN_PATH)

print("== step 1: load the run ==")
print("run: " + RUN)
print("outputs: " + str(len(OUTPUTS)))
print()
```

```text
== step 1: load the run ==
run: run5
outputs: 20
```

**Step 2: the shape rule, and two verdicts you can check by hand**

This is the rule from the first section: exactly four non-empty lines. The function returns the verdict and the reason together, because a verdict with no reason is not something you can argue with. Run it on output 13 and output 5 and count the lines yourself. You should get the same two answers it does.

```python
def poem_lines(poem):
    lines = []
    for line in poem.split("\n"):
        if line.strip():
            lines.append(line.strip())
    return lines


def check_shape(poem):
    lines = poem_lines(poem)
    if len(lines) == 4:
        return True, "4 non-empty lines"
    return False, str(len(lines)) + " non-empty lines, expected 4"


def print_verdict(i, rule, ok, reason):
    if ok:
        mark = "PASS"
    else:
        mark = "FAIL"
    print("output " + str(i) + "  " + rule + "  " + mark + "  " + reason)


print("== step 2: one rule, two outputs ==")
for index in [13, 5]:
    passed, why = check_shape(OUTPUTS[index]["poem"])
    print_verdict(index, "shape", passed, why)
print()
```

```text
== step 2: one rule, two outputs ==
output 13  shape  PASS  4 non-empty lines
output 5  shape  FAIL  5 non-empty lines, expected 4
```

**Step 3: the other three rules, run over every output**

Now the rest of the rules from the second section, each written as a countable condition. Then one loop that applies all four to all twenty outputs and keeps every verdict. The step prints only the failures, plus the two counts, because eighty passing lines would bury them.

```python
LEAD_INS = ("here is", "here's", "sure")
RULES = ["shape", "line_length", "no_preamble", "no_copy"]


def check_line_length(poem):
    for line in poem_lines(poem):
        if len(line.split()) >= 12:
            return False, "a line has " + str(len(line.split())) + " words, limit is 11"
    return True, "every line under 12 words"


def check_no_preamble(poem):
    first = poem_lines(poem)[0]
    if first.endswith(":") or first.lower().startswith(LEAD_INS):
        return False, "first line is a lead-in: " + first
    return True, "starts on the poem"


def sentences(situation):
    parts = []
    for part in situation.replace("!", ".").replace("?", ".").split("."):
        if len(part.split()) >= 4:
            parts.append(part.strip())
    return parts


def check_no_copy(situation, poem):
    low = poem.lower()
    for sentence in sentences(situation):
        if sentence.lower() in low:
            return False, "poem repeats: " + sentence
    return True, "no sentence copied"


def check_rule(rule, item):
    if rule == "shape":
        return check_shape(item["poem"])
    if rule == "line_length":
        return check_line_length(item["poem"])
    if rule == "no_preamble":
        return check_no_preamble(item["poem"])
    return check_no_copy(item["situation"], item["poem"])


def grade_run(outputs):
    verdicts = {}
    for i, item in enumerate(outputs):
        for rule in RULES:
            verdicts[(i, rule)] = check_rule(rule, item)
    return verdicts


VERDICTS = grade_run(OUTPUTS)

print("== step 3: all four rules on every output ==")
failed = 0
for i in range(len(OUTPUTS)):
    for rule in RULES:
        passed, why = VERDICTS[(i, rule)]
        if not passed:
            print_verdict(i, rule, passed, why)
            failed = failed + 1
print("checks run: " + str(len(VERDICTS)))
print("failed checks: " + str(failed))
print()
```

```text
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
```

**Step 4: put the rules next to your own labels**

`labels.csv` holds the pass or fail you gave each output of run 5 by hand, one column per rule. This step loads them, compares them cell by cell, and prints only where the two of you differ. The labels cover run 5 and nothing else, so the comparison is skipped for any other run. Two disagreements come out, both on the twelve-word edge, and both are the decision the third section asked you to make once.

```python
LABELS_PATH = HERE.parent / "fixtures" / "labels.csv"
LABELED_RUN = "run5"  # labels.csv covers run5 and no other run


def load_labels(path):
    labels = {}
    with open(path, newline="") as handle:
        for row in csv.DictReader(handle):
            for rule in RULES:
                labels[(int(row["output"]), rule)] = row[rule]
    return labels


def compare_to_labels(verdicts, labels, count):
    agreed = 0
    disagreed = []
    for i in range(count):
        for rule in RULES:
            passed, why = verdicts[(i, rule)]
            if passed:
                mine = "pass"
            else:
                mine = "fail"
            theirs = labels[(i, rule)]
            if mine == theirs:
                agreed = agreed + 1
            else:
                disagreed.append((i, rule, mine, theirs, why))
    return agreed, disagreed


print("== step 4: rules against the labels ==")
if RUN == LABELED_RUN:
    LABELS = load_labels(LABELS_PATH)
    AGREED, DISAGREED = compare_to_labels(VERDICTS, LABELS, len(OUTPUTS))
    print("agreements: " + str(AGREED))
    print("disagreements: " + str(len(DISAGREED)))
    for i, rule, mine, theirs, why in DISAGREED:
        print_verdict(i, rule, mine == "pass", "human says " + theirs + ": " + why)
else:
    print("no labels for " + RUN + ", skipping the comparison")
print()
```

```text
== step 4: rules against the labels ==
agreements: 78
disagreements: 2
output 8  line_length  FAIL  human says pass: a line has 12 words, limit is 11
output 15  line_length  FAIL  human says pass: a line has 12 words, limit is 11
```

**Step 5: sort every failure into one named bucket**

Each failing output goes to the bucket of the first rule it failed, in the order the rules are listed. Output 0 fails shape and no_preamble; shape comes first, so it lands in `wrong_shape` and stays there for good. The pass rate at the bottom counts only outputs that passed all four rules.

```python
CATEGORY_OF_RULE = {
    "shape": "wrong_shape",
    "line_length": "wrong_shape",
    "no_preamble": "preamble",
    "no_copy": "copied",
}
CATEGORIES = ["wrong_shape", "preamble", "copied"]


def categorize(verdicts, count):
    buckets = {}
    for name in CATEGORIES:
        buckets[name] = []
    passed_all = 0
    for i in range(count):
        first_failed = None
        for rule in RULES:
            passed, why = verdicts[(i, rule)]
            if not passed and first_failed is None:
                first_failed = rule
        if first_failed is None:
            passed_all = passed_all + 1
        else:
            buckets[CATEGORY_OF_RULE[first_failed]].append(i)
    return buckets, passed_all


BUCKETS, PASSED = categorize(VERDICTS, len(OUTPUTS))
PASS_RATE = PASSED / len(OUTPUTS)

print("== step 5: sort every failure into a bucket ==")
for name in CATEGORIES:
    members = BUCKETS[name]
    numbers = []
    for i in members:
        numbers.append(str(i))
    print(name + ": " + str(len(members)) + "  outputs " + ", ".join(numbers))
print("passed all rules: " + str(PASSED))
print("pass rate: " + f"{PASS_RATE:.2f}")
print()
```

```text
== step 5: sort every failure into a bucket ==
wrong_shape: 7  outputs 0, 5, 7, 8, 10, 15, 18
preamble: 2  outputs 3, 11
copied: 1  outputs 12
passed all rules: 10
pass rate: 0.50
```

**Step 6: append this run to the history and print the table**

One row per run, written once. If `history.csv` is missing the grader creates it with the header line and nothing else, so every row in the table comes from a run you actually pointed it at. The row is labeled with the run's name. Grading the same run twice does not write it twice.

```python
HISTORY_PATH = HERE / "history.csv"
HEADER = ["run"] + CATEGORIES + ["pass_rate"]


def read_history(path):
    if not path.exists():
        return []
    rows = []
    with open(path, newline="") as handle:
        reader = csv.reader(handle)
        next(reader, None)  # drop the header line
        for row in reader:
            rows.append(row)
    return rows


def history_row(run, buckets, pass_rate):
    row = [run]
    for name in CATEGORIES:
        row.append(str(len(buckets[name])))
    row.append(f"{pass_rate:.2f}")
    return row


def append_history(path, row):
    if not path.exists():
        with open(path, "w", newline="") as handle:
            csv.writer(handle).writerow(HEADER)
    for old in read_history(path):
        if old[0] == row[0]:
            return  # this run is already in the history; never write it twice
    with open(path, "a", newline="") as handle:
        csv.writer(handle).writerow(row)


def print_table(header, rows):
    widths = []
    for col in range(len(header)):
        width = len(header[col])
        for row in rows:
            if len(row[col]) > width:
                width = len(row[col])
        widths.append(width)
    for line in [header] + rows:
        cells = []
        for col in range(len(line)):
            cells.append(line[col].ljust(widths[col]))
        print("  ".join(cells).rstrip())


append_history(HISTORY_PATH, history_row(RUN, BUCKETS, PASS_RATE))
HISTORY = read_history(HISTORY_PATH)

print("== step 6: one row per run, oldest first ==")
print_table(HEADER, HISTORY)
print()
```

```text
== step 6: one row per run, oldest first ==
run   wrong_shape  preamble  copied  pass_rate
run1  0            0         0       1.00
run2  0            0         0       1.00
run3  0            0         0       1.00
run4  0            0         0       1.00
run5  7            2         1       0.50
```

**Step 7: read the trend off the table**

The closing line does arithmetic you can check by eye: the category with the largest rise in failures from the oldest row to the newest, ties going to the leftmost column, and whether the newest pass rate is below the oldest. Your history holds one row so far, so the oldest and the newest row are the same row and the line reads flat. Point the grader at `run1.json` through `run4.json`, oldest first, then at run 5 again, and the table fills out and the line starts naming the regression.

```python
def trend_line(rows):
    oldest = rows[0]
    newest = rows[-1]
    best_name = CATEGORIES[0]
    best_growth = None
    for col, name in enumerate(CATEGORIES, start=1):
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
    return ("grew the most: " + best_name + " " + f"{best_growth:+d}"
            + "  pass rate " + f"{old_rate:.2f}" + " -> " + f"{new_rate:.2f}"
            + "  getting worse: " + worse)


print("== step 7: the trend across the history ==")
print("runs in history: " + str(len(HISTORY)))
print(trend_line(HISTORY))
print()
```

```text
== step 7: the trend across the history ==
runs in history: 5
grew the most: wrong_shape +7  pass rate 1.00 -> 0.50  getting worse: yes
```
