from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from tests.repo_copy import clone_seeded_charness_repo

from .support import (
    make_fake_go_specdown,
    make_fake_npm_agent_browser,
    make_release_fixture,
    make_support_sync_fixture,
)
from .test_managed_install import init_managed_home_from_repo, load_charness_module
from .tool_fakes import make_fake_nose


@pytest.mark.release_only
def test_installed_cli_update_all_without_json_prints_progress_and_summary(tmp_path: Path, seeded_charness_git_repo: Path) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    source_repo = clone_seeded_charness_repo(source_root, seeded_charness_git_repo)
    home_root, env = init_managed_home_from_repo(tmp_path, source_repo)

    fake_agent_browser_npm, fake_agent_browser = make_fake_npm_agent_browser(tmp_path)
    fake_go, specdown_bin = make_fake_go_specdown(tmp_path)
    fake_curl, fake_nose = make_fake_nose(tmp_path)
    release_fixture = make_release_fixture(tmp_path)
    support_fixture = make_support_sync_fixture(tmp_path)
    env["PATH"] = os.pathsep.join(
        [
            str(fake_curl.parent),
            str(fake_nose.parent),
            str(fake_agent_browser_npm.parent),
            str(fake_agent_browser.parent),
            str(fake_go.parent),
            str(specdown_bin.parent),
            env["PATH"],
        ]
    )
    env["GOPATH"] = str(specdown_bin.parent.parent)
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)
    env["CHARNESS_SUPPORT_SYNC_FIXTURES"] = str(support_fixture)

    installed_cli = home_root / ".local" / "bin" / "charness"
    update_result = subprocess.run(
        [sys.executable, str(installed_cli), "update", "all", "--home-root", str(home_root), "--skip-codex-cache-refresh"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    # A successful updater command is not enough: blocking post-update doctor
    # findings now fail the aggregate operation and carry typed recovery data.
    assert update_result.returncode == 1, update_result.stderr
    payload = yaml.safe_load(update_result.stdout)
    assert payload["package_id"] == "charness"
    assert payload["scope"] == "all"
    assert payload["response_level"] == "summary"
    assert payload["tool_update"]["response_level"] == "summary"
    assert payload["tool_update"]["summary"]["tool_count"] == 15
    assert payload["tool_update"]["attention"]["manual_tool_ids"] == [
        "awiki",
        "github-gh",
        "gitleaks",
        "glow",
        "lychee",
        "repograph",
        "ruff",
        "tokei",
        "vulture",
    ]
    assert payload["tool_update"]["attention"]["not_ready_tool_ids"]
    assert "results" not in payload["tool_update"]
    assert "STEP: updating tracked external tools" in update_result.stderr
    assert "STEP: syncing support surfaces" in update_result.stderr
    assert "STEP: refreshing tool doctor state" in update_result.stderr
    assert "FAILED: update incomplete" in update_result.stderr

    detail_result = subprocess.run(
        [
            sys.executable,
            str(installed_cli),
            "update",
            "all",
            "--detail",
            "--home-root",
            str(home_root),
            "--skip-codex-cache-refresh",
        ],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert detail_result.returncode == 1, detail_result.stderr
    detail_payload = yaml.safe_load(detail_result.stdout)
    assert detail_payload["response_level"] == "detail"
    assert detail_payload["tool_update"]["results"]["agent-browser"]["update"]["status"] in {"updated", "refreshed"}


def test_probe_self_release_defaults_to_the_declared_repo(tmp_path: Path, monkeypatch) -> None:
    """The no-argument call is the one production uses, and it was unexercised.

    `charness:994` resolves the repo from `REPO_URL` when the caller passes none.
    Every existing probe test supplies a repo explicitly, so a wrong default would
    have surfaced first as a version check pointed at the wrong repository.
    """

    module = load_charness_module("charness_probe_self_release_default_under_test")
    repo = module.self_release_repo()
    fixture = tmp_path / "releases.json"
    fixture.write_text(
        json.dumps({repo: {"tag_name": "v9.9.9", "html_url": "https://example.invalid/r"}}),
        encoding="utf-8",
    )
    monkeypatch.setenv("CHARNESS_RELEASE_PROBE_FIXTURES", str(fixture))

    release = module.probe_self_release()

    assert release["repo"] == repo
    assert release["latest_tag"] == "v9.9.9"
    assert release["api_url"] == f"https://api.github.com/repos/{repo}/releases/latest"


def test_update_human_summary_without_version_none_prints_tool_statuses(capsys) -> None:
    module = load_charness_module("charness_update_output_unit_under_test")

    module.print_update_human_summary(
        {
            "package_id": "charness",
            "checkout": {"pulled": False, "repo_root": "/tmp/charness"},
            "scope": "all",
            "completed_actions": ["external_tools_updated"],
            "tool_update": {
                "results": {
                    "agent-browser": {"update": {"status": "updated"}},
                    "nose": {
                        "update": {
                            "status": "updated",
                            "mode": "script",
                            "version_transition": {"from": "0.17.0", "to": "0.18.0"},
                        }
                    },
                    "specdown": {"doctor": {"doctor_status": "ok", "healthcheck": {"status": "not-configured"}}},
                    "tokei": {
                        "update": {
                            "status": "refreshed",
                            "mode": "package_manager",
                            "package_manager": "cargo",
                            "package_name": "tokei",
                            "version_transition": {"from": "1.1.0", "to": "1.1.0"},
                        }
                    },
                    "github-gh": {
                        "update": {
                            "status": "updated",
                            "mode": "package_manager",
                            "package_manager": "npm",
                            "package_name": "gh-cli",
                            "version_transition": {"from": "2.0.0", "to": "2.1.0"},
                        }
                    },
                }
            },
        }
    )

    output = capsys.readouterr().out
    assert "VERSION: None" not in output
    assert "-> None" not in output
    assert "SCOPE: all" in output
    assert "TOOLS:" in output
    assert "  - agent-browser: updated (version unknown)" in output
    assert "  - nose: updated 0.17.0 -> 0.18.0 (script)" in output
    assert "  - specdown: ok healthcheck=not-configured" in output
    assert "  - tokei: refreshed 1.1.0 (cargo: tokei)" in output
    assert "  - github-gh: updated 2.0.0 -> 2.1.0 (npm: gh-cli)" in output


def test_tool_update_lines_empty_results_render_nothing(capsys) -> None:
    module = load_charness_module("charness_tool_update_lines_empty_under_test")

    assert module._tool_update_lines({"results": {}}) == []
    assert module._tool_update_lines({}) == []

    module.print_update_human_summary(
        {
            "package_id": "charness",
            "checkout": {"pulled": False, "repo_root": "/tmp/charness"},
            "scope": "all",
            "tool_update": {"results": {}},
        }
    )

    output = capsys.readouterr().out
    assert "TOOLS:" not in output


def test_tool_response_projection_hides_raw_probe_evidence_by_default() -> None:
    module = load_charness_module("charness_tool_response_projection_under_test")
    payload = {
        "repo_root": "/tmp/charness",
        "managed_checkout": True,
        "tool_ids": [],
        "results": {
            "demo": {
                "update": {
                    "status": "updated",
                    "mode": "script",
                    "version_transition": {"from": "1.0.0", "to": "1.1.0"},
                    "commands": [{"command": "curl https://example.invalid/install.sh | sh"}],
                    "release": {"asset_names": ["demo-linux-amd64.tar.gz"]},
                },
                "doctor": {
                    "doctor_status": "ok",
                    "doctor_disposition": "ok",
                    "support_state": "upstream-consumed",
                    "healthcheck": {"status": "ok", "output": "verbose probe output"},
                },
                "next_step": "No action required.",
            }
        },
    }

    projected = module.project_tool_response(payload, event="tool-update")

    result = projected["results"]["demo"]
    assert projected["response_level"] == "summary"
    assert projected["detail_available"] is True
    assert projected["summary"] == {"tool_count": 1, "status_counts": {"updated": 1}}
    assert result["update"] == {
        "status": "updated",
        "mode": "script",
        "version_transition": {"from": "1.0.0", "to": "1.1.0"},
    }
    assert result["doctor"] == {
        "doctor_status": "ok",
        "doctor_disposition": "ok",
        "healthcheck": {"status": "ok"},
    }
    assert "commands" not in str(projected)
    assert "asset_names" not in str(projected)
    assert "verbose probe output" not in str(projected)


def test_aggregate_tool_response_hides_per_tool_records_but_names_attention() -> None:
    module = load_charness_module("charness_aggregate_tool_response_projection_under_test")
    payload = {
        "repo_root": "/tmp/charness",
        "managed_checkout": True,
        "tool_ids": [],
        "results": {
            "failed-tool": {
                "update": {
                    "status": "failed",
                    "mode": "script",
                    "commands": [{"command": "curl https://example.invalid/install.sh | sh"}],
                },
                "doctor": {"doctor_status": "ok", "doctor_disposition": "ready"},
                "next_step": "Verbose failure evidence.",
            },
            "manual-tool": {
                "update": {"status": "manual", "mode": "manual"},
                "doctor": {"doctor_status": "ok", "doctor_disposition": "ready"},
                "next_step": "Manual updater details.",
            },
            "ready-tool": {
                "update": {"status": "updated", "mode": "script"},
                "doctor": {"doctor_status": "ok", "doctor_disposition": "ready"},
            },
            "not-ready-tool": {
                "update": {"status": "skipped", "mode": "script"},
                "doctor": {
                    "doctor_status": "missing",
                    "doctor_disposition": "blocking-install-needed",
                },
            },
        },
    }

    projected = module.project_tool_response(payload, event="tool-update")

    assert projected["summary"] == {
        "tool_count": 4,
        "status_counts": {"failed": 1, "manual": 1, "skipped": 1, "updated": 1},
    }
    assert projected["attention"] == {
        "failed_tool_ids": ["failed-tool"],
        "manual_tool_ids": ["manual-tool"],
        "not_ready_tool_ids": ["not-ready-tool"],
    }
    # tool-update mutates: the next action must point at persisted evidence,
    # never at re-running the mutating command for inspection.
    assert "integrations/locks/" in projected["next_step"]
    assert "tool doctor" in projected["next_step"]
    assert "results" not in projected
    assert "commands" not in str(projected)
    assert "Verbose failure evidence." not in str(projected)


def test_mutating_aggregate_next_action_points_at_locks_and_readonly_doctor_stays_detail() -> None:
    module = load_charness_module("charness_next_action_event_split_under_test")
    payload = {
        "results": {
            "manual-tool": {"update": {"status": "manual", "mode": "manual"}},
            "failed-tool": {"update": {"status": "failed", "mode": "script"}},
        }
    }
    for event in ("tool-update", "tool-install", "tool-repair", "tool-sync-support"):
        projected = module.project_tool_response(payload, event=event)
        assert "integrations/locks/" in projected["next_step"], event
        assert "execute the operation again" in projected["next_step"], event

    # an explicit dry-run / preview (execute=False) keeps the plain message —
    # nothing was executed, so a --detail re-run is safe inspection
    preview = module.project_tool_response(dict(payload, execute=False), event="tool-repair")
    assert preview["next_step"] == "Use --detail to inspect the listed tool records."

    doctor_payload = {
        "results": {
            "missing-tool": {"doctor": {"doctor_status": "missing", "doctor_disposition": "blocking-install-needed"}},
            "ok-tool": {"doctor": {"doctor_status": "missing", "doctor_disposition": "blocking-install-needed"}},
        }
    }
    projected = module.project_tool_response(doctor_payload, event="tool-doctor")
    assert projected["next_step"] == "Use --detail to inspect the listed tool records."


def test_compact_doctor_projection_carries_the_detected_version() -> None:
    module = load_charness_module("charness_compact_doctor_version_under_test")
    payload = {
        "results": {
            "demo": {
                "doctor": {
                    "doctor_status": "ok",
                    "doctor_disposition": "ready",
                    "version": {"observed_version": "0.31.2", "policy": "advisory"},
                }
            }
        }
    }

    projected = module.project_tool_response(payload, event="tool-doctor")

    assert projected["results"]["demo"]["doctor"]["observed_version"] == "0.31.2"
    # the rest of the version block stays detail-only
    assert "policy" not in str(projected["results"]["demo"]["doctor"])

    # a doctor result without a version block projects without the key
    bare = module.project_tool_response(
        {"results": {"demo": {"doctor": {"doctor_status": "ok", "doctor_disposition": "ready"}}}},
        event="tool-doctor",
    )
    assert "observed_version" not in bare["results"]["demo"]["doctor"]


def test_tool_response_projection_tolerates_malformed_result_entries() -> None:
    module = load_charness_module("charness_tool_response_projection_malformed_entries_under_test")

    empty = module.project_tool_response({"results": ["not-a-mapping"]}, event="tool-update")
    assert empty["summary"] == {"tool_count": 0, "status_counts": {}}
    assert empty["results"] == {}

    projected = module.project_tool_response(
        {
            "results": {
                "manual-tool": {"update": {"status": "manual", "mode": "manual"}},
                "ready-tool": {"update": {"status": "updated", "mode": "script"}},
                "malformed-tool": ["not-a-tool-record"],
            }
        },
        event="tool-update",
    )

    assert projected["summary"] == {"tool_count": 2, "status_counts": {"manual": 1, "updated": 1}}
    assert projected["attention"] == {"manual_tool_ids": ["manual-tool"]}
    assert "malformed-tool" not in str(projected)


def test_package_manager_tool_next_step_includes_version_transition() -> None:
    module = load_charness_module("charness_package_manager_next_step_under_test")

    next_step = module._package_manager_tool_next_step(
        "nose",
        {
            "mode": "package_manager",
            "package_manager": "cargo",
            "package_name": "nose-cli",
            "status": "updated",
            "version_transition": {"from": "0.17.0", "to": "0.18.0"},
        },
    )

    assert next_step == "`nose` was updated via `cargo` package `nose-cli` (0.17.0 -> 0.18.0)."

    refreshed_next_step = module._package_manager_tool_next_step(
        "nose",
        {
            "mode": "package_manager",
            "package_manager": "cargo",
            "package_name": "nose-cli",
            "status": "refreshed",
            "version_transition": {"from": "0.18.0", "to": "0.18.0"},
        },
    )

    assert refreshed_next_step == "`nose` was refreshed via `cargo` package `nose-cli` (0.18.0)."


def test_print_next_actions_labels_repo_onboarding_primary_and_merges(capsys) -> None:
    module = load_charness_module("charness_next_actions_unit_under_test")

    module._print_next_actions(
        {
            "next_action": {
                "kind": "repo-init",
                "host": None,
                "source": "repo_onboarding",
                "message": "Run charness setup in this repo.",
            },
            "repo_onboarding": {"message": "Run charness setup in this repo."},
            "claude_host_guidance": {"message": "Restart Claude Code."},
            "codex_host_guidance": {"message": "Restart Codex."},
        }
    )

    output = capsys.readouterr().out
    assert output.count("NEXT:") == 1
    assert output.count("  - repo: Run charness setup in this repo.") == 1
    assert "  - claude: Restart Claude Code." in output
    assert "  - codex: Restart Codex." in output
    assert "CODEX_NEXT_STEP" not in output
    assert "CLAUDE_NEXT_STEP" not in output
    assert "REPO_NEXT_STEP" not in output
