#!/usr/bin/env python3
"""Block issue-closeout artifacts whose commit message is not the carrier."""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

_CLOSE_RE = re.compile(
    r"(?i)\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+"
    r"(?:(?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+))?#(?P<number>\d+)\b"
)
_CLASSIFICATION_RE = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?classification\s*:\s*"
    r"(?P<classification>bug|feature|deferred-work|question|decision-needed)\s*$"
)
_COMMENT_LINE_RE = re.compile(r"^\s*#")


def _load_issue_verify_closeout():
    root = Path(__file__).resolve().parents[1]
    candidates = [
        root / "skills" / "public" / "issue" / "scripts" / "issue_verify_closeout.py",
        root / "skills" / "issue" / "scripts" / "issue_verify_closeout.py",
    ]
    module_path = next((path for path in candidates if path.is_file()), candidates[0])
    spec = importlib.util.spec_from_file_location("issue_verify_closeout_commit_msg", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=repo_root, check=False, capture_output=True, text=True)


def _staged_paths(repo_root: Path) -> list[str]:
    result = _run_git(repo_root, "diff", "--cached", "--name-only", "--diff-filter=ACM")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "failed to list staged paths")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _staged_file(repo_root: Path, path: str) -> str:
    result = _run_git(repo_root, "show", f":{path}")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"failed to read staged file {path}")
    return result.stdout


def _strip_commit_comments(body: str) -> str:
    return "\n".join(line for line in body.splitlines() if not _COMMENT_LINE_RE.match(line)).strip() + "\n"


def _strip_code_fences(body: str) -> str:
    lines: list[str] = []
    in_fence = False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(line)
    return "\n".join(lines)


def _issue_closeout_artifacts(repo_root: Path) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    for path in _staged_paths(repo_root):
        if not (path.startswith("charness-artifacts/issue/") and path.endswith(".md")):
            continue
        body = _strip_code_fences(_staged_file(repo_root, path))
        numbers = sorted({int(match.group("number")) for match in _CLOSE_RE.finditer(body)})
        if not numbers:
            continue
        artifacts.append(
            {
                "path": path,
                "numbers": numbers,
                "classification": _infer_classification(body),
            }
        )
    return artifacts


def _infer_classification(body: str) -> str:
    explicit = _CLASSIFICATION_RE.search(body)
    if explicit is not None:
        return explicit.group("classification")
    lowered = body.lower()
    if "root cause:" in lowered or "debug artifact:" in lowered:
        return "bug"
    if "resolution brief:" in lowered or "implementation:" in lowered:
        return "feature"
    if "decision:" in lowered or "answer:" in lowered:
        return "question"
    return "bug"


def evaluate(repo_root: Path, commit_msg_file: Path, repo: str) -> dict[str, Any]:
    artifacts = _issue_closeout_artifacts(repo_root)
    if not artifacts:
        return {"ok": True, "status": "not_applicable", "artifacts": []}

    issue_verify_closeout = _load_issue_verify_closeout()
    commit_msg_file = commit_msg_file.resolve()
    raw_body = commit_msg_file.read_text(encoding="utf-8")
    sanitized_body = _strip_commit_comments(raw_body)
    sanitized_file = commit_msg_file.with_suffix(commit_msg_file.suffix + ".charness-closeout-body")
    sanitized_file.write_text(sanitized_body, encoding="utf-8")
    reports: list[dict[str, Any]] = []
    try:
        for artifact in artifacts:
            report = issue_verify_closeout.verify_closeout(
                repo_root=repo_root,
                repo=repo,
                numbers=artifact["numbers"],
                classification=artifact["classification"],
                carrier="pr-body",
                backend={"id": "gh"},
                body_file=sanitized_file,
            )
            report["carrier"] = "commit-msg"
            report["source_artifact"] = artifact["path"]
            reports.append(report)
    finally:
        try:
            sanitized_file.unlink()
        except FileNotFoundError:
            pass

    ok = all(report.get("ok") for report in reports)
    return {
        "ok": ok,
        "status": "verified" if ok else "failed",
        "artifacts": artifacts,
        "reports": reports,
    }


def _format_failure(report: dict[str, Any]) -> str:
    lines = [
        "charness commit-msg: issue closeout artifact is staged, but the commit message is not a valid closeout carrier.",
    ]
    for item in report.get("reports", []):
        source = item.get("source_artifact", "<unknown>")
        numbers = ", ".join(f"#{number}" for number in item.get("numbers", []))
        lines.append(f"- {source}: {numbers}")
        if item.get("missing_close_keywords"):
            missing = ", ".join(f"#{number}" for number in item["missing_close_keywords"])
            lines.append(f"  missing close keywords: {missing}")
        if item.get("missing_fields"):
            lines.append(f"  missing ledger fields: {', '.join(item['missing_fields'])}")
        critique = item.get("resolution_critique_check", {})
        if not critique.get("ok", True):
            lines.append("  missing/invalid resolution critique evidence")
    lines.append("Put the close keywords and closeout ledger in the commit body, or unstage the issue closeout artifact.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--commit-msg-file", type=Path, required=True)
    parser.add_argument("--repo", default="corca-ai/charness")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    report = evaluate(repo_root, args.commit_msg_file, args.repo)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif not report["ok"]:
        print(_format_failure(report), file=sys.stderr)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"charness commit-msg: {exc}", file=sys.stderr)
        raise SystemExit(1)
