from __future__ import annotations

import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from scripts.adapters.control_plane_lifecycle_lib import (
    print_tool_statuses,
    update_advisory_line,
    version_transition_suffix,
)
from tests.repo_copy import clone_seeded_charness_repo

from .support import (
    FIXTURES,
    build_test_path,
    make_fake_agent_browser,
    make_fake_go_specdown,
    make_fake_npm_agent_browser,
    make_release_fixture,
    make_support_sync_fixture,
    pin_state_home,
    run_cli_in_repo,
)
from .tool_fakes import make_fake_nose

ROOT = Path(__file__).resolve().parents[2]


def load_charness_module(module_name: str = "charness_tool_lifecycle_under_test"):
    loader = importlib.machinery.SourceFileLoader(module_name, str(ROOT / "charness"))
    spec = importlib.util.spec_from_loader(module_name, loader)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_agent_browser_runtime_guard_module(module_name: str = "agent_browser_runtime_guard_under_test"):
    loader = importlib.machinery.SourceFileLoader(
        module_name,
        str(ROOT / "scripts" / "evidence" / "agent_browser_runtime_guard.py"),
    )
    spec = importlib.util.spec_from_loader(module_name, loader)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_update_advisory_line_without_manifest_route_uses_doctor_install_route_url() -> None:
    line = update_advisory_line(
        {
            "tool_id": "github-gh",
            "install_route": {
                "mode": "manual",
                "docs_url": "https://github.com/cli/cli/releases",
            },
            "update_advisory": {
                "status": "behind",
                "observed_version": "2.70.0",
                "latest_version": "2.73.0",
                "latest_tag": "v2.73.0",
            },
        }
    )

    assert line is not None
    assert "manual update required; see https://github.com/cli/cli/releases" in line
    assert "manifest install/update route" not in line


def test_version_transition_suffix_renders_from_and_to_when_different() -> None:
    assert version_transition_suffix(
        {"status": "updated", "version_transition": {"from": "0.17.0", "to": "0.18.0"}}
    ) == " 0.17.0 -> 0.18.0"


def test_version_transition_suffix_renders_to_only_when_from_matches_to() -> None:
    assert version_transition_suffix(
        {"status": "updated", "version_transition": {"from": "0.18.0", "to": "0.18.0"}}
    ) == " 0.18.0"


def test_version_transition_suffix_renders_to_only_when_from_missing() -> None:
    assert version_transition_suffix(
        {"status": "updated", "version_transition": {"from": None, "to": "0.18.0"}}
    ) == " 0.18.0"


def test_version_transition_suffix_reports_version_unknown_for_updated_without_transition() -> None:
    assert version_transition_suffix({"status": "updated"}) == " (version unknown)"
    assert version_transition_suffix({"status": "updated-not-ready"}) == " (version unknown)"
    assert version_transition_suffix({"status": "refreshed"}) == ""
    assert version_transition_suffix({"status": "refreshed-not-ready"}) == ""


def test_version_transition_suffix_empty_for_other_statuses_without_transition() -> None:
    assert version_transition_suffix({"status": "manual"}) == ""
    assert version_transition_suffix({"status": "noop"}) == ""


def test_version_transition_suffix_renders_transition_for_failed_status() -> None:
    assert version_transition_suffix(
        {"status": "failed", "version_transition": {"from": "1.0.0", "to": "2.0.0"}}
    ) == " 1.0.0 -> 2.0.0"


def test_print_tool_statuses_renders_version_transition(capsys) -> None:
    print_tool_statuses(
        [
            {
                "tool_id": "nose",
                "status": "updated",
                "version_transition": {"from": "0.17.0", "to": "0.18.0"},
                "healthcheck": {"status": "not-configured"},
            }
        ]
    )

    output = capsys.readouterr().out
    assert "nose: updated 0.17.0 -> 0.18.0 healthcheck=not-configured" in output


def cleanup_agent_browser_orphans() -> None:
    module = load_agent_browser_runtime_guard_module()
    previous_argv = sys.argv
    buffer = io.StringIO()
    try:
        sys.argv = [
            "agent_browser_runtime_guard.py",
            "--repo-root",
            str(ROOT),
            "--cleanup-orphans",
            "--execute",
        ]
        with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
            module.main()
    finally:
        sys.argv = previous_argv


