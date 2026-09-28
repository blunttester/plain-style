# plain-style

An agent skill that makes an AI write documentation you can check, plus a
zero-dependency linter that proves it did.

<!-- plain-style: allow=banned-word reason: the paragraph quotes the words it bans -->
Default model prose rotates synonyms, stacks clauses, hedges, opens with a
preamble, closes with a summary, and reaches for "leverage" and "robust". The
reader pays for all of it. This skill removes the habit and gives you a command
that fails a build when the habit returns.

## What it is

- `SKILL.md` holds the workflow and the core rules, short enough to keep in
  mind while you draft.
- `references/` holds six files that load only when the situation needs them.
  They cover Orwell's six rules, Simplified Technical English, a Google style
  digest, a doc-type table, the banned word list, and worked examples.
- `scripts/check_docs.py` is a Markdown prose linter. It needs Python 3.9 or
  later, and the standard library only.

## Install

The package is not on the npm registry. `npx` fetches the installer from
GitHub instead, so you need Node.js 18 or later and `git`:

```bash
npx github:blunttester/plain-style install            # into this repository
npx github:blunttester/plain-style install --global   # for every project
npx github:blunttester/plain-style where              # show where it would land
npx github:blunttester/plain-style uninstall
```

After it copies the files, the installer looks for Python 3.9 or later. It
tries `python3`, `python`, and `py -3`, in that order. It then prints the
full command to run the checker, with the path to the installed copy. If it
finds no Python, it still installs the skill and prints a warning.

Without Node.js, clone the repository and copy the skill directory:

```bash
git clone https://github.com/blunttester/plain-style.git
mkdir -p your-repo/.claude/skills
cp -r plain-style/.claude/skills/plain-style your-repo/.claude/skills/
```

Copy the whole directory. The checker reads `references/banned.md`, so
`scripts/` alone reports every file as clean.

Both Claude Code and GitHub Copilot read `.claude/skills/` in the repository,
so a local install serves both. A global install writes two directories:

| Agent | Global path |
|-------|-------------|
| Claude Code | `~/.claude/skills/plain-style` |
| GitHub Copilot | `~/.agents/skills/plain-style` |

The installer refuses to copy a partial skill. `scripts/` without
`references/` would load no banned words and report a clean file every time.

## Use it without an agent

The linter runs on its own:

```bash
python3 .claude/skills/plain-style/scripts/check_docs.py docs/*.md
python3 .claude/skills/plain-style/scripts/check_docs.py docs/*.md --json
```

On Windows, if `python3` is missing, use `py` in its place.

Exit codes: `0` when there are no errors, `1` when there are, `2` when the
checker cannot read a file. Wire it into a pre-commit hook or a CI job on that basis.

### What it checks

| Rule | Level | What sets it off |
|------|-------|------------------|
| `long-sentence` | error | Over 20 words in a numbered step, over 25 elsewhere |
| `banned-word` | error | A word or phrase listed in `references/banned.md` |
| `em-dash` | error | More em dashes than one per 200 words in a section |
| `paragraph-length` | error | Over 6 sentences in a paragraph |
| `glossary-synonym` | error | A second name for a concept your glossary block names once |
| `passive-voice` | hint | A form of "be" and a past participle |

Hints are off by default and never set the exit code. Pass `--hints` to see
them. The linter skips fenced code, inline code, URLs, HTML, and frontmatter.

### Waivers

Sometimes the sentence is right and the rule is wrong. Keep the sentence and
record why:

```markdown
<!-- plain-style: allow=long-sentence reason: splitting the warning separates condition from action -->
```

A line waiver covers the block that follows it. `allow-file=` covers the whole
file. Waived findings never set the exit code.

### Glossary

The linter cannot guess that "import job" and "ingestion cycle" mean the same
thing. Declare it:

```markdown
<!-- plain-style:glossary
import job: ingestion cycle, load pass, transfer run
-->
```

The left side is the term to keep. The right side lists the names the document
must not use for that concept.

## What it does not do

- It does not check layout. Run a Markdown linter such as `pymarkdown` for
  heading levels and list markers. The two do not overlap.
- It does not read source files. For docstrings and comments, apply the rules
  by hand.
- It does not fix anything. You decide whether the rule or the sentence is
  wrong.
- It does not govern documentation that a tool generates, such as API
  reference built from docstrings. Edit the docstring, not the built page.

## Develop

```bash
uv run pytest                           # 48 tests
npm run check                           # the skill checks itself
```

CI runs both on every push. The skill has to pass its own linter, or it is not
worth shipping.

## Sources

- Orwell, "Politics and the English Language", 1946. Public domain in the UK
  and the EU.
- ASD-STE100 Simplified Technical English. The standard is licensed and is
  **not** reproduced here. `references/ste.md` states the rules as practice, in
  its own words, and reproduces no dictionary entry.
- [Google developer documentation style guide](https://developers.google.com/style),
  licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
  `references/google-style.md` is a digest, not a copy.

## License

MIT. See [LICENSE](LICENSE).
