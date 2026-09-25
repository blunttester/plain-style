<!-- plain-style: allow-file=banned-word,long-sentence,passive-voice reason: shows the patterns it tells you to avoid -->

# Simplified Technical English, as applied here

ASD-STE100 was written so that a maintenance technician reading a second
language can act on a procedure without misreading it. Software runbooks have
the same reader: tired, unfamiliar with the system, needing to act correctly the
first time.

**This file is practice, not the standard.** The STE dictionary is licensed and
is not reproduced here. Where a rule below states a number, treat the number as
a working limit for this skill rather than a quotation. Where you need the
exact standard, consult ASD-STE100 itself.

## 1. One word, one meaning, one part of speech

Pick one sense for a word and keep it for the whole document. Do not use a noun
as a verb, or a verb as a noun, if a plain alternative exists.

| Word | Use it to mean | Do not use it to mean |
|------|----------------|-----------------------|
| run | start a program or command | a single execution (use "a nightly run" only if you define it) |
| check | look at something to find its state | stop something, restrain |
| stop | end a running process | a stopping point |
| start | begin a process | a beginning |
| set | give a value to a setting | a group of things |
| close | shut a connection or file | near |
| follow | do the steps in order | come after in time |
| release | publish a version | let go |
| fail | not complete correctly | a failure event (use "failure") |
| build | compile or assemble | a built artefact (use "artefact" or name it) |

**No verbing.** Write "send a request", not "request it". Write "make a
deployment" or "deploy", not "do a deploy".

## 2. Short list of verbs that carry most software procedures

Use these in the imperative. They are common, unambiguous, and have one sense
each in this context.

add, apply, build, cancel, change, check, close, connect, copy, create, delete,
deploy, disable, enable, enter, examine, export, fetch, find, install, keep,
list, load, lock, log in, log out, move, open, push, read, release, remove,
rename, replace, restart, restore, retry, roll back, run, save, select, send,
set, show, start, stop, test, type, update, upgrade, verify, wait, write.

If you need a verb that is not here, use it, but use it the same way every time.

## 3. Noun clusters: three nouns maximum

A long noun cluster forces the reader to guess which noun modifies which.

> Before: production database connection pool exhaustion alert threshold

> After: the alert threshold for pool exhaustion in the production database

Insert the prepositions the cluster removed. The sentence gets longer and the
meaning gets fixed.

## 4. Verb forms

- Use the active voice. Name the actor.
- Use the simple present for behaviour: "The importer writes to `tmp/`".
- Use the imperative for instructions: "Stop the service".
- Use the past only for events that happened: "The deploy failed at 14:20".
- Do not use `-ing` as the main verb of a sentence. Write "The job retries three
  times", not "The job is retrying three times", unless you mean right now.
- Avoid stacked auxiliaries: "should be able to be restarted" means "you can
  restart".

## 5. Sentence length

Keep a procedure step to about 20 words. Keep other sentences to about 25. One
idea per sentence. If a sentence contains "and" joining two independent
clauses, it is usually two sentences.

> Before: If the deploy failed and the pods are still in CrashLoopBackOff, you
> should roll back to the previous release, which you can find in the release
> history, and then check the logs.

> After: Check the pod state. If the pods are in `CrashLoopBackOff`, roll back
> to the previous release. Find the previous release in the release history.
> Then read the logs of the rolled-back pods.

## 6. Procedures

- One instruction per step. Two actions in one step means the reader can do one
  and believe the step is done.
- Start the step with the verb.
- Put the condition before the action: "If the queue is empty, stop the
  consumer". The reader must know whether the step applies before acting.
- State the expected result when the reader cannot see it: "The command prints
  `ok`. If it prints anything else, go to step 7."
- Number the steps. Never nest a numbered procedure inside a numbered step;
  make it a separate procedure and link to it.
- Say what the reader needs before step 1: access, credentials, tools, state.

## 7. Descriptive text

Descriptive text explains how something works and is read once, at leisure.

- The 25-word limit applies, but you may use a subordinate clause to carry a
  cause or a condition.
- Paragraphs: one topic each, six sentences maximum.
- Keep the same term for the same concept as the procedures use. A reader who
  learns "import job" in the overview must not meet "ingestion cycle" in the
  runbook.

## 8. Warnings and cautions

- Put the warning **before** the step it applies to. A warning after the step is
  a post-mortem.
- Start with the command or the condition, not with the consequence.
- State the consequence in plain words, once.
- Use one warning per hazard.

> Before: Data loss may be experienced if care is not taken when this command is
> run against production.

> After:
>
> **Warning: this command deletes all rows in `events`. There is no undo. Make
> sure you are connected to staging before you run it.**

"Make sure" replaces "ensure" throughout. It is two common words and it tells
the reader to do something, which is what a warning is for.

## 9. Paragraphs and structure

- Put the topic in the first sentence of the paragraph.
- Six sentences maximum per paragraph.
- Keep related instructions together; do not separate a step from its warning
  with a page break or an admonition block.

## When STE and precision collide

STE exists to prevent misreading, not to ban technical words. If the exact word
is `idempotent` and the reader is an engineer, write `idempotent` and define it
once. Do not paraphrase a precise term into three vague ones.
