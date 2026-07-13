from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from .support import ROOT

SCRIPTS = ROOT / "skills" / "public" / "quality" / "scripts"

def _load(name: str):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"{name}_inproc_scoped", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

lib = _load("dup_ratchet_lib")
baseline_lib = _load("dup_ratchet_baseline_lib")
fingerprint = _load("nose_fingerprint_lib")
check = _load("check_dup_ratchet")

def _write_json(path: Path, obj: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8")
    return path

def _code_inventory(path: Path, family_ids: list[str]) -> Path:
    return _write_json(path, {
        "status": "findings",
        "families": [{"family_fingerprint": fid, "family_member_hashes": [fid]} for fid in family_ids],
    })

def _consumer_repo(
    tmp_path: Path, *, baseline_ids: tuple[str, ...] = ("known1",),
) -> Path:
    repo = tmp_path / "consumer"
    (repo / ".agents").mkdir(parents=True)
    _write_json(repo / "q" / "dup-review.json", {
        "schemaVersion": "charness.quality.dup_review.v1", "fixable_ceiling": 0, "entries": [],
    })
    _write_json(repo / "q" / "dup-ratchet-baseline.json", baseline_lib.build_gate_baseline({
        fid: [fid] for fid in baseline_ids
    }))
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nrepo: consumer\ndup_ratchet:\n  enabled: true\n  floor_F: 0\n  escalation_K: 10\n  scope_paths:\n    - src\n  review_artifact_path: q/dup-review.json\n  gate_baseline_path: q/dup-ratchet-baseline.json\n",
        encoding="utf-8",
    )
    return repo

def _run_inproc(repo: Path, *cli: str) -> dict:
    args = check.parse_args(["--repo-root", str(repo), *cli])
    return check.run(args.repo_root.resolve(), args)
# --------------------------------------------------------------------------- #
# Scoped re-baseline — the routine-churn teeth fix: `--write-baseline`'s full-scan
# overwrite silently re-accepts every unreviewed new family; `--accept-rotation`
# OLD_ID=NEW_ID / `--accept-family` NEW_ID apply ONLY the named delta and refuse
# (listing) anything else. See references/dup-ratchet.md "Re-Baseline Triggers".
# --------------------------------------------------------------------------- #
def test_parse_rotations_splits_pairs_and_flags_malformed() -> None:
    pairs, malformed = lib.parse_rotations(["old=new", "bad", "  a  =  b  ", "=noold", "noNew="])
    assert pairs == [("old", "new"), ("a", "b")]
    assert malformed == ["bad", "=noold", "noNew="]


def test_plan_scoped_rebaseline_applies_only_named_rotation() -> None:
    plan = lib.plan_scoped_rebaseline(
        existing_ids={"old1", "keep"}, live_ids={"rot_new", "keep"},
        rotations=[("old1", "rot_new")], accept_families=[],
    )
    assert plan["ok"] is True
    assert plan["updated_ids"] == {"rot_new", "keep"}
    assert plan["errors"] == [] and plan["refused_added"] == []


def test_plan_scoped_rebaseline_applies_named_family_accept() -> None:
    plan = lib.plan_scoped_rebaseline(
        existing_ids={"keep"}, live_ids={"keep", "newfam"},
        rotations=[], accept_families=["newfam"],
    )
    assert plan["ok"] is True
    assert plan["updated_ids"] == {"keep", "newfam"}


def test_plan_scoped_rebaseline_refuses_unnamed_new_family() -> None:
    plan = lib.plan_scoped_rebaseline(
        existing_ids={"old1", "keep"}, live_ids={"rot_new", "keep", "unnamed"},
        rotations=[("old1", "rot_new")], accept_families=[],
    )
    assert plan["ok"] is False
    assert plan["refused_added"] == ["unnamed"]
    assert plan["updated_ids"] is None


def test_plan_scoped_rebaseline_flags_accept_family_not_in_live_scan() -> None:
    plan = lib.plan_scoped_rebaseline(
        existing_ids={"keep"}, live_ids={"keep"},
        rotations=[], accept_families=["ghost"],
    )
    assert plan["ok"] is False
    assert "--accept-family 'ghost' is not in the live scan" in " ".join(plan["errors"])


def test_plan_scoped_rebaseline_validates_rotation_and_family_names() -> None:
    plan = lib.plan_scoped_rebaseline(
        existing_ids={"keep"}, live_ids={"keep"},
        rotations=[("notinbaseline", "notinlive"), ("dup", "a"), ("dup", "b")],
        accept_families=["keep"],  # already in the baseline: nothing to accept
    )
    assert plan["ok"] is False
    joined = " ".join(plan["errors"])
    assert "notinbaseline" in joined and "not in the current baseline" in joined
    assert "notinlive" in joined and "not in the live scan" in joined
    assert "'dup'" in joined and "more than once" in joined
    assert "already in the baseline" in joined