def make_fake_go_glow(tmp_path: Path) -> tuple[Path, Path]:
    gopath = tmp_path / "go"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    script = bin_dir / "go"
    shutil.copy2(FIXTURES / "fake_go_glow.py", script)
    script.with_suffix(".json").write_text(
        json.dumps({"gopath": str(gopath), "fixtures": str(FIXTURES)}, indent=2) + "\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script, gopath


def test_fake_go_installers_honor_gobin(tmp_path: Path) -> None:
    specdown_go, _specdown_bin = make_fake_go_specdown(tmp_path / "specdown")
    glow_go, gopath = make_fake_go_glow(tmp_path / "glow")
    gobin = tmp_path / "custom-gobin"
    env = {**os.environ, "GOBIN": str(gobin)}
    pin_state_home(env, tmp_path / "home")

    gitleaks_result = subprocess.run(
        [str(specdown_go), "install", "github.com/zricethezav/gitleaks/v8@latest"],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    glow_result = subprocess.run(
        [str(glow_go), "install", "github.com/charmbracelet/glow/v2@latest"],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert gitleaks_result.returncode == 0, gitleaks_result.stderr
    assert glow_result.returncode == 0, glow_result.stderr
    assert (gobin / "gitleaks").is_file()
    assert (gobin / "glow").is_symlink()
    assert (gobin / "glow").resolve() == gopath / "bin" / "glow"


@pytest.mark.release_only
def test_tool_install_can_select_quality_validation_recommendations(tmp_path: Path, seeded_charness_repo: Path) -> None:
    repo_root = clone_seeded_charness_repo(tmp_path, seeded_charness_repo)
    release_fixture = make_release_fixture(tmp_path)
    env = os.environ.copy()
    pin_state_home(env, tmp_path / "home")
    env["PATH"] = build_test_path()
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)

    result = run_cli_in_repo(
        repo_root,
        "tool",
        "install",
        "--repo-root",
        str(repo_root),
        "--dry-run",
        "--skip-sync-support",
        "--recommendation-role",
        "validation",
        "--next-skill-id",
        "quality",
        env=env,
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["tool_selection"] == {
        "recommend_for_skill": None,
        "recommendation_role": "validation",
        "next_skill_id": "quality",
        "selected_tool_ids": ["awiki", "gitleaks", "lychee", "nose", "repograph", "ruff", "tokei", "vulture"],
    }
    assert payload["tool_ids"] == ["awiki", "gitleaks", "lychee", "nose", "repograph", "ruff", "tokei", "vulture"]
    assert payload["summary"]["tool_count"] == 8
    assert "results" not in payload


@pytest.mark.release_only
def test_tool_install_recommendation_filter_no_match_does_not_install_all(tmp_path: Path, seeded_charness_repo: Path) -> None:
    repo_root = clone_seeded_charness_repo(tmp_path, seeded_charness_repo)
    release_fixture = make_release_fixture(tmp_path)
    env = os.environ.copy()
    pin_state_home(env, tmp_path / "home")
    env["PATH"] = build_test_path()
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)

    result = run_cli_in_repo(
        repo_root,
        "tool",
        "install",
        "--repo-root",
        str(repo_root),
        "--dry-run",
        "--skip-sync-support",
        "--recommendation-role",
        "validation",
        "--next-skill-id",
        "nonexistent-skill",
        env=env,
    )

    assert result.returncode == 1
    assert "No tools matched recommendation filters" in result.stderr


def _pin_prior_observed_version(
    repo_root: Path, tool_id: str, version: str, *, env: dict[str, str]
) -> None:
    """Create a current-schema lock, then pin its prior observed version.

    The lock schema intentionally rejects partial hand-written state. Seeded
    repos may not have a lock for this tool, so obtain the complete shape from
    the current doctor lifecycle before making the deterministic version pin.
    """
    doctor_result = run_cli_in_repo(
        repo_root,
        "tool",
        "doctor",
        "--repo-root",
        str(repo_root),
        tool_id,
        env=env,
    )
    assert doctor_result.returncode == 0, doctor_result.stderr

    lock_path = repo_root / "integrations" / "locks" / f"{tool_id}.json"
    assert lock_path.is_file()
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    doctor = lock.get("doctor")
    assert isinstance(doctor, dict)
    version_state = doctor.get("version")
    assert isinstance(version_state, dict)
    version_state["observed_version"] = version
    lock_path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")


@pytest.mark.release_only
def test_tool_update_runs_configured_agent_browser_script_for_path_install(tmp_path: Path, seeded_charness_repo: Path) -> None:
    cleanup_agent_browser_orphans()
    repo_root = clone_seeded_charness_repo(tmp_path, seeded_charness_repo)
    home_root = tmp_path / "home"
    fake_agent_browser = make_fake_agent_browser(tmp_path)
    fake_npm, _browser_link = make_fake_npm_agent_browser(tmp_path)
    release_fixture = make_release_fixture(tmp_path)
    support_fixture = make_support_sync_fixture(tmp_path)
    plugin_root = home_root / ".codex" / "plugins" / "charness"
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    pin_state_home(env, home_root)
    env["PATH"] = build_test_path(fake_agent_browser.parent, fake_npm.parent)
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)
    env["CHARNESS_SUPPORT_SYNC_FIXTURES"] = str(support_fixture)
    env["CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS"] = "1"
    _pin_prior_observed_version(repo_root, "agent-browser", "0.9.2", env=env)

    result = run_cli_in_repo(repo_root, "tool", "update", "--detail", "--repo-root", str(repo_root), "agent-browser", env=env)
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    browser = payload["results"]["agent-browser"]
    assert browser["update"]["status"] == "updated"
    assert browser["update"]["mode"] == "script"
    assert browser["update"]["commands"][0]["command"] == "npm install -g agent-browser@latest"
    assert browser["update"]["release"]["latest_tag"] == "v0.25.3"
    assert browser["update"]["version_transition"] == {"from": "0.9.2", "to": "0.25.3"}
    assert browser["support"]["status"] == "synced"
    assert browser["doctor"]["doctor_status"] == "ok"
    lock_payload = json.loads((repo_root / "integrations" / "locks" / "agent-browser.json").read_text(encoding="utf-8"))
    assert lock_payload["release"]["latest_tag"] == "v0.25.3"
    assert lock_payload["update"]["update_status"] == "updated"
    assert lock_payload["update"]["mode"] == "script"
    assert lock_payload["update"]["commands"][0]["command"] == "npm install -g agent-browser@latest"
    assert lock_payload["update"]["version_transition"] == {"from": "0.9.2", "to": "0.25.3"}
    assert lock_payload["support"]["materialized_paths"] == ["support/agent-browser"]
    assert (plugin_root / "support" / "agent-browser" / "SKILL.md").is_file()
    assert lock_payload["doctor"]["doctor_status"] == "ok"


@pytest.mark.release_only
def test_tool_update_routes_npm_provenance_for_agent_browser(tmp_path: Path, seeded_charness_repo: Path) -> None:
    cleanup_agent_browser_orphans()
    repo_root = clone_seeded_charness_repo(tmp_path, seeded_charness_repo)
    home_root = tmp_path / "home"
    npm_script, browser_link = make_fake_npm_agent_browser(tmp_path)
    release_fixture = make_release_fixture(tmp_path)
    support_fixture = make_support_sync_fixture(tmp_path)
    plugin_root = home_root / ".codex" / "plugins" / "charness"
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    pin_state_home(env, home_root)
    env["PATH"] = f"{npm_script.parent}:{browser_link.parent}:{env.get('PATH', '')}"
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)
    env["CHARNESS_SUPPORT_SYNC_FIXTURES"] = str(support_fixture)
    env["CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS"] = "1"

    result = run_cli_in_repo(repo_root, "tool", "update", "--detail", "--repo-root", str(repo_root), "agent-browser", env=env)
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    browser = payload["results"]["agent-browser"]
    assert browser["update"]["status"] == "updated"
    assert browser["update"]["mode"] == "script"
    assert browser["update"]["commands"][0]["command"] == "npm install -g agent-browser@latest"
    assert browser["doctor"]["provenance"]["install_method"] == "npm"
    assert browser["support"]["status"] == "synced"
    assert (plugin_root / "support" / "agent-browser" / "SKILL.md").is_file()
    lock_payload = json.loads((repo_root / "integrations" / "locks" / "agent-browser.json").read_text(encoding="utf-8"))
    assert lock_payload["provenance"]["install_method"] == "npm"
    assert lock_payload["update"]["mode"] == "script"
    assert lock_payload["update"]["commands"][0]["command"] == "npm install -g agent-browser@latest"


