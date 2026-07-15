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
import json
import re
from pathlib import Path

import pytest

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
cli = _load("migrate_dup_fingerprints")
baseline_lib = _load("dup_ratchet_baseline_lib")
fingerprint = _load("nose_fingerprint_lib")


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


def test_cli_dry_run_reports_plan_without_writing(monkeypatch, tmp_path: Path, capsys) -> None:
    # In-process pin of the CLI surface (argv/stdout/exit contract) in dry-run
    # mode. Keep it independent of the installed nose version: live scanner
    # upgrades are separately covered by the migration collision guard.
    report = {
        "ok": True,
        "mode": "dry-run",
        "collision": {"ok": True},
    }
    monkeypatch.setattr(cli, "run", lambda *_args, **_kwargs: report)

    rc = cli.main(["--repo-root", str(tmp_path), "--json"])
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert rc == 0
    assert payload["mode"] == "dry-run"
    assert payload["collision"]["ok"] is True


def test_load_skill_runtime_bootstrap_import_error(monkeypatch, tmp_path: Path) -> None:
    # The bootstrap shim is a byte-identical canonical block shared across every
    # skill script (check_bootstrap_shim_consistency.py enforces this, so it cannot
    # carry a per-file pragma comment); this test exercises its unreachable-in-
    # practice branch directly, mirroring the same pin for inventory_nose_clones.py
    # in tests/test_nose_inprocess_coverage.py.
    isolated = tmp_path / "deep" / "nest" / "x.py"
    isolated.parent.mkdir(parents=True)
    monkeypatch.setattr(cli, "__file__", str(isolated))
    with pytest.raises(ImportError):
        cli._load_skill_runtime_bootstrap()


def test_migrate_cli_help_documents_repo_root_and_json(capsys) -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli.parse_args(["--help"])
    assert exc_info.value.code == 0
    output = capsys.readouterr().out
    expected = {
        "--repo-root": "Repository root containing the dup-ratchet artifacts to migrate",
        "--json": "Emit the migration report as JSON",
    }
    for option, fragment in expected.items():
        match = re.search(rf"^  {re.escape(option)}\b.*$", output, re.MULTILINE)
        assert match, f"missing help option: {option}"
        next_option = re.search(r"^  --[a-z][a-z-]*\b", output[match.end() :], re.MULTILINE)
        end = match.end() + next_option.start() if next_option else len(output)
        option_block = re.sub(r"\s+", " ", output[match.start() : end])
        assert fragment in option_block, f"missing help for {option}: {fragment}"


# --------------------------------------------------------------------------- #
# _read_old_gate_ids -- v2-flat fallback read (this tool is the one place
# allowed to read either the pre-migration v2 shape or the v3 shape).
# --------------------------------------------------------------------------- #
def test_read_old_gate_ids_reads_v2_flat_shape() -> None:
    assert cli._read_old_gate_ids({"code_family_fingerprints": ["a", "b", 5, ""]}) == {"a", "b"}


def test_read_old_gate_ids_none_on_garbage() -> None:
    assert cli._read_old_gate_ids(None) is None
    assert cli._read_old_gate_ids("nope") is None
    assert cli._read_old_gate_ids({"code_family_fingerprints": "nope"}) is None
    assert cli._read_old_gate_ids({}) is None


# --------------------------------------------------------------------------- #
# build_report -- error branches (no-scope-paths / scan-failed / unreadable-
# members / collision-check-failed), each via a monkeypatched seam.
# --------------------------------------------------------------------------- #
def test_build_report_no_scope_paths_refuses(tmp_path: Path) -> None:
    args = cli.parse_args(["--repo-root", str(tmp_path)])
    report = cli.build_report(tmp_path, {}, args)
    assert report["ok"] is False and report["status"] == "no-scope-paths"


def test_build_report_scan_failed(monkeypatch, tmp_path: Path) -> None:
    args = cli.parse_args(["--repo-root", str(tmp_path), "--scope-path", "src"])
    monkeypatch.setattr(cli._scan, "scan_families", lambda *_a, **_k: (None, "nose unavailable", ""))
    report = cli.build_report(tmp_path, {}, args)
    assert report["ok"] is False and report["status"] == "scan-failed"
    assert "nose unavailable" in report["messages"][0]


