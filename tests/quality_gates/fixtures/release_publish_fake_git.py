#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

config = json.loads(Path(sys.argv[0]).with_suffix(".json").read_text(encoding="utf-8"))
log_path = Path(os.environ["FAKE_GIT_LOG"])
args = sys.argv[1:]
entries = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else []
entries.append(args)
log_path.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
if os.environ.get("FAKE_GIT_DIFF_NAME_ONLY_FAIL") == "1" and args[:2] == ["diff", "--name-only"]:
    print("forced diff failure", file=sys.stderr)
    raise SystemExit(42)
raise SystemExit(subprocess.run([config["real_git"], *args]).returncode)
