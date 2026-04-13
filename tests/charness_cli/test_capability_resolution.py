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
