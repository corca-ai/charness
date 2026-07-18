#!/usr/bin/env python3
"""Suggest a focused pytest command for changed-line coverage production."""
from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:  # pragma: no cover - import bootstrap
    sys.path.insert(0, str(REPO_ROOT))

from scripts.mutation_changed_files_lib import changed_pool_files_vs_base  # noqa: E402
from scripts.mutation_coverage_producer import default_mutation_base_sha  # noqa: E402
from scripts.run_standing_pytest import expand_targets  # noqa: E402

HELP_EPILOG = """\
Statuses:
  recommended  all changed mutation-pool files map to standing pytest targets
  partial      at least one changed file maps, and at least one does not
  missing      changed mutation-pool files exist, but none map to standing tests
  noop         no eligible mutation-pool files changed over base -> worktree
  blocked      base discovery failed; pass --base-sha explicitly

Workflow:
  1. Prefer --json when feeding this into closeout automation.
  2. For recommended, pass closeout_args or command to --mutation-coverage-command.
  3. For partial, inspect unmapped_changed_pool_files before trusting the focused
     producer; use broad coverage fallback when those files need proof.
  4. For missing or blocked, run the broad mutation coverage producer instead.
"""


def _module_name(path: str) -> str:
    without_suffix = path[:-3] if path.endswith(".py") else path
    return without_suffix.replace("/", ".")


def _reference_patterns(path: str) -> list[re.Pattern[str]]:
    module = _module_name(path)
    parent, _, name = module.rpartition(".")
    escaped_path = re.escape(path)
    escaped_module = re.escape(module)
    patterns = [
        re.compile(rf"['\"]{escaped_path}['\"]"),
        re.compile(rf"\b{escaped_module}\b"),
        re.compile(
            r"\s*/\s*".join(
                rf"['\"]{re.escape(segment)}['\"]" for segment in path.split("/")
            )
        ),
    ]
    if parent and name:
        patterns.extend(
            [
                re.compile(rf"\bfrom\s+{re.escape(parent)}\s+import\s+.*\b{re.escape(name)}\b"),
                re.compile(rf"\bfrom\s+{escaped_module}\s+import\b"),
                re.compile(rf"\bimport\s+{escaped_module}\b"),
            ]
        )
    return patterns


def _loads_local_sibling(text: str, module_stem: str) -> bool:
    token = re.escape(module_stem)
    return bool(
        re.search(
            rf"(?:load_local_skill_module\([^)]*?,\s*|_load_local_release_module\(\s*|"
            rf"_load_sibling\(\s*(?:[^,)]*?,\s*)?)"
            rf"['\"]{token}['\"]",
            text,
        )
        or re.search(rf"with_name\(\s*['\"]{token}\.py['\"]\s*\)", text)
    )


def _local_loader_ancestor_levels(repo_root: Path, path: str) -> list[list[str]]:
    """Find same-directory loader parents, nearest first."""
    related = {path}
    frontier = {path}
    levels: list[list[str]] = []
    while frontier:
        parents: set[str] = set()
        for child_path in frontier:
            child = Path(child_path)
            directory = repo_root / child.parent
            if not directory.is_dir():
                continue
            for candidate in directory.glob("*.py"):
                relative = candidate.relative_to(repo_root).as_posix()
                if relative in related:
                    continue
                try:
                    text = candidate.read_text(encoding="utf-8")
                except OSError:
                    continue
                if _loads_local_sibling(text, child.stem):
                    parents.add(relative)
        if not parents:
            break
        level = sorted(parents)
        levels.append(level)
        related.update(parents)
        frontier = parents
    return levels


def _candidate_test_paths(repo_root: Path) -> list[str]:
    paths: list[str] = []
    for target in expand_targets(repo_root):
        absolute = repo_root / target
        if absolute.is_dir():
            paths.extend(
                path.relative_to(repo_root).as_posix()
                for path in absolute.rglob("test_*.py")
            )
        elif absolute.name.startswith("test_") and target.endswith(".py") and absolute.is_file():
            paths.append(target)
    return sorted(dict.fromkeys(paths))


