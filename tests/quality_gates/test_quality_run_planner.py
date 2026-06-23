from __future__ import annotations

import json
from pathlib import Path

from .support import ADAPTER_LIB, ROOT, run_script

SCRIPT = "skills/public/quality/scripts/plan_quality_run.py"
CATALOG = ROOT / "skills" / "public" / "quality" / "references" / "catalog.yaml"


def _run_plan(repo: Path) -> dict[str, object]:
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_quality_run_plan_excludes_skill_refs_when_repo_has_no_skills(tmp_path: Path) -> None:
    repo = tmp_path / "app"
    repo.mkdir()
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("print('hello')\n", encoding="utf-8")

    plan = _run_plan(repo)

    assert plan["next_action"] == "read_primer_refs"
    assert plan["gate_plan"] == "report_first"
    assert plan["skills_in_scope"] is False
    refs = plan["required_primer_refs"]
    reads = plan["required_reads"]
    assert "references/quality-lenses.md" in refs
    assert "references/skill-quality.md" not in refs
    assert "references/skill-ergonomics.md" not in refs
    assert any(
        read["path"] == "references/quality-lenses.md" and read["why"]
        for read in reads
    )


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
    assert "references/skill-quality.md" in plan["required_primer_refs"]
    assert "references/skill-ergonomics.md" in plan["required_primer_refs"]
    assert any("before broad gates" in barrier for barrier in plan["phase_barriers"])
    assert any("before fixing" in barrier for barrier in plan["phase_barriers"])
    assert any("trust_model" in barrier for barrier in plan["phase_barriers"])


def test_quality_run_plan_detects_plugin_only_skill_authoring_repo(tmp_path: Path) -> None:
    repo = tmp_path / "plugin_repo"
    skill_dir = repo / "plugins" / "acme" / "skills" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# Demo\n", encoding="utf-8")

    plan = _run_plan(repo)

    assert plan["skills_in_scope"] is True
    assert plan["sample_skill_paths"] == ["plugins/acme/skills/demo/SKILL.md"]
    assert "references/skill-quality.md" in plan["required_primer_refs"]
    assert "references/skill-ergonomics.md" in plan["required_primer_refs"]


def test_quality_run_plan_lists_all_on_demand_reference_triggers(tmp_path: Path) -> None:
    repo = tmp_path / "app"
    repo.mkdir()

    plan = _run_plan(repo)

    triggers = plan["on_demand_trigger_map"]
    assert len(triggers) == 30
    assert "references/adapter-contract.md" in triggers
    assert "references/dup-ratchet.md" in triggers
    assert "references/security-npm.md" in triggers
    assert "references/security-pnpm.md" in triggers
    assert "references/security-uv.md" in triggers
    assert "references/unit-test-quality.md" in triggers
    assert any(
        read["path"] == "references/dup-ratchet.md"
        and "scanner skew" in read["trigger"]
        for read in plan["on_demand_reads"]
    )


def test_quality_run_plan_reports_gate_packet_cost_and_trust(tmp_path: Path) -> None:
    repo = tmp_path / "app"
    repo.mkdir()

    plan = _run_plan(repo)

    packets = plan["gate_packets"]
    read_only = next(packet for packet in packets if packet["id"] == "read-only-quality")
    assert read_only["cost_tier"] == "broad"
    assert read_only["parallel_group"] == "serial-critical"
    assert "advisory" in read_only["trust_model"]
    assert "repo-native command" in read_only["run_when"]


def test_quality_reference_catalog_has_planner_schema_and_existing_paths() -> None:
    catalog = ADAPTER_LIB.load_yaml_file(CATALOG)
    skill_root = ROOT / "skills" / "public" / "quality"
    known_roles = {"required-primer", "scope-primer", "on-demand"}

    for ref in catalog["references"]:
        assert ref["role"] in known_roles
        assert (skill_root / ref["path"]).exists()
        if ref["role"] in {"required-primer", "scope-primer"}:
            assert ref.get("why")
        if ref["role"] == "on-demand":
            assert ref.get("trigger")

    for gate in catalog["gates"]:
        for field in ("id", "command", "purpose", "trust_model", "cost_tier", "parallel_group"):
            assert gate.get(field)
