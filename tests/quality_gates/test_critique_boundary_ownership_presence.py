from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

import pytest

from .support import ROOT, run_script

# The boundary-ownership typed-presence floor (#408/#414/#416): every critique
# artifact records a `## Boundary Ownership` section with a typed `Verdict:` so a
# producer/consumer ownership decision cannot be silently skipped — the
# symptom-caught-in-the-wrong-layer trap #408 took, where a passing unit test at
# the nearest surface looked like a finished fix. Presence + typed-value only;
# correctness (is the named owner right?) stays reviewer judgment, the same
# boundary as the fresh-eye floor and the D34 announcement presence posture.
# Enforced for artifacts dated on/after `BOUNDARY_OWNERSHIP_RULE_DATE`
# (2026-07-06); a dated artifact on/before the landing day (2026-07-05) is
# grandfathered — same `RULE_DATE = landing_day + 1` shape as the fresh-eye
# floor. Every post-cutoff artifact carries a valid `Fresh-eye satisfaction:`
# line here so the fresh-eye floor (checked first) passes and these cases
# isolate the boundary floor.

# `nested-delegated` passes the fresh-eye floor WITHOUT triggering the
# Reviewer-Tier-Evidence requirement that `parent-delegated` does under `--paths`,
# so these cases isolate the boundary floor cleanly.
_FRESH_EYE_OK = "Fresh-eye satisfaction: nested-delegated; recursive delegation actually ran."


def _write(repo: Path, name: str, *body: str) -> str:
    artifact = repo / "charness-artifacts" / "critique" / name
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text("\n".join(["# Demo Critique", "", *body, ""]), encoding="utf-8")
    return f"charness-artifacts/critique/{name}"


def _run(repo: Path, relpath: str, *extra: str) -> object:
    return run_script(
        "scripts/validate_critique_artifacts.py",
        "--repo-root",
        str(repo),
        "--paths",
        relpath,
        *extra,
    )


# The post-cutoff presence/typed-value floor, table-driven. A typed prefix is not
# enough if the remainder is still an unedited TODO — a stub silently claiming a
# disposition (the loophole the default scaffold Verdict line avoids); a missing
# section and an untyped verdict reject the same way.
@pytest.mark.parametrize(
    "body, errors",
    [
        ((_FRESH_EYE_OK,), ("no `## Boundary Ownership` section", "single-surface", "escalated-to-issue-spec")),
        (
            (_FRESH_EYE_OK, "", "## Boundary Ownership", "", "- Verdict: reviewed carefully, seems fine."),
            ("does not open with one of", "Boundary Ownership"),
        ),
        (
            (_FRESH_EYE_OK, "", "## Boundary Ownership", "", "- Verdict: single-surface (TODO confirm no producer-owned state is touched)."),
            ("unedited `todo`",),
        ),
    ],
)
def test_boundary_validator_rejects_post_cutoff(tmp_path: Path, body: tuple, errors: tuple) -> None:
    result = _run(tmp_path / "repo", _write(tmp_path / "repo", "2026-07-06-demo.md", *body))
    assert result.returncode == 1
    for token in errors:
        assert token in result.stderr


@pytest.mark.parametrize(
    "body",
    [
        (
            _FRESH_EYE_OK, "", "## Boundary Ownership", "",
            "- Producer: the request handler.", "- Consumer: the renderer.",
            "- Owning surface: request-layer.", "- Verdict: single-surface",
        ),
        (_FRESH_EYE_OK, "", "## Boundary Ownership", "", "- Verdict: `moved-to-owner`; relocated the fact to its producer plus generic rendering."),
    ],
)
def test_boundary_validator_accepts_post_cutoff(tmp_path: Path, body: tuple) -> None:
    result = _run(tmp_path / "repo", _write(tmp_path / "repo", "2026-07-06-demo.md", *body))
    assert result.returncode == 0, result.stderr


def test_boundary_validator_grandfathers_missing_section_on_landing_day(tmp_path: Path) -> None:
    """Dated on the floor's landing day (2026-07-05): the boundary floor is
    grandfathered even though the section is absent. The fresh-eye line is valid
    so the (already-enforced) fresh-eye floor is not what passes this case."""
    repo = tmp_path / "repo"
    relpath = _write(repo, "2026-07-05-demo.md", _FRESH_EYE_OK)

    result = _run(repo, relpath)

    assert result.returncode == 0, result.stderr


