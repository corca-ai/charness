from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module

ROOT = Path(__file__).resolve().parents[1]
_advise_google_workspace_path = import_repo_module(
    ROOT / "skills" / "public" / "gather" / "scripts" / "advise_google_workspace_path.py",
    "skills.public.gather.scripts.advise_google_workspace_path",
)
_advise_slack_path = import_repo_module(
    ROOT / "skills" / "public" / "gather" / "scripts" / "advise_slack_path.py",
    "skills.public.gather.scripts.advise_slack_path",
)


def run_helper(repo: Path, *, path_env: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PATH"] = path_env
    return subprocess.run(
        [
            sys.executable,
            "skills/public/gather/scripts/advise_google_workspace_path.py",
            "--repo-root",
            str(repo),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def seed_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "integrations" / "tools").mkdir(parents=True)
    return repo


def test_advise_google_workspace_path_reports_missing_direct_provider(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path)

    payload = _advise_google_workspace_path.payload_for(repo)

    assert payload["provider"] == "google-workspace"
    assert payload["doctor_status"] == "missing"
    assert "No repo-supported direct Google Workspace CLI provider" in payload["operator_prompt"]


def test_advise_google_workspace_path_reports_none_mode(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path)
    (repo / ".agents").mkdir()
    (repo / ".agents" / "gather-adapter.yaml").write_text(
        "version: 1\ngather_provider:\n  google_workspace:\n    mode: none\n",
        encoding="utf-8",
    )

    payload = _advise_google_workspace_path.payload_for(repo)

    assert payload["provider"] == "google-workspace"
    assert payload["doctor_status"] == "skipped"
    assert "mode=none" in payload["operator_prompt"]


def test_advise_google_workspace_path_reports_host_mediated_mode(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path)
    (repo / ".agents").mkdir()
    (repo / ".agents" / "gather-adapter.yaml").write_text(
        "version: 1\ngather_provider:\n  google_workspace:\n    mode: host-mediated\n",
        encoding="utf-8",
    )

    payload = _advise_google_workspace_path.payload_for(repo)

    assert payload["provider"] == "google-workspace"
    assert payload["doctor_status"] == "skipped"
    assert "host's google_workspace capability command" in payload["operator_prompt"]


def test_advise_google_workspace_path_cli_emits_json(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()

    result = run_helper(repo, path_env=f"{bin_dir}:/usr/bin:/bin")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["provider"] == "google-workspace"
    assert payload["provider_mode"] == "direct-cli"


def test_gather_skill_description_names_concrete_source_triggers() -> None:
    skill_text = (ROOT / "skills" / "public" / "gather" / "SKILL.md").read_text(encoding="utf-8")
    description = next(line for line in skill_text.splitlines() if line.startswith("description: "))

    for trigger in ("Slack thread", "Notion page", "Google Docs", "GitHub content", "arbitrary URL"):
        assert trigger in description


def test_gather_skill_contract_names_browser_mediated_private_source_ladder() -> None:
    skill_text = (ROOT / "skills" / "public" / "gather" / "SKILL.md").read_text(encoding="utf-8")

    assert "advise_slack_path.py" in skill_text
    assert "support/gather-slack/scripts/export-thread.sh" in skill_text
    assert "browser-mediated fallback through `agent-browser`" in skill_text
    assert "official API/export docs before browser automation" in skill_text
    assert "- `Access Mode`" in skill_text
    assert "- `Captured vs Human Confirmation`" in skill_text


def test_advise_slack_path_points_to_gather_slack_wrapper(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    payload = _advise_slack_path.payload_for(repo)

    assert payload["provider"] == "gather-slack"
    assert payload["provider_mode"] == "direct-cli"
    assert payload["wrapper_path"].endswith("skills/support/gather-slack/scripts/export-thread.sh")
    assert payload["runtime_contract_path"].endswith("skills/support/gather-slack/references/runtime-contract.md")
    assert "before browser-mediated private-source fallbacks" in payload["operator_prompt"]
    assert any("charness capability env slack.default" in step for step in payload["next_steps"])


def test_advise_slack_path_cli_emits_json(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = subprocess.run(
        [
            sys.executable,
            "skills/public/gather/scripts/advise_slack_path.py",
            "--repo-root",
            str(repo),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["provider"] == "gather-slack"
    assert payload["provider_mode"] == "direct-cli"


def test_advise_slack_path_honors_host_mediated_adapter(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "gather-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "gather_provider:",
                "  slack:",
                "    mode: host-mediated",
                "",
            ]
        ),
        encoding="utf-8",
    )

    payload = _advise_slack_path.payload_for(repo)

    assert payload["provider_mode"] == "host-mediated"
    assert payload["doctor_status"] == "skipped"
    assert "host's Slack capability command" in payload["operator_prompt"]


def test_gather_capability_needs_include_agent_browser_private_saas_path() -> None:
    payload = json.loads((ROOT / "skills" / "public" / "gather" / "capability-needs.json").read_text(encoding="utf-8"))

    assert {need["logical_id"] for need in payload["capability_needs"]} == {
        "github.default",
        "slack.default",
        "google-workspace.default",
        "agent-browser.default",
    }


def test_agent_browser_manifest_supports_gather_runtime_contract() -> None:
    payload = json.loads((ROOT / "integrations" / "tools" / "agent-browser.json").read_text(encoding="utf-8"))

    assert payload["supports_public_skills"] == ["gather"]
    assert payload["recommendation_role"] == "runtime"
    assert [layer["layer_id"] for layer in payload["config_layers"]] == [
        "agent-browser-saved-auth-state",
        "agent-browser-origin-headers",
        "agent-browser-manual-bootstrap",
    ]
