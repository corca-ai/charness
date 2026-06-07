#!/usr/bin/env python3
"""Cheap upstream pre-check: surface test assertions that pin doc/SKILL prose or
paths before the broad pytest / mutation-coverage producer pays for the failure.

Editing prose in a doc or SKILL.md, or renaming/deleting one, frequently breaks a
literal-string assertion in ``tests/`` that copied that prose or referenced that
path. The broad suite catches it minutes later. This checker reads the
working-tree diff against HEAD and reports the likely-broken pins up front so the
fix happens before the expensive cycle.

Two signals, both keyed off the current (uncommitted) diff:

- prose pin: a ``tests/`` string literal that is a verbatim substring of a line
  the diff removed/changed from a doc/SKILL ``.md`` file.
- path pin: a ``tests/`` literal reference to a doc/SKILL path the diff deleted
  or renamed away.

Advisory by default (prints findings, exit 0); ``--strict`` exits non-zero so a
caller can gate on it. The substring/path heuristic can over-report, so the
default stays advisory per the proportionality guidance in
docs/conventions/authoring-preflight.md.
"""
from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

# Prose pins copy a human phrase; require length + whitespace so identifiers,
# short tokens, and bare paths do not masquerade as prose matches.
MIN_PROSE_LENGTH = 24
DOC_SUFFIXES = (".md",)


def _git(repo_root: Path, *args: str) -> str | None:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout if result.returncode == 0 else None


def _is_doc_path(path: str) -> bool:
    return path.endswith(DOC_SUFFIXES)


def changed_status(repo_root: Path) -> list[tuple[str, str, str]]:
    """``(status, old_path, new_path)`` rows for the uncommitted diff vs HEAD.

    Rename detection (-M) is on, so a moved doc surfaces as an ``R`` row carrying
    both the gone-away source and the destination.
    """
    out = _git(repo_root, "diff", "--name-status", "-M", "HEAD")
    if out is None:
        return []
    rows: list[tuple[str, str, str]] = []
    for line in out.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        code = parts[0]
        if code.startswith("R") and len(parts) >= 3:
            rows.append(("R", parts[1], parts[2]))
        elif len(parts) >= 2:
            rows.append((code[0], parts[1], parts[1]))
    return rows


def removed_lines(repo_root: Path, path: str) -> list[str]:
    """Lines the working-tree diff removed/changed from ``path`` vs HEAD."""
    out = _git(repo_root, "diff", "--unified=0", "HEAD", "--", path)
    if out is None:
        return []
    removed: list[str] = []
    # Collect "-" body lines only inside a hunk: the ``--- a/path`` / ``+++ b/path``
    # file headers precede the first ``@@``, so gating on the hunk boundary keeps a
    # removed content line that itself starts with ``--`` from being mistaken for a
    # header.
    in_hunk = False
    for line in out.splitlines():
        if line.startswith("@@"):
            in_hunk = True
            continue
        if in_hunk and line.startswith("-"):
            stripped = line[1:].strip()
            if stripped:
                removed.append(stripped)
    return removed


def test_string_literals(test_roots: list[Path]) -> list[tuple[str, Path, int]]:
    literals: list[tuple[str, Path, int]] = []
    for root in test_roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.py")):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except (SyntaxError, UnicodeDecodeError):
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    literals.append((node.value, path, getattr(node, "lineno", 0)))
    return literals


def _prose_candidate(literal: str) -> bool:
    return len(literal) >= MIN_PROSE_LENGTH and " " in literal.strip()


def find_prose_pins(
    repo_root: Path,
    doc_paths: list[str],
    literals: list[tuple[str, Path, int]],
) -> list[dict[str, Any]]:
    removed_by_doc = {path: "\n".join(removed_lines(repo_root, path)) for path in doc_paths}
    removed_by_doc = {path: blob for path, blob in removed_by_doc.items() if blob}
    findings: list[dict[str, Any]] = []
    for literal, test_path, lineno in literals:
        if not _prose_candidate(literal):
            continue
        for doc_path, blob in removed_by_doc.items():
            if literal in blob:
                findings.append(
                    {
                        "kind": "prose",
                        "doc": doc_path,
                        "test": test_path.relative_to(repo_root).as_posix(),
                        "line": lineno,
                        "phrase": literal if len(literal) <= 100 else literal[:97] + "...",
                    }
                )
                break
    return findings


def find_path_pins(
    repo_root: Path,
    gone_paths: list[str],
    test_files: list[Path],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    cache: dict[Path, str] = {}
    for path in gone_paths:
        for test_path in test_files:
            text = cache.get(test_path)
            if text is None:
                try:
                    text = test_path.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    text = ""
                cache[test_path] = text
            if path in text:
                line = next(
                    (i + 1 for i, row in enumerate(text.splitlines()) if path in row),
                    0,
                )
                findings.append(
                    {
                        "kind": "path",
                        "doc": path,
                        "test": test_path.relative_to(repo_root).as_posix(),
                        "line": line,
                        "phrase": path,
                    }
                )
    return findings


def build_report(
    repo_root: Path,
    *,
    paths: list[str] | None,
    test_roots: list[Path],
) -> dict[str, Any]:
    rows = changed_status(repo_root)
    if paths is not None:
        wanted = set(paths)
        rows = [row for row in rows if row[1] in wanted or row[2] in wanted]
    changed_docs = [new for code, _old, new in rows if code != "D" and _is_doc_path(new)]
    gone_docs = [old for code, old, _new in rows if code in {"D", "R"} and _is_doc_path(old)]
    literals = test_string_literals(test_roots)
    test_files = sorted({path for _literal, path, _line in literals})
    prose = find_prose_pins(repo_root, changed_docs, literals)
    path_pins = find_path_pins(repo_root, gone_docs, test_files)
    findings = prose + path_pins
    return {
        "status": "findings" if findings else "clean",
        "changed_docs": changed_docs,
        "gone_docs": gone_docs,
        "findings": findings,
    }


def format_human(report: dict[str, Any]) -> str:
    if report["status"] == "clean":
        return "prose-pin: no likely test pins on changed doc/SKILL surfaces."
    lines = [
        f"WARN: prose-pin found {len(report['findings'])} likely test pin(s) on "
        "changed doc/SKILL surfaces (fix before the broad suite pays for it):"
    ]
    for finding in report["findings"]:
        if finding["kind"] == "prose":
            lines.append(
                f"- {finding['test']}:{finding['line']} pins prose from "
                f"{finding['doc']}: \"{finding['phrase']}\""
            )
        else:
            lines.append(
                f"- {finding['test']}:{finding['line']} references "
                f"renamed/deleted path {finding['doc']}"
            )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--paths",
        nargs="*",
        help="Restrict to these changed paths (defaults to the full uncommitted diff).",
    )
    parser.add_argument(
        "--tests-root",
        action="append",
        default=None,
        help="Test root to scan for pins (repeatable; defaults to tests/).",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when likely pins are found (default advisory exit 0).",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    test_root_names = args.tests_root if args.tests_root else ["tests"]
    test_roots = [repo_root / name for name in test_root_names]
    report = build_report(repo_root, paths=args.paths, test_roots=test_roots)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_human(report))
    if args.strict and report["status"] == "findings":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
