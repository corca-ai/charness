#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import runpy
import shutil
import sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

try:
    from scripts.core.subprocess_guard import run_process
except ImportError:  # flat layout: the script dir is on sys.path, the repo root is not
    _roots = (p for p in Path(__file__).resolve().parents)
    sys.path.insert(0, str(next(r for r in _roots if (r / "scripts" / "core" / "subprocess_guard.py").is_file())))
    from scripts.core.subprocess_guard import run_process

_summary_output = SimpleNamespace(
    **runpy.run_path(str(Path(__file__).with_name("summary_output_lib.py")))
)
_dynamic_entrypoints = SimpleNamespace(
    **runpy.run_path(str(Path(__file__).with_name("dynamic_entrypoint_evidence.py")))
)
_source_roles = SimpleNamespace(
    **runpy.run_path(str(Path(__file__).with_name("source_role_evidence.py")))
)
_inventory = SimpleNamespace(
    **runpy.run_path(str(Path(__file__).with_name("git_inventory_lib.py")))
)
capture_visible_repo_files = _inventory.capture_visible_repo_files
visible_repo_files = _inventory.visible_repo_files

DEFAULT_PATHS = ("runtime_bootstrap.py", "skill_runtime_bootstrap.py", "scripts", "skills", "tests")
FINDING_RE = re.compile(
    r"^(?P<path>.+?):(?P<line>\d+): (?P<message>.+?) "
    r"\((?P<confidence>\d+)% confidence, (?P<size>\d+) lines?\)$"
)
UNUSED_NAME_RE = re.compile(r"unused (?P<kind>\w+) '(?P<name>[^']+)'")
LIKELY_CONVENTION_NAMES = ("pytest_plugins", "pytestmark")
MOCK_PROTOCOL_NAMES = ("side_effect", "return_value", "call_args", "mock_calls")
TEST_PROTOCOL_TERMS = ("fake", "mock", "stub", "driver", "protocol")
STRUCTURED_OUTPUT_NAMES = ("rss_kib",)
SOURCE_SCANNED_CONTRACTS = {}
VULTURE_TIMEOUT_SECONDS = 120
NON_PYTHON_SOURCE_SUFFIXES = frozenset(
    {".c", ".cc", ".cpp", ".go", ".java", ".js", ".jsx", ".kt", ".rs", ".svelte", ".ts", ".tsx"}
)


def git_visible_python_paths(
    repo_root: Path, roots: tuple[str, ...], *, snapshot=None
) -> list[str]:
    listed = visible_repo_files(repo_root, snapshot=snapshot)
    if listed is None:
        return [root for root in roots if (repo_root / root).exists()]
    selected: list[str] = []
    for path in listed:
        if not path.is_file() or path.suffix != ".py":
            continue
        rel = path.relative_to(repo_root).as_posix()
        if any(rel == root or rel.startswith(f"{root}/") for root in roots):
            selected.append(rel)
    return sorted(selected)


def git_visible_non_python_sources(
    repo_root: Path, roots: tuple[str, ...] | None = None, *, snapshot=None
) -> list[str]:
    listed = visible_repo_files(repo_root, snapshot=snapshot)
    if listed is None:
        return []
    selected: list[str] = []
    for path in listed:
        if not path.is_file() or path.suffix.casefold() not in NON_PYTHON_SOURCE_SUFFIXES:
            continue
        rel = path.relative_to(repo_root).as_posix()
        if roots is None or any(rel == root or rel.startswith(f"{root}/") for root in roots):
            selected.append(rel)
    return sorted(selected)


def classify_finding(
    path: str,
    message: str,
    *,
    line: int | None = None,
    dataclass_fields: set[tuple[int, str]] | None = None,
    source_roles: dict[str, set[tuple[int, str]]] | None = None,
) -> str:
    name_match = UNUSED_NAME_RE.search(message)
    unused_kind = name_match.group("kind") if name_match else ""
    unused_name = name_match.group("name") if name_match else ""
    lower_path = path.lower()
    lower_name = unused_name.lower()
    in_tests = (
        lower_path.startswith("tests/")
        or "/tests/" in lower_path
        or lower_path.endswith("conftest.py")
    )
    if unused_name in LIKELY_CONVENTION_NAMES:
        return "likely_framework_convention"
    roles = source_roles or {}
    location = (line, unused_name) if line is not None else None
    if location in roles.get("pytest_fixtures", set()):
        return "likely_pytest_fixture"
    if location in roles.get("visitor_methods", set()):
        return "likely_framework_convention"
    if in_tests and lower_path.endswith("conftest.py") and unused_kind == "function":
        return "likely_pytest_fixture"
    if unused_name in MOCK_PROTOCOL_NAMES:
        return "likely_mock_protocol"
    if in_tests and unused_kind in {"attribute", "method", "property"}:
        return "likely_test_protocol"
    if any(
        term in lower_name or term in lower_path for term in TEST_PROTOCOL_TERMS
    ) and unused_kind in {
        "attribute",
        "method",
        "property",
    }:
        return "likely_test_protocol"
    fields = dataclass_fields if dataclass_fields is not None else set()
    if unused_kind == "variable" and line is not None and (line, unused_name) in (fields or set()):
        return "structured_output_field"
    if unused_kind == "variable" and unused_name in SOURCE_SCANNED_CONTRACTS.get(path, set()):
        return "source_scanned_contract"
    # Preserve context-free direct-call compatibility without affecting AST-aware scans.
    if dataclass_fields is None and unused_name in STRUCTURED_OUTPUT_NAMES:
        return "structured_output_field"
    if "unused attribute" in message:
        return "low_confidence_attribute"
    return "review_candidate"


