#!/usr/bin/env python3
from __future__ import annotations

import sys

args = sys.argv[1:]
if args == ["--version"]:
    print("tokei 12.1.2")
elif args == ["--help"]:
    print("Usage: tokei")
else:
    print("tokei")
