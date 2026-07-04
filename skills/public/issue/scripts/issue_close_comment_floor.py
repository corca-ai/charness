"""Rung-1 presence floor for `issue_tool.py close-with-comment`.

`close-with-comment` mutates GitHub directly (comment, then close). Unlike
`verify-closeout` / `validate-closeout-draft`, it previously ran no closeout-body
check beyond "the file exists" — the rung-1 presence checks only ran when the
agent *voluntarily* invoked one of those separate commands first. This module
composes the existing rung-1 checks (behavioral verdict or a typed
non-verified disposition, resolution-critique binding, source preservation) so
the manual-close mutation itself cannot happen on a silent body.
"""
from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))["sibling_loader"](__file__)
_BODY = _load_local("issue_verify_closeout_body")
_CRITIQUE = _load_local("issue_resolution_critique", "issue_close_comment_floor_critique")

# Classifications with no live user-facing behavior to confirm — mirrors
# issue_verify_closeout_body.BEHAVIORAL_VERDICT_CLASSIFICATIONS's complement.
_FLOOR_EXEMPT_CLASSIFICATIONS = ("question", "decision-needed")


def review_advisory_for_classification(classification: str) -> list[str]:
    """REVIEW-severity advisory for a close whose classification exempts it
    from the behavioral-verdict and resolution-critique floors.

    Mirrors ``scripts/skill_cut_safety_advisory.py``'s pattern: forces a
    question for whoever reads the close output, never fails the command. The
    classification is caller-supplied with no independent check on it, so a
    `question`/`decision-needed` close silently bypasses two of the three floor
    checks; this line makes that bypass visible instead of silent.
    """
    if classification not in _FLOOR_EXEMPT_CLASSIFICATIONS:
        return []
    return [
        f"REVIEW: classification '{classification}' exempts this close from the "
        "behavioral-verdict and resolution-critique floors (only source preservation still "
        "applies); confirm the classification is correct before treating this issue as "
        "resolved (advisory only, never blocks)."
    ]


def evaluate_close_comment_floor(
    *, repo_root: Path, body: str, classification: str, number: int
) -> dict[str, Any]:
    """Presence/form-only floor: refuse a manual close-with-comment whose body is
    silent on the behavioral verdict, the resolution-critique binding, or (when
    externally sourced) source preservation. It never judges whether the content
    is honest — that is the fresh-eye resolution critique (rung-2).
    """
    numbers = [number]
    source_preservation = _BODY.evaluate_source_preservation(body)
    behavioral_verdict = _BODY.evaluate_behavioral_verdict(body, classification, numbers)
    resolution_critique = _CRITIQUE.check_resolution_critique(
        repo_root=repo_root, body=body, classification=classification, numbers=numbers
    )
    ok = (
        source_preservation["ok"]
        and behavioral_verdict["ok"]
        and resolution_critique.get("ok", True)
    )
    return {
        "ok": ok,
        "classification": classification,
        "number": number,
        "source_preservation": source_preservation,
        "behavioral_verdict": behavioral_verdict,
        "resolution_critique": resolution_critique,
    }


def format_close_comment_floor_failure(report: dict[str, Any]) -> str:
    lines = [
        f"charness close-with-comment: closeout body for #{report['number']} fails the rung-1 "
        "presence floor; refusing before any GitHub mutation.",
    ]
    behavioral = report["behavioral_verdict"]
    if behavioral.get("applies") and not behavioral.get("ok", True):
        lines.append(
            "  missing behavioral verdict: add a `Behavior: <distinct evidence channel>` line, "
            "or a typed non-verified disposition (HOTL status or local-only-by-contract)."
        )
    critique = report["resolution_critique"]
    if not critique.get("ok", True):
        lines.append(
            "  missing/invalid resolution-critique evidence: add `Critique: <path>` or "
            "`Critique: blocked <host-signal>`."
        )
    preservation = report["source_preservation"]
    if preservation.get("missing"):
        lines.append(
            "  externally-sourced body is missing source preservation: add `Source text:`, "
            "`Re-read obligation:`, or `Source degraded reason:`."
        )
    return "\n".join(lines)
