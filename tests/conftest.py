"""Shared paths and helpers for the plain-style tests."""

from __future__ import annotations

import io
import os
import sys
from contextlib import redirect_stderr, redirect_stdout

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(REPO, ".claude", "skills", "plain-style")
SCRIPTS = os.path.join(SKILL, "scripts")
BANNED_PATH = os.path.join(SKILL, "references", "banned.md")
FIXTURES = os.path.join(REPO, "tests", "fixtures")

sys.path.insert(0, SCRIPTS)

import check_docs  # noqa: E402


@pytest.fixture(scope="session")
def banned():
    return check_docs.load_banned(BANNED_PATH)


@pytest.fixture
def check(banned, tmp_path):
    """Write text to a temporary file and return its findings."""

    counter = iter(range(1000))

    def run(text: str) -> list:
        path = tmp_path / f"doc{next(counter)}.md"
        path.write_text(text, encoding="utf-8")
        return check_docs.check_file(str(path), banned)

    return run


@pytest.fixture
def rules(check):
    """Return the rule names of the findings that no waiver covers."""

    def run(text: str) -> list[str]:
        return [f.rule for f in check(text) if not f.waived]

    return run


@pytest.fixture
def run_cli():
    """Run the command line entry point and capture its exit code and output."""

    def run(argv: list[str]) -> tuple[int, str]:
        out = io.StringIO()
        with redirect_stdout(out), redirect_stderr(io.StringIO()):
            code = check_docs.main(argv + ["--banned", BANNED_PATH])
        return code, out.getvalue()

    return run


def skill_errors(path: str, banned) -> list[str]:
    """Return the messages of the errors in a skill file."""
    findings = check_docs.check_file(path, banned)
    return [f.message for f in findings if not f.waived and not f.hint]
