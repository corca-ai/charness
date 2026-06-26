#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

config = json.loads(Path(sys.argv[0]).with_suffix(".json").read_text(encoding="utf-8"))
gopath = Path(config["gopath"])
fixtures = Path(config["fixtures"])
gobin = os.environ.get("GOBIN")
install_root = Path(gobin) if gobin else gopath / "bin"
install_root.mkdir(parents=True, exist_ok=True)

args = sys.argv[1:]
if args == ["version"]:
    print("go version go1.26.2 linux/arm64")
    raise SystemExit(0)
if args == ["env", "GOPATH"]:
    print(gopath)
    raise SystemExit(0)
if args == ["install", "github.com/charmbracelet/glow/v2@latest"]:
    glow = gopath / "bin" / "glow"
    glow.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(fixtures / "fake_glow.py", glow)
    glow.with_suffix(".json").write_text(
        json.dumps({"version_text": "glow 2.1.1-test", "help_text": "glow help", "runtime_text": "glow runtime"}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    glow.chmod(0o755)
    target = install_root / "glow"
    if target != glow:
        if target.exists() or target.is_symlink():
            target.unlink()
        target.symlink_to(glow)
    raise SystemExit(0)
raise SystemExit(1)
