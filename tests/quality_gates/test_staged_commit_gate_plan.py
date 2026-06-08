from __future__ import annotations

import json
import os
import subprocess
from collections.abc import Callable
from pathlib import Path

from scripts.staged_commit_gate_plan import (
    FAST_SURFACE_VERIFY_COMMANDS,
    STRUCTURAL_SWEEP_LABELS,
    GateCommand,
    block_on_structural_sweep,
    collect_staged_paths,
    fast_surface_verify_gates,
    run_predict_commit,
    staged_commit_gate_plan,
    structural_sweep_gates,
)
from scripts.surfaces_lib import load_surfaces, match_surfaces

from .support import ROOT, run_script


def _surface_verify_commands_for(paths: list[str]) -> set[str]:
    manifest = load_surfaces(ROOT, required=False)
    assert manifest is not None
    return set(match_surfaces(manifest, paths)["verify_commands"])


def _labels(paths: list[str]) -> list[str]:
    return [command.label for command in staged_commit_gate_plan(ROOT, paths, ruff_path="")]


def _write_executable(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)


def _git_init_and_stage(repo: Path, path: str, body: str) -> None:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", path], cwd=repo, check=True, capture_output=True, text=True)


def _write_predict_commit_stubs(repo: Path, *, length_fails: bool = False, attention_fails: bool = False) -> dict[str, str]:
    scripts = repo / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    length_exit = "1" if length_fails else "0"
    attention_exit = "1" if attention_fails else "0"
    _write_executable(
        scripts / "check_python_lengths.py",
        f"#!/usr/bin/env python3\nprint('length gate')\nraise SystemExit({length_exit})\n",
    )
    _write_executable(
        scripts / "check_staged_reversion.py",
        "#!/usr/bin/env python3\nprint('staged reversion gate')\n",
    )
    _write_executable(
        scripts / "validate_attention_state_visibility.py",
        f"#!/usr/bin/env python3\nprint('attention gate')\nraise SystemExit({attention_exit})\n",
    )
    _write_executable(
        scripts / "check_staged_mirror_drift.py",
        "#!/usr/bin/env python3\nprint('mirror gate')\n",
    )
    fake_bin = repo / "bin"
    fake_bin.mkdir()
    _write_executable(fake_bin / "ruff", "#!/usr/bin/env bash\necho ruff gate\n")
    return {**os.environ, "PATH": f"{fake_bin}:{os.environ.get('PATH', '')}"}


def test_staged_commit_plan_includes_commit_only_python_gates() -> None:
    labels = _labels(["scripts/new_helper.py"])

    assert "check-staged-reversion" in labels
    assert "py_compile (staged)" in labels
    assert "check-python-lengths (staged)" in labels
    assert "validate-attention-state-visibility" in labels
    assert "staged-plugin-mirror-drift" in labels


def test_staged_commit_plan_gates_changed_skill_md_core_headroom() -> None:
    # #319: a changed public/support SKILL.md pulls the commit-boundary core
    # headroom ratchet into the plan, scoped to exactly that path.
    plan = staged_commit_gate_plan(ROOT, ["skills/public/demo/SKILL.md"], ruff_path="")
    gate = next((c for c in plan if c.label == "check-skill-core-headroom (staged)"), None)
    assert gate is not None
    assert gate.argv == (
        "python3",
        "scripts/check_skill_surface_preflight.py",
        "--repo-root",
        str(ROOT),
        "--changed-skill-md",
        "skills/public/demo/SKILL.md",
    )


def test_staged_commit_plan_skips_core_headroom_without_changed_skill_md() -> None:
    # A reference edit or a non-skill change must not pull the SKILL.md core gate.
    for paths in (["skills/public/demo/references/note.md"], ["scripts/new_helper.py"], ["README.md"]):
        assert "check-skill-core-headroom (staged)" not in _labels(paths)


