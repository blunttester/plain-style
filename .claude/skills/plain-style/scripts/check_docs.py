#!/usr/bin/env python3
"""Lint Markdown prose against the plain-style rules.

Stdlib only. Reports file, line, rule, and the offending text. It does not
fix anything: the writer decides whether the rule or the sentence is wrong.

Exit codes:
    0  no errors (hints may still be printed)
    1  at least one error
    2  a file could not be read

Waivers, written as HTML comments so they stay out of the rendered page:

    <!-- plain-style: allow=long-sentence reason: the predicate breaks if split -->
    <!-- plain-style: allow-file=banned-word reason: this file lists them -->

A line waiver covers the block of lines that follows it. A file waiver covers
the whole file. Waived findings are printed as WAIVED and do not set the exit
code.

Glossary block, used by the glossary-synonym rule:

    <!-- plain-style:glossary
    import job: ingestion cycle, load pass
    -->

The left side is the term to keep; the right side lists the names for the same
concept that the document must not use.
"""

from __future__ import annotations

import argparse
import bisect
import json
import os
import re
import sys

MAX_SENTENCE_WORDS = 25
MAX_STEP_WORDS = 20
MAX_PARAGRAPH_SENTENCES = 6
WORDS_PER_EM_DASH = 200

RULES = (
    "long-sentence",
    "banned-word",
    "em-dash",
    "passive-voice",
    "paragraph-length",
    "glossary-synonym",
)
HINT_RULES = frozenset({"passive-voice"})

# ---------------------------------------------------------------------------
# masking: prose only, never code, links, or HTML
# ---------------------------------------------------------------------------

_INLINE_CODE = re.compile(r"(?<!`)(`+)(?!`).*?(?<!`)\1(?!`)", re.DOTALL)
_AUTOLINK = re.compile(r"<[^ >]+://[^ >]*>")
_LINK_TARGET = re.compile(r"\]\([^)]*\)")
_REF_DEF = re.compile(r"^\s*\[[^\]]+\]:\s*\S+")
_BARE_URL = re.compile(r"\b[a-z][a-z0-9+.-]*://\S+", re.IGNORECASE)
_HTML_TAG = re.compile(r"</?[A-Za-z][^>]*>")
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def _blank(match: re.Match) -> str:
    """Replace a match with spaces so line offsets survive."""
    return " " * (match.end() - match.start())


def mask(line: str) -> str:
    for pattern in (
        _HTML_COMMENT,
        _INLINE_CODE,
        _AUTOLINK,
        _LINK_TARGET,
        _REF_DEF,
        _BARE_URL,
        _HTML_TAG,
    ):
        line = pattern.sub(_blank, line)
    return line


# ---------------------------------------------------------------------------
# line classification
# ---------------------------------------------------------------------------

_FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
_HEADING = re.compile(r"^\s{0,3}#{1,6}\s")
_SETEXT = re.compile(r"^\s{0,3}(=+|-{2,})\s*$")
_ORDERED = re.compile(r"^(\s*)(\d+[.)])\s+")
_UNORDERED = re.compile(r"^(\s*)([-*+])\s+")
_TABLE = re.compile(r"^\s*\|")
_QUOTE = re.compile(r"^\s{0,3}>\s?")

PROSE, ORDERED, UNORDERED, HEADING, TABLE, SKIP = range(6)


class Line:
    __slots__ = ("no", "raw", "text", "kind", "indent")

    def __init__(self, no: int, raw: str, text: str, kind: int, indent: int):
        self.no = no
        self.raw = raw
        self.text = text
        self.kind = kind
        self.indent = indent


def outside_code(source: str) -> list[str]:
    """Raw lines with fenced code and frontmatter blanked, line count preserved."""
    raw_lines = source.splitlines()
    out: list[str] = []
    fence: str | None = None
    in_frontmatter = bool(raw_lines) and raw_lines[0].strip() == "---"

    for index, raw in enumerate(raw_lines, start=1):
        if in_frontmatter:
            if index > 1 and raw.strip() in ("---", "..."):
                in_frontmatter = False
            out.append("")
            continue

        fence_match = _FENCE.match(raw)
        if fence is not None:
            if fence_match and fence_match.group(1)[0] == fence[0]:
                if len(fence_match.group(1)) >= len(fence):
                    fence = None
            out.append("")
            continue
        if fence_match:
            fence = fence_match.group(1)
            out.append("")
            continue

        out.append(raw)

    return out


