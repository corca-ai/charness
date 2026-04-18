from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from .support import ROOT, run_cli


def write_machine_local_capability_config(home_root: Path, *, profiles: dict[str, object], repos: dict[str, object]) -> None:
    config_root = home_root / ".config" / "charness"
    config_root.mkdir(parents=True, exist_ok=True)
    (config_root / "capability-profiles.json").write_text(
        json.dumps({"schema_version": 1, "profiles": profiles}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (config_root / "repo-bindings.json").write_text(
        json.dumps({"schema_version": 1, "repos": repos}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def init_target_repo(path: Path, *, origin_url: str) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "remote", "add", "origin", origin_url], cwd=path, check=True, capture_output=True, text=True)
    return path


def test_capability_resolve_prefers_remote_repo_binding(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    target_repo = init_target_repo(tmp_path / "target", origin_url="git@github.com:corca-ai/charness.git")
    write_machine_local_capability_config(
        home_root,
        profiles={
            "slack.ceal-dev": {
                "provider": "gather-slack",
                "access_mode_preference": ["grant", "env"],
                "env_bindings": {"SLACK_BOT_TOKEN": "SLACK_BOT_TOKEN_CEAL_DEV"},
            }
        },
        repos={
            "github.com/corca-ai/charness": {
                "slack.default": "slack.ceal-dev",
            }
        },
    )
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    result = run_cli(
        "capability",
        "resolve",
        "--home-root",
        str(home_root),
        "--repo-root",
        str(ROOT),
        "--target-repo-root",
        str(target_repo),
        "--json",
        "slack.default",
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["matched_repo_key"] == "github.com/corca-ai/charness"
    assert payload["profile_id"] == "slack.ceal-dev"
    assert payload["provider_id"] == "gather-slack"
    assert payload["env_bindings"] == {"SLACK_BOT_TOKEN": "SLACK_BOT_TOKEN_CEAL_DEV"}


def test_capability_env_emits_alias_exports_without_printing_secret_values(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    target_repo = init_target_repo(tmp_path / "target", origin_url="git@github.com:corca-ai/charness.git")
    write_machine_local_capability_config(
        home_root,
        profiles={
            "slack.ceal-dev": {
                "provider": "gather-slack",
                "access_mode_preference": ["grant", "env"],
                "env_bindings": {"SLACK_BOT_TOKEN": "SLACK_BOT_TOKEN_CEAL_DEV"},
            }
        },
        repos={
            "github.com/corca-ai/charness": {
                "slack.default": "slack.ceal-dev",
            }
        },
    )
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["SLACK_BOT_TOKEN_CEAL_DEV"] = "super-secret-token"
    result = run_cli(
        "capability",
        "env",
        "--home-root",
        str(home_root),
        "--repo-root",
        str(ROOT),
        "--target-repo-root",
        str(target_repo),
        "slack.default",
        env=env,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == 'export SLACK_BOT_TOKEN="${SLACK_BOT_TOKEN_CEAL_DEV}"'
    assert "super-secret-token" not in result.stdout


def test_capability_doctor_reuses_provider_metadata_for_resolved_profile(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    target_repo = init_target_repo(tmp_path / "target", origin_url="git@github.com:corca-ai/charness.git")
    write_machine_local_capability_config(
        home_root,
        profiles={
            "notion.public": {
                "provider": "gather-notion",
                "access_mode_preference": ["public"],
                "env_bindings": {},
            }
        },
        repos={
            "github.com/corca-ai/charness": {
                "notion.default": "notion.public",
            }
        },
    )
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    result = run_cli(
        "capability",
        "doctor",
        "--home-root",
        str(home_root),
        "--repo-root",
        str(ROOT),
        "--target-repo-root",
        str(target_repo),
        "--json",
        "notion.default",
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["provider_id"] == "gather-notion"
    assert payload["provider_doctor"]["tool_id"] == "gather-notion"
    assert payload["provider_doctor"]["doctor_status"] == "ok"


def test_capability_init_scaffolds_machine_local_config_files(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    target_repo = init_target_repo(tmp_path / "target", origin_url="git@github.com:corca-ai/charness.git")
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    result = run_cli(
        "capability",
        "init",
        "--home-root",
        str(home_root),
        "--target-repo-root",
        str(target_repo),
        "--json",
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    profiles_path = home_root / ".config" / "charness" / "capability-profiles.json"
    bindings_path = home_root / ".config" / "charness" / "repo-bindings.json"
    assert payload["profiles_status"] == "written"
    assert payload["repo_bindings_status"] == "written"
    assert profiles_path.is_file()
    assert bindings_path.is_file()
    bindings = json.loads(bindings_path.read_text(encoding="utf-8"))
    assert "github.com/corca-ai/charness" in bindings["repos"]


def test_capability_explain_reports_skill_needs_and_announcement_adapter_binding(tmp_path: Path) -> None:
    home_root = tmp_path / "home"
    target_repo = init_target_repo(tmp_path / "target", origin_url="git@github.com:corca-ai/charness.git")
    agents_dir = target_repo / ".agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    (agents_dir / "announcement-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo-repo",
                "product_name: Demo",
                "delivery_kind: human-backend",
                "delivery_target: team-chat",
                "post_command_template: scripts/post-announcement.sh {message_file_q}",
                "delivery_capability: slack.default",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["HOME"] = str(home_root)
    gather_result = run_cli(
        "capability",
        "explain",
        "--home-root",
        str(home_root),
        "--repo-root",
        str(ROOT),
        "--target-repo-root",
        str(target_repo),
        "--json",
        "gather",
        env=env,
    )
    assert gather_result.returncode == 0, gather_result.stderr
    gather_payload = json.loads(gather_result.stdout)
    assert {need["logical_id"] for need in gather_payload["capability_needs"]} == {
        "github.default",
        "slack.default",
        "gws.default",
        "agent-browser.default",
    }

    announcement_result = run_cli(
        "capability",
        "explain",
        "--home-root",
        str(home_root),
        "--repo-root",
        str(ROOT),
        "--target-repo-root",
        str(target_repo),
        "--json",
        "announcement",
        env=env,
    )
    assert announcement_result.returncode == 0, announcement_result.stderr
    announcement_payload = json.loads(announcement_result.stdout)
    logical_ids = {need["logical_id"] for need in announcement_payload["capability_needs"]}
    assert "slack.default" in logical_ids
    assert announcement_payload["announcement_delivery"]["delivery_kind"] == "human-backend"
    assert announcement_payload["announcement_delivery"]["delivery_capability"] == "slack.default"
