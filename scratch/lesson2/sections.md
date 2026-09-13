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

## Two numbers: precision and recall

The four counts collapse into two numbers, and each answers a different question about the judge.

Precision is, of the outputs the judge failed, the share you also failed. True positives divided by true positives plus false positives. Recall is, of the outputs you failed, the share the judge caught. True positives divided by true positives plus false negatives.

Work it on specific in run 5. You failed 11 of the 20 poems on that criterion. Suppose the judge fails 10 poems, and 9 of them are poems you also failed. That is 9 true positives, 1 false positive, 2 false negatives, and 8 true negatives. Precision is 9 divided by 10, or 0.90. Recall is 9 divided by 11, or 0.82.

Now say them in plain words. Precision 0.90: when this judge fails a poem, nine times out of ten you would have failed it too, so its complaints are worth your attention. Recall 0.82: of the eleven poems you consider bad, it finds nine, and two go past unremarked.

Recall is the number that speaks to the question you walked in with. A judge with low recall lets a regression stay invisible. The poems drift, the judge keeps passing them, and the specific column in your table sits flat while the tool gets worse. Precision protects something else: your time, and your willingness to keep reading what the grader tells you.

Here is why you keep both. Suppose you rewrite the judge prompt to be harsher, and now it fails 18 of the 20 poems. It catches all 11 of yours, so recall is 1.00, a perfect score. Precision is 11 divided by 18, or 0.61. Seven of its complaints are about poems you were happy with, including output 4 and output 14. That judge has stopped measuring the tool and started measuring its own strictness. Either number alone can be pushed to look good. The pair cannot.

Recompute both on the same labeled set every time you touch the judge prompt, and write down what they were before. They are cheap to recompute, because the labels are fixtures and do not move.

You can now compute the judge's precision and recall against a set of human labels, and say in one sentence how much of what the judge reports you should believe.

## Too strict and too lenient need different fixes

Precision and recall tell you how much to trust the judge. To improve it, go back to the two lists behind those numbers and read them separately, each disagreement showing the judge's reason next to your label. False positives and false negatives are two different problems and they pull the judge prompt in opposite directions.

Start with the false positive. Output 14, Priya and the empty chair, where you said specific pass and the judge said FAIL because the poem never names Priya or Auckland. The judge's bar sits higher than yours. It wants a proper noun; you accept any concrete detail from the situation. That is a definition problem, not a model problem, and the fix is in your own sentence: say what counts as a concrete detail, and put this poem in the judge prompt as an example that passes. A false positive fix narrows the judge's idea of failure.

Now the false negative. Output 6, the blue enamel pan, where you said specific fail and the judge said PASS because the poem names the pan. The judge saw something concrete and stopped. It never asked where the detail came from. The fix is to name the miss out loud in the prompt: the detail has to come from the situation, not from the poem's own invention, and the grandmother and the smoke alarm are what the situation gave it. A false negative fix widens the judge's idea of failure.

Because the two fixes push opposite ways, one can undo the other. Tighten the prompt to catch output 6 and you may start failing output 14. This is why you rerun the judge on the same labeled set after every edit and compare the pair of numbers to what they were. Recall went up, and did precision hold? That question is answerable in seconds once the counts are printing.

A judge you have measured and adjusted is a judge whose verdicts you can put in front of someone else. It is still a model and it can still be wrong, but now you know roughly how often and in which direction, and you can say so out loud.

You can now separate the judge's false positives from its false negatives and name a different fix for each. The last section puts this judge to work on the question you came here with.

## A second table, and the answer you came for

The judge's verdicts go into a history table shaped exactly like the one from lesson 1. One row per run, labeled by the saved run's name, one column per criterion, pass rate at the end, oldest first, appended once per run and kept as CSV. This is a second file. The lesson 1 table stays as it is, and no row already written is ever recomputed.

What is new is the columns. The four code rules keep theirs, and specific, mood, and no_advice join them, with three more failure categories to sort their failures into: generic when specific fails, wrong_mood when mood fails, advice when no_advice fails.

Print the judge's confusion counts, precision, and recall directly above the table. Anyone reading a judge column, including you in six months, needs to know how much that column is worth. A column fed by a judge with recall 0.82 can move for two reasons: the tool changed, or the judge missed a few. Having the number in front of you keeps you from over-reading a small wobble, and tells you when a large move is real.

Now read the table down the columns. The specific column is nearly clean in runs 1 and 2, climbs in run 3 where the prompt was trimmed, climbs again in run 4, and stays high in run 5. The no_preamble column is clean for four straight runs and then breaks open in run 5. The advice column shows its first failures in run 4. The overall pass rate falls run over run. The two criteria trending down the most are specific and no_preamble, and the tool is getting worse overall.

That sentence has a run number in it, a criterion name in it, and a trust number behind it. It points at two separate causes: the trimmed prompt cost the poems their details, and whatever changed before run 5 brought the preambles back.

You can now separate the judge's false positives from its false negatives, name a different fix for each, and append the judge's verdicts to a run-by-criterion history table that says whether the tool is getting worse and where. You walked in with a hunch. You are leaving as the person the rest of the team asks.
