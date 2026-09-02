#!/usr/bin/env python3
"""Compare the native commands with the Python owners that still exist.

This is deliberately a standalone investigation tool. It imports only the
Python owners (and their stdlib-compatible helpers), invokes the release Rust
binary, and emits a compact semantic difference report. It does not modify
repository files.

The `export-safe` arm is gone: #748 slice 1 deleted
`scripts/check_export_safe_imports.py` and made the native command the only
owner, so there is no second implementation left to compare against. The
harness kept importing the deleted module and therefore refused to run at all,
which is why the arms that DO have a live Python owner had gone unmeasured.
Comparison belongs before an ownership switch, not after it.
"""

from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    return parser.parse_args()


def load_owners(repo_root: Path) -> Any:
    """`surfaces_lib` is the last Python owner with a native counterpart.

    `check_standalone_imports` was also compared here until slice 1 moved target
    SELECTION to `repograph standalone-targets`; what remains in Python is the
    runtime import probe, which has no native counterpart to disagree with.
    """

    sys.path.insert(0, str(repo_root))
    return importlib.import_module("scripts.adapters.surfaces_lib")


def rust_binary(repo_root: Path) -> Path:
    binary = repo_root / "native" / "repograph" / "target" / "release" / "repograph"
    if binary.is_file():
        return binary
    result = subprocess.run(
        ["cargo", "build", "--release", "--offline"],
        cwd=repo_root / "native" / "repograph",
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "cargo build failed")
    return binary


def run_rust(binary: Path, args: list[str]) -> tuple[int, dict[str, Any]]:
    result = subprocess.run([str(binary), *args], check=False, capture_output=True, text=True)
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Rust command did not emit one JSON document (exit {result.returncode}): "
            f"{result.stdout!r}; stderr={result.stderr!r}"
        ) from exc
    return result.returncode, payload


def surface_projection(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "changed_paths": report["changed_paths"],
        "matched_surface_ids": [item["surface_id"] for item in report["matched_surfaces"]],
        "sync_commands": report["sync_commands"],
        "verify_commands": report["verify_commands"],
        "unmatched_paths": report["unmatched_paths"],
    }


def surface_fixture_case(repo_root: Path, owner: Any, binary: Path) -> dict[str, Any]:
    fixtures = repo_root / "native" / "repograph" / "fixtures"
    fixture_root = fixtures / "match_surfaces"
    expected = json.loads((fixtures / "expected" / "match_surfaces.json").read_text(encoding="utf-8"))
    manifest = owner.load_surfaces(fixture_root, surfaces_path=Path("surfaces.json"))
    python_report = owner.match_surfaces(manifest, expected["paths"])
    rust_exit, rust_report = run_rust(
        binary,
        [
            "match-surfaces",
            "--repo-root",
            str(fixture_root),
            "--surfaces",
            "surfaces.json",
            *sum((["--path", path] for path in expected["paths"]), []),
        ],
    )
    return {
        "case": "match_surfaces_fixture",
        "python": {"exit_class": 0, **surface_projection(python_report)},
        "rust": {"exit_class": rust_exit, **surface_projection(rust_report)},
        "expected": {key: expected[key] for key in expected if key != "paths"},
    }


def whole_repo_surface(owner: Any, root: Path, binary: Path) -> dict[str, Any]:
    sample = [
        "README.md",
        "AGENTS.md",
        "scripts/adapters/surfaces_lib.py",
        "docs/index.md",
    ]
    python_manifest = owner.load_surfaces(root)
    python_report = owner.match_surfaces(python_manifest, sample)
    rust_exit, rust_report = run_rust(
        binary,
        ["match-surfaces", "--repo-root", str(root), *sum((["--path", path] for path in sample), [])],
    )
    return {
        "python": {"exit_class": 0, **surface_projection(python_report)},
        "rust": {"exit_class": rust_exit, **surface_projection(rust_report)},
    }


def add_difference(
    differences: list[dict[str, Any]],
    command: str,
    case: str,
    python_result: Any,
    rust_result: Any,
) -> None:
    if python_result != rust_result:
        differences.append(
            {
                "command": command,
                "case": case,
                "python_result": python_result,
                "rust_result": rust_result,
            }
        )


def compare_surface_case(differences: list[dict[str, Any]], case: dict[str, Any]) -> None:
    python_result = case["python"]
    rust_result = case["rust"]
    add_difference(differences, "match-surfaces", case["case"], python_result, rust_result)
    expected = case["expected"]
    actual = {key: rust_result[key] for key in expected}
    add_difference(differences, "match-surfaces", case["case"] + ":expected", expected, actual)


def main() -> int:
    args = parse_args()
    root = args.repo_root.expanduser().resolve()
    binary = rust_binary(root)
    surfaces_owner = load_owners(root)
    differences: list[dict[str, Any]] = []
    compare_surface_case(differences, surface_fixture_case(root, surfaces_owner, binary))
    whole_surfaces = whole_repo_surface(surfaces_owner, root, binary)
    add_difference(
        differences,
        "match-surfaces",
        "whole-repo",
        whole_surfaces["python"],
        whole_surfaces["rust"],
    )

    report = {
        "schema": "repograph.parity.v1",
        "repo_root": str(root),
        "difference_count": len(differences),
        "differences": differences,
    }
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # a harness failure is distinct from a parity difference
        print(json.dumps({"schema": "repograph.parity.v1", "error": str(exc)}))
        raise SystemExit(70)
