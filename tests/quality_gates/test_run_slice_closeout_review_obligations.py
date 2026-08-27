from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml

from scripts import run_slice_closeout as closeout

from .support import run_script


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


@pytest.mark.parametrize(
    ("plan", "allowed"),
    [
        ({"status": "not-applicable", "required": False}, True),
        (
            {
                "status": "handoff-recorded",
                "required": True,
                "impl_status": "allowed",
                "chosen_next_step": "impl",
            },
            True,
        ),
        ({"status": "not-applicable", "required": True}, False),
        ({"status": "blocked", "required": True}, False),
        (
            {
                "status": "handoff-recorded",
                "required": True,
                "impl_status": "blocked",
                "chosen_next_step": "impl",
            },
            False,
        ),
        (
            {
                "status": "handoff-recorded",
                "required": True,
                "impl_status": "allowed",
                "chosen_next_step": "critique",
            },
            False,
        ),
        (
            {
                "status": "handoff-recorded",
                "required": True,
                "impl_status": "allowed",
                "chosen_next_step": "factor-first",
            },
            False,
        ),
        (
            {
                "status": "handoff-recorded",
                "required": True,
                "impl_status": "allowed",
                "chosen_next_step": "hitl",
            },
            False,
        ),
        ({"status": "future-state", "required": False}, False),
        ({"status": "handoff-recorded", "required": True}, False),
        (None, False),
    ],
)
def test_run_slice_closeout_applies_complete_risk_state_mapping_without_keyerror(
    monkeypatch: pytest.MonkeyPatch, plan: object, allowed: bool
) -> None:
    seen: dict[str, object] = {}
    emitted: list[dict[str, object]] = []

    def fake_plan(_repo_root: Path, paths: list[str]) -> object:
        seen["paths"] = paths
        return plan

    def fake_emit(payload: dict[str, object], *, stderr_message: str | None = None) -> int:
        emitted.append(payload)
        return 1

    monkeypatch.setattr(closeout, "plan_risk_interrupt", fake_plan)
    monkeypatch.setattr(closeout, "_emit_payload", fake_emit)
    payload: dict[str, object] = {"changed_paths": ["src/planned.py"]}
    risk_paths = ["src/actual.py"]

    result = closeout._maybe_block_on_risk_interrupt(Path("."), payload, risk_paths)

    assert seen["paths"] == risk_paths
    assert payload["risk_interrupt_paths"] == risk_paths
    assert payload["risk_interrupt_plan"] is plan
    if allowed:
        assert result is None
        assert emitted == []
    else:
        assert result == 1
        assert payload["status"] == "blocked"
        assert isinstance(payload["error"], str)
        assert emitted == [payload]


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
    write_surface_manifest(
        repo,
        demo_surface(
            source_paths=[
                "README.md",
                "charness-artifacts/debug/latest.md",
                "charness-artifacts/spec/*.md",
            ],
        ),
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
                "disconfirmer: cheapest refutation run before the fix",
                "",
                "## Verification",
                "",
                "verification",
                "",
                "## Root Cause",
                "",
                "root cause",
                "",
                "## Invariant Proof",
                "",
                "- Invariant: n/a - not a workflow-boundary propagation bug",
                "- Producer Proof: n/a",
                "- Final-Consumer Proof: n/a",
                "- Interface-Shape Sibling Scan: n/a",
                "- Non-Claims: n/a",
                "",
                "## Detection Gap",
                "",
                "- no gate observed this class",
                "",
                "## Sibling Search",
                "",
                "- cross-file: scripts/other.py - same mental model",
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
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)

    result = run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(repo),
        "--paths",
        "README.md",
        "charness-artifacts/debug/latest.md",
    )
    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["risk_interrupt_plan"]["status"] == "blocked"


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


@pytest.mark.parametrize(
    "script_path",
    ["scripts/run_slice_closeout.py", "plugins/charness/scripts/run_slice_closeout.py"],
)
def test_run_slice_closeout_risk_paths_ignore_paths_override(
    tmp_path: Path, script_path: str
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".agents").mkdir()
    (repo / "charness-artifacts" / "debug").mkdir(parents=True)
    (repo / "charness-artifacts" / "spec").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / ".agents" / "surfaces.json").write_text(
        json.dumps({"version": 1, "surfaces": [demo_surface()]}) + "\n",
        encoding="utf-8",
    )
    (repo / ".agents" / "debug-adapter.yaml").write_text(
        "version: 1\nrepo: demo\nlanguage: en\noutput_dir: charness-artifacts/debug\n",
        encoding="utf-8",
    )
    _git(repo, "init")
    _git(repo, "add", "README.md", ".agents")
    _git(repo, "-c", "user.email=test@example.com", "-c", "user.name=Test", "commit", "-m", "base")

    (repo / "charness-artifacts" / "debug" / "latest.md").write_text(
        "\n".join(
            [
                "# Debug Review",
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
            ]
        ),
        encoding="utf-8",
    )
    (repo / "charness-artifacts" / "spec" / "interrupt-demo.md").write_text(
        "# Incomplete handoff\n", encoding="utf-8"
    )

    result = run_script(
        script_path,
        "--repo-root",
        str(repo),
        "--paths",
        "README.md",
        "--skip-sync",
        "--skip-verify",
        "--plan-only",
    )

    assert result.returncode == 1, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["changed_paths"] == ["README.md"]
    assert set(payload["risk_interrupt_paths"]) >= {
        "charness-artifacts/debug/latest.md",
        "charness-artifacts/spec/interrupt-demo.md",
    }
    assert payload["risk_interrupt_plan"]["status"] == "blocked"
    assert payload["status"] == "blocked"


