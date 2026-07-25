#!/usr/bin/env python3

"""One emit convention for gates that build a findings report.

Every findings-shaped gate has to make the same three decisions: findings go to
stderr so a green run's stdout stays quotable, `--json` emits the payload
verbatim, and text emission goes through the gate's own renderer. Copies of that
block had started to accumulate across gate scripts.

Kept deliberately dependency-free so a portable skill helper can adopt it by copy
without inheriting a repo-only import path.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from typing import TextIO


def findings_stream(report: dict[str, object]) -> TextIO:
    return sys.stderr if report["findings"] else sys.stdout


def emit_findings_report(
    report: dict[str, object],
    *,
    as_json: bool,
    render: Callable[[dict[str, object]], str],
) -> None:
    stream = findings_stream(report)
    if as_json:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    else:
        stream.write(render(report) + "\n")
