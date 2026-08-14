from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from scripts import check_python_runtime_inheritance

from .support import ROOT, run_loaded_script_main, run_script


def demo_surface(
    *,
    source_paths: list[str] | None = None,
    derived_paths: list[str] | None = None,
    sync_commands: list[str] | None = None,
    verify_commands: list[str] | None = None,
    notes: list[str] | None = None,
) -> dict[str, object]:
    return {
        "surface_id": "demo-surface",
        "description": "demo",
        "source_paths": source_paths if source_paths is not None else ["README.md"],
        "derived_paths": derived_paths if derived_paths is not None else [],
        "sync_commands": sync_commands if sync_commands is not None else [],
        "verify_commands": verify_commands if verify_commands is not None else [],
        "notes": notes if notes is not None else [],
    }


def write_surface_manifest(repo: Path, *surfaces: dict[str, object]) -> None:
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "surfaces.json").write_text(
        json.dumps({"version": 1, "surfaces": list(surfaces)}, indent=2) + "\n",
        encoding="utf-8",
    )


def test_run_slice_closeout_executes_sync_then_verify(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    write_surface_manifest(
        repo,
        demo_surface(
            derived_paths=["plugins/demo/README.md"],
            sync_commands=["python3 scripts/sync.py"],
            verify_commands=["python3 scripts/verify.py"],
            notes=["demo note"],
        ),
    )
    (repo / "scripts" / "sync.py").write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from pathlib import Path",
                "root = Path.cwd()",
                "(root / 'plugins' / 'demo').mkdir(parents=True, exist_ok=True)",
                "(root / 'plugins' / 'demo' / 'README.md').write_text('# Generated\\n', encoding='utf-8')",
                "(root / 'sync.log').write_text('sync\\n', encoding='utf-8')",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "scripts" / "verify.py").write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from pathlib import Path",
                "root = Path.cwd()",
                "assert (root / 'plugins' / 'demo' / 'README.md').is_file()",
                "(root / 'verify.log').write_text('verify\\n', encoding='utf-8')",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(repo),
        "--paths",
        "README.md",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "completed"
    assert payload["effective_exit_code"] == result.returncode == 0
    assert payload["proof_receipt"]["surface"] == "closeout"
    assert [step["phase"] for step in payload["executed_commands"]] == ["sync", "verify"]
    assert (repo / "sync.log").read_text(encoding="utf-8").strip() == "sync"
    assert (repo / "verify.log").read_text(encoding="utf-8").strip() == "verify"


def test_run_slice_closeout_attaches_telemetry_on_stop_path(tmp_path: Path) -> None:
    # A failing verify command drives main() to the should_stop branch, which must
    # still attach closeout telemetry (spec achieve-efficiency E1 — failed runs
    # record waste too). Covers the stop-path _attach_closeout_telemetry call site.
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    write_surface_manifest(repo, demo_surface(verify_commands=["python3 scripts/verify.py"]))
    (repo / "scripts" / "verify.py").write_text("import sys\nsys.exit(1)\n", encoding="utf-8")

    result = run_script("scripts/run_slice_closeout.py", "--repo-root", str(repo), "--paths", "README.md")
    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "failed"
    assert payload["effective_exit_code"] == result.returncode == 1
    assert payload["proof_receipt"]["adverse_subjects"]
    assert "closeout_telemetry" in payload  # attached on the stop path


def test_emit_payload_repairs_blank_adverse_cause(capsys) -> None:
    from scripts import run_slice_closeout as closeout

    payload = {"status": "blocked", "changed_paths": [], "executed_commands": [], "error": ""}

    assert closeout._emit_payload(payload) == 1
    emitted = yaml.safe_load(capsys.readouterr().out)
    assert emitted["error"].startswith("closeout receipt could not identify a cause:")
    assert emitted["proof_receipt"]["cause"] == emitted["error"]