def test_staged_commit_plan_gates_changed_artifact_shape() -> None:
    # the hand-authored artifact family pulls the blocking commit-boundary shape
    # gate, scoped to the changed charness-artifacts/** paths.
    plan = staged_commit_gate_plan(ROOT, ["charness-artifacts/critique/x.md"], ruff_path="")
    gate = next((c for c in plan if c.label == "check-artifact-shape (staged)"), None)
    assert gate is not None
    assert gate.argv == (
        "python3",
        "scripts/check_artifact_surface_preflight.py",
        "--repo-root",
        str(ROOT),
        "--changed-artifacts",
        "charness-artifacts/critique/x.md",
    )
    # and it is a blocking structural-sweep member (relocated, not advisory).
    assert "check-artifact-shape (staged)" in STRUCTURAL_SWEEP_LABELS
    assert "check-artifact-shape (staged)" in {g.label for g in structural_sweep_gates(ROOT, ["charness-artifacts/critique/x.md"])}


def test_staged_commit_plan_skips_artifact_shape_for_non_artifact_md() -> None:
    # docs/*.md is not an artifact surface, EXCEPT the handoff default docs/handoff.md.
    for paths in (["docs/x.md"], ["README.md"], ["scripts/x.py"], ["charness-artifacts/spec/x.md"]):
        assert "check-artifact-shape (staged)" not in _labels(paths)
    # in-family surfaces (prefix + adapter-scoped) pull the blocking shape gate.
    for paths in (
        ["charness-artifacts/retro/2026-06-08-x.md"],
        ["charness-artifacts/debug/2026-06-08-x.md"],
        ["charness-artifacts/quality/2026-06-08-x.md"],
        ["docs/handoff.md"],
    ):
        assert "check-artifact-shape (staged)" in _labels(paths)


def test_gate_command_serializes_to_dict() -> None:
    assert GateCommand("demo", ("python3", "demo.py")).as_dict() == {
        "label": "demo",
        "argv": ["python3", "demo.py"],
    }


def test_collect_staged_paths_reports_git_error(monkeypatch) -> None:
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args=[], returncode=1, stderr="no index\n"),
    )

    try:
        collect_staged_paths(ROOT)
    except RuntimeError as exc:
        assert str(exc) == "no index"
    else:
        raise AssertionError("expected RuntimeError")


def test_staged_commit_plan_covers_domain_and_markdown_triggers() -> None:
    labels = _labels(
        [
            "skills/public/demo/SKILL.md",
            "profiles/default/profile.yaml",
            ".agents/surfaces.json",
            "presets/default.yaml",
            "integrations/tool.json",
            "docs/usage.md",
        ]
    )

    assert "validate-skills" in labels
    assert "run-evals" in labels
    assert "validate-profiles" in labels
    assert "validate-adapters" in labels
    assert "validate-presets" in labels
    assert "validate-integrations" in labels
    assert "staged-plugin-mirror-drift" in labels
    assert "check-doc-links" in labels
    assert "check-markdown" in labels


def test_run_slice_closeout_predict_commit_uses_shared_plan() -> None:
    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(ROOT),
        "--predict-commit",
        "--paths",
        "scripts/new_helper.py",
        "--plan-only",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    planned_labels = [command["label"] for command in payload["planned_commands"]]
    assert planned_labels == [command.label for command in staged_commit_gate_plan(ROOT, ["scripts/new_helper.py"])]


def test_staged_commit_gate_plan_cli_json_and_text() -> None:
    json_result = run_script(
        "scripts/staged_commit_gate_plan.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "README.md",
        "--json",
    )
    assert json_result.returncode == 0, json_result.stderr
    assert [item["label"] for item in json.loads(json_result.stdout)] == [
        "check-staged-reversion",
        "staged-plugin-mirror-drift",
        "check-doc-links",
        "check-markdown",
    ]

    text_result = run_script(
        "scripts/staged_commit_gate_plan.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "scripts/new_helper.py",
        "--no-ruff",
    )
    assert text_result.returncode == 0, text_result.stderr
    assert "check-python-lengths (staged)" in text_result.stdout
    assert "ruff (staged)" not in text_result.stdout


