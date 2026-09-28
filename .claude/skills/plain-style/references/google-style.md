<!-- plain-style: allow-file=banned-word,passive-voice reason: quotes the patterns it rules out -->

# Google developer documentation style, digest

The full guide is large. This digest covers what comes up in almost every
document. Open the full guide when you hit a case this file does not answer.

## Voice and tone

- **Second person.** Address the reader as "you". Write "you can configure the
  importer", not "the user can configure the importer" or "we configure".
- **"We" only for the team making a decision**, mostly in ADRs and design docs:
  "We chose Postgres because...". Never "we" meaning the reader.
- **Present tense.** "The command returns 0", not "the command will return 0".
  Future tense implies a delay that does not exist.
- **Conversational, not chatty.** Contractions are fine. Exclamation marks and
  jokes are not; they age badly and translate worse.
- **No anthropomorphism.** A service does not "want" or "think". It waits,
  retries, fails.

## Headings

- Sentence case: "Configure the importer", not "Configure The Importer".
- Task headings use the imperative or a gerund. Pick one per document: every
  heading is "Configure the importer", or every heading is "Configuring the
  importer". Do not mix.
- One `#` per file, as the title. Do not skip levels.
- The heading must describe the content under it well enough to be read alone
  in a table of contents.
- No punctuation at the end of a heading.

## Lists

- Numbered lists for sequence. Bulleted lists for sets with no order.
- Start each item with a capital and keep the items parallel: all noun phrases,
  or all imperative sentences, not a mix.
- Full stop at the end of each item when the items are sentences; no full stop
  when they are short phrases. Be consistent within the list.
- If a list has two items and no order, consider a sentence instead.
- Do not use a list to avoid writing the connective tissue of an argument.

## Code and UI

- Use backticks for code, commands, file paths, flags, environment variables,
  and literal values: `dist/`, `--strict`, `NULL`.
- Do not use backticks for a product name or a concept: MkDocs, not `MkDocs`.
- Give code blocks a language so the syntax highlights: ` ```bash `.
- Show a command the reader can copy, without the shell prompt character, so
  copying does not pick up the `$`.
- Bold the literal text of a UI element: click **Save**.
- Do not tell the reader where an element sits on the screen; layouts change.
  Name the element.

## Links

- The link text says where the link goes: see
  [the contributing guide](../CONTRIBUTING.md). Never "click here" or "this page".
- Prefer relative links inside a repository so they survive a move.
- Say when a link leaves the document set, and say what the reader will find.

## Punctuation

- Use a full stop, a colon, or brackets instead of an em dash. An em dash
  usually joins two sentences that read better apart.
- Keep at most one em dash per section of about 200 words. Use it where the
  break carries weight: "Git history is the archive — never move superseded
  content to an archive directory."
- Use the serial comma.
- Avoid semicolons in procedures. They join two instructions into one step.

## Words and numbers

- Spell out zero to nine in prose; use numerals from 10 up. Always use numerals
  with units: `3 GB`, `5 s`.
- Avoid "please" in instructions. It adds a syllable and no information.
- Avoid "simply", "just", "easy", "obviously". If the step is easy the reader
  finds out; if it is not, the word blames them.
- Avoid directional words such as "above" and "below". Link to the section.
- Write dates as `2026-09-25` or "25 September 2026", never `09/25/26`.

## Accessibility and inclusion

- Alt text describes the information in the image, not the image.
- Do not use colour alone to carry meaning.
- Avoid ableist idioms such as "sanity check"; write "check" or "validation".
- Use "allowlist" and "blocklist", "primary" and "replica".

## Where Google and STE disagree

Google allows a friendlier register and longer sentences than STE. In a
procedure, STE wins: cut the sentence. In a README or a tutorial, Google wins:
keep the sentence readable and human. `references/doc-types.md` says which
applies where.
