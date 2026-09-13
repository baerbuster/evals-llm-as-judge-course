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

## Run the rules against your own labels

A rule earns your trust when you run it over a whole run and check its verdicts against your own judgment. So read run 5 yourself, poem by poem, and write down pass or fail for every rule. That is a human label: the pass or fail a person gave an output by hand. Treat those labels as ground truth, the correct answer that everything else is measured against, and call the outputs that have them your labeled set. Run 5 comes to you already labeled, along with all five saved runs. Data shipped so a run can be repeated exactly is a fixture, and that is what these are.

Then run the rules and set the two columns side by side. Agreement means the rule's verdict matches your label for that output. Disagreement means it does not. Run 5, output 12, is an agreement. The situation ended with "I have never been so glad to see a jetway," and the poem's second line is that sentence word for word. The no_copy rule fails it, you labeled it fail, and the two of you are done.

The disagreements are more useful. Run 5, output 8, has this second line:

"and the small tree still turns on its string in the car,"

Twelve words exactly. The line_length rule says under twelve, so it fails. You labeled it pass, because it reads fine. Output 15's last line does the same thing: "and the days ahead are rising up gold and full of it," twelve again, rule fail, label pass.

Nothing is broken here. You found the edge of your own rule, which is the only place a rule can be wrong. Decide it once: either twelve words is acceptable and the rule becomes twelve or fewer, or twelve is too long and those two labels were generous. Both answers are defensible. What is not defensible is leaving it undecided, because then your grader and your judgment drift apart without either of you noticing.

You can now run your rules over a set of outputs and list every case where the rule's verdict disagrees with your own label. The list is short, it is specific, and each line on it is a decision you get to make once.

## Sort every failure into a named bucket

A pass rate tells you how much broke. It does not tell you what broke. The pass rate is the share of outputs that passed, a number between 0 and 1, and on its own it is one of the least actionable numbers you can look at. Reading each failure and sorting it into a named bucket is what turns it into something you can act on. That bucket is a failure category, and the reading-and-sorting is error analysis.

For the poem tool, three categories cover everything the code rules can catch. A failure goes to wrong_shape if shape or line_length failed, to preamble if no_preamble failed, and to copied if no_copy failed.

Start with the easy one. Run 5, output 11, for the situation about someone keying a car in the grocery store lot, begins:

"Here is your poem: / Something was taken from you in a small way, / a hand in the dark that did not wait to answer, / and the hot thing rising that has nowhere to go."

One rule failed, no_preamble, so this output goes in the preamble bucket. Nothing to decide.

Run 5, output 0, is the case that needs a decision. It opens with "Here is a poem for you:" and then runs four more lines, so it fails no_preamble and it fails shape, five lines where four were expected. Two rules, one output, and a category has to hold it. Pick an order for your rules and put the failure in the bucket for the first one it failed. With shape first, output 0 lands in wrong_shape. The order itself barely matters. What matters is that it never changes, so the same failure lands in the same bucket today and next month, and the counts you compare are counts of the same thing.

Without the buckets you are left saying "half of run 5 failed" and staring at it. With them you can say which half, and go look at the part of your prompt that produces opening lines. Some things you care about have no rule behind them yet, so their buckets come later.

This section gave you the categories. The next one gives you the row of numbers they go into, and the history that makes the row mean something.

## One row per run, forever

One run's pass rate is a number with nothing to compare it to. Two runs can be a blip. What answers your original question is a history: one row per run, written once, kept forever. Make it a table with the run's name first, one column per failure category, and the overall pass rate at the end, oldest run first. Keep it as a CSV so you can open it in a spreadsheet or plot it later without touching the grader.

Every time your grader runs, it appends one row and then reads the whole file back. It never recomputes an old row. The row is labeled by the saved run's name, not by the clock, so the same run produces the same row on anyone's machine, and a row written last month still says what you saw last month.

Now read the columns down instead of across. For the poem tool, runs 1 through 4 have zeros in every bucket and a pass rate of 1.00, 1.00, 1.00, 1.00. Run 5 has numbers in wrong_shape and in preamble, and a pass rate well below the four before it. The trend is the direction a number moves across runs, oldest to newest, and this one moves one way. A regression is the tool getting worse than it used to be. You are looking at one, and the buckets say where: two categories that were empty for four straight runs are not empty now, so whatever changed between run 4 and run 5 is the thing to go read.

That is a different sentence from "it feels worse lately." It has a run number in it and a category name in it, and it survives being repeated to someone who was not there.

You can now sort every failure into a named bucket, append each run to a history of every past run, and read a run-by-category table to say whether your tool is getting worse and in which bucket.

What the table cannot tell you yet is whether run 5's Rufus poem, which never mentions Rufus or his collar, is still about the person's dog at all. No rule counts that. Lesson 2 is how you grade it anyway.
