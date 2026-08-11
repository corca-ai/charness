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


def render_findings_with_skipped(
    report: dict[str, object],
    *,
    headline: str,
    fix_hint: str,
    validated: str,
    skipped_noun: str = "invocation(s)",
) -> str:
    """Findings or a validated count -- and, on BOTH, the surface NOT proven.

    The skipped tail rides on the pass output too, which is the part a gate
    author leaves out: a bare "validated N invocations" reads as full coverage of
    a surface, and a gate that skips anything has not covered it. Counting each
    skip by reason on a green run is what keeps the pass honest.
    """
    if report["findings"]:
        lines = [headline, *(f"- {finding}" for finding in report["findings"]), fix_hint]
    else:
        lines = [validated]
    skipped: dict[str, int] = report["skipped"]  # type: ignore[assignment]
    if skipped:
        detail = ", ".join(f"{reason}: {count}" for reason, count in skipped.items())
        lines.append(f"Not proven ({sum(skipped.values())} {skipped_noun} skipped) — {detail}.")
    return "\n".join(lines)


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
