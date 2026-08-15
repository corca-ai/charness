#!/usr/bin/env python3

"""Where a command is WRITTEN, and how a finding about it is rendered.

Split from `command_dominance_lib` on a concept boundary: this file answers "which
spans of this text are commands" and "what sentence does a finding print", while
the lib answers "is this command dominated". A carrier reader is about markdown and
config syntax; the classifier is about shell tokens and registry rules. They are
edited for different reasons and by different evidence.

One-way dependency: this module imports the registry types and NOTHING from the
classifier, so the lib can import it without a cycle.

Stdlib only, and it opens no files.
"""

from __future__ import annotations

import importlib.util as _importlib_util
import re
from pathlib import Path as _Path

# The registry types, loaded by path for the same reason the lib does it: these files
# ship inside an exported plugin where this directory is not a package on `sys.path`.
# Loaded HERE and re-exported to the lib, so the whole family shares ONE `Finding`
# class rather than two structurally-identical ones from two independent execs.
_spec = _importlib_util.spec_from_file_location(
    "command_dominance_registry", _Path(__file__).resolve().with_name("command_dominance_registry.py")
)
registry_module = _importlib_util.module_from_spec(_spec)
_spec.loader.exec_module(registry_module)
Finding = registry_module.Finding
Registry = registry_module.Registry


def split_chunks(command: str) -> list[str]:
    """Split a shell one-liner into the commands it actually runs, QUOTE-AWARE.

    A regex split was quote-blind, and an adversarial round-2 reviewer showed the
    cost: `bash -c "python3 -m pytest -q tests && echo ok"` split mid-quote into
    `bash -c "python3 -m pytest -q tests` and `echo ok"`, both of which then
    failed `shlex.split` with an unterminated quote, so `resolve_invocations`
    returned [] for each and a dominated whole-suite run inside `bash -c` was
    INVISIBLE to a blocking gate. It also made the nested-chunk loop in
    `_resolve_shell_c` unreachable by construction: the outer split had already
    destroyed the string it was written to iterate.

    Operators recognised outside quotes: `&&`, `||`, `;`, `|`, and newline.
    Backslash escapes the next character. What this still does NOT model, and it
    belongs to the blind class rather than to a bigger parser here: parentheses,
    process substitution, heredocs, and `$(...)`.
    """
    chunks: list[str] = []
    buffer: list[str] = []
    quote: str | None = None
    index = 0
    while index < len(command):
        char = command[index]
        if quote is not None:
            buffer.append(char)
            if char == quote:
                quote = None
            index += 1
            continue
        if char in ("'", '"'):
            quote = char
            buffer.append(char)
            index += 1
            continue
        if char == "\\" and index + 1 < len(command):
            buffer.append(char)
            buffer.append(command[index + 1])
            index += 2
            continue
        if command[index : index + 2] in ("&&", "||"):
            chunks.append("".join(buffer))
            buffer = []
            index += 2
            continue
        if char in (";", "|", "\n"):
            chunks.append("".join(buffer))
            buffer = []
            index += 1
            continue
        buffer.append(char)
        index += 1
    chunks.append("".join(buffer))
    return [chunk.strip() for chunk in chunks if chunk.strip()]


# A command written in prose is usually fenced or inline-coded. Both are read;
# what is NOT read is a command a document merely alludes to in words, which is
# blind-class item 3.
_INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")


def iter_document_commands(text: str) -> list[tuple[int, str]]:
    """Every command-looking span in a markdown body, with its 1-based line.

    Fenced blocks contribute their content lines; inline code spans contribute
    their content. Ordinary prose contributes nothing — a sentence naming a
    command in words is invisible here, deliberately, because a reader that
    matched prose would fire on this module's own docstring.
    """
    found: list[tuple[int, str]] = []
    in_fence = False
    for number, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            if stripped:
                found.append((number, stripped))
            continue
        for span in _INLINE_CODE_RE.findall(raw):
            if span.strip():
                found.append((number, span.strip()))
    return found


_UNQUOTE_RE = re.compile(r"""^(['"])(.*)\1$""")


def _unquote(value: str) -> str:
    stripped = value.strip()
    match = _UNQUOTE_RE.match(stripped)
    if match:
        return match.group(2)
    # A `#` is only a comment OUTSIDE quotes; one inside the command is part of it.
    return stripped.split(" #", 1)[0].strip()


def read_config_literal(text: str, key: str) -> list[tuple[int, str]]:
    """Every `key = "..."` / `key: "..."` assignment in a config body, with lines.

    Lives here rather than in either caller because both the repo gate and the
    exported consumer inventory need it, and the first draft of this slice wrote
    it twice — where the second copy silently matched the whole
    `test-command = "..."` LINE as if it were the command, resolved the program to
    `test-command`, and reported a clean tree over a dominated literal. Measured,
    not hypothesised.

    Deliberately a line reader rather than a TOML/YAML parser, so one reader
    serves `cosmic-ray.toml`, a YAML adapter, and whatever a consuming repo points
    at. What it gives up: a key is matched by NAME, not by its full table path, and
    a multi-line or computed value is invisible. Both are blind-class item 3.
    """
    pattern = re.compile(rf"^\s*(?:['\"])?{re.escape(key)}(?:['\"])?\s*[=:]\s*(\S.*)$")
    found: list[tuple[int, str]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        match = pattern.match(line)
        if match:
            value = _unquote(match.group(1))
            if value:
                found.append((number, value))
    return found


def unbudgeted_basis(queue_label: str | None) -> str:
    """Why a discovered command is reported as named by no budgeted label.

    ONE owner for this sentence. It was written twice -- once in the repo gate,
    once in the exported inventory -- and a round-2 reviewer named that as the
    same drift shape this slice consolidated `budgeted_label_union` to avoid. It
    is a verdict sentence on two proof surfaces, so it gets one home.

    The wording is deliberately narrow. "No budgeted label names this command" is
    NOT "nothing bounds its runtime": a config literal can carry no queue label at
    all, so that seam is structurally always-report, and the gate that spawns the
    literal may well carry its own bar.
    """
    if not queue_label:
        return (
            "config literal: carries no queue label by construction, so no budgeted "
            "label can name it. This does NOT establish that nothing bounds its "
            "runtime -- the gate that spawns it may carry its own bar."
        )
    return f"queue label {queue_label!r} has no budget entry"


def finding_message(finding: Finding) -> str:
    """The refusal text. It names the replacement, because a refusal that does not
    say what it wants is one an author routes around rather than obeys."""
    where = f"{finding.site}:{finding.line}" if finding.line is not None else finding.site
    return (
        f"{where}: `{finding.command}` is a dominated command "
        f"({finding.rule_id}). Use `{finding.replacement}` instead. {finding.reason}"
    )
