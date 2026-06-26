#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

config = json.loads(Path(sys.argv[0]).with_suffix(".json").read_text(encoding="utf-8"))
bin_dir = Path(config["bin_dir"])
fixtures = Path(config["fixtures"])

args = sys.argv[1:]
if args == ["install", "tokei", "--force"]:
    target = bin_dir / "tokei"
    shutil.copy2(fixtures / "fake_tokei.py", target)
    target.chmod(0o755)
    print("installed tokei")
    raise SystemExit(0)
raise SystemExit(1)
