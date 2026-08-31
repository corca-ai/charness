from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest
import yaml

from tests.dsl import Repo
from tests.quality_gates.support import run_script

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INVENTORY = _load("inventory_boundary_bypass_lib", ROOT / "scripts" / "inventory_boundary_bypass_lib.py")
RATCHET = _load("boundary_bypass_ratchet_lib", ROOT / "scripts" / "boundary_bypass_ratchet_lib.py")
CHECK_RATCHET = ROOT / "scripts" / "check_boundary_bypass_ratchet.py"

IMPORT_SAFE = "\n".join(
    [
        "def main() -> int:",
        "    return 0",
        "",
        "if __name__ == '__main__':",
        "    raise SystemExit(main())",
        "",
    ]
)


def _repo_with_candidate(tmp_path: Path) -> Path:
    return (
        Repo()
        .file("scripts/foo.py", IMPORT_SAFE)
        .file(
            "tests/test_foo.py",
            "\n".join(
                [
                    "from support import run_script",
                    "def test_x():",
                    "    result = run_script('scripts/foo.py')",
                    "    assert result.returncode == 0",
                    "    import json; assert json.loads(result.stdout)",
                    "",
                ]
            ),
        )
        .build(tmp_path)
    )


def _run_ratchet(*args: str) -> subprocess.CompletedProcess[str]:
    return run_script(str(CHECK_RATCHET), *args, cwd=ROOT)


def test_matching_baseline_passes(tmp_path: Path) -> None:
    payload = INVENTORY.find_boundary_bypass_candidates(_repo_with_candidate(tmp_path))
    baseline = RATCHET.build_baseline(payload)
    report = RATCHET.check_payload(payload, baseline, {})
    assert report["ok"] is True
    assert report["summary"]["candidate_count"] == 1
    assert report["summary"]["candidate_key_count"] == 1


def test_real_inventory_path_move_keeps_a_baselined_identity(tmp_path: Path) -> None:
    original = _repo_with_candidate(tmp_path / "original")
    moved = (
        Repo()
        .file("scripts/foo.py", IMPORT_SAFE)
        .file(
            "tests/renamed/test_foo.py",
            "\n".join(
                [
                    "from support import run_script",
                    "def test_x():",
                    "    result = run_script('scripts/foo.py')",
                    "    assert result.returncode == 0",
                    "    import json; assert json.loads(result.stdout)",
                    "",
                ]
            ),
        )
        .build(tmp_path / "moved")
    )
    baseline = RATCHET.build_baseline(INVENTORY.find_boundary_bypass_candidates(original))

    assert RATCHET.check_payload(INVENTORY.find_boundary_bypass_candidates(moved), baseline, {})["ok"] is True


def test_content_identity_is_path_invariant_and_preserves_membership_and_multiplicity() -> None:
    """The R6 contract: path moves do not mint a key; call-site changes do."""
    def payload(test_file: str, members: list[str]) -> dict:
        return {
            "schemaVersion": "charness.quality.boundary_bypass_inventory.v2",
            "call_site_fingerprint_algo_version": "1",
            "candidates": [{
                "test_file": test_file,
                "import_safe_targets": ["scripts/foo.py"],
                "clean_inprocess_targets": ["scripts/foo.py"],
                "internal_boundary_targets": [],
                "behavior_assert": True,
                "likely_keep_boundary": False,
                "call_site_member_hashes": members,
            }],
        }

    baseline_payload = payload("tests/old_location.py", ["call-A"])
    baseline = RATCHET.build_baseline(baseline_payload)
    assert RATCHET.check_payload(payload("tests/moved_location.py", ["call-A"]), baseline, {})["ok"] is True
    assert RATCHET.check_payload(payload("tests/moved_location.py", ["call-B"]), baseline, {})["new_candidate_keys"]
    assert RATCHET.check_payload(payload("tests/moved_location.py", ["call-A", "call-B"]), baseline, {})["new_candidate_keys"]
    assert RATCHET.check_payload(payload("tests/moved_location.py", ["call-A", "call-A"]), baseline, {})["new_candidate_keys"]


def test_new_unexempt_candidate_fails_no_increase(tmp_path: Path) -> None:
    payload = INVENTORY.find_boundary_bypass_candidates(_repo_with_candidate(tmp_path))
    baseline = RATCHET.build_baseline({
        "schemaVersion": payload["schemaVersion"],
        "call_site_fingerprint_algo_version": payload["call_site_fingerprint_algo_version"],
        "candidates": [],
    })
    report = RATCHET.check_payload(payload, baseline, {})
    assert report["ok"] is False
    assert report["new_candidate_keys"] == RATCHET.candidate_keys(payload)
    assert report["count_increases"]["candidate_count"] == {"baseline": 0, "current": 1}


