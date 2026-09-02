#!/usr/bin/env python3

"""One emit convention for gates that build a findings report.

Every findings-shaped gate has to make the same two decisions: findings go to
stderr so a green run's stdout stays quotable, and the payload is emitted as
YAML. Copies of that block had started to accumulate across gate scripts.

`emit_findings_report` carried an `as_json` selector until the 2026-08-14 removal
of `--json`. Output is unconditionally YAML now, so the selector is gone rather
than left defaulted -- a dead format switch on a shared emitter is exactly the
residue that made the last migration look finished when it was not.

Kept deliberately dependency-free so a portable skill helper can adopt it by copy
without inheriting a repo-only import path.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TextIO


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import load_path_module  # noqa: E402

render_yaml = load_path_module(
    "scripts.yaml_output", Path(__file__).resolve().parent.parent / "yaml_output.py"
).render_yaml


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


def findings_payload(
    report: dict[str, object],
    *,
    fix_hint: str,
    skipped_noun: str,
    skipped_note: str = "",
) -> dict[str, object]:
    """Fold the fix hint and the not-proven tail into the emitted payload.

    The payload-shaped successor to ``render_findings_with_skipped``, and it lives here
    for the same reason that renderer did: the block was copied into
    ``check_documented_command_flags`` and ``check_documented_subcommands``, the dup
    ratchet forced it out, and the 2026-08-14 YAML migration open-coded it back into
    both. Only the two strings ever differed.

    The tail rides on the PASS too, which is the part a gate author leaves out: a bare
    ``status: pass`` beside a non-empty ``skipped`` map reads as full coverage, and a
    run that skipped an invocation has not proven it.
    """
    payload = dict(report)
    if report["findings"]:
        payload["fix_hint"] = fix_hint
    skipped: dict[str, int] = report["skipped"]  # type: ignore[assignment]
    if skipped:
        payload["not_proven"] = (
            f"{sum(skipped.values())} {skipped_noun} skipped and NOT proven by this run"
            f"{skipped_note}; see `skipped` for the reason counts."
        )
    return payload


def emit_findings_report(report: dict[str, object]) -> None:
    findings_stream(report).write(render_yaml(report))
