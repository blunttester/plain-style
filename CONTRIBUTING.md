# Contributing

## Run the checks

```bash
uv run pytest     # the test suite
npm run check     # the skill checks its own documentation
```

[uv](https://docs.astral.sh/uv/) reads `pyproject.toml`, installs pytest into a
local environment, and runs it. You need no other setup. CI runs the same
command on Python 3.9 to 3.13, and installs the packed tarball on
Linux, macOS, and Windows. Both checks have to pass before a merge.

## Rules for this repository

- **The linter stays dependency free.** `check_docs.py` runs inside other
  people's repositories. It imports the standard library only and supports
  Python 3.9 or later. Apple ships Python 3.9 with macOS, so do not raise
  the floor without a reason. A test asserts the import list. The test suite
  may use pytest, because tests never ship.
- **`references/banned.md` is the only word list.** The script parses that file
  at run time. Never add a second copy inside the code.
- **The skill passes its own linter.** A test asserts this. If your change
  makes a skill file fail, fix the file or fix the rule, and say which.
- **`SKILL.md` stays under 150 lines.** A test asserts this too. Detail belongs
  in `references/`, which loads only when needed.
- **Write the docs in the style the skill enforces.** Read `SKILL.md` before
  you edit prose here.

## Add a banned word

Add a row to the right table in `references/banned.md`. The first cell is the
word or pattern, the second is the replacement, or `delete`.

Use the regular expression form when a word is filler in one context and
correct in another:

```markdown
| /\bjust\s+(?=run\b\|add\b)/ | delete |
```

Escape a pipe inside the expression as `\|`, so the Markdown table still
parses. Then add a test that proves both the catch and the exception.

## Add a rule to the checker

1. Add the rule name to `RULES` in `scripts/check_docs.py`.
2. Decide whether it is an error or a hint. A rule that cannot be accurate with
   the standard library belongs in `HINT_RULES`.
3. Emit findings from `check_file`.
4. Add tests for the catch, the exception, and the waiver.
5. Document it in the README table and in `SKILL.md`.

## Report a false positive

Open an issue with the smallest Markdown that reproduces it, the rule name, and
what you expected. A false positive is a bug: people stop reading a linter that
cries wolf.