@pytest.mark.release_only
def test_tool_doctor_reports_specdown_binary_contract_without_support_sync(tmp_path: Path, seeded_charness_repo: Path) -> None:
    repo_root = clone_seeded_charness_repo(tmp_path, seeded_charness_repo)
    home_root = tmp_path / "home"
    go_script, specdown_script = make_fake_go_specdown(tmp_path)
    fake_curl, _fake_nose = make_fake_nose(tmp_path)
    release_fixture = make_release_fixture(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    pin_state_home(env, home_root)
    env["PATH"] = build_test_path(fake_curl.parent, go_script.parent, specdown_script.parent)
    env["GOPATH"] = str(specdown_script.parent.parent)
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)

    result = run_cli_in_repo(repo_root, "tool", "doctor", "--detail", "--repo-root", str(repo_root), "specdown", env=env)
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    specdown = payload["results"]["specdown"]
    doctor = specdown["doctor"]

    assert doctor["doctor_status"] == "ok"
    assert doctor["support_state"] == "upstream-consumed"
    assert doctor["support_sync"]["status"] == "not-tracked"
    assert doctor["detect"]["results"][0]["command"] == "specdown version"
    assert doctor["healthcheck"]["status"] == "not-configured"
    assert doctor["healthcheck"]["skipped"] is True
    assert doctor["provenance"]["install_method"] == "go"
    assert doctor["provenance"]["package_name"] == "github.com/corca-ai/specdown/cmd/specdown"
    assert doctor["release"]["latest_tag"] == "v0.47.2"


