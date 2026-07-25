#!/usr/bin/env python3
"""Preflight prompt-mutation scenarios and transcripts for blinding leaks.

This is an advisory/read-only helper, not a standing gate. It scans the parts of
an eval scenario that are actually shown to the captured run, plus any supplied
transcripts, for git history/ref probes that can reveal arm identity before the
expensive capture/judge path is trusted.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

GIT_PREFIX = r"\bgit\b(?:\s+(?:-[Cc]\s+\S+|--no-pager|-c\s+\S+))*\s+"

BLOCKING_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("git-diff", re.compile(GIT_PREFIX + r"diff\b", re.IGNORECASE)),
    ("git-log", re.compile(GIT_PREFIX + r"log\b", re.IGNORECASE)),
    ("git-show", re.compile(GIT_PREFIX + r"show\b", re.IGNORECASE)),
    ("git-for-each-ref", re.compile(GIT_PREFIX + r"for-each-ref\b", re.IGNORECASE)),
    ("git-reflog", re.compile(GIT_PREFIX + r"reflog\b", re.IGNORECASE)),
)

ADVISORY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("git-rev-parse", re.compile(GIT_PREFIX + r"rev-parse\b", re.IGNORECASE)),
    ("git-status", re.compile(GIT_PREFIX + r"status\b", re.IGNORECASE)),
)

SCENARIO_VISIBLE_KEYS = {
    "prompt",
    "requiredCommandFragments",
    "requiredSummaryFragments",
    "declaredReferences",
}


def _load_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except OSError as exc:
        raise RuntimeError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{path}: invalid JSON: {exc}") from exc


def _iter_strings(value: Any, *, path: str = "$"):
    stack = [(path, value)]
    while stack:
        current_path, current = stack.pop()
        if isinstance(current, str):
            yield current_path, current
        elif isinstance(current, list):
            for index in range(len(current) - 1, -1, -1):
                stack.append((f"{current_path}[{index}]", current[index]))
        elif isinstance(current, dict):
            for key, item in reversed(list(current.items())):
                # `_`-prefixed keys are author comments: not shown to the captured
                # run, so scanning them would report on text the agent cannot see.
                if not str(key).startswith("_"):
                    stack.append((f"{current_path}.{key}", item))


def _scenario_visible_payload(data: Any) -> list[tuple[str, str]]:
    if not isinstance(data, dict):
        return list(_iter_strings(data))
    selected: list[tuple[str, str]] = []
    for key in sorted(SCENARIO_VISIBLE_KEYS):
        if key in data:
            selected.extend(_iter_strings(data[key], path=f"$.{key}"))
    return selected


def _line_col(text: str, offset: int) -> tuple[int, int]:
    before = text[:offset]
    line = before.count("\n") + 1
    last_newline = before.rfind("\n")
    col = offset + 1 if last_newline < 0 else offset - last_newline
    return line, col


def _scan_text(source: str, field: str, text: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for severity, patterns in (("clean-proof-blocker", BLOCKING_PATTERNS), ("advisory", ADVISORY_PATTERNS)):
        for rule_id, pattern in patterns:
            for match in pattern.finditer(text):
                line, col = _line_col(text, match.start())
                findings.append(
                    {
                        "severity": severity,
                        "rule": rule_id,
                        "source": source,
                        "field": field,
                        "line": line,
                        "column": col,
                        "match": match.group(0),
                    }
                )
    return findings


def scan_scenario(path: Path) -> list[dict[str, Any]]:
    data = _load_json(path)
    findings: list[dict[str, Any]] = []
    for field, text in _scenario_visible_payload(data):
        findings.extend(_scan_text(str(path), field, text))
    return findings


def scan_text_file(path: Path) -> list[dict[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise RuntimeError(f"cannot read {path}: {exc}") from exc
    return _scan_text(str(path), "$", text)


def run(args: argparse.Namespace) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    scan_inputs = [*(args.scenario_spec or []), *(args.transcript or []), *(args.text or [])]
    for path in args.scenario_spec or []:
        findings.extend(scan_scenario(path))
    for path in (args.transcript or []) + (args.text or []):
        findings.extend(scan_text_file(path))
    blockers = [finding for finding in findings if finding["severity"] == "clean-proof-blocker"]
    no_inputs = not scan_inputs
    return {
        "ok": True,
        "clean_proof_claim": bool(scan_inputs) and not blockers,
        "clean_proof_blocker_count": len(blockers),
        "blocking_count": len(blockers),
        "advisory_count": sum(1 for finding in findings if finding["severity"] == "advisory"),
        "scanned_inputs_count": len(scan_inputs),
        "no_inputs": no_inputs,
        "findings": findings,
        "non_claim": _non_claim(no_inputs=no_inputs, blockers=blockers),
    }


def _non_claim(*, no_inputs: bool, blockers: list[dict[str, Any]]) -> str:
    messages = {
        "empty": (
            "No input files were supplied, so this run makes no clean-proof claim. "
            "Pass --scenario-spec, --transcript, or --text to scan visible content."
        ),
        "blocked": (
            "History/ref probe tokens were found, so no clean blinding proof is claimed. "
            "This advisory helper does not block commits or CI by exit status."
        ),
        "scoped": (
            "This scans visible scenario text and supplied transcripts only; it does not prove "
            "a blind workspace or predict hidden tool behavior."
        ),
    }
    key = "empty" if no_inputs else "blocked" if blockers else "scoped"
    return messages[key]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Find prompt-mutation clean-proof blinding risks.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--scenario-spec", type=Path, action="append", help="Scenario spec JSON to scan.")
    parser.add_argument("--transcript", type=Path, action="append", help="Captured transcript text to scan.")
    parser.add_argument("--text", type=Path, action="append", help="Additional text file to scan.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = run(args)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for finding in report["findings"]:
            print(
                f"{finding['severity']}: {finding['source']} {finding['field']} "
                f"{finding['line']}:{finding['column']} {finding['rule']} ({finding['match']})"
            )
        if report["no_inputs"]:
            print("prompt-mutation clean-proof preflight: no input files supplied; no clean-proof claim made")
        elif not report["findings"]:
            print("prompt-mutation clean-proof preflight: no visible git history/ref probe tokens found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
