#!/usr/bin/env python3
"""Refuse a new wall-clock dependency in `tests/`, and let the recorded ones only shrink.

A test whose claim depends on wall-clock time -- a `time.sleep` standing in for
synchronisation, a `time.monotonic` deadline polling for something the child
could signal, an assertion on measured elapsed time -- passes on the machine
that wrote it and fails on a loaded runner. Six scheduled mutation runs in a
row died in their coverage baseline that way (#764), and the operator's rule
on 2026-09-03 was that such a test should not exist: it is rewritten to an
observation the test itself forces, or deleted; never retried, widened, or
deselected (#779).

The census that named every site is `charness-artifacts/goal-runs/775/wall-clock-census.md`;
#780 rewrote the last of them and the baseline has been EMPTY since. The rule
is now simply: any `time.sleep`, `time.monotonic`, or `time.perf_counter` CALL
in a test file is red. The record format is kept so the gate can only ever be
loosened by a named, reviewed entry: a file above its recorded count (zero,
for every file) is red, a file below its count is a prompt to lower the
record, and `--write-baseline` refuses to raise any count. The replacement a
test reaches for is `tests/fifo_witness.py` (block on a FIFO the controlled
child holds) or a controlled clock in the module under test.

What is deliberately outside the rule: a sleep inside a seeded child script is
a string literal, not a call, and the child is the controlled input; a
`time.time()` used as a file age or ordering value is data, not a claim (the
census kept both kinds). Files under a `fixtures` directory are executed as
children, not collected as tests, and are not scanned. An empty matched
universe is a refusal (S40), never a pass.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_repo_file_listing_module = import_repo_module(__file__, "scripts.core.repo_file_listing")
iter_matching_repo_files = _repo_file_listing_module.iter_matching_repo_files

DEFAULT_SCAN_GLOBS = ("tests/*.py", "tests/**/*.py")
DEFAULT_BASELINE_REL = "charness-artifacts/quality/wall-clock-baseline.json"
SKIP_PATH_PARTS = {"__pycache__", "fixtures"}
WALL_CLOCK_CALLS = frozenset({"time.sleep", "time.monotonic", "time.perf_counter"})
BASELINE_SCHEMA = "charness.wall-clock-baseline/v1"


def _dotted(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_dotted(node.value)}.{node.attr}"
    return ""


def wall_clock_sites(source: str, filename: str) -> list[tuple[int, str]]:
    """Every wall-clock call in one module: `(line, dotted name)`.

    Both spellings count: `time.sleep(...)` and a bare `sleep(...)` imported
    from `time`. A string literal that happens to contain `time.sleep` is a
    seeded child's body, not a call, and is not a site.
    """
    tree = ast.parse(source, filename=filename)
    imported: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "time":
            for alias in node.names:
                imported[alias.asname or alias.name] = f"time.{alias.name}"
    sites: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _dotted(node.func)
        resolved = imported.get(name, name)
        if resolved in WALL_CLOCK_CALLS:
            sites.append((node.lineno, resolved))
    return sites


def _iter_scan_paths(repo_root: Path, *, require_git: bool) -> list[Path]:
    paths = iter_matching_repo_files(repo_root, DEFAULT_SCAN_GLOBS, require_git=require_git)
    return [path for path in paths if not (set(path.parts) & SKIP_PATH_PARTS)]


def measure(repo_root: Path, *, require_git: bool) -> tuple[dict[str, list[tuple[int, str]]], int]:
    """Per-file wall-clock sites for every scanned test file, plus the file count."""
    scan_paths = _iter_scan_paths(repo_root, require_git=require_git)
    found: dict[str, list[tuple[int, str]]] = {}
    for path in scan_paths:
        relative = path.relative_to(repo_root).as_posix()
        sites = wall_clock_sites(path.read_text(encoding="utf-8"), str(path))
        if sites:
            found[relative] = sites
    return found, len(scan_paths)


def load_baseline(path: Path) -> dict[str, int]:
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema") != BASELINE_SCHEMA:
        raise SystemExit(f"{path}: not a {BASELINE_SCHEMA} record")
    files = payload.get("files")
    if not isinstance(files, dict) or not all(
        isinstance(k, str) and isinstance(v, int) and v > 0 for k, v in files.items()
    ):
        raise SystemExit(f"{path}: `files` must map test paths to positive site counts")
    return dict(files)


def judge(
    found: dict[str, list[tuple[int, str]]], baseline: dict[str, int]
) -> tuple[list[str], list[str]]:
    """`(failures, shrink_prompts)` for the measured tree against the record."""
    failures: list[str] = []
    prompts: list[str] = []
    for relative, sites in sorted(found.items()):
        allowed = baseline.get(relative, 0)
        if len(sites) > allowed:
            listed = ", ".join(f"{line} {name}" for line, name in sites)
            failures.append(
                f"{relative}: {len(sites)} wall-clock call(s), baseline {allowed} "
                f"(sites: {listed}); a test's claim must not depend on wall-clock time -- "
                "force the observation or delete the test"
            )
        elif len(sites) < allowed:
            prompts.append(f"{relative}: {len(sites)} < baseline {allowed}; lower the record")
    for relative, allowed in sorted(baseline.items()):
        if relative not in found:
            prompts.append(f"{relative}: 0 < baseline {allowed}; drop it from the record")
    return failures, prompts


def write_baseline(
    path: Path, found: dict[str, list[tuple[int, str]]], previous: dict[str, int]
) -> None:
    files = {relative: len(sites) for relative, sites in sorted(found.items())}
    raised = [rel for rel, count in files.items() if count > previous.get(rel, 0) and previous]
    if raised:
        raise SystemExit(
            "refusing to raise the wall-clock baseline for: " + ", ".join(raised) + "; "
            "the record only shrinks"
        )
    payload = {"schema": BASELINE_SCHEMA, "files": files, "total": sum(files.values())}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--require-git-file-listing", action="store_true")
    parser.add_argument("--baseline", type=Path, default=None)
    parser.add_argument("--write-baseline", action="store_true")
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    baseline_path = args.baseline or (repo_root / DEFAULT_BASELINE_REL)
    found, scanned = measure(repo_root, require_git=args.require_git_file_listing)
    if not scanned:
        raise SystemExit(
            "refusing empty matched universe for check_wall_clock_form "
            f"(scan globs: {', '.join(DEFAULT_SCAN_GLOBS)})."
        )
    previous = load_baseline(baseline_path)
    if args.write_baseline:
        write_baseline(baseline_path, found, previous)
        print(
            f"Wrote wall-clock baseline: {sum(len(s) for s in found.values())} site(s) in {len(found)} file(s)."
        )
        return 0
    failures, prompts = judge(found, previous)
    for prompt in prompts:
        print(f"ADVISORY: {prompt}", file=sys.stderr)
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    total = sum(len(sites) for sites in found.values())
    print(
        f"Validated wall-clock form: {scanned} test file(s) scanned, {total} recorded site(s) "
        f"in {len(found)} file(s), none new."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
