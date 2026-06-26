from __future__ import annotations

import json
import sys
from pathlib import Path

from scripts.operator_acceptance_lib import SHARED_START_CANDIDATES, synthesize_operator_acceptance
from scripts.validate_quality_closeout_contract import validate_quality_closeout_contract
from tests.script_loader import load_script_module

from .support import ROOT

LIST_CAPABILITIES = load_script_module(
    "tests.quality_gates.script_behaviors_list_capabilities",
    ROOT / "skills/public/find-skills/scripts/list_capabilities.py",
)
SURVEY_VERIFICATION = load_script_module(
    "tests.quality_gates.script_behaviors_survey_verification",
    ROOT / "skills/public/impl/scripts/survey_verification.py",
)
CURRENT_RELEASE = load_script_module(
    "tests.quality_gates.script_behaviors_current_release",
    ROOT / "skills/public/release/scripts/current_release.py",
)
SYNTHESIZE_OPERATOR_ACCEPTANCE = load_script_module(
    "tests.quality_gates.script_behaviors_synthesize_operator_acceptance",
    ROOT / "skills/public/setup/scripts/synthesize_operator_acceptance.py",
)


def test_release_current_release_reports_packaging_version(monkeypatch, capsys) -> None:
    payload = CURRENT_RELEASE.build_payload(ROOT)
    expected = json.loads((ROOT / "packaging" / "charness.json").read_text(encoding="utf-8"))["version"]
    assert payload["package_id"] == "charness"
    assert payload["surface_versions"]["packaging_manifest"] == expected
    assert payload["checked_in_plugin_root"].endswith("plugins/charness")
    assert payload["fresh_checkout_probes"]["status"] in {"configured", "not_configured"}

    monkeypatch.setattr(sys, "argv", ["current_release.py", "--repo-root", str(ROOT)])
    CURRENT_RELEASE.main()
    cli_payload = json.loads(capsys.readouterr().out)
    assert cli_payload["package_id"] == "charness"
    assert cli_payload["surface_versions"]["packaging_manifest"] == expected


def test_setup_synthesize_operator_acceptance_outputs_tiered_draft(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    (repo / "docs" / "specs").mkdir(parents=True)
    (repo / "scripts").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "docs" / "handoff.md").write_text("# Handoff\n", encoding="utf-8")
    (repo / "docs" / "roadmap.md").write_text("# Roadmap\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
    (repo / "scripts" / "run-quality.sh").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    (repo / "docs" / "specs" / "demo.spec.md").write_text(
        "\n".join(
            [
                "# Demo Spec",
                "",
                "## Local Smoke",
                "",
                "### Functional Check",
                "",
                "```bash",
                "./scripts/run-quality.sh",
                "```",
                "",
                "## Hosted Publish",
                "",
                "### Functional Check",
                "",
                "```bash",
                "gh workflow run release.yml",
                "```",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    payload = synthesize_operator_acceptance(
        repo_root=repo,
        output_path=Path("docs/operator-acceptance.md"),
        write=False,
        force=False,
    )
    assert payload["shared_start_commands"] == [command for command, _path in SHARED_START_CANDIDATES]
    assert payload["acceptance_buckets"]["cheap_first"][0]["commands"] == "./scripts/run-quality.sh"
    assert "gh workflow run release.yml" in payload["acceptance_buckets"]["external_or_costly"][0]["commands"]
    assert payload["acceptance_buckets"]["human_judgment"][0]["source_path"] == "docs/handoff.md"
    assert "## Cheap First" in payload["markdown"]
    assert "## External Or Costly Checks" in payload["markdown"]
    assert "## Human Judgment" in payload["markdown"]

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "synthesize_operator_acceptance.py",
            "--repo-root",
            str(repo),
            "--json",
        ],
    )
    SYNTHESIZE_OPERATOR_ACCEPTANCE.main()
    cli_payload = json.loads(capsys.readouterr().out)
    assert cli_payload["acceptance_buckets"]["cheap_first"][0]["commands"] == "./scripts/run-quality.sh"
    assert "## Environment Prerequisites" in cli_payload["markdown"]


def test_find_skills_lists_adapter_configured_trusted_roots(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    local_skill_dir = repo / "skills" / "public" / "local-demo"
    trusted_skill_dir = repo / "vendor" / "trusted-skills" / "trusted-demo"
    adapter_dir = repo / ".agents"
    local_skill_dir.mkdir(parents=True)
    trusted_skill_dir.mkdir(parents=True)
    adapter_dir.mkdir(parents=True)

    (local_skill_dir / "SKILL.md").write_text(
        "\n".join(["---", "name: local-demo", 'description: "Local demo skill."', "---", "", "# Local Demo"]),
        encoding="utf-8",
    )
    (trusted_skill_dir / "SKILL.md").write_text(
        "\n".join(["---", "name: trusted-demo", 'description: "Trusted demo skill."', "---", "", "# Trusted Demo"]),
        encoding="utf-8",
    )
    (adapter_dir / "find-skills-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "language: en",
                "output_dir: charness-artifacts/find-skills",
                "trusted_skill_roots:",
                "- vendor/trusted-skills",
                "prefer_local_first: true",
                "allow_external_registry: false",
                "",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(sys, "argv", ["list_capabilities.py", "--repo-root", str(repo)])
    LIST_CAPABILITIES.main()
    payload = json.loads(capsys.readouterr().out)
    assert payload["public_skills"][0]["id"] == "local-demo"
    assert payload["trusted_skills"][0]["id"] == "trusted-demo"


def test_impl_survey_reports_broken_preferred_skill_symlink(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    adapter_dir = repo / ".agents"
    skills_dir = adapter_dir / "skills"
    adapter_dir.mkdir(parents=True)
    skills_dir.mkdir(parents=True)

    (adapter_dir / "impl-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "language: en",
                "output_dir: charness-artifacts/impl",
                "verification_tools:",
                "- cmd:python3",
                "- skill:agent-browser",
                "ui_verification_tools:",
                "- skill:agent-browser",
                "verification_install_proposals:",
                "- Install the preferred browser verifier before closing UI work.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (skills_dir / "agent-browser").symlink_to(repo / "missing-agent-browser")

    monkeypatch.setattr(sys, "argv", ["survey_verification.py", "--repo-root", str(repo)])
    SURVEY_VERIFICATION.main()
    payload = json.loads(capsys.readouterr().out)
    assert payload["missing_tools"] == ["skill:agent-browser"]
    assert payload["missing_ui_tools"] == ["skill:agent-browser"]
    assert payload["tool_checks"][1]["warning"].startswith("Broken skill symlink:")
    assert "Repo-specific verification install proposals are available." in payload["warnings"]


def test_quality_skill_discloses_advisory_and_prompt_asset_root_boundary() -> None:
    dispatch = (
        ROOT / "skills" / "public" / "quality" / "references" / "inventory-dispatch.md"
    ).read_text(encoding="utf-8")
    prompt_policy = (
        ROOT / "skills" / "public" / "quality" / "references" / "prompt-asset-policy.md"
    ).read_text(encoding="utf-8")

    assert "`prompt_asset_roots: []` only means no canonical asset root is declared" in dispatch
    assert "must not suppress inline prompt/content inventory" in prompt_policy

    validate_quality_closeout_contract(ROOT)
