#!/usr/bin/env python3
"""Compare the spike commands with their Python owners.

This is deliberately a standalone investigation tool. It imports only the
Python owners (and their stdlib-compatible helpers), invokes the release Rust
binary, and emits a compact semantic difference report. It does not modify
repository files.
"""

from __future__ import annotations

import argparse
import importlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    return parser.parse_args()


def load_owners(repo_root: Path) -> tuple[Any, Any, Any]:
    sys.path.insert(0, str(repo_root))
    return (
        importlib.import_module("scripts.check_export_safe_imports"),
        importlib.import_module("scripts.check_standalone_imports"),
        importlib.import_module("scripts.surfaces_lib"),
    )


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


def write_file_list(root: Path, paths: Iterable[Path], directory: Path) -> Path:
    handle = tempfile.NamedTemporaryFile(prefix="repograph-parity-", suffix=".nul", dir=directory, delete=False)
    try:
        with handle:
            for path in paths:
                handle.write((path.relative_to(root).as_posix()).encode("utf-8"))
                handle.write(b"\0")
    except BaseException:
        Path(handle.name).unlink(missing_ok=True)
        raise
    return Path(handle.name)


def source_line(path: Path, line: int) -> str:
    return path.read_text(encoding="utf-8").splitlines()[line - 1]


def python_violation(message: str, path: Path, root: Path) -> dict[str, Any]:
    match = re.search(r":(\d+):", message)
    line = int(match.group(1)) if match else 0
    if "the path `" in message:
        kind = "forbidden-asset-path"
    elif "import_repo_module" in message:
        kind = "forbidden-import-repo-module"
    elif "`from " in message:
        kind = "forbidden-from-import"
    elif "`import " in message:
        kind = "forbidden-import"
    else:
        kind = "owner-error"
    return {
        "path": path.relative_to(root).as_posix(),
        "line": line,
        "kind": kind,
        "source": source_line(path, line) if line else "",
    }


