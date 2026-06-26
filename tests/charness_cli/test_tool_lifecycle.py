from __future__ import annotations

import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
import sys
import textwrap
from pathlib import Path

import pytest

from scripts.control_plane_lifecycle_lib import update_advisory_line
from tests.repo_copy import clone_seeded_charness_repo

from .support import (
    build_test_path,
    clone_seeded_managed_home,
    make_fake_agent_browser,
    make_fake_go_specdown,
    make_fake_npm_agent_browser,
    make_release_fixture,
    make_support_sync_fixture,
    run_cli,
    run_cli_in_repo,
)
from .tool_fakes import make_fake_cautilus, make_fake_nose

ROOT = Path(__file__).resolve().parents[2]


def load_charness_module(module_name: str = "charness_tool_lifecycle_under_test"):
    loader = importlib.machinery.SourceFileLoader(module_name, str(ROOT / "charness"))
    spec = importlib.util.spec_from_loader(module_name, loader)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_agent_browser_runtime_guard_module(module_name: str = "agent_browser_runtime_guard_under_test"):
    loader = importlib.machinery.SourceFileLoader(module_name, str(ROOT / "scripts" / "agent_browser_runtime_guard.py"))
    spec = importlib.util.spec_from_loader(module_name, loader)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_update_advisory_line_without_manifest_route_uses_manual_docs_url() -> None:
    line = update_advisory_line(
        {
            "tool_id": "cautilus",
            "mode": "manual",
            "docs_url": "https://github.com/corca-ai/cautilus/releases",
            "update_advisory": {
                "status": "behind",
                "observed_version": "0.15.4",
                "latest_version": "0.17.1",
                "latest_tag": "v0.17.1",
                "html_url": "https://github.com/corca-ai/cautilus/releases/tag/v0.17.1",
            },
        }
    )

    assert line is not None
    assert "manual update required; see https://github.com/corca-ai/cautilus/releases" in line
    assert "manifest install/update route" not in line


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