def parse_findings(
    stdout: str,
    *,
    repo_root: Path | None = None,
    scan_paths: list[str] | None = None,
) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    role_cache: dict[str, dict[str, set[tuple[int, str]]]] = {}
    for line in stdout.splitlines():
        match = FINDING_RE.match(line)
        if not match:
            continue
        path = match.group("path")
        message = match.group("message")
        finding_line = int(match.group("line"))
        if repo_root is not None and path not in role_cache:
            role_cache[path] = _source_roles.source_role_locations(repo_root / path)
        roles = role_cache.get(path)
        fields = roles.get("dataclass_fields") if roles is not None else None
        findings.append(
            {
                "path": path,
                "line": finding_line,
                "message": message,
                "confidence": int(match.group("confidence")),
                "size": int(match.group("size")),
                "classification": classify_finding(
                    path,
                    message,
                    line=finding_line,
                    dataclass_fields=fields,
                    source_roles=roles,
                ),
            }
        )
    if repo_root is None or scan_paths is None:
        return findings
    candidates = {
        (str(finding["path"]), match.group("name"))
        for finding in findings
        if finding["classification"] == "review_candidate"
        and (match := UNUSED_NAME_RE.search(str(finding["message"]))) is not None
        and match.group("kind") in {"function", "method"}
    }
    registered = _dynamic_entrypoints.find_registered_dynamic_entrypoints(
        repo_root,
        candidates,
        scan_paths,
    )
    for finding in findings:
        match = UNUSED_NAME_RE.search(str(finding["message"]))
        key = (str(finding["path"]), match.group("name")) if match is not None else None
        if key in registered:
            finding["classification"] = "registered_dynamic_entrypoint"
    return findings


def classification_counts(findings: list[dict[str, object]]) -> dict[str, int]:
    return dict(sorted(Counter(str(finding["classification"]) for finding in findings).items()))


def summarize_run(run: dict[str, object], *, sample_limit: int) -> dict[str, object]:
    findings = list(run.get("findings", []))
    review_candidates = [
        finding
        for finding in findings
        if isinstance(finding, dict) and finding.get("classification") == "review_candidate"
    ][:sample_limit]
    return {
        "confidence": run.get("confidence"),
        "status": run.get("status"),
        "exit_code": run.get("exit_code"),
        "finding_count": len(findings),
        "classification_counts": run.get("classification_counts", {}),
        "review_candidate_sample": review_candidates,
        "stderr_present": bool(run.get("stderr")),
    }


def summarize(payload: dict[str, object], *, sample_limit: int = 10) -> dict[str, object]:
    return {
        "summary_note": "summary is triage output; use --detail for full vulture command and findings",
        "repo_root": payload["repo_root"],
        "applicability": payload["applicability"],
        "paths": payload["paths"],
        "git_visible_python_file_count": payload["git_visible_python_file_count"],
        "git_visible_non_python_source_count": payload["git_visible_non_python_source_count"],
        "primary": summarize_run(payload["primary"], sample_limit=sample_limit),
        "sweep": summarize_run(payload["sweep"], sample_limit=sample_limit),
        "notes": payload["notes"],
    }


def run_vulture(repo_root: Path, paths: list[str], *, confidence: int) -> dict[str, object]:
    if shutil.which("vulture") is None:
        return {
            "confidence": confidence,
            "status": "missing",
            "command": "vulture",
            "exit_code": None,
            "findings": [],
            "stderr": "vulture is not installed",
        }
    command = ["vulture", *paths, "--min-confidence", str(confidence), "--sort-by-size"]
    completed = run_process(command, cwd=repo_root, timeout_seconds=VULTURE_TIMEOUT_SECONDS)
    findings = parse_findings(completed.stdout, repo_root=repo_root, scan_paths=paths)
    return {
        "confidence": confidence,
        "status": "findings"
        if completed.returncode == 3
        else "clean"
        if completed.returncode == 0
        else "error",
        "command": " ".join(command),
        "exit_code": completed.returncode,
        "findings": findings,
        "classification_counts": classification_counts(findings),
        "stderr": completed.stderr.strip(),
    }


