from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

from .support import ROOT, run_script

_PLANNER_SPEC = importlib.util.spec_from_file_location(
    "plan_release_run",
    ROOT / "skills" / "public" / "release" / "scripts" / "plan_release_run.py",
)
assert _PLANNER_SPEC is not None and _PLANNER_SPEC.loader is not None
_PLANNER = importlib.util.module_from_spec(_PLANNER_SPEC)
_PLANNER_SPEC.loader.exec_module(_PLANNER)


def test_release_real_host_proof_triggers_for_support_tool_surfaces() -> None:
    result = run_script(
        "skills/public/release/scripts/check_real_host_proof.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "integrations/tools/tokei.json",
        "scripts/doctor.py",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["required"] is True
    assert "integrations-and-control-plane" in payload["surface_hits"]
    assert any("tool doctor" in item for item in payload["checklist"])
    assert any("tool install" in item for item in payload["checklist"])
    assert any("manifest-supported path" in item for item in payload["checklist"])


def test_release_real_host_proof_stays_off_for_unrelated_paths() -> None:
    result = run_script(
        "skills/public/release/scripts/check_real_host_proof.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "docs/retro-self-improvement-spec.md",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["required"] is False
    assert payload["checklist"] == []


def test_release_real_host_proof_clean_changeset_does_not_trigger() -> None:
    result = run_script(
        "skills/public/release/scripts/check_real_host_proof.py",
        "--repo-root",
        str(ROOT),
        "--paths",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["required"] is False
    assert payload["changed_paths"] == []
    assert payload["surface_hits"] == []
    assert payload["path_hits"] == []
    assert payload["checklist"] == []


def test_release_real_host_proof_fails_loud_on_unresolved_surface_id(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "release-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: consumer",
                "output_dir: charness-artifacts/release",
                "package_id: consumer",
                "packaging_manifest_path: packaging/consumer.json",
                "checked_in_plugin_root: plugins/consumer",
                "sync_command: true",
                "quality_command: true",
                "real_host_required_surfaces:",
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
        "skills/public/release/scripts/check_real_host_proof.py",
        "--repo-root",
        str(repo),
        "--paths",
        "scripts/release/verify-public-release.mjs",
    )

    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    payload = json.loads(result.stderr)
    assert payload["required"] is False
    assert payload["configuration_status"] == "broken"
    assert payload["unresolved_trigger_surfaces"] == ["release-packagng"]
    assert payload["checklist"] == []
    assert "real_host_required_surfaces" in payload["reason"]
    assert "Fix the typo" in payload["remediation"]


def test_release_skill_enforces_phase_barriers_for_mutating_commands() -> None:
    payload = _PLANNER.build_plan(
        SimpleNamespace(
            repo_root=ROOT,
            remote="origin",
            critique_artifact=None,
            critique_blocked=None,
            publish_current=False,
            part=None,
            set_version=None,
        )
    )

    assert "references/publication-boundary.md" in {item["path"] for item in payload["required_reads"]}
    assert any("publish-dry-run" in item and "publish-execute" in item for item in payload["phase_barriers"])
    assert any("parallelize" in item and "git" in item for item in payload["phase_barriers"])
    assert all({"id", "cost_tier", "trust_model", "run_when"} <= set(packet) for packet in payload["gate_packets"])
