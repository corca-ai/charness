#!/usr/bin/env python3
"""Author-time required-shape source for the GitHub-issue closeout-draft surface.

``validate-closeout-draft`` (which reuses ``verify_closeout``) enforces a body
shape an author otherwise discovers by failing the validator several times (the
recurring authoring-preflight class). This module is the *shape source* the
artifact-surface preflight dispatcher reads for ``--type closeout-draft`` —
exactly like a scaffold script, it prints the required shape and a starter stub.

It never re-declares the contract: every classification, ledger field, carrier,
and manual-fallback reason is rendered from the LIVE enforced constants in the
sibling verifier modules, so the surfaced shape cannot drift from the gate.
"""
from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))["sibling_loader"](__file__)
_VERIFY = _load_local("issue_verify_closeout")
_BODY = _load_local("issue_verify_closeout_body")
_FLOORS = _load_local("issue_closeout_rung1_floors")
_CRITIQUE = _load_local("issue_resolution_critique")
_ledger_counts = _load_local("issue_closeout_ledger_counts")
_CONSOLIDATED = _load_local("issue_consolidated_closeout")


def _min_signal_clause() -> str:
    """Render the blocked-signal floor from the live constant, or omit the number
    when the shared helper is unreachable. Never invents a value."""
    minimum = _CRITIQUE.min_blocked_signal_length()
    return f" >= {minimum} chars" if minimum is not None else " specific enough to be a real host signal"
_CLOSEOUT_DRAFT_STUB_TEMPLATE = (
    Path(__file__).resolve().parent / "templates" / "closeout_draft_stub.txt"
).read_text(encoding="utf-8")


def _field_label(field_id: str, aliases: tuple[str, ...]) -> str:
    """Render one ledger field as ``field_id`` plus its accepted ``Header:``
    keyword(s) when they differ — the failure message names the field_id, the
    body needs the header. Case-insensitive; written as ``Header: value``."""
    headers = " / ".join(f"{alias.title()}:" for alias in aliases)
    if aliases == (field_id,):
        return f"{field_id.title()}:"
    return f"{field_id} ({headers})"


def _ledger_block() -> list[str]:
    """The per-classification ledger fields, rendered from the live requirement
    map (``issue_verify_closeout_body._classification_requirements``)."""
    out: list[str] = ["Classification ledger fields (substantive value per field; `TODO`/`TBD`/`n/a` do not count):"]
    for classification in _VERIFY.CLASSIFICATIONS:
        labels = [_field_label(fid, aliases) for fid, aliases in _BODY._classification_requirements(classification)]
        out.append(f"  - {classification}: {', '.join(labels)}")
    # Rendered from the OWNER's constant, never hand-typed here. This line used
    # to state one of the two sibling rules and silently missed the other when it
    # landed; this module's contract is that it re-declares nothing.
    for finding_id, description in _ledger_counts.SIBLING_RULE_DESCRIPTIONS.items():
        out.append(f"  - {description} (`{finding_id}` fails otherwise).")
    return out


def _consolidated_block() -> list[str]:
    """Render the exceptional disposition by querying its live body owner.

    `consolidated` moves work and must not use a GitHub auto-close carrier: the
    tracker would render that close as completed.  This belongs beside the
    generic shape, not in a prose-only reference, because this is the surface
    an author consults before making the irreversible carrier choice.
    """
    classification = _CONSOLIDATED.CLASSIFICATION
    probe = "Closes #5\nJtbd: move the work\nConsolidated into: #6\n"
    refused = [
        carrier
        for carrier in _VERIFY.CARRIERS
        if _BODY._missing_ledger_fields(probe, classification, carrier=carrier)
    ]
    allowed = [carrier for carrier in _VERIFY.CARRIERS if carrier not in refused]
    observed = _CONSOLIDATED.evaluate("Jtbd: move the work\nConsolidated into: #6\n")
    return [
        "",
        f"Consolidated disposition ({classification}) — this is a MOVE, not a repair:",
        f"  - Do not use draft carriers {', '.join(refused)}; GitHub auto-closes those carriers",
        "    as completed. Use `issue_tool.py close-with-comment` with",
        f"    `--reason {_CONSOLIDATED.REQUIRED_CLOSE_REASON!r}` instead.",
        "    Omit a close keyword from that comment: a neutral `Closes #N` is non-operative there,",
        "    while `Fixes` / `Resolves` remains a refused repair claim.",
        "  - The body requires `Jtbd:` and exactly one `Consolidated into: #N`; it must not",
        "    name an issue this carrier closes or claim Implementation, Prevention, Resolution brief,",
        "    Behavior, HOTL, Critique, Fixes, or Resolves.",
        "  - The body grammar deliberately does NOT assert these backend facts; the required",
        "    close-with-comment carrier reads them before comment/close mutation:",
        *[f"    - {fact}." for fact in observed["not_checked_here"]],
        f"  - `{', '.join(allowed)}` is only the generic verifier carrier that does not auto-close;",
        "    it is not the consolidated close path above.",
    ]


