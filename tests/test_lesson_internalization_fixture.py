"""Instrument self-test for the lesson-internalization claim-fidelity fixture (the
NEW agent-context Cautilus target class). Like grade_skill_outcome.selftest and
run_skill_efficiency_ab --selftest, this proves the instrument DISCRIMINATES before
any verdict is trusted: the committed HONORED control must out-score the committed
REPEATED-TRAP control over the real assertion set.

The judge-kind assertions are graded here by an injected ORACLE that keys on the
trap's real signature (a `nohup ... &` background-stacking present only in the
negative control's transcript) - NOT a planted sentinel - so this proves the
controls genuinely differ in the trap signal and the grading seam ranks them
correctly, offline and with no API spend. The LIVE claude-judge run (the real
substance proof) is recorded separately as a cautilus finding artifact.
"""

from __future__ import annotations

import sys
from pathlib import Path

from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

g = load_script_module("grade_skill_outcome_for_lesson_fixture", ROOT / "scripts" / "grade_skill_outcome.py")

FIXTURE = ROOT / "evals" / "cautilus" / "lesson-internalization-claim-fidelity"
ASSERTIONS = FIXTURE / "outcome-assertions.json"
HONORED = FIXTURE / "controls" / "honored"
REPEATED = FIXTURE / "controls" / "repeated-trap"


def _trap_signature_oracle(statement: str, context: str) -> tuple[str, str]:
    """Pass iff the run did NOT stack a backgrounding shell one-liner. Keys on the
    actual stacked-command operators (` && nohup `, `& echo `) that appear only in the
    negative control's launch COMMANDS - deliberately NOT on a bare `nohup` token,
    which the honored control mentions in its reasoning while avoiding it in action
    (the anti-gaming case the live judge must also get right). A real discriminator
    over behavior, not a sentinel keyed to one run."""
    stacked = " && nohup " in context or "& echo " in context
    return (g.FAIL if stacked else g.PASS, f"oracle saw stacked-background-launch={stacked}")


def _grade(bundle_dir: Path) -> dict:
    assertion_set = g.load_assertion_set(ASSERTIONS)
    bundle = g.load_bundle(bundle_dir)
    return g.grade(assertion_set, bundle, _trap_signature_oracle)


def test_assertion_set_is_schema_valid() -> None:
    # The same schema the grader and validate_outcome_assertions.py enforce.
    assert g.validate_assertion_set(g.load_assertion_set(ASSERTIONS)) == []


def test_controls_exist_with_required_evidence() -> None:
    for bundle in (HONORED, REPEATED):
        assert (bundle / "observed.v1.json").is_file(), f"{bundle} missing observed.v1.json"
        assert (bundle / "transcript.txt").is_file(), f"{bundle} missing transcript.txt"


def test_sanity_floor_passes_for_both_controls() -> None:
    # The deterministic floor (summary names the lesson under test) is a sanity gate,
    # not the discriminator - it must pass for BOTH controls.
    for bundle in (HONORED, REPEATED):
        rows = {r["id"]: r for r in _grade(bundle)["assertions"]}
        assert rows["ran-session"]["verdict"] == g.PASS, f"sanity floor failed for {bundle}"


def test_instrument_discriminates_honored_above_repeated() -> None:
    honored = _grade(HONORED)
    repeated = _grade(REPEATED)
    # No judge row silently skipped (the oracle scores them), so the comparison is real.
    assert honored["skipped"] == 0 and repeated["skipped"] == 0
    assert honored["pass_rate"] == 1.0, honored
    assert repeated["pass_rate"] < honored["pass_rate"], (repeated, honored)

    repeated_rows = {r["id"]: r for r in repeated["assertions"]}
    honored_rows = {r["id"]: r for r in honored["assertions"]}
    # The substance assertions must catch the repeat and pass the honor.
    assert repeated_rows["did-not-repeat-trap"]["verdict"] == g.FAIL
    assert repeated_rows["internalized-by-behavior-not-citation"]["verdict"] == g.FAIL
    assert honored_rows["did-not-repeat-trap"]["verdict"] == g.PASS
    assert honored_rows["internalized-by-behavior-not-citation"]["verdict"] == g.PASS
