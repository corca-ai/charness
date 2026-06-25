from __future__ import annotations

import importlib.util
import json
import runpy
import sys
from pathlib import Path

import pytest

from scripts import validate_quality_reference_catalog as catalog_validator
from scripts.validate_quality_reference_catalog import (
    ValidationError,
    validate_quality_reference_catalog,
)

from .support import ADAPTER_LIB, ROOT, run_script

SCRIPT = "skills/public/quality/scripts/plan_quality_run.py"
SCRIPT_PATH = ROOT / SCRIPT
CATALOG = ROOT / "skills" / "public" / "quality" / "references" / "catalog.yaml"
INDEX = ROOT / "skills" / "public" / "quality" / "references" / "index.md"

PLAN_SPEC = importlib.util.spec_from_file_location("quality_run_plan_under_test", SCRIPT_PATH)
assert PLAN_SPEC is not None and PLAN_SPEC.loader is not None
PLAN = importlib.util.module_from_spec(PLAN_SPEC)
PLAN_SPEC.loader.exec_module(PLAN)


def _run_plan(repo: Path, *extra: str) -> dict[str, object]:
    result = run_script(SCRIPT, "--repo-root", str(repo), *extra, "--json")
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
    packet = plan["structural_review_packet"]
    assert packet["required"] is True
    assert packet["target_skill"]["status"] == "unspecified"
    assert "Target boundary:" in packet["write_artifact_signals"]
    assert "Ambient repo findings:" in packet["write_artifact_signals"]
    assert "structural review result:" in packet["write_artifact_signals"]
    assert {question["id"] for question in packet["questions"]} >= {
        "target_vs_ambient",
        "helper_owned_packet",
        "dogfood_pressure",
        "next_structural_move",
    }
    assert any("before broad gates" in barrier for barrier in plan["phase_barriers"])
    assert any("before fixing" in barrier for barrier in plan["phase_barriers"])
    assert any("structural_review_packet" in barrier for barrier in plan["phase_barriers"])
    assert any("trust_model" in barrier for barrier in plan["phase_barriers"])


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


def test_quality_run_plan_human_output_lists_reference_and_gate_packets() -> None:
    text = PLAN.format_human(
        {
            "next_action": "read_primer_refs",
            "skills_in_scope": False,
            "skill_scope_reason": "no skills found",
            "gate_plan": "report_first",
            "required_reads": [
                {"path": "references/quality-lenses.md", "why": "judge the report"}
            ],
            "phase_barriers": ["Trust deterministic gates; inspect advisory gates."],
            "structural_review_packet": {
                "target_skill": {"status": "resolved", "path": "skills/public/retro/SKILL.md"},
                "questions": [
                    {"id": "target_vs_ambient", "question": "Separate target and ambient findings."}
                ],
            },
            "gate_packets": [
                {
                    "id": "read-only-quality",
                    "cost_tier": "broad",
                    "trust_model": "advisory-plus-deterministic",
                }
            ],
        }
    )

    assert "references/quality-lenses.md: judge the report" in text
    assert "- structural_review_packet:" in text
    assert "target_vs_ambient: Separate target and ambient findings." in text
    assert "- gate_packets:" in text
    assert "read-only-quality: broad / advisory-plus-deterministic" in text
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
