"""S22 (2026-07-28 triage sweep): omitting the classification event disarmed the
brief-before-mutation contract, and `audit_brief.py` had no test module at all.

Non-claim: this checker has no caller in the `issue` workflow today (the skill
never invokes it), so these tests pin the checker's verdict, not an enforced
repo boundary."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from .support import ROOT
from .seeding_support import load_module

SCRIPT_PATH = ROOT / "skills" / "public" / "issue" / "scripts" / "audit_brief.py"
FIXTURE_DIR = SCRIPT_PATH.parent / "fixtures"


def _load_audit_brief():
    return load_module("audit_brief", SCRIPT_PATH)


def _audit(events: list[dict[str, object]]) -> dict[str, object]:
    return _load_audit_brief().audit(events)


def test_mutation_without_any_classification_event_is_a_violation() -> None:
    # The sweep's exact transcript: mutation + close, no classification event.
    # It returned `audit ok: 1 fix-unit(s) checked`, exit 0.
    summary = _audit(
        [
            {"kind": "mutation", "issue": 143, "tool": "Edit"},
            {"kind": "close", "issue": 143},
        ]
    )

    assert summary["ok"] is False
    assert summary["violations"][0]["issue"] == 143


def test_classification_recorded_after_the_mutation_is_a_violation() -> None:
    # Declaring the classification later is the same disarm: at mutation time the
    # unit was unclassified, so the contract had nothing to arm it.
    summary = _audit(
        [
            {"kind": "mutation", "issue": 143, "tool": "Edit"},
            {"kind": "classification", "issue": 143, "classification": "feature"},
        ]
    )

    assert summary["ok"] is False


def test_unrecognized_classification_value_is_a_violation() -> None:
    summary = _audit(
        [
            {"kind": "classification", "issue": 143, "classification": "featrue"},
            {"kind": "mutation", "issue": 143, "tool": "Edit"},
        ]
    )

    assert summary["ok"] is False
    assert "featrue" in summary["violations"][0]["reason"]


def test_checked_in_fixtures_keep_their_verdicts() -> None:
    module = _load_audit_brief()
    verdicts = {
        path.name: module.audit(module.load_transcript(path))["ok"]
        for path in sorted(FIXTURE_DIR.glob("transcript-*.json"))
    }

    assert verdicts == {
        "transcript-bad-jumped-to-mutation.json": False,
        "transcript-good-bug.json": True,
        "transcript-good-feature-pause.json": True,
        "transcript-good-feature-trivial.json": True,
    }


def test_bug_class_mutation_without_a_brief_still_passes() -> None:
    # Only feature / deferred-work owe a brief; arming on omission must not turn
    # every bug fix into a violation.
    summary = _audit(
        [
            {"kind": "classification", "issue": 145, "classification": "bug"},
            {"kind": "mutation", "issue": 145, "tool": "Edit"},
        ]
    )

    assert summary["ok"] is True


def test_transcript_events_round_trip_as_json() -> None:
    # The fixtures are the checker's public input shape; keep them loadable.
    for path in sorted(FIXTURE_DIR.glob("transcript-*.json")):
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        assert isinstance(payload["events"], list) and payload["events"]


def _load_transcript_text(tmp_path: Path, text: str):
    path = tmp_path / "transcript.json"
    path.write_text(text, encoding="utf-8")
    return _load_audit_brief().load_transcript(path)


def test_empty_transcript_is_a_transcript_error_not_a_clean_audit(tmp_path: Path) -> None:
    # It used to load fine and report `audit ok: 0 fix-unit(s) checked`, exit 0 —
    # the same absent-input-certifies-itself shape this checker exists to catch.
    with pytest.raises(ValueError, match="nothing to audit"):
        _load_transcript_text(tmp_path, json.dumps({"events": []}))


def test_non_numeric_issue_is_reported_as_a_transcript_error(tmp_path: Path) -> None:
    # Without the check the crash surfaced from audit(), outside main()'s try
    # block: a traceback and exit 1, indistinguishable from a real audit failure.
    with pytest.raises(ValueError, match="non-numeric"):
        _load_transcript_text(
            tmp_path,
            json.dumps({"events": [{"kind": "mutation", "issue": "corca-ai/charness#143"}]}),
        )
