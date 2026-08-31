from __future__ import annotations

import json
import os
from pathlib import Path

import yaml

from tests.quality_gates.git_fixture_support import init_git_repo

from .support import ROOT, pin_state_home, run_cli


def write_repo_capability_config(target_repo_root: Path, *, bindings: dict[str, str], profiles: dict[str, object]) -> None:
    config_dir = target_repo_root / ".charness" / "local"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "capability.json").write_text(
        json.dumps(
            {"version": 1, "bindings": bindings, "profiles": profiles},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def init_target_repo(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    init_git_repo(path)
    return path


def test_capability_resolve_reads_repo_local_config(tmp_path: Path) -> None:
    # The capability-resolution control plane is provider-agnostic: a consuming
    # runtime binds a logical capability id to its own provider + secret env
    # alias. github-gh is a retained known provider used here to exercise the
    # mechanism (gather-slack/notion were removed with #418).
    target_repo = init_target_repo(tmp_path / "target")
    write_repo_capability_config(
        target_repo,
        bindings={"github.default": "github.acme-dev"},
        profiles={
            "github.acme-dev": {
                "provider": "github-gh",
                "access_mode_preference": ["grant", "env"],
                "env_bindings": {"GH_TOKEN": "GH_TOKEN_ACME_DEV"},
            },
        },
    )
    result = run_cli(
        "capability",
        "resolve",
        "--repo-root",
        str(ROOT),
        "--target-repo-root",
        str(target_repo),
        "github.default",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["profile_id"] == "github.acme-dev"
    assert payload["provider_id"] == "github-gh"
    assert payload["env_bindings"] == {"GH_TOKEN": "GH_TOKEN_ACME_DEV"}
    assert payload["capability_config_path"].endswith(".charness/local/capability.json")


def test_capability_env_emits_alias_exports_without_printing_secret_values(tmp_path: Path) -> None:
    target_repo = init_target_repo(tmp_path / "target")
    write_repo_capability_config(
        target_repo,
        bindings={"github.default": "github.acme-dev"},
        profiles={
            "github.acme-dev": {
                "provider": "github-gh",
                "access_mode_preference": ["grant", "env"],
                "env_bindings": {"GH_TOKEN": "GH_TOKEN_ACME_DEV"},
            },
        },
    )
    env = os.environ.copy()
    pin_state_home(env, tmp_path / "home")
    env["GH_TOKEN_ACME_DEV"] = "super-secret-token"
    result = run_cli(
        "capability",
        "env",
        "--repo-root",
        str(ROOT),
        "--target-repo-root",
        str(target_repo),
        "github.default",
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["shell_exports"] == ['export GH_TOKEN="${GH_TOKEN_ACME_DEV}"']
    assert "super-secret-token" not in result.stdout


def test_capability_doctor_reuses_provider_metadata_for_resolved_profile(tmp_path: Path) -> None:
    target_repo = init_target_repo(tmp_path / "target")
    write_repo_capability_config(
        target_repo,
        bindings={"web-fetch.default": "web-fetch.local"},
        profiles={
            "web-fetch.local": {
                "provider": "web-fetch",
                "access_mode_preference": ["public"],
                "env_bindings": {},
            },
        },
    )
    result = run_cli(
        "capability",
        "doctor",
        "--repo-root",
        str(ROOT),
        "--target-repo-root",
        str(target_repo),
        "web-fetch.default",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["provider_id"] == "web-fetch"
    assert payload["provider_doctor"]["tool_id"] == "web-fetch"
    assert payload["provider_doctor"]["doctor_status"] == "ok"


def test_capability_init_scaffolds_repo_local_config_and_updates_gitignore(tmp_path: Path) -> None:
    target_repo = init_target_repo(tmp_path / "target")
    result = run_cli(
        "capability",
        "init",
        "--target-repo-root",
        str(target_repo),
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    local_path = target_repo / ".charness" / "local" / "capability.json"
    example_path = target_repo / ".charness" / "capability.example.json"
    gitignore_path = target_repo / ".gitignore"
    assert payload["capability_local_status"] == "written"
    assert payload["capability_example_status"] == "written"
    assert local_path.is_file()
    assert example_path.is_file()
    local_data = json.loads(local_path.read_text(encoding="utf-8"))
    assert local_data["bindings"] == {
        "github.default": "github.change-me",
    }
    assert set(local_data["profiles"]) == {"github.change-me"}
    # gather is public-source only: the scaffold must not seed a credentialed
    # gather provider (gather-slack) or a raw token route (SLACK_BOT_TOKEN, gws-cli).
    local_text = local_path.read_text(encoding="utf-8")
    assert "gws-cli" not in local_text
    assert "gather-slack" not in local_text
    assert "SLACK_BOT_TOKEN" not in local_text
    example_data = json.loads(example_path.read_text(encoding="utf-8"))
    assert "bindings" in example_data
    assert "profiles" in example_data
    assert "gather-slack" not in example_path.read_text(encoding="utf-8")
    assert gitignore_path.is_file()
    gitignore_lines = gitignore_path.read_text(encoding="utf-8").splitlines()
    assert "/.charness/local/" in gitignore_lines


def test_capability_init_does_not_duplicate_gitignore_line_when_already_present(tmp_path: Path) -> None:
    target_repo = init_target_repo(tmp_path / "target")
    gitignore_path = target_repo / ".gitignore"
    gitignore_path.write_text("/build/\n/.charness/local/\n", encoding="utf-8")
    result = run_cli(
        "capability",
        "init",
        "--target-repo-root",
        str(target_repo),
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["gitignore_status"] == "already-present"
    gitignore_text = gitignore_path.read_text(encoding="utf-8")
    assert gitignore_text.count("/.charness/local/") == 1


def test_capability_resolve_reports_missing_config_when_file_does_not_exist(tmp_path: Path) -> None:
    target_repo = init_target_repo(tmp_path / "target")
    result = run_cli(
        "capability",
        "resolve",
        "--repo-root",
        str(ROOT),
        "--target-repo-root",
        str(target_repo),
        "slack.default",
    )
    assert result.returncode != 0
    combined = (result.stdout + result.stderr).lower()
    assert ".charness/local/capability.json" in combined
    assert "charness capability init" in combined


def test_capability_resolve_failure_points_at_retired_xdg_layout(tmp_path: Path) -> None:
    target_repo = init_target_repo(tmp_path / "target")
    result = run_cli(
        "capability",
        "resolve",
        "--repo-root",
        str(ROOT),
        "--target-repo-root",
        str(target_repo),
        "slack.default",
    )
    assert result.returncode != 0
    combined = result.stdout + result.stderr
    assert "retired" in combined.lower() or "no longer read" in combined.lower()
    assert "capability-profiles.json" in combined


def test_capability_explain_reports_skill_needs_and_announcement_adapter_binding(tmp_path: Path) -> None:
    target_repo = init_target_repo(tmp_path / "target")
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

    gather_result = run_cli(
        "capability",
        "explain",
        "--repo-root",
        str(ROOT),
        "--target-repo-root",
        str(target_repo),
        "gather",
    )
    assert gather_result.returncode == 0, gather_result.stderr
    gather_payload = yaml.safe_load(gather_result.stdout)
    assert {need["logical_id"] for need in gather_payload["capability_needs"]} == {
        "github.default",
        "google-workspace.default",
        "agent-browser.default",
    }

    announcement_result = run_cli(
        "capability",
        "explain",
        "--repo-root",
        str(ROOT),
        "--target-repo-root",
        str(target_repo),
        "announcement",
    )
    assert announcement_result.returncode == 0, announcement_result.stderr
    announcement_payload = yaml.safe_load(announcement_result.stdout)
    logical_ids = {need["logical_id"] for need in announcement_payload["capability_needs"]}
    assert "slack.default" in logical_ids
    assert announcement_payload["announcement_delivery"]["delivery_kind"] == "human-backend"
    assert announcement_payload["announcement_delivery"]["status"] == "executable"
    assert announcement_payload["announcement_delivery"]["delivery_capability"] == "slack.default"


def test_capability_explain_keeps_unwired_thread_reply_draft_only(tmp_path: Path) -> None:
    target_repo = init_target_repo(tmp_path / "target")
    agents_dir = target_repo / ".agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    (agents_dir / "announcement-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo-repo",
                "delivery_kind: human-backend",
                "delivery_target: team-chat",
                "post_command_template: scripts/post-announcement.sh {message_file_q}",
                "delivery_capability: slack.default",
                "outputs:",
                "  - id: body",
                "    audience_tags:",
                "      - user",
                "    delivery_role: parent",
                "  - id: reply",
                "    audience_tags:",
                "      - operator",
                "    delivery_role: thread_reply",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_cli(
        "capability",
        "explain",
        "--repo-root",
        str(ROOT),
        "--target-repo-root",
        str(target_repo),
        "announcement",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["announcement_delivery"]["status"] == "draft-only"
    assert payload["announcement_delivery"]["blocking_issues"]
    assert "slack.default" not in {need["logical_id"] for need in payload["capability_needs"]}
    assert any("draft-only" in note for note in payload["notes"])


def test_capability_explain_keeps_thread_reply_before_parent_draft_only(tmp_path: Path) -> None:
    target_repo = init_target_repo(tmp_path / "target")
    agents_dir = target_repo / ".agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    (agents_dir / "announcement-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo-repo",
                "delivery_kind: human-backend",
                "delivery_target: team-chat",
                "post_command_template: scripts/post-announcement.sh --thread {parent_delivery_handle_q} {message_file_q}",
                "delivery_capability: slack.default",
                "outputs:",
                "  - id: reply",
                "    audience_tags:",
                "      - operator",
                "    delivery_role: thread_reply",
                "  - id: body",
                "    audience_tags:",
                "      - user",
                "    delivery_role: parent",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_cli(
        "capability",
        "explain",
        "--repo-root",
        str(ROOT),
        "--target-repo-root",
        str(target_repo),
        "announcement",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["announcement_delivery"]["status"] == "draft-only"
    assert any("before any preceding `parent`" in issue for issue in payload["announcement_delivery"]["blocking_issues"])
    assert "slack.default" not in {need["logical_id"] for need in payload["capability_needs"]}
