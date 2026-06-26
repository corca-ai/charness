#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

log = os.environ.get("FAKE_DISTINCT_CHANNEL_LOG")
if log:
    path = Path(log)
    entries = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    entries.append(sys.argv[1:])
    path.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
if os.environ.get("FAKE_DISTINCT_CHANNEL_RESULT") == "fail":
    print("distinct channel could not confirm the published release", file=sys.stderr)
    raise SystemExit(1)
print("distinct channel confirmed the published release")
raise SystemExit(0)
