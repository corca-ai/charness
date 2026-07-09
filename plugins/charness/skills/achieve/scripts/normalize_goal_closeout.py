#!/usr/bin/env python3
"""Normalize common achieve goal closeout form mistakes.

This helper is intentionally narrow: it fixes shapes already enforced by
check_goal_artifact.py without inventing missing evidence. It is an authoring
affordance for the "fail, patch, fail again" closeout churn class.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

STATUS_RE = re.compile(r"^Status:\s*(?P<status>\w+)\s*$", re.MULTILINE)
BACKTICK_EVIDENCE_RE = re.compile(
    r"^(?P<label>Retro|Host log probe|Disposition review):\s+`(?P<path>[^`\n]+)`\s*$",
    re.MULTILINE,
)
ROUTING_RE = re.compile(
    r"^(?P<prefix>-\s*)Routing:\s+(?P<skill>quality|impl|issue)\s+(?:--?|\u2014)\s+",
    re.MULTILINE,
)

QUEUE_SCAFFOLD_MARKERS = (
    "Record decisions, confirmations, credential actions, manual proof steps",
    "Decision: operator-only decision or confirmation needed",
)

VALID_RETRO_DISPOSITION_PREFIXES = (
    "applied:",
    "issue #",
    "none \u2014",
    "accepted-risk:",
    "out-of-scope:",
)


def _section_span(text: str, heading: str) -> tuple[int, int] | None:
    pattern = re.compile(rf"^## {re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(text)
    if match is None:
        return None
    next_match = re.search(r"^##\s+", text[match.end() :], re.MULTILINE)
    end = len(text) if next_match is None else match.end() + next_match.start()
    return match.end(), end


def _replace_section_body(text: str, heading: str, body: str) -> tuple[str, bool]:
    span = _section_span(text, heading)
    if span is None:
        return text, False
    start, end = span
    replacement = "\n\n" + body.strip() + "\n\n"
    updated = text[:start] + replacement + text[end:]
    return updated, updated != text


def _sub_with_count(pattern: re.Pattern[str], text: str, replacement) -> tuple[str, int]:
    count = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal count
        count += 1
        return replacement(match)

    return pattern.sub(repl, text), count


def _strip_backtick_evidence(text: str) -> tuple[str, int]:
    return _sub_with_count(
        BACKTICK_EVIDENCE_RE,
        text,
        lambda match: f"{match.group('label')}: {match.group('path')}",
    )


def _normalize_routing(text: str) -> tuple[str, int]:
    return _sub_with_count(
        ROUTING_RE,
        text,
        lambda match: f"{match.group('prefix')}Routing: find-skills -> {match.group('skill')} \u2014 ",
    )


def _clear_operator_queue_scaffold(text: str) -> tuple[str, bool]:
    span = _section_span(text, "Operator Decision Queue")
    if span is None:
        return text, False
    body = text[span[0] : span[1]]
    if not any(marker in body for marker in QUEUE_SCAFFOLD_MARKERS):
        return text, False
    return _replace_section_body(
        text,
        "Operator Decision Queue",
        "none \u2014 no operator-only decision remains for this completed local goal.",
    )


def _normalize_auto_retro_line(line: str) -> tuple[str, bool]:
    if not line.startswith("Retro dispositions:"):
        return line, False
    payload = line.split(":", 1)[1].strip()
    plain = payload.replace("`", "")
    if plain.startswith(VALID_RETRO_DISPOSITION_PREFIXES):
        normalized = f"Retro dispositions: {plain}"
    elif plain.startswith("PASS"):
        normalized = f"Retro dispositions: applied: {plain}"
    else:
        normalized = f"Retro dispositions: applied: {plain}"
    return normalized, normalized != line


def _normalize_auto_retro(text: str) -> tuple[str, int]:
    span = _section_span(text, "Auto-Retro")
    if span is None:
        return text, 0
    body = text[span[0] : span[1]]
    changed = 0
    lines = []
    for line in body.splitlines():
        normalized, line_changed = _normalize_auto_retro_line(line)
        changed += int(line_changed)
        lines.append(normalized)
    if not changed:
        return text, 0
    return text[: span[0]] + "\n".join(lines) + text[span[1] :], changed


def normalize(text: str, *, complete: bool = False) -> tuple[str, list[str]]:
    fixes: list[str] = []
    updated, count = _strip_backtick_evidence(text)
    if count:
        fixes.append(f"stripped backticks from {count} closeout evidence line(s)")
    updated2, count = _normalize_routing(updated)
    if count:
        fixes.append(f"normalized {count} Routing line(s) to name find-skills")
    updated3, changed = _clear_operator_queue_scaffold(updated2)
    if changed:
        fixes.append("replaced Operator Decision Queue scaffold with a none disposition")
    updated4, count = _normalize_auto_retro(updated3)
    if count:
        fixes.append(f"normalized {count} Auto-Retro disposition line(s)")
    if complete:
        updated5 = STATUS_RE.sub("Status: complete", updated4, count=1)
        if updated5 != updated4:
            fixes.append("set Status: complete")
        updated4 = updated5
    return updated4, fixes


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize common achieve closeout artifact form errors.")
    parser.add_argument("--goal-path", type=Path, required=True)
    parser.add_argument("--write", action="store_true", help="Write changes in place. Default is dry-run.")
    parser.add_argument("--complete", action="store_true", help="Also set `Status: complete`.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        original = args.goal_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"cannot read {args.goal_path}: {exc}", file=sys.stderr)
        return 2
    updated, fixes = normalize(original, complete=args.complete)
    changed = updated != original
    if changed and args.write:
        args.goal_path.write_text(updated, encoding="utf-8")
    payload = {"changed": changed, "written": bool(changed and args.write), "fixes": fixes}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        status = "wrote" if payload["written"] else "would change" if changed else "unchanged"
        print(f"normalize-goal-closeout: {status}")
        for fix in fixes:
            print(f"- {fix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
