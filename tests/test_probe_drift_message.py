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
    DECISION_RECORD,
    FLOOR_COMMAND,
    FLOOR_PROBE,
    MARKER_COMMAND,
    MARKER_PROBE,
    MARKER_RECURSIVE_COMMAND,
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
    assert "launder a measurement change" in message
    # The rule causes a reader would otherwise mistake for a write.
    assert "inventory-consumer-fields.json" in message
    assert "ENFORCED_FROM_DATE" in message
    assert "git was unavailable" in message
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
    assert "quote the counts in PROSE" in message


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
