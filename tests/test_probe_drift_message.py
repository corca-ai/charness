"""The drift message is only read when a probe drifts, so nothing green exercises it.

#536's repair is a message. `assert expr, msg` evaluates `msg` lazily, so in a passing suite
`probe_drift_message` is called ZERO times — a bounded round pointed out that deleting the
cause paragraph, the update list, or the commands would be a silent green edit, and that the
mutants proving those parts reach the reader had been killed by hand rather than by anything
checked in. `tests/` is also outside the mutation pool, so no gate covers it either.

These pin the claims the message makes, and the paths and commands it names. They do not judge
whether the prose reads well — they fail if it stops saying the load-bearing things, or if it
names a script or a probe that does not exist.
"""

from __future__ import annotations

import json
from pathlib import Path

from tests.probe_drift_support import (
    CORPUS_CAUSES,
    DECISION_RECORD,
    DISCRIMINATION_PATHS,
    FLOOR_COMMAND,
    FLOOR_PROBE,
    GATE_MODULE,
    MARKER_COMMAND,
    MARKER_PROBE,
    MARKER_RECURSIVE_COMMAND,
    RULE_CAUSES,
    UPDATE_SURFACES,
    probe_drift_message,
)

ROOT = Path(__file__).resolve().parent.parent


def test_the_message_separates_a_corpus_cause_from_a_rule_cause() -> None:
    """The correction that mattered most: the two causes have OPPOSITE remedies.

    A first version said flatly "the fix is to re-record, not to undo the write". That is wrong
    whenever the measurement rule moved rather than the corpus, and following it would launder a
    rule regression into the pinned probe and into the decision record.
    """
    message = probe_drift_message("artifacts_scanned", probe=MARKER_PROBE)

    assert "FIRST decide WHICH changed" in message
    assert "If the CORPUS changed, re-record" in message
    assert "do NOT re-record yet" in message
    assert "launder a measurement" in message  # wraps across lines in the render
    # The rule causes a reader would otherwise mistake for a write.
    assert "inventory-consumer-fields.json" in message
    assert "ENFORCED_FROM_DATE" in message
    # No git-availability cause is asserted, and its ABSENCE is deliberate. Version 2 listed
    # one, and a round showed it named a field and a value no code produces (`exemption_state`
    # returns `not-corroborated`, never `unavailable`), got a shallow checkout backwards, and
    # could not move any pinned number on this corpus anyway — every artifact resolves
    # `not-claimed` before git is consulted. A cause that cannot fire is the wolf-crier this
    # goal's Non-Goals forbid, so it was removed rather than reworded.
    assert "git was unavailable" not in message
    # And the corpus cause a reader would otherwise miss, because no file appears or vanishes.
    assert "REWRITTEN" in message
    assert "history/" in message


def test_the_message_names_every_surface_that_carries_the_same_numbers() -> None:
    """Five surfaces, not three. The probes themselves refuted the smaller claim."""
    message = probe_drift_message("floor", probe=FLOOR_PROBE)

    assert MARKER_PROBE in message
    assert FLOOR_PROBE in message
    assert DECISION_RECORD in message
    assert "_provenance.recursive_variant" in message
    assert "nests HERE, not at top level" in message
    assert "_provenance.current_corpus" in message
    assert "_provenance` bookkeeping" in message
    assert "quotes the counts in prose" in message


def test_the_message_does_not_tell_a_reader_to_overwrite_provenance() -> None:
    """The first version's actual defect: it would have deleted `_provenance`.

    `--json` emits only the measured payload. Pasting that over a probe file destroys
    `_provenance`, and the next run then fails with a bare `KeyError: '_provenance'` — the
    diagnostic class #536 exists to remove, reintroduced by the fix for #536.
    """
    message = probe_drift_message("artifacts_scanned", probe=MARKER_PROBE)

    # COUNT, not presence: both probe payload lines must carry it. A mutation that dropped the
    # instruction from ONE of them survived a presence check, which would leave a reader
    # correctly told to keep `_provenance` for one probe and silently told to destroy it for the
    # other — the worse half of the bug this replaced.
    assert message.count("keeping `_provenance`") == 2, message
    assert "neither emits `_provenance`" in message
    assert "no output can be pasted over a probe file wholesale" in message
    # And the nesting warning, which is the specific step whose omission produced a bare
    # `KeyError: '_provenance'` on the next run.
    assert "nests HERE, not at top level" in message


def test_every_path_and_command_the_message_names_actually_exists() -> None:
    """A message that names a wrong path is worse than the bare number it replaced."""
    for probe in (MARKER_PROBE, FLOOR_PROBE):
        path = ROOT / probe
        assert path.is_file(), f"the drift message names a probe that does not exist: {probe}"
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert "_provenance" in payload, (
            f"{probe} has no `_provenance`; the message's keep-provenance instruction is stale"
        )
    assert (ROOT / DECISION_RECORD).is_file()

    marker_provenance = json.loads((ROOT / MARKER_PROBE).read_text(encoding="utf-8"))["_provenance"]
    assert "recursive_variant" in marker_provenance, (
        "the message says the recursive payload nests under `_provenance.recursive_variant`"
    )
    assert "current_corpus" in marker_provenance, (
        "the message says `_provenance.current_corpus` quotes the counts in prose"
    )

    for command in (MARKER_COMMAND, MARKER_RECURSIVE_COMMAND, FLOOR_COMMAND):
        script = command.split()[1]
        assert (ROOT / script).is_file(), f"the drift message names a missing script: {script}"


