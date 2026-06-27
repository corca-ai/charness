#!/usr/bin/env python3
from __future__ import annotations

import sys

args = sys.argv[1:]
if args == ["--version"]:
    print("cautilus 1.2.3")
    raise SystemExit(0)
if args == ["doctor", "--help"]:
    print("cautilus doctor")
    raise SystemExit(0)
raise SystemExit(0)
