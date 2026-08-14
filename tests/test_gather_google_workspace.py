from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import yaml

from runtime_bootstrap import import_repo_module

ROOT = Path(__file__).resolve().parents[1]
GATHER_SKILL = (ROOT / "skills" / "public" / "gather" / "SKILL.md").read_text(encoding="utf-8")
_advise_google_workspace_path = import_repo_module(
    ROOT / "skills" / "public" / "gather" / "scripts" / "advise_google_workspace_path.py",
    "skills.public.gather.scripts.advise_google_workspace_path",
)


def run_script_main(module, monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", [f"{module.__name__}.py", *args])
    try:
        result = module.main()
        returncode = result if isinstance(result, int) else 0
    except SystemExit as exc:
        returncode = exc.code if isinstance(exc.code, int) else 1
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=returncode, stdout=captured.out, stderr=captured.err)


def seed_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "integrations" / "tools").mkdir(parents=True)
    return repo


def test_advise_google_workspace_path_defaults_to_none(tmp_path: Path) -> None:
    # gather is public-source only: with no adapter, google_workspace defaults to
    # `none` and stops with a missing-capability explanation instead of reaching
    # for a credentialed provider path.
    repo = seed_repo(tmp_path)

    payload = _advise_google_workspace_path.payload_for(repo)

    assert payload["provider"] == "google-workspace"
    assert payload["provider_mode"] == "none"
    assert payload["doctor_status"] == "skipped"
    assert "mode=none" in payload["operator_prompt"]


def test_advise_google_workspace_path_reports_missing_under_explicit_direct_cli(tmp_path: Path) -> None:
    # There is no repo-owned Google Workspace direct CLI, so an explicit direct-cli
    # request still degrades to the missing-direct-provider guidance.
    repo = seed_repo(tmp_path)
    (repo / ".agents").mkdir()
    (repo / ".agents" / "gather-adapter.yaml").write_text(
        "version: 1\ngather_provider:\n  google_workspace:\n    mode: direct-cli\n",
        encoding="utf-8",
    )

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


def test_advise_google_workspace_path_cli_emits_yaml(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = seed_repo(tmp_path)

    result = run_script_main(
        _advise_google_workspace_path,
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["provider"] == "google-workspace"
    assert payload["provider_mode"] == "none"


def test_gather_skill_description_is_public_source_only() -> None:
    description = next(line for line in GATHER_SKILL.splitlines() if line.startswith("description: "))

    for trigger in ("public web page", "GitHub content", "arbitrary URL", "public-source only"):
        assert trigger in description
    # Credentialed org data is out of scope: the description must not advertise
    # gather as a Slack/Notion acquisition tool.
    assert "Slack thread" not in description
    assert "Notion page" not in description


def test_gather_skill_contract_is_public_source_only() -> None:
    # Plain gather is public-source only; the generic body must NOT hard-name a
    # credentialed provider CLI/token path (the discovery leak #417/#418 fix).
    assert "public-source only" in GATHER_SKILL
    assert "advise_slack_path.py" not in GATHER_SKILL
    assert "SLACK_BOT_TOKEN" not in GATHER_SKILL
    assert "support/gather-slack" not in GATHER_SKILL
    assert "browser-mediated fallback through `agent-browser`" in GATHER_SKILL
    assert "official API/export docs before browser automation" in GATHER_SKILL
    assert "- `Access Mode`" in GATHER_SKILL
    assert "- `Captured vs Human Confirmation`" in GATHER_SKILL


def test_gather_capability_needs_are_public_source_only() -> None:
    payload = json.loads((ROOT / "skills" / "public" / "gather" / "capability-needs.json").read_text(encoding="utf-8"))

    logical_ids = {need["logical_id"] for need in payload["capability_needs"]}
    assert logical_ids == {
        "github.default",
        "google-workspace.default",
        "agent-browser.default",
    }
    # Credentialed Slack/Notion runtimes are removed: gather declares no such need.
    assert "slack.default" not in logical_ids


def test_agent_browser_manifest_supports_gather_runtime_contract() -> None:
    payload = json.loads((ROOT / "integrations" / "tools" / "agent-browser.json").read_text(encoding="utf-8"))

    assert payload["supports_public_skills"] == ["gather"]
    assert payload["recommendation_role"] == "runtime"
    assert [layer["layer_id"] for layer in payload["config_layers"]] == [
        "agent-browser-saved-auth-state",
        "agent-browser-origin-headers",
        "agent-browser-manual-bootstrap",
    ]
