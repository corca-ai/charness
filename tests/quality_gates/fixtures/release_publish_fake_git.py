#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

config = json.loads(Path(sys.argv[0]).with_suffix(".json").read_text(encoding="utf-8"))
log_path = Path(os.environ["FAKE_GIT_LOG"])
args = sys.argv[1:]
entries = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else []
entries.append(args)
log_path.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
if os.environ.get("FAKE_GIT_DIFF_NAME_ONLY_FAIL") == "1" and args[:2] == ["diff", "--name-only"]:
    print("forced diff failure", file=sys.stderr)
    raise SystemExit(42)
if os.environ.get("FAKE_GIT_LS_REMOTE_PREVIOUS_TAG_FAIL") == "1" and args == [
    "ls-remote",
    "--tags",
    "origin",
    "refs/tags/v0.0.0",
]:
    print("forced previous tag lookup failure", file=sys.stderr)
    raise SystemExit(44)
if os.environ.get("FAKE_GIT_TAG_LIST_FAIL") == "1" and args == ["tag", "--list", "v[0-9]*.[0-9]*.[0-9]*"]:
    print("forced local tag list failure", file=sys.stderr)
    raise SystemExit(45)
if os.environ.get("FAKE_GIT_LS_REMOTE_TAG_HISTORY_FAIL") == "1" and args == [
    "ls-remote",
    "--tags",
    "origin",
    "refs/tags/v[0-9]*",
]:
    print("forced remote tag history failure", file=sys.stderr)
    raise SystemExit(46)
if os.environ.get("FAKE_GIT_FETCH_TAG_FAIL") == "1" and args == [
    "fetch",
    "--quiet",
    "origin",
    "refs/tags/v0.0.0:refs/tags/v0.0.0",
]:
    print("forced tag fetch failure", file=sys.stderr)
    raise SystemExit(43)
raise SystemExit(subprocess.run([config["real_git"], *args]).returncode)
