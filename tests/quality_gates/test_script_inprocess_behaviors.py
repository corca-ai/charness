from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

from scripts import capability_catalog as CAPABILITY_CATALOG
from scripts.gates_support.operator_acceptance_lib import SHARED_START_CANDIDATES, synthesize_operator_acceptance
from tests.script_loader import load_script_module
from tools.validate_quality_closeout_contract import validate_quality_closeout_contract

from .support import ROOT

SURVEY_VERIFICATION = load_script_module(
    "tests.quality_gates.script_behaviors_survey_verification",
    ROOT / "skills/public/impl/scripts/survey_verification.py",
)
CURRENT_RELEASE = load_script_module(
    "tests.quality_gates.script_behaviors_current_release",
    ROOT / "skills/public/release/scripts/current_release.py",
)
FRESH_CHECKOUT_PROBES = load_script_module(
    "tests.quality_gates.script_behaviors_fresh_checkout_probes",
    ROOT / "skills/public/release/scripts/check_fresh_checkout_probes.py",
)
SYNTHESIZE_OPERATOR_ACCEPTANCE = load_script_module(
    "tests.quality_gates.script_behaviors_synthesize_operator_acceptance",
    ROOT / "skills/public/setup/scripts/synthesize_operator_acceptance.py",
)
PLAN_RELEASE_RUN = load_script_module(
    "tests.quality_gates.script_behaviors_plan_release_run",
    ROOT / "skills/public/release/scripts/plan_release_run.py",
)


def test_release_current_release_reports_packaging_version(monkeypatch, capsys) -> None:
    payload = CURRENT_RELEASE.build_payload(ROOT)
    expected = json.loads((ROOT / "packaging" / "charness.json").read_text(encoding="utf-8"))[
        "version"
    ]
    assert payload["package_id"] == "charness"
    assert payload["surface_versions"]["packaging_manifest"] == expected
    assert payload["materialized_plugin_root"].endswith("plugins/charness")
    # `current_release` is a status dump; it deliberately does NOT run the probes,
    # so the block it embeds is `not_established`, never a probe verdict.
    # `configured` used to be that word, and it read as a satisfied probe run.
    fresh_checkout = payload["fresh_checkout_probes"]
    assert fresh_checkout["status"] in {"not_established", "not_configured"}
    if fresh_checkout["status"] == "not_established":
        assert "probe_results" not in fresh_checkout

    monkeypatch.setattr(sys, "argv", ["current_release.py", "--repo-root", str(ROOT)])
    CURRENT_RELEASE.main()
    cli_payload = yaml.safe_load(capsys.readouterr().out)
    assert cli_payload["package_id"] == "charness"
    assert cli_payload["surface_versions"]["packaging_manifest"] == expected


def test_release_fresh_checkout_detail_emits_payload(tmp_path: Path, monkeypatch) -> None:
    payload = {
        "status": "configured",
        "fresh_checkout_probes": ["echo ok"],
        "probe_results": [],
        "blockers": [],
    }
    emitted: list[dict[str, object]] = []

    monkeypatch.setattr(
        FRESH_CHECKOUT_PROBES,
        "build_payload",
        lambda _root, *, run_probes: payload,
    )
    monkeypatch.setattr(
        FRESH_CHECKOUT_PROBES.yaml_output,
        "emit_yaml",
        emitted.append,
    )
    timeout_kwargs: dict[str, object] = {}
    monkeypatch.setattr(
        FRESH_CHECKOUT_PROBES.SKILL_RUNTIME,
        "arm_cli_timeout",
        lambda **kwargs: timeout_kwargs.update(kwargs) or (lambda: None),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "check_fresh_checkout_probes.py",
            "--repo-root",
            str(tmp_path),
            "--detail",
        ],
    )

    assert FRESH_CHECKOUT_PROBES.main() == 0
    assert emitted == [payload]
    assert timeout_kwargs == {
        "label": "release fresh checkout probes",
        "default_seconds": 0,
    }


