"""#473: the forced-scope probe for `--fail-on-pre-rule-refusal`.

`audit_disposition_corpus.py` reports `pre_rule_rung1a_refusals`, and that count
is **structurally 0 for every possible corpus**: `apply_disposition_rungs`
returns at `if not in_scope` before any `disposition_blank` can be set, so
"pre-rule" and "rung-1a refused" are mutually exclusive by control flow. The flag
`--fail-on-pre-rule-refusal` therefore never returned 1 in any real run, and the
module says so honestly in its own docstring.

The resolution is a probe, not a deletion. The flag is a TRIPWIRE, and the
situation it was written for is not "the current corpus" — it is "the grandfather
leaked", i.e. a rung reordered above the scope check. In THAT situation it must
fire. Deleting it would remove a guard for a real regression on the grounds that
the regression has not happened yet; leaving it unproven would leave a guard
nobody has ever seen work.

So these tests construct the leak shape directly and pin that the tripwire fires.
`summarize` is a pure function of the audited rows, which is what makes the
forced scope reachable without corrupting a real goal artifact.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
MODULE = "skills/public/achieve/scripts/audit_disposition_corpus.py"


@pytest.fixture(scope="module")
def audit():
    spec = importlib.util.spec_from_file_location("_audit_disposition_corpus", ROOT / MODULE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["_audit_disposition_corpus"] = module
    spec.loader.exec_module(module)
    return module


def _row(**overrides) -> dict:
    """One audited row in the shape `summarize` consumes."""
    row = {
        "goal": "2026-01-01-x.md",
        "status": "complete",
        "status_normalized": "complete",
        "created": "2026-01-01",
        "in_scope": False,
        "auto_retro_blank": False,
        "retro_improvements_present": True,
        "has_disposition_review_line": True,
        "rung1a_block_the_blank": False,
        "disposition_optout": None,
        "evidence_ok": True,
    }
    row.update(overrides)
    return row


def test_the_count_is_zero_for_every_shape_the_real_corpus_can_produce(audit) -> None:
    """The structural claim the module makes about itself, pinned.

    Pre-rule (`in_scope is False`) and rung-1a-refused are mutually exclusive
    while the scope check precedes the rungs, so no honest row sets both.
    """
    rows = [
        _row(in_scope=False, rung1a_block_the_blank=False),
        _row(in_scope=True, rung1a_block_the_blank=True),
        _row(in_scope=True, rung1a_block_the_blank=False),
        _row(status_normalized="active", in_scope=False),
    ]
    summary = audit.summarize(rows)
    assert summary["pre_rule_rung1a_refusals"] == 0
    assert "structurally 0" in summary["pre_rule_refusal_detectability"]


def test_the_tripwire_fires_when_the_grandfather_leaks(audit) -> None:
    """THE PROBE. Force the mutually-exclusive pair that control flow forbids.

    A row that is both pre-rule and rung-1a-refused is exactly what a rung
    reordered above the scope check would produce. If the tripwire cannot detect
    that, it is a guard that cannot guard and should be deleted instead.
    """
    leaked = _row(goal="2026-01-01-leaked.md", in_scope=False, rung1a_block_the_blank=True)
    summary = audit.summarize([leaked, _row()])
    assert summary["pre_rule_rung1a_refusals"] == 1, (
        "the tripwire cannot see the leak it exists to catch"
    )
    # And the reported detectability must STOP denying the signal once it fires.
    # As a constant it said "this count CANNOT be non-zero" in the one run where
    # it was -- steering a reader away from the only evidence the guard produces.
    detectability = summary["pre_rule_refusal_detectability"]
    assert "ORDERING ASSUMPTION VIOLATED" in detectability
    assert "structurally 0" not in detectability
    assert "2026-01-01-leaked.md" in detectability


def test_the_flags_exit_path_turns_that_detection_into_a_failure(
    audit, monkeypatch, tmp_path, capsys
) -> None:
    """Detection is not refusal. Drive the REAL `main`, not a copy of its one line.

    The first version of this test defined a local `exit_code` helper mirroring
    `main`'s `if args.fail_on_pre_rule_refusal and summary[...]` and asserted
    against that. It would have stayed green with the flag deleted, the condition
    inverted, or `main` returning 0 unconditionally -- a check that cannot fail in
    the situation it was written for, which is the very defect #473 reports.
    """
    leaked = _row(goal="2026-01-01-leaked.md", in_scope=False, rung1a_block_the_blank=True)
    monkeypatch.setattr(audit, "audit_goal", lambda repo_root, path: leaked)
    goals = tmp_path / audit.GOAL_DIR
    goals.mkdir(parents=True)
    (goals / "2026-01-01-leaked.md").write_text("# leaked\n", encoding="utf-8")

    monkeypatch.setattr(
        sys, "argv", ["audit", "--repo-root", str(tmp_path), "--fail-on-pre-rule-refusal"]
    )
    assert audit.main() == 1, "the flag did not refuse on a leak it detected"
    # The refusal must be REPORTED, not just returned: parse the emitted YAML and
    # pin the count, so a `main` that exits 1 while printing a clean summary fails.
    reported = yaml.safe_load(capsys.readouterr().out)
    assert reported["summary"]["pre_rule_rung1a_refusals"] == 1

    # Same leak, no flag: the runner is a read-only audit surface and must not gate.
    monkeypatch.setattr(sys, "argv", ["audit", "--repo-root", str(tmp_path)])
    assert audit.main() == 0

    # Clean corpus with the flag: no refusal.
    monkeypatch.setattr(audit, "audit_goal", lambda repo_root, path: _row())
    monkeypatch.setattr(
        sys, "argv", ["audit", "--repo-root", str(tmp_path), "--fail-on-pre-rule-refusal"]
    )
    assert audit.main() == 0


@pytest.mark.slow_corpus
def test_the_real_corpus_still_reports_a_clean_grandfather(audit) -> None:
    """The tripwire being armed must not mean it is tripping today."""
    rows = [audit.audit_goal(ROOT, p) for p in sorted((ROOT / audit.GOAL_DIR).glob("*.md"))]
    summary = audit.summarize(rows)
    assert summary["pre_rule_rung1a_refusals"] == 0
    # And the denominator is still stated rather than bare.
    assert summary["in_scope"] == summary["in_scope_dated"] + summary["in_scope_undatable"]
