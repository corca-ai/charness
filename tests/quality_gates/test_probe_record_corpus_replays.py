"""Every checked-in probe record's stimulus still reproduces.

WHY THIS EXISTS AS A GATE AND NOT ONLY AS A CLI. A round-1 bounded review grepped the tree
and found that nothing ran `--replay-stimulus`: no floor, no surface, no closeout, no
standing check. `#674`'s premise is "thirteen review rounds, no gate", and an opt-in CLI
nobody invokes leaves that premise exactly as true for record fourteen. The detector was
inert.

The sweep is deliberately here rather than in the pre-commit path. It costs ~8s for the
whole corpus -- each record resolves its adapter documents once per declaration through a
real subprocess -- which is far over the ~1s pre-commit budget
(`docs/conventions/validator-timing-layers.md`) and right for the standing lane, where the
corpus changes rarely and a dead control is expensive to find any other way.

WHAT A FAILURE HERE MEANS: the named record's `## Stimulus` declares something the owning
reader does not honor, so the polarity control it contrasts against could not have failed.
Run `python3 scripts/check_probe_record.py --record <path> --replay-stimulus` for the
reason. It does NOT mean the record's conclusion is wrong -- it means the reproduction
steps as published do not reproduce, which is a claim defect on a proof artifact.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import probe_record_lib, probe_stimulus_replay

ROOT = Path(__file__).resolve().parents[2]
RECORDS = sorted((ROOT / "charness-artifacts" / "probe").glob("*.md"))


def test_the_corpus_is_not_empty():
    """A glob that silently matched nothing would make every test below vacuously green --
    the shape this repo's `no silent caps` rule exists to refuse."""
    assert len(RECORDS) >= 13, [path.name for path in RECORDS]


@pytest.mark.parametrize("record", RECORDS, ids=lambda path: path.stem)
def test_a_checked_in_records_stimulus_still_reproduces(record: Path):
    parsed = probe_record_lib.parse_probe_record(record.read_text(encoding="utf-8"))
    result = probe_stimulus_replay.replay_probe_stimulus(parsed, repo_root=ROOT)
    assert result["state"] != probe_stimulus_replay.STIMULUS_NOT_ESTABLISHED, result["reasons"]


def test_the_adapter_records_are_actually_replayed_and_not_all_skipped():
    """`not-configured` is a legitimate answer for a record that writes no adapter document,
    and it is also what every extraction miss degrades to. Without this, a regression that
    stopped recognising heredocs would turn the whole sweep green."""
    replayed = [
        record.stem
        for record in RECORDS
        if probe_stimulus_replay.replay_probe_stimulus(
            probe_record_lib.parse_probe_record(record.read_text(encoding="utf-8")), repo_root=ROOT
        )["state"] == probe_stimulus_replay.STIMULUS_EVALUATED
    ]
    assert len(replayed) >= 13, replayed
