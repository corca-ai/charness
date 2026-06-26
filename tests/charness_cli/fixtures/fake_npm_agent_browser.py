#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


def copy_executable(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    target.chmod(0o755)


config = json.loads(Path(sys.argv[0]).with_suffix(".json").read_text(encoding="utf-8"))
npm_prefix = Path(config["npm_prefix"])
bin_dir = Path(config["bin_dir"])
fixtures = Path(config["fixtures"])

args = sys.argv[1:]
if args == ["prefix", "-g"]:
    print(npm_prefix)
    raise SystemExit(0)
if args == ["install", "-g", "agent-browser@latest"]:
    print("updated agent-browser")
    raise SystemExit(0)
if args in (["install", "-g", "defuddle"], ["install", "-g", "defuddle@latest"]):
    copy_executable(fixtures / "fake_defuddle.py", bin_dir / "defuddle")
    print("updated defuddle")
    raise SystemExit(0)
raise SystemExit(1)
