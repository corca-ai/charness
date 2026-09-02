#!/usr/bin/env python3
"""Seeded no-op gate used by the declarative runner fixture."""

from __future__ import annotations

import os
import sys
import time

label = sys.argv[1]
if label == "slow":
    time.sleep(1.2)
if os.environ.get("QUALITY_FAIL_LABEL") == label:
    print(f"failure output from {label}")
    raise SystemExit(1)
if label == "unproven":
    print("scope was not established")
    raise SystemExit(3)
if label == "partial":
    print("scope was only partly established")
    raise SystemExit(4)
if label == "ordinary-exit-three":
    raise SystemExit(3)
if label == "warning":
    print("advisory: WARN: inspect this passing gate")
else:
    print(f"success output from {label}")