@pytest.mark.parametrize(
    "script_path",
    ["scripts/run_slice_closeout.py", "plugins/charness/scripts/run_slice_closeout.py"],
)
def test_run_slice_closeout_non_git_observation_fails_closed_on_global_interrupt(
    tmp_path: Path, script_path: str
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".agents").mkdir()
    (repo / "charness-artifacts" / "debug").mkdir(parents=True)
    (repo / "charness-artifacts" / "spec").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    write_surface_manifest(repo, demo_surface())
    (repo / ".agents" / "debug-adapter.yaml").write_text(
        "version: 1\nrepo: demo\nlanguage: en\noutput_dir: charness-artifacts/debug\n",
        encoding="utf-8",
    )
    (repo / "charness-artifacts" / "debug" / "latest.md").write_text(
        "\n".join(
            [
                "# Debug Review", "", "## Seam Risk", "", "- Interrupt ID: no-git-seam",
                "- Risk Class: host-disproves-local", "- Seam: missing-git-observer",
                "- Disproving Observation: Git path observation is unavailable",
                "- What Local Reasoning Cannot Prove: actual changed paths",
                "- Generalization Pressure: factor-now", "", "## Interrupt Decision", "",
                "- Critique Required: yes", "- Next Step: spec",
                "- Handoff Artifact: charness-artifacts/spec/no-git-seam.md", "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "charness-artifacts" / "spec" / "no-git-seam.md").write_text(
        "# Incomplete handoff\n", encoding="utf-8"
    )

    result = run_script(
        script_path, "--repo-root", str(repo), "--paths", "README.md",
        "--skip-sync", "--skip-verify", "--plan-only",
    )

    assert result.returncode == 1, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["risk_interrupt_path_observations"][0]["status"] == "unavailable"
    assert payload["risk_interrupt_paths"] == []
    assert payload["risk_interrupt_plan"]["status"] == "blocked"
    assert payload["status"] == "blocked"


@pytest.mark.parametrize(
    "script_path",
    ["scripts/run_slice_closeout.py", "plugins/charness/scripts/run_slice_closeout.py"],
)
def test_run_slice_closeout_rechecks_risk_paths_created_by_sync(
    tmp_path: Path, script_path: str
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".agents").mkdir()
    (repo / "scripts").mkdir()
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / ".agents" / "surfaces.json").write_text(
        json.dumps(
            {
                "version": 1,
                "surfaces": [
                    demo_surface(sync_commands=["python3 scripts/create_interrupt.py"])
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / ".agents" / "debug-adapter.yaml").write_text(
        "version: 1\nrepo: demo\nlanguage: en\noutput_dir: charness-artifacts/debug\n",
        encoding="utf-8",
    )
    (repo / "scripts" / "create_interrupt.py").write_text(
        "\n".join(
            [
                "from pathlib import Path",
                "debug = Path('charness-artifacts/debug')",
                "spec = Path('charness-artifacts/spec')",
                "debug.mkdir(parents=True)",
                "spec.mkdir(parents=True)",
                "(debug / 'latest.md').write_text('''# Debug Review",
                "",
                "## Seam Risk",
                "",
                "- Interrupt ID: sync-seam",
                "- Risk Class: host-disproves-local",
                "- Seam: sync-created-output",
                "- Disproving Observation: sync created a new risk path",
                "- What Local Reasoning Cannot Prove: final generated bytes",
                "- Generalization Pressure: factor-now",
                "",
                "## Interrupt Decision",
                "",
                "- Critique Required: yes",
                "- Next Step: spec",
                "- Handoff Artifact: charness-artifacts/spec/sync-seam.md",
                "''', encoding='utf-8')",
                "(spec / 'sync-seam.md').write_text('# Incomplete handoff\\n', encoding='utf-8')",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    _git(repo, "init")
    _git(repo, "add", "README.md", ".agents", "scripts")
    _git(repo, "-c", "user.email=test@example.com", "-c", "user.name=Test", "commit", "-m", "base")

    result = run_script(
        script_path,
        "--repo-root",
        str(repo),
        "--paths",
        "README.md",
        "--skip-verify",
    )

    assert result.returncode == 1, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["changed_paths"] == ["README.md"]
    assert [step["phase"] for step in payload["executed_commands"]] == ["sync"]
    assert set(payload["risk_interrupt_paths"]) >= {
        "charness-artifacts/debug/latest.md",
        "charness-artifacts/spec/sync-seam.md",
    }
    assert payload["risk_interrupt_plan"]["status"] == "blocked"
    assert payload["status"] == "blocked"
