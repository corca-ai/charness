#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

config_path = Path(sys.argv[0]).with_suffix(".json")
config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}

args = sys.argv[1:]
if args == ["--version"]:
    print(config.get("version_text", "glow version 2.1.2"))
    raise SystemExit(0)
if args == ["--help"]:
    print(config.get("help_text", "glow help"))
    raise SystemExit(0)
print(config.get("runtime_text", "glow"))