def _payload_sink(payload: dict[str, object], *, as_json: bool) -> int:
    assert as_json is True
    assert payload["status"] in {"planned", "failed", "completed"}
    return 0 if payload["status"] != "failed" else 1


def _runner(returncode: int, stdout: str = "", stderr: str = "") -> Callable[[Path, str, str], dict[str, object]]:
    def run_command(repo_root: Path, command: str, phase: str) -> dict[str, object]:
        return {"phase": phase, "command": command, "returncode": returncode, "stdout": stdout, "stderr": stderr}

    return run_command


def test_run_predict_commit_non_json_plan_empty_fail_and_success(capsys) -> None:
    assert run_predict_commit(ROOT, paths=[], as_json=False, plan_only=True, run_command=_runner(0), emit_payload=_payload_sink) == 0
    assert run_predict_commit(
        ROOT,
        paths=["README.md"],
        as_json=False,
        plan_only=True,
        run_command=_runner(0),
        emit_payload=_payload_sink,
    ) == 0
    assert "charness pre-commit: check-doc-links" in capsys.readouterr().out
    assert run_predict_commit(ROOT, paths=[], as_json=False, plan_only=False, run_command=_runner(0), emit_payload=_payload_sink) == 0

    failure_rc = run_predict_commit(
        ROOT,
        paths=["README.md"],
        as_json=False,
        plan_only=False,
        run_command=_runner(7, "bad stdout\n", "bad stderr\n"),
        emit_payload=_payload_sink,
    )
    captured = capsys.readouterr()
    assert failure_rc == 1
    assert "bad stdout" in captured.out
    assert "bad stderr" in captured.err

    success_rc = run_predict_commit(
        ROOT,
        paths=["README.md"],
        as_json=False,
        plan_only=False,
        run_command=_runner(0),
        emit_payload=_payload_sink,
    )
    assert success_rc == 0
    assert "charness pre-commit: ok" in capsys.readouterr().out


def test_run_predict_commit_surfaces_advisory_provider_lines(capsys) -> None:
    # #2a: advisory providers emit exit-0 informational lines that never change the
    # return code; they appear in text output and carry into the json payload.
    def provider(repo_root: Path, selected_paths: list[str]) -> list[str]:
        return ["ADVISORY: example nudge", "- charness-artifacts/debug/x.md"]

    rc = run_predict_commit(
        ROOT,
        paths=["README.md"],
        as_json=False,
        plan_only=False,
        run_command=_runner(0),
        emit_payload=_payload_sink,
        advisory_provider=provider,
    )
    out = capsys.readouterr().out
    assert rc == 0
    assert "ADVISORY: example nudge" in out
    assert "- charness-artifacts/debug/x.md" in out

    captured: list[dict[str, object]] = []

    def capture_sink(payload: dict[str, object], *, as_json: bool) -> int:
        captured.append(payload)
        return 0

    run_predict_commit(
        ROOT,
        paths=["README.md"],
        as_json=True,
        plan_only=False,
        run_command=_runner(0),
        emit_payload=capture_sink,
        advisory_provider=provider,
    )
    assert captured[-1]["advisories"] == ["ADVISORY: example nudge", "- charness-artifacts/debug/x.md"]