def _consolidated_required_shape() -> str:
    """The executable guide for an author who has already selected consolidation.

    The unqualified shape is a catalog for every classification.  Reusing that
    catalog after `consolidated` is selected made an author reconcile a generic
    carrier menu with a late exception at the irreversible choice, so this route
    deliberately contains only obligations that apply to consolidation.
    """
    return "\n".join(
        [
            "closeout-draft required shape for classification `consolidated`",
            "(enforced by `issue_tool.py validate-closeout-draft` before mutation):",
            *_consolidated_block(),
            "",
            "AI-provenance: add a substantive `AI-provenance: <…>` line; this applies",
            "to every classification so the eventual external close is legible as agent-authored.",
            "",
            "Externally-sourced body: if it carries substantive `Source origin:`, also add at",
            "least one of `Source text:` / `Re-read obligation:` / `Source degraded reason:`.",
        ]
    ).rstrip() + "\n"


def _hotl_vocabulary() -> str:
    """The typed HOTL statuses, expanded from the verifier's own anchored pattern and
    then CHECKED against it.

    Expanding the alternation by string surgery alone leaked the inner group
    (`blocked-needs-(?:operator, capability)`). Every rendered token is matched back
    against the live pattern, so a shape that names a status the verifier would refuse
    cannot be printed -- the producer asks the rule rather than restating it.
    """
    source = _FLOORS._HOTL_STATUS_LEAD.pattern
    body = source.split("(?:", 1)[1].rsplit(")", 1)[0].replace("\\b", "")
    tokens: set[str] = set()
    for part in _split_top_level(body):
        if "(?:" in part:
            head, inner = part.split("(?:", 1)
            inner = inner.rsplit(")", 1)[0]
            tokens.update(f"{head}{alt}" for alt in _split_top_level(inner))
        else:
            tokens.add(part)
    accepted = sorted(tok for tok in tokens if tok and _FLOORS._HOTL_STATUS_LEAD.match(tok))
    return ", ".join(accepted)


def _split_top_level(pattern_body: str) -> list[str]:
    """Split an alternation on `|` at nesting depth 0."""
    parts, depth, current = [], 0, ""
    for char in pattern_body:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        if char == "|" and depth == 0:
            parts.append(current)
            current = ""
            continue
        current += char
    parts.append(current)
    return [part for part in parts if part]


