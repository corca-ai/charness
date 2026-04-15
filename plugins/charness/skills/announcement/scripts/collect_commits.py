#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def git(*args: str, repo_root: Path) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.stderr.strip() or f"git {' '.join(args)} failed")
    return completed.stdout


def load_last_head(record_path: Path) -> str | None:
    if not record_path.exists():
        return None
    lines = [line for line in record_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        return None
    try:
        payload = json.loads(lines[-1])
    except json.JSONDecodeError:
        return None
    head = payload.get("head_commit")
    return head if isinstance(head, str) and head else None


def collect_commits(repo_root: Path, limit: int) -> dict[str, object]:
    record_path = repo_root / ".charness" / "announcement" / "announcements.jsonl"
    last_head = load_last_head(record_path)
    revision_range = f"{last_head}..HEAD" if last_head else f"-n {limit}"
    if last_head:
        args = ["log", "--reverse", "--format=%H%x1f%s", f"{last_head}..HEAD"]
    else:
        args = ["log", "--reverse", f"-n{limit}", "--format=%H%x1f%s", "HEAD"]
    raw = git(*args, repo_root=repo_root)
    commits = []
    for line in raw.splitlines():
        sha, _, subject = line.partition("\x1f")
        if sha:
            commits.append({"sha": sha, "subject": subject})
    return {
        "last_recorded_head": last_head,
        "record_path": str(record_path.relative_to(repo_root)),
        "revision_range": revision_range,
        "commits": commits,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()
    payload = collect_commits(args.repo_root.resolve(), args.limit)
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
