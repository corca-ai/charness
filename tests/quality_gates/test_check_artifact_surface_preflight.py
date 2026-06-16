from __future__ import annotations

import importlib.util
import runpy
import sys
from dataclasses import replace
from pathlib import Path

import pytest

from scripts import check_artifact_surface_preflight as preflight

from .support import ROOT

# --- registry / surface resolution (pure) -------------------------------------


def test_surface_for_path_maps_prefix_families() -> None:
    assert preflight.surface_for_path("charness-artifacts/critique/x.md").artifact_type == "critique"
    assert preflight.surface_for_path("charness-artifacts/ideation/x.md").artifact_type == "ideation"
    assert preflight.surface_for_path("charness-artifacts/retro/x.md").artifact_type == "retro"
    # unknown / non-md / out-of-family -> None
    assert preflight.surface_for_path("charness-artifacts/spec/x.md") is None
    assert preflight.surface_for_path("scripts/x.py") is None
    assert preflight.surface_for_path("charness-artifacts/critique/x.txt") is None


def test_retro_surface_excludes_rolled_up_and_history() -> None:
    # the retro validator skips recent-lessons.md and history/, so the commit-
    # boundary arm must not block on them either.
    assert preflight.surface_for_path("charness-artifacts/retro/recent-lessons.md") is None
    assert preflight.surface_for_path("charness-artifacts/retro/history/2026-01-01-x.md") is None
    assert preflight.surface_for_path("charness-artifacts/retro/2026-06-08-x.md").artifact_type == "retro"


def test_surface_for_path_maps_adapter_scoped_trio() -> None:
    # debug/quality default dirs + handoff's default docs/handoff.md file.
    assert preflight.surface_for_path("charness-artifacts/debug/x.md").artifact_type == "debug"
    assert preflight.surface_for_path("charness-artifacts/quality/x.md").artifact_type == "quality"
    assert preflight.surface_for_path("docs/handoff.md").artifact_type == "handoff"
    # other docs/*.md are not the handoff artifact.
    assert preflight.surface_for_path("docs/other.md") is None
    # adapter-scoped validators validate-all (no --paths) and are author-time-only
    # (NOT in the fail-fast commit-boundary sweep — a validate-all gate there would
    # reorder the deeper closeout stages).
    for t in ("debug", "quality", "handoff"):
        assert preflight.surface_for_type(t).paths_arg is False
        assert preflight.surface_for_type(t).commit_boundary is False


def test_surface_for_type_and_goal_closeout_has_no_scaffold() -> None:
    goal = preflight.surface_for_type("goal-closeout")
    assert goal is not None
    assert goal.scaffold is None  # validator-constants/template row, not a scaffold
    assert goal.commit_boundary is False  # owned by the achieve complete-flip
    assert preflight.surface_for_type("nope") is None


def test_extract_section_pulls_named_block() -> None:
    text = "intro\n## A\nbody a\n## B\nbody b\n"
    assert preflight._extract_section(text, "## A").strip() == "## A\nbody a"
    assert "not found" in preflight._extract_section(text, "## Z")


# --- commit-boundary grouping + blocking (logic, no real validators) ----------


def _fake_run(rc_for):
    def runner(repo_root, argv):
        import subprocess

        joined = " ".join(argv)
        return subprocess.CompletedProcess(argv, rc_for(joined), stdout="out\n", stderr="err\n")

    return runner


def test_changed_artifacts_groups_by_validator_and_passes(monkeypatch) -> None:
    monkeypatch.setattr(preflight, "_run", _fake_run(lambda _cmd: 0))
    report = preflight.changed_artifacts(
        ROOT,
        [
            "charness-artifacts/critique/a.md",
            "charness-artifacts/critique/b.md",
            "charness-artifacts/ideation/c.md",
            "charness-artifacts/retro/recent-lessons.md",  # excluded -> ignored
            "scripts/x.py",  # out-of-family -> ignored
        ],
    )
    assert report["status"] == "ok"
    # two owning validators (critique + ideation); the critique one carries both paths
    checked = {row["validator"]: row["paths"] for row in report["checked"]}
    assert "scripts/validate_critique_artifacts.py" in checked
    assert checked["scripts/validate_critique_artifacts.py"] == [
        "charness-artifacts/critique/a.md",
        "charness-artifacts/critique/b.md",
    ]
    assert "scripts/validate_ideation_artifact.py" in checked
    # recent-lessons + scripts produced no group
    assert "scripts/validate_retro_artifact.py" not in checked