def test_the_message_distinguishes_the_recursive_variant_in_its_own_heading() -> None:
    """The site whose failure is about the nested payload must say which payload it means."""
    plain = probe_drift_message("rows", probe=MARKER_PROBE)
    recursive = probe_drift_message("rows", probe=MARKER_PROBE, variant="recursive variant")

    assert "(recursive variant)" in recursive
    assert "(recursive variant)" not in plain


def test_each_surface_is_paired_with_the_command_that_actually_produces_it() -> None:
    """The inversion a substring pin could not see.

    A round showed that swapping `MARKER_COMMAND` and `FLOOR_COMMAND` in the surface list left
    every assertion in this file green while instructing the reader to paste floor output over
    the marker payload — strictly worse than the bare number the message replaced. So the
    pairing is asserted, not just the presence of both strings.
    """
    pairs = {surface: command for surface, command in UPDATE_SURFACES}
    for surface, command in pairs.items():
        if command is None:
            continue
        if MARKER_PROBE in surface and "recursive_variant" in surface:
            assert command == MARKER_RECURSIVE_COMMAND, surface
        elif MARKER_PROBE in surface:
            assert command == MARKER_COMMAND, surface
        elif FLOOR_PROBE in surface:
            assert command == FLOOR_COMMAND, surface
        else:
            raise AssertionError(f"a command was paired with a surface it cannot produce: {surface}")

    # And every payload-replacing surface must say to keep `_provenance` — one per probe, so a
    # duplicated marker line cannot satisfy the count on its own.
    keepers = [surface for surface, command in UPDATE_SURFACES if command and "keeping `_provenance`" in surface]
    assert len(keepers) == 2, keepers
    assert any(MARKER_PROBE in surface for surface in keepers)
    assert any(FLOOR_PROBE in surface for surface in keepers)


def test_the_cause_lists_are_not_swapped() -> None:
    """The other inversion: the classification itself, not its vocabulary.

    Every earlier assertion here was a substring test over the whole message, so swapping the
    corpus and rule lists left them all green while telling the reader to re-record on a rule
    change — the exact harm round 1 caught in the unhedged version.
    """
    corpus = "\n".join(CORPUS_CAUSES)
    rules = "\n".join(RULE_CAUSES)

    # A corpus cause is about the measured artifacts; a rule cause is about the measuring code.
    assert "charness-artifacts/quality/" in corpus
    assert "quality/history/" in corpus
    assert GATE_MODULE not in corpus, "a rule cause leaked into the corpus list"
    assert "inventory-consumer-fields.json" not in corpus

    assert GATE_MODULE in rules
    assert "MIN_ENGAGEMENT_RESIDUAL_CHARS" in rules
    assert "inventory-consumer-fields.json" in rules
    assert "REWRITTEN" not in rules, "a corpus cause leaked into the rule list"

    message = probe_drift_message("floor", probe=FLOOR_PROBE)
    # And the message must place them under the right headings, in order.
    corpus_at = message.index("If the CORPUS changed, re-record")
    rules_at = message.index("If the RULE changed, do NOT re-record yet")
    first_corpus_cause = message.index(CORPUS_CAUSES[0])
    first_rule_cause = message.index(RULE_CAUSES[0])
    assert corpus_at < first_corpus_cause < rules_at < first_rule_cause


def test_the_discrimination_paths_include_the_module_the_thresholds_actually_live_in() -> None:
    """Version 2 said to diff "the measuring scripts"; three of four thresholds are not there.

    A reader following that saw no diff, concluded the corpus had changed, and would have
    re-recorded a rule regression. The paths are now named as files.
    """
    assert GATE_MODULE in DISCRIMINATION_PATHS
    assert "charness-artifacts/quality/" in DISCRIMINATION_PATHS
    for path in DISCRIMINATION_PATHS:
        target = ROOT / path
        assert target.exists(), f"the drift message tells a reader to diff a missing path: {path}"

    message = probe_drift_message("floor", probe=FLOOR_PROBE)
    assert "the thresholds are NOT in the measure" in message


def test_the_message_does_not_claim_a_field_the_floor_probe_lacks() -> None:
    """Version 2 said BOTH probes have `_provenance.current_corpus`. Only the marker one does.

    The pin that was supposed to cover this checked the marker probe only, so it was scoped
    around the false claim instead of catching it.
    """
    floor_provenance = json.loads((ROOT / FLOOR_PROBE).read_text(encoding="utf-8"))["_provenance"]
    assert "current_corpus" not in floor_provenance, (
        "the floor probe grew a `current_corpus` field; the message now says it has none"
    )
    message = probe_drift_message("floor", probe=FLOOR_PROBE)
    assert "The floor probe has NO such field" in message


def test_the_message_does_not_claim_D47_names_the_floor_probe() -> None:
    """Version 2 said D47 cites the floor probe's `field_mention_residuals.count`. It does not.

    The coupling is real but it is asserted by a test, not by D47's text, so a reader who went
    to verify the claim found nothing and could conclude a floor drift needs no D47 edit.
    """
    decision_text = (ROOT / DECISION_RECORD).read_text(encoding="utf-8")
    assert "field_mention_residuals" not in decision_text, (
        "D47 now names the field; the message's `does NOT name the floor probe` line is stale"
    )
    message = probe_drift_message("floor", probe=FLOOR_PROBE)
    assert "does NOT name the floor probe" in message

