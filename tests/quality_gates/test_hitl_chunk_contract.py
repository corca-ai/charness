from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from .support import ROOT, run_script

HITL_SKILL = (ROOT / "skills" / "public" / "hitl" / "SKILL.md").read_text(encoding="utf-8")
CHUNK_CONTRACT = (ROOT / "skills" / "public" / "hitl" / "references" / "chunk-contract.md").read_text(
    encoding="utf-8"
)

CHECK_SCRIPT = "skills/public/hitl/scripts/check_chunk_contract.py"


def _load_hitl_lib():
    module_path = ROOT / "scripts" / "hitl_review_artifact_lib.py"
    spec = importlib.util.spec_from_file_location("hitl_review_artifact_lib", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_hitl_skill_requires_agent_assessment_before_decision() -> None:
    assert "Agent Assessment" in HITL_SKILL
    assert "Recommended Disposition" in HITL_SKILL
    assert "non-binding" in HITL_SKILL
    assert "question-only chunks are not enough" in HITL_SKILL


def test_hitl_chunk_contract_lists_assessment_and_recommendation() -> None:
    assert "agent assessment" in CHUNK_CONTRACT
    assert "recommended disposition" in CHUNK_CONTRACT
    assert "display-only" in CHUNK_CONTRACT
    assert "Suggestions never auto-record as approval" in CHUNK_CONTRACT


def test_hitl_output_shape_orders_assessment_before_decision_needed() -> None:
    assessment_index = HITL_SKILL.index("Agent Assessment")
    recommendation_index = HITL_SKILL.index("Recommended Disposition")
    decision_index = HITL_SKILL.index("Decision Needed")

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
        "critique SKILL.md": ROOT / "skills" / "public" / "critique" / "SKILL.md",
        "spec SKILL.md": ROOT / "skills" / "public" / "spec" / "SKILL.md",
        "narrative SKILL.md": ROOT / "skills" / "public" / "narrative" / "SKILL.md",
        "setup SKILL.md": ROOT / "skills" / "public" / "setup" / "SKILL.md",
    }
    missing = [name for name, path in surfaces.items() if target not in path.read_text(encoding="utf-8")]

    assert not missing, f"surfaces missing agent-assessment-invariant cite: {missing}"


def test_hitl_chunk_contract_extends_invariant_to_applied_and_full_target_review() -> None:
    assert "Full Target Review" in CHUNK_CONTRACT
    applied_section = CHUNK_CONTRACT.split("## Applied Rewrite Review", 1)[1].split("##", 1)[0]
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


# --- S21 (2026-07-28 triage sweep): the self-check certified an empty chunk ---


def test_check_chunk_contract_lib_rejects_empty_and_whitespace_only_chunks() -> None:
    lib = _load_hitl_lib()

    # Both used to return [] -> {"status": "pass"}: the contract check ran over
    # nothing and reported the contract satisfied.
    assert lib.check_chunk_contract("") != []
    assert lib.check_chunk_contract("   \n\n") != []
    assert "nothing to read" in lib.check_chunk_contract("")[0]


def test_check_chunk_contract_lib_detects_a_decision_request_without_a_question_mark() -> None:
    lib = _load_hitl_lib()
    asking = "Please approve or reject this rename before I continue."

    errors = lib.check_chunk_contract(asking)

    assert any("Agent Assessment" in error for error in errors)
    assert any("Recommended Disposition" in error for error in errors)


def test_check_chunk_contract_lib_still_skips_a_purely_informational_chunk() -> None:
    # The widened detection must not swallow the informational case: a chunk that
    # merely mentions a decision it is NOT asking for stays out of scope.
    lib = _load_hitl_lib()

    assert lib.check_chunk_contract("Status update: still gathering evidence; no decision yet.") == []
    assert lib.check_chunk_contract("The prior decision stands; nothing needed from you.") == []


def test_check_chunk_contract_script_blocks_whitespace_only_chunk_file(tmp_path: Path) -> None:
    chunk_path = tmp_path / "chunk.md"
    chunk_path.write_text("   \n\n", encoding="utf-8")

    result = run_script(CHECK_SCRIPT, "--chunk-file", str(chunk_path))

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"


def test_check_chunk_contract_lib_ignores_decision_verbs_in_descriptive_prose() -> None:
    # A false positive here blocks a chunk that asked nothing, so the bare verbs
    # only count in request position and fenced examples are not the author's ask.
    lib = _load_hitl_lib()

    assert lib.check_chunk_contract("The validator will reject a digest with no records.") == []
    assert lib.check_chunk_contract("I can confirm the rewrite preserves the contract.") == []
    assert lib.check_chunk_contract("```yaml\napprove: true\n```\nThis block shows the schema.") == []


def test_check_chunk_contract_lib_flags_a_line_initial_request() -> None:
    lib = _load_hitl_lib()

    assert lib.check_chunk_contract("Approve or revise before I apply this.") != []
    assert lib.check_chunk_contract("Approval needed on the rename.") != []


def test_check_chunk_contract_script_blocks_empty_stdin() -> None:
    # The sweep's literal reproduction: `printf '' | check_chunk_contract.py`.
    # Driven through stdin on purpose — the `--chunk-file` test does not reach
    # `sys.stdin.read()`, which is the path the row actually exercised.
    result = subprocess.run(
        [sys.executable, CHECK_SCRIPT],
        cwd=ROOT,
        input="",
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert json.loads(result.stdout)["status"] == "blocked"
