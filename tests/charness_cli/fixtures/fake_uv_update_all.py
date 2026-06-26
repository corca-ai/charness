#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


def write_tool(name: str, version_text: str, help_text: str) -> None:
    target = bin_dir / name
    shutil.copy2(fixtures / "fake_tool_version_help.py", target)
    target.with_suffix(".json").write_text(
        json.dumps({"version_text": version_text, "help_text": help_text}, indent=2) + "\n",
        encoding="utf-8",
    )
    target.chmod(0o755)


config = json.loads(Path(sys.argv[0]).with_suffix(".json").read_text(encoding="utf-8"))
bin_dir = Path(config["bin_dir"])
fixtures = Path(config["fixtures"])

args = sys.argv[1:]
if args == ["tool", "upgrade", "ruff"]:
    write_tool("ruff", "ruff 0.15.18", "Run Ruff")
    print("upgraded ruff")
    raise SystemExit(0)
if args == ["tool", "upgrade", "vulture"]:
    write_tool("vulture", "vulture 2.14", "usage: vulture")
    print("upgraded vulture")
    raise SystemExit(0)
raise SystemExit(1)
