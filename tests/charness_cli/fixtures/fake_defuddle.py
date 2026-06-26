#!/usr/bin/env python3
from __future__ import annotations

import sys

args = sys.argv[1:]
print("defuddle 0.1.0" if args == ["--version"] else "defuddle help")