def test_changed_artifacts_blocks_when_owning_validator_fails(monkeypatch) -> None:
    monkeypatch.setattr(preflight, "_run", _fake_run(lambda cmd: 1 if "critique" in cmd else 0))
    report = preflight.changed_artifacts(
        ROOT,
        ["charness-artifacts/critique/bad.md", "charness-artifacts/ideation/ok.md"],
    )
    assert report["status"] == "blocked"
    assert report["blocked"] == ["scripts/validate_critique_artifacts.py"]


def test_changed_artifacts_skips_author_time_only_surfaces(monkeypatch) -> None:
    # debug/quality/handoff are author-time-only (commit_boundary=False), so the
    # commit-boundary arm must NOT run them even when their paths change — the broad
    # gate is their enforcement, and the fail-fast sweep stays changed-scoped.
    captured: list[list[str]] = []

    def fake_run(repo_root, argv):
        import subprocess

        captured.append(argv)
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    monkeypatch.setattr(preflight, "_run", fake_run)
    report = preflight.changed_artifacts(
        ROOT,
        ["charness-artifacts/debug/a.md", "charness-artifacts/quality/b.md", "docs/handoff.md"],
    )
    assert report["status"] == "ok"
    assert report["checked"] == []  # none of the trio run at the commit boundary
    assert captured == []


def test_changed_artifacts_noop_for_unrelated_paths(monkeypatch) -> None:
    monkeypatch.setattr(preflight, "_run", _fake_run(lambda _cmd: 1))
    report = preflight.changed_artifacts(ROOT, ["docs/x.md", "scripts/y.py"])
    assert report["status"] == "ok"
    assert report["checked"] == []


# --- in-process integration against the real repo -----------------------------
# Called in-process (not via subprocess) on purpose: the dispatcher is import-safe,
# so testing it in-process keeps it off the boundary-bypass ratchet. The dispatcher
# still subprocesses the real scaffold/validator internally, so these remain honest
# end-to-end checks of the shape source + the relocated verdict.


def test_describe_goal_closeout_reads_template() -> None:
    surface = preflight.surface_for_type("goal-closeout")
    out = preflight.describe(ROOT, surface, target_rel=None)
    assert "## Final Verification" in out
    assert "Disposition review:" in out
    # goal-closeout has no shape validator at the commit boundary; the closeout owns it.
    assert "achieve closeout" in out


def test_emit_stub_critique_carries_required_sections() -> None:
    text, code = preflight.emit_stub(ROOT, preflight.surface_for_type("critique"))
    assert code == 0
    # the scaffold stub must carry the validator-required sections by construction
    assert "## Reviewer Tier Evidence" in text
    assert "## Structured Findings" in text


def test_describe_adapter_scoped_runs_validate_all_without_paths() -> None:
    # an adapter-scoped surface (paths_arg=False) must NOT get --paths in describe
    # (its validator has no such flag); it reports a surface-level validate-all
    # verdict. charness-artifacts/debug/latest.md is a real valid debug artifact.
    out = preflight.describe(ROOT, preflight.surface_for_type("debug"), target_rel="charness-artifacts/debug/latest.md")
    assert "owning validator: python3 scripts/validate_debug_artifact.py --repo-root ." in out
    assert "--paths" not in out
    assert "validate-all" in out


def test_emit_stub_goal_closeout_has_no_scaffold_message() -> None:
    text, code = preflight.emit_stub(ROOT, preflight.surface_for_type("goal-closeout"))
    assert code == 0
    assert "no scaffold script" in text


