from __future__ import annotations

import re
import runpy
import sys
from pathlib import Path

import pytest
import yaml

from scripts import validate_quality_reference_catalog as catalog_validator
from scripts.validate_quality_reference_catalog import (
    ValidationError,
    validate_quality_reference_catalog,
)

from .seeding_support import load_module
from .support import ROOT, run_script

SCRIPT = "skills/public/quality/scripts/plan_quality_run.py"
SCRIPT_PATH = ROOT / SCRIPT
CATALOG = ROOT / "skills" / "public" / "quality" / "references" / "catalog.yaml"

PLAN = load_module("quality_run_plan_under_test", SCRIPT_PATH)


def _assert_help_pairs(output: str, expected_pairs: dict[str, str]) -> None:
    """Assert each option's wrapped argparse block contains its own help text."""
    for option, fragment in expected_pairs.items():
        match = re.search(rf"^  {re.escape(option)}\b.*$", output, re.MULTILINE)
        assert match, f"missing help option: {option}"
        next_option = re.search(r"^  --[a-z][a-z-]*\b", output[match.end() :], re.MULTILINE)
        end = match.end() + next_option.start() if next_option else len(output)
        option_block = re.sub(r"\s+", " ", output[match.start() : end])
        assert fragment in option_block, f"missing help for {option}: {fragment}"


def test_quality_run_plan_help_describes_repo_root_and_detail(
    capsys, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "argv", ["plan_quality_run.py", "--help"])

    with pytest.raises(SystemExit) as excinfo:
        PLAN.main()

    assert excinfo.value.code == 0
    _assert_help_pairs(
        capsys.readouterr().out,
        {
            "--repo-root": "Repository root to inspect for skills and quality inputs.",
            "--detail": "Emit the full quality run plan as YAML.",
        },
    )