def test_run_slice_closeout_appends_agent_browser_hygiene_when_guard_exists(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    write_surface_manifest(repo, demo_surface(verify_commands=["python3 scripts/verify.py"]))
    (repo / "scripts" / "verify.py").write_text("from pathlib import Path\nPath('verify.log').write_text('verify\\n')\n", encoding="utf-8")
    (repo / "scripts" / "agent_browser_runtime_guard.py").write_text(
        "from pathlib import Path\nPath('hygiene.log').write_text('hygiene\\n')\n",
        encoding="utf-8",
    )
    result = run_script("scripts/run_slice_closeout.py", "--repo-root", str(repo), "--paths", "README.md")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert [step["phase"] for step in payload["executed_commands"]] == ["verify", "verify"]
    assert (repo / "hygiene.log").read_text(encoding="utf-8").strip() == "hygiene"


def test_run_slice_closeout_blocks_unsafe_agent_browser_surface_commands(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    write_surface_manifest(
        repo,
        demo_surface(verify_commands=["bash -lc 'agent-browser open https://example.com'"]),
    )

    result = run_script("scripts/run_slice_closeout.py", "--repo-root", str(repo), "--paths", "README.md")
    payload = yaml.safe_load(result.stdout)

    assert result.returncode == 1
    assert payload["status"] == "blocked"
    assert payload["proof_receipt"]["cause"]
    assert payload["proof_receipt"]["effective_exit_code"] == result.returncode
    assert "unsafe agent-browser probe" in "\n".join(payload["blockers"])


def test_run_slice_closeout_plan_only_blocks_invalid_focused_coverage_command() -> None:
    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "scripts/mutation_coverage_producer.py",
        "--skip-sync",
        "--verification-lock",
        "--produce-mutation-coverage",
        "--mutation-coverage-command",
        "python3 scripts/not_pytest.py",
        "--plan-only",
    )

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "blocked"
    assert "must start with" in payload["error"]


def test_run_slice_closeout_plan_only_lists_focused_coverage_command() -> None:
    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "scripts/mutation_coverage_producer.py",
        "--skip-sync",
        "--verification-lock",
        "--produce-mutation-coverage",
        "--mutation-coverage-command",
        "python3 -m pytest -q tests/quality_gates/test_mutation_coverage_producer.py",
        "--plan-only",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    planned = payload["planned_commands"]
    assert planned[-1] == {
        "phase": "verify",
        "command": "python3 -m pytest -q tests/quality_gates/test_mutation_coverage_producer.py",
        "coverage_producer": True,
    }


def test_run_slice_closeout_plan_only_lists_extra_coverage_targets() -> None:
    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "scripts/mutation_coverage_producer.py",
        "--skip-sync",
        "--verification-lock",
        "--produce-mutation-coverage",
        "--mutation-coverage-extra-pytest-target",
        "tests/quality_gates/test_mutation_coverage_producer.py::test_instrument_broad_command_rewrites_and_preserves_glob",
        "--plan-only",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["planned_commands"][-1] == {
        "phase": "verify",
        "coverage_producer": True,
        "extra_pytest_targets": [
            "tests/quality_gates/test_mutation_coverage_producer.py::test_instrument_broad_command_rewrites_and_preserves_glob"
        ],
    }


def test_run_slice_closeout_blocks_extra_targets_without_producer() -> None:
    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "scripts/mutation_coverage_producer.py",
        "--skip-sync",
        "--verification-lock",
        "--mutation-coverage-extra-pytest-target",
        "tests/quality_gates/test_mutation_coverage_producer.py",
        "--plan-only",
    )

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert "--mutation-coverage-extra-pytest-target requires" in payload["error"]


def test_run_slice_closeout_internal_focused_command_plan_helpers(
    tmp_path: Path, monkeypatch
) -> None:
    from scripts import run_slice_closeout as closeout

    swept: list[list[str]] = []
    args = SimpleNamespace(
        produce_mutation_coverage=True,
        mutation_coverage_command="python3 -m pytest -q tests/demo.py",
        mutation_coverage_extra_pytest_target=[],
    )
    monkeypatch.setattr(
        closeout,
        "structural_sweep_planned_commands",
        lambda repo_root, paths: swept.append(paths) or [],
    )
    closeout._planned_commands(
        tmp_path,
        ["historical.md", "live.py"],
        [("verify", "ruff check .")],
        args,
        structural_paths=["live.py"],
    )
    assert swept == [["live.py"]]

    assert closeout._unsafe_blocker_command_plan([("verify", "ruff check .")], args) == [
        ("verify", "ruff check ."),
        ("verify", "python3 -m pytest -q tests/demo.py"),
    ]
    assert closeout._planned_commands(tmp_path, ["README.md"], [("verify", "ruff check .")], args)[-1] == {
        "phase": "verify",
        "command": "python3 -m pytest -q tests/demo.py",
        "coverage_producer": True,
    }


