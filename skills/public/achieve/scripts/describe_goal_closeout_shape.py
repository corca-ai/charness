#!/usr/bin/env python3
"""Author-time required-shape source for the goal-closeout complete gate.

``check_goal_artifact.py`` (at the complete flip) enforces closeout-evidence
forms an author otherwise discovers by failing the flip several times (the
recurring authoring-preflight class). This module is the *shape source* the
artifact-surface preflight dispatcher reads for ``--type goal-closeout``,
alongside the goal template's ``## Final Verification``
block: the template seeds the lines to author into, and this module surfaces the
enforced FORMS the template prose leaves implicit.

It never re-declares the contract: the allowed skip-reason enum and the
disposition opt-out floor are rendered from the LIVE enforced constants, so the
surfaced shape cannot drift from the gate.

A2 (goal-conditional describe): with ``--goal-path <artifact>`` this module reads
the in-progress goal and emits only the floors *that goal* triggers (and which
are still missing), folding the dry ``check_goal_artifact.py`` pass the
After-phase used to run separately. It does NOT re-derive any floor logic: it
runs the LIVE ``check_complete_evidence`` + ``check_timebox_closeout`` reports and
reads their scope/trigger/refusal fields, so the goal-conditional view cannot
drift from the gate either. It stays an authoring affordance — never a
precondition that blocks the flip; ``check_goal_artifact.py`` remains the
authoritative complete-flip gate. Scope non-claim: the proof-mismatch floor
(``scripts/proof_mismatch.py``, a portable ``from scripts.`` module) and the
mutable-HEAD freshness floor are outside this view; neither is a D-audit
conditional ``keep`` floor and both stay the flip gate's job.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from typing import Any


def _load_sibling(module_name: str) -> Any:
    spec = importlib.util.spec_from_file_location(
        module_name, Path(__file__).resolve().parent / f"{module_name}.py"
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"{module_name}.py not found beside describe_goal_closeout_shape.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_repo_script(module_name: str) -> Any:
    """Load a repo-root ``scripts/<module_name>.py`` via the nearest ``scripts/``
    ancestor — the clone-safe walk the skill packages use, resolving in the
    working tree and the installed plugin export alike."""
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        candidate = ancestor / "scripts" / f"{module_name}.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location(module_name, candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError(f"scripts/{module_name}.py not found")


# Single sources: the skip-reason enum, the disposition-line form summaries, and
# the opt-out min length are read live from the validators that enforce them.
_PRESCRIBED = _load_repo_script("check_prescribed_skill_executed_lib")
_DISPOSITION_FORM = _load_repo_script("disposition_form")
_DISPOSITION = _load_sibling("goal_artifact_disposition_grammar")


def required_shape() -> str:
    skip_enum = ", ".join(sorted(_PRESCRIBED.ALLOWED_SKIP_REASONS))
    min_skip = _PRESCRIBED.MIN_SKIP_LENGTH
    min_optout = _DISPOSITION.MIN_OPTOUT_REASON
    valid_form = _DISPOSITION_FORM.VALID_FORM_SUMMARY
    dest_form = _DISPOSITION_FORM.DESTINATION_FORM_SUMMARY
    lines = [
        "goal-closeout required shape (enforced by `check_goal_artifact.py` at the",
        "complete flip — `Status: complete`). The template above seeds the lines;",
        "these are the FORMS the gate enforces on them:",
        "",
        "`## Final Verification` — `Retro:`, `Host log probe:`, and (for in-scope goals)",
        "`Disposition review:` each must be EITHER:",
        "  - a bound `<path>`: the evidence file EXISTS, is non-empty, and BINDS to this",
        "    goal — its basename or content contains the goal slug (the Activation line's",
        "    `/goal @<...-slug>` minus the date prefix). Citing an unrelated pre-existing",
        "    artifact fails the binding check. A bare path, not `<path>`/`TODO`/`TBD`.",
        f"  - OR `skipped: <reason>: <detail>` where <reason> is one of: {skip_enum}",
        f"    (free text is rejected) and the whole reason is >= {min_skip} chars.",
        "",
        "`## Coordination Cues` — `Routing:` must NAME both `find-skills` and the routed",
        "skill for recorded work (e.g. `Routing: find-skills recommended achieve for the",
        "goal lifecycle`), or `Routing: n/a — <reason>` (>= 30 chars). Gather/Release/Issue",
        "closeout floors fire the same way — see `--type goal-coordination` for the full shape.",
        "",
        "`## Auto-Retro` — the disposition floor: replace the seeded `Retro dispositions: TODO`.",
        f"  - per-improvement / opt-out (`Retro dispositions:`), one of: {valid_form}",
        f"    (the `none — <reason>` opt-out is >= {min_optout} chars; bare prose/memory is rejected).",
        f"  - `Structural follow-up:` (when the retro names transferable waste), one of: {dest_form}",
        "A blank/placeholder `## Auto-Retro` with a cited retro listing improvements is refused.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def stub() -> str:
    """A starter closeout block (bound evidence paths + a disposition opt-out)."""
    return (
        "<!-- goal-closeout starter; bind each path to THIS goal's slug, or use a "
        "skipped: <allowed-reason>: <detail> line. Run --type goal-closeout for the forms. -->\n"
        "## Final Verification\n\n"
        "Retro: charness-artifacts/retro/<date>-<goal-slug>.md\n"
        "Host log probe: charness-artifacts/retro/<date>-<goal-slug>-host-log.md\n"
        "Disposition review: charness-artifacts/critique/<date>-<goal-slug>-disposition-review.md\n\n"
        "## Auto-Retro\n\n"
        "Retro dispositions: none — <>=30-char reason no surfaced improvement needs active disposition>\n"
    )


def _evidence_unsatisfied(ev: dict[str, Any], name: str) -> str | None:
    """Why the always-required/scope-gated evidence ``name`` is unmet, else None.

    Reads the live ``check_complete_evidence`` refusal sets directly (no
    re-derivation), so it cannot diverge from the gate.
    """
    if name in ev.get("missing", []):
        return "missing line (or an untouched TODO/<path> placeholder)"
    for entry in ev.get("missing_evidence_files", []):
        if entry.get("name") == name:
            return f"evidence file not found: {entry.get('path', '')}"
    for entry in ev.get("invalid_skips", []):
        if entry.get("name") == name:
            return "skip reason is not an allowed enum"
    for entry in ev.get("binding_failures", []):
        if entry.get("name") == name:
            return "evidence file does not bind to this goal's slug"
    return None


def _evidence_row(name: str, label: str, ev: dict[str, Any], form_hint: str) -> dict[str, Any]:
    unsat = _evidence_unsatisfied(ev, name)
    return {"floor": name, "label": label, "triggered": True, "satisfied": unsat is None, "detail": unsat or form_hint}


def _floor_rows(ev: dict[str, Any], tb: dict[str, Any], early_close_required: bool) -> list[dict[str, Any]]:
    """The goal-conditional floor catalog, read from the live reports.

    Each row records whether the floor is ``triggered`` for *this* goal (its
    scope/content trigger, taken from the floor module's own report fields) and
    whether it is currently ``satisfied`` (no corresponding refusal). The form
    rungs 1c/1d/1f are surfaced only when they actively refuse — that is exactly
    the "goal-conditional missing-line set" the After-phase needs, and reading the
    refusal field keeps them drift-free.
    """
    disp = ev.get("disposition_scope", {})
    in_scope = bool(disp.get("in_scope"))
    rows: list[dict[str, Any]] = [
        _evidence_row("retro_artifact", "`Retro:` closeout evidence", ev,
                      "bound retro `<path>` (basename/content carries the goal slug) or `skipped: <enum>: <detail>`"),
        _evidence_row("host_log_probe", "`Host log probe:` closeout evidence", ev,
                      "bound host-log `<path>` or `skipped: <enum>: <detail>`"),
        {"floor": "disposition_review", "label": "`Disposition review:` line (rung 1b)",
         "triggered": in_scope, "satisfied": _evidence_unsatisfied(ev, "disposition_review") is None,
         "detail": _evidence_unsatisfied(ev, "disposition_review")
         or "bound `Disposition review: <path>` or `skipped: host-blocked-subagent: <detail>`"},
        {"floor": "disposition_blank", "label": "`## Auto-Retro` not blank (rung 1a)",
         "triggered": in_scope and bool(ev.get("retro_improvements_present")),
         "satisfied": ev.get("disposition_blank") is None,
         "detail": (ev.get("disposition_blank") or {}).get(
             "reason", "disposition each cited improvement (`applied:`/`issue #N`) or record a `Retro dispositions: none — <reason>` opt-out")},
    ]
    for key, label in (("disposition_form", "`## Auto-Retro` disposition FORM (rung 1c)"),
                       ("recurrence_lineage", "`issue #N` recurrence-lineage marker (rung 1d)"),
                       ("residual_ledger", "`## Residual Ledger` row disposition (rung 1f)")):
        problem = ev.get(key)
        rows.append({"floor": key, "label": label, "triggered": bool(problem),
                     "satisfied": False, "detail": (problem or {}).get("reason", "")})
    sf_scope = ev.get("structural_followup_scope", {})
    sf = ev.get("structural_followup")
    rows.append({"floor": "structural_followup", "label": "`Structural follow-up:` destination (rung 1e)",
                 "triggered": bool(sf_scope.get("enforced") and sf_scope.get("transferable_waste_named")),
                 "satisfied": sf is None,
                 "detail": (sf or {}).get("reason") if sf else
                 "the cited retro names transferable waste; add a `Structural follow-up: <destination>` line"})
    for key, sub, label in (
        ("phase_routing", "phase_routing_floor", "`Routing:` names find-skills + the routed skill"),
        ("gather", "gather_floor", "`Gather:` routes the external source through gather"),
        ("release", "release_floor", "`Release:` verifies the release surface"),
        ("issue_closeout", "issue_closeout_floor", "`Issue closeout:` stages the tracked-issue close"),
    ):
        floor = ev.get(sub, {})
        rows.append({"floor": key, "label": label, "triggered": bool(floor.get("triggered")),
                     "satisfied": bool(floor.get("satisfied", True)),
                     "detail": floor.get("reason") or "satisfied: a real step line or `n/a — <reason>` opt-out is recorded"})
    deleg = ev.get("closeout_delegation", {})
    mode = deleg.get("mode", "standalone")
    failures = deleg.get("failures", [])
    rows.append({"floor": "closeout_delegation", "label": f"`## Closeout Delegation` ({mode}) checklist",
                 "triggered": bool(deleg.get("declared")) and mode in {"orchestrated", "orchestrator"},
                 "satisfied": not failures,
                 "detail": "; ".join(failures) if failures else "every delegated-proof item resolved (verified/skipped/issue #N)"})
    placeholders = ev.get("section_placeholders", [])
    rows.append({"floor": "section_placeholders", "label": "no seeded section placeholders remain (final-status floor)",
                 "triggered": bool(placeholders), "satisfied": not placeholders,
                 "detail": ", ".join(f"{p['section']} (line {p['line']}: {p['marker']!r})" for p in placeholders)
                 or "no section's first body line is a TODO/TBD/pending placeholder"})
    rows.append({"floor": "early_close_report", "label": "early-close report shape",
                 "triggered": bool(early_close_required),
                 "satisfied": _evidence_unsatisfied(ev, "early_close_report") is None,
                 "detail": _evidence_unsatisfied(ev, "early_close_report") or "early-close report present and well-formed"})
    rows.append({"floor": "timebox", "label": "timebox closeout window",
                 "triggered": bool(tb.get("applies")), "satisfied": bool(tb.get("ok", True)),
                 "detail": "; ".join(tb.get("issues", [])) or f"timebox status: {tb.get('status')}"})
    return rows


def goal_conditional_shape(repo_root: Path, text: str) -> dict[str, Any]:
    """Evaluate which closeout floors *this* goal triggers, and which are met.

    Runs the live ``check_complete_evidence`` + ``check_timebox_closeout`` reports
    (the same the complete flip uses) and classifies each floor — no floor logic
    is re-implemented here.
    """
    closeout = _load_sibling("goal_artifact_closeout_evidence")
    timebox = _load_sibling("goal_artifact_timebox")
    ev = closeout.check_complete_evidence(repo_root, text)
    tb = timebox.check_timebox_closeout(text)
    rows = _floor_rows(ev, tb, bool(closeout._early_close_report.report_required(text)))
    triggered = [row for row in rows if row["triggered"]]
    return {
        "triggered": triggered,
        "missing": [row for row in triggered if not row["satisfied"]],
        "not_triggered": [row["floor"] for row in rows if not row["triggered"]],
    }


def render_goal_conditional(report: dict[str, Any], rel_path: str) -> str:
    missing = report["missing"]
    satisfied = [row for row in report["triggered"] if row["satisfied"]]
    lines = [
        f"goal-closeout shape for `{rel_path}` — goal-conditional: only the floors THIS",
        "goal triggers are listed (grandfathered / no-trigger floors are omitted). This is",
        "an authoring affordance run before drafting closeout; it does NOT block the flip —",
        "`check_goal_artifact.py` stays the authoritative complete-flip gate.",
        "",
    ]
    if missing:
        lines.append("MISSING — fill before flipping to `complete`:")
        lines.extend(f"  - {row['label']}: {row['detail']}" for row in missing)
    else:
        lines.append("MISSING — none: every triggered floor is currently satisfied.")
    lines.append("")
    if satisfied:
        lines.append("SATISFIED — already met (no action):")
        lines.extend(f"  - {row['label']}" for row in satisfied)
        lines.append("")
    lines.append(
        f"({len(report['not_triggered'])} floor(s) not triggered for this goal: "
        + ", ".join(report["not_triggered"]) + ".)"
    )
    lines += ["", "Form reference (how to fill the MISSING lines above):", "", required_shape().rstrip()]
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--goal-path", type=Path, help="Emit the goal-conditional triggered-floor set for this artifact (A2)")
    mode.add_argument("--stub", action="store_true", help="Emit a starter closeout block")
    args = parser.parse_args(argv)
    if args.goal_path is not None:
        path = args.goal_path.expanduser().resolve()
        if not path.exists():
            sys.stderr.write(f"goal artifact not found: {path}\n")
            return 2
        repo_root = args.repo_root.expanduser().resolve()
        try:
            rel = path.relative_to(repo_root).as_posix()
        except ValueError:
            rel = str(path)
        report = goal_conditional_shape(repo_root, path.read_text(encoding="utf-8"))
        sys.stdout.write(render_goal_conditional(report, rel))
        return 0
    sys.stdout.write(stub() if args.stub else required_shape())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