def test_quality_run_plan_main_emits_yaml_detail_in_process(
    capsys, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    plan = {"next_action": {"kind": "inspect", "reason": "test"}}
    monkeypatch.setattr(PLAN, "build_plan", lambda _repo_root, *, target_skill: plan)

    monkeypatch.setattr(
        sys, "argv", ["plan_quality_run.py", "--repo-root", str(tmp_path), "--detail"]
    )
    assert PLAN.main() == 0
    assert yaml.safe_load(capsys.readouterr().out) == plan

@pytest.mark.parametrize(
    ("loader_name", "adjacent_name"),
    [
        ("_load_declaration_lifecycle", "quality_declaration_lifecycle.py"),
        ("_load_plan_renderer", "quality_run_plan_render.py"),
    ],
)
def test_quality_run_plan_fails_loudly_when_adjacent_module_is_not_loadable(
    monkeypatch: pytest.MonkeyPatch, loader_name: str, adjacent_name: str
) -> None:
    real_spec_from_file_location = PLAN.importlib.util.spec_from_file_location

    def missing_adjacent_spec(name: str, path: Path):
        if Path(path).name == adjacent_name:
            return None
        return real_spec_from_file_location(name, path)

    monkeypatch.setattr(
        PLAN.importlib.util, "spec_from_file_location", missing_adjacent_spec
    )

    with pytest.raises(ImportError, match=rf"{adjacent_name} not loadable beside"):
        getattr(PLAN, loader_name)()


def _run_plan(repo: Path, *extra: str) -> dict[str, object]:
    result = run_script(SCRIPT, "--repo-root", str(repo), *extra, "--detail")
    assert result.returncode == 0, result.stderr
    return yaml.safe_load(result.stdout)


def test_quality_run_plan_excludes_skill_refs_when_repo_has_no_skills(tmp_path: Path) -> None:
    repo = tmp_path / "app"
    repo.mkdir()
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("print('hello')\n", encoding="utf-8")

    plan = _run_plan(repo)

    assert plan["next_action"]["kind"] == "read_primer_refs"
    assert plan["gate_plan"] == "report_first"
    assert plan["skills_in_scope"] is False
    reads = plan["required_reads"]
    refs = [read["path"] for read in reads]
    assert "references/quality-lenses.md" in refs
    assert "references/skill-quality.md" not in refs
    assert "references/skill-ergonomics.md" not in refs
    assert any(
        read["path"] == "references/quality-lenses.md"
        and read["why"]
        and read["size_bytes"] == (ROOT / "skills/public/quality/references/quality-lenses.md").stat().st_size
        for read in reads
    )
    assert plan["declaration_lifecycle"]["status"] == "not-configured"


def test_quality_run_plan_includes_skill_refs_for_skill_authoring_repo(tmp_path: Path) -> None:
    repo = tmp_path / "skill_repo"
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                'description: "Demo skill."',
                "---",
                "",
                "# Demo",
                "",
                "Use this when a demo skill is needed.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    plan = _run_plan(repo)

    assert plan["skills_in_scope"] is True
    assert plan["sample_skill_paths"] == ["skills/public/demo/SKILL.md"]
    assert "references/skill-quality.md" in {read["path"] for read in plan["required_reads"]}
    assert "references/skill-ergonomics.md" in {read["path"] for read in plan["required_reads"]}
    packet = plan["structural_review_packet"]
    assert packet["required"] is True
    assert packet["target_skill"]["status"] == "unspecified"
    assert "Target boundary:" in packet["write_artifact_signals"]
    assert "Ambient repo findings:" in packet["write_artifact_signals"]
    assert "structural review result:" in packet["write_artifact_signals"]
    assert "Recommended Next Quality Moves:" in packet["write_artifact_signals"]
    assert {question["id"] for question in packet["questions"]} >= {
        "capability_needed",
        "sequencing_applicability",
        "current_centers",
        "quality_move_card",
        "enforcement_posture",
    }
    assert packet["quality_move_card"]["applies_to"] == "recommended moves only"
    assert packet["quality_move_card"]["default_enforcement_posture"] == "advisory-or-no-gate"
    assert "floor-candidate" in packet["quality_move_card"]["move_types"]
    assert "candidate-floor" in packet["quality_move_card"]["enforcement_postures"]
    assert any("before broad gates" in barrier for barrier in plan["phase_barriers"])
    assert any("before fixing" in barrier for barrier in plan["phase_barriers"])
    assert any("structural_review_packet" in barrier for barrier in plan["phase_barriers"])
    assert any("trust_model" in barrier for barrier in plan["phase_barriers"])


def test_quality_run_plan_routes_declared_commands_and_surfaces_without_claiming_execution(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "typescript_app"
    skill = repo / "skills" / "support" / "feedback-review"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("# Feedback review\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (repo / "tsconfig.json").write_text("{}\n", encoding="utf-8")
    adapter = repo / ".agents" / "quality-adapter.yaml"
    adapter.parent.mkdir(parents=True)
    adapter.write_text(
        "version: 1\nrepo: typescript_app\noutput_dir: charness-artifacts/quality\n"
        "preset_lineage:\n- typescript-quality\n"
        "gate_commands:\n- npm run quality:report\n"
        "review_commands:\n- npm run ui\n"
        "security_commands:\n- npm audit\n"
        "product_surfaces:\n- installable_cli\n- bundled_skill\n- web_app\n- support_skill\n"
        "cli_skill_surface_probe_commands:\n- npm run cli -- --help\n"
        "canonical_markdown_surfaces:\n- AGENTS.md\n"
        "skill_ergonomics_skill_paths:\n- skills/support/feedback-review/SKILL.md\n",
        encoding="utf-8",
    )

    plan = _run_plan(repo)
    lifecycle = plan["declaration_lifecycle"]

    assert lifecycle["status"] == "action-required"
    assert lifecycle["presets"] == [
        {
            "preset": "typescript-quality",
            "declaration_state": "declared",
            "repo_signal_detected": True,
            "reconciliation_state": "metadata-only",
            "reconciliation_reason": "no local machine-readable preset prescription",
        }
    ]
    assert {row["command"] for row in lifecycle["commands"]} == {
        "npm run quality:report",
        "npm run ui",
        "npm audit",
    }
    assert all(row["execution_state"] == "not-run" for row in lifecycle["commands"])
    assert lifecycle["skills"][0]["path"] == "skills/support/feedback-review/SKILL.md"
    assert lifecycle["declared_skill_paths"][0]["target_state"] == "resolved"
    assert {row["surface"] for row in lifecycle["surfaces"]} >= {
        "installable_cli",
        "bundled_skill",
        "web_app",
        "support_skill",
        "AGENTS.md",
    }
    assert next(row for row in lifecycle["surfaces"] if row["surface"] == "web_app")[
        "routing_state"
    ] == "partial"
    assert next(row for row in lifecycle["surfaces"] if row["surface"] == "support_skill")[
        "routing_state"
    ] == "routed"
    packet_commands = {packet["command"] for packet in plan["gate_packets"]}
    assert "npm run quality:report" in packet_commands
    assert "npm audit" in packet_commands
    assert "npm run ui" in packet_commands
    assert "npm run cli -- --help" in packet_commands
    assert any("inventory_entrypoint_docs_ergonomics.py" in command for command in packet_commands)
    assert any("declared-only" in barrier for barrier in plan["phase_barriers"])
    available_packet_ids = {packet["id"] for packet in plan["gate_packets"]}
    referenced_packet_ids = {
        packet_id
        for row in lifecycle["surfaces"]
        for packet_id in row.get("packet_ids", [])
    }
    assert referenced_packet_ids <= available_packet_ids


def test_quality_run_plan_surface_reuses_reconciled_catalog_packet_id(
    tmp_path: Path,
) -> None:
    lifecycle_module = PLAN._load_declaration_lifecycle()
    raw = {
        "review_commands": ["same-command"],
        "product_surfaces": ["web_app"],
    }
    command_rows, packets = lifecycle_module._declared_commands(
        raw, [{"id": "existing", "command": "same-command"}]
    )

    surfaces, _surface_packets = lifecycle_module._surface_rows(
        tmp_path, raw, [], command_rows
    )

    assert packets == []
    assert command_rows[0]["packet_id"] == "existing"
    assert surfaces[0]["packet_ids"] == ["existing"]


def test_quality_run_plan_uses_adapter_packets_when_generic_runner_is_absent(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "consumer"
    adapter = repo / ".agents" / "quality-adapter.yaml"
    adapter.parent.mkdir(parents=True)
    adapter.write_text(
        "version: 1\nrepo: consumer\noutput_dir: charness-artifacts/quality\n"
        "gate_commands:\n- npm run check\n"
        "security_commands:\n- npm audit --omit=dev\n",
        encoding="utf-8",
    )

    plan = _run_plan(repo)

    packets = {packet["id"]: packet for packet in plan["gate_packets"]}
    assert "read-only-quality" not in packets
    assert packets["adapter-gate-1"]["command"] == "npm run check"
    assert packets["adapter-security-1"]["command"] == "npm audit --omit=dev"
    # Every repo-native catalog gate this consumer lacks is reported as unavailable
    # rather than advertised.
    assert plan["declaration_lifecycle"]["unavailable_catalog_gates"] == [
        {
            "id": "read-only-quality",
            "command": "./scripts/run-quality.sh --read-only",
            "reason": "missing repo-native command scripts/run-quality.sh",
        },
    ]
    assert {
        "kind": "catalog_gate_unavailable",
        "detail": "read-only-quality: missing repo-native command scripts/run-quality.sh",
    } in plan["declaration_lifecycle"]["gaps"]


def test_quality_run_plan_names_unreachable_declared_surface(tmp_path: Path) -> None:
    repo = tmp_path / "app"
    adapter = repo / ".agents" / "quality-adapter.yaml"
    adapter.parent.mkdir(parents=True)
    adapter.write_text(
        "version: 1\nrepo: app\noutput_dir: charness-artifacts/quality\n"
        "product_surfaces:\n- installable_cli\n"
        "skill_ergonomics_skill_paths:\n- AGENTS.md\n",
        encoding="utf-8",
    )

    lifecycle = _run_plan(repo)["declaration_lifecycle"]

    cli = next(row for row in lifecycle["surfaces"] if row["surface"] == "installable_cli")
    assert cli["routing_state"] == "unreachable"
    assert lifecycle["declared_skill_paths"][0]["target_state"] == "unreachable"
    assert {gap["kind"] for gap in lifecycle["gaps"]} == {
        "catalog_gate_unavailable",
        "declared_surface_unreachable",
    }


def test_quality_run_plan_does_not_route_commands_from_invalid_adapter(tmp_path: Path) -> None:
    repo = tmp_path / "app"
    adapter = repo / ".agents" / "quality-adapter.yaml"
    adapter.parent.mkdir(parents=True)
    adapter.write_text(
        "version: 7\ngate_commands:\n- destructive-command\n",
        encoding="utf-8",
    )

    plan = _run_plan(repo)

    lifecycle = plan["declaration_lifecycle"]
    assert lifecycle["status"] == "invalid"
    assert lifecycle["adapter"]["errors"] == ["version must be 1"]
    assert "destructive-command" not in {
        packet["command"] for packet in plan["gate_packets"]
    }


def test_quality_run_plan_resolves_target_skill_for_structural_review(tmp_path: Path) -> None:
    repo = tmp_path / "skill_repo"
    for skill_id in ("retro", "quality"):
        skill_dir = repo / "skills" / "public" / skill_id
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(f"# {skill_id}\n", encoding="utf-8")

    plan = _run_plan(repo, "--target-skill", "retro")

    target = plan["structural_review_packet"]["target_skill"]
    assert target["requested"] == "retro"
    assert target["status"] == "resolved"
    assert target["path"] == "skills/public/retro/SKILL.md"
    assert "target-vs-ambient" in target["note"]


def test_quality_run_plan_reports_ambiguous_target_skill(tmp_path: Path) -> None:
    repo = tmp_path / "skill_repo"
    for skill_path in (
        repo / "skills" / "public" / "demo" / "SKILL.md",
        repo / "skills" / "support" / "demo" / "SKILL.md",
    ):
        skill_path.parent.mkdir(parents=True)
        skill_path.write_text("# Demo\n", encoding="utf-8")

    plan = _run_plan(repo, "--target-skill", "demo")

    target = plan["structural_review_packet"]["target_skill"]
    assert target["status"] == "ambiguous"
    assert target["path"] is None
    assert target["matches"] == [
        "skills/public/demo/SKILL.md",
        "skills/support/demo/SKILL.md",
    ]


def test_quality_run_plan_reports_missing_target_skill(tmp_path: Path) -> None:
    repo = tmp_path / "skill_repo"
    skill_dir = repo / "skills" / "public" / "quality"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# Quality\n", encoding="utf-8")

    plan = _run_plan(repo, "--target-skill", "retro")

    target = plan["structural_review_packet"]["target_skill"]
    assert target["requested"] == "retro"
    assert target["status"] == "not_found"
    assert target["path"] is None


def test_quality_run_plan_detects_plugin_only_skill_authoring_repo(tmp_path: Path) -> None:
    repo = tmp_path / "plugin_repo"
    skill_dir = repo / "plugins" / "acme" / "skills" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# Demo\n", encoding="utf-8")

    plan = _run_plan(repo)

    assert plan["skills_in_scope"] is True
    assert plan["sample_skill_paths"] == ["plugins/acme/skills/demo/SKILL.md"]
    assert "references/skill-quality.md" in {read["path"] for read in plan["required_reads"]}
    assert "references/skill-ergonomics.md" in {read["path"] for read in plan["required_reads"]}


def test_quality_run_plan_lists_all_on_demand_reference_triggers(tmp_path: Path) -> None:
    repo = tmp_path / "app"
    repo.mkdir()

    plan = _run_plan(repo)

    triggers = plan["on_demand_trigger_map"]
    # `>=`, not `==`: the equality red on every catalog ADDITION, which is the churn this pin was
    # costing, while the thing worth catching is a REMOVAL. Be honest about what that trades --
    # this is a RATCHET FLOOR and it goes slack the moment the catalog grows to 36, because the
    # first addition silently buys one free removal. Bump the floor with any addition, or it
    # decays into the thing it replaced.
    #
    # Deliberately NOT "every on-demand read has a trigger": that cannot fail here, because
    # scripts/validate_quality_reference_catalog.py:65-66 already raises on an on-demand
    # reference without a `trigger`, and it is queued at run-quality.sh:721.
    # 2026-09-02: 35 -> 34 when #768 retired references/boundary-bypass-ratchet.md.
    assert len(triggers) >= 34
    # This one CAN fail, and nothing else holds it. The map is keyed by path
    # (plan_quality_run.py:304-308) while the catalog validator assigns `paths[path] = role`
    # (scripts/validate_quality_reference_catalog.py:67) with no duplicate check -- so two entries
    # sharing a path pass validation and then collapse into one key here. Exact under additions.
    assert len(triggers) == len(plan["on_demand_reads"])
    assert "references/adapter-contract.md" in triggers
    assert "references/dup-ratchet.md" in triggers
    assert "references/security-npm.md" in triggers
    assert "references/security-pnpm.md" in triggers
    assert "references/security-uv.md" in triggers
    assert "references/unit-test-quality.md" in triggers
    assert "references/proof-path-efficiency.md" in triggers
    # Demoted required-primers now load on demand; the planner brief carries their
    # load-bearing residue (see test_quality_run_plan_brief_carries_demoted_primer_discipline).
    assert "references/gate-classification.md" in triggers
    assert "references/automation-promotion.md" in triggers
    assert "references/maintainer-local-enforcement.md" in triggers
    assert "references/inventory-dispatch.md" in triggers
    assert any(
        read["path"] == "references/dup-ratchet.md"
        and "scanner skew" in read["trigger"]
        for read in plan["on_demand_reads"]
    )


def test_quality_run_plan_brief_carries_demoted_primer_discipline(tmp_path: Path) -> None:
    repo = tmp_path / "app"
    repo.mkdir()
    # A canonical final gate so the maintainer-local prompt sharpens to the named-gate form.
    (repo / "scripts").mkdir()
    (repo / "scripts" / "run-quality.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")

    plan = _run_plan(repo)
    brief = plan["brief"]

    # The demoted primers are NOT mandatory reads any more...
    reads = {read["path"] for read in plan["required_reads"]}
    assert "references/gate-classification.md" not in reads
    assert "references/automation-promotion.md" not in reads
    assert "references/maintainer-local-enforcement.md" not in reads
    assert "references/inventory-dispatch.md" not in reads

    # ...but their load-bearing residue rides in the brief.
    gc = brief["gate_classification"]
    assert set(gc["closeout_states"]) == {"healthy", "weak", "missing", "deferred"}
    # The non-obvious weak-on-cost-redundancy rule must be carried, not just the label.
    assert "cheaper" in gc["closeout_states"]["weak"]
    assert gc["detail_ref"] == "references/gate-classification.md"

    ap = brief["automation_promotion"]
    assert set(ap["cases"]) == {"AUTO_EXISTING", "AUTO_CANDIDATE", "NON_AUTOMATABLE"}
    assert ap["detail_ref"] == "references/automation-promotion.md"

    mle = brief["maintainer_local_enforcement"]
    assert mle["final_gates_detected"] == ["scripts/run-quality.sh"]
    assert "DETECTED" in mle["prompt"]
    assert "missing" in mle["field_discipline"]
    assert mle["detail_ref"] == "references/maintainer-local-enforcement.md"

    # inventory-dispatch was demoted the same way: the routing index rides in the
    # brief so the run picks a focused inventory without opening the ~297-line doc.
    idp = brief["inventory_dispatch"]
    assert idp["detail_ref"] == "references/inventory-dispatch.md"
    assert "--summary" in idp["consumption"]
    areas = {area["area"] for area in idp["areas"]}
    assert {"skills", "source-hygiene", "runtime-test-economics"} <= areas
    # each area routes to at least one detail_ref (some also name inventory scripts)
    assert all(area.get("detail_refs") for area in idp["areas"])


def test_quality_run_plan_brief_standing_maintainer_prompt_without_final_gate(tmp_path: Path) -> None:
    repo = tmp_path / "app"
    repo.mkdir()

    plan = _run_plan(repo)
    mle = plan["brief"]["maintainer_local_enforcement"]

    # No final gate detected -> the prompt stays the always-emitted standing question
    # (maximally proactive: no reactive-trigger blind spot on the silent-gap repo).
    assert mle["final_gates_detected"] == []
    assert "If the repo has a canonical final" in mle["prompt"]


def test_quality_run_plan_human_output_lists_reference_and_gate_packets() -> None:
    text = PLAN.format_human(
        {
            "next_action": {"kind": "read_primer_refs"},
            "skills_in_scope": False,
            "skill_scope_reason": "no skills found",
            "gate_plan": "report_first",
            "declaration_lifecycle": {
                "status": "action-required",
                "adapter": {"found": True, "valid": True},
                "presets": [
                    {
                        "preset": "typescript-quality",
                        "reconciliation_state": "metadata-only",
                        "reconciliation_reason": "no local machine-readable preset prescription",
                    }
                ],
                "commands": [
                    {
                        "field": "review_commands",
                        "routing_state": "routed",
                        "execution_state": "not-run",
                        "command": "npm run ui",
                    }
                ],
                "surfaces": [
                    {
                        "surface": "web_app",
                        "routing_state": "partial",
                        "packet_ids": ["adapter-review-1"],
                    }
                ],
                "declared_skill_paths": [
                    {
                        "declaration": "skills/public/quality/SKILL.md",
                        "target_state": "resolved",
                        "packet_id": "skill-ergonomics",
                    }
                ],
                "gaps": [
                    {"kind": "preset_requirement_missing", "detail": "typescript-quality"}
                ],
            },
            "required_reads": [
                {"path": "references/quality-lenses.md", "why": "judge the report", "size_bytes": 42},
                {
                    "path": "references/missing.md",
                    "why": "show an unavailable measurement",
                    "measurement_state": "unavailable",
                    "unavailable_reason": "missing",
                },
                {"path": "references/legacy.md", "why": "show a legacy measurement"},
            ],
            "phase_barriers": ["Trust deterministic gates; inspect advisory gates."],
            "structural_review_packet": {
                "target_skill": {"status": "resolved", "path": "skills/public/retro/SKILL.md"},
                "questions": [
                    {"id": "target_vs_ambient", "question": "Separate target and ambient findings."}
                ],
            },
            "brief": {
                "gate_classification": {
                    "closeout_states": {
                        "healthy": "works",
                        "weak": "costly or redundant",
                        "missing": "absent",
                        "deferred": "later",
                    },
                    "detail_ref": "references/gate-classification.md",
                },
                "automation_promotion": {
                    "cases": ["AUTO_EXISTING", "NON_AUTOMATABLE"],
                    "detail_ref": "references/automation-promotion.md",
                },
                "maintainer_local_enforcement": {
                    "prompt": "Name the final local gate.",
                    "field_discipline": "missing stays explicit",
                },
                "inventory_dispatch": {
                    "areas": [
                        {"area": "skills", "inventories": ["inventory_skill.py"]},
                        {"area": "runtime", "inventories": []},
                    ],
                    "detail_ref": "references/inventory-dispatch.md",
                },
            },
            "gate_packets": [
                {
                    "id": "read-only-quality",
                    "command": "./scripts/run-quality.sh --mode read-only",
                    "cost_tier": "broad",
                    "trust_model": "advisory-plus-deterministic",
                }
            ],
        }
    )
    assert "references/legacy.md: show a legacy measurement [unmeasured]" in text
    assert "[42 bytes]" in text
    assert "[unavailable (missing)]" in text

    assert "references/quality-lenses.md: judge the report" in text
    assert "- structural_review_packet:" in text
    assert "target_vs_ambient: Separate target and ambient findings." in text
    assert "- gate_packets:" in text
    assert "read-only-quality: broad / advisory-plus-deterministic" in text
    assert (
        "preset typescript-quality: metadata-only — advisory: "
        "no local machine-readable preset prescription"
    ) in text
    assert "command review_commands: routed / not-run / npm run ui" in text
    assert "surface web_app: partial / adapter-review-1" in text
    assert (
        "skill path skills/public/quality/SKILL.md: resolved / skill-ergonomics"
        in text
    )
    assert "GAP preset_requirement_missing: typescript-quality" in text
    assert "gate states: healthy, weak, missing, deferred" in text
    assert "weak also = costly or redundant" in text
    assert "automation: AUTO_EXISTING, NON_AUTOMATABLE" in text
    assert "maintainer-local: Name the final local gate." in text
    assert "field: missing stays explicit" in text
    assert "inventory dispatch (2 concern areas" in text
    assert "skills: inventory_skill.py" in text
    assert "runtime: (detail_refs only)" in text
    assert "command: ./scripts/run-quality.sh --mode read-only" in text
    assert "- on_demand_reads: open only from concrete findings" in text


def test_quality_run_plan_yaml_loader_fails_loudly_without_repo_adapter(monkeypatch: pytest.MonkeyPatch) -> None:
    class NoAdapterAncestor:
        def __truediv__(self, _part: str) -> NoAdapterAncestor:
            return self

        def is_file(self) -> bool:
            return False

        def __str__(self) -> str:
            return "/tmp/no-adapter"

    class MissingPath:
        def __init__(self, _value: object) -> None:
            pass

        def resolve(self) -> MissingPath:
            return self

        @property
        def parents(self) -> list[NoAdapterAncestor]:
            return [NoAdapterAncestor()]

    monkeypatch.setattr(PLAN, "Path", MissingPath)

    with pytest.raises(RuntimeError, match="scripts/adapter_lib.py not found"):
        PLAN._load_yaml_file(CATALOG)


def test_quality_run_plan_yaml_emitter_bootstraps_repo_path(
    capsys, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo_text = str(ROOT)
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != repo_text])

    PLAN._emit_yaml({"status": "ok"})

    assert sys.path[0] == repo_text
    assert yaml.safe_load(capsys.readouterr().out) == {"status": "ok"}


def test_quality_run_plan_yaml_emitter_fails_loudly_without_renderer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class NoRendererAncestor:
        def __truediv__(self, _part: str) -> NoRendererAncestor:
            return self

        def is_file(self) -> bool:
            return False

    class MissingPath:
        def __init__(self, _value: object) -> None:
            pass

        def resolve(self) -> MissingPath:
            return self

        @property
        def parents(self) -> list[NoRendererAncestor]:
            return [NoRendererAncestor()]

    monkeypatch.setattr(PLAN, "Path", MissingPath)

    with pytest.raises(RuntimeError, match="scripts/yaml_output.py not found"):
        PLAN._emit_yaml({"status": "unreachable"})


@pytest.mark.parametrize(
    ("catalog", "expected"),
    [
        ({}, "`references` must be a list"),
        ({"references": ["bad"]}, "reference #1 must be a mapping"),
        ({"references": [{"path": "references/nope.txt", "role": "required-primer"}]}, "needs a markdown `path`"),
        ({"references": [{"path": "references/nope.md", "role": "mystery"}]}, "unknown role `mystery`"),
        ({"references": [{"path": "references/nope.md", "role": "required-primer"}]}, "needs `why`"),
        ({"references": [{"path": "references/nope.md", "role": "on-demand"}]}, "needs `trigger`"),
    ],
)
def test_quality_reference_catalog_rejects_invalid_reference_schema(
    catalog: dict[str, object],
    expected: str,
) -> None:
    with pytest.raises(ValidationError, match=expected):
        catalog_validator._catalog_reference_roles(catalog)


@pytest.mark.parametrize(
    ("catalog", "expected"),
    [
        ({}, "`gates` must be a list"),
        ({"gates": ["bad"]}, "gate #1 must be a mapping"),
        ({"gates": [{"id": "read-only-quality"}]}, "gate #1 needs `command`"),
    ],
)
def test_quality_reference_catalog_rejects_invalid_gate_schema(
    catalog: dict[str, object],
    expected: str,
) -> None:
    with pytest.raises(ValidationError, match=expected):
        catalog_validator._validate_gate_packets(catalog)


def test_quality_reference_catalog_matches_index_sections() -> None:
    validate_quality_reference_catalog(ROOT)


def test_quality_reference_catalog_cli_main_reports_success(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "argv", ["validate_quality_reference_catalog.py", "--repo-root", str(ROOT)])

    assert catalog_validator.main() == 0
    assert "Validated quality reference catalog/index parity." in capsys.readouterr().out


def test_quality_reference_catalog_script_entry_reports_validation_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["validate_quality_reference_catalog.py", "--repo-root", str(tmp_path)],
    )

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_path(str(ROOT / "scripts" / "validate_quality_reference_catalog.py"), run_name="__main__")

    assert exc_info.value.code == 1
    assert "missing quality reference index" in capsys.readouterr().err


def test_quality_reference_catalog_rejects_missing_catalog(tmp_path: Path) -> None:
    quality_refs = tmp_path / "skills" / "public" / "quality" / "references"
    quality_refs.mkdir(parents=True)
    (quality_refs / "index.md").write_text("# Quality Reference Index\n", encoding="utf-8")

    with pytest.raises(ValidationError, match="missing quality reference catalog"):
        validate_quality_reference_catalog(tmp_path)


def test_quality_reference_catalog_rejects_missing_referenced_file(tmp_path: Path) -> None:
    quality_refs = tmp_path / "skills" / "public" / "quality" / "references"
    quality_refs.mkdir(parents=True)
    (quality_refs / "index.md").write_text(
        "\n".join(
            [
                "# Quality Reference Index",
                "",
                "## Required And Scope Primers",
                "",
                "- `references/quality-lenses.md` -- lens.",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (quality_refs / "catalog.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "references:",
                "  - path: references/quality-lenses.md",
                "    role: required-primer",
                "    why: lens",
                "gates:",
                "  - id: read-only-quality",
                "    command: ./scripts/run-quality.sh --read-only",
                "    purpose: read-only gate",
                "    trust_model: deterministic",
                "    cost_tier: broad",
                "    parallel_group: serial-critical",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="missing referenced file"):
        validate_quality_reference_catalog(tmp_path)


def test_quality_reference_catalog_validator_rejects_index_only_review_detail(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    quality_refs = repo / "skills" / "public" / "quality" / "references"
    quality_refs.mkdir(parents=True)
    (quality_refs / "index.md").write_text(
        "\n".join(
            [
                "# Quality Reference Index",
                "",
                "## Required And Scope Primers",
                "",
                "- `references/quality-lenses.md` -- lens.",
                "- `references/security-npm.md` -- npm.",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (quality_refs / "catalog.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "references:",
                "  - path: references/quality-lenses.md",
                "    role: required-primer",
                "    why: lens",
                "gates: []",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (quality_refs / "quality-lenses.md").write_text("# Lenses\n", encoding="utf-8")
    (quality_refs / "security-npm.md").write_text("# npm\n", encoding="utf-8")

    with pytest.raises(ValidationError) as exc_info:
        validate_quality_reference_catalog(repo)
    message = str(exc_info.value)
    assert "index reference(s) missing from catalog" in message
    assert "references/security-npm.md" in message


def test_quality_reference_catalog_validator_rejects_section_role_mismatch(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    quality_refs = repo / "skills" / "public" / "quality" / "references"
    quality_refs.mkdir(parents=True)
    (quality_refs / "index.md").write_text(
        "\n".join(
            [
                "# Quality Reference Index",
                "",
                "## On-Demand Review Detail",
                "",
                "- `references/security-npm.md` -- npm.",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (quality_refs / "catalog.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "references:",
                "  - path: references/security-npm.md",
                "    role: required-primer",
                "    why: npm",
                "gates: []",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (quality_refs / "security-npm.md").write_text("# npm\n", encoding="utf-8")

    with pytest.raises(ValidationError) as exc_info:
        validate_quality_reference_catalog(repo)
    message = str(exc_info.value)
    assert "index/catalog role mismatch" in message
    assert "references/security-npm.md" in message
    assert "required-primer" in message


def test_quality_reference_catalog_validator_rejects_catalog_only_reference(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    quality_refs = repo / "skills" / "public" / "quality" / "references"
    quality_refs.mkdir(parents=True)
    (quality_refs / "index.md").write_text(
        "\n".join(
            [
                "# Quality Reference Index",
                "",
                "## Required And Scope Primers",
                "",
                "- `references/quality-lenses.md` -- lens.",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (quality_refs / "catalog.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "references:",
                "  - path: references/quality-lenses.md",
                "    role: required-primer",
                "    why: lens",
                "  - path: references/security-npm.md",
                "    role: on-demand",
                "    trigger: npm",
                "gates: []",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (quality_refs / "quality-lenses.md").write_text("# Lenses\n", encoding="utf-8")
    (quality_refs / "security-npm.md").write_text("# npm\n", encoding="utf-8")

    with pytest.raises(ValidationError) as exc_info:
        validate_quality_reference_catalog(repo)
    message = str(exc_info.value)
    assert "catalog reference(s) missing from index sections" in message
    assert "references/security-npm.md" in message