def classify(lines: list[str]) -> list[Line]:
    """Mark each line's kind and mask everything that is not prose."""
    out: list[Line] = []
    in_comment = False

    for index, raw in enumerate(lines, start=1):
        body = raw
        if in_comment:
            close = body.find("-->")
            if close == -1:
                out.append(Line(index, raw, "", SKIP, 0))
                continue
            body = " " * (close + 3) + body[close + 3:]
            in_comment = False

        if not body.strip():
            out.append(Line(index, raw, "", SKIP, 0))
            continue

        body = _QUOTE.sub(lambda m: " " * len(m.group(0)), body)
        text = mask(body)

        # mask() removes complete comments; an opener left over spans lines.
        opener = text.find("<!--")
        if opener != -1:
            text = text[:opener] + " " * (len(text) - opener)
            in_comment = True

        if not text.strip():
            kind = SKIP
        elif _HEADING.match(text) or _SETEXT.match(text.rstrip()):
            kind = HEADING
        elif _TABLE.match(text):
            kind = TABLE
        elif _ORDERED.match(text):
            kind = ORDERED
        elif _UNORDERED.match(text):
            kind = UNORDERED
        else:
            kind = PROSE

        indent = len(text) - len(text.lstrip())
        out.append(Line(index, raw, text, kind, indent))

    return out


# ---------------------------------------------------------------------------
# chunks: a paragraph or a single list item
# ---------------------------------------------------------------------------


class Chunk:
    def __init__(self, kind: int):
        self.kind = kind
        self.parts: list[tuple[int, str]] = []

    def build(self) -> tuple[str, list[int], list[int]]:
        """Return the joined text plus offset and line-number lookup tables."""
        pieces: list[str] = []
        starts: list[int] = []
        numbers: list[int] = []
        cursor = 0
        for number, text in self.parts:
            starts.append(cursor)
            numbers.append(number)
            pieces.append(text)
            cursor += len(text) + 1
        return "\n".join(pieces), starts, numbers


def sections(lines: list[Line]) -> list[list[Line]]:
    """Group lines by heading, so a long document earns no free em dashes."""
    out: list[list[Line]] = [[]]
    for line in lines:
        if line.kind == SKIP:
            continue
        if line.kind == HEADING:
            out.append([])
        out[-1].append(line)
    return [section for section in out if section]


def chunks(lines: list[Line]) -> list[Chunk]:
    out: list[Chunk] = []
    current: Chunk | None = None
    previous_kind = PROSE

    for line in lines:
        if line.kind in (SKIP, HEADING, TABLE):
            current = None
            continue

        if line.kind in (ORDERED, UNORDERED):
            kind = line.kind
            # A nested bullet inside a numbered step is still a step.
            if kind == UNORDERED and previous_kind == ORDERED and line.indent >= 2:
                kind = ORDERED
            marker = (_ORDERED if line.kind == ORDERED else _UNORDERED).match(line.text)
            body = " " * len(marker.group(0)) + line.text[marker.end():]
            current = Chunk(kind)
            out.append(current)
            current.parts.append((line.no, body))
            previous_kind = kind
            continue

        if current is None:
            current = Chunk(PROSE)
            out.append(current)
            previous_kind = PROSE
        current.parts.append((line.no, line.text))

    return out


# ---------------------------------------------------------------------------
# sentences
# ---------------------------------------------------------------------------

_ABBREVIATIONS = frozenset(
    """e.g i.e etc vs cf approx fig al dr mr mrs ms st inc ltd jr sr no
    resp ca est min max sec vol ie eg""".split()
)
_WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’/_-]*")
_OPENERS = "\"'“‘([*_`"


