#!/usr/bin/env python3
from __future__ import annotations

import sys

args = sys.argv[1:]
if args == ["version"]:
    print("0.47.2")
    raise SystemExit(0)
if args == ["run", "-help"]:
    print("Usage: specdown run", file=sys.stderr)
    raise SystemExit(0)
raise SystemExit(1)
