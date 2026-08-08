"""Refuse transcribed facts on FORWARD-LOOKING prose surfaces.

A number in prose is read as current. When a command can regenerate it, the prose
should carry the COMMAND, not the command's output -- otherwise the number is true
on the day it is written and misleading every day after, and the next reader acts
on it instead of checking.

The seam, which decides whether a surface is in scope at all:

- **Dated, append-only RECORDS** -- retros, critiques, audits, slice logs, commit
  messages. A number there describes one moment that will never be true again, and
  that is exactly what it is for. OUT OF SCOPE, permanently, not by grandfather.
- **Rolling, FORWARD-LOOKING surfaces** -- agent prompt files, conventions, docs,
  skill prose. A number there is read as today's answer. IN SCOPE.

Two ways to satisfy it, and the difference is what the command COSTS:

- A CHEAP command (`git describe`, `gh issue list`, a grep): carry the command
  alone. The reader runs it and gets today's answer for nothing.
- An EXPENSIVE command (a multi-minute suite, a fan-out census, a full-corpus
  sweep): carry the command AND link the checked-in artifact holding its output.
  Telling a reader to re-run an expensive gate to learn one number is not a fix --
  it moves the cost onto every future reader, forever. The artifact is the
  provenance: it records what was run, when, and against what, so the prose links
  it instead of copying numbers out of it.

Portability: nothing here knows one repo's layout. Surfaces and exemptions are
resolved from the consuming repo's quality adapter, with defaults that fit an
ordinary repo. A consumer's exemptions belong in that consumer's adapter, never in
this shipped file.
"""

from __future__ import annotations

import fnmatch
import re
from pathlib import Path

# Surfaces a reader treats as current. Deliberately excludes any dated-record
# directory: those are out of scope by nature, not by exemption.
DEFAULT_SURFACES = (
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "docs/*.md",
    "docs/conventions/*.md",
)

FENCE_RE = re.compile(r"^\s*```")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
LINK_TARGET_RE = re.compile(r"(?<=\])\([^)]*\)")
URL_RE = re.compile(r"<?\bhttps?://\S+>?")

# Each pattern pairs the literal class with the replacement the author should
# write instead, because a refusal that does not say what to do trains avoidance.
PATTERNS = (
    (
        re.compile(r"\b(?:v\d+\.\d+(?:\.\d+)?|\d+\.\d+\.\d+)\b"),
        "a release or tool version",
        "carry `git describe --tags --abbrev=0`, or link the release artifact",
    ),
    (
        re.compile(r"\b(?=[0-9a-f]{7,40}\b)(?=[0-9a-f]*[a-f])(?=[0-9a-f]*\d)[0-9a-f]{7,40}\b", re.IGNORECASE),
        "a commit sha",
        "carry `git rev-parse --short HEAD`, or link the commit",
    ),
    (
        re.compile(
            # The number must END in a digit. An identifier list -- `24, issue 13` --
            # is not a count, and `[\d,]*` alone swallowed the comma and matched it.
            r"\b\d(?:[\d,]*\d)?\s+(?:commits?|issues?|files?|tests?|lines?|artifacts?|skills?|checks?|entries|findings?)\b",
            re.IGNORECASE,
        ),
        "an as-of count",
        "carry the command that recounts it, or link the artifact that measured it",
    ),
)


def scrub(line: str) -> str:
    """Remove the spans the rule asks the author to WRITE.

    Fenced blocks, inline code, link targets, and URLs carry commands and paths.
    Refusing a number inside them would reject the replacement the rule just
    recommended. Link TEXT stays in scope: that is prose a reader believes.
    """
    for pattern in (INLINE_CODE_RE, LINK_TARGET_RE, URL_RE):
        line = pattern.sub(" ", line)
    return line


def scan_text(text: str) -> list[tuple[int, str, str, str]]:
    hits: list[tuple[int, str, str, str]] = []
    in_fence = False
    for lineno, raw in enumerate(text.splitlines(), start=1):
        if FENCE_RE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        prose = scrub(raw)
        for pattern, label, remedy in PATTERNS:
            match = pattern.search(prose)
            if match:
                hits.append((lineno, match.group(0).strip(), label, remedy))
                break
    return hits


def resolve_config(adapter: dict | None) -> tuple[tuple[str, ...], dict[str, str]]:
    """Read surfaces and exemptions from the consuming repo's adapter.

    `load_adapter` returns a RESULT envelope (`found`/`valid`/`data`), not the
    adapter body, so the config is read from `data` when that shape is present.
    Accepting the bare body too keeps this callable from a test or a host that
    already unwrapped it.
    """
    adapter = adapter or {}
    body = adapter.get("data") if isinstance(adapter.get("data"), dict) else adapter
    config = (body or {}).get("regenerable_facts") or {}
    surfaces = tuple(config.get("surfaces") or DEFAULT_SURFACES)
    exemptions = dict(config.get("exemptions") or {})
    return surfaces, exemptions


def exemption_for(rel: str, exemptions: dict[str, str]) -> str | None:
    for pattern, reason in exemptions.items():
        if rel == pattern or fnmatch.fnmatch(rel, pattern):
            return reason or None
    return None


def scan_repo(repo_root: Path, adapter: dict | None = None) -> dict:
    surfaces, exemptions = resolve_config(adapter)
    findings: list[dict[str, object]] = []
    exempted: list[dict[str, str]] = []
    checked = 0
    seen: set[Path] = set()
    for pattern in surfaces:
        for path in sorted(repo_root.glob(pattern)):
            if not path.is_file() or path in seen:
                continue
            seen.add(path)
            rel = path.relative_to(repo_root).as_posix()
            reason = exemption_for(rel, exemptions)
            if reason is not None:
                exempted.append({"path": rel, "reason": reason})
                continue
            checked += 1
            for lineno, literal, label, remedy in scan_text(path.read_text(encoding="utf-8", errors="ignore")):
                findings.append(
                    {"path": rel, "line": lineno, "literal": literal, "label": label, "remedy": remedy}
                )
    return {
        "checked": checked,
        "surfaces": list(surfaces),
        "exempted": exempted,
        "findings": findings,
        # An exemption without a stated reason is the same unfalsifiable claim the
        # rule exists to remove, so it is reported rather than honoured silently.
        "unreasoned_exemptions": [p for p, r in exemptions.items() if not r],
    }
