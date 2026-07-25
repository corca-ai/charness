"""Rung-1 presence floor for `issue_tool.py close-with-comment`.

`close-with-comment` mutates GitHub directly (comment, then close). Unlike
`verify-closeout` / `validate-closeout-draft`, it previously ran no closeout-body
check beyond "the file exists" — the rung-1 presence checks only ran when the
agent *voluntarily* invoked one of those separate commands first. This module
composes the existing rung-1 checks (behavioral verdict or a typed
non-verified disposition, HOTL entry disposition, AI-provenance marker,
resolution-critique binding, source preservation) so the manual-close mutation
itself cannot happen on a silent body.

Two rung-1 checks that ``verify-closeout`` owns are deliberately NOT composed
here, so a future reader does not re-file the gap. Neither is a rung-level
exemption — both are presence checks like the ones above:

- **Close-keyword** (`_missing_close_keywords`). ``verify-closeout`` itself
  already exempts this carrier: ``issue_verify_closeout.py`` skips the check when
  ``carrier == "manual-fallback"``, which is what a manual close-with-comment is.
  A ``Closes #N`` keyword is honoured by GitHub only in a commit message or a PR
  body, never in an issue comment, and ``close-with-comment`` closes through the
  API regardless. Composing it here would demand a line that does nothing and
  would diverge from the sibling verifier.
- **Ledger fields** (`_missing_ledger_fields`). ``verify-closeout`` *does* apply
  these to this same body, and they are presence-only — the repo's archetype for
  that shape, which ``evaluate_source_preservation`` describes itself as
  mirroring. Left out as scope restraint, not on principle: wiring them would
  tighten the manual-close path well past the named provenance residual, newly
  refusing short close comments whose ledger lives in the commit carrier.
  ``verify-closeout`` still enforces them when run. Revisit as a deliberate
  tightening with its own before/after, not as a gap. (The leading underscore is
  not the obstacle — ``issue_verify_closeout.py`` already aliases the same private
  name across the module boundary.)
"""
from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))["sibling_loader"](__file__)
_BODY = _load_local("issue_verify_closeout_body")
_CRITIQUE = _load_local("issue_resolution_critique", "issue_close_comment_floor_critique")

# The floor-exemption advisory now has a single carrier-neutral owner in
# ``issue_verify_closeout_body`` (D36). Re-export it so this module's existing
# caller (``issue_close.py``'s ``_CLOSE_COMMENT_FLOOR.review_advisory_for_classification``)
# keeps working while the commit-msg carrier shares the same implementation — no
# duplicated advisory body to drift between carriers or trip the dup-ratchet gate.
review_advisory_for_classification = _BODY.review_advisory_for_classification


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
    # The HOTL-disposition floor landed after this composition and was never wired
    # in, so the carrier that mutates GitHub *directly* was the one carrier where an
    # undispositioned HOTL entry could not be refused. Presence-gated like the rest:
    # a body with no HOTL entry is inert, so this adds no obligation to bodies that
    # never had a live loop.
    hotl_dispositions = _BODY.evaluate_hotl_dispositions(body, classification)
    # Same asymmetry as the HOTL floor above: `verify-closeout` and the commit-msg
    # carrier both check the AI-provenance marker, and this carrier — the only one
    # that writes to GitHub itself — did not. The marker is what makes the
    # irreversible external write legible as agent-authored to the rung-2 observer,
    # so the carrier with the strongest need for it was the one carrier without it.
    ai_provenance = _BODY.evaluate_ai_provenance(body, classification)
    resolution_critique = _CRITIQUE.check_resolution_critique(
        repo_root=repo_root, body=body, classification=classification, numbers=numbers
    )
    ok = (
        source_preservation["ok"]
        and behavioral_verdict["ok"]
        and hotl_dispositions["ok"]
        and ai_provenance["ok"]
        and resolution_critique.get("ok", True)
    )
    return {
        "ok": ok,
        "classification": classification,
        "number": number,
        "source_preservation": source_preservation,
        "behavioral_verdict": behavioral_verdict,
        "hotl_dispositions": hotl_dispositions,
        "ai_provenance": ai_provenance,
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
    hotl = report["hotl_dispositions"]
    for entry in hotl.get("undispositioned", []):
        target = entry.get("target") or f"#{report['number']}"
        lines.append(
            f"  undispositioned HOTL entry {target}: the value must LEAD WITH a typed HOTL "
            f"status (or local-only-by-contract), not merely mention one; got {entry['value']!r}."
        )
    provenance = report["ai_provenance"]
    if provenance.get("applies") and not provenance.get("ok", True):
        lines.append(
            "  missing `AI-provenance:` marker: an agent-posted close comment must name "
            "itself as agent-authored so the rung-2 observer can read the write for what it is."
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
