# Breaking Points

Topic: Evals and LLM-as-Judge
Learner: someone who shipped an AI feature and cannot tell if it is getting worse
Capstone: a working grader printing real precision and recall

Each breaking point is a place the learner gets stuck or nods along without understanding.

### 1. The gap between intuition and evidence

The learner has "correct" as a feeling, but how can they apply that? They have the feeling that their AI tool is producing worse output than it used to, but they can't prove it. How can they formulate their intuition into a rule they could hand to someone else? They cannot start building a grader because they cannot say what it is grading.

### 2. What to do with raw evidence, and what to do when it disagrees with your intuition

The learner has formulated their intuitions into pass/fail checks, but how do they actually use that? They built the rules for a grader, but how can they utilize these rules? And as they begin to do that, they learn their rules might not have been as consistent as they thought, it fails things they would pass and passes things they would fail.

### 3. What does the final grade mean

The learner sees the pass rate and stops. 17% failing, great. What does that mean? What can they do with this percentage to finally find out whether their AI tool is getting worse or not? Until they read each failure and sort it into a bucket, they cannot say what got worse or where to look. Everyone nods at "look at your failures" and almost nobody does it, because it is manual.

### 4. Handling qualitative data with LLMs as judge

The learner has a working grader, but it cannot answer questions with subjective or qualitative criteria like whether a response was "polite". They need some kind of system that can grade their responses on a qualitative level, without being purely quantitative.

### 5. How to judge the judge?

They've instituted an LLM-as-judge to grade more qualitative aspects of their tool's outputs. Excellent. But if the original tool was an AI that could produce errors, who's to say their judge isn't making the same mistake? What metrics can they use to check the accuracy of their grading AI, before it is put in charge of verifying the accuracy of their product AI?

### 6. Error analysis on the judge: reading where it disagreed with the human

They've now received some data about the accuracy of their LLM-as-judge, but what do they do with it? Where the judge disagreed with the human, was it flagging good outputs or missing bad ones? What is the difference between those two and what can the learner do about each of them?