def tests_referencing_paths(repo_root: Path, changed_paths: list[str]) -> dict[str, list[str]]:
    tests = _candidate_test_paths(repo_root)
    test_text: dict[str, str] = {}
    for test_path in tests:
        try:
            test_text[test_path] = (repo_root / test_path).read_text(encoding="utf-8")
        except OSError:
            continue
    matches: dict[str, list[str]] = {}
    for changed_path in changed_paths:
        path_levels = [[changed_path], *_local_loader_ancestor_levels(repo_root, changed_path)]
        for level in path_levels:
            patterns = [pattern for related in level for pattern in _reference_patterns(related)]
            found = sorted(
                test_path
                for test_path, text in test_text.items()
                if any(pattern.search(text) for pattern in patterns)
            )
            if found:
                matches[changed_path] = found
                break
    return {path: sorted(paths) for path, paths in matches.items() if paths}


def build_recommendation(repo_root: Path, *, base_sha: str | None = None) -> dict[str, object]:
    base = (base_sha or default_mutation_base_sha(repo_root)).strip()
    if not base:
        return {
            "status": "blocked",
            "reason": "could not resolve merge-base with origin/main; pass --base-sha explicitly",
            "changed_pool_files": [],
        }
    changed = changed_pool_files_vs_base(repo_root, base)
    if not changed:
        return {
            "status": "noop",
            "reason": "no eligible mutation-pool files changed over base -> worktree",
            "base_sha": base,
            "changed_pool_files": [],
        }
    matches = tests_referencing_paths(repo_root, changed)
    missing = [path for path in changed if path not in matches]
    targets = sorted({test_path for paths in matches.values() for test_path in paths})
    if not targets:
        return {
            "status": "missing",
            "reason": (
                "no standing pytest target references the changed pool files or "
                "their local-loader ancestors"
            ),
            "base_sha": base,
            "changed_pool_files": changed,
            "unmapped_changed_pool_files": missing,
        }
    command = shlex.join(
        [
            "python3",
            "scripts/run_standing_pytest.py",
            "--repo-root",
            ".",
            "--mode",
            "read-only",
            *(token for target in targets for token in ("--pytest-target", target)),
        ]
    )
    status = "recommended" if not missing else "partial"
    reason = (
        "nearest direct or local-loader references found in standing pytest targets; "
        "use the command as changed-line coverage evidence while retaining broad proof"
    )
    if status == "partial":
        reason = (
            "textual references found for a subset of changed pool files; the command "
            "only proves mapped files, so inspect unmapped_changed_pool_files or use "
            "the broad coverage fallback"
        )
    return {
        "status": status,
        "reason": reason,
        "base_sha": base,
        "changed_pool_files": changed,
        "mapped_tests_by_file": matches,
        "unmapped_changed_pool_files": missing,
        "command": command,
        "closeout_args": [
            "--produce-mutation-coverage",
            "--mutation-coverage-command",
            command,
        ],
    }


def _format_text_diagnostics(payload: dict[str, object]) -> list[str]:
    status = str(payload["status"])
    reason = str(payload["reason"])
    lines = [f"status: {status}", reason]
    unmapped = payload.get("unmapped_changed_pool_files")
    if isinstance(unmapped, list) and unmapped:
        lines.append("unmapped_changed_pool_files:")
        lines.extend(f"  - {path}" for path in unmapped)
    if status == "partial":
        lines.append(
            "NEXT: pass the printed command only if the mapped subset is enough; "
            "otherwise use the broad coverage fallback."
        )
    elif status == "missing":
        lines.append("NEXT: use the broad coverage fallback; no focused producer was found.")
    elif status == "noop":
        lines.append("NEXT: no mutation coverage producer is needed for this diff.")
    elif status == "blocked":
        lines.append("NEXT: pass --base-sha or ensure origin/main is available.")
    return lines


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=HELP_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--base-sha", default=None)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    repo_root = args.repo_root.resolve()
    payload = build_recommendation(repo_root, base_sha=args.base_sha)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        command = payload.get("command")
        if command:
            print(command)
            if payload["status"] == "partial":
                print("\n".join(_format_text_diagnostics(payload)), file=sys.stderr)
        else:
            print("\n".join(_format_text_diagnostics(payload)), file=sys.stderr)
    return 0 if payload["status"] in {"recommended", "partial", "noop"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