def _is_boundary(text: str, dot: int, after: int) -> bool:
    start = dot - 1
    while start >= 0 and (text[start].isalnum() or text[start] in "._'-"):
        start -= 1
    word = text[start + 1:dot].lower().strip(".")
    if word in _ABBREVIATIONS:
        return False
    if len(word) == 1 and word.isalpha():  # an initial, as in "J. Smith"
        return False

    index = after
    while index < len(text) and text[index].isspace():
        index += 1
    if index >= len(text):
        return True
    char = text[index]
    return char.isupper() or char.isdigit() or char in _OPENERS


def split_sentences(text: str) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    start = 0
    index = 0
    length = len(text)
    while index < length:
        if text[index] in ".!?":
            after = index + 1
            while after < length and text[after] in ".!?)]\"'”’":
                after += 1
            if after >= length or (text[after].isspace() and _is_boundary(text, index, after)):
                piece = text[start:after]
                if piece.strip():
                    out.append((start, piece.strip()))
                start = after
                index = after
                continue
        index += 1
    tail = text[start:]
    if tail.strip():
        out.append((start, tail.strip()))
    return out


def count_words(sentence: str) -> int:
    return len(_WORD.findall(sentence))


# ---------------------------------------------------------------------------
# banned list
# ---------------------------------------------------------------------------

_TABLE_ROW = re.compile(r"^\s*\|(.+)\|\s*$")
_SEPARATOR = re.compile(r"^[\s|:-]+$")
_CELL_SPLIT = re.compile(r"(?<!\\)\|")
_HEADER_CELLS = {"word or pattern", "word", "pattern", "phrase"}


def load_banned(path: str) -> list[tuple[str, re.Pattern[str]]]:
    """Read the two-column tables in banned.md. That file is the only list."""
    entries: list[tuple[str, re.Pattern[str]]] = []
    seen: set[str] = set()
    with open(path, encoding="utf-8") as handle:
        for raw in handle:
            row = _TABLE_ROW.match(raw)
            if not row or _SEPARATOR.match(raw.strip()):
                continue
            cells = [
                cell.strip().strip("`").replace("\\|", "|")
                for cell in _CELL_SPLIT.split(row.group(1))
            ]
            if len(cells) < 2 or not cells[0]:
                continue
            term = cells[0]
            if term.lower() in _HEADER_CELLS or set(term) <= set("-: "):
                continue
            if term.lower() in seen:
                continue
            seen.add(term.lower())
            replacement = cells[1]
            if term.startswith("/") and term.endswith("/") and len(term) > 2:
                pattern = re.compile(term[1:-1], re.IGNORECASE)
            else:
                spaced = r"\s+".join(re.escape(part) for part in term.split())
                pattern = re.compile(rf"(?<![\w-]){spaced}(?![\w-])", re.IGNORECASE)
            entries.append((replacement, pattern))
    return entries


# ---------------------------------------------------------------------------
# passive voice heuristic
# ---------------------------------------------------------------------------

_IRREGULAR = (
    "done|made|built|sent|kept|held|set|put|shown|known|written|given|taken|"
    "found|run|read|lost|left|told|brought|caught|bought|dealt|meant|split|cut"
)
_PASSIVE = re.compile(
    rf"\b(is|are|was|were|be|been|being|am|gets|got)\s+"
    rf"(?:\w+ly\s+)?((?:\w+(?:ed|en))|{_IRREGULAR})\b",
    re.IGNORECASE,
)
_NOT_PASSIVE = frozenset({"been", "seen", "open", "often", "children", "women", "men"})

# After a form of "be", these read as adjectives far more often than as passives.
_ADJECTIVAL = frozenset(
    """based related required intended expected supposed located limited designed
    involved interested concerned advanced complicated detailed embedded enabled
    disabled deprecated unchanged undefined unsupported aligned suited tied
    bound keen aware""".split()
)


# ---------------------------------------------------------------------------
# waivers and glossary
# ---------------------------------------------------------------------------

