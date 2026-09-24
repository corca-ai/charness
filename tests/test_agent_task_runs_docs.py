"""Task-execution docs alignment: carrier vs executor wording and the keep_worktree bound.

`docs/agent-task-runs.md` is the contract surface for `charness task run`
receipts. Two wordings drifted from the implementation: "carrier" was used
for the require-change prompt shaping as well as the candidate carrier, and
the retention paragraph read as if `keep_worktree` pins a worktree while the
sweep expires kept copies past its newest-N bound. These tests tie the page's
claims to the code constants so the drift fails instead of compounding.
"""

from __future__ import annotations

from pathlib import Path

from scripts.gates_support import runtime_root_retention as retention

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs" / "agent-task-runs.md"


def _page() -> str:
    return PAGE.read_text(encoding="utf-8")


def test_carrier_means_candidate_carrier_and_executor_means_agent_runner() -> None:
    body = _page()
    assert "Executor names" in body
    assert "carrier names where the candidate lives" in body
    for kind in ("commit-only", "commit-plus-dirty", "worktree-only", "unknown"):
        assert kind in body
    assert "the carrier injects scope" not in body


def test_keep_worktree_newest_n_hold_matches_the_sweep_limit() -> None:
    body = _page()
    assert "newest-N hold, not a pin" in body
    assert f"newest {retention.KEPT_WORKTREE_LIMIT} kept worktrees per key" in body
    assert "verified salvage" in body


def test_release_needs_a_commit_carried_candidate_with_clean_proof() -> None:
    body = _page()
    assert "`commit-only`, clean tree" in body
    assert "`clean`/`noop` changed-line proof" in body
    assert "`keep_worktree` true" in body
