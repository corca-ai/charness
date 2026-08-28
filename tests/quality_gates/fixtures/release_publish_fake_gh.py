#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

log_path = Path(os.environ["FAKE_GH_LOG"])
args = sys.argv[1:]
entries = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else []
entries.append(args)
log_path.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")

if args == ["auth", "status"]:
    print("authenticated")
    raise SystemExit(0)
if args == ["repo", "view", "--json", "url", "--jq", ".url"]:
    print("https://github.com/example/demo")
    raise SystemExit(0)
if args == ["repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"]:
    print("example/demo")
    raise SystemExit(0)
if args[:2] == ["release", "upload"]:
    if len(args) != 4 or args[2].startswith("-") or args[3].startswith("-"):
        raise SystemExit(2)
    asset_state_path = Path(os.environ["FAKE_GH_RELEASE_ASSET_STATE"])
    asset_state = json.loads(asset_state_path.read_text(encoding="utf-8")) if asset_state_path.exists() else {}
    asset_state.setdefault(args[2], []).append(Path(args[3]).name)
    asset_state_path.write_text(json.dumps(asset_state, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(0)
if args[:2] == ["release", "view"] and len(args) > 3:
    if (
        len(args) != 7
        or args[2].startswith("-")
        or args[3:6] != ["--json", "assets", "--jq"]
        or not args[6]
    ):
        raise SystemExit(2)
    asset_state_path = Path(os.environ["FAKE_GH_RELEASE_ASSET_STATE"])
    asset_state = json.loads(asset_state_path.read_text(encoding="utf-8")) if asset_state_path.exists() else {}
    print("\n".join(asset_state.get(args[2], [])))
    raise SystemExit(0)
if args[:2] == ["release", "view"]:
    state_path = Path(os.environ["FAKE_GH_RELEASE_STATE"])
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else []
    raise SystemExit(0 if args[2] in state else 1)
if args[:2] == ["release", "create"]:
    tag = args[2]
    state_path = Path(os.environ["FAKE_GH_RELEASE_STATE"])
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else []
    if tag not in state and os.environ.get("FAKE_GH_RELEASE_CREATE_WITHOUT_VIEW") != "1":
        state.append(tag)
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    print(f"https://github.com/example/demo/releases/tag/{tag}")
    raise SystemExit(0)
if args[:2] == ["issue", "view"]:
    issue_view_count = sum(entry[:2] == ["issue", "view"] for entry in entries)
    fail_after = int(os.environ.get("FAKE_GH_ISSUE_VIEW_FAIL_AFTER", "0"))
    if os.environ.get("FAKE_GH_ISSUE_VIEW_FAIL") == "1" or (fail_after and issue_view_count > fail_after):
        print("issue view failed", file=sys.stderr)
        raise SystemExit(1)
    state_path = Path(os.environ["FAKE_GH_ISSUE_STATE"])
    state = json.loads(state_path.read_text(encoding="utf-8"))
    number = args[2]
    print(json.dumps({"number": int(number), "state": state.get(number, "OPEN"), "url": f"https://github.com/example/demo/issues/{number}"}))
    raise SystemExit(0)
if args[:2] == ["issue", "close"]:
    state_path = Path(os.environ["FAKE_GH_ISSUE_STATE"])
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state[args[2]] = "CLOSED"
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    print(f"closed issue {args[2]}")
    raise SystemExit(0)
raise SystemExit(1)
