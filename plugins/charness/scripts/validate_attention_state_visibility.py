#!/usr/bin/env python3

"""Ensure exit-zero attention states are declared as visible or intentionally local.

This closes the recurrence class behind issue #175: a helper can return
`no_adapter`, `disabled`, `not_configured`, or `skipped` with exit 0, and the
state can quietly read as a clean pass unless the command surface makes the
attention state visible or declares why it is not a closeout signal.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_DECLARATION_PATH = "skills/public/quality/references/attention-state-visibility.json"
DEFAULT_SCAN_ROOTS = ("scripts", "skills/public", "skills/support")
PLUGIN_DECLARATION_PATH = "skills/quality/references/attention-state-visibility.json"
ATTENTION_TERMS = (
    "no_adapter",
    "disabled",
    "not_configured",
    "skipped",
    "advisory-only",
    "prose_review_status",
)
EXCLUDED_PATHS = {
    "scripts/validate_attention_state_visibility.py",
}
ALLOWED_VISIBILITY = {
    "artifact_visible",
    "explicit_skip_summary",
    "hard_failure_or_blocker",
    "local_noop_not_closeout",
    "metric_or_trace",
    "operator_summary",
    "stdout_attention",
    "structured_warning",
    "support_trace",
    "terminal_payload",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--declaration-path", type=Path)
    parser.add_argument("--scan-root", action="append", type=Path, default=[])
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def _portable_path(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root).as_posix()


def _string_constants(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        raise ValueError(f"cannot parse {path}: {exc}") from exc
    values: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            values.append(node.value)
    return values


def default_scan_roots(repo_root: Path) -> list[Path]:
    roots = [Path("scripts")]
    if (repo_root / "skills" / "public").is_dir() or (repo_root / "skills" / "support").is_dir():
        roots.extend([Path("skills/public"), Path("skills/support")])
    elif (repo_root / "skills").is_dir():
        roots.append(Path("skills"))
    if (repo_root / "support").is_dir():
        roots.append(Path("support"))
    return roots


def default_declaration_path(repo_root: Path) -> Path:
    for candidate in (
        repo_root / DEFAULT_DECLARATION_PATH,
        repo_root / PLUGIN_DECLARATION_PATH,
    ):
        if candidate.is_file():
            return candidate
    return repo_root / DEFAULT_DECLARATION_PATH


def declaration_key(relative_path: str) -> str:
    if relative_path.startswith("skills/public/") or relative_path.startswith("skills/support/"):
        return relative_path
    if relative_path.startswith("skills/"):
        return f"skills/public/{relative_path[len('skills/') :]}"
    if relative_path.startswith("support/"):
        return f"skills/support/{relative_path[len('support/') :]}"
    return relative_path


def detect_attention_states(repo_root: Path, scan_roots: list[Path]) -> tuple[dict[str, list[str]], dict[str, str]]:
    detected: dict[str, list[str]] = {}
    source_paths: dict[str, str] = {}
    for root in scan_roots:
        absolute_root = root if root.is_absolute() else repo_root / root
        if not absolute_root.exists():
            continue
        for path in sorted(absolute_root.rglob("*.py")):
            relative = _portable_path(repo_root, path)
            if relative in EXCLUDED_PATHS or "__pycache__" in path.parts:
                continue
            constants = _string_constants(path)
            hits = sorted({term for term in ATTENTION_TERMS if any(term in value for value in constants)})
            if hits:
                key = declaration_key(relative)
                if key in detected and source_paths[key] != relative:
                    raise ValueError(
                        f"duplicate declaration key {key} from {source_paths[key]} and {relative}"
                    )
                detected[key] = hits
                source_paths[key] = relative
    return detected, source_paths


def _string_list(value: Any) -> list[str]:
    return value if isinstance(value, list) and all(isinstance(item, str) for item in value) else []


def validate_declaration(
    repo_root: Path,
    declaration_path: Path,
    detected: dict[str, list[str]],
    source_paths: dict[str, str],
) -> tuple[list[str], dict[str, Any]]:
    if not declaration_path.is_file():
        return [f"{declaration_path.relative_to(repo_root)}: not found"], {}

    raw = json.loads(declaration_path.read_text(encoding="utf-8"))
    entries = raw.get("files", {})
    if not isinstance(entries, dict):
        return ["attention-state declaration must contain a `files` mapping"], raw

    failures: list[str] = []
    detected_paths = set(detected)
    declared_paths = set(entries)

    for path in sorted(detected_paths - declared_paths):
        failures.append(
            f"{path}: attention state(s) {', '.join(detected[path])} are not declared in "
            f"{declaration_path.relative_to(repo_root)}."
        )
    for path in sorted(declared_paths - detected_paths):
        failures.append(
            f"{path}: declared in {declaration_path.relative_to(repo_root)} but no attention "
            "state terms are detected on disk."
        )

    for path in sorted(detected_paths & declared_paths):
        entry = entries.get(path, {})
        if not isinstance(entry, dict):
            failures.append(f"{path}: declaration entry must be an object.")
            continue
        declared_states = sorted(set(_string_list(entry.get("states"))))
        actual_states = detected[path]
        if declared_states != actual_states:
            failures.append(
                f"{path}: declared states {declared_states} do not match detected states {actual_states}."
            )
        visibility = _string_list(entry.get("visibility"))
        if not visibility:
            failures.append(f"{path}: visibility must be a non-empty string list.")
        unknown_visibility = sorted(set(visibility) - ALLOWED_VISIBILITY)
        if unknown_visibility:
            failures.append(f"{path}: unknown visibility value(s): {', '.join(unknown_visibility)}.")
        rationale = entry.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            failures.append(f"{path}: rationale must be a non-empty string.")
        evidence_terms = _string_list(entry.get("evidence_terms"))
        if not evidence_terms:
            failures.append(f"{path}: evidence_terms must be a non-empty string list.")
            continue
        source = (repo_root / source_paths[path]).read_text(encoding="utf-8")
        missing_terms = [term for term in evidence_terms if term not in source]
        if missing_terms:
            failures.append(
                f"{path}: evidence_terms missing from source: {', '.join(repr(term) for term in missing_terms)}."
            )

    return failures, raw


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    declaration_path = (args.declaration_path or default_declaration_path(repo_root)).resolve()
    scan_roots = args.scan_root or default_scan_roots(repo_root)

    try:
        detected, source_paths = detect_attention_states(repo_root, scan_roots)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    failures, raw = validate_declaration(repo_root, declaration_path, detected, source_paths)
    payload = {
        "declaration_path": _portable_path(repo_root, declaration_path),
        "scan_roots": [root.as_posix() for root in scan_roots],
        "attention_terms": list(ATTENTION_TERMS),
        "detected_file_count": len(detected),
        "declared_file_count": len(raw.get("files", {})) if isinstance(raw.get("files"), dict) else 0,
        "detected": detected,
        "source_paths": source_paths,
        "failures": failures,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    elif failures:
        for failure in failures:
            print(failure, file=sys.stderr)
    else:
        print(f"Validated attention-state visibility declarations for {len(detected)} file(s).")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
