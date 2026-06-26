#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--repo-root", type=Path, required=True)
args = parser.parse_args()
repo_root = args.repo_root.resolve()
version = json.loads((repo_root / "packaging" / "demo.json").read_text(encoding="utf-8"))["version"]
for rel in (
    ".claude-plugin/marketplace.json",
    "plugins/demo/.claude-plugin/plugin.json",
    "plugins/demo/.codex-plugin/plugin.json",
):
    path = repo_root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"version": version}, indent=2) + "\n", encoding="utf-8")
agents_path = repo_root / ".agents" / "plugins" / "marketplace.json"
agents_path.parent.mkdir(parents=True, exist_ok=True)
agents_path.write_text(
    json.dumps({"plugins": [{"name": "demo", "source": {"path": "./plugins/demo"}}]}, indent=2) + "\n",
    encoding="utf-8",
)
