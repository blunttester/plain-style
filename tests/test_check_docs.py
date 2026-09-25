"""Tests for the plain-style checker."""

from __future__ import annotations

import json
import os
import re

import pytest

from conftest import BANNED_PATH, FIXTURES, SKILL, check_docs, skill_errors

HEAD = "# T\n\n"


def words(count: int) -> str:
    return " ".join(["word"] * count) + " end."


# --------------------------------------------------------------------------
# masking
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("```bash\nleverage --robust\n```\n\nPlain sentence.\n", []),
        ("Run `leverage --utilize` now.\n", []),
        ("See [the guide](https://example.com/leverage/robust).\n", []),
        ("<!--\nwe leverage this\n-->\n\nClean line.\n", []),
        ("We leverage the cache.\n", ["banned-word"]),
    ],
    ids=["fenced code", "inline code", "url", "multiline comment", "bare word"],
)
def test_masking(rules, text, expected):
    assert rules(HEAD + text) == expected


def test_frontmatter_is_ignored(rules):
    text = "---\ndescription: leverage robust synergy\n---\n\n# T\n\nClean line.\n"
    assert rules(text) == []


# --------------------------------------------------------------------------
# sentence and paragraph length
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "flagged"),
    [
        (words(24), False),
        (words(30), True),
        ("1. " + words(19), False),
        ("1. " + words(23), True),
        ("1. Do the thing.\n\n   - " + words(23), True),
    ],
    ids=["prose 24", "prose 30", "step 19", "step 23", "nested bullet in step"],
)
def test_sentence_limits(rules, text, flagged):
    assert ("long-sentence" in rules(HEAD + text + "\n")) is flagged


def test_abbreviation_does_not_end_a_sentence(rules):
    text = HEAD + " ".join(["word"] * 12) + " e.g. " + " ".join(["word"] * 14) + ".\n"
    assert "long-sentence" in rules(text)


def test_paragraph_over_six_sentences(rules):
    text = HEAD + " ".join(["One short sentence."] * 7) + "\n"
    assert "paragraph-length" in rules(text)


def test_list_items_are_not_one_paragraph(rules):
    text = HEAD + "".join(f"- Item {n} here.\n" for n in range(10))
    assert "paragraph-length" not in rules(text)


# --------------------------------------------------------------------------
# banned list
# --------------------------------------------------------------------------


def test_banned_list_loads(banned):
    assert banned, "banned.md produced no rules"
    assert any("easy" in pattern.pattern for _, pattern in banned), (
        "an escaped pipe in a regex row broke the table parser"
    )


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Use just the header row.", []),
        ("Just run the script.", ["banned-word"]),
        ("Clearly labelled fields help.", []),
        ("Clearly this holds.", ["banned-word"]),
    ],
)
def test_context_sensitive_rows(rules, text, expected):
    assert rules(HEAD + text + "\n") == expected


def test_message_names_the_matched_text(check):
    assert '"leverage"' in check(HEAD + "We leverage it.\n")[0].message


def test_missing_banned_file_yields_no_rules():
    assert check_docs.load_banned(os.devnull) == []


# --------------------------------------------------------------------------
# waivers
# --------------------------------------------------------------------------


def test_line_waiver_covers_the_following_block(check):
    text = (
        HEAD
        + "<!-- plain-style: allow=banned-word reason: quoted -->\n"
        + "We leverage the cache.\n\nWe leverage it again.\n"
    )
    assert [f.waived for f in check(text)] == [True, False]


def test_file_waiver_reason_does_not_eat_the_last_rule(rules):
    text = (
        "<!-- plain-style: allow-file=banned-word,long-sentence reason: why -->\n"
        "# T\n\nWe leverage it. " + words(30) + "\n"
    )
    assert rules(text) == []


def test_waiver_inside_a_fence_is_inert(rules):
    text = (
        HEAD
        + "```markdown\n<!-- plain-style: allow-file=banned-word -->\n```\n\n"
        + "We leverage it.\n"
    )
    assert rules(text) == ["banned-word"]