def test_release_run_planner_sets_its_own_timeout_budget(tmp_path: Path, monkeypatch) -> None:
    """The planner must not inherit the shared 10s script default.

    Measured unloaded on this repo the planner takes 7.00s / 6.90s / 8.81s, so 10s is
    a 1.1x margin against its own typical cost. Every gate lane here runs in parallel,
    so under `pytest -n` it is killed mid-report and
    `test_public_skill_yaml_output_contract.test_detail_yaml_is_structured` fails on
    the empty stdout -- a check that passes only on an idle machine.

    Pinned the same way the sibling `check_fresh_checkout_probes` budget is: on the
    kwargs handed to `arm_cli_timeout`, so a silent revert to the shared default is a
    failing test rather than a flake somebody re-runs until it goes green.
    """
    emitted: list[dict[str, object]] = []
    timeout_kwargs: dict[str, object] = {}

    monkeypatch.setattr(PLAN_RELEASE_RUN, "build_plan", lambda _args: {"next_action": {}})
    monkeypatch.setattr(PLAN_RELEASE_RUN.yaml_output, "emit_yaml", emitted.append)
    monkeypatch.setattr(
        PLAN_RELEASE_RUN.SKILL_RUNTIME,
        "arm_cli_timeout",
        lambda **kwargs: timeout_kwargs.update(kwargs) or (lambda: None),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["plan_release_run.py", "--repo-root", str(tmp_path), "--detail"],
    )

    assert PLAN_RELEASE_RUN.main() == 0
    assert timeout_kwargs["label"] == "release run planner"
    budget = timeout_kwargs["default_seconds"]
    # Bounded on BOTH sides, and the ceiling is a real assertion rather than a comment
    # claiming one. The first cut of this said "bounded on BOTH sides" over a floor and
    # a non-zero check only -- `default_seconds=86400` would have passed both while
    # being the disabled timeout the sentence says it rejects. A bounded review caught
    # it, and it is the same prose-over-code defect this very commit repairs in
    # `check_skill_ownership_overlap.py`: a comment asserting a stronger invariant than
    # the code holds.
    assert isinstance(budget, (int, float)) and budget > 0, (
        "the planner must declare a finite budget, not disable the timeout"
    )
    assert budget >= 30, (
        f"budget {budget}s leaves no room over the planner's measured ~7-9s cost "
        "under the parallel load every gate lane creates"
    )
    assert budget <= 300, (
        f"budget {budget}s is a disabled timeout wearing a number. This command's work "
        "IS bounded; a report-only planner running for minutes is a defect it should "
        "surface, not wait out."
    )


def test_setup_synthesize_operator_acceptance_outputs_tiered_draft(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    (repo / "docs" / "specs").mkdir(parents=True)
    (repo / "scripts").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "docs" / "index.md").write_text("# Docs\n", encoding="utf-8")
    (repo / "docs" / "roadmap.md").write_text("# Roadmap\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
    (repo / "scripts" / "run-quality.sh").write_text(
        "#!/usr/bin/env bash\nexit 0\n", encoding="utf-8"
    )
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
    assert payload["shared_start_commands"] == [
        command for command, _path in SHARED_START_CANDIDATES
    ]
    assert payload["acceptance_buckets"]["cheap_first"][0]["commands"] == "./scripts/run-quality.sh"
    assert (
        "gh workflow run release.yml"
        in payload["acceptance_buckets"]["external_or_costly"][0]["commands"]
    )
    assert payload["acceptance_buckets"]["human_judgment"][0]["source_path"] == "docs/index.md"
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
        ],
    )
    SYNTHESIZE_OPERATOR_ACCEPTANCE.main()
    cli_payload = yaml.safe_load(capsys.readouterr().out)
    assert (
        cli_payload["acceptance_buckets"]["cheap_first"][0]["commands"]
        == "./scripts/run-quality.sh"
    )
    assert "## Environment Prerequisites" in cli_payload["markdown"]


def test_capability_catalog_lists_adapter_configured_trusted_roots(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    local_skill_dir = repo / "skills" / "public" / "local-demo"
    trusted_skill_dir = repo / "vendor" / "trusted-skills" / "trusted-demo"
    adapter_dir = repo / ".agents"
    local_skill_dir.mkdir(parents=True)
    trusted_skill_dir.mkdir(parents=True)
    adapter_dir.mkdir(parents=True)

    (local_skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: local-demo",
                'description: "Local demo skill."',
                "---",
                "",
                "# Local Demo",
            ]
        ),
        encoding="utf-8",
    )
    (trusted_skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: trusted-demo",
                'description: "Trusted demo skill."',
                "---",
                "",
                "# Trusted Demo",
            ]
        ),
        encoding="utf-8",
    )
    (adapter_dir / "capability-catalog-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "language: en",
                "output_dir: charness-artifacts/capability-catalog",
                "trusted_skill_roots:",
                "- vendor/trusted-skills",
                "prefer_local_first: true",
                "allow_external_registry: false",
                "",
            ]
        ),
        encoding="utf-8",
    )

    payload = CAPABILITY_CATALOG.list_catalog(repo)["inventory"]
    assert payload["public_skills"][0]["id"] == "local-demo"
    assert payload["trusted_skills"][0]["id"] == "trusted-demo"


def test_impl_survey_reports_broken_preferred_skill_symlink(
    tmp_path: Path, monkeypatch, capsys
) -> None:
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
    # `survey_verification.py` emits YAML since the `--json` removal. YAML is a JSON
    # superset, so this also reads the compact-JSON fallback used without PyYAML.
    payload = yaml.safe_load(capsys.readouterr().out)
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