def test_predict_commit_rejects_length_violating_staged_python(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init_and_stage(repo, "scripts/too_long.py", "print('valid')\n")
    env = _write_predict_commit_stubs(repo, length_fails=True)

    result = run_script("scripts/run_slice_closeout.py", "--repo-root", str(repo), "--predict-commit", "--json", env=env)

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["status"] == "failed"
    assert payload["executed_commands"][-1]["command"].startswith("python3 scripts/check_python_lengths.py")


def test_predict_commit_rejects_attention_violating_staged_python(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init_and_stage(repo, "scripts/bad_attention.py", "print('valid')\n")
    env = _write_predict_commit_stubs(repo, attention_fails=True)

    result = run_script("scripts/run_slice_closeout.py", "--repo-root", str(repo), "--predict-commit", "--json", env=env)

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["status"] == "failed"
    assert payload["executed_commands"][-1]["command"].startswith("python3 scripts/validate_attention_state_visibility.py")


def test_predict_commit_accepts_clean_staged_python(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init_and_stage(repo, "scripts/clean.py", "print('valid')\n")
    env = _write_predict_commit_stubs(repo)

    result = run_script("scripts/run_slice_closeout.py", "--repo-root", str(repo), "--predict-commit", "--json", env=env)

    payload = json.loads(result.stdout)
    assert result.returncode == 0, result.stderr
    assert payload["status"] == "completed"
    assert [step["returncode"] for step in payload["executed_commands"]] == [0, 0, 0, 0, 0, 0]


def test_skill_packages_surface_runs_fast_ergonomics_checker() -> None:
    # #314 acceptance (1): the fast skill-ergonomics checker must run in the
    # skill-packages surface verify_commands so portable-package issue anchors,
    # dated incidents, and host-surface references fail at the commit boundary,
    # not only at the broad/bundle quality gate.
    surfaces = json.loads((ROOT / ".agents" / "surfaces.json").read_text(encoding="utf-8"))
    skill_packages = next(s for s in surfaces["surfaces"] if s["surface_id"] == "skill-packages")
    assert (
        "python3 scripts/validate_skill_ergonomics.py --repo-root ." in skill_packages["verify_commands"]
    ), skill_packages["verify_commands"]


def test_repo_python_surface_runs_fast_boundary_bypass_ratchet_before_broad_pytest() -> None:
    # #314 acceptance (1): the fast boundary-bypass ratchet must run in the
    # repo-python surface and precede the broad pytest so a redundant boundary-
    # spawning test fails at the commit boundary, not 172s into the broad gate.
    surfaces = json.loads((ROOT / ".agents" / "surfaces.json").read_text(encoding="utf-8"))
    repo_python = next(s for s in surfaces["surfaces"] if s["surface_id"] == "repo-python")
    verify = repo_python["verify_commands"]
    ratchet_idx = next(
        (i for i, cmd in enumerate(verify) if "check_boundary_bypass_ratchet.py" in cmd), None
    )
    broad_idx = next(
        (i for i, cmd in enumerate(verify) if cmd.startswith("pytest") and "tests/quality_gates" in cmd),
        None,
    )
    assert ratchet_idx is not None, verify
    assert broad_idx is not None, verify
    assert ratchet_idx < broad_idx, verify


def test_fast_surface_verify_allowlist_keys_exist_in_some_surface() -> None:
    # #314 acceptance (2/3): every reconciliation allowlist key must still appear
    # in some surface verify_commands. If surfaces.json renames or drops a fast
    # checker without updating FAST_SURFACE_VERIFY_COMMANDS (or vice versa), the
    # two commit-boundary paths would silently disagree -- pin it so drift fails.
    surfaces = json.loads((ROOT / ".agents" / "surfaces.json").read_text(encoding="utf-8"))
    all_verify = {cmd for s in surfaces["surfaces"] for cmd in s["verify_commands"]}
    for command in FAST_SURFACE_VERIFY_COMMANDS:
        assert command in all_verify, f"{command!r} not found in any surface verify_commands"


def test_precommit_plan_agrees_with_aggregate_fast_subset_for_skill_change() -> None:
    # #314 acceptance (2/3): when a touched surface lists a fast checker in its
    # verify_commands (consumed by the run_slice_closeout aggregate), the literal
    # git pre-commit plan must run that SAME checker. "Passes the aggregate" and
    # "passes pre-commit" become one guarantee for the fast subset.
    paths = ["skills/public/critique/SKILL.md"]
    surface_verify = _surface_verify_commands_for(paths)
    expected_fast = {
        command for command in FAST_SURFACE_VERIFY_COMMANDS if command in surface_verify
    }
    assert "python3 scripts/validate_skill_ergonomics.py --repo-root ." in expected_fast

    precommit_labels = {command.label for command in staged_commit_gate_plan(ROOT, paths, ruff_path="")}
    for command, label in FAST_SURFACE_VERIFY_COMMANDS.items():
        if command in expected_fast:
            assert label in precommit_labels, (label, precommit_labels)


def test_precommit_plan_agrees_with_aggregate_fast_subset_for_test_change() -> None:
    # #314: a changed test file routes to the repo-python surface, whose
    # verify_commands now include the boundary-bypass ratchet; the pre-commit
    # plan must run the same ratchet.
    paths = ["tests/quality_gates/test_example.py"]
    surface_verify = _surface_verify_commands_for(paths)
    assert "python3 scripts/check_boundary_bypass_ratchet.py --repo-root ." in surface_verify

    gates = fast_surface_verify_gates(ROOT, paths)
    labels = {gate.label for gate in gates}
    assert "check-boundary-bypass-ratchet" in labels
    argv = next(gate.argv for gate in gates if gate.label == "check-boundary-bypass-ratchet")
    assert argv == ("python3", "scripts/check_boundary_bypass_ratchet.py", "--repo-root", ".")


def test_fast_surface_verify_gates_degrade_without_surfaces_manifest(tmp_path: Path) -> None:
    # #314: tmp repos with no surfaces.json must not gain spurious gates; the
    # reconciliation degrades cleanly so the existing pre-commit fixtures hold.
    assert fast_surface_verify_gates(tmp_path, ["skills/public/critique/SKILL.md"]) == []
    assert fast_surface_verify_gates(ROOT, []) == []


# --- #332: the cheap structural sweep must run first in the full closeout ------


def _sweep_sink(payload: dict[str, object], *, as_json: bool, stderr_message: str | None = None) -> int:
    return 0 if payload["status"] not in {"blocked", "failed"} else 1


def test_structural_sweep_gates_select_only_the_named_subset() -> None:
    # #332: the sweep is exactly the presence/structural gates, drawn FROM
    # staged_commit_gate_plan (single source of truth) -- never ruff/lengths/
    # py_compile/skills/run-evals (those stay in verify, not the cheap sweep).
    paths = ["scripts/x.py", "skills/public/demo/scripts/y.py", "skills/public/demo/SKILL.md"]
    sweep_labels = {gate.label for gate in structural_sweep_gates(ROOT, paths)}
    assert sweep_labels <= STRUCTURAL_SWEEP_LABELS
    plan_labels = {gate.label for gate in staged_commit_gate_plan(ROOT, paths, ruff_path="")}
    assert sweep_labels <= plan_labels  # the sweep is a strict subset of the plan
    for excluded in ("ruff (staged)", "py_compile (staged)", "check-python-lengths (staged)", "run-evals"):
        assert excluded not in sweep_labels


def test_structural_sweep_covers_each_329_class_file_type() -> None:
    # #332 B2: coverage is per-gate, not uniform. attention-state fires on a
    # scripts/*.py; ergonomics on a skill-package file; the preflight on SKILL.md.
    assert "validate-attention-state-visibility" in {g.label for g in structural_sweep_gates(ROOT, ["scripts/x.py"])}
    assert "validate-skill-ergonomics" in {g.label for g in structural_sweep_gates(ROOT, ["skills/public/demo/scripts/y.py"])}
    assert "check-skill-core-headroom (staged)" in {g.label for g in structural_sweep_gates(ROOT, ["skills/public/demo/SKILL.md"])}
    # docs-only change pulls no structural sweep gate (no-op).
    assert structural_sweep_gates(ROOT, ["docs/x.md"]) == []


def test_block_on_structural_sweep_blocks_then_passes() -> None:
    # #332: a failed sweep gate blocks the full closeout (returns non-zero, status
    # blocked, records the failing label); a clean sweep returns None and lets the
    # closeout proceed.
    failing = {"status": "x", "changed_paths": ["scripts/x.py"]}
    rc = block_on_structural_sweep(
        ROOT, failing, as_json=True, plan_only=False, run_command=_runner(1), emit_payload=_sweep_sink
    )
    assert rc == 1
    assert failing["status"] == "blocked"
    assert failing["structural_sweep"]["failed_label"] == "validate-attention-state-visibility"

    clean = {"status": "x", "changed_paths": ["scripts/x.py"]}
    assert block_on_structural_sweep(
        ROOT, clean, as_json=True, plan_only=False, run_command=_runner(0), emit_payload=_sweep_sink
    ) is None
    assert clean["structural_sweep"]["status"] == "ok"
    assert clean["status"] == "x"  # untouched -> closeout continues


def test_block_on_structural_sweep_is_noop_in_plan_only() -> None:
    # plan_only surfaces the sweep through planned_commands, so the blocker no-ops.
    payload = {"status": "x", "changed_paths": ["scripts/x.py"]}
    assert block_on_structural_sweep(
        ROOT, payload, as_json=True, plan_only=True, run_command=_runner(1), emit_payload=_sweep_sink
    ) is None
    assert "structural_sweep" not in payload


def _minimal_surfaces(repo: Path) -> Path:
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    manifest = repo / ".agents" / "surfaces.json"
    manifest.write_text(
        json.dumps(
            {
                "version": 1,
                "surfaces": [
                    {
                        "surface_id": "repo-python",
                        "description": "repo python",
                        "source_paths": ["scripts/**"],
                        "derived_paths": [],
                        "sync_commands": [],
                        "verify_commands": [],
                        "notes": [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return manifest


def test_full_closeout_blocks_329_class_violation_at_structural_sweep(tmp_path: Path) -> None:
    # #332 high-confidence: the FULL closeout (not --predict-commit) blocks a
    # #329-class attention violation at the cheap structural sweep BEFORE reaching
    # surface-match/cautilus/broad pytest. Red without the fix: with the sweep
    # blocker removed the closeout would proceed to status=completed.
    repo = tmp_path / "repo"
    repo.mkdir()
    manifest = _minimal_surfaces(repo)
    scripts = repo / "scripts"
    scripts.mkdir()
    _write_executable(
        scripts / "validate_attention_state_visibility.py",
        "#!/usr/bin/env python3\nimport sys\nprint('undeclared skipped', file=sys.stderr)\nraise SystemExit(1)\n",
    )
    (scripts / "bad.py").write_text("STATE = 'skipped'\n", encoding="utf-8")

    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(repo),
        "--surfaces-path",
        str(manifest),
        "--skip-broad-pytest",
        "--allow-unmatched",
        "--json",
        "--paths",
        "scripts/bad.py",
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1, result.stderr
    assert payload["status"] == "blocked"
    assert payload["structural_sweep"]["failed_label"] == "validate-attention-state-visibility"


def test_fast_surface_verify_gates_degrade_on_surface_error() -> None:
    # #320: a manifest that loads but cannot match the changed paths makes
    # surfaces matching raise SurfaceError (here a repo-escaping path trips
    # normalize_repo_path). The commit-boundary gate must degrade to no extra
    # gates rather than propagate the error -- covers the
    # `except SurfaceError: return []` branch the mutation gate flagged as a
    # test-uncovered changed line.
    assert fast_surface_verify_gates(ROOT, ["../escape.py"]) == []


def test_unrelated_change_adds_no_fast_surface_gates() -> None:
    # #314: a markdown-only change whose surfaces declare no fast checker must
    # not pull the fast subset into the pre-commit plan (no broad widening).
    labels = {command.label for command in staged_commit_gate_plan(ROOT, ["README.md"], ruff_path="")}
    assert labels.isdisjoint(set(FAST_SURFACE_VERIFY_COMMANDS.values()))
