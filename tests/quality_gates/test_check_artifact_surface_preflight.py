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
