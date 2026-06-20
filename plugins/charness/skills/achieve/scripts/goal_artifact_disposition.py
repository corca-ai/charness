"""Improvement-disposition closeout gate — the deterministic rung.

Gives the After-phase disposition rule teeth without a prose word-list (round-2
critique proved a classifier over-fires or passes pure narration). This module
is the **deterministic floor** (rung 1):

- **1a block-the-blank** — refuse the ``complete`` flip when the cited retro
  lists actionable improvements but the goal's ``## Auto-Retro`` is blank and no
  opt-out is recorded. Emptiness/structure only; never classifies prose.
- **1b review-ran evidence** — require a bound ``Disposition review:`` line so a
  fresh-eye review provably ran (presence/binding-only BY DESIGN — wired in via
  ``CLOSEOUT_EVIDENCE_NAMES`` by the closeout-evidence wrapper, gated here by
  scope).

The substantive per-improvement judgment (*did the Auto-Retro genuinely dispose
each improvement?*) is **rung 2** — a fresh-eye subagent that records a verdict a
human audits. Determinism categorically cannot make that call, so this module
never tries; a deterministic false-positive trains token-theater and is worse
than a false-negative, so the teeth stay narrow and ungameable.

This module owns the rung **verdicts** (the ``apply_*_floor`` builders + the
``apply_disposition_rungs`` orchestrator). The markdown grammar and
disposition-scope primitives the verdicts parse live in the cohesive leaf
sibling ``goal_artifact_disposition_grammar.py`` (loaded below), so neither file
approaches the single-file line gate. The grammar import is the module's only
sibling dependency and is one-directional (the grammar leaf never imports back).
"""
from __future__ import annotations

import importlib.util
from datetime import date
from pathlib import Path
from typing import Any

# Rung 1d (the recurrence-lineage floor) lands later than rungs 1a/1b, so it has
# its own enforce-from-date that grandfathers every goal frozen before it. Goals
# Created on/after this date must carry a recurrence-lineage marker on each
# ``issue``-routed ``## Auto-Retro`` disposition. Clone-safe: in-file content.
RECURRENCE_LINEAGE_RULE_DATE = date(2026, 6, 8)