def not_applicable_run(confidence: int) -> dict[str, object]:
    return {
        "confidence": confidence,
        "status": "not-applicable",
        "command": None,
        "exit_code": None,
        "findings": [],
        "classification_counts": {},
        "stderr": "",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        required=True,
        help="Repo root for the vulture-backed dead-code advisory scan",
    )
    parser.add_argument(
        "--path",
        action="append",
        default=[],
        help="Repo-relative path to scan for dead code (repeatable; defaults applied if omitted)",
    )
    parser.add_argument(
        "--primary-confidence",
        type=int,
        default=80,
        help="vulture --min-confidence for the high-confidence primary pass",
    )
    parser.add_argument(
        "--sweep-confidence",
        type=int,
        default=60,
        help="vulture --min-confidence for the lower-confidence sweep pass",
    )
    _summary_output.add_output_args(
        parser,
        summary_help="Emit compact YAML counts and samples instead of full vulture commands",
        detail_help="Emit the full advisory payload as YAML",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    roots = tuple(args.path or DEFAULT_PATHS)
    snapshot = capture_visible_repo_files(repo_root)
    paths = git_visible_python_paths(repo_root, roots, snapshot=snapshot)
    non_python_scope = "requested-roots" if args.path else "repo-wide-default-guard"
    non_python_sources = git_visible_non_python_sources(
        repo_root, roots if args.path else None, snapshot=snapshot
    )
    applicable = bool(paths)
    applicability = (
        "not-applicable-no-python-paths"
        if not applicable
        else "partial-python-only"
        if non_python_sources
        else "applicable-python-scope"
    )
    primary = (
        run_vulture(repo_root, paths, confidence=args.primary_confidence)
        if applicable
        else not_applicable_run(args.primary_confidence)
    )
    sweep = (
        run_vulture(repo_root, paths, confidence=args.sweep_confidence)
        if applicable
        else not_applicable_run(args.sweep_confidence)
    )
    payload = {
        "repo_root": str(repo_root),
        "applicability": applicability,
        "paths": roots,
        "git_visible_python_file_count": len(paths),
        "git_visible_non_python_source_count": len(non_python_sources),
        "non_python_scope": non_python_scope,
        "non_python_source_sample": non_python_sources[:10],
        "primary": primary,
        "sweep": sweep,
        "notes": [
            "Vulture is advisory here; do not treat a clean primary pass as proof that no dead files exist.",
            "The lower-confidence sweep is for cleanup review and will include framework conventions and dynamic-use false positives.",
        ],
    }
    if _summary_output.emit_selected(payload, args, summarize=summarize):
        return 0
    review_candidates = [
        finding for finding in sweep["findings"] if finding["classification"] == "review_candidate"
    ]
    if review_candidates:
        # Surface through run-quality.sh's ADVISORY attention filter so the opt-in
        # gate's findings are visible without --verbose. This never blocks: the gate
        # always exits 0. Only the review_candidate class is called out here; the
        # framework-convention / test-protocol noise classes stay in the detail below.
        print(
            f"ADVISORY: vulture flagged {len(review_candidates)} dead-code review_candidate "
            f"finding(s) of {len(sweep['findings'])} total for separate triage (advisory only, never blocks)."
        )
    if not applicable:
        print(
            "NOT APPLICABLE: no Git-visible Python files matched the requested roots; no dead-code verdict was produced."
        )
    elif non_python_sources:
        print(
            f"PARTIAL: vulture covers {len(paths)} Python file(s), not "
            f"{len(non_python_sources)} Git-visible non-Python source file(s); "
            "no repo-wide dead-code verdict was produced."
        )
    print(
        f"Primary Python scope ({args.primary_confidence}%): {primary['status']} ({len(primary['findings'])} findings)"
    )
    print(
        f"Sweep Python scope ({args.sweep_confidence}%): {sweep['status']} ({len(sweep['findings'])} findings)"
    )
    # `.get`: the vulture-missing run dict has no `classification_counts` key (only
    # the ran-clean/findings/error dicts do). Keying it directly here crashed the human
    # path (exit 1) when vulture was absent, so an opted-in advisory gate falsely turned
    # the run red — the gate must stay exit-0 advisory even with the tool missing.
    classification_counts = sweep.get("classification_counts") or {}
    if classification_counts:
        counts = ", ".join(f"{name}={count}" for name, count in classification_counts.items())
        print(f"Sweep classifications: {counts}")
    ordered = sorted(
        sweep["findings"],
        key=lambda finding: (
            0 if finding["classification"] == "review_candidate" else 1,
            str(finding["classification"]),
        ),
    )
    for finding in ordered:
        print(
            f"{finding['path']}:{finding['line']} {finding['message']} [{finding['classification']}]"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