def python_file_result(owner: Any, path: Path, root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Enumerate a fail-fast owner's complete offender set.

    Each reported offending line is excluded in a temporary copy, and the
    owner is rerun until that copy passes. This preserves the owner's detector
    and makes multi-violation fixtures set-comparable without changing it.
    """

    original = path.read_text(encoding="utf-8")
    working_lines = original.splitlines(keepends=True)
    violations: list[dict[str, Any]] = []
    unestablished: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="repograph-owner-") as temp_dir:
        temp_path = Path(temp_dir) / path.name
        seen: set[tuple[int, str]] = set()
        while True:
            temp_path.write_text("".join(working_lines), encoding="utf-8")
            try:
                owner.validate_imports(temp_path)
            except SyntaxError as exc:
                unestablished.append(
                    {"path": path.relative_to(root).as_posix(), "status": "parse-error", "detail": str(exc)}
                )
                break
            except owner.ValidationError as exc:
                violation = python_violation(str(exc), path, root)
                key = (violation["line"], violation["kind"])
                if key in seen:
                    break
                seen.add(key)
                violations.append(violation)
                if violation["line"] <= 0 or violation["line"] > len(working_lines):
                    break
                newline = "\n" if working_lines[violation["line"] - 1].endswith("\n") else ""
                working_lines[violation["line"] - 1] = "pass" + newline
                continue
            break
    return violations, unestablished


def python_export(owner: Any, root: Path, paths: list[Path]) -> dict[str, Any]:
    violations: list[dict[str, Any]] = []
    unestablished: list[dict[str, Any]] = []
    for path in paths:
        file_violations, file_unestablished = python_file_result(owner, path, root)
        violations.extend(file_violations)
        unestablished.extend(file_unestablished)
    violations.sort(key=lambda item: (item["path"], item["line"], item["kind"], item["source"]))
    return {
        "exit_class": 1 if violations or unestablished else 0,
        "verdict": "fail" if violations or unestablished else "pass",
        "files_total": len(paths),
        "violations": violations,
        "unestablished": unestablished,
    }


def rust_export(binary: Path, root: Path, paths: list[Path], temp_root: Path) -> dict[str, Any]:
    file_list = write_file_list(root, paths, temp_root)
    try:
        exit_class, payload = run_rust(
            binary,
            ["export-safe", "--repo-root", str(root), "--file-list", str(file_list)],
        )
    finally:
        file_list.unlink(missing_ok=True)
    payload = dict(payload)
    payload["exit_class"] = exit_class
    payload["verdict"] = "fail" if exit_class == 1 else "pass" if exit_class == 0 else "unestablished"
    return payload


def export_fixture_cases(repo_root: Path, owner: Any, binary: Path, temp_root: Path) -> list[dict[str, Any]]:
    fixtures = repo_root / "native" / "repograph" / "fixtures"
    cases = []
    for expected_path in sorted((fixtures / "expected").glob("export_safe_*.json")):
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        fixture_rel = Path(expected["fixture"])
        fixture = fixtures / fixture_rel
        case_root = fixtures / fixture_rel.parts[0]
        case_relative = Path(*fixture_rel.parts[1:])
        python_result = python_export(owner, case_root, [fixture])
        rust_result = rust_export(binary, case_root, [fixture], temp_root)
        expected_violations = [
            {"path": case_relative.as_posix(), **item}
            for item in expected["violations"]
        ]
        expected_violations.sort(key=lambda item: (item["path"], item["line"], item["kind"], item["source"]))
        cases.append(
            {
                "case": expected_path.stem,
                "python": python_result,
                "rust": rust_result,
                "expected": expected_violations,
            }
        )
    return cases


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


def target_projection(root: Path, owner: Any, paths: list[Path]) -> dict[str, Any]:
    targets = []
    for path in paths:
        shapes = owner._probe_commands(root, path)
        targets.append(
            {
                "module": path.stem,
                "path": path.relative_to(root).as_posix(),
                "shapes": [shape for shape, _command in shapes],
            }
        )
    return {"targets": targets, "discovered": len(paths), "exit_class": 0}


def rust_standalone(
    binary: Path,
    root: Path,
    temp_root: Path,
    changed: list[str] | None = None,
) -> dict[str, Any]:
    all_files = [path for path in root.rglob("*") if path.is_file()]
    file_list = write_file_list(root, all_files, temp_root)
    try:
        args = ["standalone-targets", "--repo-root", str(root), "--file-list", str(file_list)]
        if changed is not None:
            args += ["--changed", *changed]
        exit_class, report = run_rust(binary, args)
    finally:
        file_list.unlink(missing_ok=True)
    return {
        "exit_class": exit_class,
        "discovered": report["discovered"],
        "targets": [
            {
                "module": target["module"],
                "path": target["path"],
                "shapes": [shape["shape"] for shape in target["shapes"]],
            }
            for target in report["targets"]
        ],
        "scope": report["scope"],
        "unmatched_changed": report["unmatched_changed"],
    }


def changed_owner_targets(root: Path, owner: Any, changed: list[str]) -> list[Path]:
    discovered = owner.discover_modules(root)
    wanted: dict[Path, Path] = {}
    for value in changed:
        path = Path(value)
        wanted[path.resolve() if path.is_absolute() else (root / path).resolve()] = path
    by_resolved = {path.resolve(): path for path in discovered}
    return [by_resolved[key] for key in wanted if key in by_resolved]


def standalone_fixture_case(repo_root: Path, owner: Any, binary: Path, temp_root: Path) -> dict[str, Any]:
    fixtures = repo_root / "native" / "repograph" / "fixtures"
    fixture_root = fixtures / "standalone_targets"
    expected = json.loads((fixtures / "expected" / "standalone_targets.json").read_text(encoding="utf-8"))
    python_paths = owner.discover_modules(fixture_root)
    python_report = target_projection(fixture_root, owner, python_paths)
    rust_report = rust_standalone(binary, fixture_root, temp_root)
    changed = expected["changed_order"] + [expected["changed_order"][0]]
    python_changed = target_projection(
        fixture_root, owner, changed_owner_targets(fixture_root, owner, changed)
    )
    rust_changed = rust_standalone(binary, fixture_root, temp_root, changed)
    return {
        "case": "standalone_targets_fixture",
        "python": {**python_report, "changed": python_changed["targets"]},
        "rust": {**rust_report, "changed": rust_changed["targets"]},
        "expected": expected,
    }


def whole_repo_surface(owner: Any, root: Path, binary: Path) -> dict[str, Any]:
    sample = [
        "README.md",
        "AGENTS.md",
        "scripts/check_export_safe_imports.py",
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


def whole_repo_standalone(owner: Any, root: Path, binary: Path) -> dict[str, Any]:
    paths = owner.discover_modules(root)
    python_report = target_projection(root, owner, paths)
    rust_exit, report = run_rust(binary, ["standalone-targets", "--repo-root", str(root)])
    rust_report = {
        "exit_class": rust_exit,
        "discovered": report["discovered"],
        "targets": [
            {
                "module": target["module"],
                "path": target["path"],
                "shapes": [shape["shape"] for shape in target["shapes"]],
            }
            for target in report["targets"]
        ],
    }
    return {"python": python_report, "rust": rust_report}


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


def compare_export_case(differences: list[dict[str, Any]], case: dict[str, Any]) -> None:
    python_result = {
        "exit_class": case["python"]["exit_class"],
        "verdict": case["python"]["verdict"],
        "violations": case["python"]["violations"],
        "unestablished": case["python"]["unestablished"],
    }
    rust_result = {
        "exit_class": case["rust"]["exit_class"],
        "verdict": case["rust"]["verdict"],
        "violations": case["rust"]["violations"],
        "unestablished": case["rust"]["unestablished"],
    }
    add_difference(differences, "export-safe", case["case"], python_result, rust_result)
    add_difference(differences, "export-safe", case["case"] + ":expected", case["expected"], case["rust"]["violations"])


def compare_surface_case(differences: list[dict[str, Any]], case: dict[str, Any]) -> None:
    python_result = case["python"]
    rust_result = case["rust"]
    add_difference(differences, "match-surfaces", case["case"], python_result, rust_result)
    expected = case["expected"]
    actual = {key: rust_result[key] for key in expected}
    add_difference(differences, "match-surfaces", case["case"] + ":expected", expected, actual)


def compare_standalone_case(differences: list[dict[str, Any]], case: dict[str, Any]) -> None:
    python_result = {
        "exit_class": case["python"]["exit_class"],
        "discovered": case["python"]["discovered"],
        "targets": case["python"]["targets"],
        "changed": case["python"]["changed"],
    }
    rust_result = {
        "exit_class": case["rust"]["exit_class"],
        "discovered": case["rust"]["discovered"],
        "targets": case["rust"]["targets"],
        "changed": case["rust"]["changed"],
    }
    add_difference(differences, "standalone-targets", case["case"], python_result, rust_result)
    expected = {
        "targets": case["expected"]["targets"],
        "changed_order": case["expected"]["changed_order"],
    }
    actual = {
        "targets": case["rust"]["targets"],
        "changed_order": [target["path"] for target in case["rust"]["changed"]],
    }
    add_difference(differences, "standalone-targets", case["case"] + ":expected", expected, actual)


def main() -> int:
    args = parse_args()
    root = args.repo_root.expanduser().resolve()
    binary = rust_binary(root)
    export_owner, standalone_owner, surfaces_owner = load_owners(root)
    differences: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="repograph-parity-") as temp_dir:
        temp_root = Path(temp_dir)
        for case in export_fixture_cases(root, export_owner, binary, temp_root):
            compare_export_case(differences, case)
        compare_surface_case(differences, surface_fixture_case(root, surfaces_owner, binary))
        compare_standalone_case(
            differences,
            standalone_fixture_case(root, standalone_owner, binary, temp_root),
        )

        export_paths = export_owner.iter_python_targets(root)
        python_whole_export = python_export(export_owner, root, export_paths)
        rust_exit, rust_payload = run_rust(binary, ["export-safe", "--repo-root", str(root)])
        rust_whole_export = {
            "exit_class": rust_exit,
            "verdict": "fail" if rust_exit == 1 else "pass" if rust_exit == 0 else "unestablished",
            "files_total": rust_payload["files_total"],
            "violations": rust_payload["violations"],
            "unestablished": rust_payload["unestablished"],
        }
        add_difference(
            differences,
            "export-safe",
            "whole-repo",
            python_whole_export,
            rust_whole_export,
        )

        whole_surfaces = whole_repo_surface(surfaces_owner, root, binary)
        add_difference(
            differences,
            "match-surfaces",
            "whole-repo",
            whole_surfaces["python"],
            whole_surfaces["rust"],
        )
        whole_standalone = whole_repo_standalone(standalone_owner, root, binary)
        add_difference(
            differences,
            "standalone-targets",
            "whole-repo",
            whole_standalone["python"],
            whole_standalone["rust"],
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
