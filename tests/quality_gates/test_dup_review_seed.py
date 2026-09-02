"""Item-5 slice 1: reviewed-fixable dup overlay (dup_review_lib + seed_dup_review).

Covers the spec's piece-1 acceptance: artifact shape, seed classification
(portable -> intentional, else unreviewed), family_id keying, existing-entry
preservation, and validation. No gating (slice 2). See
charness-artifacts/spec/boy-scout-dup-ratchet.md.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from .seeding_support import load_module
from .support import ROOT, run_script

SCRIPTS = ROOT / "skills" / "public" / "quality" / "scripts"
SEED_SCRIPT = SCRIPTS / "seed_dup_review.py"


def _load(name: str):
    return load_module(f"{name}_inproc", SCRIPTS / f"{name}.py")


lib = _load("dup_review_lib")
seed = _load("seed_dup_review")


def _code_family(identity: str, files: list[str]) -> dict:
    # Slice 4: the seed keys code identity on the stamped `family_fingerprint` (was family_id).
    return {"family_fingerprint": identity, "sample_locations": [{"file": f} for f in files]}


# --------------------------------------------------------------------------- #
# classify
# --------------------------------------------------------------------------- #
def test_classify_all_portable_is_intentional() -> None:
    files = [
        "skills/public/achieve/scripts/resolve_adapter.py",
        "skills/public/impl/scripts/resolve_adapter.py",
    ]
    assert lib.classify(files) == "intentional"


def test_classify_mixed_is_unreviewed() -> None:
    files = [
        "skills/public/achieve/scripts/resolve_adapter.py",
        "skills/public/quality/scripts/real_logic.py",
    ]
    assert lib.classify(files) == "unreviewed"


def test_classify_empty_is_unreviewed() -> None:
    assert lib.classify([]) == "unreviewed"


# --------------------------------------------------------------------------- #
# family_records + build_review
# --------------------------------------------------------------------------- #
def test_family_records_keys_code_by_fingerprint_and_doc_by_signature() -> None:
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
            {
                "id": "realdup",
                "surface": "code",
                "class": "fixable",
                "note": "operator",
                "reviewed_at": "2026-06-10",
            },
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
    review = lib.build_review(
        {}, [_code_family("p", ["a/init_adapter.py"])], [], reviewed_at="2026-06-19"
    )
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


def _recorded_inventory(monkeypatch, *, returncode: int, stdout: str, stderr: str = "") -> None:
    def main():
        print(stdout, end="")
        if stderr:
            print(stderr, end="", file=sys.stderr)
        return returncode

    monkeypatch.setattr(
        seed._SKILL_RUNTIME,
        "load_local_skill_module",
        lambda *_args: SimpleNamespace(main=main),
    )


def test_build_result_consumes_injected_inventories(tmp_path: Path) -> None:
    code_json = _write_inventory(
        tmp_path / "code.json",
        [_code_family("fid1", ["a/resolve_adapter.py", "b/resolve_adapter.py"])],
    )
    doc_json = _write_inventory(tmp_path / "doc.json", [{"signature": "docsig"}])
    args = SimpleNamespace(
        repo_root=tmp_path,
        output="charness-artifacts/quality/dup-review.json",
        code_inventory=code_json,
        doc_inventory=doc_json,
        reviewed_at="2026-06-19",
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
    code_json = _write_inventory(
        tmp_path / "code.json", [_code_family("fid1", ["a/init_adapter.py", "b/init_adapter.py"])]
    )
    doc_json = _write_inventory(tmp_path / "doc.json", [])
    result = run_script(
        str(SEED_SCRIPT),
        "--repo-root",
        str(tmp_path),
        "--code-inventory",
        str(code_json),
        "--doc-inventory",
        str(doc_json),
        "--reviewed-at",
        "2026-06-19",
        "--write",
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr
    overlay = json.loads(
        (tmp_path / "charness-artifacts" / "quality" / "dup-review.json").read_text(
            encoding="utf-8"
        )
    )
    assert overlay["schemaVersion"] == lib.SCHEMA_VERSION
    assert lib.validate_review(overlay) == []
    assert any(e["id"] == "fid1" and e["class"] == "intentional" for e in overlay["entries"])


def test_seed_cli_dry_run_does_not_write(tmp_path: Path) -> None:
    code_json = _write_inventory(tmp_path / "code.json", [])
    doc_json = _write_inventory(tmp_path / "doc.json", [])
    result = run_script(
        str(SEED_SCRIPT),
        "--repo-root",
        str(tmp_path),
        "--code-inventory",
        str(code_json),
        "--doc-inventory",
        str(doc_json),
        "--reviewed-at",
        "2026-06-19",
        cwd=ROOT,
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
        "entries": [
            {"id": "x", "surface": "code", "class": "intentional", "note": 5, "reviewed_at": 9}
        ],
    }
    errors = " ".join(lib.validate_review(bad))
    assert "note" in errors and "reviewed_at" in errors


def test_validate_review_flags_empty_id() -> None:
    bad = {
        "schemaVersion": lib.SCHEMA_VERSION,
        "fixable_ceiling": 0,
        "entries": [
            {"id": "", "surface": "code", "class": "intentional", "note": "n", "reviewed_at": "d"}
        ],
    }
    assert any("id must be a non-empty string" in e for e in lib.validate_review(bad))


def test_validate_review_flags_entries_not_list() -> None:
    bad = {"schemaVersion": lib.SCHEMA_VERSION, "fixable_ceiling": 0, "entries": "nope"}
    assert "entries must be a list" in lib.validate_review(bad)


# --------------------------------------------------------------------------- #
# seed CLI helpers + main() in-process (independent of subprocess coverage capture).
# --------------------------------------------------------------------------- #
def test_families_from_payload_separates_declared_empty_from_unestablished() -> None:
    # `[]` with no reason means the payload DECLARED zero families. Every other shape now
    # carries a reason, because reading them as zero seeded a confident overlay over a
    # corpus that was never scanned (the twin of dup_ratchet_scan's sweep S29 fix).
    assert seed._families_from_payload(json.dumps({"families": []}), "src") == ([], None)
    assert seed._families_from_payload(json.dumps({"families": [{"family_id": "x"}]}), "src") == (
        [{"family_id": "x"}],
        None,
    )
    for text, fragment in (
        ("[not: yaml", "did not emit YAML"),
        ("", "produced no output"),
        ("   \n", "produced no output"),
        (json.dumps({"families": "bad"}), "declares no families list"),
        (json.dumps([1, 2]), "not a report object"),
        (json.dumps({"status": "missing", "families": []}), "degraded (status=missing)"),
        (json.dumps({"status": "error", "families": []}), "degraded (status=error)"),
    ):
        families, reason = seed._families_from_payload(text, "src")
        assert families == [] and reason is not None and fragment in reason, text


def test_run_inventory_parses_subprocess(monkeypatch, tmp_path: Path) -> None:
    families = [{"family_id": "z", "sample_locations": []}]
    _recorded_inventory(monkeypatch, returncode=0, stdout=json.dumps({"families": families}))
    assert seed._run_inventory(tmp_path / "x.py", tmp_path) == (families, None)


def test_run_inventory_refuses_a_nonzero_exit(monkeypatch, tmp_path: Path) -> None:
    # The producer's return code was read by nothing. DEFENSIVE, not reproduced: neither
    # inventory exits nonzero today (`inventory_nose_clones.main` always returns 0;
    # `inventory_doc_duplicates` exits 1 only under `--require-nose`, which this caller does
    # not pass), and the reachable crash prints nothing, which the blank-output row covers.
    # The check exists so a future nonzero exit cannot seed as if it had scanned.
    _recorded_inventory(
        monkeypatch,
        returncode=3,
        stdout=json.dumps({"families": []}),
        stderr="traceback",
    )
    families, reason = seed._run_inventory(tmp_path / "x.py", tmp_path)
    assert families == [] and reason is not None and "exited 3" in reason


def test_load_existing_reads_valid_and_refuses_corrupt(tmp_path: Path) -> None:
    assert seed._load_existing(tmp_path / "absent.json") == ({}, None)
    path = tmp_path / "ex.json"
    path.write_text(json.dumps({"entries": []}), encoding="utf-8")
    assert seed._load_existing(path) == ({"entries": []}, None)
    # A corrupt overlay read as "no prior review", so --write rebuilt it from scratch and
    # dropped every operator classification while reporting success.
    path.write_text("not json", encoding="utf-8")
    existing, reason = seed._load_existing(path)
    assert existing == {} and reason is not None and "present but unreadable" in reason


def test_main_refuses_to_reseed_over_a_corrupt_overlay(tmp_path: Path, monkeypatch, capsys) -> None:
    code_json = _write_inventory(
        tmp_path / "code.json", [_code_family("mid", ["a/x.py", "b/x.py"])]
    )
    doc_json = _write_inventory(tmp_path / "doc.json", [])
    overlay = tmp_path / "dup-review.json"
    overlay.write_text('{"entries": [{"surface": "code",', encoding="utf-8")  # truncated mid-write
    monkeypatch.setattr(
        seed.sys,
        "argv",
        [
            "seed_dup_review.py",
            "--repo-root",
            str(tmp_path),
            "--output",
            "dup-review.json",
            "--code-inventory",
            str(code_json),
            "--doc-inventory",
            str(doc_json),
            "--write",
        ],
    )
    assert seed.main() == 1
    assert "refused" in capsys.readouterr().err
    assert overlay.read_text(encoding="utf-8") == '{"entries": [{"surface": "code",'  # untouched


def test_main_inprocess_write(tmp_path: Path, monkeypatch, capsys) -> None:
    code_json = _write_inventory(
        tmp_path / "code.json",
        [_code_family("mid", ["a/resolve_adapter.py", "b/resolve_adapter.py"])],
    )
    doc_json = _write_inventory(tmp_path / "doc.json", [])
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "seed",
            "--repo-root",
            str(tmp_path),
            "--code-inventory",
            str(code_json),
            "--doc-inventory",
            str(doc_json),
            "--reviewed-at",
            "2026-06-19",
            "--write",
        ],
    )
    assert seed.main() == 0
    assert "1 code" in capsys.readouterr().out
    assert (tmp_path / "charness-artifacts" / "quality" / "dup-review.json").is_file()


def test_main_inprocess_dry_run_human(tmp_path: Path, monkeypatch, capsys) -> None:
    code_json = _write_inventory(tmp_path / "code.json", [])
    doc_json = _write_inventory(tmp_path / "doc.json", [])
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "seed",
            "--repo-root",
            str(tmp_path),
            "--code-inventory",
            str(code_json),
            "--doc-inventory",
            str(doc_json),
            "--reviewed-at",
            "2026-06-19",
        ],
    )
    assert seed.main() == 0
    assert "previewed" in capsys.readouterr().out


def test_main_inprocess_invalid_overlay_exits_one(tmp_path: Path, monkeypatch, capsys) -> None:
    code_json = _write_inventory(tmp_path / "code.json", [])
    doc_json = _write_inventory(tmp_path / "doc.json", [])
    monkeypatch.setattr(seed.dup_review, "validate_review", lambda _review: ["forced error"])
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "seed",
            "--repo-root",
            str(tmp_path),
            "--code-inventory",
            str(code_json),
            "--doc-inventory",
            str(doc_json),
            "--reviewed-at",
            "2026-06-19",
        ],
    )
    assert seed.main() == 1
    assert "invalid overlay" in capsys.readouterr().err


def test_families_reports_an_unreadable_injected_inventory_as_a_reason(tmp_path: Path) -> None:
    # An injected `--code-inventory` that cannot be READ is not an empty family set.
    # Returning `[]` with no reason here is the same unestablished-scope read the
    # subsystem's one rule refuses: `[]` may only mean the producer DECLARED zero.
    unreadable = tmp_path / "inventory-dir.json"
    unreadable.mkdir()

    families, reason = seed._families(unreadable, tmp_path / "absent.py", tmp_path)

    assert families == []
    assert reason is not None and "cannot read" in reason and str(unreadable) in reason


def test_load_existing_refuses_a_parseable_overlay_that_lost_its_entries_list(
    tmp_path: Path,
) -> None:
    # Unparseable is not the only unreadable: a payload that PARSES but is a list, a
    # scalar, or a dict whose `entries` key was renamed yields zero prior entries
    # through a successful parse — the same silent wipe, one branch over.
    path = tmp_path / "ex.json"
    for payload in ('["entries"]', '"entries"', '{"reviewed": []}'):
        path.write_text(payload, encoding="utf-8")

        existing, reason = seed._load_existing(path)

        assert existing == {}, payload
        assert reason is not None and "no `entries` list" in reason, payload
        assert "refusing to reseed" in reason, payload


def test_main_refusal_names_the_unreadable_input(tmp_path: Path, monkeypatch, capsys) -> None:
    unreadable = tmp_path / "code-dir.json"
    unreadable.mkdir()
    # The DOC arm is injected as a declared-empty inventory even though this test is
    # about the CODE arm. Left uninjected it runs the real producer, which shells out
    # to `nose`; wherever that binary is absent the doc arm contributes its OWN
    # unestablished reason and three of the four assertions below pass whether or not
    # the code-arm branch works at all. A test that refuses for a reason it did not
    # name is the same class this suite exists to refuse.
    doc_json = _write_inventory(tmp_path / "doc.json", [])
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "seed",
            "--repo-root",
            str(tmp_path),
            "--code-inventory",
            str(unreadable),
            "--doc-inventory",
            str(doc_json),
            "--reviewed-at",
            "2026-06-19",
        ],
    )

    assert seed.main() == 1

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "cannot read" in captured.err
    assert str(unreadable) in captured.err
    assert "refused" in captured.err


def test_main_help_documents_repo_root(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", ["seed", "--help"])
    with pytest.raises(SystemExit) as exc_info:
        seed.main()
    assert exc_info.value.code == 0
    output = capsys.readouterr().out
    expected = {
        "--repo-root": "Repository root whose duplicate inventories and overlay should be managed"
    }
    for option, fragment in expected.items():
        match = re.search(rf"^  {re.escape(option)}\b.*$", output, re.MULTILINE)
        assert match, f"missing help option: {option}"
        next_option = re.search(r"^  --[a-z][a-z-]*\b", output[match.end() :], re.MULTILINE)
        end = match.end() + next_option.start() if next_option else len(output)
        option_block = re.sub(r"\s+", " ", output[match.start() : end])
        assert fragment in option_block, f"missing help for {option}: {fragment}"
