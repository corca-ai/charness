"""Item-5 slice 1: reviewed-fixable dup overlay (dup_review_lib + seed_dup_review).

Covers the spec's piece-1 acceptance: artifact shape, seed classification
(portable -> intentional, else unreviewed), family_id keying, existing-entry
preservation, and validation. No gating (slice 2). See
charness-artifacts/spec/boy-scout-dup-ratchet.md.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from .support import ROOT, run_script

SCRIPTS = ROOT / "skills" / "public" / "quality" / "scripts"
SEED_SCRIPT = SCRIPTS / "seed_dup_review.py"


def _load(name: str):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"{name}_inproc", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


lib = _load("dup_review_lib")
seed = _load("seed_dup_review")


def _code_family(family_id: str, files: list[str]) -> dict:
    return {"family_id": family_id, "sample_locations": [{"file": f} for f in files]}


# --------------------------------------------------------------------------- #
# classify
# --------------------------------------------------------------------------- #
def test_classify_all_portable_is_intentional() -> None:
    files = ["skills/public/achieve/scripts/resolve_adapter.py", "skills/public/impl/scripts/resolve_adapter.py"]
    assert lib.classify(files) == "intentional"


def test_classify_mixed_is_unreviewed() -> None:
    files = ["skills/public/achieve/scripts/resolve_adapter.py", "skills/public/quality/scripts/real_logic.py"]
    assert lib.classify(files) == "unreviewed"


def test_classify_empty_is_unreviewed() -> None:
    assert lib.classify([]) == "unreviewed"


def test_classify_never_returns_fixable() -> None:
    # Slice 1 never auto-confirms fixable; the only two outcomes are intentional/unreviewed.
    assert lib.classify(["scripts/anything.py"]) in ("intentional", "unreviewed")
    assert lib.classify(["scripts/anything.py"]) != "fixable"


# --------------------------------------------------------------------------- #
# family_records + build_review
# --------------------------------------------------------------------------- #
def test_family_records_keys_code_by_family_id_and_doc_by_signature() -> None:
    code = [_code_family("aaa", ["x/resolve_adapter.py"])]
    doc = [{"signature": "bbb"}, {"signature": ""}, {"no": "sig"}]
    records = lib.family_records(code, doc)
    assert ("code", "aaa", ["x/resolve_adapter.py"]) in records
    assert ("doc", "bbb", []) in records
    assert len(records) == 2  # empty/absent signatures skipped


def test_build_review_auto_seeds_portable_intentional_only() -> None:
    code = [
        _code_family("portable1", ["a/resolve_adapter.py", "b/resolve_adapter.py"]),
        _code_family("realdup", ["a/logic.py", "b/logic.py"]),
    ]
    review = lib.build_review({}, code, [], reviewed_at="2026-06-19")
    ids = {(e["surface"], e["id"]): e for e in review["entries"]}
    assert ids[("code", "portable1")]["class"] == "intentional"
    assert ("code", "realdup") not in ids  # unreviewed is implicit, not stored
    assert review["fixable_ceiling"] == 0
    assert review["schemaVersion"] == lib.SCHEMA_VERSION


def test_build_review_preserves_existing_classifications() -> None:
    existing = {
        "schemaVersion": lib.SCHEMA_VERSION,
        "fixable_ceiling": 1,
        "entries": [
            {"id": "realdup", "surface": "code", "class": "fixable", "note": "operator", "reviewed_at": "2026-06-10"},
        ],
    }
    # The same family reappears in the inventory; the operator's 'fixable' must win
    # over any auto-seed, and the existing entry must survive.
    code = [_code_family("realdup", ["a/resolve_adapter.py", "b/resolve_adapter.py"])]
    review = lib.build_review(existing, code, [], reviewed_at="2026-06-19")
    entry = next(e for e in review["entries"] if e["id"] == "realdup")
    assert entry["class"] == "fixable"
    assert entry["reviewed_at"] == "2026-06-10"
    assert review["fixable_ceiling"] == 1


# --------------------------------------------------------------------------- #
# validate_review
# --------------------------------------------------------------------------- #
def test_validate_review_accepts_well_formed() -> None:
    review = lib.build_review({}, [_code_family("p", ["a/init_adapter.py"])], [], reviewed_at="2026-06-19")
    assert lib.validate_review(review) == []


def test_validate_review_flags_bad_schema_surface_class_and_ceiling() -> None:
    bad = {
        "schemaVersion": "wrong",
        "fixable_ceiling": 5,
        "entries": [
            {"id": "x", "surface": "bogus", "class": "nope", "note": "n", "reviewed_at": "d"},
            {"id": "x", "surface": "bogus", "class": "nope", "note": "n", "reviewed_at": "d"},
        ],
    }
    errors = lib.validate_review(bad)
    joined = " ".join(errors)
    assert "schemaVersion" in joined
    assert "surface" in joined
    assert "class" in joined
    assert "duplicate" in joined
    assert "fixable_ceiling" in joined


def test_validate_review_rejects_non_object() -> None:
    assert lib.validate_review([1, 2, 3]) == ["review must be a JSON object"]


# --------------------------------------------------------------------------- #
# CLI: build_result (in-process) + the bootstrap shim guard
# --------------------------------------------------------------------------- #
def _write_inventory(path: Path, families: list[dict]) -> Path:
    path.write_text(json.dumps({"status": "findings", "families": families}), encoding="utf-8")
    return path


def test_build_result_consumes_injected_inventories(tmp_path: Path) -> None:
    code_json = _write_inventory(tmp_path / "code.json", [_code_family("fid1", ["a/resolve_adapter.py", "b/resolve_adapter.py"])])
    doc_json = _write_inventory(tmp_path / "doc.json", [{"signature": "docsig"}])
    args = SimpleNamespace(
        repo_root=tmp_path, output="charness-artifacts/quality/dup-review.json",
        code_inventory=code_json, doc_inventory=doc_json, reviewed_at="2026-06-19",
    )
    result = seed.build_result(args)
    assert result["code_family_count"] == 1
    assert result["doc_family_count"] == 1
    entry = next(e for e in result["review"]["entries"] if e["id"] == "fid1")
    assert entry["class"] == "intentional"  # family_id flows through to the overlay


def test_seed_bootstrap_import_error_guard(tmp_path: Path, monkeypatch) -> None:
    isolated = tmp_path / "deep" / "nest" / "x.py"
    isolated.parent.mkdir(parents=True)
    monkeypatch.setattr(seed, "__file__", str(isolated))
    with pytest.raises(ImportError):
        seed._load_skill_runtime_bootstrap()


# --------------------------------------------------------------------------- #
# CLI: real entrypoint (write + dry-run) via subprocess
# --------------------------------------------------------------------------- #
def test_seed_cli_writes_overlay(tmp_path: Path) -> None:
    code_json = _write_inventory(tmp_path / "code.json", [_code_family("fid1", ["a/init_adapter.py", "b/init_adapter.py"])])
    doc_json = _write_inventory(tmp_path / "doc.json", [])
    result = run_script(
        str(SEED_SCRIPT), "--repo-root", str(tmp_path),
        "--code-inventory", str(code_json), "--doc-inventory", str(doc_json),
        "--reviewed-at", "2026-06-19", "--write", "--json", cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr
    overlay = json.loads((tmp_path / "charness-artifacts" / "quality" / "dup-review.json").read_text(encoding="utf-8"))
    assert overlay["schemaVersion"] == lib.SCHEMA_VERSION
    assert lib.validate_review(overlay) == []
    assert any(e["id"] == "fid1" and e["class"] == "intentional" for e in overlay["entries"])


def test_seed_cli_dry_run_does_not_write(tmp_path: Path) -> None:
    code_json = _write_inventory(tmp_path / "code.json", [])
    result = run_script(
        str(SEED_SCRIPT), "--repo-root", str(tmp_path),
        "--code-inventory", str(code_json), "--reviewed-at", "2026-06-19", cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr
    assert "previewed" in result.stdout
    assert not (tmp_path / "charness-artifacts" / "quality" / "dup-review.json").exists()


# --------------------------------------------------------------------------- #
# Remaining validate_review branches (every line of a new file is a changed line).
# --------------------------------------------------------------------------- #
def test_validate_review_flags_non_dict_entry() -> None:
    bad = {"schemaVersion": lib.SCHEMA_VERSION, "fixable_ceiling": 0, "entries": [42]}
    assert any("must be an object" in e for e in lib.validate_review(bad))


def test_validate_review_flags_non_string_note_and_reviewed_at() -> None:
    bad = {
        "schemaVersion": lib.SCHEMA_VERSION,
        "fixable_ceiling": 0,
        "entries": [{"id": "x", "surface": "code", "class": "intentional", "note": 5, "reviewed_at": 9}],
    }
    errors = " ".join(lib.validate_review(bad))
    assert "note" in errors and "reviewed_at" in errors


def test_validate_review_flags_empty_id() -> None:
    bad = {
        "schemaVersion": lib.SCHEMA_VERSION,
        "fixable_ceiling": 0,
        "entries": [{"id": "", "surface": "code", "class": "intentional", "note": "n", "reviewed_at": "d"}],
    }
    assert any("id must be a non-empty string" in e for e in lib.validate_review(bad))


def test_validate_review_flags_entries_not_list() -> None:
    bad = {"schemaVersion": lib.SCHEMA_VERSION, "fixable_ceiling": 0, "entries": "nope"}
    assert "entries must be a list" in lib.validate_review(bad)


# --------------------------------------------------------------------------- #
# seed CLI helpers + main() in-process (independent of subprocess coverage capture).
# --------------------------------------------------------------------------- #
def test_families_from_payload_handles_invalid_and_valid() -> None:
    assert seed._families_from_payload("not json") == []
    assert seed._families_from_payload("") == []
    assert seed._families_from_payload(json.dumps({"families": [{"family_id": "x"}]})) == [{"family_id": "x"}]
    assert seed._families_from_payload(json.dumps({"families": "bad"})) == []


def test_run_inventory_parses_subprocess(monkeypatch, tmp_path: Path) -> None:
    import subprocess

    families = [{"family_id": "z", "sample_locations": []}]
    monkeypatch.setattr(
        seed.subprocess, "run",
        lambda *a, **k: subprocess.CompletedProcess(a[0], 0, json.dumps({"families": families}), ""),
    )
    assert seed._run_inventory(tmp_path / "x.py", tmp_path) == families


def test_load_existing_reads_valid_and_tolerates_invalid(tmp_path: Path) -> None:
    assert seed._load_existing(tmp_path / "absent.json") == {}
    path = tmp_path / "ex.json"
    path.write_text(json.dumps({"entries": []}), encoding="utf-8")
    assert seed._load_existing(path) == {"entries": []}
    path.write_text("not json", encoding="utf-8")
    assert seed._load_existing(path) == {}


def test_main_inprocess_write_json(tmp_path: Path, monkeypatch, capsys) -> None:
    code_json = _write_inventory(tmp_path / "code.json", [_code_family("mid", ["a/resolve_adapter.py", "b/resolve_adapter.py"])])
    monkeypatch.setattr(
        sys, "argv",
        ["seed", "--repo-root", str(tmp_path), "--code-inventory", str(code_json),
         "--reviewed-at", "2026-06-19", "--write", "--json"],
    )
    assert seed.main() == 0
    out = json.loads(capsys.readouterr().out)
    assert out["code_family_count"] == 1
    assert (tmp_path / "charness-artifacts" / "quality" / "dup-review.json").is_file()


def test_main_inprocess_dry_run_human(tmp_path: Path, monkeypatch, capsys) -> None:
    code_json = _write_inventory(tmp_path / "code.json", [])
    monkeypatch.setattr(
        sys, "argv",
        ["seed", "--repo-root", str(tmp_path), "--code-inventory", str(code_json), "--reviewed-at", "2026-06-19"],
    )
    assert seed.main() == 0
    assert "previewed" in capsys.readouterr().out


def test_main_inprocess_invalid_overlay_exits_one(tmp_path: Path, monkeypatch, capsys) -> None:
    code_json = _write_inventory(tmp_path / "code.json", [])
    monkeypatch.setattr(seed.dup_review, "validate_review", lambda _review: ["forced error"])
    monkeypatch.setattr(
        sys, "argv",
        ["seed", "--repo-root", str(tmp_path), "--code-inventory", str(code_json), "--reviewed-at", "2026-06-19"],
    )
    assert seed.main() == 1
    assert "invalid overlay" in capsys.readouterr().err
