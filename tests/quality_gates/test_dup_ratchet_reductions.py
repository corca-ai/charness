"""Item-5 slice D: membership-reduction pre-pass (dup_ratchet_lib.classify_reductions).

Split out of ``test_dup_ratchet.py`` (test-file length cap): ``classify_reductions``
is a self-contained pure function (S4-Defer-3, resolved) — before the hard arm runs,
a candidate-new fingerprint whose member-hash multiset is a PROPER sub-multiset of a
vanished baseline family's is a membership REDUCTION (advisory), not new duplication.
See charness-artifacts/spec/boy-scout-dup-ratchet.md (Slice 4, S4-Defer-3) and
tests/quality_gates/test_dup_ratchet.py for the CLI-level (end-to-end) reduction
coverage that builds on this pure policy.
"""

from __future__ import annotations

from .support import ROOT
from .seeding_support import load_module

SCRIPTS = ROOT / "skills" / "public" / "quality" / "scripts"


def _load(name: str):
    return load_module(f"{name}_inproc", SCRIPTS / f"{name}.py")


lib = _load("dup_ratchet_lib")


def test_classify_reductions_proper_sub_multiset_is_a_reduction() -> None:
    # baseline {A,A,B} vanished, live {A,B} candidate -> reduction.
    live = {"new": ["A", "B"]}
    baseline = {"old": ["A", "A", "B"]}
    assert lib.classify_reductions(live, baseline, {"new"}) == [
        {"new_fingerprint": "new", "old_fingerprint": "old"}
    ]


def test_classify_reductions_grow_is_not_a_reduction() -> None:
    # baseline {A,B}, live {A,A,B} -> NOT a reduction (candidate is a SUPERSET, not
    # a proper sub-multiset) -> the CLI must hard-block it as genuine new/changed dup.
    live = {"new": ["A", "A", "B"]}
    baseline = {"old": ["A", "B"]}
    assert lib.classify_reductions(live, baseline, {"new"}) == []


def test_classify_reductions_equal_multiset_is_not_a_reduction() -> None:
    # Equal totals is NOT "strictly smaller" -> not a proper sub-multiset (would only
    # happen if the same fingerprint reappeared, which can't be "vanished" anyway).
    live = {"new": ["A", "B"]}
    baseline = {"old": ["A", "B"]}
    assert lib.classify_reductions(live, baseline, {"new"}) == []


def test_classify_reductions_disjoint_content_is_genuine_new() -> None:
    live = {"new": ["X", "Y"]}
    baseline = {"old": ["A", "B"]}
    assert lib.classify_reductions(live, baseline, {"new"}) == []


def test_classify_reductions_over_represented_member_is_not_a_sub_multiset() -> None:
    # baseline {A,B,C} vanished (total=3), candidate {A,A} has a strictly SMALLER
    # total (2 < 3) but is NOT a sub-multiset: "A" appears twice in the candidate
    # against only one "A" in the vanished family. Total alone is not sufficient --
    # every per-member count must also fit, or this is genuine new/changed content.
    live = {"new": ["A", "A"]}
    baseline = {"old": ["A", "B", "C"]}
    assert lib.classify_reductions(live, baseline, {"new"}) == []


def test_classify_reductions_ignores_baseline_families_still_live() -> None:
    # A baseline family still present in the live scan is not "vanished" -- it
    # cannot be the reduction's origin even if it would otherwise superset the
    # candidate (this is what "new_code" already excludes via gate_baseline_ids).
    live = {"still_here": ["A", "B"], "new": ["A"]}
    baseline = {"still_here": ["A", "B"]}
    assert lib.classify_reductions(live, baseline, {"new"}) == []


def test_classify_reductions_deterministic_pairing_prefers_smallest_then_lexicographic() -> None:
    live = {"new": ["A"]}
    baseline = {"zzz_big": ["A", "B", "C"], "aaa_small": ["A", "B"], "bbb_small": ["A", "X"]}
    # Two vanished supersets tie at total=2 ("aaa_small", "bbb_small"); "aaa_small"
    # wins lexicographically. The total=3 superset loses to both smaller ones.
    assert lib.classify_reductions(live, baseline, {"new"}) == [
        {"new_fingerprint": "new", "old_fingerprint": "aaa_small"}
    ]


def test_classify_reductions_candidate_absent_from_live_is_skipped_not_a_crash() -> None:
    # A candidate name not present in live_members (should not happen in practice;
    # the CLI only asks about fingerprints from the scan it just ran) is a no-op,
    # never an error -- classify_reductions stays a pure best-effort classifier.
    assert lib.classify_reductions({}, {"old": ["A"]}, {"ghost"}) == []