def test_inproc_scoped_rebaseline_rotation_updates_only_named_pair(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("old1", "keep"))
    code_json = _code_inventory(tmp_path / "code.json", ["ROT_NEW", "keep"])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--accept-rotation", "old1=ROT_NEW")
    assert report["ok"] is True and report["status"] == "scoped-rebaseline-written"
    assert report["accepted_rotations"] == [{"old": "old1", "new": "ROT_NEW"}]
    assert report["accepted_families"] == []
    written = json.loads((repo / "q" / "dup-ratchet-baseline.json").read_text(encoding="utf-8"))
    assert baseline_lib.load_gate_baseline_ids(written) == {"ROT_NEW", "keep"}


def test_inproc_scoped_rebaseline_family_accept_updates_only_named_id(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("keep",))
    code_json = _code_inventory(tmp_path / "code.json", ["keep", "NEWFAM"])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--accept-family", "NEWFAM")
    assert report["ok"] is True and report["status"] == "scoped-rebaseline-written"
    assert report["accepted_families"] == ["NEWFAM"]
    written = json.loads((repo / "q" / "dup-ratchet-baseline.json").read_text(encoding="utf-8"))
    assert baseline_lib.load_gate_baseline_ids(written) == {"keep", "NEWFAM"}


def test_inproc_scoped_rebaseline_refuses_unnamed_new_family_and_preserves_baseline(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("old1", "keep"))
    code_json = _code_inventory(tmp_path / "code.json", ["ROT_NEW", "keep", "BRANDNEW"])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--accept-rotation", "old1=ROT_NEW")
    assert report["ok"] is False and report["status"] == "scoped-rebaseline-refused"
    assert report["refused_added"] == ["BRANDNEW"]
    preserved = json.loads((repo / "q" / "dup-ratchet-baseline.json").read_text(encoding="utf-8"))
    assert baseline_lib.load_gate_baseline_ids(preserved) == {"old1", "keep"}  # unchanged


def test_inproc_scoped_rebaseline_fails_when_live_fingerprints_unreadable(tmp_path: Path) -> None:
    # An existing baseline IS present and loadable (skips the "no readable
    # baseline" early return), but the injected code-inventory path does not
    # exist, so `code_family_members` returns a reason -- the scoped rebaseline
    # must refuse with that reason rather than proceed with an empty live set.
    repo = _consumer_repo(tmp_path, baseline_ids=("old1",))
    report = _run_inproc(
        repo, "--code-inventory", str(tmp_path / "absent.json"), "--accept-rotation", "old1=new1",
    )
    assert report["ok"] is False and report["status"] == "scoped-rebaseline-failed"
    joined = " ".join(report["messages"])
    assert "cannot compute live fingerprints" in joined and "unreadable" in joined


def test_inproc_scoped_rebaseline_requires_existing_baseline(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("old1",))
    (repo / "q" / "dup-ratchet-baseline.json").unlink()
    code_json = _code_inventory(tmp_path / "code.json", ["ROT_NEW"])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--accept-rotation", "old1=ROT_NEW")
    assert report["ok"] is False and report["status"] == "scoped-rebaseline-failed"
    assert "--write-baseline" in " ".join(report["messages"])


def test_inproc_scoped_rebaseline_malformed_rotation_is_invalid(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("old1",))
    code_json = _code_inventory(tmp_path / "code.json", ["old1"])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--accept-rotation", "badformat")
    assert report["ok"] is False and report["status"] == "scoped-rebaseline-invalid"
    assert any("malformed" in m for m in report["messages"])


def test_inproc_write_baseline_warns_preferring_scoped_mode_on_overwrite(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("old",))
    code_json = _code_inventory(tmp_path / "code.json", ["a", "b"])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--write-baseline")
    assert report["ok"] is True and report["status"] == "baseline-written"
    assert any("WARN" in m and "--accept-rotation" in m for m in report["messages"])


def test_inproc_write_baseline_no_warn_on_first_bootstrap(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("old",))
    (repo / "q" / "dup-ratchet-baseline.json").unlink()
    code_json = _code_inventory(tmp_path / "code.json", ["a", "b"])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--write-baseline")
    assert report["ok"] is True and report["status"] == "baseline-written"
    assert not any("WARN" in m for m in report["messages"])
