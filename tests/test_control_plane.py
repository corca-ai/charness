from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_script(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", *args],
        cwd=cwd or ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def seed_control_plane_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    tools_dir = repo / "integrations" / "tools"
    locks_dir = repo / "integrations" / "locks"
    generated_dir = repo / "skills" / "support" / "generated"
    bin_dir = repo / "bin"
    tools_dir.mkdir(parents=True)
    locks_dir.mkdir(parents=True)
    generated_dir.mkdir(parents=True)
    bin_dir.mkdir(parents=True)

    (tools_dir / "manifest.schema.json").write_text(
        (ROOT / "integrations" / "tools" / "manifest.schema.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (bin_dir / "demo-tool").write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                'case \"${1:-}\" in',
                '  version) echo \"demo-tool 1.2.3\" ;;',
                '  help) echo \"demo-tool help\" ;;',
                '  update) echo \"updated\" ;;',
                '  *) echo \"demo-tool\" ;;',
                "esac",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (bin_dir / "demo-tool").chmod(0o755)
    (tools_dir / "demo-tool.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": "demo-tool",
                "kind": "external_binary_with_skill",
                "display_name": "demo-tool",
                "upstream_repo": "example/demo-tool",
                "homepage": "https://example.com/demo-tool",
                "lifecycle": {
                    "install": {"mode": "manual"},
                    "update": {
                        "mode": "script",
                        "commands": ["./bin/demo-tool update"],
                    },
                },
                "checks": {
                    "detect": {
                        "commands": ["./bin/demo-tool version"],
                        "success_criteria": ["exit_code:0", "stdout_contains:1.2.3"],
                    },
                    "healthcheck": {
                        "commands": ["./bin/demo-tool help"],
                        "success_criteria": ["exit_code:0", "stdout_contains:help"],
                    },
                },
                "access_modes": ["binary", "degraded"],
                "version_expectation": {
                    "policy": "minimum",
                    "constraint": ">=1.0.0",
                    "detected_by": "stdout",
                },
                "support_skill_source": {
                    "source_type": "local_wrapper",
                    "path": "docs/demo-tool-upstream.md",
                    "ref": "main",
                    "sync_strategy": "generated_wrapper",
                    "wrapper_skill_id": "demo-tool-wrapper",
                },
                "degradation": {"when_missing": ["manual fallback"]},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return repo


def test_validate_integrations_passes_on_current_repo() -> None:
    result = run_script("scripts/validate-integrations.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_validate_integrations_rejects_invalid_generated_wrapper(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    tools_dir = repo / "integrations" / "tools"
    tools_dir.mkdir(parents=True)
    (tools_dir / "manifest.schema.json").write_text(
        (ROOT / "integrations" / "tools" / "manifest.schema.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tools_dir / "bad.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": "bad",
                "kind": "external_skill",
                "display_name": "bad",
                "upstream_repo": "example/bad",
                "homepage": "https://example.com/bad",
                "lifecycle": {"install": {"mode": "manual"}, "update": {"mode": "manual"}},
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
                    "sync_strategy": "generated_wrapper",
                },
            }
        ),
        encoding="utf-8",
    )
    result = run_script("scripts/validate-integrations.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "generated_wrapper requires wrapper_skill_id" in result.stderr


def test_validate_integrations_rejects_unsorted_access_modes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    tools_dir = repo / "integrations" / "tools"
    tools_dir.mkdir(parents=True)
    (tools_dir / "manifest.schema.json").write_text(
        (ROOT / "integrations" / "tools" / "manifest.schema.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
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
    tools_dir = repo / "integrations" / "tools"
    tools_dir.mkdir(parents=True)
    (tools_dir / "manifest.schema.json").write_text(
        (ROOT / "integrations" / "tools" / "manifest.schema.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
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


def test_doctor_sync_and_update_work_on_seed_repo(tmp_path: Path) -> None:
    repo = seed_control_plane_repo(tmp_path)

    doctor = run_script("scripts/doctor.py", "--repo-root", str(repo), "--json", "--write-locks")
    assert doctor.returncode == 0, doctor.stderr
    doctor_payload = json.loads(doctor.stdout)
    assert doctor_payload[0]["tool_id"] == "demo-tool"
    assert doctor_payload[0]["kind"] == "external_binary_with_skill"
    assert doctor_payload[0]["access_modes"] == ["binary", "degraded"]
    assert doctor_payload[0]["capability_requirements"] == {}
    assert doctor_payload[0]["doctor_status"] == "ok"
    assert doctor_payload[0]["support_state"] == "wrapped-upstream"
    assert doctor_payload[0]["support_sync"]["status"] == "not-tracked"

    sync = run_script("scripts/sync_support.py", "--repo-root", str(repo), "--execute", "--json")
    assert sync.returncode == 0, sync.stderr
    sync_payload = json.loads(sync.stdout)
    assert sync_payload[0]["status"] == "synced"
    generated_skill = repo / "skills" / "support" / "generated" / "demo-tool-wrapper" / "SKILL.md"
    assert generated_skill.exists()

    update = run_script("scripts/update_tools.py", "--repo-root", str(repo), "--execute", "--json")
    assert update.returncode == 0, update.stderr
    update_payload = json.loads(update.stdout)
    assert update_payload[0]["status"] == "updated"

    lock_path = repo / "integrations" / "locks" / "demo-tool.json"
    assert lock_path.exists()
    lock_payload = json.loads(lock_path.read_text(encoding="utf-8"))
    assert lock_payload["support"]["sync_strategy"] == "generated_wrapper"
    assert lock_payload["doctor"]["doctor_status"] == "ok"
    assert lock_payload["doctor"]["support_sync"]["status"] == "not-tracked"
    assert lock_payload["update"]["update_status"] == "updated"


def test_doctor_detects_missing_materialized_support_from_previous_sync(tmp_path: Path) -> None:
    repo = seed_control_plane_repo(tmp_path)

    sync = run_script("scripts/sync_support.py", "--repo-root", str(repo), "--execute", "--json")
    assert sync.returncode == 0, sync.stderr

    generated_skill = repo / "skills" / "support" / "generated" / "demo-tool-wrapper" / "SKILL.md"
    assert generated_skill.exists()
    generated_skill.unlink()

    doctor = run_script("scripts/doctor.py", "--repo-root", str(repo), "--json", "--write-locks")
    assert doctor.returncode == 1, doctor.stderr
    doctor_payload = json.loads(doctor.stdout)
    assert doctor_payload[0]["doctor_status"] == "support-missing"
    assert doctor_payload[0]["support_sync"]["status"] == "missing"
    assert doctor_payload[0]["support_sync"]["missing_paths"] == [
        "skills/support/generated/demo-tool-wrapper/SKILL.md"
    ]


def test_sync_support_reference_materializes_reference_artifact_and_lock(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    tools_dir = repo / "integrations" / "tools"
    locks_dir = repo / "integrations" / "locks"
    generated_dir = repo / "skills" / "support" / "generated"
    tools_dir.mkdir(parents=True)
    locks_dir.mkdir(parents=True)
    generated_dir.mkdir(parents=True)

    (tools_dir / "manifest.schema.json").write_text(
        (ROOT / "integrations" / "tools" / "manifest.schema.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tools_dir / "agent-browser.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": "agent-browser",
                "kind": "external_binary_with_skill",
                "display_name": "agent-browser",
                "upstream_repo": "vercel-labs/agent-browser",
                "homepage": "https://github.com/vercel-labs/agent-browser",
                "lifecycle": {"install": {"mode": "manual"}, "update": {"mode": "manual"}},
                "checks": {
                    "detect": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                },
                "access_modes": ["binary", "degraded"],
                "version_expectation": {"policy": "advisory", "constraint": "latest"},
                "support_skill_source": {
                    "source_type": "upstream_repo",
                    "path": "skills/agent-browser/SKILL.md",
                    "ref": "main",
                    "sync_strategy": "reference",
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    sync = run_script("scripts/sync_support.py", "--repo-root", str(repo), "--execute", "--json")
    assert sync.returncode == 0, sync.stderr
    sync_payload = json.loads(sync.stdout)
    assert sync_payload[0]["status"] == "synced"

    reference_path = repo / "skills" / "support" / "generated" / "agent-browser" / "REFERENCE.md"
    assert reference_path.exists()
    reference_text = reference_path.read_text(encoding="utf-8")
    assert "upstream repo: `vercel-labs/agent-browser`" in reference_text
    assert "sync strategy: `reference`" in reference_text

    lock_payload = json.loads((repo / "integrations" / "locks" / "agent-browser.json").read_text(encoding="utf-8"))
    assert lock_payload["support"]["sync_strategy"] == "reference"
    assert lock_payload["support"]["materialized_paths"] == ["skills/support/generated/agent-browser/REFERENCE.md"]
