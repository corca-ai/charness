#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

config = json.loads(Path(sys.argv[0]).with_suffix(".json").read_text(encoding="utf-8"))
args = sys.argv[1:]
if args == ["--version"]:
    print(config["version_text"])
elif args in (["--help"], ["check", "--help"]):
    print(config["help_text"])
else:
    print(config["version_text"])
