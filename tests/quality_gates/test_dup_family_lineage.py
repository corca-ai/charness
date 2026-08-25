from __future__ import annotations

import importlib.util
from pathlib import Path

# provenance-contract fixture: duplicate_lineage

ROOT = Path(__file__).parents[2]
SCRIPT = ROOT / "skills/public/quality/scripts/dup_family_lineage.py"
spec = importlib.util.spec_from_file_location("dup_family_lineage", SCRIPT)
assert spec is not None and spec.loader is not None
lineage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lineage)


def _family(fingerprint: str, paths: list[str], hashes: list[str]) -> dict:
    return {"fingerprint": fingerprint, "member_paths": paths, "member_hashes": hashes}


def test_relation_distinguishes_rotation_growth_reduction_and_merge() -> None:
    old = _family("old", ["a.py", "b.py"], ["a", "b"])
    assert lineage.relation(old, _family("rot", ["a.py", "b.py"], ["a2", "b2"])) == "rotation-proposal"
    assert lineage.relation(old, _family("grow", ["a.py", "b.py", "c.py"], ["a", "b", "c"])) == "membership-growth"
    assert lineage.relation(old, _family("shrink", ["a.py"], ["a"])) == "membership-reduction"
    assert lineage.relation(old, _family("merge", ["b.py", "c.py"], ["b", "c"])) == "family-merge-proposal"


def test_propose_rotation_never_accepts_or_suppresses() -> None:
    proposals = lineage.propose(
        live_members={"new": ["a2", "b2"]},
        live_spans={"new": [{"file": "a.py"}, {"file": "b.py"}]},
        baseline_families=[_family("old", ["a.py", "b.py"], ["a", "b"])],
        reviewed_ids={"old"},
    )
    assert proposals == [{
        "new_fingerprint": "new",
        "old_fingerprints": ["old"],
        "relation": "rotation-proposal",
        "review_status": "proposal-only",
    }]


def test_propose_mixed_cohort_keeps_growth_and_new_distinct() -> None:
    proposals = lineage.propose(
        live_members={
            "rot": ["a2", "b2"],
            "grow": ["a", "b", "c"],
            "fresh": ["x", "y"],
        },
        live_spans={
            "rot": [{"file": "a.py"}, {"file": "b.py"}],
            "grow": [{"file": "a.py"}, {"file": "b.py"}, {"file": "c.py"}],
            "fresh": [{"file": "x.py"}, {"file": "y.py"}],
        },
        baseline_families=[_family("old", ["a.py", "b.py"], ["a", "b"])],
        reviewed_ids={"old"},
    )
    assert [(row["new_fingerprint"], row["relation"]) for row in proposals] == [
        ("fresh", "new-family"),
        ("grow", "membership-growth"),
        ("rot", "rotation-proposal"),
    ]


def test_missing_lineage_paths_do_not_create_noise_or_accept() -> None:
    assert lineage.propose(
        live_members={"new": ["x"]},
        live_spans={"new": [{"file": "x.py"}]},
        baseline_families=[{"fingerprint": "old", "member_hashes": ["old"]}],
        reviewed_ids={"old"},
    ) == []


def test_missing_lineage_paths_are_explicitly_not_approval_eligible() -> None:
    assert lineage.readiness(
        [_family("old", [], ["old"])], reviewed_ids={"old"}
    ) == {
        "status": "unavailable",
        "reason_code": "baseline-member-paths-missing",
        "missing_fingerprints": ["old"],
    }