def enable_cautilus_adapter(repo_root: Path) -> None:
    adapter = repo_root / ".agents" / "cautilus-adapter.yaml"
    text = adapter.read_text(encoding="utf-8")
    lines = []
    for line in text.splitlines():
        if line.startswith("run_mode:"):
            lines.append("run_mode: adaptive")
        elif line.startswith("disabled_reason:"):
            continue
        else:
            lines.append(line)
    adapter.write_text("\n".join(lines) + "\n", encoding="utf-8")


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
    script.write_text(
        textwrap.dedent(
            f"""\
            #!/usr/bin/env python3
            import os
            import pathlib
            import sys

            gopath = pathlib.Path({str(gopath)!r})
            gobin = os.environ.get("GOBIN")
            install_root = pathlib.Path(gobin) if gobin else gopath / "bin"
            install_root.mkdir(parents=True, exist_ok=True)

            args = sys.argv[1:]
            if args == ["version"]:
                print("go version go1.26.2 linux/arm64")
                raise SystemExit(0)
            if args == ["env", "GOPATH"]:
                print(gopath)
                raise SystemExit(0)
            if args == ["install", "github.com/charmbracelet/glow/v2@latest"]:
                glow = gopath / "bin" / "glow"
                glow.write_text(
                    "\\n".join(
                        [
                            "#!/usr/bin/env python3",
                            "import sys",
                            "args = sys.argv[1:]",
                            "if args == ['--version']:",
                            "    print('glow 2.1.1-test')",
                            "    raise SystemExit(0)",
                            "if args == ['--help']:",
                            "    print('glow help')",
                            "    raise SystemExit(0)",
                            "print('glow runtime')",
                        ]
                    ) + "\\n",
                    encoding="utf-8",
                )
                glow.chmod(0o755)
                target = install_root / "glow"
                if target != glow:
                    if target.exists() or target.is_symlink():
                        target.unlink()
                    target.symlink_to(glow)
                raise SystemExit(0)
            raise SystemExit(1)
            """
        ),
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script, gopath


@pytest.mark.release_only
def test_tool_install_persists_manual_guidance_and_support_state(tmp_path: Path, seeded_charness_repo: Path) -> None:
    repo_root = clone_seeded_charness_repo(tmp_path, seeded_charness_repo)
    enable_cautilus_adapter(repo_root)
    home_root = tmp_path / "home"
    release_fixture = make_release_fixture(tmp_path)
    support_fixture = make_support_sync_fixture(tmp_path)
    plugin_root = home_root / ".codex" / "plugins" / "charness"
    env = os.environ.copy()
    env["HOME"] = str(home_root)
    env["PATH"] = build_test_path()
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)
    env["CHARNESS_SUPPORT_SYNC_FIXTURES"] = str(support_fixture)

    result = run_cli_in_repo(repo_root, "tool", "install", "--repo-root", str(repo_root), "--json", "cautilus", env=env)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    cautilus = payload["results"]["cautilus"]
    assert cautilus["install"]["status"] == "manual"
    assert cautilus["install"]["docs_url"] == "https://github.com/corca-ai/cautilus"
    assert cautilus["install"]["install_url"] == "https://github.com/corca-ai/cautilus/blob/main/install.sh"
    assert cautilus["install"]["release"]["latest_tag"] == "v1.2.3"
    assert cautilus["support"]["status"] == "synced"
    assert cautilus["support"]["materialized_paths"] == ["support/cautilus"]
    assert cautilus["support"]["materialized_base"] == str(plugin_root)
    assert cautilus["doctor"]["doctor_status"] == "missing"
    assert cautilus["doctor"]["doctor_disposition"] == "advisory-install-needed"
    assert cautilus["install"]["repo_followup"]["rendered_command"] == f"cautilus install --repo-root {repo_root}"
    assert cautilus["doctor"]["install_route"]["repo_followup"]["rendered_command"] == (
        f"cautilus install --repo-root {repo_root}"
    )
    assert cautilus["doctor"]["release"]["latest_version"] == "1.2.3"
    assert "Follow-up command: `cautilus install --repo-root" in cautilus["next_step"]
    lock_payload = json.loads((repo_root / "integrations" / "locks" / "cautilus.json").read_text(encoding="utf-8"))
    assert lock_payload["release"]["latest_tag"] == "v1.2.3"
    assert lock_payload["install"]["install_status"] == "manual"
    assert lock_payload["support"]["materialized_paths"] == ["support/cautilus"]
    assert lock_payload["doctor"]["doctor_status"] == "missing"
    assert (plugin_root / "support" / "cautilus" / "SKILL.md").is_file()


@pytest.mark.release_only
def test_tool_install_can_select_quality_validation_recommendations(tmp_path: Path, seeded_charness_repo: Path) -> None:
    repo_root = clone_seeded_charness_repo(tmp_path, seeded_charness_repo)
    release_fixture = make_release_fixture(tmp_path)
    env = os.environ.copy()
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
        "--json",
        "--recommendation-role",
        "validation",
        "--next-skill-id",
        "quality",
        env=env,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["tool_selection"] == {
        "recommend_for_skill": None,
        "recommendation_role": "validation",
        "next_skill_id": "quality",
        "selected_tool_ids": ["cautilus", "gitleaks", "nose", "ruff", "tokei", "vulture"],
    }
    assert payload["tool_ids"] == ["cautilus", "gitleaks", "nose", "ruff", "tokei", "vulture"]
    assert set(payload["results"]) == {"cautilus", "gitleaks", "nose", "ruff", "tokei", "vulture"}


@pytest.mark.release_only
def test_tool_install_recommendation_filter_no_match_does_not_install_all(tmp_path: Path, seeded_charness_repo: Path) -> None:
    repo_root = clone_seeded_charness_repo(tmp_path, seeded_charness_repo)
    release_fixture = make_release_fixture(tmp_path)
    env = os.environ.copy()
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
        "--json",
        "--recommendation-role",
        "validation",
        "--next-skill-id",
        "nonexistent-skill",
        env=env,
    )

    assert result.returncode == 1
    assert "No tools matched recommendation filters" in result.stderr


