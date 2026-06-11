from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

from .support import ROOT, run_script


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


def test_run_slice_closeout_appends_agent_browser_hygiene_when_guard_exists(tmp_path: Path) -> None:
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
                        "derived_paths": [],
                        "sync_commands": [],
                        "verify_commands": ["python3 scripts/verify.py"],
                        "notes": [],
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "scripts" / "verify.py").write_text("from pathlib import Path\nPath('verify.log').write_text('verify\\n')\n", encoding="utf-8")
    (repo / "scripts" / "agent_browser_runtime_guard.py").write_text(
        "from pathlib import Path\nPath('hygiene.log').write_text('hygiene\\n')\n",
        encoding="utf-8",
    )
    result = run_script("scripts/run_slice_closeout.py", "--repo-root", str(repo), "--paths", "README.md", "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert [step["phase"] for step in payload["executed_commands"]] == ["verify", "verify"]
    assert (repo / "hygiene.log").read_text(encoding="utf-8").strip() == "hygiene"


def test_run_slice_closeout_blocks_unsafe_agent_browser_surface_commands(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
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
                        "derived_paths": [],
                        "sync_commands": [],
                        "verify_commands": ["bash -lc 'agent-browser open https://example.com'"],
                        "notes": [],
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script("scripts/run_slice_closeout.py", "--repo-root", str(repo), "--paths", "README.md", "--json")
    payload = json.loads(result.stdout)

    assert result.returncode == 1
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
    assert "." in captured.err
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
        "skills/public/setup/scripts/inspect_repo.py",
        "--skip-sync",
        "--skip-verify",
        "--json",
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert "public-skill validation review is required" in payload["error"]
    assert "--ack-cautilus-skill-review" in payload["error"]
    assert payload["cautilus_plan"]["run_mode"] == "ask"
    assert payload["cautilus_plan"]["status"] == "not-required"
    assert payload["cautilus_plan"]["required"] is False
    assert payload["cautilus_plan"]["scenario_registry_review_required"] is True
    assert payload["cautilus_plan"]["changed_public_skills"] == ["setup"]
    assert any(
        item["skill_id"] == "setup"
        for item in payload["cautilus_plan"]["skill_validation_recommendations"]
    )


def test_run_slice_closeout_allows_acknowledged_public_skill_review() -> None:
    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "skills/public/setup/scripts/inspect_repo.py",
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


def test_run_slice_closeout_blocks_hitl_recommended_public_skill_review_until_acknowledged() -> None:
    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "skills/public/critique/SKILL.md",
        "charness-artifacts/cautilus/latest.md",
        "--skip-sync",
        "--skip-verify",
        "--json",
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["cautilus_plan"]["run_mode"] == "ask"
    assert payload["cautilus_plan"]["status"] == "ready-for-validation"
    assert payload["cautilus_plan"]["required"] is False
    assert payload["cautilus_plan"]["artifact_changed"] is True
    assert payload["cautilus_plan"]["scenario_registry_review_required"] is False
    assert payload["cautilus_plan"]["changed_public_skills"] == ["critique"]
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
                "- Critique Required: yes",
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
        "# Critique\n\n- Interrupt Source: seam-demo\n",
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


