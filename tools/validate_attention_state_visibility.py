#!/usr/bin/env python3

"""Ensure exit-zero attention states are declared as visible or intentionally local.

This closes the recurrence class behind issue #175: a helper can return
`no_adapter`, `disabled`, `not_configured`, `not_evaluable`, or `skipped` with
exit 0, and the state can quietly read as a clean pass unless the command
surface makes the attention state visible or declares why it is not a closeout
signal.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from yaml_output import emit_yaml

DEFAULT_DECLARATION_PATH = "skills/public/quality/references/attention-state-visibility.json"
DEFAULT_SCAN_ROOTS = ("scripts", "tools", "skills/public", "skills/shared", "skills/support")
PLUGIN_DECLARATION_PATH = "skills/quality/references/attention-state-visibility.json"
ATTENTION_TERMS = (
    "no_adapter",
    "no_records",
    "disabled",
    "not_configured",
    "not_evaluable",
    "skipped",
    "advisory-only",
    "prose_review_status",
)
EXCLUDED_PATHS = {
    "tools/validate_attention_state_visibility.py",
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


@dataclass(frozen=True)
class ScanRoot:
    source: Path
    display_prefix: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--declaration-path", type=Path)
    parser.add_argument("--scan-root", action="append", type=Path, default=[])
    parser.add_argument(
        "--scan-root-map",
        action="append",
        default=[],
        metavar="SOURCE=DISPLAY_PREFIX",
        help="Scan SOURCE while rendering detected files under DISPLAY_PREFIX in declarations.",
    )
    return parser.parse_args()


def _portable_path(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root).as_posix()


# What separates a status VALUE from English prose that happens to use the word.
#
# A status is a TOKEN: the whole string is the state (`"skipped"`), or the state
# is one delimiter-separated part of a state-shaped token (`"silently-skipped"`).
# English prose is a sentence -- it has spaces, and the word inside it is being
# used, not assigned.
#
# The gate scanned every string constant for the term as a SUBSTRING, so a
# docstring explaining that something may be skipped tripped a check about
# exit-zero status values. Twice recorded (#302's `silently-skipped` docstring,
# and a parsing docstring). Both are prose; neither could ever be read as a state
# by anything, which is why neither was a real finding.
_TOKEN_SPLIT = re.compile(r"[^A-Za-z0-9]+")
# A labelled field: `WARNING: skipped`, `status=not_configured`, `a; b`. Each side
# is examined on its own, so a state carrying its visibility prefix still reads as
# a state while the surrounding sentence does not.
_FIELD_SPLIT = re.compile(r"[:=;,()\[\]{}\"\']|\s-\s")


def _is_status_value(value: str, term: str) -> bool:
    """Is `term` used as a STATE in `value`, rather than as a word in a sentence?

    A state is token-shaped. It appears either as the whole value (`"skipped"`),
    as one part of a state-shaped token (`"silently-skipped"`), or as one side of
    a labelled field (`"WARNING: skipped"`, `"status=not_configured"`) -- which is
    a state WITH its visibility marker, exactly the shape this gate wants declared.

    An English sentence is not a state, however many of the words match.
    """
    term_parts = [part for part in _TOKEN_SPLIT.split(term) if part]
    if not term_parts:
        return False
    for field in _FIELD_SPLIT.split(value):
        stripped = field.strip()
        if not stripped or any(character.isspace() for character in stripped):
            continue  # a phrase, not a state token
        value_parts = [part for part in _TOKEN_SPLIT.split(stripped) if part]
        for index in range(len(value_parts) - len(term_parts) + 1):
            if value_parts[index : index + len(term_parts)] == term_parts:
                return True
    return False


def _docstring_nodes(tree: ast.AST) -> set[int]:
    """Every constant that IS a docstring, by identity.

    A docstring is documentation; nothing reads it as a state. Excluding it is
    the structural half of the prose/value split above.
    """
    marked: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body = getattr(node, "body", None)
        if not body:
            continue
        first = body[0]
        if (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            marked.add(id(first.value))
    return marked


def _string_constants(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        raise ValueError(f"cannot parse {path}: {exc}") from exc
    docstrings = _docstring_nodes(tree)
    values: list[str] = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and id(node) not in docstrings
        ):
            values.append(node.value)
    return values


def _scan_root(repo_root: Path, source: Path, display_prefix: Path | None = None) -> ScanRoot:
    absolute_source = source if source.is_absolute() else repo_root / source
    if display_prefix is None:
        # Render detected files under their repo-relative path so declaration
        # keys match regardless of whether --scan-root was given relative or as
        # an absolute path inside the repo.
        try:
            display_prefix = absolute_source.resolve().relative_to(repo_root.resolve())
        except ValueError:
            display_prefix = source
    return ScanRoot(source=absolute_source, display_prefix=display_prefix)


def _sibling_support_root(repo_root: Path) -> Path:
    return repo_root.parent / "charness-support"


def default_scan_roots(repo_root: Path) -> list[ScanRoot]:
    roots = [_scan_root(repo_root, Path("scripts"))]
    if (repo_root / "skills" / "public").is_dir() or (repo_root / "skills" / "support").is_dir():
        roots.extend(
            [
                _scan_root(repo_root, Path("skills/public")),
                _scan_root(repo_root, Path("skills/support")),
            ]
        )
        if (repo_root / "skills" / "shared").is_dir():
            # `skills/shared` carries repo-owned helpers with real attention states --
            # the reviewer-result diagnostic floor counts `skipped_oversized_records`
            # -- and sat outside every source-layout scan root, so its declaration
            # could never be satisfied and read as a stale entry instead of a covered
            # one. The export layout already scanned it via the `skills` branch below.
            roots.append(_scan_root(repo_root, Path("skills/shared")))
    elif (repo_root / "skills").is_dir():
        roots.append(_scan_root(repo_root, Path("skills")))
        sibling_support = _sibling_support_root(repo_root)
        if sibling_support.is_dir():
            roots.append(ScanRoot(source=sibling_support, display_prefix=Path("skills/support")))
    if (repo_root / "support").is_dir():
        roots.append(_scan_root(repo_root, Path("support")))
    return roots


def parse_scan_root_maps(repo_root: Path, values: list[str]) -> list[ScanRoot]:
    roots: list[ScanRoot] = []
    for value in values:
        if "=" not in value:
            raise ValueError(f"--scan-root-map must be SOURCE=DISPLAY_PREFIX, got {value!r}")
        source_raw, display_raw = value.split("=", 1)
        if not source_raw or not display_raw:
            raise ValueError(f"--scan-root-map must be SOURCE=DISPLAY_PREFIX, got {value!r}")
        source = Path(source_raw)
        roots.append(
            ScanRoot(
                source=source if source.is_absolute() else repo_root / source,
                display_prefix=Path(display_raw),
            )
        )
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


def detect_attention_states(
    repo_root: Path,
    scan_roots: list[ScanRoot],
) -> tuple[dict[str, list[str]], dict[str, str], dict[str, Path]]:
    detected: dict[str, list[str]] = {}
    source_paths: dict[str, str] = {}
    source_files: dict[str, Path] = {}
    for root in scan_roots:
        absolute_root = root.source.resolve()
        if not absolute_root.exists():
            continue
        for path in sorted(absolute_root.rglob("*.py")):
            relative_to_scan = path.resolve().relative_to(absolute_root).as_posix()
            relative = (root.display_prefix / relative_to_scan).as_posix()
            if relative in EXCLUDED_PATHS or "__pycache__" in path.parts:
                continue
            constants = _string_constants(path)
            hits = sorted(
                {
                    term
                    for term in ATTENTION_TERMS
                    if any(_is_status_value(value, term) for value in constants)
                }
            )
            if hits:
                key = declaration_key(relative)
                if key in detected and source_paths[key] != relative:
                    raise ValueError(
                        f"duplicate declaration key {key} from {source_paths[key]} and {relative}"
                    )
                detected[key] = hits
                source_paths[key] = relative
                source_files[key] = path
    return detected, source_paths, source_files


def _string_list(value: Any) -> list[str]:
    return value if isinstance(value, list) and all(isinstance(item, str) for item in value) else []


def validate_declaration(
    repo_root: Path,
    declaration_path: Path,
    detected: dict[str, list[str]],
    source_paths: dict[str, str],
    source_files: dict[str, Path],
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
            failures.append(
                f"{path}: unknown visibility value(s): {', '.join(unknown_visibility)}."
            )
        rationale = entry.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            failures.append(f"{path}: rationale must be a non-empty string.")
        evidence_terms = _string_list(entry.get("evidence_terms"))
        if not evidence_terms:
            failures.append(f"{path}: evidence_terms must be a non-empty string list.")
            continue
        source = source_files[path].read_text(encoding="utf-8")
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

    try:
        scan_roots = [
            *[_scan_root(repo_root, root) for root in args.scan_root],
            *parse_scan_root_maps(repo_root, args.scan_root_map),
        ] or default_scan_roots(repo_root)
        detected, source_paths, source_files = detect_attention_states(repo_root, scan_roots)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    failures, raw = validate_declaration(
        repo_root, declaration_path, detected, source_paths, source_files
    )
    payload = {
        "declaration_path": _portable_path(repo_root, declaration_path),
        "scan_roots": [
            {
                "source": str(root.source),
                "display_prefix": root.display_prefix.as_posix(),
            }
            for root in scan_roots
        ],
        "attention_terms": list(ATTENTION_TERMS),
        "detected_file_count": len(detected),
        "declared_file_count": len(raw.get("files", {}))
        if isinstance(raw.get("files"), dict)
        else 0,
        "detected": detected,
        "source_paths": source_paths,
        "failures": failures,
    }
    # Unconditional YAML. The retired human output was the `failures` list on a
    # failing run and a count of `detected` on a passing one; both already live in
    # the payload, so `status` is the only addition needed to keep the verdict
    # readable without re-deriving it from an empty list.
    payload["status"] = "invalid" if failures else "valid"
    emit_yaml(payload)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