def test_build_report_unreadable_members(monkeypatch, tmp_path: Path) -> None:
    # A family with a stamped fingerprint but no `locations` -> the v1 recomputation
    # (which reads the raw span) fails -> _enrich_live_scan marks it unreadable ->
    # build_report refuses rather than proceeding with a partial migration.
    args = cli.parse_args(["--repo-root", str(tmp_path), "--scope-path", "src"])
    monkeypatch.setattr(
        cli._scan, "scan_families",
        lambda *_a, **_k: (
            [{"family_fingerprint": "x", "family_member_hashes": ["h"], "family_id": "nid"}],
            None, "0.1.0",
        ),
    )
    report = cli.build_report(tmp_path, {}, args)
    assert report["ok"] is False and report["status"] == "unreadable-members"
    assert report["unreadable_family_ids"] == ["nid"]


def test_build_report_collision_check_failed(monkeypatch, tmp_path: Path) -> None:
    args = cli.parse_args(["--repo-root", str(tmp_path), "--scope-path", "src"])
    (tmp_path / "a.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    monkeypatch.setattr(
        cli._scan, "scan_families",
        lambda *_a, **_k: (
            [{
                "family_fingerprint": "x", "family_member_hashes": ["h"], "family_id": "nid",
                "locations": [{"file": "a.py", "start": 1, "end": 2}],
            }],
            None, "0.1.0",
        ),
    )
    monkeypatch.setattr(
        cli._plan, "collision_report",
        lambda _enriched: {"ok": False, "distinct_v2_fingerprints": 1, "distinct_nose_family_ids": 2},
    )
    report = cli.build_report(tmp_path, {}, args)
    assert report["ok"] is False and report["status"] == "collision-check-failed"


# --------------------------------------------------------------------------- #
# run() -- adapter-invalid short-circuit, and the full --execute write path.
# --------------------------------------------------------------------------- #
def test_run_adapter_invalid(monkeypatch, tmp_path: Path) -> None:
    args = cli.parse_args(["--repo-root", str(tmp_path)])
    monkeypatch.setattr(
        cli._quality_adapter, "load_quality_adapter_strict",
        lambda _root: {"errors": ["bad adapter"], "data": {}},
    )
    report = cli.run(tmp_path, args)
    assert report["ok"] is False and report["status"] == "adapter-invalid"
    assert "bad adapter" in report["messages"][0]