def test_inventory_schema_mismatch_fails(tmp_path: Path) -> None:
    payload = INVENTORY.find_boundary_bypass_candidates(_repo_with_candidate(tmp_path))
    baseline = RATCHET.build_baseline(payload)
    payload["schemaVersion"] = "different.schema.v2"
    report = RATCHET.check_payload(payload, baseline, {})
    assert report["ok"] is False
    assert report["schema_mismatch"] == {
        "baseline": "charness.quality.boundary_bypass_inventory.v2",
        "current": "different.schema.v2",
    }


def test_algorithm_version_mismatch_fails_and_persisted_baseline_is_refused(tmp_path: Path) -> None:
    payload = INVENTORY.find_boundary_bypass_candidates(_repo_with_candidate(tmp_path))
    baseline = RATCHET.build_baseline(payload)
    baseline["call_site_fingerprint_algo_version"] = "2"

    report = RATCHET.check_payload(payload, baseline, {})
    assert report["ok"] is False
    assert report["algorithm_mismatch"] is True

    path = tmp_path / "baseline.json"
    path.write_text(json.dumps(baseline), encoding="utf-8")
    with pytest.raises(RATCHET.RatchetError, match="call_site_fingerprint_algo_version"):
        RATCHET.load_baseline(path)


def _written_baseline(tmp_path: Path, mutate) -> Path:
    payload = INVENTORY.find_boundary_bypass_candidates(_repo_with_candidate(tmp_path))
    baseline = RATCHET.build_baseline(payload)
    mutate(baseline)
    path = tmp_path / "baseline.json"
    path.write_text(json.dumps(baseline), encoding="utf-8")
    return path


@pytest.mark.parametrize("drift", [1, -1])
def test_a_baseline_whose_key_count_disagrees_with_its_key_list_is_refused(tmp_path: Path, drift: int) -> None:
    """`candidate_keys` carries the whole verdict once `candidate_key_count` leaves COUNT_FIELDS.

    BOTH directions, because they fail differently and only one of them is the shape this file
    has actually been in. Stale-HIGH is the observed one: at commit `7a43c8a4` the repo's
    baseline recorded 151 against 150 keys. Stale-LOW is the one that would matter if the field
    were still enforced. Neither is tolerable now, because a count that disagrees with its own
    list is evidence the file was hand-edited rather than regenerated, and it is the LIST that
    `new_candidate_keys` diffs against.
    """
    path = _written_baseline(
        tmp_path,
        lambda b: b["summary"].__setitem__("candidate_key_count", len(b["candidate_keys"]) + drift),
    )
    with pytest.raises(RATCHET.RatchetError, match="disagrees with"):
        RATCHET.load_baseline(path)


@pytest.mark.parametrize("bad", [None, "59", 59.0, True, [59]])
def test_a_baseline_without_a_usable_key_count_is_refused(tmp_path: Path, bad: object) -> None:
    """Absence is refused too, and that is the point.

    The threat model for this check is a hand-edit. Deleting the `candidate_key_count` line is at
    least as easy as mis-editing it, so tolerating a missing field would let the edit the check
    exists to catch turn the check off. `build_baseline` always writes it, so nothing legitimate
    omits it. The non-int cases are here because `int(...)` on a hand-typo would have escaped as a
    bare ValueError past `check_boundary_bypass_ratchet.py`'s `except RatchetError`, replacing the
    gate's JSON refusal contract with a traceback.
    """
    def mutate(baseline: dict) -> None:
        if bad is None:
            del baseline["summary"]["candidate_key_count"]
        else:
            baseline["summary"]["candidate_key_count"] = bad

    with pytest.raises(RATCHET.RatchetError, match="must be an integer"):
        RATCHET.load_baseline(_written_baseline(tmp_path, mutate))


def test_a_consistent_baseline_still_loads(tmp_path: Path) -> None:
    path = _written_baseline(tmp_path, lambda baseline: None)
    baseline = RATCHET.load_baseline(path)
    assert baseline["summary"]["candidate_key_count"] == len(baseline["candidate_keys"])


