from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from .support import ROOT, run_script

CHECK_SCRIPT = "skills/public/hitl/scripts/check_chunk_contract.py"


def _load_hitl_lib():
    module_path = ROOT / "scripts" / "hitl_review_artifact_lib.py"
    spec = importlib.util.spec_from_file_location("hitl_review_artifact_lib", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_hitl_skill_requires_agent_assessment_before_decision() -> None:
    skill_text = (ROOT / "skills" / "public" / "hitl" / "SKILL.md").read_text(encoding="utf-8")

    assert "Agent Assessment" in skill_text
    assert "Recommended Disposition" in skill_text
    assert "non-binding" in skill_text
    assert "question-only chunks are not enough" in skill_text


def test_hitl_chunk_contract_lists_assessment_and_recommendation() -> None:
    chunk_contract = (ROOT / "skills" / "public" / "hitl" / "references" / "chunk-contract.md").read_text(
        encoding="utf-8"
    )

    assert "agent assessment" in chunk_contract
    assert "recommended disposition" in chunk_contract
    assert "display-only" in chunk_contract
    assert "Suggestions never auto-record as approval" in chunk_contract


def test_hitl_output_shape_orders_assessment_before_decision_needed() -> None:
    skill_text = (ROOT / "skills" / "public" / "hitl" / "SKILL.md").read_text(encoding="utf-8")

    assessment_index = skill_text.index("Agent Assessment")
    recommendation_index = skill_text.index("Recommended Disposition")
    decision_index = skill_text.index("Decision Needed")

    assert assessment_index < decision_index
    assert recommendation_index < decision_index


def test_check_chunk_contract_lib_flags_question_only_chunk() -> None:
    lib = _load_hitl_lib()
    bad = "## Decision Needed\n\nShould we accept this rewrite?"
    errors = lib.check_chunk_contract(bad)

    assert any("Agent Assessment" in err for err in errors)
    assert any("Recommended Disposition" in err for err in errors)


def test_check_chunk_contract_lib_accepts_fully_shaped_chunk() -> None:
    lib = _load_hitl_lib()
    good = (
        "### Agent Assessment\n"
        "The proposed rewrite preserves the contract.\n\n"
        "### Recommended Disposition\n"
        "accept (display-only)\n\n"
        "### Decision Needed\n"
        "Approve, revise, or defer?\n"
    )
    assert lib.check_chunk_contract(good) == []


def test_check_chunk_contract_lib_skips_chunks_without_decision_prompt() -> None:
    lib = _load_hitl_lib()
    informational = "Status update: still gathering evidence; no decision yet."

    assert lib.check_chunk_contract(informational) == []


def test_check_chunk_contract_script_blocks_missing_recommendation(tmp_path: Path) -> None:
    chunk_path = tmp_path / "chunk.md"
    chunk_path.write_text(
        "## Decision Needed\n\nShould we accept the rewritten section?\n",
        encoding="utf-8",
    )

    result = run_script(CHECK_SCRIPT, "--chunk-file", str(chunk_path))

    assert result.returncode == 1, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert any("Agent Assessment" in err for err in payload["errors"])
    assert any("Recommended Disposition" in err for err in payload["errors"])


def test_agent_assessment_invariant_reference_exists() -> None:
    invariant_path = ROOT / "skills" / "shared" / "references" / "agent-assessment-invariant.md"

    assert invariant_path.is_file()
    text = invariant_path.read_text(encoding="utf-8")
    assert "Agent Assessment" in text
    assert "Recommended Disposition" in text
    assert "display-only" in text
    assert "check_chunk_contract.py" in text


def test_agent_assessment_invariant_is_cited_across_chunk_surfaces() -> None:
    target = "agent-assessment-invariant.md"
    surfaces = {
        "hitl SKILL.md": ROOT / "skills" / "public" / "hitl" / "SKILL.md",
        "hitl chunk-contract.md": ROOT / "skills" / "public" / "hitl" / "references" / "chunk-contract.md",
        "quality proposal-flow.md": (
            ROOT / "skills" / "public" / "quality" / "references" / "proposal-flow.md"
        ),
        "premortem SKILL.md": ROOT / "skills" / "public" / "premortem" / "SKILL.md",
        "spec SKILL.md": ROOT / "skills" / "public" / "spec" / "SKILL.md",
        "narrative SKILL.md": ROOT / "skills" / "public" / "narrative" / "SKILL.md",
        "init-repo SKILL.md": ROOT / "skills" / "public" / "init-repo" / "SKILL.md",
    }
    missing = [name for name, path in surfaces.items() if target not in path.read_text(encoding="utf-8")]

    assert not missing, f"surfaces missing agent-assessment-invariant cite: {missing}"


def test_hitl_chunk_contract_extends_invariant_to_applied_and_full_target_review() -> None:
    text = (ROOT / "skills" / "public" / "hitl" / "references" / "chunk-contract.md").read_text(
        encoding="utf-8"
    )

    assert "Full Target Review" in text
    applied_section = text.split("## Applied Rewrite Review", 1)[1].split("##", 1)[0]
    assert "Agent Assessment" in applied_section
    assert "Recommended Disposition" in applied_section


def test_check_chunk_contract_script_passes_complete_chunk(tmp_path: Path) -> None:
    chunk_path = tmp_path / "chunk.md"
    chunk_path.write_text(
        (
            "### Agent Assessment\n"
            "Constraint X is upheld.\n\n"
            "### Recommended Disposition\n"
            "accept (display-only)\n\n"
            "### Decision Needed\n"
            "Approve or revise?\n"
        ),
        encoding="utf-8",
    )

    result = run_script(CHECK_SCRIPT, "--chunk-file", str(chunk_path))

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["errors"] == []
