<!-- plain-style: allow-file=banned-word reason: this file names the doc types that discuss those words -->

# Doc types and rule strength

Find your doc type, read the row, then write. If a document mixes types, split
it or apply the stricter row to the stricter part. A README with an install
procedure gets Google tone in the prose and full STE in the numbered steps.

| Doc type | Reader | Reader's state | STE | Orwell | Google | Shape |
|----------|--------|----------------|-----|--------|--------|-------|
| Runbook, incident procedure | On-call engineer | Under pressure, possibly at 03:00, maybe new to the system | Full | Full | Formatting only | Numbered steps, one action each, expected result after each step, rollback at the end |
| Install or setup procedure | New user | Wants it working, not explained | Full | Full | Full | Prerequisites, numbered steps, verification command |
| README | Someone deciding whether to use this | Skimming, 30 seconds of patience | Light | Full | Full | What it is, how it works, quick start, key files, where to go next |
| Tutorial, how-to | Learner following along | Typing what you write | Full in steps, light in prose | Full | Full | Goal first, then steps, then what they can now do |
| API or CLI reference | Developer with a specific question | Scanning for one entry | Light | Full | Full | Fixed structure per entry, same order every time, no prose between entries |
| Design doc | Reviewer, future maintainer | Reading to disagree | Light | Full | Tone only | Problem, constraints, options, decision, consequences |
| ADR | Future maintainer asking "why is it like this?" | Reading one page in isolation | Light | Full | Tone only | Context, decision, status, consequences. Present tense, no history of the meeting |
| Changelog | User upgrading | Looking for what breaks | Light | Full | Full | Grouped by change type, breaking changes first, one line each |
| Code comment, docstring | The next person to edit this code | Already reading the code | Light | Full | Naming only | State intent or constraint, not restate the code |
| Skill file, agent prompt, instruction file | A model, then the human maintaining it | Reads every word, follows reasons better than commands | Light | Full | Tone only | Trigger first, then the workflow in order, then the rules. Give the reason for a rule instead of raising your voice |

## What the strength columns mean

**Full STE** means every rule in `references/ste.md` applies: approved word
senses, three-noun limit, one instruction per step, condition before action,
warning before the step it guards. Use it where a misread sentence causes an
outage or a data loss.

**Light STE** means the sentence-level rules apply but the vocabulary rules
relax. Keep sentences short, keep one term per concept, keep the noun clusters
small. You may use a precise technical word that STE would reject, if the
reader knows it and no plain word is as exact.

**Full Orwell** applies everywhere and has no light version. Orwell's rules are
about not writing on autopilot, and there is no document where autopilot helps.

**Google full** means second person, present tense, sentence-case headings,
code formatting for code, and the link and list conventions in
`references/google-style.md`. **Tone only** means keep the voice but drop the
formatting conventions where the document has its own template, as ADRs do.

## Reasoning is allowed in design docs and ADRs

STE forbids most subordinate clauses because a procedure step must be read
once and obeyed. A design doc is the opposite: the reader must follow why one
option beat another. Write the reasoning, in short sentences, one step of the
argument per sentence. Short sentences and a real argument are compatible;
`references/examples.md` shows a pair.

## Generated documents

If a tool writes the file, do not edit the file. Edit whatever the tool reads,
then run the tool again. That is usually a docstring, a schema, a template, or
a page in another system.

Check before you start. Look for a header comment saying "generated", a
frontmatter field naming a source, or the file's path in a generator's config.
