# Record and Replay

Topic: Evals and LLM-as-Judge
Learner: someone who shipped an AI feature and cannot tell if it is getting worse
Capstone: a working grader printing real precision and recall

This file fixes how the judge in build-along 2 gets its answers from the model in live mode, saves them, and reads them back in replay mode. The generator prompt for build-along 2 and the README follow it. Build-along 1 has no model calls and no modes.

## Modes

- **Replay** is the default. The bare command needs no API key and makes no API call.
- **Live** is turned on with a `--live` flag. It needs the API key in the environment and calls the model.
- The first line printed is the mode: `mode: replay` or `mode: live`.

The default is replay because the reviewer has no key and the email requires the run to be free. The build-along says in one line that a real project would flip the default.

## What live saves

Every model reply is saved raw, exactly as it came back, before any parsing. One file per reply, in `build/judge/responses/`.

The file name is built from the three things that identify the question: the saved run's name, the output's index in that run, and the criterion. Example:

```
build/judge/responses/run3_output12_politeness.txt
```

Live overwrites an existing file with the same name.

## What replay does

For each output and criterion, replay builds the same file name, opens it, and hands the raw text to the same parser live uses. The parser is the only code that turns a reply into a pass/fail verdict and reason, and it runs in both modes, so live and replay produce identical verdicts, false positive and false negative lists, precision, and recall.

If the file does not exist, replay stops immediately and prints the missing file's path. It never falls back to a live call. This should never happen from a fresh unzip; it can only happen if a criterion, saved run, or fixture changed after recording, or a file was left out of the zip.

## What is shipped

Every reply file for every saved run, output, and criterion, recorded in one live run during plan step 22. The reviewer's replay run uses them unchanged.