@pytest.mark.parametrize("field", RATCHET.COUNT_FIELDS)
def test_writer_integrity_refuses_every_hand_edited_enforced_count(tmp_path: Path, field: str) -> None:
    path = _written_baseline(
        tmp_path,
        lambda baseline: baseline["summary"].__setitem__(field, baseline["summary"][field] + 1),
    )

    with pytest.raises(RATCHET.RatchetError, match="writer_integrity_sha256"):
        RATCHET.load_baseline(path)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda baseline: baseline["candidate_keys"].__setitem__(0, "0" * 16),
        lambda baseline: baseline.__setitem__("inventory_schemaVersion", "different.inventory.v2"),
    ],
)
def test_writer_integrity_refuses_other_persisted_verdict_inputs(tmp_path: Path, mutate) -> None:
    with pytest.raises(RATCHET.RatchetError, match="writer_integrity_sha256"):
        RATCHET.load_baseline(_written_baseline(tmp_path, mutate))


def test_writer_requires_confirmation_before_replacing_an_existing_baseline(tmp_path: Path) -> None:
    repo = _repo_with_candidate(tmp_path / "repo")
    baseline_path = tmp_path / "baseline.json"
    common_args = ("--repo-root", str(repo), "--baseline", str(baseline_path), "--write-baseline")

    created = _run_ratchet(*common_args)
    assert created.returncode == 0
    assert yaml.safe_load(created.stdout)["status"] == "baseline-written"

    baseline_path.write_text("{}\n", encoding="utf-8")
    refused = _run_ratchet(*common_args)
    assert refused.returncode == 1
    refusal = yaml.safe_load(refused.stdout)
    assert "--confirm-baseline-delta" in refusal["error"]
    expected_payload = INVENTORY.find_boundary_bypass_candidates(repo)
    assert refusal["baseline_delta"] == {
        "previous_metadata": {
            "schemaVersion": None,
            "policy": None,
            "inventory_schemaVersion": None,
            "call_site_fingerprint_algo_version": None,
        },
        "proposed_metadata": {
            "schemaVersion": RATCHET.RATCHET_SCHEMA_VERSION,
            "policy": "no_increase",
            "inventory_schemaVersion": expected_payload["schemaVersion"],
            "call_site_fingerprint_algo_version": expected_payload["call_site_fingerprint_algo_version"],
        },
        "previous_summary": None,
        "proposed_summary": RATCHET.build_baseline(expected_payload)["summary"],
        "added_candidate_keys": RATCHET.candidate_keys(expected_payload),
        "removed_candidate_keys": [],
    }
    assert json.loads(baseline_path.read_text(encoding="utf-8")) == {}

    replaced = _run_ratchet(*common_args, "--confirm-baseline-delta")
    assert replaced.returncode == 0
    assert yaml.safe_load(replaced.stdout)["changed"] is True
    assert RATCHET.load_baseline(baseline_path)[RATCHET.INTEGRITY_FIELD]


def test_cli_evaluates_a_matching_existing_baseline(tmp_path: Path) -> None:
    repo = _repo_with_candidate(tmp_path / "repo")
    baseline_path = tmp_path / "baseline.json"
    baseline_path.write_text(json.dumps(RATCHET.build_baseline(INVENTORY.find_boundary_bypass_candidates(repo))), encoding="utf-8")

    result = _run_ratchet("--repo-root", str(repo), "--baseline", str(baseline_path))

    assert result.returncode == 0
    assert yaml.safe_load(result.stdout)["ok"] is True


def test_writer_refuses_malformed_existing_baseline_without_a_traceback(tmp_path: Path) -> None:
    repo = _repo_with_candidate(tmp_path / "repo")
    baseline_path = tmp_path / "baseline.json"
    baseline_path.write_text("{not-json", encoding="utf-8")

    result = _run_ratchet(
        "--repo-root", str(repo), "--baseline", str(baseline_path), "--write-baseline"
    )

    assert result.returncode == 1
    assert "invalid JSON" in yaml.safe_load(result.stdout)["error"]
    assert "Traceback" not in result.stderr


def test_writer_refuses_an_existing_directory_baseline_without_a_traceback(tmp_path: Path) -> None:
    repo = _repo_with_candidate(tmp_path / "repo")
    baseline_path = tmp_path / "baseline-directory"
    baseline_path.mkdir()

    result = _run_ratchet(
        "--repo-root", str(repo), "--baseline", str(baseline_path), "--write-baseline"
    )

    assert result.returncode == 1
    assert "baseline path must be a regular file" in yaml.safe_load(result.stdout)["error"]
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("contents", ["[]", "null", '"not an object"'])
def test_evaluation_refuses_non_object_baseline_without_a_traceback(tmp_path: Path, contents: str) -> None:
    repo = _repo_with_candidate(tmp_path / "repo")
    baseline_path = tmp_path / "baseline.json"
    baseline_path.write_text(contents, encoding="utf-8")

    result = _run_ratchet("--repo-root", str(repo), "--baseline", str(baseline_path))

    assert result.returncode == 1
    assert "baseline must be a JSON object" in yaml.safe_load(result.stdout)["error"]
    assert "Traceback" not in result.stderr


