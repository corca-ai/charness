from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .release_publish_fixtures import _release_env, _run_publish_patch, _seed_publish_release_repo


def _configure_retro_trigger(repo: Path, *, surface_id: str, source_paths: list[str]) -> None:
    (repo / ".agents" / "retro-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "output_dir: charness-artifacts/retro",
                "summary_path: charness-artifacts/retro/recent-lessons.md",
                "auto_session_trigger_surfaces:",
                f"  - {surface_id}",
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
                        "surface_id": surface_id,
                        "description": surface_id,
                        "source_paths": source_paths,
                        "derived_paths": [],
                        "sync_commands": [],
                        "verify_commands": [],
                        "notes": [],
                    }
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_publish_release_records_retro_trigger_evaluation_from_release_delta(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    _configure_retro_trigger(repo, surface_id="operator-docs", source_paths=["README.md"])
    (repo / "README.md").write_text("# Demo\n\nRelease operator note.\n", encoding="utf-8")
    subprocess.run(
        ["git", "add", ".agents/retro-adapter.yaml", ".agents/surfaces.json", "README.md"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Update release operator docs"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )

    env = _release_env(tmp_path, bin_dir)
    result = _run_publish_patch(repo, env)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    retro_payload = payload["retro_trigger_evaluation"]
    assert retro_payload["triggered"] is True
    assert retro_payload["evaluated_at"] == "final_release_paths"
    assert retro_payload["closeout"]["status"] == "written"
    assert Path(repo, retro_payload["closeout"]["artifact_path"]).is_file()
    assert retro_payload["input"]["mode"] == "explicit_paths"
    assert retro_payload["surface_hits"] == ["operator-docs"]
    assert "README.md" in retro_payload["changed_paths"]
    artifact_text = (repo / "charness-artifacts" / "release" / "latest.md").read_text(encoding="utf-8")
    assert "## Retro Trigger Evaluation" in artifact_text
    assert "Triggered: `True`." in artifact_text
    assert "Closeout status: `written`." in artifact_text
    assert "`operator-docs`" in artifact_text
    assert "`README.md`" in artifact_text


def test_publish_release_retro_trigger_includes_helper_generated_release_paths(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    _configure_retro_trigger(repo, surface_id="release-packaging", source_paths=["packaging/**"])
    subprocess.run(
        ["git", "add", ".agents/retro-adapter.yaml", ".agents/surfaces.json"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Configure retro release trigger"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )

    env = _release_env(tmp_path, bin_dir)
    result = _run_publish_patch(repo, env)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    retro_payload = payload["retro_trigger_evaluation"]
    assert retro_payload["triggered"] is True
    assert retro_payload["surface_hits"] == ["release-packaging"]
    assert "packaging/demo.json" in retro_payload["changed_paths"]
    assert retro_payload["closeout"]["status"] == "written"
    artifact_path = repo / retro_payload["closeout"]["artifact_path"]
    assert artifact_path.is_file()
    assert "Release publish triggered a configured automatic session retro" in artifact_path.read_text(
        encoding="utf-8"
    )
