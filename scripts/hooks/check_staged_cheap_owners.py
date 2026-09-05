#!/usr/bin/env python3
"""Run the cheap owners of staged files; Slice-reopen does not skip these.

``Slice-reopen:`` admits a commit without a release-lane receipt. It must not
also skip the sub-second owners of the files just edited. Those owners are
docs-length, Python tokei caps, and the debug seam-risk index — the class
that turned eight release-lane surprises into a session
(recurrence-class: gate-failures-patched-serially).
"""

from __future__ import annotations

import argparse
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

_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _subprocess_guard.run_process
_plan_helpers = import_repo_module(__file__, "scripts.staged_commit_gate_plan_helpers")
GateCommand = _plan_helpers.GateCommand
collect_staged_scope_paths = _plan_helpers.collect_staged_scope_paths

DEBUG_PREFIX = "charness-artifacts/debug/"


def cheap_owner_gates(
    repo_root: Path, paths: list[str], existing: list[str] | None = None
) -> list[GateCommand]:
    """Path-scoped cheap owners. Deletions still trigger corpus checks."""
    present = existing if existing is not None else [path for path in paths if (repo_root / path).is_file()]
    gates: list[GateCommand] = []
    staged_py = [path for path in present if path.endswith(".py")]
    if staged_py and (repo_root / "scripts/gates/check_code_lengths.py").is_file():
        gates.append(
            GateCommand(
                "check-python-lengths (staged)",
                (
                    "python3",
                    "scripts/gates/check_code_lengths.py",
                    "--repo-root",
                    str(repo_root),
                    "--paths",
                    *staged_py,
                ),
            )
        )
    if any(path.startswith("docs/") and path.endswith(".md") for path in paths) and (
        repo_root / "scripts/gates/check_docs_length.py"
    ).is_file():
        gates.append(
            GateCommand(
                "check-docs-length (staged)",
                (
                    "python3",
                    "scripts/gates/check_docs_length.py",
                    "--repo-root",
                    str(repo_root),
                    "--require-git-file-listing",
                ),
            )
        )
    if any(path.startswith(DEBUG_PREFIX) for path in paths) and (
        repo_root / "scripts/retro_debug/build_debug_seam_risk_index.py"
    ).is_file():
        gates.append(
            GateCommand(
                "validate-debug-seam-index (staged)",
                (
                    "python3",
                    "scripts/retro_debug/build_debug_seam_risk_index.py",
                    "--repo-root",
                    str(repo_root),
                    "--check",
                ),
            )
        )
    if any(path.endswith(".schema.json") for path in paths) and (
        repo_root / "scripts/gates/check_schema_enum_axis.py"
    ).is_file():
        gates.append(
            GateCommand(
                "check-schema-enum-axis (staged)",
                (
                    "python3",
                    "scripts/gates/check_schema_enum_axis.py",
                    "--repo-root",
                    str(repo_root),
                ),
            )
        )
    return gates


def run_cheap_owners(repo_root: Path, paths: list[str] | None = None) -> tuple[int, str]:
    scoped = paths if paths is not None else collect_staged_scope_paths(repo_root)
    existing = [path for path in scoped if (repo_root / path).is_file()]
    for gate in cheap_owner_gates(repo_root, scoped, existing):
        result = run_process(list(gate.argv), cwd=repo_root, timeout_seconds=None)
        if result.returncode != 0:
            body = (result.stderr or result.stdout or "").rstrip()
            return (
                2,
                f"{body}\ncharness pre-commit: cheap owner {gate.label} refused this staged set",
            )
    return 0, ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument(
        "--paths",
        nargs="*",
        default=None,
        help="Repo-relative paths to judge. Default: the staged scope.",
    )
    args = parser.parse_args(argv)
    repo_root = args.repo_root.expanduser().resolve()
    try:
        code, text = run_cheap_owners(repo_root, args.paths)
    except RuntimeError as exc:
        print(f"charness pre-commit: cheap owners unavailable: {exc}", file=sys.stderr)
        return 2
    if text:
        print(text, file=sys.stderr if code else sys.stdout)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
