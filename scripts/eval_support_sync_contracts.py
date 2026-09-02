#!/usr/bin/env python3

from __future__ import annotations

import argparse
import contextlib
import io
import sys
from pathlib import Path

import yaml


def _load_repo_runtime_bootstrap():
    _repo_bootstrap_pathlib = __import__("pathlib")
    _repo_bootstrap_sys = __import__("sys")
    repo_root = next(
        (
            ancestor
            for ancestor in _repo_bootstrap_pathlib.Path(__file__).resolve().parents
            if (ancestor / "scripts" / "adapter_lib.py").is_file()
        ),
        None,
    )
    if repo_root is None:
        raise ImportError("scripts/adapter_lib.py not found")
    repo_root_text = str(repo_root)
    if repo_root_text not in _repo_bootstrap_sys.path:
        _repo_bootstrap_sys.path.insert(0, repo_root_text)


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_sync_support = import_repo_module(__file__, "scripts.sync_support")


class EvalError(Exception):
    pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    previous_argv = sys.argv
    sys.argv = [
        str(Path(_sync_support.__file__)),
        "--repo-root",
        str(repo_root),
        "--tool-id",
        "agent-browser",
        "--tool-id",
        "specdown",
    ]
    stdout = io.StringIO()
    stderr = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            returncode = int(_sync_support.main())
    finally:
        sys.argv = previous_argv
    if returncode != 0:
        raise EvalError(stderr.getvalue() or "support-sync dry-run failed")

    payload = yaml.safe_load(stdout.getvalue())
    if len(payload) != 2:
        raise EvalError(f"unexpected payload {payload!r}")

    agent_browser, specdown = payload
    if agent_browser["tool_id"] != "agent-browser" or agent_browser["status"] != "dry-run":
        raise EvalError(f"unexpected agent-browser payload {agent_browser!r}")
    if agent_browser["support_state"] != "upstream-consumed":
        raise EvalError(f"unexpected agent-browser payload {agent_browser!r}")
    if specdown["tool_id"] != "specdown" or specdown["status"] != "dry-run":
        raise EvalError(f"unexpected specdown payload {specdown!r}")
    if specdown["support_state"] != "upstream-consumed":
        raise EvalError(f"unexpected specdown payload {specdown!r}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (EvalError, yaml.YAMLError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