@pytest.mark.release_only
def test_tool_repair_agent_browser_previews_and_executes_cleanup(tmp_path: Path, seeded_charness_repo: Path) -> None:
    cleanup_agent_browser_orphans()
    repo_root = clone_seeded_charness_repo(tmp_path, seeded_charness_repo)
    home_root = tmp_path / "home"
    fake_agent_browser = make_fake_agent_browser(tmp_path)
    release_fixture = make_release_fixture(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    pin_state_home(env, home_root)
    env["PATH"] = build_test_path(fake_agent_browser.parent)
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)

    preview = run_cli_in_repo(repo_root, "tool", "repair", "--detail", "--repo-root", str(repo_root), "agent-browser", env=env)
    assert preview.returncode == 0, preview.stderr
    preview_payload = yaml.safe_load(preview.stdout)
    preview_browser = preview_payload["results"]["agent-browser"]
    assert preview_browser["repair"]["status"] == "preview"
    assert preview_browser["repair"]["execute"] is False
    assert "post-hoc mitigation only" in preview_browser["repair"]["caveat"]
    assert preview_browser["repair"]["cleanup"]["preview_only"] is True
    assert preview_browser["doctor"]["doctor_status"] == "ok"
    assert "upstream/unproven" in preview_browser["next_step"]

    executed = run_cli_in_repo(
        repo_root,
        "tool",
        "repair",
        "--detail",
        "--repo-root",
        str(repo_root),
        "--execute",
        "agent-browser",
        env=env,
    )
    assert executed.returncode == 0, executed.stderr
    executed_payload = yaml.safe_load(executed.stdout)
    executed_browser = executed_payload["results"]["agent-browser"]
    assert executed_browser["repair"]["status"] == "executed"
    assert executed_browser["repair"]["execute"] is True
    assert executed_browser["repair"]["cleanup"]["preview_only"] is False
    assert executed_browser["doctor"]["doctor_status"] == "ok"
    assert "post-doctor verification" in executed_browser["next_step"]
    assert "post-hoc mitigation only" in executed_browser["repair"]["caveat"]
    assert "upstream/unproven" in executed_browser["next_step"]
    lock_payload = json.loads((repo_root / "integrations" / "locks" / "agent-browser.json").read_text(encoding="utf-8"))
    assert lock_payload["doctor"]["doctor_status"] == "ok"


@pytest.mark.release_only
def test_tool_repair_reports_unsupported_tools(tmp_path: Path, seeded_charness_repo: Path) -> None:
    repo_root = clone_seeded_charness_repo(tmp_path, seeded_charness_repo)
    env = os.environ.copy()
    pin_state_home(env, tmp_path / "home")
    env["PATH"] = build_test_path()

    result = run_cli_in_repo(repo_root, "tool", "repair", "--repo-root", str(repo_root), "specdown", env=env)

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    specdown = payload["results"]["specdown"]
    assert specdown["repair"]["status"] == "unsupported"
    assert "No repo-owned repair action is declared" in specdown["next_step"]


