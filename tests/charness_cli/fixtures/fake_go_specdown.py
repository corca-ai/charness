#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path


def copy_executable(source: Path, target: Path, config: dict[str, str] | None = None) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    if config is not None:
        target.with_suffix(".json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    target.chmod(0o755)


config = json.loads(Path(sys.argv[0]).with_suffix(".json").read_text(encoding="utf-8"))
gopath = Path(config["gopath"])
bin_dir = Path(config["bin_dir"])
fixtures = Path(config["fixtures"])
gobin = os.environ.get("GOBIN")
install_root = Path(gobin) if gobin else gopath / "bin"
install_root.mkdir(parents=True, exist_ok=True)

args = sys.argv[1:]
if args == ["env", "GOPATH"]:
    print(gopath)
    raise SystemExit(0)
if args == ["install", "github.com/gitleaks/gitleaks/v8@latest"]:
    for target in (install_root / "gitleaks", bin_dir / "gitleaks"):
        copy_executable(fixtures / "fake_gitleaks.py", target)
    print("installed gitleaks")
    raise SystemExit(0)
if args == ["install", "github.com/charmbracelet/glow/v2@latest"]:
    glow_config = {"version_text": "glow version 2.1.2", "help_text": "glow help", "runtime_text": "glow"}
    for target in (install_root / "glow", bin_dir / "glow"):
        copy_executable(fixtures / "fake_glow.py", target, glow_config)
    print("installed glow")
    raise SystemExit(0)
if args == ["install", "github.com/corca-ai/specdown/cmd/specdown@latest"]:
    print("installed specdown")
    raise SystemExit(0)
raise SystemExit(1)
