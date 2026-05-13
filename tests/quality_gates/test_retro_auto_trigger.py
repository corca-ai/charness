from __future__ import annotations

import json
from pathlib import Path

from .support import ROOT, run_script


def test_retro_auto_trigger_hits_configured_install_surface() -> None:
    result = run_script(
        "skills/public/retro/scripts/check_auto_trigger.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "README.md",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["triggered"] is True
    assert "checked-in-plugin-export" in payload["surface_hits"]


def test_retro_auto_trigger_skips_non_matching_slice() -> None:
    result = run_script(
        "skills/public/retro/scripts/check_auto_trigger.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "docs/retro-self-improvement-spec.md",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["triggered"] is False
    assert payload["surface_hits"] == []
    assert payload["path_hits"] == []


def test_retro_auto_trigger_skips_missing_surfaces_when_no_trigger_config(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "retro-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: consumer",
                "output_dir: charness-artifacts/retro",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/retro/scripts/check_auto_trigger.py",
        "--repo-root",
        str(repo),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["triggered"] is False
    assert payload["reason"] == "No auto-retro trigger surfaces or path globs are configured."
    assert payload["configuration_status"] == "missing"
    assert "intentional opt-out" in payload["remediation"]
    assert payload["surface_hits"] == []
    assert payload["path_hits"] == []


def test_retro_auto_trigger_distinguishes_intentional_empty_trigger_config(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "retro-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: consumer",
                "output_dir: charness-artifacts/retro",
                "auto_session_trigger_surfaces: []",
                "auto_session_trigger_path_globs: []",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/retro/scripts/check_auto_trigger.py",
        "--repo-root",
        str(repo),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["triggered"] is False
    assert payload["configuration_status"] == "intentional-empty"
    assert payload["reason"] == "Auto-retro trigger surfaces and path globs are explicitly empty."
    assert "remediation" not in payload


def test_retro_auto_trigger_clean_changeset_does_not_trigger() -> None:
    result = run_script(
        "skills/public/retro/scripts/check_auto_trigger.py",
        "--repo-root",
        str(ROOT),
        "--paths",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["triggered"] is False
    assert payload["changed_paths"] == []
    assert payload["surface_hits"] == []
    assert payload["path_hits"] == []


def test_retro_auto_trigger_fails_loud_on_unresolved_surface_id(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "retro-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: consumer",
                "output_dir: charness-artifacts/retro",
                "auto_session_trigger_surfaces:",
                "  - release-packagng",
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
                        "surface_id": "release-packaging",
                        "description": "release packaging surface",
                        "source_paths": ["scripts/release/**"],
                        "derived_paths": ["dist/**"],
                        "sync_commands": [],
                        "verify_commands": [],
                        "notes": [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/retro/scripts/check_auto_trigger.py",
        "--repo-root",
        str(repo),
        "--paths",
        "scripts/release/verify-public-release.mjs",
    )

    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    payload = json.loads(result.stderr)
    assert payload["triggered"] is False
    assert payload["configuration_status"] == "broken"
    assert payload["unresolved_trigger_surfaces"] == ["release-packagng"]
    assert "auto_session_trigger_surfaces" in payload["reason"]
    assert "Fix the typo" in payload["remediation"]


def test_retro_auto_trigger_reports_missing_surfaces_remediation_when_configured(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "retro-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: consumer",
                "output_dir: charness-artifacts/retro",
                "auto_session_trigger_surfaces:",
                "  - checked-in-plugin-export",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/retro/scripts/check_auto_trigger.py",
        "--repo-root",
        str(repo),
        "--paths",
        "README.md",
    )

    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    payload = json.loads(result.stderr)
    assert payload["triggered"] is False
    assert "missing surfaces manifest" in payload["error"]
    assert ".agents/surfaces.json" in payload["remediation"]
