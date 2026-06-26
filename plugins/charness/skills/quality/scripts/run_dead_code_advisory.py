#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from collections import Counter
from pathlib import Path

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
GIT_LIST_TIMEOUT_SECONDS = 30
VULTURE_TIMEOUT_SECONDS = 120


def git_visible_python_paths(repo_root: Path, roots: tuple[str, ...]) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", "*.py"],
            cwd=repo_root,
            check=False,
            capture_output=True,
            timeout=GIT_LIST_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return [root for root in roots if (repo_root / root).exists()]
    if result.returncode != 0:
        return [root for root in roots if (repo_root / root).exists()]
    selected: list[str] = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        rel = raw.decode("utf-8")
        path = repo_root / rel
        if not path.is_file():
            continue
        if any(rel == root or rel.startswith(f"{root}/") for root in roots):
            selected.append(rel)
    return sorted(selected)


def classify_finding(path: str, message: str) -> str:
    name_match = UNUSED_NAME_RE.search(message)
    unused_kind = name_match.group("kind") if name_match else ""
    unused_name = name_match.group("name") if name_match else ""
    lower_path = path.lower()
    lower_name = unused_name.lower()
    in_tests = lower_path.startswith("tests/") or "/tests/" in lower_path or lower_path.endswith("conftest.py")
    if unused_name in LIKELY_CONVENTION_NAMES:
        return "likely_framework_convention"
    if in_tests and lower_path.endswith("conftest.py") and unused_kind == "function":
        return "likely_pytest_fixture"
    if unused_name in MOCK_PROTOCOL_NAMES:
        return "likely_mock_protocol"
    if in_tests and unused_kind in {"attribute", "method", "property"}:
        return "likely_test_protocol"
    if any(term in lower_name or term in lower_path for term in TEST_PROTOCOL_TERMS) and unused_kind in {
        "attribute",
        "method",
        "property",
    }:
        return "likely_test_protocol"
    if unused_name in STRUCTURED_OUTPUT_NAMES:
        return "structured_output_field"
    if "unused attribute" in message:
        return "low_confidence_attribute"
    return "review_candidate"


def parse_findings(stdout: str) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for line in stdout.splitlines():
        match = FINDING_RE.match(line)
        if not match:
            continue
        path = match.group("path")
        message = match.group("message")
        findings.append(
            {
                "path": path,
                "line": int(match.group("line")),
                "message": message,
                "confidence": int(match.group("confidence")),
                "size": int(match.group("size")),
                "classification": classify_finding(path, message),
            }
        )
    return findings


def classification_counts(findings: list[dict[str, object]]) -> dict[str, int]:
    return dict(sorted(Counter(str(finding["classification"]) for finding in findings).items()))


def summarize_run(run: dict[str, object], *, sample_limit: int) -> dict[str, object]:
    findings = list(run.get("findings", []))
    review_candidates = [
        finding for finding in findings if isinstance(finding, dict) and finding.get("classification") == "review_candidate"
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
        "summary_note": "summary is triage output; use --json for full vulture command and findings",
        "repo_root": payload["repo_root"],
        "paths": payload["paths"],
        "git_visible_python_file_count": payload["git_visible_python_file_count"],
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
    try:
        completed = subprocess.run(
            command,
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=VULTURE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        completed = subprocess.CompletedProcess(
            command,
            124,
            str(exc.stdout or ""),
            f"timed out after {VULTURE_TIMEOUT_SECONDS}s",
        )
    findings = parse_findings(completed.stdout)
    return {
        "confidence": confidence,
        "status": "findings" if completed.returncode == 3 else "clean" if completed.returncode == 0 else "error",
        "command": " ".join(command),
        "exit_code": completed.returncode,
        "findings": findings,
        "classification_counts": classification_counts(findings),
        "stderr": completed.stderr.strip(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root for the vulture-backed dead-code advisory scan")
    parser.add_argument("--path", action="append", default=[], help="Repo-relative path to scan for dead code (repeatable; defaults applied if omitted)")
    parser.add_argument("--primary-confidence", type=int, default=80, help="vulture --min-confidence for the high-confidence primary pass")
    parser.add_argument("--sweep-confidence", type=int, default=60, help="vulture --min-confidence for the lower-confidence sweep pass")
    parser.add_argument("--json", action="store_true", help="Emit the full advisory payload as JSON")
    parser.add_argument("--summary", action="store_true", help="Emit compact JSON counts and samples instead of full vulture commands")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    roots = tuple(args.path or DEFAULT_PATHS)
    paths = git_visible_python_paths(repo_root, roots)
    primary = run_vulture(repo_root, paths, confidence=args.primary_confidence)
    sweep = run_vulture(repo_root, paths, confidence=args.sweep_confidence)
    payload = {
        "repo_root": str(repo_root),
        "paths": roots,
        "git_visible_python_file_count": len(paths),
        "primary": primary,
        "sweep": sweep,
        "notes": [
            "Vulture is advisory here; do not treat a clean primary pass as proof that no dead files exist.",
            "The lower-confidence sweep is for cleanup review and will include framework conventions and dynamic-use false positives.",
        ],
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    if args.summary:
        print(json.dumps(summarize(payload), ensure_ascii=False, indent=2))
        return 0
    print(f"Primary ({args.primary_confidence}%): {primary['status']} ({len(primary['findings'])} findings)")
    print(f"Sweep ({args.sweep_confidence}%): {sweep['status']} ({len(sweep['findings'])} findings)")
    if sweep["classification_counts"]:
        counts = ", ".join(f"{name}={count}" for name, count in sweep["classification_counts"].items())
        print(f"Sweep classifications: {counts}")
    ordered = sorted(
        sweep["findings"],
        key=lambda finding: (0 if finding["classification"] == "review_candidate" else 1, str(finding["classification"])),
    )
    for finding in ordered:
        print(f"{finding['path']}:{finding['line']} {finding['message']} [{finding['classification']}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
