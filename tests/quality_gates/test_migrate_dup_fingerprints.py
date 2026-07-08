"""Item-5 slice D: dup-fingerprint algo migration planner (migrate_dup_fingerprints_lib).

Unit coverage for the PURE planning functions the one-shot v1->v2 migration tool
uses to remap the gate baseline, the advisory baseline, and the dup-review overlay
against a synthetic live scan -- no real nose invocation needed. See
charness-artifacts/spec/boy-scout-dup-ratchet.md (Slice D, S4-D8/S4-Defer-1/3):
survivors remap, vanished ids drop, requires_review candidates are refused unless
named, class/note/reviewed_at survive byte-for-byte, and the collision assertion
fires on an artificial collision.
"""

from __future__ import annotations

import importlib.util

from .support import ROOT

SCRIPTS = ROOT / "skills" / "public" / "quality" / "scripts"


def _load(name: str):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"{name}_inproc", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


plan = _load("migrate_dup_fingerprints_lib")


def _entry(v1: str, v2: str, member_hashes: list[str], nose_id: str | None = None) -> dict:
    return {"v1": v1, "v2": v2, "member_hashes": member_hashes, "nose_id": nose_id or v2, "files": []}


# --------------------------------------------------------------------------- #
# collision_report
# --------------------------------------------------------------------------- #
def test_collision_report_ok_when_counts_match() -> None:
    enriched = [_entry("v1a", "v2a", ["m1"], "n1"), _entry("v1b", "v2b", ["m2"], "n2")]
    report = plan.collision_report(enriched)
    assert report == {"distinct_v2_fingerprints": 2, "distinct_nose_family_ids": 2, "ok": True}


def test_collision_report_fires_on_artificial_collision() -> None:
    # Two distinct nose families reduced to the SAME v2 fingerprint (an
    # implementation bug, not a corpus fact under PQ1's global-clustering guarantee).
    enriched = [_entry("v1a", "SAME", ["m1"], "n1"), _entry("v1b", "SAME", ["m2"], "n2")]
    report = plan.collision_report(enriched)
    assert report["distinct_v2_fingerprints"] == 1
    assert report["distinct_nose_family_ids"] == 2
    assert report["ok"] is False


# --------------------------------------------------------------------------- #
# plan_gate_baseline_migration
# --------------------------------------------------------------------------- #
def test_gate_migration_remaps_survivors() -> None:
    enriched = [_entry("v1a", "v2a", ["m1", "m2"])]
    result = plan.plan_gate_baseline_migration({"v1a"}, enriched, [])
    assert result["survivors"] == ["v1a"]
    assert result["vanished"] == []
    assert result["new_members"] == {"v2a": ["m1", "m2"]}


def test_gate_migration_drops_vanished_old_ids() -> None:
    enriched = [_entry("v1a", "v2a", ["m1"])]
    result = plan.plan_gate_baseline_migration({"v1a", "v1_gone"}, enriched, [])
    assert result["vanished"] == ["v1_gone"]
    assert "v1_gone" not in result["new_members"]


def test_gate_migration_refuses_requires_review_without_accept() -> None:
    enriched = [_entry("v1x", "v2x", ["m"])]  # v1x was NOT in the old baseline
    result = plan.plan_gate_baseline_migration(set(), enriched, [])
    assert result["requires_review"] == ["v2x"]
    assert result["accepted_new"] == []
    assert result["new_members"] == {}  # excluded, not silently absorbed


def test_gate_migration_accepts_named_requires_review_family() -> None:
    enriched = [_entry("v1x", "v2x", ["m"])]
    result = plan.plan_gate_baseline_migration(set(), enriched, ["v2x"])
    assert result["accepted_new"] == ["v2x"]
    assert result["requires_review"] == []
    assert result["new_members"] == {"v2x": ["m"]}


def test_gate_migration_survivors_and_requires_review_coexist() -> None:
    enriched = [_entry("v1a", "v2a", ["m1"]), _entry("v1x", "v2x", ["m2"])]
    result = plan.plan_gate_baseline_migration({"v1a"}, enriched, [])
    assert result["survivors"] == ["v1a"]
    assert result["requires_review"] == ["v2x"]
    assert result["new_members"] == {"v2a": ["m1"]}  # only the survivor, not the candidate


# --------------------------------------------------------------------------- #
# plan_advisory_baseline_migration
# --------------------------------------------------------------------------- #
def test_advisory_migration_remaps_survivors_drops_vanished_ignores_new() -> None:
    enriched = [_entry("v1a", "v2a", ["m1"]), _entry("v1x", "v2x", ["m2"])]  # v1x is a brand-new live family
    result = plan.plan_advisory_baseline_migration({"v1a", "v1_gone"}, enriched)
    assert result["survivors"] == ["v1a"]
    assert result["vanished"] == ["v1_gone"]
    assert result["new_ids"] == ["v2a"]  # v2x excluded -- advisory never auto-accepts new families


# --------------------------------------------------------------------------- #
# plan_review_migration
# --------------------------------------------------------------------------- #
def test_review_migration_remaps_id_preserves_class_note_reviewed_at_verbatim() -> None:
    entries = [{
        "surface": "code", "id": "v1a", "class": "intentional",
        "note": "hand-reviewed: portable boilerplate", "reviewed_at": "2026-05-01",
    }]
    enriched = [_entry("v1a", "v2a", ["m1"])]
    result = plan.plan_review_migration(entries, enriched)
    assert result["entries"] == [{
        "surface": "code", "id": "v2a", "class": "intentional",
        "note": "hand-reviewed: portable boilerplate", "reviewed_at": "2026-05-01",
    }]
    assert result["dropped_ids"] == []


def test_review_migration_drops_orphaned_entry_and_logs_id() -> None:
    entries = [
        {"surface": "code", "id": "v1a", "class": "fixable", "note": "n", "reviewed_at": "d"},
        {"surface": "code", "id": "v1_orphan", "class": "intentional", "note": "n2", "reviewed_at": "d2"},
    ]
    enriched = [_entry("v1a", "v2a", ["m1"])]  # v1_orphan is not in the live scan
    result = plan.plan_review_migration(entries, enriched)
    ids = {e["id"] for e in result["entries"]}
    assert ids == {"v2a"}
    assert result["dropped_ids"] == ["v1_orphan"]


def test_review_migration_passes_through_doc_entries_untouched() -> None:
    entries = [{"surface": "doc", "id": "path#heading", "class": "intentional", "note": "n", "reviewed_at": "d"}]
    result = plan.plan_review_migration(entries, [])  # no code families in the live scan at all
    assert result["entries"] == entries
    assert result["dropped_ids"] == []


def test_review_migration_skips_non_dict_entries_defensively() -> None:
    result = plan.plan_review_migration(["not-a-dict", 5, None], [])
    assert result["entries"] == [] and result["dropped_ids"] == []
