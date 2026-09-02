"""Every checked-in probe record's stimulus still reproduces.

WHY THIS EXISTS AS A GATE AND NOT ONLY AS A CLI. A round-1 bounded review grepped the tree
and found that nothing ran `--replay-stimulus`: no floor, no surface, no closeout, no
standing check. `#674`'s premise is "thirteen review rounds, no gate", and an opt-in CLI
nobody invokes leaves that premise exactly as true for record fourteen. The detector was
inert.

The sweep is deliberately here rather than in the pre-commit path. Each document costs one
resolve whole plus one or two per declaration, every one a real subprocess, so the corpus
costs tens of seconds -- far over the ~1s pre-commit budget
(`docs/validator-timing-layers.md`) and right for the standing lane, where the
corpus changes rarely and a dead control is expensive to find any other way.

WHAT A FAILURE HERE MEANS: the named record's `## Stimulus` declares something the owning
reader does not honor, so the polarity control it contrasts against could not have failed.
Run `python3 scripts/gates/check_probe_record.py --record <path> --replay-stimulus` for the
reason. It does NOT mean the record's conclusion is wrong -- it means the reproduction
steps as published do not reproduce, which is a claim defect on a proof artifact.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import probe_record_lib, probe_stimulus_replay

ROOT = Path(__file__).resolve().parents[2]
RECORDS = sorted((ROOT / "charness-artifacts" / "probe").glob("*.md"))


def _stimulus(record: Path) -> str:
    parsed = probe_record_lib.parse_probe_record(record.read_text(encoding="utf-8"))
    return (parsed.get("sections") or {}).get("stimulus") or ""


# DERIVED, not a hand-written count. Round 2 found both floors written as `>= 13` against a
# 24-file corpus: eleven records could be deleted with the gate green, and the number gains a
# silent slot of slack the moment a fourteenth adapter record lands. The set of records that
# WRITE an adapter document is what this gate is a floor for, so it is computed.
ADAPTER_RECORDS = [record for record in RECORDS if probe_stimulus_replay.extract_adapter_documents(_stimulus(record))]


def test_the_corpus_glob_matched_something():
    """A glob that silently matched nothing would make every test below vacuously green --
    the shape this repo's `no silent caps` rule exists to refuse."""
    assert RECORDS, "no probe records matched charness-artifacts/probe/*.md"
    assert ADAPTER_RECORDS, "no probe record writes an adapter document; the sweep proves nothing"


@pytest.mark.parametrize("record", RECORDS, ids=lambda path: path.stem)
def test_a_checked_in_records_stimulus_still_reproduces(record: Path):
    parsed = probe_record_lib.parse_probe_record(record.read_text(encoding="utf-8"))
    result = probe_stimulus_replay.replay_probe_stimulus(parsed, repo_root=ROOT)
    assert result["state"] != probe_stimulus_replay.STIMULUS_NOT_ESTABLISHED, result["reasons"]


def test_every_record_that_writes_an_adapter_is_actually_replayed():
    """`not-configured` is a legitimate answer for a record that writes no adapter document,
    and it is also what every extraction miss degrades to -- so a regression that stopped
    recognising heredocs would turn the sweep above green while measuring nothing.

    This counts DOCUMENTS EXTRACTED, not records passing. The first cut counted records
    reaching `evaluated`, which conflates `was replayed` with `passed`: one record honestly
    regressing failed both tests, and this one failed with the misleading message `not all
    skipped`."""
    unreplayed = [
        record.stem
        for record in ADAPTER_RECORDS
        if probe_stimulus_replay.replay_probe_stimulus(
            probe_record_lib.parse_probe_record(record.read_text(encoding="utf-8")), repo_root=ROOT
        )["state"] == probe_stimulus_replay.STIMULUS_NOT_CONFIGURED
    ]
    assert not unreplayed, unreplayed