def _write_adapter_with_globs(repo: Path, *globs: str) -> None:
    adapter = repo / ".agents" / "critique-adapter.yaml"
    adapter.parent.mkdir(parents=True, exist_ok=True)
    body = "version: 1\nrepo: demo\n" + "boundary_cross_surface_globs:\n" + "".join(
        f'  - "{g}"\n' for g in globs
    )
    adapter.write_text(body, encoding="utf-8")


def _write_with_verdict(repo: Path, name: str, verdict: str) -> str:
    return _write(
        repo,
        name,
        _FRESH_EYE_OK,
        "",
        "## Boundary Ownership",
        "",
        f"- Verdict: {verdict}",
    )


def test_probe_rejects_single_surface_on_cross_surface_hit(tmp_path: Path) -> None:
    """The #408 objective override: a changed path matching the repo cross-surface
    probe rejects a bare `single-surface` verdict even though the presence floor
    alone would accept it."""
    repo = tmp_path / "repo"
    _write_adapter_with_globs(repo, "scripts/*.py")
    relpath = _write_with_verdict(repo, "2026-07-06-demo.md", "single-surface")

    result = _run(repo, relpath, "--changed-path", "scripts/reducer.py")

    assert result.returncode == 1
    assert "cross-surface probe" in result.stderr
    assert "single-surface" in result.stderr and "rejected" in result.stderr


