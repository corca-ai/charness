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
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = ROOT / "skills/public/achieve/scripts/describe_goal_closeout_shape.py"


def _load():
    spec = importlib.util.spec_from_file_location("describe_goal_closeout_shape", _SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


desc = _load()


def _assert_help_pairs(output: str, expected_pairs: dict[str, str]) -> None:
    """Assert each fragment belongs to its option block, not only usage text."""
    for option, fragment in expected_pairs.items():
        match = re.search(rf"^  {re.escape(option)}\b.*$", output, re.MULTILINE)
        assert match, f"missing help option: {option}"
        next_option = re.search(r"^  --[a-z][a-z-]*\b", output[match.end() :], re.MULTILINE)
        end = match.end() + next_option.start() if next_option else len(output)
        option_block = re.sub(r"\s+", " ", output[match.start() : end])
        assert fragment in option_block, f"missing help for {option}: {fragment}"


def test_describe_goal_closeout_shape_help_describes_repo_root() -> None:
    result = subprocess.run(
        [sys.executable, str(_SCRIPT), "--help"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    _assert_help_pairs(result.stdout, {"--repo-root": "Repo root for resolving goal evidence paths."})


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


def test_evidence_unsatisfied_covers_every_refusal_branch() -> None:
    ev = {
        "missing": ["retro_artifact"],
        "missing_evidence_files": [{"name": "host_log_probe", "path": "h.md"}],
        "invalid_skips": [{"name": "disposition_review"}],
        "binding_failures": [{"name": "early_close_report"}],
    }
    assert desc._evidence_unsatisfied(ev, "retro_artifact") == "missing line (or an untouched TODO/<path> placeholder)"
    assert "not found: h.md" in desc._evidence_unsatisfied(ev, "host_log_probe")
    assert "enum" in desc._evidence_unsatisfied(ev, "disposition_review")
    assert "bind" in desc._evidence_unsatisfied(ev, "early_close_report")
    assert desc._evidence_unsatisfied(ev, "not_present") is None


def test_evidence_unsatisfied_surfaces_hollow_early_close_report() -> None:
    # A present, bound early-close report can still refuse the flip on section-body
    # shape (`apply_report_shape` -> invalid_early_close_reports -> ok=False). That
    # refusal channel is name-scoped nowhere in the other refusal sets, so without
    # this branch the row falsely reads "present and well-formed" while the flip is
    # refused with no reason (the describe/gate drift a fresh-eye caught).
    ev = {
        "invalid_early_close_reports": [
            {"path": "r.md", "failures": [{"section": "waste_retro", "reason": "required section body is hollow"}]}
        ],
    }
    detail = desc._evidence_unsatisfied(ev, "early_close_report")
    assert detail is not None and "waste_retro" in detail and "hollow" in detail
    # the report-scoped refusal must not leak into a different floor's row
    assert desc._evidence_unsatisfied(ev, "retro_artifact") is None


def test_goal_conditional_surfaces_hollow_early_close_report(tmp_path: Path) -> None:
    # Integration: a triggered early-close goal whose report is PRESENT + BOUND but
    # has a hollow section must land in the goal-conditional MISSING set (with the
    # shape reason), not read as a satisfied "present and well-formed" floor.
    slug, created = "hollow-early", "2026-06-14"
    retro = tmp_path / "charness-artifacts/retro" / f"{created}-{slug}.md"
    probe = tmp_path / "charness-artifacts/probe" / f"{created}-{slug}.json"
    report_file = tmp_path / "charness-artifacts/goals" / f"{created}-{slug}-early-close-report.md"
    hollow_report = (
        f"# Early Close Report — {slug}\n\n"
        "## Why early closeout was chosen\n\nNo safe next slice remained; only unsafe work was left.\n\n"
        "## What user decisions are needed\n\nWhether to push or defer the carrier commit.\n\n"
        "## Waste and retro\n\nNone.\n"  # terse body -> `required section body is hollow`
    )
    for target, body in (
        (retro, f"# Retro for {slug}\n\nbody\n"),
        (probe, f'{{"goal":"{slug}"}}\n'),
        (report_file, hollow_report),
    ):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    text = _preamble(slug, created) + (
        "## Goal\n\nReal outcome.\n\n"
        "## Final Verification\n\n"
        "No safe next slice: only unsafe release work remains and user confirmation is required first.\n"
        f"Retro: {retro.relative_to(tmp_path)}\n"
        f"Host log probe: {probe.relative_to(tmp_path)}\n"
        f"Early close report: {report_file.relative_to(tmp_path)}\n\n"
        "## Auto-Retro\n\napplied: no deferred report gap remains\n"
    )
    report = desc.goal_conditional_shape(tmp_path, text)
    assert "early_close_report" in _missing_keys(report)
    row = next(r for r in report["missing"] if r["floor"] == "early_close_report")
    assert "shape invalid" in row["detail"] and "waste_retro" in row["detail"] and "hollow" in row["detail"]
    # the false-green wording must be gone from a genuinely-hollow report
    assert "present and well-formed" not in row["detail"]


def test_render_shows_missing_none_and_satisfied_block() -> None:
    report = {
        "triggered": [
            {"floor": "a", "label": "Floor A", "satisfied": True, "detail": "ok"},
            {"floor": "b", "label": "Floor B", "satisfied": True, "detail": "ok"},
        ],
        "missing": [],
        "not_triggered": ["gather", "release"],
    }
    out = desc.render_goal_conditional(report, "g.md")
    assert "MISSING — none: every triggered floor is currently satisfied." in out
    assert "SATISFIED — already met" in out
    assert "Floor A" in out and "Floor B" in out


def test_goal_path_outside_repo_root_falls_back_to_abs_path(tmp_path: Path, capsys) -> None:
    # goal lives OUTSIDE --repo-root -> path.relative_to(repo_root) raises
    # ValueError -> the rendered header uses the absolute path, not a crash.
    repo = tmp_path / "repo"
    repo.mkdir()
    goal = tmp_path / "outside-goal.md"
    goal.write_text(_preamble("outside-goal", "2026-06-14") + "## Goal\n\nx.\n", encoding="utf-8")
    assert desc.main(["--repo-root", str(repo), "--goal-path", str(goal)]) == 0
    assert str(goal.resolve()) in capsys.readouterr().out


def test_static_catalog_path_is_unchanged(capsys) -> None:
    # backward-compat: no --goal-path -> the dispatcher-facing static required_shape
    assert desc.main([]) == 0
    static = capsys.readouterr().out
    assert "goal-closeout required shape" in static
    assert "goal-conditional" not in static  # the static catalog is not the goal-aware view


def test_closeout_stub_lives_in_template_asset() -> None:
    template = (
        ROOT
        / "skills"
        / "public"
        / "achieve"
        / "scripts"
        / "templates"
        / "closeout_stub.txt"
    )
    assert template.read_text(encoding="utf-8") == desc.stub()


# --- the module that documents the cure had the disease ----------------------
#
# Its own docstring says it "never re-declares the contract... rendered from the
# LIVE enforced constants, so the surfaced shape cannot drift from the gate" --
# and it typed the floor numbers by hand, so one constant edit silently staled
# the operator-facing strings. These tests move each constant and require the
# rendered text to follow, which is the only way that claim is checkable.


def _shape() -> str:
    return desc.required_shape()


def test_no_floor_number_is_typed_into_this_module() -> None:
    """The literal check the goal's acceptance names. A number written here is a
    second copy of a floor, and a second copy is what drifts."""
    source = _SCRIPT.read_text(encoding="utf-8")
    body = "\n".join(
        line for line in source.splitlines()
        if "chars" in line and not line.lstrip().startswith("#")
    )
    assert "30 chars" not in body
    assert "20+ chars" not in body
    # Every rendered char-floor must interpolate rather than state a number.
    for line in body.splitlines():
        if ">= " in line and "chars" in line:
            assert "{" in line, f"floor number typed by hand: {line.strip()}"


def test_the_skip_reason_floor_is_rendered_from_the_live_constant(monkeypatch) -> None:
    monkeypatch.setattr(desc._PRESCRIBED, "MIN_SKIP_LENGTH", 4321)
    assert "4321 chars" in _shape()


def test_the_disposition_optout_floor_is_rendered_from_the_live_constant(monkeypatch) -> None:
    monkeypatch.setattr(desc._DISPOSITION, "MIN_OPTOUT_REASON", 4322)
    assert "4322 chars" in _shape()


def test_the_operator_queue_floor_is_rendered_from_the_live_constant(monkeypatch) -> None:
    monkeypatch.setattr(desc._OPERATOR_QUEUE, "MIN_EMPTY_QUEUE_REASON", 4323)
    assert "4323 chars" in _shape()


def test_the_declarable_phases_are_rendered_from_the_live_tuple(monkeypatch) -> None:
    monkeypatch.setattr(desc._PHASE_ROUTING, "DECLARABLE_PHASES", ("fabricated",))
    assert "`fabricated`" in _shape()


def test_the_queue_floor_number_and_its_own_regex_cannot_disagree() -> None:
    """The number lived inside a regex quantifier AND in two prose surfaces. The
    pattern is now built from the constant, so a change cannot move one without
    the other."""
    queue = desc._OPERATOR_QUEUE
    minimum = queue.MIN_EMPTY_QUEUE_REASON
    assert queue._EMPTY.search("none — " + "x" * minimum)
    assert not queue._EMPTY.search("none — " + "x" * (minimum - 1))