def _load_local_module(module_name: str):
    """Load a sibling achieve-script module by name via filesystem spec.

    Mirrors the self-contained sibling-loading the closeout-evidence wrapper uses
    so a moved/relocated module resolves both in the working tree and in the
    installed plugin export without a ``from scripts.`` import.
    """
    spec = importlib.util.spec_from_file_location(
        module_name, Path(__file__).resolve().parent / f"{module_name}.py"
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"{module_name}.py not found beside goal_artifact_disposition.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# The goal-artifact markdown grammar + disposition-scope primitives live in a
# cohesive leaf sibling so this module stays the "rung verdicts" concern and both
# files keep real headroom under the single-file line gate. Re-bound here so the
# established public surface (``disposition_gate_applies``, ``auto_retro_is_blank``,
# ``find_disposition_optout``, ``retro_lists_improvements``, ``_mask_fences``)
# stays on ``goal_artifact_disposition`` for existing importers.
_grammar = _load_local_module("goal_artifact_disposition_grammar")
DISPOSITION_RULE_DATE = _grammar.DISPOSITION_RULE_DATE
_mask_fences = _grammar._mask_fences
goal_created_date = _grammar.goal_created_date
is_floor_in_scope = _grammar.is_floor_in_scope
disposition_gate_applies = _grammar.disposition_gate_applies
_section_body = _grammar._section_body
auto_retro_is_blank = _grammar.auto_retro_is_blank
retro_lists_improvements = _grammar.retro_lists_improvements
find_disposition_optout = _grammar.find_disposition_optout
_bound_retro_path = _grammar._bound_retro_path


_FORM_MODULE = None


def _load_shared_form():
    """Load the shared disposition-form grammar (``scripts/disposition_form.py``).

    Parent-walks to ``scripts/`` exactly like the closeout wrapper resolves
    ``check_prescribed_skill_executed_lib``, so the single source of grammar
    resolves both in-tree and in the installed export. Cached at module level;
    lazy so importing this leaf standalone never requires the shared module.
    """
    global _FORM_MODULE
    if _FORM_MODULE is not None:
        return _FORM_MODULE
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        candidate = ancestor / "scripts" / "disposition_form.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("disposition_form", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            _FORM_MODULE = module
            return module
    raise ImportError("scripts/disposition_form.py not found above goal_artifact_disposition.py")


def apply_disposition_form_floor(report: dict[str, Any], text: str) -> None:
    """Disposition rung 1c: reject invalid disposition **forms** in
    ``## Auto-Retro`` for goals Created on/after the form rule date.

    Form/enum only (never a content classifier): a bare ``memory``/prose-only
    disposition fails; ``applied: …``/``issue #N``/``none — <reason>`` pass, even
    when vague. Its own enforce-from-date (later than rungs 1a/1b) grandfathers
    every goal frozen before the floor existed. The grammar lives once in the
    shared module so neither this gate nor the session-retro validator forks it.
    """
    form = _load_shared_form()
    created = goal_created_date(text)
    enforced = form.is_form_enforced(created)
    report["disposition_form_scope"] = {
        "enforced": enforced,
        "created": created.isoformat() if created else None,
        "rule_date": form.DISPOSITION_FORM_RULE_DATE.isoformat(),
    }
    if not enforced:
        return
    body = _section_body(_mask_fences(text), "Auto-Retro")
    if not body:
        return
    invalid = form.invalid_dispositions(body)
    if invalid:
        report["disposition_form"] = {
            "invalid": [{"marker": e["marker"], "value": e["value"]} for e in invalid],
            "reason": (
                "one or more `## Auto-Retro` disposition lines use an invalid form; each must be "
                f"{form.VALID_FORM_SUMMARY} — a bare `memory`/prose-only disposition is rejected"
            ),
        }
        report["ok"] = False


def apply_recurrence_lineage_floor(report: dict[str, Any], text: str) -> None:
    """Disposition rung 1d: an ``issue #N`` disposition in ``## Auto-Retro`` must
    carry a recurrence-lineage marker, so a re-file of a known recurring class
    cannot silently launder as a fresh narrow issue (the recurring authoring-
    preflight-skip loop engine).

    Presence/enum only (never a content classifier — the achieve guardrail): the
    floor checks ONLY that an ``issue``-form disposition carries a
    ``recurs:``/``recurrence:``/``lineage:``/``novel:`` marker with content. Whether
    a ``novel:`` claim is actually a re-file is rung 2's (the fresh-eye disposition
    review's) substantive call, never the floor's. Its own enforce-from-date
    grandfathers goals frozen before the floor existed; fail-CLOSED on an undatable
    goal mirrors the sibling rungs. Only ``issue``-form dispositions are checked
    (uniformly) — deciding *which* issues "look recurring" would itself be the
    classifier the guardrail forbids.
    """
    form = _load_shared_form()
    created = goal_created_date(text)
    enforced = is_floor_in_scope(created, RECURRENCE_LINEAGE_RULE_DATE)
    report["recurrence_lineage_scope"] = {
        "enforced": enforced,
        "created": created.isoformat() if created else None,
        "rule_date": RECURRENCE_LINEAGE_RULE_DATE.isoformat(),
    }
    if not enforced:
        return
    body = _section_body(_mask_fences(text), "Auto-Retro")
    if not body:
        return
    missing = [
        {"marker": entry["marker"], "value": entry["value"]}
        for entry in form.scan_dispositions(body)
        if entry["verdict"]["kind"] == "issue" and not form.has_recurrence_lineage(entry["value"])
    ]
    if missing:
        report["recurrence_lineage"] = {
            "missing": missing,
            "reason": (
                "one or more `## Auto-Retro` `issue` dispositions lack "
                f"{form.RECURRENCE_LINEAGE_SUMMARY}; each issue-routed disposition must carry it "
                "(e.g. `issue #N (novel: <why no matching recurring class>)` or "
                "`issue #N (recurs: <lineage>)`) so a re-file of a known recurring class cannot "
                "launder as a fresh narrow issue. Presence-only — the fresh-eye disposition "
                "review judges whether a `novel:` claim is actually a re-file"
            ),
        }
        report["ok"] = False


def apply_structural_followup_floor(report: dict[str, Any], text: str, retro_text: str) -> None:
    """Disposition rung 1e: when the cited retro names a transferable waste item
    (a ``## Sibling Search`` trigger), the goal's ``## Auto-Retro`` must carry a
    structural-follow-up **destination** line, so "recorded in recent-lessons"
    can no longer be mistaken for a structural fix.

    Presence/form-enum only (never a content classifier — the achieve guardrail):
    the floor checks ONLY that a ``Structural follow-up:`` line is present and
    uses one of the four destination forms. Whether the chosen destination is
    substantively right (e.g. a memory note dressed up as ``applied:``) is rung
    2's — the fresh-eye disposition review's — call, never the floor's. Its own
    enforce-from-date grandfathers goals frozen before the floor existed;
    fail-CLOSED on an undatable goal mirrors the sibling rungs. Inert unless the
    retro actually names transferable waste, so a no-transferable-waste goal is
    never forced to add a destination line (no over-fire).
    """
    form = _load_shared_form()
    created = goal_created_date(text)
    enforced = is_floor_in_scope(created, form.STRUCTURAL_FOLLOWUP_RULE_DATE)
    transferable = form.names_transferable_waste(retro_text)
    report["structural_followup_scope"] = {
        "enforced": enforced,
        "transferable_waste_named": transferable,
        "created": created.isoformat() if created else None,
        "rule_date": form.STRUCTURAL_FOLLOWUP_RULE_DATE.isoformat(),
    }
    if not enforced or not transferable:
        return
    body = _section_body(_mask_fences(text), "Auto-Retro") or ""
    verdict = form.evaluate_structural_followup(body)
    if verdict["problem"]:
        report["structural_followup"] = verdict
        report["ok"] = False


def apply_disposition_rungs(report: dict[str, Any], text: str, in_scope: bool) -> None:
    """Attach the disposition-gate verdict to ``report`` (mutates in place).

    Rung 1a (block-the-blank): refuse the flip when the bound retro lists ≥1
    improvement, the goal's ``## Auto-Retro`` is blank, and no opt-out is
    recorded. Fires independently of any rung-1b ``disposition_review`` skip
    (host portability: a subagent-blocked host degrades to rung 1 only, and the
    blank check must still fire). The substantive per-improvement judgment is
    rung 2's job — recorded for a human, never scored here.
    """
    # Rung 1c (the disposition-form floor) runs first and on its own
    # enforce-from-date, so it fires even when rungs 1a/1b are grandfathered.
    apply_disposition_form_floor(report, text)
    # Rung 1d (the recurrence-lineage floor) likewise runs on its own date, so a
    # missing lineage marker on an issue-routed disposition blocks even when rungs
    # 1a/1b are grandfathered.
    apply_recurrence_lineage_floor(report, text)
    # Read the bound retro once: rung 1e needs it to detect the transferable-waste
    # trigger, and rung 1a (below) reuses it for the improvement-list check.
    retro_path = _bound_retro_path(report)
    retro_text = ""
    if retro_path is not None:
        try:
            retro_text = Path(retro_path).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            retro_text = ""
    # Rung 1e (the structural-follow-up destination floor) runs on its own date,
    # so a missing destination on a transferable-waste retro blocks even when
    # rungs 1a/1b are grandfathered.
    apply_structural_followup_floor(report, text, retro_text)
    created = goal_created_date(text)
    # Rung 1f (the residual-ledger floor): each `## Residual Ledger` row must
    # carry a concrete disposition, so a prose-only `defer`/`recorded in retro`
    # residual is refused. Own enforce-from-date; inert with no ledger rows. The
    # heavy logic lives in the shared grammar so this at-cap leaf stays minimal.
    ledger = _load_shared_form().residual_ledger_report(text, created)
    report["residual_ledger_scope"] = ledger["scope"]
    if ledger.get("problem"):
        report["residual_ledger"] = ledger
        report["ok"] = False
    report["disposition_scope"] = {
        "in_scope": in_scope,
        "created": created.isoformat() if created else None,
        "rule_date": DISPOSITION_RULE_DATE.isoformat(),
        "reason": (
            "Created >= rule date (or undatable; fail-closed): disposition gate applies"
            if in_scope
            else "Created < rule date: grandfathered, disposition gate inert"
        ),
    }
    optout = find_disposition_optout(text)
    if optout is not None:
        report["disposition_optout"] = {"reason": optout}
    if not in_scope:
        return
    has_improvements = retro_lists_improvements(retro_text) if retro_path is not None else False
    blank = auto_retro_is_blank(text)
    report["retro_improvements_present"] = has_improvements
    report["auto_retro_blank"] = blank
    if has_improvements and blank and optout is None:
        report["disposition_blank"] = {
            "reason": (
                "the cited retro lists actionable `## Next Improvements` but the goal's "
                "`## Auto-Retro` is blank and no `Retro dispositions: none — <reason>` opt-out "
                "is recorded; disposition each improvement (`applied: <what>` or `issue <id>`) "
                "or record the opt-out before flipping to complete"
            )
        }
        report["ok"] = False