_WAIVER = re.compile(
    r"<!--\s*plain-style:\s*allow(?P<scope>-file)?="
    r"(?P<rules>[\w-]+(?:\s*,\s*[\w-]+)*)",
    re.IGNORECASE,
)
_GLOSSARY = re.compile(r"<!--\s*plain-style:glossary\s*(?P<body>.*?)-->", re.DOTALL | re.IGNORECASE)


def parse_waivers(raw_lines: list[str]) -> tuple[set[str], list[tuple[int, int, set[str]]]]:
    file_rules: set[str] = set()
    ranges: list[tuple[int, int, set[str]]] = []

    for index, raw in enumerate(raw_lines, start=1):
        match = _WAIVER.search(raw)
        if not match:
            continue
        rules = {r.strip() for r in match.group("rules").split(",") if r.strip()}
        if match.group("scope"):
            file_rules |= rules
            continue
        # The waiver covers the next run of non-blank lines.
        cursor = index if raw[: match.start()].strip() else index + 1
        while cursor <= len(raw_lines) and not raw_lines[cursor - 1].strip():
            cursor += 1
        end = cursor
        while end < len(raw_lines) and raw_lines[end].strip():
            end += 1
        ranges.append((min(index, cursor), max(end, index), rules))
    return file_rules, ranges


def parse_glossary(source: str) -> dict[str, str]:
    """Map each disallowed alternative to the term the document must use."""
    alternatives: dict[str, str] = {}
    for block in _GLOSSARY.finditer(source):
        for raw in block.group("body").splitlines():
            if ":" not in raw:
                continue
            term, _, rest = raw.partition(":")
            term = term.strip()
            if not term:
                continue
            for alternative in rest.split(","):
                alternative = alternative.strip()
                if alternative:
                    alternatives[alternative.lower()] = term
    return alternatives


# ---------------------------------------------------------------------------
# checking
# ---------------------------------------------------------------------------


class Finding:
    __slots__ = ("path", "line", "rule", "message", "snippet", "waived")

    def __init__(self, path: str, line: int, rule: str, message: str, snippet: str):
        self.path = path
        self.line = line
        self.rule = rule
        self.message = message
        self.snippet = snippet
        self.waived = False

    @property
    def hint(self) -> bool:
        return self.rule in HINT_RULES


def _trim(text: str, limit: int = 100) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def check_file(path: str, banned: list[tuple[str, re.Pattern[str]]]) -> list[Finding]:
    with open(path, encoding="utf-8") as handle:
        source = handle.read()

    # Waivers and glossary blocks only count outside fenced code, so that a
    # document can show an example of one without arming it.
    prose_lines = outside_code(source)
    file_waivers, waiver_ranges = parse_waivers(prose_lines)
    glossary = parse_glossary("\n".join(prose_lines))
    lines = classify(prose_lines)

    checkable = [line for line in lines if line.kind != SKIP]
    findings: list[Finding] = []

    # banned words and glossary synonyms, per line
    for line in checkable:
        for replacement, pattern in banned:
            for match in pattern.finditer(line.text):
                found = " ".join(match.group(0).split())
                findings.append(
                    Finding(
                        path,
                        line.no,
                        "banned-word",
                        f'"{found}" -> {replacement}',
                        _trim(line.text),
                    )
                )
        for alternative, term in glossary.items():
            pattern = re.compile(rf"(?<![\w-]){re.escape(alternative)}(?![\w-])", re.IGNORECASE)
            if pattern.search(line.text):
                findings.append(
                    Finding(
                        path,
                        line.no,
                        "glossary-synonym",
                        f'use "{term}" for this concept',
                        _trim(alternative),
                    )
                )

    # em dashes, budgeted per section so a long document earns no free ones
    for section in sections(lines):
        section_words = sum(count_words(line.text) for line in section)
        budget = max(1, round(section_words / WORDS_PER_EM_DASH))
        used = 0
        for line in section:
            for _ in re.finditer("—", line.text):
                used += 1
                if used > budget:
                    findings.append(
                        Finding(
                            path,
                            line.no,
                            "em-dash",
                            f"em dash {used} in this section, budget is {budget} "
                            f"for {section_words} words; use a full stop, a colon, "
                            f"or brackets",
                            _trim(line.text),
                        )
                    )

    # sentence and paragraph rules, per chunk
    for chunk in chunks(lines):
        text, starts, numbers = chunk.build()
        sentences = split_sentences(text)
        limit = MAX_STEP_WORDS if chunk.kind == ORDERED else MAX_SENTENCE_WORDS

        for offset, sentence in sentences:
            line_no = numbers[max(0, bisect.bisect_right(starts, offset) - 1)]
            words = count_words(sentence)
            if words > limit:
                kind = "step" if chunk.kind == ORDERED else "sentence"
                findings.append(
                    Finding(
                        path,
                        line_no,
                        "long-sentence",
                        f"{words} words in a {kind}, limit is {limit}",
                        _trim(sentence),
                    )
                )
            for match in _PASSIVE.finditer(sentence):
                participle = match.group(2).lower()
                if participle in _NOT_PASSIVE or participle in _ADJECTIVAL:
                    continue
                findings.append(
                    Finding(
                        path,
                        line_no,
                        "passive-voice",
                        "possible passive; name the actor",
                        _trim(match.group(0)),
                    )
                )

        if chunk.kind == PROSE and len(sentences) > MAX_PARAGRAPH_SENTENCES:
            findings.append(
                Finding(
                    path,
                    numbers[0],
                    "paragraph-length",
                    f"{len(sentences)} sentences, limit is {MAX_PARAGRAPH_SENTENCES}",
                    _trim(sentences[0][1], 60),
                )
            )

    for finding in findings:
        if finding.rule in file_waivers:
            finding.waived = True
            continue
        for start, end, rules in waiver_ranges:
            if finding.rule in rules and start <= finding.line <= end:
                finding.waived = True
                break

    findings.sort(key=lambda f: (f.line, f.rule))
    return findings


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------