def test_tool_next_step_prefers_agent_browser_repair_for_cleanup_runtime_drift() -> None:
    module = load_charness_module("charness_tool_repair_next_step_under_test")
    doctor_result = {
        "doctor_status": "unhealthy",
        "healthcheck": {
            "results": [
                {
                    "stdout": json.dumps(
                        {
                            "next_step": "python3 scripts/evidence/agent_browser_runtime_guard.py --repo-root . --cleanup-orphans --execute",
                            "next_step_kind": "cleanup_command",
                        }
                    ),
                }
            ]
        },
    }

    next_step = module.tool_next_step("agent-browser", None, doctor_result, None)

    assert "charness tool repair --execute agent-browser" in next_step


@pytest.mark.release_only
def test_tool_install_executes_glow_install_script_and_refreshes_doctor(tmp_path: Path, seeded_charness_repo: Path) -> None:
    repo_root = clone_seeded_charness_repo(tmp_path, seeded_charness_repo)
    home_root = tmp_path / "home"
    fake_go, gopath = make_fake_go_glow(tmp_path)
    release_fixture = make_release_fixture(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    pin_state_home(env, home_root)
    env["PATH"] = build_test_path(fake_go.parent, home_root / ".local" / "bin")
    env["GOPATH"] = str(gopath)
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)

    result = run_cli_in_repo(repo_root, "tool", "install", "--detail", "--repo-root", str(repo_root), "glow", env=env)
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    glow = payload["results"]["glow"]

    assert glow["install"]["status"] == "installed"
    assert glow["install"]["mode"] == "script"
    assert glow["doctor"]["doctor_status"] == "ok"
    assert glow["doctor"]["provenance"]["install_method"] == "go"
    assert glow["doctor"]["provenance"]["package_name"] == "github.com/charmbracelet/glow/v2"
    assert glow["doctor"]["release"]["latest_tag"] == "v2.1.2"
    assert (home_root / ".local" / "bin" / "glow").is_symlink()
    assert (gopath / "bin" / "glow").is_file()


@pytest.mark.release_only
def test_tool_update_routes_go_provenance_for_specdown(tmp_path: Path, seeded_charness_repo: Path) -> None:
    repo_root = clone_seeded_charness_repo(tmp_path, seeded_charness_repo)
    home_root = tmp_path / "home"
    go_script, specdown_script = make_fake_go_specdown(tmp_path)
    fake_curl, _fake_nose = make_fake_nose(tmp_path)
    release_fixture = make_release_fixture(tmp_path)
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    pin_state_home(env, home_root)
    env["PATH"] = build_test_path(fake_curl.parent, go_script.parent, specdown_script.parent)
    env["GOPATH"] = str(specdown_script.parent.parent)
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)

    result = run_cli_in_repo(
        repo_root,
        "tool",
        "update",
        "--detail",
        "--repo-root",
        str(repo_root),
        "--skip-sync-support",
        "specdown",
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    specdown = payload["results"]["specdown"]
    # This case owns package-manager provenance, not a forced version change:
    # the seeded lock may already report the fake binary's version, making the
    # correctly executed update idempotent (`refreshed`).
    assert specdown["update"]["status"] in {"updated", "refreshed"}
    assert specdown["update"]["mode"] == "package_manager"
    assert specdown["update"]["package_manager"] == "go"
    assert specdown["update"]["package_name"] == "github.com/corca-ai/specdown/cmd/specdown"
    assert specdown["update"]["commands"][0]["command"] == "go install github.com/corca-ai/specdown/cmd/specdown@latest"
    assert specdown["doctor"]["provenance"]["install_method"] == "go"
    lock_payload = json.loads((repo_root / "integrations" / "locks" / "specdown.json").read_text(encoding="utf-8"))
    assert lock_payload["provenance"]["install_method"] == "go"
    assert lock_payload["update"]["mode"] == "package_manager"
    assert lock_payload["update"]["package_manager"] == "go"
    assert lock_payload["update"]["package_name"] == "github.com/corca-ai/specdown/cmd/specdown"
    assert lock_payload["update"]["commands"][0]["command"] == "go install github.com/corca-ai/specdown/cmd/specdown@latest"
