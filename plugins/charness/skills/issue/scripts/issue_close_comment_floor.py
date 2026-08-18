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
- **Ledger fields** (`_missing_ledger_fields`). ``consolidated`` is the narrow
  exception: its required `close-with-comment` carrier composes that
  classification's own fields so it cannot close an issue into itself or invent a
  repair claim. Other classifications remain out of scope: applying their full
  resolution ledger here would newly refuse short close comments whose ledger
  lives in a commit carrier. ``verify-closeout`` still enforces those fields when
  run. Revisit that broader tightening with its own before/after, not as a gap.
  (The leading underscore is not the obstacle — ``issue_verify_closeout.py``
  already aliases the same private name across the module boundary.)
"""
from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))["sibling_loader"](__file__)
_BODY = _load_local("issue_verify_closeout_body")
_FLOORS = _load_local("issue_closeout_rung1_floors")
_PROBE_FLOOR = _load_local("issue_probe_record_floor")
_CRITIQUE = _load_local("issue_resolution_critique", "issue_close_comment_floor_critique")
_CONSOLIDATED_CLASSIFICATION = "consolidated"

# The floor-exemption advisory now has a single carrier-neutral owner in
# ``issue_verify_closeout_body`` (D36). Re-export it so this module's existing
# caller (``issue_close.py``'s ``_CLOSE_COMMENT_FLOOR.review_advisory_for_classification``)
# keeps working while the commit-msg carrier shares the same implementation — no
# duplicated advisory body to drift between carriers or trip the dup-ratchet gate.
review_advisory_for_classification = _FLOORS.review_advisory_for_classification


def evaluate_close_comment_floor(
    *,
    repo_root: Path,
    body: str,
    classification: str,
    number: int,
    consolidation_readback: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Presence/form-only floor: refuse a manual close-with-comment whose body is
    silent on the behavioral verdict, the resolution-critique binding, or (when
    externally sourced) source preservation. It never judges whether the content
    is honest — that is the fresh-eye resolution critique (rung-2).
    """
    numbers = [number]
    source_preservation = _FLOORS.evaluate_source_preservation(body)
    behavioral_verdict = _FLOORS.evaluate_behavioral_verdict(body, classification, numbers)
    # The HOTL-disposition floor landed after this composition and was never wired
    # in, so the carrier that mutates GitHub *directly* was the one carrier where an
    # undispositioned HOTL entry could not be refused. Presence-gated like the rest:
    # a body with no HOTL entry is inert, so this adds no obligation to bodies that
    # never had a live loop.
    hotl_dispositions = _FLOORS.evaluate_hotl_dispositions(body, classification, numbers)
    # Same asymmetry as the HOTL floor above: `verify-closeout` and the commit-msg
    # carrier both check the AI-provenance marker, and this carrier — the only one
    # that writes to GitHub itself — did not. The marker is what makes the
    # irreversible external write legible as agent-authored to the rung-2 observer,
    # so the carrier with the strongest need for it was the one carrier without it.
    ai_provenance = _FLOORS.evaluate_ai_provenance(body, classification)
    # THE THIRD INSTANCE OF THE ASYMMETRY THIS FILE ALREADY NAMES TWICE. The
    # `consolidated` disposition and its four tracker readbacks both landed on
    # `verify_closeout`, and a consolidated close is REQUIRED to use this carrier
    # (it is the only one that passes `--reason "not planned"`) -- so the one
    # carrier a consolidation must use was the one carrier that checked neither its
    # destination grammar nor whether that destination exists, is open, or names the
    # issue moving into it. `carrier` is `manual-fallback` here because that is what
    # this path is; it also means the auto-close refusal cannot fire against it.
    # SCOPED TO `consolidated`, deliberately. Applying the full resolution ledger to
    # every classification on this carrier is a much larger floor change than the gap
    # this repairs -- it would newly demand `Root cause:`/`Prevention:` from every
    # manual close that has always been allowed without them. That broader asymmetry
    # (this carrier checks fewer ledger fields than `verify-closeout` does) is real and
    # is left where it was, not silently widened under cover of this fix.
    consolidated_ledger = (
        _BODY._missing_ledger_fields(
            body, classification, carrier="manual-fallback", invoked_numbers=tuple(numbers)
        )
        if classification == _CONSOLIDATED_CLASSIFICATION
        else []
    )
    readback = list(consolidation_readback or [])
    for entry in readback:
        consolidated_ledger.extend(
            f"consolidation:{problem}" for problem in entry.get("problems_to_surface", [])
        )
    resolution_critique = _CRITIQUE.check_resolution_critique(
        repo_root=repo_root, body=body, classification=classification, numbers=numbers
    )
    # THE FOURTH INSTANCE OF THE ASYMMETRY THIS FILE ALREADY NAMES THREE TIMES, and it
    # was found the same way the others should have been -- by the closeout floor matrix
    # re-deriving every cell and reading `inert` here while `verify-closeout` read
    # `fires`. The probe-record floor landed on `verify_closeout` first, which would
    # again have left the one carrier that mutates GitHub DIRECTLY as the one carrier
    # where a behavioral claim could reach a real issue with no measurement behind it.
    probe_record = _PROBE_FLOOR.evaluate_probe_record(
        body, classification, numbers, repo_root=repo_root
    )
    ok = (
        source_preservation["ok"]
        and behavioral_verdict["ok"]
        and hotl_dispositions["ok"]
        and ai_provenance["ok"]
        and resolution_critique.get("ok", True)
        and probe_record["ok"]
        and not consolidated_ledger
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
        "probe_record": probe_record,
        "missing_ledger_fields": consolidated_ledger,
        "consolidation_readback": readback,
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
    for problem in _PROBE_FLOOR.probe_record_problems(report.get("probe_record", {})):
        lines.append(f"  {problem}")
    hotl = report["hotl_dispositions"]
    for entry in hotl.get("undispositioned", []):
        target = entry.get("target") or f"#{report['number']}"
        lines.append(
            f"  undispositioned HOTL entry {target}: the value must LEAD WITH a typed HOTL "
            f"status (or local-only-by-contract), not merely mention one; got {entry['value']!r}. "
            "This floor is presence-gated: if there was no live human loop, DELETE the line "
            "rather than writing `none`/`n/a` -- a body with no HOTL entry is inert and passes."
        )
    provenance = report["ai_provenance"]
    if provenance.get("applies") and not provenance.get("ok", True):
        lines.append(
            "  missing `AI-provenance:` marker: an agent-posted close comment must name "
            "itself as agent-authored so the rung-2 observer can read the write for what it is."
        )
    critique = report["resolution_critique"]
    # Observer refusals FIRST and on their own line: the critique line is present
    # and valid on this path, so the generic "add `Critique: <path>`" message would
    # send the author to fix the one thing that is not wrong.
    for refusal in critique.get("observer_refusals", []) or []:
        lines.append(f"  {refusal['reason']}")
    if not critique.get("ok", True) and not critique.get("observer_refusals"):
        lines.append(
            "  missing/invalid resolution-critique evidence: add `Critique: <path>` or "
            "`Critique: blocked <host-signal>`."
        )
    # Rendered LAST and never omitted: this floor refuses on `missing_ledger_fields`
    # and printed nothing for it, so a `consolidated` close that fixed its HOTL line by
    # typing a status -- which the message above tells the author to do -- was refused
    # again, this time by the repair-claim rule, with only the header line to read.
    for finding in report.get("missing_ledger_fields") or []:
        lines.append(f"  {finding}")
    preservation = report["source_preservation"]
    if preservation.get("missing"):
        lines.append(
            "  externally-sourced body is missing source preservation: add `Source text:`, "
            "`Re-read obligation:`, or `Source degraded reason:`."
        )
    return "\n".join(lines)