def default_banned_path() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(here), "references", "banned.md")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check Markdown prose against the plain-style rules."
    )
    parser.add_argument("files", nargs="+", help="Markdown files to check")
    parser.add_argument(
        "--banned", default=default_banned_path(), help="path to banned.md"
    )
    parser.add_argument(
        "--show-waived", action="store_true", help="print findings that a waiver covers"
    )
    parser.add_argument(
        "--hints", action="store_true", help="print hint-level findings, which are off by default"
    )
    parser.add_argument(
        "--json", action="store_true", help="print findings as JSON, one object each"
    )
    args = parser.parse_args(argv)

    if os.path.exists(args.banned):
        banned = load_banned(args.banned)
    else:
        print(f"warning: no banned list at {args.banned}", file=sys.stderr)
        banned = []

    errors = 0
    hints = 0
    waived = 0
    read_failures = 0
    records: list[dict[str, object]] = []

    for path in args.files:
        try:
            findings = check_file(path, banned)
        except OSError as error:
            print(f"error: cannot read {path}: {error}", file=sys.stderr)
            read_failures += 1
            continue

        for finding in findings:
            if finding.waived:
                waived += 1
                level = "waived"
                show = args.show_waived
                prefix = "WAIVED "
            elif finding.hint:
                hints += 1
                level = "hint"
                show = args.hints
                prefix = "hint "
            else:
                errors += 1
                level = "error"
                show = True
                prefix = ""

            if not show:
                continue
            if args.json:
                records.append(
                    {
                        "path": finding.path,
                        "line": finding.line,
                        "rule": finding.rule,
                        "level": level,
                        "message": finding.message,
                        "text": finding.snippet,
                    }
                )
                continue
            print(f"{prefix}{finding.path}:{finding.line}: {finding.rule}: {finding.message}")
            print(f"    {finding.snippet}")

    if args.json:
        json.dump(
            {
                "findings": records,
                "summary": {
                    "errors": errors,
                    "hints": hints,
                    "waived": waived,
                    "files": len(args.files),
                },
            },
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
    else:
        parts = [f"{errors} error(s)", f"{hints} hint(s)", f"{waived} waived"]
        print(f"\n{', '.join(parts)} across {len(args.files)} file(s)")

    if read_failures:
        return 2
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