def test_run_slice_closeout_preexecution_blocks_invalid_focused_command(
    tmp_path: Path, monkeypatch
) -> None:
    from scripts import run_slice_closeout as closeout

    payload = {"changed_paths": ["README.md"], "executed_commands": []}
    monkeypatch.setattr(closeout, "block_on_structural_sweep", lambda *args, **kwargs: None)
    for name in (
        "advise_prose_pin",
        "advise_skill_surface_preflight",
        "advise_doc_surface_preflight",
        "advise_new_pool_module",
        "advise_over_slicing",
        "advise_floor_addition_restraint",
        "advise_close_keyword_leakage",
        "advise_decaying_habits",
    ):
        monkeypatch.setattr(closeout, name, lambda *args, **kwargs: None)
    monkeypatch.setattr(closeout, "_maybe_block_on_unmatched", lambda *args, **kwargs: None)
    monkeypatch.setattr(closeout, "_maybe_block_on_cautilus", lambda *args, **kwargs: None)
    monkeypatch.setattr(closeout, "_maybe_block_on_risk_interrupt", lambda *args, **kwargs: None)

    rc = closeout._run_preexecution_blocks(
        tmp_path,
        payload,
        SimpleNamespace(
            plan_only=False,
            allow_unmatched=False,
            ack_cautilus_skill_review=False,
            produce_mutation_coverage=True,
            mutation_coverage_command="python3 scripts/not_pytest.py",
        ),
    )

    assert rc == 1
    assert payload["status"] == "blocked"
    assert "must start with" in payload["error"]


def test_base_range_preexecution_sweeps_only_live_worktree_paths(
    tmp_path: Path, monkeypatch
) -> None:
    from scripts import run_slice_closeout as closeout

    payload = {"changed_paths": ["historical.md", "live.py"], "executed_commands": []}
    seen: dict[str, object] = {}

    def capture(*args, **kwargs):
        seen["paths"] = kwargs["paths"]
        return 9

    monkeypatch.setattr(closeout, "block_on_structural_sweep", capture)

    rc = closeout._run_preexecution_blocks(
        tmp_path,
        payload,
        SimpleNamespace(plan_only=False),
        structural_paths=["live.py"],
    )

    assert rc == 9
    assert seen["paths"] == ["live.py"]
    assert payload["changed_paths"] == ["historical.md", "live.py"]


