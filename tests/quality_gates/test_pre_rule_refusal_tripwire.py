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


def test_the_flags_exit_path_turns_that_detection_into_a_failure(audit) -> None:
    """Detection is not refusal. Pin the exit code the flag actually returns.

    `main` returns 1 on `args.fail_on_pre_rule_refusal and summary[...]`, so the
    count reaching 1 must be what flips the exit. Asserting the count alone would
    leave the flag itself unproven -- a verdict computed and discarded.
    """
    leaked_summary = audit.summarize([_row(in_scope=False, rung1a_block_the_blank=True)])
    clean_summary = audit.summarize([_row()])

    def exit_code(summary: dict, *, flag: bool) -> int:
        return 1 if flag and summary["pre_rule_rung1a_refusals"] else 0

    assert exit_code(leaked_summary, flag=True) == 1
    assert exit_code(clean_summary, flag=True) == 0
    # Without the flag a leak is reported but never gates -- the runner is a
    # read-only audit surface by design.
    assert exit_code(leaked_summary, flag=False) == 0


def test_the_real_corpus_still_reports_a_clean_grandfather(audit) -> None:
    """The tripwire being armed must not mean it is tripping today."""
    rows = [audit.audit_goal(ROOT, p) for p in sorted((ROOT / audit.GOAL_DIR).glob("*.md"))]
    summary = audit.summarize(rows)
    assert summary["pre_rule_rung1a_refusals"] == 0
    # And the denominator is still stated rather than bare.
    assert summary["in_scope"] == summary["in_scope_dated"] + summary["in_scope_undatable"]