@pytest.mark.release_only
def test_installed_cli_tool_install_materializes_cautilus_support(tmp_path: Path, seeded_managed_home: dict[str, Path]) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    enable_cautilus_adapter(home_root / ".agents" / "src" / "charness")
    release_fixture = make_release_fixture(tmp_path)
    support_fixture = make_support_sync_fixture(tmp_path)
    plugin_root = home_root / ".codex" / "plugins" / "charness"
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)
    env["CHARNESS_SUPPORT_SYNC_FIXTURES"] = str(support_fixture)

    result = run_cli("tool", "install", "--home-root", str(home_root), "--json", "cautilus", env=env)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    cautilus = payload["results"]["cautilus"]
    managed_repo = home_root / ".agents" / "src" / "charness"

    assert payload["managed_checkout"] is True
    assert payload["repo_root"] == str(managed_repo)
    assert cautilus["install"]["status"] == "manual"
    assert cautilus["install"]["install_url"] == "https://github.com/corca-ai/cautilus/blob/main/install.sh"
    assert cautilus["install"]["release"]["latest_tag"] == "v1.2.3"
    assert cautilus["support"]["status"] == "synced"
    assert cautilus["support"]["materialized_paths"] == ["support/cautilus"]
    assert cautilus["doctor"]["doctor_status"] == "missing"
    assert (plugin_root / "support" / "cautilus" / "SKILL.md").is_file()

    lock_payload = json.loads((managed_repo / "integrations" / "locks" / "cautilus.json").read_text(encoding="utf-8"))
    assert lock_payload["install"]["install_status"] == "manual"
    assert lock_payload["support"]["materialized_paths"] == ["support/cautilus"]
    assert lock_payload["doctor"]["doctor_status"] == "missing"


@pytest.mark.release_only
def test_installed_cli_tool_doctor_reports_ok_for_cautilus_with_binary_and_support(
    tmp_path: Path, seeded_managed_home: dict[str, Path]
) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    enable_cautilus_adapter(home_root / ".agents" / "src" / "charness")
    release_fixture = make_release_fixture(tmp_path)
    support_fixture = make_support_sync_fixture(tmp_path)
    plugin_root = home_root / ".codex" / "plugins" / "charness"
    fake_cautilus = make_fake_cautilus(tmp_path)
    env["PATH"] = build_test_path(fake_cautilus.parent)
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)
    env["CHARNESS_SUPPORT_SYNC_FIXTURES"] = str(support_fixture)

    sync_result = run_cli("tool", "sync-support", "--home-root", str(home_root), "--json", "cautilus", env=env)
    assert sync_result.returncode == 0, sync_result.stderr

    doctor_result = run_cli("tool", "doctor", "--home-root", str(home_root), "--json", "cautilus", env=env)
    assert doctor_result.returncode == 0, doctor_result.stderr
    payload = json.loads(doctor_result.stdout)
    cautilus = payload["results"]["cautilus"]["doctor"]

    assert cautilus["doctor_status"] == "ok"
    assert cautilus["support_state"] == "upstream-consumed"
    assert cautilus["support_sync"]["status"] == "ok"
    assert cautilus["support_discovery"]["status"] == "materialized"
    assert cautilus["support_discovery"]["intent_triggers"] == [
        "evaluator-backed behavior review",
        "behavior evaluation",
        "behavior review",
        "prompt behavior regression",
        "instruction behavior regression",
        "baseline compare",
        "cautilus eval",
        "cautilus scenario",
        "operator reading test",
        "프롬프트 회귀",
        "동작 평가",
    ]
    assert cautilus["support_discovery"]["support_skill_path"] == str(plugin_root / "support" / "cautilus" / "SKILL.md")
    assert cautilus["support_discovery"]["materialized_kind"] == "installed-plugin-copy"
    assert cautilus["release"]["latest_tag"] == "v1.2.3"


