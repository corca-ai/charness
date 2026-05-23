#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

TRAILER_RE = re.compile(r"^(?P<key>[A-Za-z][A-Za-z0-9-]*):\s*(?P<value>.+)$")
CLOSING_RE = re.compile(
    r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+"
    r"(?:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)?#\d+\b",
    re.IGNORECASE,
)
MAX_TRAILERS = 20
MAX_TRAILER_VALUE_LENGTH = 400
MAX_CLOSING_REFERENCES = 20


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


def trim_body(body: str, limit: int) -> tuple[str, bool]:
    if limit < 0 or len(body) <= limit:
        return body, False
    return body[:limit].rstrip() + "\n[truncated]", True


def trim_text(text: str, limit: int) -> tuple[str, bool]:
    if limit < 0 or len(text) <= limit:
        return text, False
    return text[:limit].rstrip() + "[truncated]", True


def parse_trailers(body: str) -> tuple[list[dict[str, object]], bool]:
    paragraphs = [paragraph for paragraph in body.strip().split("\n\n") if paragraph.strip()]
    if not paragraphs:
        return [], False
    trailer_lines = [line.strip() for line in paragraphs[-1].splitlines() if line.strip()]
    trailers: list[dict[str, object]] = []
    for line in trailer_lines[:MAX_TRAILERS]:
        match = TRAILER_RE.match(line)
        if not match:
            return [], False
        value, value_truncated = trim_text(match.group("value"), MAX_TRAILER_VALUE_LENGTH)
        raw, raw_truncated = trim_text(line, MAX_TRAILER_VALUE_LENGTH + len(match.group("key")) + 2)
        trailers.append(
            {
                "key": match.group("key"),
                "value": value,
                "raw": raw,
                "truncated": value_truncated or raw_truncated,
            }
        )
    return trailers, len(trailer_lines) > MAX_TRAILERS


def closing_references(body: str) -> tuple[list[str], bool]:
    matches = CLOSING_RE.findall(body)
    return matches[:MAX_CLOSING_REFERENCES], len(matches) > MAX_CLOSING_REFERENCES


def parse_commits(raw: str, body_limit: int) -> list[dict[str, object]]:
    commits: list[dict[str, object]] = []
    for entry in raw.split("\x1e"):
        entry = entry.strip("\n")
        if not entry:
            continue
        sha, sep, rest = entry.partition("\x1f")
        if not sep:
            continue
        parents_raw, _, rest = rest.partition("\x1f")
        subject, _, body = rest.partition("\x1f")
        parents = [parent for parent in parents_raw.split() if parent]
        trimmed_body, body_truncated = trim_body(body.strip(), body_limit)
        trailers, trailers_truncated = parse_trailers(body)
        close_refs, closing_references_truncated = closing_references(f"{subject}\n\n{body}")
        commits.append(
            {
                "sha": sha,
                "subject": subject,
                "parents": parents,
                "is_merge": len(parents) > 1,
                "has_body": bool(body.strip()),
                "body": trimmed_body,
                "body_truncated": body_truncated,
                "trailers": trailers,
                "trailers_truncated": trailers_truncated,
                "closing_references": close_refs,
                "closing_references_truncated": closing_references_truncated,
            }
        )
    return commits


FANOUT_LARGE_WINDOW_THRESHOLD = 30
FANOUT_MEDIUM_WINDOW_THRESHOLD = 15


def build_fanout_hint(commits: list[dict[str, object]]) -> dict[str, object]:
    commit_count = len(commits)
    signals: list[str] = []
    if commit_count >= FANOUT_LARGE_WINDOW_THRESHOLD:
        signals.append(f"large_window: {commit_count} commits >= {FANOUT_LARGE_WINDOW_THRESHOLD}")
    elif commit_count >= FANOUT_MEDIUM_WINDOW_THRESHOLD:
        signals.append(f"medium_window: {commit_count} commits >= {FANOUT_MEDIUM_WINDOW_THRESHOLD}")
    recommended = commit_count >= FANOUT_LARGE_WINDOW_THRESHOLD
    return {
        "commit_count": commit_count,
        "signals": signals,
        "recommended": recommended,
        "reference": "skills/public/announcement/references/large-window-fanout.md",
    }


def collect_commits(
    repo_root: Path,
    limit: int,
    body_limit: int,
    *,
    include_fanout_hint: bool = False,
) -> dict[str, object]:
    record_path = repo_root / ".charness" / "announcement" / "announcements.jsonl"
    last_head = load_last_head(record_path)
    revision_range = f"{last_head}..HEAD" if last_head else f"-n {limit}"
    if last_head:
        args = ["log", "--reverse", "--format=%H%x1f%P%x1f%s%x1f%b%x1e", f"{last_head}..HEAD"]
    else:
        args = ["log", "--reverse", f"-n{limit}", "--format=%H%x1f%P%x1f%s%x1f%b%x1e", "HEAD"]
    raw = git(*args, repo_root=repo_root)
    commits = parse_commits(raw, body_limit)
    payload: dict[str, object] = {
        "last_recorded_head": last_head,
        "record_path": str(record_path.relative_to(repo_root)),
        "revision_range": revision_range,
        "body_limit": body_limit,
        "commits": commits,
    }
    if include_fanout_hint:
        payload["fanout_hint"] = build_fanout_hint(commits)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root whose git log and announcement record are scanned for new commits")
    parser.add_argument("--limit", type=int, default=12, help="Maximum commits to inspect when no previous announcement head is recorded")
    parser.add_argument("--body-limit", type=int, default=1200, help="Maximum commit-body characters to retain before truncation")
    parser.add_argument(
        "--fanout-hint",
        action="store_true",
        help=(
            "emit a `fanout_hint` block with commit count, advisory signals, and a "
            "recommended boolean per skills/public/announcement/references/"
            "large-window-fanout.md heuristics"
        ),
    )
    args = parser.parse_args()
    payload = collect_commits(
        args.repo_root.resolve(),
        args.limit,
        args.body_limit,
        include_fanout_hint=args.fanout_hint,
    )
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