def test_baseline_requires_advisory_candidate_pairs(tmp_path: Path) -> None:
    path = _written_baseline(tmp_path, lambda baseline: baseline.pop("candidate_pairs"))

    with pytest.raises(RATCHET.RatchetError, match="candidate_pairs"):
        RATCHET.load_baseline(path)


@pytest.mark.parametrize("bad_test_file", ["", None, 0, ["tests/test_foo.py"]])
def test_a_row_without_a_usable_test_file_is_refused_rather_than_skipped(bad_test_file: object) -> None:
    """Refusing, not skipping, because skipping can only MASK the enforced arms.

    `check_payload` fires on `current > baseline`, so anything that drops rows can only lower
    `current` -- it can never trip the ratchet, only hide a row from `candidate_count` and its
    three row-shaped siblings. The old `candidate_keys` skipped these rows and the old
    `filtered_summary` did not; unifying the two walks had to pick one, and skipping was the
    direction that loses a verdict. The published payload contract already rejects the shape
    (`validate_boundary_bypass_payload.py:48-49`), so refusing here agrees with it.
    """
    payload = {
        "schemaVersion": "charness.quality.boundary_bypass_inventory.v2",
        "candidates": [{"test_file": bad_test_file, "import_safe_targets": ["scripts/foo.py"]}],
    }
    with pytest.raises(RATCHET.RatchetError, match="must be a non-empty string"):
        RATCHET.filtered_summary(payload, {})
    with pytest.raises(RATCHET.RatchetError, match="must be a non-empty string"):
        RATCHET.candidate_keys(payload)


def test_empty_call_site_members_are_refused_rather_than_dropped() -> None:
    payload = {
        "schemaVersion": "charness.quality.boundary_bypass_inventory.v2",
        "candidates": [{
            "test_file": "tests/test_foo.py",
            "import_safe_targets": ["scripts/foo.py"],
            "call_site_member_hashes": [],
        }],
    }

    with pytest.raises(RATCHET.RatchetError, match="call_site_member_hashes"):
        RATCHET.candidate_keys(payload)


def test_candidate_key_count_is_the_size_of_the_key_set_not_a_sum_of_row_targets() -> None:
    """The property COUNT_FIELDS relies on, pinned so it cannot regress silently.

    Without this, `filtered_summary` could drift back to summing per-row target counts and the
    subsumption argument for dropping `candidate_key_count` from COUNT_FIELDS would quietly stop
    holding, with nothing failing. The payload here repeats a key across two rows -- a shape this
    repo's generator does not emit, which is exactly why the old sum-shaped version agreed with
    the published contract by luck rather than by construction.
    """
    payload = {
        "schemaVersion": "charness.quality.boundary_bypass_inventory.v2",
        "candidates": [
            {"test_file": "tests/test_foo.py", "import_safe_targets": ["scripts/foo.py", "scripts/foo.py"], "call_site_member_hashes": ["same"]},
            {"test_file": "tests/test_foo.py", "import_safe_targets": ["scripts/foo.py"], "call_site_member_hashes": ["same"]},
        ],
    }
    summary = RATCHET.filtered_summary(payload, {})
    assert summary["candidate_key_count"] == len(RATCHET.candidate_keys(payload)) == 1


def test_exemption_requires_why_rationale(tmp_path: Path) -> None:
    path = tmp_path / "exemptions.txt"
    path.write_text("tests/test_foo.py::scripts/foo.py\n", encoding="utf-8")
    with pytest.raises(RATCHET.RatchetError, match="# why:"):
        RATCHET.load_exemptions(path)


def test_exemption_allows_new_candidate(tmp_path: Path) -> None:
    payload = INVENTORY.find_boundary_bypass_candidates(_repo_with_candidate(tmp_path))
    baseline = RATCHET.build_baseline({
        "schemaVersion": payload["schemaVersion"],
        "call_site_fingerprint_algo_version": payload["call_site_fingerprint_algo_version"],
        "candidates": [],
    })
    exemptions = {RATCHET.candidate_keys(payload)[0]: "intentional CLI contract"}
    report = RATCHET.check_payload(payload, baseline, exemptions)
    assert report["ok"] is True
    assert report["summary"]["candidate_count"] == 0
    assert report["exempted_count"] == 1
