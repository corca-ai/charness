#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


class EvalError(Exception):
    pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    result = subprocess.run(
        [
            "python3",
            "scripts/sync_support.py",
            "--repo-root",
            str(repo_root),
            "--tool-id",
            "agent-browser",
            "--tool-id",
            "specdown",
            "--json",
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise EvalError(result.stderr or "support-sync dry-run failed")

    payload = json.loads(result.stdout)
    if len(payload) != 2:
        raise EvalError(f"unexpected payload {payload!r}")

    agent_browser, specdown = payload
    if agent_browser["tool_id"] != "agent-browser" or agent_browser["status"] != "dry-run":
        raise EvalError(f"unexpected agent-browser payload {agent_browser!r}")
    if agent_browser["support_state"] != "upstream-consumed":
        raise EvalError(f"unexpected agent-browser payload {agent_browser!r}")
    if specdown["tool_id"] != "specdown" or specdown["status"] != "skipped":
        raise EvalError(f"unexpected specdown payload {specdown!r}")
    if specdown["reason"] != "integration has no support_skill_source":
        raise EvalError(f"unexpected specdown payload {specdown!r}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (EvalError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
