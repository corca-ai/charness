#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

DEFAULT_PATHS = ("runtime_bootstrap.py", "skill_runtime_bootstrap.py", "scripts", "skills", "tests")
FINDING_RE = re.compile(
    r"^(?P<path>.+?):(?P<line>\d+): (?P<message>.+?) "
    r"\((?P<confidence>\d+)% confidence, (?P<size>\d+) lines?\)$"
)
LIKELY_CONVENTION_NAMES = ("pytest_plugins", "pytestmark")
STRUCTURED_OUTPUT_NAMES = ("rss_kib",)


def git_visible_python_paths(repo_root: Path, roots: tuple[str, ...]) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", "*.py"],
        cwd=repo_root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        return [root for root in roots if (repo_root / root).exists()]
    selected: list[str] = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        rel = raw.decode("utf-8")
        if any(rel == root or rel.startswith(f"{root}/") for root in roots):
            selected.append(rel)
    return sorted(selected)


def classify_finding(message: str) -> str:
    if any(name in message for name in LIKELY_CONVENTION_NAMES):
        return "likely_framework_convention"
    if any(name in message for name in STRUCTURED_OUTPUT_NAMES):
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
        message = match.group("message")
        findings.append(
            {
                "path": match.group("path"),
                "line": int(match.group("line")),
                "message": message,
                "confidence": int(match.group("confidence")),
                "size": int(match.group("size")),
                "classification": classify_finding(message),
            }
        )
    return findings


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
    completed = subprocess.run(command, cwd=repo_root, check=False, capture_output=True, text=True)
    return {
        "confidence": confidence,
        "status": "findings" if completed.returncode == 3 else "clean" if completed.returncode == 0 else "error",
        "command": " ".join(command),
        "exit_code": completed.returncode,
        "findings": parse_findings(completed.stdout),
        "stderr": completed.stderr.strip(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--path", action="append", default=[])
    parser.add_argument("--primary-confidence", type=int, default=80)
    parser.add_argument("--sweep-confidence", type=int, default=60)
    parser.add_argument("--json", action="store_true")
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
    print(f"Primary ({args.primary_confidence}%): {primary['status']} ({len(primary['findings'])} findings)")
    print(f"Sweep ({args.sweep_confidence}%): {sweep['status']} ({len(sweep['findings'])} findings)")
    for finding in sweep["findings"]:
        print(
            f"{finding['path']}:{finding['line']} "
            f"{finding['message']} [{finding['classification']}]"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