@pytest.mark.parametrize("base", [None, "auto"])
def test_run_slice_closeout_main_runs_focused_coverage_after_plan(
    tmp_path: Path, monkeypatch, base: str | None
) -> None:
    from scripts import run_slice_closeout as closeout

    seen: dict[str, object] = {}
    payload = {
        "changed_paths": ["README.md"],
        "sync_commands": [],
        "verify_commands": [],
        "unmatched_paths": [],
        "executed_commands": [],
    }
    argv = ["run_slice_closeout.py", "--repo-root", str(tmp_path)]
    if base is not None:
        argv += ["--base", base]
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(closeout, "_advise_staged_reversion", lambda repo_root: None)
    monkeypatch.setattr(closeout, "load_surfaces", lambda repo_root, surfaces_path=None: {"path": "manifest"})
    monkeypatch.setattr(closeout, "_resolve_changed_paths", lambda repo_root, args: ["README.md"])
    monkeypatch.setattr(closeout, "match_surfaces", lambda manifest, changed_paths: dict(payload))
    monkeypatch.setattr(closeout, "headroom_for", lambda paths, repo_root: [])
    monkeypatch.setattr(closeout, "collect_changed_paths", lambda repo_root: ["live.py"])

    def capture_preexecution(*args, **kwargs):
        seen["structural_paths"] = kwargs["structural_paths"]
        return None

    monkeypatch.setattr(closeout, "_run_preexecution_blocks", capture_preexecution)
    monkeypatch.setattr(
        closeout,
        "plan_broad_pytest_policy",
        lambda command_plan, **kwargs: {"command_plan": command_plan},
    )
    monkeypatch.setattr(closeout, "should_block_broad_pytest_policy", lambda *args, **kwargs: False)
    monkeypatch.setattr(closeout, "_unsafe_command_blockers", lambda command_plan: [])
    monkeypatch.setattr(closeout, "_unsafe_blocker_command_plan", lambda command_plan, args: command_plan)
    monkeypatch.setattr(
        closeout,
        "_resolve_broad_producer",
        lambda *args, **kwargs: seen.setdefault("broad", kwargs.get("base_sha")),
    )
    monkeypatch.setattr(closeout, "execute_command_plan", lambda *args, **kwargs: False)
    monkeypatch.setattr(
        closeout,
        "run_focused_closeout_coverage",
        lambda args, repo_root, payload, run_command, **kwargs: seen.setdefault("focused", kwargs.get("base_sha"))
        or False,
    )
    monkeypatch.setattr(closeout, "attach_gate_runtime_advisory", lambda payload: None)
    monkeypatch.setattr(closeout, "emit_usage_episode_for_slice_closeout", lambda repo_root, status: {"status": "emitted"})
    monkeypatch.setattr(closeout, "_attach_closeout_telemetry", lambda repo_root, payload: None)
    monkeypatch.setattr(closeout, "_emit_payload", lambda payload, **kwargs: 0)

    assert closeout.main() == 0
    assert seen["structural_paths"] == (["live.py"] if base is not None else None)
    assert seen == {
        "broad": None,
        "focused": None,
        "structural_paths": ["live.py"] if base is not None else None,
    }


def test_run_slice_closeout_main_reuses_explicit_campaign_sha_for_both_producers(
    tmp_path: Path, monkeypatch
) -> None:
    from scripts import run_slice_closeout as closeout

    resolved: list[str] = []
    seen: dict[str, object] = {}
    payload = {
        "changed_paths": ["README.md"],
        "sync_commands": [],
        "verify_commands": [],
        "unmatched_paths": [],
        "executed_commands": [],
    }
    monkeypatch.setattr(
        sys,
        "argv",
        ["run_slice_closeout.py", "--repo-root", str(tmp_path), "--base", "campaign-ref"],
    )
    monkeypatch.setattr(closeout, "_advise_staged_reversion", lambda repo_root: None)
    monkeypatch.setattr(closeout, "load_surfaces", lambda repo_root, surfaces_path=None: {"path": "manifest"})
    monkeypatch.setattr(
        closeout,
        "resolve_explicit_campaign_base",
        lambda repo_root, base, *, has_paths=False: resolved.append(base) or "campaign-sha",
    )
    monkeypatch.setattr(
        closeout,
        "collect_changed_paths_since_resolved_base",
        lambda repo_root, base_sha: ["README.md"] if base_sha == "campaign-sha" else [],
    )
    monkeypatch.setattr(closeout, "match_surfaces", lambda manifest, changed_paths: dict(payload))
    monkeypatch.setattr(closeout, "headroom_for", lambda paths, repo_root: [])
    monkeypatch.setattr(closeout, "collect_changed_paths", lambda repo_root: ["staged.py", "unstaged.py"])

    def capture_preexecution(*args, **kwargs):
        seen["structural_paths"] = kwargs["structural_paths"]
        return None

    monkeypatch.setattr(closeout, "_run_preexecution_blocks", capture_preexecution)
    monkeypatch.setattr(
        closeout,
        "plan_broad_pytest_policy",
        lambda command_plan, **kwargs: {"command_plan": command_plan},
    )
    monkeypatch.setattr(closeout, "should_block_broad_pytest_policy", lambda *args, **kwargs: False)
    monkeypatch.setattr(closeout, "_unsafe_command_blockers", lambda command_plan: [])
    monkeypatch.setattr(closeout, "_unsafe_blocker_command_plan", lambda command_plan, args: command_plan)
    monkeypatch.setattr(
        closeout,
        "_resolve_broad_producer",
        lambda args, repo_root, run_command, *, base_sha=None: seen.setdefault("broad", base_sha),
    )
    monkeypatch.setattr(closeout, "execute_command_plan", lambda *args, **kwargs: False)
    monkeypatch.setattr(
        closeout,
        "run_focused_closeout_coverage",
        lambda args, repo_root, payload, run_command, *, base_sha=None: seen.setdefault("focused", base_sha)
        or False,
    )
    monkeypatch.setattr(closeout, "attach_gate_runtime_advisory", lambda payload: None)
    monkeypatch.setattr(closeout, "emit_usage_episode_for_slice_closeout", lambda repo_root, status: {"status": "emitted"})
    monkeypatch.setattr(closeout, "_attach_closeout_telemetry", lambda repo_root, payload: None)
    monkeypatch.setattr(closeout, "_emit_payload", lambda payload, **kwargs: 0)

    assert closeout.main() == 0
    assert resolved == ["campaign-ref"]
    assert seen == {
        "broad": "campaign-sha",
        "focused": "campaign-sha",
        "structural_paths": ["staged.py", "unstaged.py"],
    }


