#!/usr/bin/env python3
"""Reference gate for unfloored-file drift.

This sample is intentionally generic. Adapt the constants or convert them to
CLI arguments inside the target repo.

What it demonstrates:

- enumerate meaningful source files before trusting prior review artifacts
- discover gate scripts by glob instead of a hardcoded tuple
- strip shell comments before matching floored paths
- fail on contradictions: floored and exempted at the same time
- keep a warn band visible on stderr even when the gate passes
- cross-check inventory-discovered gate scripts with lefthook and CI references
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
POLICY = {
    "min_statements_threshold": 30,
    "fail_below_pct": 80.0,
    "warn_ceiling_pct": 95.0,
    "exemption_list_path": "scripts/coverage-floor-exemptions.txt",
    "gate_script_pattern": "*-quality-gate.sh",
    "lefthook_path": "lefthook.yml",
    "ci_workflow_glob": ".github/workflows/*.yml",
}
FLOOR_PATH_RE = re.compile(r'"(src/[A-Za-z0-9_./-]+\.py)"')


def strip_shell_comments(text: str) -> str:
    return "\n".join(line.split("#", 1)[0] for line in text.splitlines())


def discover_gate_scripts() -> list[Path]:
    return sorted((REPO_ROOT / "scripts").glob(POLICY["gate_script_pattern"]))


def collect_declared_floors(gate_paths: list[Path]) -> set[str]:
    declared: set[str] = set()
    for gate_path in gate_paths:
        text = strip_shell_comments(gate_path.read_text(encoding="utf-8"))
        for match in FLOOR_PATH_RE.finditer(text):
            declared.add(match.group(1))
    return declared


def collect_exemptions() -> set[str]:
    exemption_path = REPO_ROOT / POLICY["exemption_list_path"]
    if not exemption_path.is_file():
        return set()
    exempted: set[str] = set()
    for raw in exemption_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        full_path = REPO_ROOT / line
        if not full_path.is_file():
            raise SystemExit(f"FAIL: exemption path does not exist: {line}")
        exempted.add(line)
    return exempted


def load_operational_refs() -> set[str]:
    refs: set[str] = set()
    lefthook_path = REPO_ROOT / POLICY["lefthook_path"]
    if lefthook_path.is_file():
        refs.add(lefthook_path.as_posix())
        refs.update(re.findall(r"scripts/[A-Za-z0-9_./-]+\.sh", lefthook_path.read_text(encoding="utf-8")))
    for workflow in sorted(REPO_ROOT.glob(POLICY["ci_workflow_glob"])):
        refs.add(workflow.as_posix())
        refs.update(re.findall(r"scripts/[A-Za-z0-9_./-]+\.sh", workflow.read_text(encoding="utf-8")))
    return refs


def meta_check_gate_scripts(gate_paths: list[Path]) -> None:
    discovered = {path.relative_to(REPO_ROOT).as_posix() for path in gate_paths}
    refs = load_operational_refs()
    orphaned = sorted(path for path in discovered if path not in refs)
    foreign = sorted(path for path in refs if path.startswith("scripts/") and path.endswith(".sh") and path not in discovered)
    if orphaned or foreign:
        lines = ["FAIL: quality-gate discovery drift detected."]
        if orphaned:
            lines.append("Orphaned discovered gates:")
            lines.extend(f"  - {path}" for path in orphaned)
        if foreign:
            lines.append("Operational refs not matched by gate_script_pattern:")
            lines.extend(f"  - {path}" for path in foreign)
        raise SystemExit("\n".join(lines))


def load_coverage_report() -> dict[str, object]:
    report_path = REPO_ROOT / "coverage.json"
    if not report_path.is_file():
        raise SystemExit("FAIL: expected a repo-owned coverage JSON artifact such as coverage.json")
    return json.loads(report_path.read_text(encoding="utf-8"))


def classify_unfloored_files(report: dict[str, object], declared: set[str], exempted: set[str]) -> tuple[list[str], list[str]]:
    offenders: list[str] = []
    warn_band: list[str] = []
    files = report.get("files", {})
    if not isinstance(files, dict):
        raise SystemExit("FAIL: coverage report did not contain a `files` mapping")
    for path, info in sorted(files.items()):
        if not isinstance(path, str) or not path.startswith("src/") or path in declared or path in exempted:
            continue
        summary = info.get("summary", {}) if isinstance(info, dict) else {}
        statements = int(summary.get("num_statements", 0))
        percent = float(summary.get("percent_covered", 0.0))
        if statements < POLICY["min_statements_threshold"]:
            continue
        if percent < POLICY["fail_below_pct"]:
            offenders.append(f"{path}  stmts={statements} cov={percent:.2f}%")
        elif percent < POLICY["warn_ceiling_pct"]:
            warn_band.append(f"{path}  stmts={statements} cov={percent:.2f}%")
    return offenders, warn_band


def main() -> int:
    gate_paths = discover_gate_scripts()
    if not gate_paths:
        raise SystemExit("FAIL: no gate scripts matched gate_script_pattern")
    for gate_path in gate_paths:
        if not gate_path.is_file():
            raise SystemExit(f"FAIL: gate script path does not exist: {gate_path.relative_to(REPO_ROOT)}")
    meta_check_gate_scripts(gate_paths)

    declared = collect_declared_floors(gate_paths)
    exempted = collect_exemptions()
    contradictions = sorted(declared & exempted)
    if contradictions:
        raise SystemExit(
            "FAIL: the following paths are both floored and exempted:\n"
            + "\n".join(f"  - {path}" for path in contradictions)
        )

    offenders, warn_band = classify_unfloored_files(load_coverage_report(), declared, exempted)
    if warn_band:
        print("WARN: unfloored files in warn-band:", file=sys.stderr)
        for line in warn_band:
            print(f"  - {line}", file=sys.stderr)
    if offenders:
        print("FAIL: unfloored files below fail_below_pct:", file=sys.stderr)
        for line in offenders:
            print(f"  - {line}", file=sys.stderr)
        return 1
    print(
        f"OK: {len(declared)} floored, {len(exempted)} exempted, "
        f"{len(warn_band)} in warn-band."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
