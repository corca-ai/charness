from __future__ import annotations

import io
import sys
from pathlib import Path

import yaml

from tests.script_main import load_script_module, run_loaded_script_main

from .seeding_support import load_module
from .support import ROOT, run_script

HITL_SKILL = (ROOT / "skills" / "public" / "hitl" / "SKILL.md").read_text(encoding="utf-8")
CHUNK_CONTRACT = (
    ROOT / "skills" / "public" / "hitl" / "references" / "chunk-contract.md"
).read_text(encoding="utf-8")

CHECK_SCRIPT = "skills/public/hitl/scripts/check_chunk_contract.py"
CHECK_MODULE = load_script_module(
    "hitl_check_chunk_contract",
    ROOT / "skills" / "public" / "hitl" / "scripts" / "check_chunk_contract.py",
)


def _load_hitl_lib():
    module_path = ROOT / "scripts" / "hitl_review_artifact_lib.py"
    return load_module("hitl_review_artifact_lib", module_path)


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
    payload = yaml.safe_load(result.stdout)
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
    payload = yaml.safe_load(result.stdout)
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

    assert (
        lib.check_chunk_contract("Status update: still gathering evidence; no decision yet.") == []
    )
    assert lib.check_chunk_contract("The prior decision stands; nothing needed from you.") == []


def test_check_chunk_contract_script_blocks_whitespace_only_chunk_file(tmp_path: Path) -> None:
    chunk_path = tmp_path / "chunk.md"
    chunk_path.write_text("   \n\n", encoding="utf-8")

    result = run_script(CHECK_SCRIPT, "--chunk-file", str(chunk_path))

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "blocked"


def test_check_chunk_contract_lib_ignores_decision_verbs_in_descriptive_prose() -> None:
    # A false positive here blocks a chunk that asked nothing, so the bare verbs
    # only count in request position and fenced examples are not the author's ask.
    lib = _load_hitl_lib()

    assert lib.check_chunk_contract("The validator will reject a digest with no records.") == []
    assert lib.check_chunk_contract("I can confirm the rewrite preserves the contract.") == []
    assert (
        lib.check_chunk_contract("```yaml\napprove: true\n```\nThis block shows the schema.") == []
    )


def test_check_chunk_contract_lib_flags_a_line_initial_request() -> None:
    lib = _load_hitl_lib()

    assert lib.check_chunk_contract("Approve or revise before I apply this.") != []
    assert lib.check_chunk_contract("Approval needed on the rename.") != []


def test_check_chunk_contract_script_blocks_empty_stdin(monkeypatch) -> None:
    # The sweep's literal reproduction: `printf '' | check_chunk_contract.py`.
    # Driven through stdin on purpose — the `--chunk-file` test does not reach
    # `sys.stdin.read()`, which is the path the row actually exercised.
    monkeypatch.setattr(sys, "stdin", io.StringIO(""))
    result = run_loaded_script_main(CHECK_SCRIPT, CHECK_MODULE)

    assert result.returncode == 1
    assert yaml.safe_load(result.stdout)["status"] == "blocked"


def lib_errors(text: str):
    return _load_hitl_lib().check_chunk_contract(text)


def test_check_chunk_contract_lib_falls_back_to_raw_text_on_an_unterminated_fence() -> None:
    # An unterminated fence would otherwise swallow the rest of the chunk, hiding a
    # real request. A missed request is the expensive direction, so the ambiguous
    # case fails toward detection.
    asking = "```yaml\napprove: true\n\nApprove or revise before I apply.\n"

    assert lib_errors(asking) != []


def test_check_chunk_contract_script_reports_an_unreadable_chunk_file_as_an_error() -> None:
    # A missing path used to raise FileNotFoundError with exit 1 — the same code a
    # well-formed `blocked` verdict returns, so "you gave me nothing" and "the
    # chunk violates the contract" were indistinguishable to a caller.
    result = run_script(CHECK_SCRIPT, "--chunk-file", "/tmp/charness-does-not-exist.md")

    assert result.returncode == 2
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "error"
    assert "could not be read" in payload["errors"][0]


def test_error_payload_keeps_a_non_ascii_chunk_path_readable(tmp_path: Path) -> None:
    """The error arm serializes an operator-facing message, so it must not escape.

    `str(exc)` on the unreadable-file arm embeds the path the operator typed. A
    Korean or otherwise non-ASCII path is an ordinary case in this repo, and an
    escaping serializer (`allow_unicode=False` on the YAML dump, or the
    `ensure_ascii=True` JSON fallback) would render it as `\\uXXXX` — the caller
    then cannot read back the path they got wrong, which is the whole point of
    this arm.
    """
    missing = tmp_path / "없는-리뷰-청크.md"

    result = run_script(CHECK_SCRIPT, "--chunk-file", str(missing))

    assert result.returncode == 2
    # The raw bytes, not just the parsed payload: `yaml.safe_load` decodes
    # `\uXXXX` back to the same string, so asserting on the parsed value alone
    # would pass under either setting and prove nothing about what the operator
    # sees.
    assert "없는-리뷰-청크.md" in result.stdout
    assert "\\u" not in result.stdout
    assert yaml.safe_load(result.stdout)["status"] == "error"


def test_contract_error_messages_stay_ascii_only() -> None:
    """Pins the premise that the verdict arm's non-ASCII escaping rests on.

    `check_chunk_contract` returns a closed set of fixed messages and `main`
    pairs them with a `pass`/`blocked` status, so the verdict payload cannot
    carry a non-ASCII character for any input — which is why no test can
    distinguish an escaping serializer from a non-escaping one on that arm
    (`allow_unicode` on the YAML dump, `ensure_ascii` on the JSON fallback
    `render_yaml` uses when PyYAML is absent). That equivalence
    is contingent, not permanent: the day a message quotes the chunk back, it
    stops holding silently. This test makes that day visible.

    It is a named scope, not a gate: it asserts what the message set is, and
    fails loudly if the set gains text a caller supplies.
    """
    lib = _load_hitl_lib()
    produced = [
        *lib.check_chunk_contract(""),
        *lib.check_chunk_contract("Approve this 리뷰 or revise it before I continue?"),
    ]

    assert produced, "expected both arms to produce messages"
    for message in produced:
        assert message.isascii(), f"contract message is no longer ASCII-only: {message!r}"