def test_run_slice_closeout_main_fails_narrow_broad_pytest_proof_scope(
    tmp_path: Path, monkeypatch
) -> None:
    from scripts import run_slice_closeout as closeout

    emitted: dict[str, object] = {}
    payload = {
        "changed_paths": ["README.md", "scripts/tool.py"],
        "sync_commands": [],
        "verify_commands": ["python3 scripts/run_standing_pytest.py --repo-root . --mode read-only"],
        "unmatched_paths": [],
        "executed_commands": [],
    }
    monkeypatch.setattr(sys, "argv", ["run_slice_closeout.py", "--repo-root", str(tmp_path)])
    monkeypatch.setattr(closeout, "_advise_staged_reversion", lambda repo_root: None)
    monkeypatch.setattr(closeout, "load_surfaces", lambda repo_root, surfaces_path=None: {"path": "manifest"})
    monkeypatch.setattr(closeout, "_resolve_changed_paths", lambda repo_root, args: ["README.md", "scripts/tool.py"])
    monkeypatch.setattr(closeout, "match_surfaces", lambda manifest, changed_paths: dict(payload))
    monkeypatch.setattr(closeout, "headroom_for", lambda paths, repo_root: [])
    monkeypatch.setattr(closeout, "_run_preexecution_blocks", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        closeout,
        "plan_broad_pytest_policy",
        lambda command_plan, **kwargs: {"command_plan": command_plan},
    )
    monkeypatch.setattr(closeout, "should_block_broad_pytest_policy", lambda *args, **kwargs: False)
    monkeypatch.setattr(closeout, "_unsafe_command_blockers", lambda command_plan: [])
    monkeypatch.setattr(closeout, "_unsafe_blocker_command_plan", lambda command_plan, args: command_plan)
    monkeypatch.setattr(closeout, "_resolve_broad_producer", lambda *args, **kwargs: None)

    def fake_execute_command_plan(*args, **kwargs) -> bool:
        closeout_payload = args[2]
        closeout_payload["recorded_broad_pytest_proofs"] = [
            {"command": "pytest", "changed_paths": ["README.md"]}
        ]
        return False

    monkeypatch.setattr(closeout, "execute_command_plan", fake_execute_command_plan)
    monkeypatch.setattr(closeout, "run_focused_closeout_coverage", lambda *args, **kwargs: False)
    monkeypatch.setattr(closeout, "attach_gate_runtime_advisory", lambda payload: None)
    monkeypatch.setattr(closeout, "_attach_closeout_telemetry", lambda repo_root, payload: None)
    monkeypatch.setattr(closeout, "_emit_payload", lambda payload, **kwargs: emitted.update(payload) or 1)

    assert closeout.main() == 1
    assert emitted["status"] == "failed"
    assert emitted["broad_pytest_scope_findings"][0]["missing_changed_paths"] == ["scripts/tool.py"]