def test_changed_artifacts_passes_scaffold_roundtrip() -> None:
    # the critique scaffold's own render must pass its validator at the commit
    # boundary (round-trip), proving the shape-by-construction arm is real.
    stub_text, code = preflight.emit_stub(ROOT, preflight.surface_for_type("critique"))
    assert code == 0
    target = ROOT / "charness-artifacts" / "critique" / "_preflight_roundtrip_selftest.md"
    try:
        target.write_text(stub_text, encoding="utf-8")
        rel = target.relative_to(ROOT).as_posix()
        report = preflight.changed_artifacts(ROOT, [rel])
        assert report["status"] == "ok", report
    finally:
        target.unlink(missing_ok=True)


def test_main_errors_on_unknown_surface(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", ["x", "--path", "charness-artifacts/spec/x.md"])
    assert preflight.main() == 2
    assert "no registered surface" in capsys.readouterr().err


# --- #335: cover the changed-line gaps v0.28.0 left in this dispatcher ---------


def test_resolve_returns_raw_for_out_of_repo_path() -> None:
    # _resolve's ValueError arm: a path that does not live under the repo root is
    # returned verbatim (it can never map to a surface, but must not crash).
    assert preflight._resolve(ROOT, "/nonexistent/outside/x.md") == "/nonexistent/outside/x.md"


def test_shape_text_handles_each_missing_shape_source() -> None:
    critique = preflight.surface_for_type("critique")
    # scaffold render failure -> the "(could not render scaffold ...)" arm
    bad_scaffold = replace(critique, scaffold="scripts/does_not_exist_scaffold.py")
    assert "could not render scaffold" in preflight._shape_text(ROOT, bad_scaffold)
    # template-section source that points at a missing template -> "(template ... not found)"
    bad_template = replace(critique, scaffold=None, template_section="nope/missing.md|## Heading")
    assert "not found" in preflight._shape_text(ROOT, bad_template)
    # template-PREAMBLE source that points at a missing template -> "(template ... not found)"
    bad_preamble = replace(critique, scaffold=None, template_section=None, template_preamble="nope/missing.md")
    assert "not found" in preflight._shape_text(ROOT, bad_preamble)
    # no shape source at all -> "(no shape source registered)"
    no_source = replace(critique, scaffold=None, template_section=None)
    assert preflight._shape_text(ROOT, no_source) == "(no shape source registered)"


def test_emit_stub_scaffold_failure_returns_code_one() -> None:
    bad = replace(preflight.surface_for_type("critique"), scaffold="scripts/does_not_exist_scaffold.py")
    text, code = preflight.emit_stub(ROOT, bad)
    assert code == 1
    assert text  # surfaces the scaffold's stderr/stdout, not silence


def test_describe_prefix_surface_includes_paths_and_failure_detail(monkeypatch) -> None:
    # critique is paths_arg=True: describe must pass --paths AND, when the file
    # fails its owning validator, echo the failure detail. Force the FAIL arm via
    # a stubbed _run (independent of the critique validator's enforce-when-present
    # rules), which exercises describe's --paths/verdict/detail lines.
    import subprocess

    def failing_run(repo_root, argv):
        return subprocess.CompletedProcess(argv, 1, stdout="", stderr="missing reviewer-tier section")

    monkeypatch.setattr(preflight, "_run", failing_run)
    target = ROOT / "charness-artifacts" / "critique" / "_preflight_describe_selftest.md"
    try:
        target.write_text("# not a real critique\n", encoding="utf-8")
        rel = target.relative_to(ROOT).as_posix()
        out = preflight.describe(ROOT, preflight.surface_for_type("critique"), target_rel=rel)
        assert f"--paths {rel}" in out
        assert "current verdict on" in out and "FAIL" in out
        assert "missing reviewer-tier section" in out
    finally:
        target.unlink(missing_ok=True)


def test_format_changed_renders_ok_and_blocked_reports() -> None:
    ok_report = {"status": "ok", "checked": [
        {"validator": "scripts/validate_critique_artifacts.py", "paths": ["a.md"], "returncode": 0, "stdout": "", "stderr": ""},
    ]}
    ok_text = preflight._format_changed(ok_report)
    assert "artifact-shape-preflight: ok" in ok_text
    assert "[ok]" in ok_text

    blocked_report = {"status": "blocked", "checked": [
        {"validator": "scripts/validate_critique_artifacts.py", "paths": ["bad.md"], "returncode": 1, "stdout": "", "stderr": "missing section X"},
    ]}
    blocked_text = preflight._format_changed(blocked_report)
    assert "[BLOCK]" in blocked_text
    assert "missing section X" in blocked_text
    assert "owning validator failed at the commit boundary" in blocked_text


def test_main_changed_artifacts_text_and_json(monkeypatch, capsys) -> None:
    blocked = {"status": "blocked", "blocked": ["scripts/validate_critique_artifacts.py"], "checked": [
        {"validator": "scripts/validate_critique_artifacts.py", "paths": ["bad.md"], "returncode": 1, "stdout": "", "stderr": "boom"},
    ]}
    monkeypatch.setattr(preflight, "changed_artifacts", lambda repo_root, paths: blocked)
    # text mode -> _format_changed, exit 1 on blocked
    monkeypatch.setattr(sys, "argv", ["x", "--changed-artifacts", "charness-artifacts/critique/bad.md"])
    assert preflight.main() == 1
    assert "[BLOCK]" in capsys.readouterr().out
    # json mode -> json.dumps arm
    monkeypatch.setattr(sys, "argv", ["x", "--changed-artifacts", "charness-artifacts/critique/bad.md", "--json"])
    assert preflight.main() == 1
    assert '"status": "blocked"' in capsys.readouterr().out


def test_main_changed_artifacts_ok_returns_zero(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", ["x", "--changed-artifacts", "docs/unrelated.md"])
    assert preflight.main() == 0
    assert "artifact-shape-preflight: ok" in capsys.readouterr().out


def test_main_type_describes_surface(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", ["x", "--type", "goal-closeout"])
    assert preflight.main() == 0
    assert "## Final Verification" in capsys.readouterr().out


def test_main_emit_stub_writes_stub(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", ["x", "--type", "critique", "--emit-stub"])
    assert preflight.main() == 0
    assert "## Reviewer Tier Evidence" in capsys.readouterr().out


def test_main_requires_one_selector(monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["x"])
    with pytest.raises(SystemExit) as exc:  # parser.error exits 2
        preflight.main()
    assert exc.value.code == 2


# --- #335 Slice 4: goal-closeout / coordination-floor authoring surfaces --------


def test_goal_coordination_surface_reads_coordination_cues() -> None:
    surface = preflight.surface_for_type("goal-coordination")
    assert surface is not None
    assert surface.commit_boundary is False  # owned by the achieve complete flip
    out = preflight.describe(ROOT, surface, target_rel=None)
    assert "## Coordination Cues" in out
    assert "Routing" in out and "Issue closeout" in out
    assert "achieve closeout" in out  # validator=None -> owned at the flip


def test_goal_early_close_surface_renders_required_sections() -> None:
    surface = preflight.surface_for_type("goal-early-close")
    assert surface is not None
    assert surface.commit_boundary is False
    out = preflight.describe(ROOT, surface, target_rel=None)
    assert "## Why early closeout was chosen" in out
    assert "## What user decisions are needed" in out
    assert "## Waste and retro" in out


def test_goal_early_close_emit_stub_round_trips_the_floor_validator(tmp_path: Path) -> None:
    # Dogfood: the preflight's emit-stub for goal-early-close must produce a report
    # that PASSES the achieve early-close-report floor's own validator — so an author
    # starting from the surfaced stub cannot fail the complete flip on shape.
    text, code = preflight.emit_stub(ROOT, preflight.surface_for_type("goal-early-close"))
    assert code == 0
    spec = importlib.util.spec_from_file_location(
        "goal_artifact_early_close_report",
        ROOT / "skills/public/achieve/scripts/goal_artifact_early_close_report.py",
    )
    ecr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ecr)
    report = tmp_path / "early-close.md"
    report.write_text(text, encoding="utf-8")
    assert ecr.validate_report_shape(report) == []


# --- goal-activation-preflight-surface: the `Activation:` preamble line ---------


def test_extract_preamble_stops_at_first_h2() -> None:
    text = "# Title\n\nStatus: draft\nActivation: `/goal @x.md`\n\nintro para\n## Section\nbody\n"
    out = preflight._extract_preamble(text)
    assert "# Title" in out
    assert "Activation: `/goal @x.md`" in out
    assert "intro para" in out
    assert "## Section" not in out and "body" not in out
    # a template with no preamble (starts at an H2) reports the miss, never crashes.
    assert preflight._extract_preamble("## First\nbody\n") == "(template preamble not found)"


def test_goal_activation_surface_reads_activation_preamble() -> None:
    surface = preflight.surface_for_type("goal-activation")
    assert surface is not None
    assert surface.validator is None
    assert surface.scaffold is None
    assert surface.commit_boundary is False  # checked at activation-readiness, not a commit gate
    assert surface.template_preamble is not None  # preamble source, not a `## Heading` section
    out = preflight.describe(ROOT, surface, target_rel=None)
    # surfaces the preamble shape (the Activation line + Status/Created), not a section.
    assert "Activation: `/goal @" in out
    assert "Status:" in out
    # owner line names the REAL enforcer — the default check_goal_artifact.py check
    # (goal_lib.check_goal's Activation:-line requirement) — and explicitly rules out
    # --pursue-ready (which skips it) and the complete-flip default.
    assert "check_goal_artifact.py" in out
    assert "NOT `--pursue-ready`" in out
    assert "achieve closeout (check_goal_artifact.py at the complete flip)" not in out


def test_emit_stub_goal_activation_points_at_template_preamble() -> None:
    text, code = preflight.emit_stub(ROOT, preflight.surface_for_type("goal-activation"))
    assert code == 0
    assert "no scaffold script" in text
    assert "goal_artifact_template.md" in text


def test_goal_activation_surface_lives_in_the_real_goal_preamble() -> None:
    # The surfaced shape must match the live template preamble (single source), so
    # the author sees exactly what `check_goal_artifact.py` requires.
    template = (ROOT / "skills/public/achieve/scripts/goal_artifact_template.md").read_text(encoding="utf-8")
    assert "Activation: `/goal @{goal_rel}`" in template.split("## ", 1)[0]


def test_module_main_guard_executes(monkeypatch) -> None:
    # cover `sys.exit(main())` (the __main__ guard) in-process via runpy, not a
    # subprocess, so the dispatcher stays off the boundary-bypass ratchet.
    monkeypatch.setattr(sys, "argv", ["x", "--type", "critique"])
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(ROOT / "scripts" / "check_artifact_surface_preflight.py"), run_name="__main__")
    assert exc.value.code == 0


# --- closeout-draft + enriched goal-closeout author-time surfaces ---------------
# The authoring-preflight class extended to the GitHub-issue closeout-draft and the
# goal-closeout complete gate: the dispatcher surfaces each shape rendered LIVE from
# the owning validator's constants (the new `shape_command` source), never re-declared.


def _load_describe(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_closeout_draft_surface_is_author_time_shape_only() -> None:
    s = preflight.surface_for_type("closeout-draft")
    assert s is not None
    assert s.validator is None  # a verdict needs the full validate-closeout-draft command
    assert s.scaffold is None
    assert s.commit_boundary is False  # author-time shape only; the validator stays enforcement
    assert s.shape_command == ("skills/public/issue/scripts/describe_closeout_draft_shape.py",)
    out = preflight.describe(ROOT, s, target_rel=None)
    # the owner line names the real validator command, not the complete-flip default
    assert "validate-closeout-draft" in out
    assert "achieve closeout (check_goal_artifact.py at the complete flip)" not in out


def test_closeout_draft_describe_emits_the_named_required_fields() -> None:
    out = preflight.describe(ROOT, preflight.surface_for_type("closeout-draft"), target_rel=None)
    # the four fields the goal names + the carrier-body-source trap
    assert "resolution_critique" in out and "tool signal:" in out
    assert "COMMIT MESSAGE" in out and "direct-commit" in out
    assert "Closes #N" in out  # close keyword
    assert "Classification ledger fields" in out


def test_closeout_draft_shape_pins_live_verifier_constants() -> None:
    # drift guard: every enforced enum/field the verifier checks appears in the
    # surfaced shape, rendered from the live constants (never a stale hand copy).
    desc = _load_describe("skills/public/issue/scripts/describe_closeout_draft_shape.py", "dccs")
    shape = desc.required_shape()
    for value in (*desc._VERIFY.CLASSIFICATIONS, *desc._VERIFY.CARRIERS,
                  *desc._VERIFY.MANUAL_FALLBACK_REASONS, *desc._CRITIQUE.CRITIQUE_REQUIRED_CLASSIFICATIONS):
        assert value in shape, value
    for classification in desc._VERIFY.CLASSIFICATIONS:
        for field_id, _aliases in desc._BODY._classification_requirements(classification):
            assert field_id in shape or f"{field_id.title()}:" in shape, field_id


def test_closeout_draft_stub_body_satisfies_the_real_validator_helpers() -> None:
    # round-trip drift guard: a body built from the SURFACED headers passes the
    # validator's own ledger/keyword helpers for every classification, proving the
    # surfaced fields ARE the enforced ones (not a drifted copy).
    desc = _load_describe("skills/public/issue/scripts/describe_closeout_draft_shape.py", "dccs2")
    body = desc._BODY
    for classification in desc._VERIFY.CLASSIFICATIONS:
        lines = ["Closes #5"]
        for field_id, aliases in body._classification_requirements(classification):
            value = "a decision and proof" if field_id == "siblings" else "x"
            lines.append(f"{aliases[0].title()}: {value}")
        text = "\n".join(lines)
        assert body._missing_ledger_fields(text, classification) == [], classification
        assert body._missing_close_keywords(text, [5], "o/r") == [], classification


def test_closeout_draft_emit_stub_renders_a_starter_body() -> None:
    text, code = preflight.emit_stub(ROOT, preflight.surface_for_type("closeout-draft"))
    assert code == 0
    assert "Closes #N" in text
    assert "Critique #N:" in text


def test_goal_closeout_describe_now_surfaces_the_enforced_forms() -> None:
    # enriched: keeps the template block AND adds the enforced forms read live from
    # check_goal_artifact's constants (the four the goal names).
    out = preflight.describe(ROOT, preflight.surface_for_type("goal-closeout"), target_rel=None)
    assert "## Final Verification" in out  # template block still present (backward compat)
    assert all(r in out for r in ("host-blocked-subagent", "host-log-not-exposed", "evaluator-unavailable"))
    assert "goal slug" in out  # bare-path + goal-slug binding
    assert "Routing:" in out and "find-skills" in out  # Routing form
    assert "applied:" in out  # disposition form


def test_goal_closeout_shape_pins_live_skip_enum_and_optout_floors() -> None:
    desc = _load_describe("skills/public/achieve/scripts/describe_goal_closeout_shape.py", "dgcs")
    shape = desc.required_shape()
    for reason in desc._PRESCRIBED.ALLOWED_SKIP_REASONS:
        assert reason in shape, reason
    assert str(desc._PRESCRIBED.MIN_SKIP_LENGTH) in shape
    assert str(desc._DISPOSITION.MIN_OPTOUT_REASON) in shape
    # drift guard: the disposition-line forms are the LIVE summaries (not prose), so
    # the surfaced `Retro dispositions:` / `Structural follow-up:` forms cannot drift
    # from disposition_form.py's enforced sets. This pins that `Retro dispositions:`
    # uses VALID_FORM_SUMMARY (NOT the `repo-local guard:` destination form, which is
    # only valid on `Structural follow-up:`) — the form that would otherwise misdirect.
    assert desc._DISPOSITION_FORM.VALID_FORM_SUMMARY in shape
    assert desc._DISPOSITION_FORM.DESTINATION_FORM_SUMMARY in shape
    assert "repo-local guard" not in desc._DISPOSITION_FORM.VALID_FORM_SUMMARY  # the B1 invariant


def test_goal_closeout_emit_stub_combines_template_message_and_enforced_stub() -> None:
    text, code = preflight.emit_stub(ROOT, preflight.surface_for_type("goal-closeout"))
    assert code == 0
    assert "no scaffold script" in text  # template-seeded message (backward compat)
    assert "## Final Verification" in text and "Retro:" in text  # enforced-form starter


def test_goal_closeout_stub_round_trips_complete_gate_when_filled(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    slug = "closeout-stub-roundtrip"
    date = "2026-06-12"
    goal_rel = f"charness-artifacts/goals/{date}-{slug}.md"
    evidence_paths = {
        "retro": f"charness-artifacts/retro/{date}-{slug}.md",
        "host": f"charness-artifacts/retro/{date}-{slug}-host-log.md",
        "review": f"charness-artifacts/critique/{date}-{slug}-disposition-review.md",
    }
    for rel in evidence_paths.values():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{slug}\nNo actionable improvements were surfaced.\n", encoding="utf-8")

    emitted_stub, code = preflight.emit_stub(ROOT, preflight.surface_for_type("goal-closeout"))
    assert code == 0
    closeout_stub = (
        emitted_stub[emitted_stub.index("## Final Verification") :]
        .replace("charness-artifacts/retro/<date>-<goal-slug>.md", evidence_paths["retro"])
        .replace("charness-artifacts/retro/<date>-<goal-slug>-host-log.md", evidence_paths["host"])
        .replace(
            "charness-artifacts/critique/<date>-<goal-slug>-disposition-review.md",
            evidence_paths["review"],
        )
        .replace(
            "Retro dispositions: none — <>=30-char reason no surfaced improvement needs active disposition>",
            "Retro dispositions: none — the bound retro fixture records no actionable improvements, so no active disposition is needed",
        )
    )
    goal_path = tmp_path / goal_rel
    goal_path.parent.mkdir(parents=True, exist_ok=True)
    goal_path.write_text(
        f"""# Achieve Goal: Closeout Stub Roundtrip

Status: complete
Created: {date}
Activation: `/goal @{goal_rel}`

## Active Operating Frame

- Current slice: final closeout fixture.
- Next action: validate the filled goal-closeout stub.

## Goal

Prove the surfaced goal-closeout stub can be filled without reading validator grammar.

## Non-Goals

N/A — fixture-only goal.

## Boundaries

N/A — local fixture with no external side effects.

## User Acceptance

Run the goal checker and see it accept the completed fixture.

## Agent Verification Plan

Run the actual `check_goal_artifact.py` complete-state validator.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |

## Operator Decision Queue

none — synthetic closeout fixture has no operator-only decisions.

## Coordination Cues

Routing: n/a — synthetic closeout fixture recorded no implementation, debug, quality, or issue phase work.
Gather: n/a — synthetic closeout fixture used no external URL or private-source context.
Release: n/a — synthetic closeout fixture touched no release or install manifest surface.
Issue closeout: n/a — synthetic closeout fixture resolved no tracked GitHub issue.

## Slice Log

N/A — synthetic closeout round-trip fixture; no implementation slices.

## Context Sources

N/A — synthetic fixture.

## Interview Decisions

N/A — synthetic fixture.

## Plan Critique Findings

N/A — synthetic fixture.

## Off-Goal Findings

N/A — synthetic fixture.

{closeout_stub}
## User Verification Instructions

Run `check_goal_artifact.py` on the fixture.
""",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "check_goal_artifact.py",
            "--repo-root",
            str(tmp_path),
            "--goal-path",
            str(goal_path),
        ],
    )
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(ROOT / "skills/public/achieve/scripts/check_goal_artifact.py"), run_name="__main__")

    assert exc.value.code == 0, capsys.readouterr().out


def test_run_shape_command_reports_render_failure() -> None:
    bad = replace(
        preflight.surface_for_type("closeout-draft"),
        shape_command=("scripts/does_not_exist_shape.py",),
    )
    text, code = preflight._run_shape_command(ROOT, bad, stub=False)
    assert code == 1
    assert "could not render shape source" in text


def test_emit_stub_no_source_arm() -> None:
    # a (hypothetical) surface with no scaffold/template/shape_command reports the
    # no-stub-source arm rather than crashing — cover the defensive branch.
    bare = replace(
        preflight.surface_for_type("closeout-draft"),
        scaffold=None, template_section=None, template_preamble=None, shape_command=None,
    )
    text, code = preflight.emit_stub(ROOT, bare)
    assert code == 0
    assert "no stub source registered" in text


@pytest.mark.parametrize(
    "rel",
    [
        "skills/public/issue/scripts/describe_closeout_draft_shape.py",
        "skills/public/achieve/scripts/describe_goal_closeout_shape.py",
    ],
)
def test_describe_script_main_renders_shape_and_stub(rel: str, capsys) -> None:
    desc = _load_describe(rel, f"main_{Path(rel).stem}")
    assert desc.main([]) == 0
    shape_out = capsys.readouterr().out
    assert desc.main(["--stub"]) == 0
    stub_out = capsys.readouterr().out
    assert shape_out.strip() and stub_out.strip()
    assert shape_out != stub_out  # shape and stub are distinct surfaces


@pytest.mark.parametrize(
    "rel",
    [
        "skills/public/issue/scripts/describe_closeout_draft_shape.py",
        "skills/public/achieve/scripts/describe_goal_closeout_shape.py",
    ],
)
def test_describe_script_main_guard_executes(rel: str, monkeypatch) -> None:
    # cover `raise SystemExit(main())` (the __main__ guard) in-process via runpy.
    monkeypatch.setattr(sys, "argv", ["x"])
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(ROOT / rel), run_name="__main__")
    assert exc.value.code == 0


@pytest.mark.parametrize(
    "rel,loader,sibling",
    [
        ("skills/public/issue/scripts/describe_closeout_draft_shape.py", "_load_local", "issue_verify_closeout_body"),
        ("skills/public/achieve/scripts/describe_goal_closeout_shape.py", "_load_sibling", "goal_artifact_disposition_grammar"),
    ],
)
def test_describe_sibling_loader_fails_closed_when_spec_missing(rel, loader, sibling, monkeypatch) -> None:
    # fail-closed: the sibling loader raises ImportError when the spec cannot be
    # built (mirrors the repo's established loader-coverage pattern).
    desc = _load_describe(rel, f"loaderfail_{Path(rel).stem}")
    monkeypatch.setattr(importlib.util, "spec_from_file_location", lambda *a, **k: None)
    with pytest.raises(ImportError):
        getattr(desc, loader)(sibling)


def test_goal_closeout_prescribed_lib_loader_fails_closed(monkeypatch) -> None:
    # covers BOTH the in-loop spec-None `continue` and the final not-found raise of
    # the ancestor-walk loader for check_prescribed_skill_executed_lib.
    desc = _load_describe("skills/public/achieve/scripts/describe_goal_closeout_shape.py", "prescribedfail")
    monkeypatch.setattr(importlib.util, "spec_from_file_location", lambda *a, **k: None)
    with pytest.raises(ImportError, match="check_prescribed_skill_executed_lib"):
        desc._load_repo_script("check_prescribed_skill_executed_lib")