def test_probe_accepts_moved_to_owner_on_cross_surface_hit(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_adapter_with_globs(repo, "scripts/*.py")
    relpath = _write_with_verdict(repo, "2026-07-06-demo.md", "moved-to-owner")

    result = _run(repo, relpath, "--changed-path", "scripts/reducer.py")

    assert result.returncode == 0, result.stderr


def test_probe_accepts_single_surface_without_hit(tmp_path: Path) -> None:
    """No probe match -> `single-surface` stays acceptable (the floor is presence
    only when the objective override does not fire)."""
    repo = tmp_path / "repo"
    _write_adapter_with_globs(repo, "scripts/*.py")
    relpath = _write_with_verdict(repo, "2026-07-06-demo.md", "single-surface")

    result = _run(repo, relpath, "--changed-path", "docs/readme.md")

    assert result.returncode == 0, result.stderr


def test_boundary_scaffold_default_stub_fails_validation_post_cutoff(tmp_path: Path) -> None:
    """The scaffold's own unedited `## Boundary Ownership` Verdict stub must NOT
    satisfy the boundary floor once dated post-cutoff — defense-in-depth against
    a future change pre-filling a real verdict (the same loophole the fresh-eye
    stub test guards). `--report-all` surfaces both floors so the boundary
    message is asserted even though the unedited fresh-eye stub also fails."""
    import sys

    sys.path.insert(0, str(ROOT / "skills" / "public" / "critique" / "scripts"))
    import scaffold_critique_artifact as scaffold

    template = scaffold.render_template(title="Critique Review", date_text="2026-07-06")
    repo = tmp_path / "repo"
    artifact = repo / "charness-artifacts" / "critique" / "2026-07-06-critique-review.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(template, encoding="utf-8")

    result = _run(repo, "charness-artifacts/critique/2026-07-06-critique-review.md", "--report-all")

    assert result.returncode == 1
    assert "Boundary Ownership" in result.stderr
    assert "single-surface" in result.stderr


# --- impl stop-gate escalation hook, in-process (AC7); reuses this file's
# --- single _write_adapter_with_globs fixture writer.


def _load_hook():
    hook_dir = ROOT / "skills" / "public" / "impl" / "scripts"
    if str(hook_dir) not in sys.path:
        sys.path.insert(0, str(hook_dir))
    import check_boundary_escalation

    return check_boundary_escalation


def test_hook_triggers_on_cross_surface_change(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_adapter_with_globs(repo, "scripts/*.py")

    payload = _load_hook().build_payload(repo, ["scripts/reducer.py"], None)
    assert payload["triggered"] is True
    assert "escalate" in payload["reason"]


def test_hook_silent_without_probe_config(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_adapter_with_globs(repo)  # no globs -> empty probe

    payload = _load_hook().build_payload(repo, ["scripts/reducer.py"], None)
    assert payload["triggered"] is False


def test_hook_no_hit_on_unrelated_change(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_adapter_with_globs(repo, "scripts/*.py")

    payload = _load_hook().build_payload(repo, ["docs/readme.md"], None)
    assert payload["triggered"] is False


# --- impl stop-gate escalation hook CLI: bootstrap shim, parse_args, main (#421)


def test_hook_shim_not_found_raises_import_error(tmp_path: Path, monkeypatch) -> None:
    """Cover check_boundary_escalation._load_skill_runtime_bootstrap()'s "not
    found" raise (mirrors the scaffold family's forcing technique in
    tests/test_scaffold_inprocess_coverage.py): pointing __file__ at an isolated
    tree with no ancestor skill_runtime_bootstrap.py forces the ancestor walk to
    miss, since the real repo always finds one."""
    hook = _load_hook()
    isolated = tmp_path / "deep" / "nest" / "check_boundary_escalation.py"
    isolated.parent.mkdir(parents=True)
    monkeypatch.setattr(hook, "__file__", str(isolated))
    with pytest.raises(ImportError, match="skill_runtime_bootstrap.py not found"):
        hook._load_skill_runtime_bootstrap()


def test_hook_parse_args_reads_flags(monkeypatch) -> None:
    hook = _load_hook()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "check_boundary_escalation.py",
            "--changed-path",
            "a.py",
            "b.py",
            "--changed-ref",
            "base..HEAD",
            "--json",
        ],
    )
    args = hook.parse_args()
    assert args.changed_path == ["a.py", "b.py"]
    assert args.changed_ref == "base..HEAD"
    assert args.json is True
    assert args.repo_root == hook.REPO_ROOT


def test_hook_parse_args_defaults_to_no_flags(monkeypatch) -> None:
    hook = _load_hook()
    monkeypatch.setattr(sys, "argv", ["check_boundary_escalation.py"])
    args = hook.parse_args()
    assert args.changed_path is None
    assert args.changed_ref is None
    assert args.json is False


def test_hook_main_json_output(monkeypatch, capsys) -> None:
    hook = _load_hook()
    fake_payload = {
        "triggered": True,
        "changed_paths": ["scripts/reducer.py"],
        "probe": {"globs": ["scripts/*.py"], "surfaces": []},
        "reason": "escalate this slice to a standalone critique",
    }
    monkeypatch.setattr(hook, "build_payload", lambda repo_root, changed_path, changed_ref: fake_payload)
    monkeypatch.setattr(sys, "argv", ["check_boundary_escalation.py", "--json"])
    assert hook.main() == 0
    assert json.loads(capsys.readouterr().out) == fake_payload


def test_hook_main_plain_output(monkeypatch, capsys) -> None:
    hook = _load_hook()
    fake_payload = {
        "triggered": True,
        "changed_paths": ["scripts/reducer.py"],
        "probe": {"globs": ["scripts/*.py"], "surfaces": []},
        "reason": "escalate this slice to a standalone critique",
    }
    monkeypatch.setattr(hook, "build_payload", lambda repo_root, changed_path, changed_ref: fake_payload)
    monkeypatch.setattr(sys, "argv", ["check_boundary_escalation.py"])
    assert hook.main() == 0
    out = capsys.readouterr().out
    assert out == "escalate this slice to a standalone critique\ntriggered: true\n"


def test_hook_module_main_guard_executes(monkeypatch, capsys) -> None:
    """Cover `if __name__ == "__main__": raise SystemExit(main())` in-process via
    runpy (mirrors check_artifact_surface_preflight's test_module_main_guard_executes),
    not a subprocess, so the script stays off the boundary-bypass ratchet.
    `--changed-path docs/x.md` bypasses git and matches none of the real repo's
    configured boundary_cross_surface_globs (scripts/*_lib.py, skills/shared/**),
    so `triggered: false` is deterministic regardless of real working-tree state.
    Dormant coupling (fresh-eye 2026-07-08): this reads the LIVE critique
    adapter; `boundary_cross_surface_surfaces` is empty today, but the
    `repo-markdown` surface declares `docs/*.md`, so adding it to the probe
    surfaces would flip this to `triggered: true` — if that happens, switch
    this test to an isolated tmp-repo adapter rather than another path."""
    monkeypatch.setattr(sys, "argv", ["check_boundary_escalation.py", "--changed-path", "docs/x.md"])
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(
            str(ROOT / "skills" / "public" / "impl" / "scripts" / "check_boundary_escalation.py"),
            run_name="__main__",
        )
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "no cross-surface probe hit" in out
    assert "triggered: false" in out


# --- charness dogfoods its own probe (DBD-4) --------------------------------
# These guard the self-adoption against silent regression: emptying the globs or
# dropping --changed-ref would turn the #408 5b tooth back off in charness CI
# (fixture-proven but not live), which is exactly the residual DBD-4 closed.


def test_charness_dogfoods_its_own_cross_surface_probe() -> None:
    from scripts import boundary_probe_lib, critique_adapter_lib

    probe = boundary_probe_lib.probe_config_from_adapter(
        critique_adapter_lib.load_adapter(ROOT)["data"]
    )
    assert probe["globs"], "charness must configure its own boundary_cross_surface_globs (DBD-4 dogfood)"
    # A change to a root shared lib must hit; a doc/test change must not.
    assert boundary_probe_lib.cross_surface_hit(ROOT, ["scripts/surfaces_lib.py"], globs=probe["globs"])
    assert not boundary_probe_lib.cross_surface_hit(ROOT, ["docs/handoff.md"], globs=probe["globs"])
    assert not boundary_probe_lib.cross_surface_hit(ROOT, ["tests/test_x.py"], globs=probe["globs"])


def test_run_quality_wires_changed_ref_range_for_cross_surface_probe() -> None:
    run_quality = (ROOT / "scripts" / "run-quality.sh").read_text(encoding="utf-8")
    critique_line = next(
        line for line in run_quality.splitlines() if "validate-critique-artifacts" in line
    )
    assert "--changed-ref" in critique_line, (
        "run-quality.sh must pass --changed-ref to validate-critique-artifacts so the "
        "cross-surface 5b tooth fires in charness CI, not just unit fixtures (DBD-4)"
    )
    # A BARE ref resolves to that one commit's diff-tree (the fork point), not the
    # unpushed range — silently mis-targeting the tooth. Require the RANGE form.
    assert "..HEAD" in critique_line or "..HEAD" in run_quality, (
        "the --changed-ref value must be a range (base..HEAD); a bare sha resolves to "
        "the fork-point commit's own diff, not the change under review (DBD-4 wiring bug)"
    )


def test_changed_ref_range_fires_tooth_end_to_end(tmp_path: Path) -> None:
    # End-to-end proof of the run-quality wiring: a `base..HEAD` range whose
    # committed change touches a `scripts/*_lib.py` path rejects a bare
    # `single-surface` verdict — exactly the CI path. Fails if the wiring regresses
    # to a bare sha (which resolves the fork-point's own diff, not the range).
    import subprocess

    repo = tmp_path / "repo"
    _write_adapter_with_globs(repo, "scripts/*_lib.py")
    (repo / "scripts").mkdir(exist_ok=True)
    (repo / "scripts" / "keep.py").write_text("x = 1\n", encoding="utf-8")

    def g(*a: str) -> str:
        return subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True, text=True).stdout

    for cmd in (["init"], ["config", "user.email", "t@t"], ["config", "user.name", "t"], ["add", "-A"], ["commit", "-qm", "base"]):
        g(*cmd)
    base = g("rev-parse", "HEAD").strip()

    (repo / "scripts" / "foo_lib.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    relpath = _write_with_verdict(repo, "2026-07-06-demo.md", "single-surface")
    g("add", "-A")
    g("commit", "-qm", "change")

    result = _run(repo, relpath, "--changed-ref", f"{base}..HEAD")
    assert result.returncode == 1
    assert "cross-surface probe" in result.stderr
