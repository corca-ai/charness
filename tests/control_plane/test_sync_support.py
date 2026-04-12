from __future__ import annotations

import json
from pathlib import Path

from .support import ROOT, run_script, seed_control_plane_repo


def test_doctor_sync_and_update_work_on_seed_repo(tmp_path: Path) -> None:
    repo = seed_control_plane_repo(tmp_path)
    doctor = run_script("scripts/doctor.py", "--repo-root", str(repo), "--json", "--write-locks")
    assert doctor.returncode == 0, doctor.stderr
    doctor_payload = json.loads(doctor.stdout)
    assert doctor_payload[0]["tool_id"] == "demo-tool"
    assert doctor_payload[0]["kind"] == "external_binary_with_skill"
    assert doctor_payload[0]["access_modes"] == ["binary", "degraded"]
    assert doctor_payload[0]["capability_requirements"] == {}
    assert doctor_payload[0]["readiness"]["ok"] is True
    assert doctor_payload[0]["readiness"]["failed_checks"] == []
    assert doctor_payload[0]["doctor_status"] == "ok"
    assert doctor_payload[0]["support_state"] == "wrapped-upstream"
    assert doctor_payload[0]["support_sync"]["status"] == "not-tracked"

    sync = run_script("scripts/sync_support.py", "--repo-root", str(repo), "--execute", "--json")
    assert sync.returncode == 0, sync.stderr
    assert json.loads(sync.stdout)[0]["status"] == "synced"
    generated_skill = repo / "skills" / "support" / "generated" / "demo-tool-wrapper" / "SKILL.md"
    assert generated_skill.exists()

    update = run_script("scripts/update_tools.py", "--repo-root", str(repo), "--execute", "--json")
    assert update.returncode == 0, update.stderr
    assert json.loads(update.stdout)[0]["status"] == "updated"

    lock_payload = json.loads((repo / "integrations" / "locks" / "demo-tool.json").read_text(encoding="utf-8"))
    assert lock_payload["support"]["sync_strategy"] == "generated_wrapper"
    assert lock_payload["doctor"]["doctor_status"] == "ok"
    assert lock_payload["doctor"]["readiness"]["ok"] is True
    assert lock_payload["doctor"]["support_sync"]["status"] == "not-tracked"
    assert lock_payload["update"]["update_status"] == "updated"


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
                    "notes": ["Use the upstream browser debugging guidance directly."],
                },
                "config_layers": [
                    {"layer_id": "authenticated-binary", "layer_type": "authenticated-binary", "summary": "Use the installed browser CLI directly."}
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    sync = run_script("scripts/sync_support.py", "--repo-root", str(repo), "--execute", "--json")
    assert sync.returncode == 0, sync.stderr
    assert json.loads(sync.stdout)[0]["status"] == "synced"

    reference_path = repo / "skills" / "support" / "generated" / "agent-browser" / "REFERENCE.md"
    assert reference_path.exists()
    reference_text = reference_path.read_text(encoding="utf-8")
    assert "upstream repo: `vercel-labs/agent-browser`" in reference_text
    assert "sync strategy: `reference`" in reference_text
    assert "## Reuse Notes" in reference_text
    assert "Use the upstream browser debugging guidance directly." in reference_text
    assert "## Config Layers" in reference_text
    assert "`authenticated-binary`: Use the installed browser CLI directly." in reference_text

    lock_payload = json.loads((repo / "integrations" / "locks" / "agent-browser.json").read_text(encoding="utf-8"))
    assert lock_payload["support"]["sync_strategy"] == "reference"
    assert lock_payload["support"]["materialized_paths"] == ["skills/support/generated/agent-browser/REFERENCE.md"]


def test_sync_support_copy_materializes_upstream_checkout(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    upstream = tmp_path / "upstream"
    tools_dir = repo / "integrations" / "tools"
    locks_dir = repo / "integrations" / "locks"
    generated_dir = repo / "skills" / "support" / "generated"
    tools_dir.mkdir(parents=True)
    locks_dir.mkdir(parents=True)
    generated_dir.mkdir(parents=True)
    (upstream / "skills" / "demo-copy").mkdir(parents=True)
    (upstream / "skills" / "demo-copy" / "SKILL.md").write_text("# demo\n", encoding="utf-8")
    (upstream / "skills" / "demo-copy" / "helper.sh").write_text("echo demo\n", encoding="utf-8")

    (tools_dir / "manifest.schema.json").write_text(
        (ROOT / "integrations" / "tools" / "manifest.schema.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tools_dir / "demo-copy.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": "demo-copy",
                "kind": "external_skill",
                "display_name": "demo-copy",
                "upstream_repo": "example/demo-copy",
                "homepage": "https://example.com/demo-copy",
                "lifecycle": {"install": {"mode": "manual"}, "update": {"mode": "manual"}},
                "checks": {
                    "detect": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                },
                "access_modes": ["binary"],
                "version_expectation": {"policy": "advisory", "constraint": "latest"},
                "support_skill_source": {
                    "source_type": "upstream_repo",
                    "path": "skills/demo-copy",
                    "ref": "main",
                    "sync_strategy": "copy",
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    sync = run_script(
        "scripts/sync_support.py",
        "--repo-root",
        str(repo),
        "--execute",
        "--upstream-checkout",
        f"example/demo-copy={upstream}",
        "--json",
    )
    assert sync.returncode == 0, sync.stderr
    assert json.loads(sync.stdout)[0]["materialized_paths"] == ["skills/support/generated/demo-copy"]
    assert (repo / "skills" / "support" / "generated" / "demo-copy" / "SKILL.md").exists()
    assert (repo / "skills" / "support" / "generated" / "demo-copy" / "helper.sh").exists()


def test_sync_support_symlink_materializes_upstream_checkout(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    upstream = tmp_path / "upstream"
    tools_dir = repo / "integrations" / "tools"
    locks_dir = repo / "integrations" / "locks"
    generated_dir = repo / "skills" / "support" / "generated"
    tools_dir.mkdir(parents=True)
    locks_dir.mkdir(parents=True)
    generated_dir.mkdir(parents=True)
    (upstream / "skills" / "demo-link").mkdir(parents=True)
    (upstream / "skills" / "demo-link" / "SKILL.md").write_text("# demo-link\n", encoding="utf-8")

    (tools_dir / "manifest.schema.json").write_text(
        (ROOT / "integrations" / "tools" / "manifest.schema.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tools_dir / "demo-link.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": "demo-link",
                "kind": "external_skill",
                "display_name": "demo-link",
                "upstream_repo": "example/demo-link",
                "homepage": "https://example.com/demo-link",
                "lifecycle": {"install": {"mode": "manual"}, "update": {"mode": "manual"}},
                "checks": {
                    "detect": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                },
                "access_modes": ["binary"],
                "version_expectation": {"policy": "advisory", "constraint": "latest"},
                "support_skill_source": {
                    "source_type": "upstream_repo",
                    "path": "skills/demo-link",
                    "ref": "main",
                    "sync_strategy": "symlink",
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    sync = run_script(
        "scripts/sync_support.py",
        "--repo-root",
        str(repo),
        "--execute",
        "--upstream-checkout",
        f"example/demo-link={upstream}",
        "--json",
    )
    assert sync.returncode == 0, sync.stderr
    link_root = repo / "skills" / "support" / "generated" / "demo-link"
    assert link_root.is_symlink()
    assert link_root.resolve() == (upstream / "skills" / "demo-link").resolve()


def test_sync_support_local_dev_symlink_overrides_copy_manifest(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    upstream = tmp_path / "upstream"
    tools_dir = repo / "integrations" / "tools"
    locks_dir = repo / "integrations" / "locks"
    generated_dir = repo / "skills" / "support" / "generated"
    tools_dir.mkdir(parents=True)
    locks_dir.mkdir(parents=True)
    generated_dir.mkdir(parents=True)
    (upstream / "skills" / "demo-copy").mkdir(parents=True)
    (upstream / "skills" / "demo-copy" / "SKILL.md").write_text("# demo-copy\n", encoding="utf-8")

    (tools_dir / "manifest.schema.json").write_text(
        (ROOT / "integrations" / "tools" / "manifest.schema.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (tools_dir / "demo-copy.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": "demo-copy",
                "kind": "external_skill",
                "display_name": "demo-copy",
                "upstream_repo": "example/demo-copy",
                "homepage": "https://example.com/demo-copy",
                "lifecycle": {"install": {"mode": "manual"}, "update": {"mode": "manual"}},
                "checks": {
                    "detect": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                },
                "access_modes": ["binary"],
                "version_expectation": {"policy": "advisory", "constraint": "latest"},
                "support_skill_source": {
                    "source_type": "upstream_repo",
                    "path": "skills/demo-copy",
                    "ref": "main",
                    "sync_strategy": "copy",
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    sync = run_script(
        "scripts/sync_support.py",
        "--repo-root",
        str(repo),
        "--execute",
        "--upstream-checkout",
        f"example/demo-copy={upstream}",
        "--local-dev-symlink",
        "--json",
    )
    assert sync.returncode == 0, sync.stderr
    assert json.loads(sync.stdout)[0]["sync_strategy"] == "symlink"
    link_root = repo / "skills" / "support" / "generated" / "demo-copy"
    assert link_root.is_symlink()
    assert link_root.resolve() == (upstream / "skills" / "demo-copy").resolve()
