#!/usr/bin/env python3
from __future__ import annotations

import sys

args = sys.argv[1:]
if args == ["--version"]:
    print("agent-browser 0.25.3")
    raise SystemExit(0)
if args == ["--help"]:
    print("agent-browser")
    raise SystemExit(0)
raise SystemExit(0)