def test_run_execute_writes_three_artifacts(monkeypatch, tmp_path: Path) -> None:
    # Full execute-path integration on a synthetic 2-family corpus: fam_a survives
    # (its old v1 id was accepted) and gets remapped; fam_b is a brand-new v1 id
    # (not previously accepted) and stays requires_review/excluded. The overlay
    # carries one surviving entry (remapped verbatim) and one orphan (dropped).
    (tmp_path / "a.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    (tmp_path / "b.py").write_text("def g():\n    return 2\n", encoding="utf-8")
    fam_a = {
        "family_fingerprint": "v2_a", "family_member_hashes": ["ha"],
        "family_id": "nid_a", "locations": [{"file": "a.py", "start": 1, "end": 2}],
    }
    fam_b = {
        "family_fingerprint": "v2_b", "family_member_hashes": ["hb"],
        "family_id": "nid_b", "locations": [{"file": "b.py", "start": 1, "end": 2}],
    }
    monkeypatch.setattr(cli._scan, "scan_families", lambda *_a, **_k: ([fam_a, fam_b], None, "0.1.0"))
    v1_a = fingerprint.family_content_fingerprint(fam_a, tmp_path, algo="1")

    gate_rel, nose_rel, review_rel = "q/dup-ratchet-baseline.json", "q/nose-baseline.json", "q/dup-review.json"
    (tmp_path / "q").mkdir()
    (tmp_path / gate_rel).write_text(json.dumps({"code_family_fingerprints": [v1_a]}), encoding="utf-8")
    (tmp_path / nose_rel).write_text(json.dumps({"code_family_fingerprints": [v1_a]}), encoding="utf-8")
    (tmp_path / review_rel).write_text(json.dumps({
        "schemaVersion": "charness.quality.dup_review.v1", "fixable_ceiling": 0,
        "entries": [
            {"surface": "code", "id": v1_a, "class": "intentional", "note": "kept", "reviewed_at": "d"},
            {"surface": "code", "id": "orphan_v1", "class": "fixable", "note": "gone", "reviewed_at": "d"},
        ],
    }), encoding="utf-8")

    config = {"scope_paths": ["src"], "review_artifact_path": review_rel, "gate_baseline_path": gate_rel}
    monkeypatch.setattr(
        cli._quality_adapter, "load_quality_adapter_strict",
        lambda _root: {"errors": [], "data": {"dup_ratchet": config}},
    )
    args = cli.parse_args([
        "--repo-root", str(tmp_path), "--scope-path", "src",
        "--nose-baseline-path", nose_rel, "--execute",
    ])
    report = cli.run(tmp_path, args)
    assert report["ok"] is True
    assert any("wrote" in m and gate_rel in m for m in report["messages"])
    assert any("wrote" in m and nose_rel in m for m in report["messages"])
    assert any("wrote" in m and review_rel in m for m in report["messages"])

    written_gate = json.loads((tmp_path / gate_rel).read_text(encoding="utf-8"))
    assert baseline_lib.validate_gate_baseline(written_gate) == []
    # v1_a survived (remapped to v2_a); fam_b's v1 was never accepted, so v2_b
    # stays requires_review and is excluded from the migrated baseline.
    assert baseline_lib.load_gate_baseline_ids(written_gate) == {"v2_a"}

    written_review = json.loads((tmp_path / review_rel).read_text(encoding="utf-8"))
    ids = {e["id"] for e in written_review["entries"]}
    assert ids == {"v2_a"}  # orphan_v1 dropped
    kept_entry = next(e for e in written_review["entries"] if e["id"] == "v2_a")
    assert kept_entry["class"] == "intentional" and kept_entry["note"] == "kept"  # verbatim


def test_apply_report_refuses_to_write_invalid_migrated_review(tmp_path: Path) -> None:
    # plan_review_migration never validates entry CONTENT (only remaps the id), so
    # an entry with an invalid class survives the remap verbatim; apply_report must
    # refuse to persist an invalid dup-review.json rather than writing it silently.
    report = {
        "tool_version": "0.1.0", "algo_version": "2",
        "gate_baseline": {
            "path": "q/dup-ratchet-baseline.json", "_new_members": {"v2a": ["h1"]}, "new_family_count": 1,
        },
        "nose_baseline": {"path": "q/nose-baseline.json", "_new_ids": ["v2a"], "new_family_count": 1},
        "dup_review": {
            "path": "q/dup-review.json", "_note": None,
            "_entries": [{"surface": "code", "id": "v2a", "class": "not-a-real-class", "note": "n", "reviewed_at": "d"}],
        },
    }
    with pytest.raises(RuntimeError, match="failed validation"):
        cli.apply_report(tmp_path, report)
    # Gate/nose baselines are written before the review is validated (no rollback),
    # but the invalid review itself must never land on disk.
    assert not (tmp_path / "q" / "dup-review.json").is_file()


# --------------------------------------------------------------------------- #
# _print_human + main()'s text-mode branch.
# --------------------------------------------------------------------------- #
def test_print_human_full_report(capsys) -> None:
    report = {
        "ok": True, "mode": "dry-run", "tool_version": "0.1.0", "algo_version": "2",
        "collision": {"distinct_v2_fingerprints": 3, "distinct_nose_family_ids": 3, "ok": True},
        "gate_baseline": {
            "path": "q/dup-ratchet-baseline.json", "old_family_count": 2, "survivor_count": 1,
            "vanished": ["old_gone"], "accepted_new": [],
            "requires_review": [{"v2_fingerprint": "v2_new", "files": ["a.py", "b.py"]}],
            "new_family_count": 1,
        },
        "nose_baseline": {
            "path": "q/nose-baseline.json", "old_family_count": 2, "survivor_count": 1,
            "vanished": ["old_gone"], "new_family_count": 1,
        },
        "dup_review": {"path": "q/dup-review.json", "code_entries_before": 5, "dropped_ids": ["orphan1"]},
        "messages": ["some prior message"],
    }
    cli._print_human(report)
    out = capsys.readouterr().out
    assert "some prior message" in out
    assert "mode=dry-run tool_version=0.1.0 algo_version=2" in out
    assert "collision check: distinct v2 fingerprints=3 distinct nose family ids=3 ok=True" in out
    assert (
        "gate baseline q/dup-ratchet-baseline.json: 2 old -> 1 survivor(s), "
        "1 vanished, 0 accepted-new, 1 requires_review -> 1 new total" in out
    )
    assert "requires_review: v2_new (a.py, b.py)" in out
    assert "nose baseline q/nose-baseline.json: 2 old -> 1 survivor(s), 1 vanished -> 1 new total" in out
    assert "dup-review q/dup-review.json: 5 code entries before, 1 dropped as orphaned" in out


def test_main_text_mode_calls_print_human(monkeypatch, capsys, tmp_path: Path) -> None:
    import sys as _sys

    monkeypatch.setattr(
        cli, "run",
        lambda _repo_root, _args: {"ok": False, "status": "no-scope-paths", "messages": ["refusing to scan"]},
    )
    monkeypatch.setattr(_sys, "argv", ["migrate_dup_fingerprints.py", "--repo-root", str(tmp_path)])
    rc = cli.main()
    out = capsys.readouterr().out
    assert rc == 1
    assert "refusing to scan" in out
