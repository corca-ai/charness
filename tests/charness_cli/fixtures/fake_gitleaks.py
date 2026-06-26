#!/usr/bin/env python3
from __future__ import annotations

import sys

args = sys.argv[1:]
if args == ["version"]:
    print("gitleaks version 8.27.2")
elif args == ["help"]:
    print("gitleaks help")
else:
    print("gitleaks")
