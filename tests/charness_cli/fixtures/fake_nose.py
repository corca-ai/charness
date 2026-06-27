#!/usr/bin/env python3
from __future__ import annotations

import sys

args = sys.argv[1:]
if args == ["--version"]:
    print("nose 0.14.0")
    raise SystemExit(0)
if args == ["scan", "--help"]:
    print("Find duplicated code")
    raise SystemExit(0)
if args and args[0] == "scan":
    print("[]")
    raise SystemExit(0)
raise SystemExit(0)
