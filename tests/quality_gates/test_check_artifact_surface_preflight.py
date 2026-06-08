from __future__ import annotations

import sys

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