@pytest.mark.release_only
def test_installed_cli_tool_sync_support_reports_materialized_support_and_binary_gap(
    tmp_path: Path, seeded_managed_home: dict[str, Path]
) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    enable_cautilus_adapter(home_root / ".agents" / "src" / "charness")
    release_fixture = make_release_fixture(tmp_path)
    support_fixture = make_support_sync_fixture(tmp_path)
    plugin_root = home_root / ".codex" / "plugins" / "charness"
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)
    env["CHARNESS_SUPPORT_SYNC_FIXTURES"] = str(support_fixture)

    sync_result = run_cli("tool", "sync-support", "--home-root", str(home_root), "--json", "cautilus", env=env)
    assert sync_result.returncode == 0, sync_result.stderr
    payload = json.loads(sync_result.stdout)
    cautilus = payload["results"]["cautilus"]

    assert cautilus["support"]["status"] == "synced"
    assert cautilus["support"]["materialized_paths"] == ["support/cautilus"]
    assert cautilus["support"]["materialized_base"] == str(plugin_root)
    assert cautilus["support"]["discovery_stub_path"] is None
    assert cautilus["support"]["intent_triggers"] == [
        "evaluator-backed behavior review",
        "behavior evaluation",
        "behavior review",
        "prompt behavior regression",
        "instruction behavior regression",
        "baseline compare",
        "cautilus eval",
        "cautilus scenario",
        "operator reading test",
        "프롬프트 회귀",
        "동작 평가",
    ]
    assert cautilus["doctor"]["doctor_status"] == "missing"
    assert cautilus["doctor"]["doctor_disposition"] == "advisory-install-needed"
    assert cautilus["doctor"]["install_route"]["mode"] == "manual"
    assert cautilus["doctor"]["install_route"]["docs_url"] == "https://github.com/corca-ai/cautilus"
    assert cautilus["doctor"]["install_route"]["install_url"] == "https://github.com/corca-ai/cautilus/blob/main/install.sh"
    assert cautilus["doctor"]["install_route"]["repo_followup"]["rendered_command"] == (
        f"cautilus install --repo-root {home_root / '.agents' / 'src' / 'charness'}"
    )
    assert cautilus["doctor"]["support_discovery"]["status"] == "materialized"
    assert cautilus["doctor"]["support_discovery"]["support_skill_path"] == str(plugin_root / "support" / "cautilus" / "SKILL.md")
    assert cautilus["doctor"]["support_discovery"]["materialized_kind"] == "installed-plugin-copy"
    assert cautilus["doctor"]["install_route"]["commands"] == []
    assert "Support skill materialization for `cautilus` was refreshed under support/cautilus" in cautilus["next_step"]
    assert "the standalone binary is still missing" in cautilus["next_step"]
    assert "Install docs: https://github.com/corca-ai/cautilus/blob/main/install.sh" in cautilus["next_step"]
    assert "Docs: https://github.com/corca-ai/cautilus" in cautilus["next_step"]
    assert f"Support skill is available at `{plugin_root / 'support' / 'cautilus' / 'SKILL.md'}`." in cautilus["next_step"]
    assert "installed Charness plugin support surface" in cautilus["next_step"]
    assert "Follow-up command: `cautilus install --repo-root" in cautilus["next_step"]


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
    env["PATH"] = build_test_path(fake_agent_browser.parent, fake_npm.parent)
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)
    env["CHARNESS_SUPPORT_SYNC_FIXTURES"] = str(support_fixture)
    env["CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS"] = "1"

    result = run_cli_in_repo(repo_root, "tool", "update", "--repo-root", str(repo_root), "--json", "agent-browser", env=env)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    browser = payload["results"]["agent-browser"]
    assert browser["update"]["status"] == "updated"
    assert browser["update"]["mode"] == "script"
    assert browser["update"]["commands"][0]["command"] == "npm install -g agent-browser@latest"
    assert browser["update"]["release"]["latest_tag"] == "v0.25.3"
    assert browser["support"]["status"] == "synced"
    assert browser["doctor"]["doctor_status"] == "ok"
    lock_payload = json.loads((repo_root / "integrations" / "locks" / "agent-browser.json").read_text(encoding="utf-8"))
    assert lock_payload["release"]["latest_tag"] == "v0.25.3"
    assert lock_payload["update"]["update_status"] == "updated"
    assert lock_payload["update"]["mode"] == "script"
    assert lock_payload["update"]["commands"][0]["command"] == "npm install -g agent-browser@latest"
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
    env["PATH"] = f"{npm_script.parent}:{browser_link.parent}:{env.get('PATH', '')}"
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)
    env["CHARNESS_SUPPORT_SYNC_FIXTURES"] = str(support_fixture)
    env["CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS"] = "1"

    result = run_cli_in_repo(repo_root, "tool", "update", "--repo-root", str(repo_root), "--json", "agent-browser", env=env)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
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
    env["PATH"] = build_test_path(fake_curl.parent, go_script.parent, specdown_script.parent)
    env["GOPATH"] = str(specdown_script.parent.parent)
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)

    result = run_cli_in_repo(repo_root, "tool", "doctor", "--repo-root", str(repo_root), "--json", "specdown", env=env)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
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
    env["PATH"] = build_test_path(fake_agent_browser.parent)
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)

    preview = run_cli_in_repo(repo_root, "tool", "repair", "--repo-root", str(repo_root), "--json", "agent-browser", env=env)
    assert preview.returncode == 0, preview.stderr
    preview_payload = json.loads(preview.stdout)
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
        "--repo-root",
        str(repo_root),
        "--execute",
        "--json",
        "agent-browser",
        env=env,
    )
    assert executed.returncode == 0, executed.stderr
    executed_payload = json.loads(executed.stdout)
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
    env["PATH"] = build_test_path()

    result = run_cli_in_repo(repo_root, "tool", "repair", "--repo-root", str(repo_root), "--json", "specdown", env=env)

    assert result.returncode == 1
    payload = json.loads(result.stdout)
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
                            "next_step": "python3 scripts/agent_browser_runtime_guard.py --repo-root . --cleanup-orphans --execute",
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
    env["PATH"] = build_test_path(fake_go.parent, home_root / ".local" / "bin")
    env["GOPATH"] = str(gopath)
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)

    result = run_cli_in_repo(repo_root, "tool", "install", "--repo-root", str(repo_root), "--json", "glow", env=env)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
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
    env["PATH"] = build_test_path(fake_curl.parent, go_script.parent, specdown_script.parent)
    env["GOPATH"] = str(specdown_script.parent.parent)
    env["CHARNESS_RELEASE_PROBE_FIXTURES"] = str(release_fixture)

    result = run_cli_in_repo(
        repo_root,
        "tool",
        "update",
        "--repo-root",
        str(repo_root),
        "--json",
        "--skip-sync-support",
        "specdown",
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    specdown = payload["results"]["specdown"]
    assert specdown["update"]["status"] == "updated"
    assert specdown["update"]["mode"] == "script"
    assert specdown["update"]["commands"][0]["command"] == "curl -fsSL https://raw.githubusercontent.com/corca-ai/specdown/main/install.sh | sh"
    assert specdown["doctor"]["provenance"]["install_method"] == "go"
    lock_payload = json.loads((repo_root / "integrations" / "locks" / "specdown.json").read_text(encoding="utf-8"))
    assert lock_payload["provenance"]["install_method"] == "go"
    assert lock_payload["update"]["mode"] == "script"
    assert lock_payload["update"]["commands"][0]["command"] == "curl -fsSL https://raw.githubusercontent.com/corca-ai/specdown/main/install.sh | sh"
