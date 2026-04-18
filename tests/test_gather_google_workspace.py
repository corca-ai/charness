from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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
    shutil.copy2(ROOT / "integrations" / "tools" / "gws-cli.json", repo / "integrations" / "tools" / "gws-cli.json")
    return repo


def test_advise_google_workspace_path_reports_ready_gws_cli(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "gws").write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                'if [[ "${1:-}" == "--version" ]]; then',
                '  echo "gws 0.18.1"',
                'elif [[ "${1:-}" == "auth" && "${2:-}" == "--help" ]]; then',
                '  echo "login"',
                'elif [[ "${1:-}" == "auth" && "${2:-}" == "status" ]]; then',
                '  echo "{}"',
                "else",
                "  exit 1",
                "fi",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (bin_dir / "gws").chmod(0o755)

    result = run_helper(repo, path_env=f"{bin_dir}:/usr/bin:/bin")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["provider"] == "gws-cli"
    assert payload["doctor_status"] == "ok"
    assert payload["operator_prompt"] == "Use the authenticated `gws` CLI path for private Google Workspace gather."


def test_advise_google_workspace_path_reports_missing_gws_cli(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path)
    empty_bin = tmp_path / "empty-bin"
    empty_bin.mkdir()

    result = run_helper(repo, path_env=f"{empty_bin}:/usr/bin:/bin")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["doctor_status"] == "missing"
    assert any("Install `gws`" in step for step in payload["next_steps"])


def test_gather_skill_description_names_concrete_source_triggers() -> None:
    skill_text = (ROOT / "skills" / "public" / "gather" / "SKILL.md").read_text(encoding="utf-8")
    description = next(line for line in skill_text.splitlines() if line.startswith("description: "))

    for trigger in ("Slack thread", "Notion page", "Google Docs", "GitHub content", "arbitrary URL"):
        assert trigger in description


def test_gather_skill_contract_names_browser_mediated_private_source_ladder() -> None:
    skill_text = (ROOT / "skills" / "public" / "gather" / "SKILL.md").read_text(encoding="utf-8")

    assert "browser-mediated fallback through `agent-browser`" in skill_text
    assert "official API/export docs before browser automation" in skill_text
    assert "- `Access Mode`" in skill_text
    assert "- `Captured vs Human Confirmation`" in skill_text


def test_gather_capability_needs_include_agent_browser_private_saas_path() -> None:
    payload = json.loads((ROOT / "skills" / "public" / "gather" / "capability-needs.json").read_text(encoding="utf-8"))

    assert {need["logical_id"] for need in payload["capability_needs"]} == {
        "github.default",
        "slack.default",
        "gws.default",
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
