#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import resolve_adapter


def _run_git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=repo_root, capture_output=True, text=True, check=False)


def _git_freshness(repo_root: Path, remote_name: str) -> dict[str, object]:
    if not (repo_root / ".git").exists():
        return {"status": "not-git", "remote_name": remote_name, "ahead_count": 0, "ahead_examples": []}

    remote_result = _run_git(repo_root, "remote", "get-url", remote_name)
    if remote_result.returncode != 0:
        return {
            "status": "missing-remote",
            "remote_name": remote_name,
            "ahead_count": 0,
            "ahead_examples": [],
            "detail": (remote_result.stderr or remote_result.stdout).strip(),
        }

    upstream_result = _run_git(repo_root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
    upstream_ref = upstream_result.stdout.strip() if upstream_result.returncode == 0 and upstream_result.stdout.strip() else f"{remote_name}/main"

    count_result = _run_git(repo_root, "rev-list", "--count", f"HEAD..{upstream_ref}")
    if count_result.returncode != 0:
        return {
            "status": "unavailable",
            "remote_name": remote_name,
            "upstream_ref": upstream_ref,
            "ahead_count": 0,
            "ahead_examples": [],
            "detail": (count_result.stderr or count_result.stdout).strip(),
        }

    ahead_count = int((count_result.stdout or "0").strip() or "0")
    log_result = _run_git(repo_root, "log", "--oneline", "-n", "5", f"HEAD..{upstream_ref}")
    ahead_examples = [line for line in log_result.stdout.splitlines() if line.strip()]
    return {
        "status": "ahead" if ahead_count else "current",
        "remote_name": remote_name,
        "upstream_ref": upstream_ref,
        "ahead_count": ahead_count,
        "ahead_examples": ahead_examples,
    }


def _status_lines(repo_root: Path, paths: list[str]) -> list[str]:
    if not paths:
        return []
    result = _run_git(repo_root, "status", "--short", "--", *paths)
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    adapter = resolve_adapter.load_adapter(repo_root)
    data = adapter["data"]
    source_documents = list(data.get("source_documents", []))
    mutable_documents = set(data.get("mutable_documents", []))
    status_lines = _status_lines(repo_root, source_documents)
    payload = {
        "artifact_path": adapter["artifact_path"],
        "adapter_path": adapter["path"],
        "source_documents": [
            {
                "path": path,
                "exists": (repo_root / path).is_file(),
                "mutable": path in mutable_documents,
            }
            for path in source_documents
        ],
        "dirty_paths": status_lines,
        "freshness": _git_freshness(repo_root, str(data.get("remote_name", "origin"))),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
