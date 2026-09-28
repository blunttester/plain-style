---
name: plain-style
description: Write and edit documentation in plain, checkable English. Use this skill whenever you create or change a README, runbook, procedure, ADR, design doc, API reference, changelog, contributing guide, or a docstring or comment that explains behaviour or intent. Use it when a request contains "document", "write docs", "write a README", "write a runbook", "add docs", "clean up the docs", or "improve this doc", and whenever you are about to write more than one paragraph of prose into a Markdown file. If you are unsure whether a file counts as documentation, assume it does and use the skill.
---

# plain-style

A reader opens a document to get a fact and act on it. Every word that carries
no fact costs the reader time. This skill removes those words.

Three sources, one layer each:

- **Orwell's six rules** (*Politics and the English Language*, 1946) set the
  attitude and settle ties.
- **ASD-STE100 Simplified Technical English** gives the sentence-level rules.
- **The Google developer documentation style guide** gives tone and formatting.

## Workflow

1. **Name the doc type and the reader.** Open `references/doc-types.md` and read
   the row for that type. The row says how hard to apply each layer. A runbook
   and a design doc need different discipline, and guessing wastes a draft.
2. **Draft.** Get the facts down in order. Do not polish yet.
3. **Revise against the core rules below.** Most of the value sits here. A first
   draft defaults to the habits this skill exists to correct.
4. **Run the checker.**

   ```bash
   python3 scripts/check_docs.py path/to/file.md
   ```

   If `python3` is missing, try `python` or, on Windows, `py`.

   Fix what it reports. If the text is right and the rule is wrong, keep the
   text, add a waiver comment, and give the reason on one line:

   ```markdown
   <!-- plain-style: allow=long-sentence reason: the SQL predicate breaks if split -->
   ```

   Orwell's rule 6 allows this. Volume of waivers shows you skipped step 3.

## Core rules

- **One term for one concept, for the whole document.** Define it once, then
  repeat it. Synonyms read as variety to the writer and as new concepts to the
  reader.
- **Short sentences.** Aim for 20 words in a procedure step, 25 elsewhere. One
  idea per sentence; if you need two, write two sentences.
- **One instruction per step, in the imperative, condition before action.**
  Write "If the job is still running, stop it", not "Stop the job, if running".
  The reader must know whether the step applies before doing it.
- **Active voice, with the actor named.** "The build script overwrites
  `dist/`", not "`dist/` is overwritten". Passive voice hides who acts, and the
  reader usually needs to know who acts.
- **Plain, common words.** Prefer the short Anglo-Saxon word to the Latinate
  one. `references/banned.md` holds the list and the replacements.
- **Cut the opening paragraph, the closing summary, the throat-clearing, and
  the hedge.** Start with the fact. State uncertainty only where it is real,
  and then say what is uncertain and why.
- **Prose for explanation, lists for steps and parallel items.** A bulleted
  argument drops the connective words that carry the reasoning.

## Precedence

When rules conflict: safety and accuracy first, then STE in procedures, then
Orwell, then Google. Break any of them rather than write something barbarous.

## Scope

This skill governs documentation files you write or edit. It overrides any
terse style active in the session, such as a caveman mode. Those styles govern
chat replies, not files that outlive the session.

It does not govern:

- **Generated files.** A tool builds some documentation from somewhere else.
  Examples: API reference from docstrings, a page from an OpenAPI schema,
  module docs from Terraform. Editing the built copy loses the edit the next
  time the tool runs. Edit the docstring or the schema instead.
- **Commit messages.** A separate skill owns those.
- **Chat and issue replies.**

## References

Open a reference file when you reach the situation in the right column. Each
one loads only when needed, which is why `SKILL.md` stays short.

| File | Open it when |
|------|--------------|
| `references/doc-types.md` | Always, at step 1. Maps doc type to reader and rule strength. |
| `references/ste.md` | Writing a procedure, runbook, warning, or any numbered steps. |
| `references/orwell.md` | A sentence feels stale or inflated and you cannot say why. |
| `references/google-style.md` | Formatting a heading, list, link, code sample, or UI element; choosing tone. |
| `references/banned.md` | The checker flags a word, or a phrase sounds like filler. |
| `references/examples.md` | You want the target voice before drafting. |

## Checker notes

- The checker reads Markdown. For docstrings and code comments, apply the core
  rules by hand; the same rules hold, the tool does not parse them.
- It complements a Markdown linter such as `pymarkdown`. The linter checks
  layout, this checks the sentences. Run both; they do not overlap.
- Passive voice is a hint. Hints are off by default and never set a non-zero
  exit code. Pass `--hints` to see them. A stdlib heuristic cannot tell a
  passive clause from an adjective, so you judge it.
- Pass `--json` when a hook or a CI job reads the output.
