from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from .support import ROOT, run_script


def test_check_changed_surfaces_reports_expected_obligations_for_readme() -> None:
    result = run_script(
        "scripts/check_changed_surfaces.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "README.md",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    surface_ids = {surface["surface_id"] for surface in payload["matched_surfaces"]}
    assert "checked-in-plugin-export" in surface_ids
    assert "repo-markdown" in surface_ids
    assert "python3 scripts/sync_root_plugin_manifests.py --repo-root ." in payload["sync_commands"]
    assert "python3 scripts/validate_packaging.py --repo-root ." in payload["verify_commands"]
    assert "python3 scripts/validate_packaging_committed.py --repo-root ." in payload["verify_commands"]
    assert "python3 scripts/check_doc_links.py --repo-root ." in payload["verify_commands"]
    assert "./scripts/check-markdown.sh" in payload["verify_commands"]


def test_check_changed_surfaces_reports_unmatched_paths() -> None:
    result = run_script(
        "scripts/check_changed_surfaces.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "notes/private-plan.txt",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["matched_surfaces"] == []
    assert payload["unmatched_paths"] == ["notes/private-plan.txt"]


def test_select_verifiers_returns_smallest_repo_owned_bundle_for_readme() -> None:
    result = run_script(
        "scripts/select_verifiers.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "README.md",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["bundle_status"] == "repo-owned-bundle"
    recommendations = payload["recommended_commands"]
    assert recommendations[0] == {
        "phase": "sync",
        "command": "python3 scripts/sync_root_plugin_manifests.py --repo-root .",
        "reason_surface_ids": ["checked-in-plugin-export"],
    }
    verify_commands = {item["command"] for item in recommendations if item["phase"] == "verify"}
    assert "python3 scripts/validate_packaging.py --repo-root ." in verify_commands
    assert "python3 scripts/validate_packaging_committed.py --repo-root ." in verify_commands
    assert "python3 scripts/check_doc_links.py --repo-root ." in verify_commands
    assert "./scripts/check-markdown.sh" in verify_commands


def test_select_verifiers_includes_public_skill_policy_for_public_skill_changes() -> None:
    result = run_script(
        "scripts/select_verifiers.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "skills/public/premortem/SKILL.md",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    verify_commands = {item["command"] for item in payload["recommended_commands"] if item["phase"] == "verify"}
    assert "python3 scripts/validate_skills.py --repo-root ." in verify_commands
    assert "python3 scripts/validate_public_skill_validation.py --repo-root ." in verify_commands
    assert "python3 scripts/validate_public_skill_dogfood.py --repo-root ." in verify_commands
    assert "python3 scripts/validate_cautilus_proof.py --repo-root ." in verify_commands


def test_select_verifiers_includes_public_skill_policy_for_policy_json_changes() -> None:
    result = run_script(
        "scripts/select_verifiers.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "docs/public-skill-validation.json",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    verify_commands = {item["command"] for item in payload["recommended_commands"] if item["phase"] == "verify"}
    assert "python3 scripts/validate_public_skill_validation.py --repo-root ." in verify_commands


def test_select_verifiers_includes_adapter_and_prompt_proof_for_named_cautilus_adapter_changes() -> None:
    result = run_script(
        "scripts/select_verifiers.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        ".agents/cautilus-adapters/chatbot-proposals.yaml",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    verify_commands = {item["command"] for item in payload["recommended_commands"] if item["phase"] == "verify"}
    assert "python3 scripts/validate_adapters.py --repo-root ." in verify_commands
    assert "python3 scripts/validate_cautilus_proof.py --repo-root ." in verify_commands


def test_select_verifiers_includes_chatbot_proposal_runner_for_packet_changes() -> None:
    result = run_script(
        "scripts/select_verifiers.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "evals/cautilus/chatbot-scenario-proposal-inputs.json",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    verify_commands = {item["command"] for item in payload["recommended_commands"] if item["phase"] == "verify"}
    assert "python3 scripts/validate_cautilus_scenarios.py --repo-root ." in verify_commands
    assert "python3 scripts/eval_cautilus_chatbot_proposals.py --repo-root . --json" in verify_commands


def test_select_verifiers_includes_chatbot_benchmark_smoke_for_compare_runner_changes() -> None:
    result = run_script(
        "scripts/select_verifiers.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "scripts/eval_cautilus_chatbot_compare.py",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    verify_commands = {item["command"] for item in payload["recommended_commands"] if item["phase"] == "verify"}
    assert (
        "python3 scripts/eval_cautilus_chatbot_compare.py --repo-root . --baseline-repo . --candidate-repo . --output-dir /tmp/charness-cautilus-chatbot-benchmark-self-compare"
        in verify_commands
    )


def test_select_verifiers_includes_public_skill_dogfood_for_registry_changes() -> None:
    result = run_script(
        "scripts/select_verifiers.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "docs/public-skill-dogfood.json",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    verify_commands = {item["command"] for item in payload["recommended_commands"] if item["phase"] == "verify"}
    assert "python3 scripts/validate_public_skill_dogfood.py --repo-root ." in verify_commands


def test_select_verifiers_reports_missing_bundle_for_unmatched_paths() -> None:
    result = run_script(
        "scripts/select_verifiers.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "notes/private-plan.txt",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["bundle_status"] == "missing-bundle"
    assert payload["recommended_commands"] == []
    assert any("not covered by `.agents/surfaces.json`" in note for note in payload["notes"])
    assert any("No repo-owned verifier bundle matched these changes" in note for note in payload["notes"])


def test_validate_surfaces_rejects_duplicate_ids(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "surfaces.json").write_text(
        json.dumps(
            {
                "version": 1,
                "surfaces": [
                    {
                        "surface_id": "dup",
                        "description": "first",
                        "source_paths": ["README.md"],
                        "derived_paths": [],
                        "sync_commands": [],
                        "verify_commands": [],
                        "notes": [],
                    },
                    {
                        "surface_id": "dup",
                        "description": "second",
                        "source_paths": ["docs/**"],
                        "derived_paths": [],
                        "sync_commands": [],
                        "verify_commands": [],
                        "notes": [],
                    },
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script("scripts/validate_surfaces.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "duplicate surface id `dup`" in result.stderr


def test_run_slice_closeout_executes_sync_then_verify(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "scripts").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / ".agents" / "surfaces.json").write_text(
        json.dumps(
            {
                "version": 1,
                "surfaces": [
                    {
                        "surface_id": "demo-surface",
                        "description": "demo",
                        "source_paths": ["README.md"],
                        "derived_paths": ["plugins/demo/README.md"],
                        "sync_commands": ["python3 scripts/sync.py"],
                        "verify_commands": ["python3 scripts/verify.py"],
                        "notes": ["demo note"],
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
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
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "completed"
    assert [step["phase"] for step in payload["executed_commands"]] == ["sync", "verify"]
    assert (repo / "sync.log").read_text(encoding="utf-8").strip() == "sync"
    assert (repo / "verify.log").read_text(encoding="utf-8").strip() == "verify"


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
    monkeypatch.setenv("PATH", f"{fake_bin}:{os.environ.get('PATH', '')}")

    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import run_slice_closeout

        result = run_slice_closeout.run_command(
            repo,
            "python3 -c 'import sys; print(sys.executable)' && pytest --version",
            "verify",
        )
    finally:
        sys.path.remove(str(ROOT / "scripts"))
        sys.modules.pop("run_slice_closeout", None)

    assert result["returncode"] == 0, result["stderr"]
    output_lines = result["stdout"].strip().splitlines()
    assert output_lines[0] == sys.executable
    assert output_lines[1].startswith("pytest ")


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

    result = run_script(
        "scripts/check_python_runtime_inheritance.py",
        "--repo-root",
        str(repo),
    )

    assert result.returncode == 1
    assert "bad.py:4" in result.stderr
    assert "must pin" in result.stderr


def test_run_slice_closeout_blocks_unmatched_paths_by_default(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "surfaces.json").write_text(
        json.dumps(
            {
                "version": 1,
                "surfaces": [
                    {
                        "surface_id": "demo-surface",
                        "description": "demo",
                        "source_paths": ["README.md"],
                        "derived_paths": [],
                        "sync_commands": [],
                        "verify_commands": [],
                        "notes": [],
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(repo),
        "--paths",
        "notes/todo.txt",
    )
    assert result.returncode == 1
    assert "not covered by the surfaces manifest" in result.stderr


def test_run_slice_closeout_blocks_public_skill_review_until_acknowledged() -> None:
    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "skills/public/init-repo/scripts/inspect_repo.py",
        "--skip-sync",
        "--skip-verify",
        "--json",
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert "public-skill validation review is required" in payload["error"]
    assert "--ack-cautilus-skill-review" in payload["error"]
    assert payload["cautilus_plan"]["required"] is False
    assert payload["cautilus_plan"]["scenario_registry_review_required"] is True
    assert payload["cautilus_plan"]["changed_public_skills"] == ["init-repo"]
    assert any(
        item["skill_id"] == "init-repo"
        for item in payload["cautilus_plan"]["skill_validation_recommendations"]
    )


def test_run_slice_closeout_allows_acknowledged_public_skill_review() -> None:
    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "skills/public/init-repo/scripts/inspect_repo.py",
        "--skip-sync",
        "--skip-verify",
        "--ack-cautilus-skill-review",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "completed"
    assert payload["cautilus_plan"]["scenario_registry_review_required"] is True
    assert payload["executed_commands"] == []


def test_run_slice_closeout_blocks_hitl_recommended_public_skill_review() -> None:
    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "skills/public/premortem/SKILL.md",
        "charness-artifacts/cautilus/latest.md",
        "--skip-sync",
        "--skip-verify",
        "--json",
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["cautilus_plan"]["required"] is True
    assert payload["cautilus_plan"]["artifact_changed"] is True
    assert payload["cautilus_plan"]["scenario_registry_review_required"] is False
    assert payload["cautilus_plan"]["changed_public_skills"] == ["premortem"]
    assert payload["cautilus_plan"]["skill_validation_recommendations"][0]["validation_tier"] == "hitl-recommended"
    assert "public-skill validation review is required" in payload["error"]


def test_run_slice_closeout_blocks_for_forced_risk_interrupt_without_spec_refresh(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "debug").mkdir(parents=True)
    (repo / "charness-artifacts" / "spec").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / ".agents" / "debug-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/debug",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / ".agents" / "surfaces.json").write_text(
        json.dumps(
            {
                "version": 1,
                "surfaces": [
                    {
                        "surface_id": "demo-surface",
                        "description": "demo",
                        "source_paths": ["README.md", "charness-artifacts/debug/latest.md", "charness-artifacts/spec/*.md"],
                        "derived_paths": [],
                        "sync_commands": [],
                        "verify_commands": [],
                        "notes": [],
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "charness-artifacts" / "debug" / "latest.md").write_text(
        "\n".join(
            [
                "# Debug Review",
                "Date: 2026-04-22",
                "",
                "## Problem",
                "",
                "problem",
                "",
                "## Correct Behavior",
                "",
                "correct",
                "",
                "## Observed Facts",
                "",
                "- fact",
                "",
                "## Reproduction",
                "",
                "repro",
                "",
                "## Candidate Causes",
                "",
                "- one",
                "- two",
                "- three",
                "",
                "## Hypothesis",
                "",
                "hypothesis",
                "",
                "## Verification",
                "",
                "verification",
                "",
                "## Root Cause",
                "",
                "root cause",
                "",
                "## Seam Risk",
                "",
                "- Interrupt ID: seam-demo",
                "- Risk Class: host-disproves-local",
                "- Seam: slack-thread-activation",
                "- Disproving Observation: live host disproved local reasoning",
                "- What Local Reasoning Cannot Prove: thread visibility semantics",
                "- Generalization Pressure: factor-now",
                "",
                "## Interrupt Decision",
                "",
                "- Premortem Required: yes",
                "- Next Step: spec",
                "- Handoff Artifact: charness-artifacts/spec/interrupt-demo.md",
                "",
                "## Prevention",
                "",
                "prevention",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "charness-artifacts" / "spec" / "interrupt-demo.md").write_text(
        "# Premortem\n\n- Interrupt Source: seam-demo\n",
        encoding="utf-8",
    )

    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(repo),
        "--paths",
        "README.md",
        "charness-artifacts/debug/latest.md",
        "--json",
    )
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["risk_interrupt_plan"]["status"] == "blocked"
