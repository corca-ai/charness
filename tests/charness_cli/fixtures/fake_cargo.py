#!/usr/bin/env python3
"""Minimal cargo fixture for native artifact producer tests."""

from __future__ import annotations

import os
import sys
from pathlib import Path

if sys.argv[1:] != ["build", "--release", "--locked"]:
    raise SystemExit(2)

log_path = os.environ.get("FAKE_CARGO_LOG")
if log_path:
    Path(log_path).write_text(
        " ".join(sys.argv[1:]) + "\n" + os.environ.get("RUSTUP_TOOLCHAIN", "") + "\n",
        encoding="utf-8",
    )

binary = Path.cwd() / "target" / "release" / "repograph"
binary.parent.mkdir(parents=True, exist_ok=True)
binary.write_text("#!/bin/sh\nprintf '%s\\n' fake-repograph\n", encoding="utf-8")
binary.chmod(0o755)
