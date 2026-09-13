# Writeup

## What I cut, and why

Most of the topic. Evals and LLM-as-judge is far bigger than ninety minutes, so I kept only what the capstone needs and left the rest on the floor.

Sample size and significance went first. Twenty outputs in one run cannot separate a real regression from noise, but the statistics that would say so need a lesson of their own, and the question the learner walked in with, which criterion and which run, is answerable without them.

Multiple labelers and inter-annotator agreement went next. One person's labels are the ground truth here, because the learner is one person who shipped one feature.

Scored rubrics and pairwise comparison went too. Precision and recall need a binary positive class, and binary is what the capstone prints.

Judge ensembles, what judging costs at volume, and wiring the grader into CI all sit after you trust one judge. Earning that trust is where this course stops.

## Where it is weakest

This was really fun, and I came out of it with more ideas than I had time for. First among them: more evals, specifically around timing. Right now the build-alongs only meet the twenty-minute requirement if the learner is copy/pasting the code rather than typing every line of it. With more time I would build a timing eval first and get both build-alongs comfortably under twenty.

I also got to try something new on the prompt engineering side that I had been curious about for a while. I applied an MVC paradigm to the prompting and I think the model responded really well to it. I will be running some tests on that technique shortly for sure.
