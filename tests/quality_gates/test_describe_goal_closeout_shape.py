"""A2 (goal-conditional describe) tests for ``describe_goal_closeout_shape.py``.

The ``--goal-path`` mode reads the in-progress goal and emits only the floors
*that goal* triggers (and which are still missing), reusing the live
``check_complete_evidence`` + ``check_timebox_closeout`` reports — never
re-deriving floor logic. The static ``required_shape()`` catalog cannot surface
the runtime-conditional floors (the D-audit ``keep`` set: rungs 1a/1b/1e,
section-placeholder, closeout-delegation, timebox); these tests prove the
goal-conditional view does, and that grandfathered floors stay omitted.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = ROOT / "skills/public/achieve/scripts/describe_goal_closeout_shape.py"


def _load():
    spec = importlib.util.spec_from_file_location("describe_goal_closeout_shape", _SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


desc = _load()


def _preamble(slug: str, created: str) -> str:
    return (
        f"# Achieve Goal: {slug}\n\n"
        f"Status: active\nCreated: {created}\n"
        f"Activation: `/goal @charness-artifacts/goals/{created}-{slug}.md`\n\n"
    )


def _triggered_keys(report: dict) -> set[str]:
    return {row["floor"] for row in report["triggered"]}


def _missing_keys(report: dict) -> set[str]:
    return {row["floor"] for row in report["missing"]}


def test_bare_grandfathered_goal_triggers_only_baseline_evidence(tmp_path: Path) -> None:
    # Old Created date -> every runtime-conditional scope floor is grandfathered;
    # no gather/release/issue/timebox/delegation content -> nothing else fires.
    text = _preamble("bare-floor", "2026-05-01") + (
        "## Active Operating Frame\n\n- Current slice: bare fixture.\n\n"
        "## Goal\n\nReal outcome text.\n\n"
        "## Context Sources\n\n- charness-artifacts/spec/x.md (repo-local, no URL)\n\n"
        "## Slice Log\n\nReal slice notes, no release/issue work.\n\n"
        "## Coordination Cues\n\nReal routing notes.\n\n"
        "## Final Verification\n\nReal verification notes.\n\n"
        "## Auto-Retro\n\nReal retro notes.\n"
    )
    report = desc.goal_conditional_shape(tmp_path, text)
    assert _triggered_keys(report) == {"retro_artifact", "host_log_probe"}
    # the runtime-conditional floors are correctly omitted (grandfathered / no trigger)
    for floor in ("disposition_review", "gather", "release", "issue_closeout",
                  "timebox", "closeout_delegation", "phase_routing", "structural_followup"):
        assert floor in report["not_triggered"], floor


def test_multi_floor_goal_triggers_the_conditional_floors(tmp_path: Path) -> None:
    # Recent Created (in scope) + content that trips gather/release/issue/timebox/
    # delegation. Coordination Cues left empty so each is triggered-and-missing.
    text = _preamble("multi-floor", "2026-06-14") + (
        "## Active Operating Frame\n\n"
        "- Timebox: 2h\n- Activation time: 2026-06-14T00:00:00Z\n"
        "- Closeout reserve: 20m\n- Done-early policy: continue_next_improvement\n\n"
        "## Goal\n\nReal outcome text.\n\n"
        "## Context Sources\n\n- https://example.com/external-source\n\n"
        "## Slice Log\n\n- What changed: bump_version in the manifest. Closes #123.\n\n"
        "## Closeout Delegation\n\nCloseout mode: orchestrated\n\n"
        "## Coordination Cues\n\n_no step lines yet_\n\n"
        "## Final Verification\n\n_no evidence lines yet_\n\n"
        "## Auto-Retro\n\n_pending_\n"
    )
    report = desc.goal_conditional_shape(tmp_path, text)
    triggered = _triggered_keys(report)
    # the content-conditional floors a static catalog cannot name are all surfaced
    for floor in ("gather", "release", "issue_closeout", "timebox",
                  "closeout_delegation", "disposition_review", "phase_routing"):
        assert floor in triggered, floor
        assert floor not in report["not_triggered"], floor
    # ... and each is in the actionable MISSING set (unsatisfied)
    missing = _missing_keys(report)
    for floor in ("gather", "release", "issue_closeout", "closeout_delegation"):
        assert floor in missing, floor


def test_structural_followup_keep_floor_surfaced_from_bound_retro(tmp_path: Path) -> None:
    # The headline A2 case: a runtime-conditional `keep` floor (rung 1e) the static
    # catalog structurally cannot surface. A bound retro that names transferable
    # waste (a `## Sibling Search` decision bullet) + lists improvements must make
    # the goal-conditional view trigger structural_followup AND the block-the-blank
    # rung 1a, even though neither is derivable from constants alone.
    slug = "structural-keep"
    retro_rel = f"charness-artifacts/retro/2026-06-14-{slug}-retro.md"
    retro = tmp_path / retro_rel
    retro.parent.mkdir(parents=True, exist_ok=True)
    retro.write_text(
        f"# Retro {slug}\n\n"
        "## Next Improvements\n\n- improve the closeout describe affordance\n\n"
        "## Sibling Search\n\n- recurring describe-first gap | decision: applied as a guard\n",
        encoding="utf-8",
    )
    text = _preamble(slug, "2026-06-14") + (
        "## Active Operating Frame\n\n- Current slice: 1e fixture.\n\n"
        "## Goal\n\nReal outcome.\n\n"
        "## Coordination Cues\n\nRouting: n/a — fixture records no phase work needing a route here today.\n\n"
        f"## Final Verification\n\nRetro: {retro_rel}\n"
        "Host log probe: skipped: host-log-not-exposed: this host does not expose per-goal token timings here\n\n"
        "## Auto-Retro\n\n"  # deliberately blank to exercise rung 1a (block-the-blank)
    )
    report = desc.goal_conditional_shape(tmp_path, text)
    triggered = _triggered_keys(report)
    assert "structural_followup" in triggered  # rung 1e: the conditional keep floor
    assert "disposition_blank" in triggered  # rung 1a: cited retro lists improvements + blank Auto-Retro
    assert {"structural_followup", "disposition_blank"} <= _missing_keys(report)
    # retro evidence binds (filename carries the slug) -> retro_artifact is satisfied
    retro_row = next(r for r in report["triggered"] if r["floor"] == "retro_artifact")
    assert retro_row["satisfied"], retro_row


def test_goal_path_mode_is_nonblocking_and_renders(tmp_path: Path, capsys) -> None:
    goal = tmp_path / "g.md"
    goal.write_text(
        _preamble("render-check", "2026-06-14")
        + "## Goal\n\nReal outcome.\n\n## Final Verification\n\n_pending_\n",
        encoding="utf-8",
    )
    # the affordance never blocks: exit code is 0 even with floors unmet
    code = desc.main(["--repo-root", str(tmp_path), "--goal-path", str(goal)])
    assert code == 0
    out = capsys.readouterr().out
    assert "goal-conditional" in out
    assert "MISSING" in out
    assert "Form reference" in out  # the static forms travel with the one call
    # only triggered floors are rendered: a non-triggered floor's label is absent
    assert "external source routed through gather" not in out


def test_goal_path_missing_file_reports_and_does_not_crash(tmp_path: Path, capsys) -> None:
    code = desc.main(["--repo-root", str(tmp_path), "--goal-path", str(tmp_path / "nope.md")])
    assert code == 2
    assert "not found" in capsys.readouterr().err


def test_static_catalog_path_is_unchanged(capsys) -> None:
    # backward-compat: no --goal-path -> the dispatcher-facing static required_shape
    assert desc.main([]) == 0
    static = capsys.readouterr().out
    assert "goal-closeout required shape" in static
    assert "goal-conditional" not in static  # the static catalog is not the goal-aware view
