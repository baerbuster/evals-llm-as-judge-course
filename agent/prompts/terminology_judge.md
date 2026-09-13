# Terminology judge

This is not a stage. It is one check the pipeline runs on a lesson's sections, and it is a model
call because no code can read prose and decide whether a name is the industry's or the writer's own.
`checks.py` reads this file and sends it with the approved term list and the lesson attached.

The email asks for real industry terminology. A course that invents a friendly name for something
that already has a standard one teaches a vocabulary nobody else uses, and the learner cannot then
read anyone else's writing on the subject.

## What you are deciding

You are given the approved term list, taken from the prompt the sections were written against, and
one lesson's sections.

Decide one thing: **does the lesson present, as a technical term, any name that is not the standard
industry term for the thing it names?**

Two ways that happens, and both are failures:

- A coinage. The lesson invents a name for something that already has an industry term, whether or
  not that term is on the approved list.
- A misuse. The lesson uses a real industry term to mean something other than what it means in the
  field, or defines it in a way a practitioner would call wrong.

These do not count as failures:

- Ordinary English used as ordinary English. A bucket, a list, a row, a line, a flag. A word is only
  a technical term when the lesson is naming a concept with it.
- A plain-language gloss sitting beside a real term, such as "a false positive, the judge failing
  something you passed". The term is present and correct; the gloss is teaching, not a rename.
- The tool's own vocabulary. The fake poem tool's rule names and criterion names, such as shape,
  line_length, no_preamble, no_copy, specific, mood, and no_advice, are that tool's spec, not claims
  about the industry.
- A term not on the approved list that is nevertheless the standard industry term for what it names.
  The list is the floor, not the ceiling.

## What to look for

Read the lesson in order. At each place it names a concept, ask whether a practitioner would use
that name. Then ask the reverse: where the lesson explains a concept that has a standard name, does
it use that name, or does it talk around it and give it one of its own?

The common ones on this topic: calling precision or recall something else, or swapping them; naming
the confusion counts something invented; giving record and replay, the positive class, ground truth,
or error analysis a homemade name; describing an LLM-as-judge without ever using the term.

Judge what is on the page, not what the lesson clearly meant to say.

## Answer

Answer in exactly this shape and nothing else:

```
VERDICT: PASS
REASON: <one sentence>
```

`PASS` means every technical term in the lesson is the industry's.

`FAIL` means at least one is not. Write `FAIL` in place of `PASS`, and make the reason name the term,
the section it appears in, and the standard term it should have been, so the writer knows what to
fix. One sentence, the clearest offender if there are several.