def required_shape(classification: str | None = None) -> str:
    """Render either the full catalog or a classification-specific author guide."""
    if classification == _CONSOLIDATED.CLASSIFICATION:
        return _consolidated_required_shape()
    crit = ", ".join(_CRITIQUE.CRITIQUE_REQUIRED_CLASSIFICATIONS)
    behavioral = ", ".join(_FLOORS.BEHAVIORAL_VERDICT_CLASSIFICATIONS)
    # OBSERVED, not restated. Round 1 caught this line rendering the behavioral
    # tuple for a floor that no longer shares it; hand-typing the replacement would
    # have moved the drift one level up rather than removing it. Ask the floor.
    provenance_scope = (
        "EVERY classification"
        if all(
            _FLOORS.evaluate_ai_provenance("", value)["applies"]
            for value in _VERIFY.CLASSIFICATIONS
        )
        else ", ".join(
            value for value in _VERIFY.CLASSIFICATIONS
            if _FLOORS.evaluate_ai_provenance("", value)["applies"]
        )
    )
    carriers = ", ".join(_VERIFY.CARRIERS)
    reasons = ", ".join(_VERIFY.MANUAL_FALLBACK_REASONS)
    # Three floors this shape used to omit while its own validator hard-blocked on
    # them, so a draft filled straight from here failed the check it was written to
    # pass. Rendered from the verifier's live constants, never restated: a shape
    # producer that re-declares a rule is a fork that drifts.
    lines = [
        "closeout-draft required shape (enforced by `issue_tool.py validate-closeout-draft`,",
        "which reuses `verify_closeout` — same checks before anything mutates GitHub):",
        "This is the all-classifications catalog; after selecting `consolidated`, rerun with",
        "`--classification consolidated` for its non-conflicting carrier guide.",
        "",
        f"Carrier (--carrier, one of: {carriers}) decides the carrier-body SOURCE:",
        "  - direct-commit: the body is the COMMIT MESSAGE — pass `--commit-message-file`",
        "    (the proposed commit subject/body), NOT `--body-file`. (Post-close",
        "    `verify-closeout` reads the same message back from the commit via `git show`.)",
        "    This is the trap that cost a round-trip.",
        "  - pr-body / manual-fallback: the body is `--body-file`.",
        "",
        "Close keyword (not required for manual-fallback): each --number needs a",
        "`Closes #N` / `Fixes #N` / `Resolves #N` line (optionally `owner/repo#N`).",
        "",
        f"resolution_critique (required for classifications: {crit}):",
        "  - a `Critique: <path>` line (single-issue) or `Critique #N: <path>` (bundled,",
        "    one per --number, or `Critique #1 #2: <path>`).",
        "  - <path> is a checked-in critique artifact that EXISTS, is non-empty, and",
        "    BINDS to the issue number: its basename carries the number, or its content",
        "    CITES it -- `#N`, `issue N`, `issues/N`, `gh-N`. A bare number with no",
        "    citation marker does NOT bind (a `Date:` line must not bind #27).",
        "  - the cited critique must itself pass `validate_critique_artifacts` (a blocked",
        "    fresh-eye satisfaction there needs `host signal:` / `tool signal:`);",
        "    `Critique: blocked <signal>` records a host-blocked-subagent fallback; the",
        f"    SIGNAL you write must be{_min_signal_clause()} long (the"
        " `host-blocked-subagent:`",
        "    head the skill prepends does not count toward it), and a skipped critique",
        "    prints a non-blocking `REVIEW: ... was SKIPPED` line.",
        "",
    ]
    lines += _ledger_block()
    lines += _consolidated_block()
    lines += [
        "",
        f"manual-fallback carrier also requires --manual-fallback-reason one of: {reasons}.",
        "",
        "Externally-sourced body (a substantive `Source origin:`): also needs at least one",
        "of `Source text:` / `Re-read obligation:` / `Source degraded reason:`.",
        "",
        "If the body declares a `## Proof Ledger`: each gap must be dispositioned",
        "(no proof entry / reached < required / gap lacks disposition all fail).",
    ]
    lines += [
        "",
        f"Behavior (required for classifications: {behavioral}):",
        "  - one `Behavior #N: <…>` line per closed issue (single-issue shorthand",
        "    `Behavior: <…>`), naming the DISTINCT channel the user-facing behavior was",
        "    confirmed through, or a typed non-`verified` disposition.",
        "  - a typed disposition satisfies it exactly as a confirmation does; this floor",
        "    refuses SILENCE, it never declares completion.",
        "",
        f"AI-provenance (required for {provenance_scope}):",
        "  - an `AI-provenance: <…>` line, so the irreversible external write is legible",
        "    as agent-authored to the distinct observer. Presence/form only.",
        "  - NOT scoped to the behavior-bearing classifications: authorship is not a fact",
        "    about behavior change, so a light close owes the marker too.",
        "",
        "HOTL dispositions (only when the draft carries HOTL entries):",
        "  - each value must BEGIN with a typed status; an unanchored mention lets a",
        "    status's own negation pass. Vocabulary:",
        f"    {_hotl_vocabulary()}",
        "  - `issue` must additionally carry its tracker ref (`#N`).",
    ]
    return "\n".join(lines).rstrip() + "\n"


def stub() -> str:
    """A starter closeout body (feature/deferred-work shape — the common case)."""
    return _CLOSEOUT_DRAFT_STUB_TEMPLATE


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root accepted by artifact-surface preflight (default: current directory)",
    )
    parser.add_argument("--stub", action="store_true", help="Emit a starter closeout body")
    parser.add_argument(
        "--classification",
        choices=_VERIFY.CLASSIFICATIONS,
        help="Render the selected classification's guide instead of the full catalog",
    )
    args = parser.parse_args(argv)
    sys.stdout.write(stub() if args.stub else required_shape(args.classification))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