# --------------------------------------------------------------------------
# glossary
# --------------------------------------------------------------------------

GLOSSARY = "<!-- plain-style:glossary\nimport job: ingestion cycle, load pass\n-->"


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ("Each ingestion cycle writes to the table.", ["glossary-synonym"]),
        ("Each import job writes to the table.", []),
        ("A clean sentence.", []),
    ],
    ids=["alternative", "preferred term", "block does not flag itself"],
)
def test_glossary(rules, body, expected):
    assert rules(f"{HEAD}{GLOSSARY}\n\n{body}\n") == expected


def test_glossary_inside_a_fence_is_inert(rules):
    text = f"{HEAD}```markdown\n{GLOSSARY}\n```\n\nEach ingestion cycle runs.\n"
    assert rules(text) == []


# --------------------------------------------------------------------------
# em dashes
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Git history is the archive — never archive by hand.\n", []),
        ("One — two.\n\nThree — four.\n", ["em-dash"]),
    ],
    ids=["one per section", "two in one section"],
)
def test_em_dash_budget(rules, text, expected):
    assert rules(HEAD + text) == expected


def test_em_dash_budget_is_per_section(rules):
    assert rules("# A\n\nOne — two.\n\n## B\n\nThree — four.\n") == []


# --------------------------------------------------------------------------
# passive voice
# --------------------------------------------------------------------------


def test_passive_is_a_hint(check):
    findings = check(HEAD + "The file is deleted.\n")
    assert [f.rule for f in findings] == ["passive-voice"]
    assert findings[0].hint


def test_adjectival_participle_is_not_passive(check):
    assert check(HEAD + "The value is required.\n") == []


# --------------------------------------------------------------------------
# command line
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("fixture", "code"),
    [("clean.md", 0), ("dirty.md", 1), ("does-not-exist.md", 2)],
)
def test_exit_codes(run_cli, fixture, code):
    assert run_cli([os.path.join(FIXTURES, fixture)])[0] == code


def test_dirty_output_names_the_rule(run_cli):
    assert "banned-word" in run_cli([os.path.join(FIXTURES, "dirty.md")])[1]


def test_hints_are_off_by_default(run_cli):
    assert "passive-voice" not in run_cli([os.path.join(FIXTURES, "clean.md")])[1]


def test_json_shape(run_cli):
    payload = json.loads(run_cli([os.path.join(FIXTURES, "dirty.md"), "--json"])[1])
    assert set(payload) == {"findings", "summary"}
    assert sorted(payload["findings"][0]) == [
        "level",
        "line",
        "message",
        "path",
        "rule",
        "text",
    ]


# --------------------------------------------------------------------------
# the skill has to pass its own checker
# --------------------------------------------------------------------------

REFERENCES = os.path.join(SKILL, "references")
SKILL_FILES = [os.path.join(SKILL, "SKILL.md")] + [
    os.path.join(REFERENCES, name) for name in sorted(os.listdir(REFERENCES))
]


@pytest.mark.parametrize("path", SKILL_FILES, ids=os.path.basename)
def test_skill_file_is_clean(path, banned):
    assert skill_errors(path, banned) == []


def test_skill_md_stays_short():
    with open(os.path.join(SKILL, "SKILL.md"), encoding="utf-8") as handle:
        assert len(handle.readlines()) < 150


def test_checker_imports_stdlib_only():
    """The installed script has to run where no third-party package exists."""
    path = os.path.join(SKILL, "scripts", "check_docs.py")
    with open(path, encoding="utf-8") as handle:
        source = handle.read()
    allowed = {"__future__", "argparse", "bisect", "json", "os", "re", "sys"}
    imported = set(re.findall(r"^(?:import|from)\s+(\w+)", source, re.MULTILINE))
    assert imported <= allowed, f"non-stdlib import: {sorted(imported - allowed)}"
