from __future__ import annotations

import json
import os
from pathlib import Path

from .support import ROOT, run_script, seed_control_plane_repo


def write_manifest_schema(repo: Path) -> None:
    tools_dir = repo / "integrations" / "tools"
    tools_dir.mkdir(parents=True, exist_ok=True)
    (tools_dir / "manifest.schema.json").write_text(
        (ROOT / "integrations" / "tools" / "manifest.schema.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )


def test_doctor_sync_and_update_work_on_seed_repo(tmp_path: Path) -> None:
    repo = seed_control_plane_repo(tmp_path)
    env = os.environ.copy()
    env["CHARNESS_CACHE_HOME"] = str(tmp_path / "cache-home")
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
    assert doctor_payload[0]["support_sync"]["action_required"] is True
    assert doctor_payload[0]["support_sync"]["suggested_command"] == "charness tool sync-support demo-tool"
    assert doctor_payload[0]["install_route"]["mode"] == "manual"
    assert "Local support skill surface is not materialized yet." in doctor_payload[0]["next_steps"][0]

    sync = run_script(
        "scripts/sync_support.py",
        "--repo-root",
        str(repo),
        "--execute",
        "--json",
        env=env,
    )
    assert sync.returncode == 0, sync.stderr
    sync_payload = json.loads(sync.stdout)[0]
    assert sync_payload["status"] == "synced"
    generated_skill_root = repo / "skills" / "support" / "generated" / "demo-tool-wrapper"
    assert generated_skill_root.is_symlink()
    assert (generated_skill_root / "SKILL.md").exists()

    update = run_script("scripts/update_tools.py", "--repo-root", str(repo), "--execute", "--json")
    assert update.returncode == 0, update.stderr
    assert json.loads(update.stdout)[0]["status"] == "updated"

    lock_payload = json.loads((repo / "integrations" / "locks" / "demo-tool.json").read_text(encoding="utf-8"))
    assert lock_payload["support"]["source_type"] == "local_wrapper"
    assert lock_payload["support"]["cache_path"]
    assert lock_payload["support"]["content_digest"]
    assert lock_payload["doctor"]["doctor_status"] == "ok"
    assert lock_payload["doctor"]["readiness"]["ok"] is True
    assert lock_payload["doctor"]["support_sync"]["status"] == "not-tracked"
    assert "install_route" not in lock_payload["doctor"]
    assert lock_payload["update"]["update_status"] == "updated"


def test_sync_support_materializes_upstream_checkout_into_cache_and_repo_symlink(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    upstream = tmp_path / "upstream"
    cache_home = tmp_path / "cache-home"
    tools_dir = repo / "integrations" / "tools"
    locks_dir = repo / "integrations" / "locks"
    generated_dir = repo / "skills" / "support" / "generated"
    tools_dir.mkdir(parents=True)
    locks_dir.mkdir(parents=True)
    generated_dir.mkdir(parents=True)
    (upstream / "skills" / "demo-copy" / "references").mkdir(parents=True)
    (upstream / "skills" / "demo-copy" / "SKILL.md").write_text("# demo\n", encoding="utf-8")
    (upstream / "skills" / "demo-copy" / "helper.sh").write_text("echo demo\n", encoding="utf-8")
    (upstream / "skills" / "demo-copy" / "references" / "note.md").write_text("# note\n", encoding="utf-8")
    write_manifest_schema(repo)
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
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["CHARNESS_CACHE_HOME"] = str(cache_home)
    sync = run_script(
        "scripts/sync_support.py",
        "--repo-root",
        str(repo),
        "--execute",
        "--upstream-checkout",
        f"example/demo-copy={upstream}",
        "--json",
        cwd=ROOT,
        env=env,
    )
    assert sync.returncode == 0, sync.stderr
    payload = json.loads(sync.stdout)[0]
    link_root = repo / "skills" / "support" / "generated" / "demo-copy"
    assert payload["materialized_paths"] == ["skills/support/generated/demo-copy"]
    assert link_root.is_symlink()
    assert (link_root / "SKILL.md").read_text(encoding="utf-8") == "# demo\n"
    assert (link_root / "helper.sh").read_text(encoding="utf-8") == "echo demo\n"
    assert (link_root / "references" / "note.md").read_text(encoding="utf-8") == "# note\n"
    cache_path = Path(payload["cache_path"])
    assert cache_path.is_dir()
    assert str(cache_path).startswith(str(cache_home.resolve()))


def test_sync_support_uses_fixture_checkout_without_explicit_override(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    fixture_root = tmp_path / "fixture-upstream"
    cache_home = tmp_path / "cache-home"
    tools_dir = repo / "integrations" / "tools"
    locks_dir = repo / "integrations" / "locks"
    generated_dir = repo / "skills" / "support" / "generated"
    tools_dir.mkdir(parents=True)
    locks_dir.mkdir(parents=True)
    generated_dir.mkdir(parents=True)
    (fixture_root / "skills" / "fixture-skill").mkdir(parents=True)
    (fixture_root / "skills" / "fixture-skill" / "SKILL.md").write_text("# fixture\n", encoding="utf-8")
    fixture_map = tmp_path / "support-fixtures.json"
    fixture_map.write_text(
        json.dumps({"example/fixture-repo@main": str(fixture_root)}, indent=2) + "\n",
        encoding="utf-8",
    )
    write_manifest_schema(repo)
    (tools_dir / "fixture-skill.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": "fixture-skill",
                "kind": "external_skill",
                "display_name": "fixture-skill",
                "upstream_repo": "example/fixture-repo",
                "homepage": "https://example.com/fixture-skill",
                "lifecycle": {"install": {"mode": "manual"}, "update": {"mode": "manual"}},
                "checks": {
                    "detect": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["true"], "success_criteria": ["exit_code:0"]},
                },
                "access_modes": ["binary"],
                "version_expectation": {"policy": "advisory", "constraint": "latest"},
                "support_skill_source": {
                    "source_type": "upstream_repo",
                    "path": "skills/fixture-skill",
                    "ref": "main",
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["CHARNESS_CACHE_HOME"] = str(cache_home)
    env["CHARNESS_SUPPORT_SYNC_FIXTURES"] = str(fixture_map)
    sync = run_script(
        "scripts/sync_support.py",
        "--repo-root",
        str(repo),
        "--execute",
        "--json",
        env=env,
    )
    assert sync.returncode == 0, sync.stderr
    payload = json.loads(sync.stdout)[0]
    assert payload["status"] == "synced"
    assert (repo / "skills" / "support" / "generated" / "fixture-skill").is_symlink()


def test_sync_support_rejects_upstream_skill_file_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    tools_dir = repo / "integrations" / "tools"
    tools_dir.mkdir(parents=True)
    write_manifest_schema(repo)
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
                    "source_type": "upstream_repo",
                    "path": "skills/bad/SKILL.md",
                    "ref": "main",
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    result = run_script("scripts/validate-integrations.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "must point at a skill root directory" in result.stderr