def test_run_slice_closeout_blocks_unsafe_focused_coverage_command(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    write_surface_manifest(repo, demo_surface())

    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(repo),
        "--paths",
        "README.md",
        "--skip-sync",
        "--skip-verify",
        "--verification-lock",
        "--produce-mutation-coverage",
        "--mutation-coverage-command",
        "pytest -q tests/test_demo.py; agent-browser open https://example.com",
    )

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "blocked"
    assert "unsafe agent-browser probe" in "\n".join(payload["blockers"])


def test_run_slice_closeout_preserves_parent_python_before_login_shell_path(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    fake_python = fake_bin / "python3"
    fake_python.write_text(
        "#!/usr/bin/env bash\n"
        "echo wrong-python >&2\n"
        "exit 42\n",
        encoding="utf-8",
    )
    fake_python.chmod(0o755)
    fake_pytest = fake_bin / "pytest"
    fake_pytest.write_text(
        "#!/usr/bin/env bash\n"
        "echo wrong-pytest >&2\n"
        "exit 43\n",
        encoding="utf-8",
    )
    fake_pytest.chmod(0o755)
    fake_node = fake_bin / "node"
    fake_node.write_text("#!/usr/bin/env bash\necho fake-node\n", encoding="utf-8")
    fake_node.chmod(0o755)
    child_script = repo / "child.py"
    child_script.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "print(sys.executable)\n",
        encoding="utf-8",
    )
    child_script.chmod(0o755)
    monkeypatch.setenv("PATH", f"{fake_bin}:{os.environ.get('PATH', '')}")

    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import run_slice_closeout

        result = run_slice_closeout.run_command(
            repo,
            "python3 -c 'import sys; print(sys.executable)' && ./child.py && pytest --version && node",
            "verify",
        )
    finally:
        sys.path.remove(str(ROOT / "scripts"))
        sys.modules.pop("run_slice_closeout", None)

    assert result["returncode"] == 0, result["stderr"]
    output_lines = result["stdout"].strip().splitlines()
    assert output_lines[0] == sys.executable
    assert output_lines[1] == sys.executable
    assert output_lines[2].startswith("pytest ")
    assert output_lines[3] == "fake-node"


def test_run_slice_closeout_emits_heartbeat_for_long_running_commands(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setenv("CHARNESS_CLOSEOUT_PROGRESS_INTERVAL_SECONDS", "0.1")

    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import run_slice_closeout

        result = run_slice_closeout.run_command(
            repo,
            "python3 -c 'import time; time.sleep(0.25); print(\"done\")'",
            "verify",
        )
    finally:
        sys.path.remove(str(ROOT / "scripts"))
        sys.modules.pop("run_slice_closeout", None)

    captured = capsys.readouterr()
    assert result["returncode"] == 0, result["stderr"]
    assert result["stdout"].strip() == "done"
    assert "RUN [verify]" in captured.err
    assert "HEARTBEAT [verify] elapsed=" in captured.err
    assert "PASS [verify]" in captured.err


def test_check_python_runtime_inheritance_rejects_unpinned_bash_login_shell(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scripts_dir = repo / "scripts"
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "bad.py").write_text(
        "\n".join(
            [
                "import subprocess",
                "",
                "def run(command):",
                "    return subprocess.run(['/bin/bash', '-lc', command])",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_loaded_script_main(
        "check_python_runtime_inheritance.py",
        check_python_runtime_inheritance,
        "--repo-root",
        str(repo),
    )

    assert result.returncode == 1
    assert "bad.py:4" in result.stderr
    assert "must pin" in result.stderr


def test_run_slice_closeout_blocks_unmatched_paths_by_default(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_surface_manifest(repo, demo_surface())

    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(repo),
        "--paths",
        "notes/todo.txt",
    )
    assert result.returncode == 1
    assert "not covered by the surfaces manifest" in result.stderr
