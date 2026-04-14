from __future__ import annotations

import json
import os
from pathlib import Path

from .support import ROOT, run_script, seed_control_plane_repo


def write_manifest_schema(repo: Path) -> Path:
    tools_dir = repo / "integrations" / "tools"
    tools_dir.mkdir(parents=True, exist_ok=True)
    (tools_dir / "manifest.schema.json").write_text(
        (ROOT / "integrations" / "tools" / "manifest.schema.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    return tools_dir
def test_validate_integrations_rejects_invalid_local_wrapper(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    tools_dir = write_manifest_schema(repo)
    (tools_dir / "bad.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": "bad",
                "kind": "external_skill",
                "display_name": "bad",
                "upstream_repo": "example/bad",
                "homepage": "https://example.com/bad",
                "lifecycle": {
                    "install": {"mode": "manual", "install_url": "https://example.com/bad/install"},
                    "update": {"mode": "manual"},
                },
                "checks": {
                    "detect": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                },
                "access_modes": ["binary"],
                "version_expectation": {"policy": "advisory", "constraint": "latest"},
                "support_skill_source": {
                    "source_type": "local_wrapper",
                    "path": "docs/bad.md",
                    "ref": "main",
                },
            }
        ),
        encoding="utf-8",
    )
    result = run_script("scripts/validate-integrations.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "local_wrapper requires wrapper_skill_id" in result.stderr


def test_validate_integrations_requires_install_entrypoint_for_support_backed_tools(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    tools_dir = write_manifest_schema(repo)
    (tools_dir / "missing-install-url.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": "missing-install-url",
                "kind": "external_binary_with_skill",
                "display_name": "missing-install-url",
                "upstream_repo": "example/missing-install-url",
                "homepage": "https://example.com/missing-install-url",
                "lifecycle": {"install": {"mode": "manual"}, "update": {"mode": "manual"}},
                "checks": {
                    "detect": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                },
                "access_modes": ["binary"],
                "version_expectation": {"policy": "advisory", "constraint": "latest"},
                "support_skill_source": {
                    "source_type": "upstream_repo",
                    "path": "skills/missing-install-url",
                    "ref": "main",
                },
            }
        ),
        encoding="utf-8",
    )
    result = run_script("scripts/validate-integrations.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "must declare lifecycle.install.install_url" in result.stderr


def test_validate_integrations_rejects_unsorted_access_modes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    tools_dir = write_manifest_schema(repo)
    (tools_dir / "bad-order.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": "bad-order",
                "kind": "external_binary",
                "display_name": "bad-order",
                "upstream_repo": "example/bad-order",
                "homepage": "https://example.com/bad-order",
                "lifecycle": {"install": {"mode": "manual"}, "update": {"mode": "manual"}},
                "checks": {
                    "detect": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                },
                "access_modes": ["env", "binary", "degraded"],
                "version_expectation": {"policy": "advisory", "constraint": "latest"},
            }
        ),
        encoding="utf-8",
    )
    result = run_script("scripts/validate-integrations.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "access_modes must stay in preferred runtime order" in result.stderr


def test_validate_integrations_requires_capability_requirements_for_grant_and_env(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    tools_dir = write_manifest_schema(repo)
    (tools_dir / "grant-env.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": "grant-env",
                "kind": "external_binary",
                "display_name": "grant-env",
                "upstream_repo": "example/grant-env",
                "homepage": "https://example.com/grant-env",
                "lifecycle": {"install": {"mode": "manual"}, "update": {"mode": "manual"}},
                "checks": {
                    "detect": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                },
                "access_modes": ["grant", "env", "degraded"],
                "version_expectation": {"policy": "advisory", "constraint": "latest"},
            }
        ),
        encoding="utf-8",
    )
    result = run_script("scripts/validate-integrations.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "grant access requires capability_requirements.grant_ids" in result.stderr


def test_validate_integrations_rejects_unsorted_config_layers(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    tools_dir = write_manifest_schema(repo)
    (tools_dir / "bad-layers.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": "bad-layers",
                "kind": "external_binary",
                "display_name": "bad-layers",
                "upstream_repo": "example/bad-layers",
                "homepage": "https://example.com/bad-layers",
                "lifecycle": {"install": {"mode": "manual"}, "update": {"mode": "manual"}},
                "checks": {
                    "detect": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                },
                "access_modes": ["grant", "env", "degraded"],
                "capability_requirements": {"grant_ids": ["demo.grant"], "env_vars": ["DEMO_TOKEN"]},
                "config_layers": [
                    {"layer_id": "env-fallback", "layer_type": "env", "summary": "Use env fallback."},
                    {"layer_id": "grant-first", "layer_type": "grant", "summary": "Use runtime grant first."},
                ],
                "version_expectation": {"policy": "advisory", "constraint": "latest"},
            }
        ),
        encoding="utf-8",
    )
    result = run_script("scripts/validate-integrations.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "config_layers must stay in preferred order" in result.stderr


def test_doctor_detects_missing_materialized_support_from_previous_sync(tmp_path: Path) -> None:
    repo = seed_control_plane_repo(tmp_path)
    env = os.environ.copy()
    env["CHARNESS_CACHE_HOME"] = str(tmp_path / "cache-home")
    sync = run_script("scripts/sync_support.py", "--repo-root", str(repo), "--execute", "--json", env=env)
    assert sync.returncode == 0, sync.stderr
    generated_skill_root = repo / "skills" / "support" / "generated" / "demo-tool-wrapper"
    generated_skill_root.unlink()

    doctor = run_script("scripts/doctor.py", "--repo-root", str(repo), "--json", "--write-locks")
    assert doctor.returncode == 1, doctor.stderr
    doctor_payload = json.loads(doctor.stdout)
    assert doctor_payload[0]["doctor_status"] == "support-missing"
    assert doctor_payload[0]["support_sync"]["status"] == "missing"
    assert doctor_payload[0]["support_sync"]["missing_paths"] == ["skills/support/generated/demo-tool-wrapper"]
    assert doctor_payload[0]["support_sync"]["action_required"] is True
    assert doctor_payload[0]["support_sync"]["suggested_command"] == "charness tool sync-support demo-tool"
    assert "Previously materialized support skill paths are missing." in doctor_payload[0]["next_steps"][0]


def test_doctor_reports_not_ready_when_readiness_check_fails(tmp_path: Path) -> None:
    repo = seed_control_plane_repo(tmp_path)
    (repo / ".demo-ready").unlink()

    doctor = run_script("scripts/doctor.py", "--repo-root", str(repo), "--json", "--write-locks")
    assert doctor.returncode == 1, doctor.stderr
    doctor_payload = json.loads(doctor.stdout)
    assert doctor_payload[0]["doctor_status"] == "not-ready"
    payload = doctor_payload[0]["readiness"]
    assert payload["ok"] is False
    assert payload["failed_checks"] == ["demo-ready-file"]


def test_doctor_reads_support_owned_capability_metadata(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    support_dir = repo / "skills" / "support" / "gather-slack"
    locks_dir = repo / "integrations" / "locks"
    support_dir.mkdir(parents=True)
    locks_dir.mkdir(parents=True)
    (support_dir / "SKILL.md").write_text(
        "\n".join(["---", "name: gather-slack", 'description: "Slack runtime."', "---", "", "# Gather Slack"]) + "\n",
        encoding="utf-8",
    )
    (support_dir / "capability.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "capability_id": "gather-slack",
                "kind": "support_runtime",
                "display_name": "Slack gather",
                "summary": "Support-owned Slack runtime.",
                "support_skill_path": "skills/support/gather-slack/SKILL.md",
                "supports_public_skills": ["gather"],
                "checks": {
                    "detect": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                },
                "access_modes": ["grant", "env", "degraded"],
                "capability_requirements": {"grant_ids": ["slack.history"], "env_vars": ["SLACK_BOT_TOKEN"]},
                "config_layers": [
                    {"layer_id": "slack-grant", "layer_type": "grant", "summary": "Prefer runtime grant first."},
                    {"layer_id": "slack-env", "layer_type": "env", "summary": "Fallback to env."},
                ],
                "readiness_checks": [{"check_id": "slack-ready", "summary": "Slack runtime is ready.", "commands": ["true"], "success_criteria": ["exit_code:0"]}],
                "version_expectation": {"policy": "advisory", "constraint": "local"},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    doctor = run_script("scripts/doctor.py", "--repo-root", str(repo), "--json", "--write-locks")
    assert doctor.returncode == 0, doctor.stderr
    payload = json.loads(doctor.stdout)
    assert payload[0]["tool_id"] == "gather-slack"
    assert payload[0]["kind"] == "support_runtime"
    assert payload[0]["support_state"] == "native-support"
    assert payload[0]["doctor_status"] == "ok"
    assert payload[0]["access_modes"] == ["grant", "env", "degraded"]

    lock_payload = json.loads((locks_dir / "gather-slack.json").read_text(encoding="utf-8"))
    assert lock_payload["manifest_path"] == "skills/support/gather-slack/capability.json"
    assert lock_payload["doctor"]["kind"] == "support_runtime"
