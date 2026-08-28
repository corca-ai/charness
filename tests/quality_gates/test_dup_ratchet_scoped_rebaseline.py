from __future__ import annotations

import json
from pathlib import Path

from .seeding_support import load_module
from .support import ROOT

SCRIPTS = ROOT / "skills" / "public" / "quality" / "scripts"

def _load(name: str):
    return load_module(f"{name}_inproc_scoped", SCRIPTS / f"{name}.py")

lib = _load("dup_ratchet_lib")
baseline_lib = _load("dup_ratchet_baseline_lib")
fingerprint = _load("nose_fingerprint_lib")
check = _load("check_dup_ratchet")

def _write_json(path: Path, obj: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8")
    return path

def _code_inventory(
    path: Path, family_ids: list[str], members: dict[str, list[str]] | None = None
) -> Path:
    return _write_json(path, {
        "status": "findings",
        "families": [{"family_fingerprint": fid,
                      "family_member_hashes": (members or {}).get(fid, [fid])} for fid in family_ids],
    })

def _consumer_repo(
    tmp_path: Path, *, baseline_ids: tuple[str, ...] = ("known1",),
    baseline_members: dict[str, list[str]] | None = None,
    review_entries: tuple[dict, ...] = (),
) -> Path:
    repo = tmp_path / "consumer"
    (repo / ".agents").mkdir(parents=True)
    _write_json(repo / "q" / "dup-review.json", {
        "schemaVersion": "charness.quality.dup_review.v1", "fixable_ceiling": 0,
        "entries": list(review_entries),
    })
    _write_json(repo / "q" / "dup-ratchet-baseline.json", baseline_lib.build_gate_baseline(
        baseline_members if baseline_members is not None else {fid: [fid] for fid in baseline_ids}
    ))
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


def test_plan_scoped_rebaseline_exempts_named_exempt_live_ids() -> None:
    plan = lib.plan_scoped_rebaseline(
        existing_ids={"old1", "keep"}, live_ids={"rot_new", "keep", "tolerated"},
        rotations=[("old1", "rot_new")], accept_families=[],
        exempt_live_ids={"tolerated"},
    )
    assert plan["ok"] is True
    assert plan["updated_ids"] == {"rot_new", "keep"}  # exempt id neither refused nor absorbed


def test_scoped_rebaseline_exemptions_mirror_evaluate_universe() -> None:
    # Scoped-rebaseline disagreement regression: the evaluate path tolerates
    # overlay-intentional families and membership reductions, so the scoped
    # planner's refusal universe must exempt exactly those.
    live = {"SHRUNK": ["h1", "h2"], "INTENT": ["x"], "keep": ["keep"], "NAMED": ["n"]}
    existing = {"bigfam": ["h1", "h1", "h2"], "keep": ["keep"], "old1": ["o"]}
    overlay = {"entries": [{"class": "intentional", "surface": "code", "id": "INTENT"}]}
    exemptions = lib.scoped_rebaseline_exemptions(
        live_members=live, existing_members=existing, overlay=overlay, named_new_ids={"NAMED"},
    )
    assert exemptions["ignored_intentional"] == ["INTENT"]
    assert exemptions["unnamed_reductions"] == [{"new_fingerprint": "SHRUNK", "old_fingerprint": "bigfam"}]
    assert exemptions["exempt_live_ids"] == {"INTENT", "SHRUNK"}
    joined = " ".join(exemptions["advisories"])
    assert "--accept-rotation bigfam=SHRUNK" in joined and "INTENT" in joined


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


def test_inproc_scoped_rebaseline_leaves_intentional_family_unrefused(tmp_path: Path) -> None:
    # A live family classified `intentional` in the review overlay is clean to the
    # evaluate path, so a scoped accept of an evaluate-suggested rotation must not
    # refuse it as "unnamed new" — and must not absorb it into the baseline either.
    repo = _consumer_repo(
        tmp_path, baseline_ids=("old1", "keep"),
        review_entries=({"class": "intentional", "surface": "code", "id": "INTENT"},),
    )
    code_json = _code_inventory(tmp_path / "code.json", ["ROT_NEW", "keep", "INTENT"])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--accept-rotation", "old1=ROT_NEW")
    assert report["ok"] is True and report["status"] == "scoped-rebaseline-written"
    assert report["ignored_intentional"] == ["INTENT"]
    written = json.loads((repo / "q" / "dup-ratchet-baseline.json").read_text(encoding="utf-8"))
    assert baseline_lib.load_gate_baseline_ids(written) == {"ROT_NEW", "keep"}  # INTENT not absorbed


def test_inproc_scoped_rebaseline_leaves_unnamed_reduction_unrefused(tmp_path: Path) -> None:
    # A membership reduction is advisory-only to the evaluate path; a scoped accept
    # that does not name its rotation must proceed, keep the vanished old family,
    # leave the shrunk fingerprint out, and re-print the rotation hint.
    repo = _consumer_repo(
        tmp_path,
        baseline_members={"bigfam": ["h1", "h1", "h2"], "old1": ["old1"], "keep": ["keep"]},
    )
    code_json = _code_inventory(
        tmp_path / "code.json", ["ROT_NEW", "keep", "SHRUNK"], members={"SHRUNK": ["h1", "h2"]},
    )
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--accept-rotation", "old1=ROT_NEW")
    assert report["ok"] is True and report["status"] == "scoped-rebaseline-written"
    assert report["unnamed_reductions"] == [{"new_fingerprint": "SHRUNK", "old_fingerprint": "bigfam"}]
    assert any("--accept-rotation bigfam=SHRUNK" in m for m in report["messages"])
    written = json.loads((repo / "q" / "dup-ratchet-baseline.json").read_text(encoding="utf-8"))
    assert baseline_lib.load_gate_baseline_ids(written) == {"bigfam", "ROT_NEW", "keep"}


def test_inproc_scoped_rebaseline_refuses_genuine_new_alongside_exemptions(tmp_path: Path) -> None:
    # Over-swallow guard: the exemptions must not widen past the evaluate-tolerated
    # classes. With an intentional family, an unnamed reduction, AND a genuinely new
    # unnamed family all live in one run, only the genuine one is refused, and the
    # baseline is left untouched.
    repo = _consumer_repo(
        tmp_path,
        baseline_members={"bigfam": ["h1", "h1", "h2"], "old1": ["old1"], "keep": ["keep"]},
        review_entries=({"class": "intentional", "surface": "code", "id": "INTENT"},),
    )
    code_json = _code_inventory(
        tmp_path / "code.json", ["ROT_NEW", "keep", "SHRUNK", "INTENT", "BRANDNEW"],
        members={"SHRUNK": ["h1", "h2"]},
    )
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--accept-rotation", "old1=ROT_NEW")
    assert report["ok"] is False and report["status"] == "scoped-rebaseline-refused"
    assert report["refused_added"] == ["BRANDNEW"]
    preserved = json.loads((repo / "q" / "dup-ratchet-baseline.json").read_text(encoding="utf-8"))
    assert baseline_lib.load_gate_baseline_ids(preserved) == {"bigfam", "old1", "keep"}


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


# --------------------------------------------------------------------------- #
# `--restamp-tool-version` — the version-only skew fix. A nose bump re-stamps
# nothing, so the skew warning fires on every run until someone re-baselines; but
# `--write-baseline` absorbs every unreviewed new family and the scoped accepts
# require naming an id, so "only the version moved" had no honest fix and the
# warning became furniture. This path re-stamps ONLY when the family set is
# provably unchanged.
# --------------------------------------------------------------------------- #
def _stamped_inventory(path: Path, family_ids: list[str], tool_version: str) -> Path:
    return _write_json(path, {
        "status": "findings",
        "tool_version": tool_version,
        "families": [{"family_fingerprint": fid, "family_member_hashes": [fid]} for fid in family_ids],
    })


def _stamped_repo(tmp_path: Path, family_ids: tuple[str, ...], tool_version: str) -> Path:
    repo = _consumer_repo(tmp_path, baseline_ids=family_ids)
    _write_json(repo / "q" / "dup-ratchet-baseline.json", baseline_lib.build_gate_baseline(
        {fid: [fid] for fid in family_ids},
        tool_version=tool_version,
        algo_version=fingerprint.FINGERPRINT_ALGO_VERSION,
    ))
    return repo


def test_inproc_restamp_rewrites_the_version_when_only_the_version_moved(tmp_path: Path) -> None:
    repo = _stamped_repo(tmp_path, ("keep1", "keep2"), "0.19.0")
    code_json = _stamped_inventory(tmp_path / "code.json", ["keep1", "keep2"], "0.20.0")

    report = _run_inproc(repo, "--code-inventory", str(code_json), "--restamp-tool-version")

    assert report["ok"] is True and report["status"] == "restamp-written"
    assert report["baseline_tool_version"] == "0.19.0"
    assert report["tool_version"] == "0.20.0"
    assert report["code_family_count"] == 2
    written = json.loads((repo / "q" / "dup-ratchet-baseline.json").read_text(encoding="utf-8"))
    assert baseline_lib.load_gate_baseline_tool_version(written) == "0.20.0"
    # The set must survive the re-stamp untouched; that is the whole claim.
    assert set(baseline_lib.load_gate_baseline_members(written)) == {"keep1", "keep2"}


def test_inproc_restamp_refuses_when_the_family_set_changed(tmp_path: Path) -> None:
    """A bump that regrouped families makes the stored set genuinely stale. Re-stamping
    it would assert a review under the new scanner that never happened."""
    repo = _stamped_repo(tmp_path, ("keep", "gone"), "0.19.0")
    code_json = _stamped_inventory(tmp_path / "code.json", ["keep", "arrived"], "0.20.0")

    report = _run_inproc(repo, "--code-inventory", str(code_json), "--restamp-tool-version")

    assert report["ok"] is False and report["status"] == "restamp-refused"
    assert report["added"] == ["arrived"] and report["removed"] == ["gone"]
    written = json.loads((repo / "q" / "dup-ratchet-baseline.json").read_text(encoding="utf-8"))
    assert baseline_lib.load_gate_baseline_tool_version(written) == "0.19.0", "refusal must not write"
    assert set(baseline_lib.load_gate_baseline_members(written)) == {"keep", "gone"}


def test_inproc_restamp_refuses_a_pure_addition(tmp_path: Path) -> None:
    """Refusal is in BOTH directions: a new family arriving is new duplication, and
    slipping it in under a version re-stamp is exactly the absorption this avoids."""
    repo = _stamped_repo(tmp_path, ("keep",), "0.19.0")
    code_json = _stamped_inventory(tmp_path / "code.json", ["keep", "arrived"], "0.20.0")

    report = _run_inproc(repo, "--code-inventory", str(code_json), "--restamp-tool-version")

    assert report["ok"] is False and report["status"] == "restamp-refused"
    assert report["added"] == ["arrived"] and report["removed"] == []


def test_inproc_restamp_is_a_noop_when_the_version_already_matches(tmp_path: Path) -> None:
    repo = _stamped_repo(tmp_path, ("keep",), "0.20.0")
    code_json = _stamped_inventory(tmp_path / "code.json", ["keep"], "0.20.0")

    report = _run_inproc(repo, "--code-inventory", str(code_json), "--restamp-tool-version")

    assert report["ok"] is True and report["status"] == "restamp-noop"
    assert any("nothing to re-stamp" in m for m in report["messages"])


def test_inproc_restamp_fails_without_a_readable_baseline(tmp_path: Path) -> None:
    repo = _stamped_repo(tmp_path, ("keep",), "0.19.0")
    (repo / "q" / "dup-ratchet-baseline.json").unlink()
    code_json = _stamped_inventory(tmp_path / "code.json", ["keep"], "0.20.0")

    report = _run_inproc(repo, "--code-inventory", str(code_json), "--restamp-tool-version")

    assert report["ok"] is False and report["status"] == "restamp-failed"
    assert any("--write-baseline" in m for m in report["messages"])


def test_rebaseline_module_bootstrap_guard_raises_without_an_ancestor_shim(
    tmp_path: Path, monkeypatch
) -> None:
    """Cover the portability shim's not-found guard (same forcing technique as
    tests/test_adapter_shim_inprocess_coverage.py). The happy path always finds
    skill_runtime_bootstrap.py walking up from THIS repo, so the branch only runs
    with __file__ pointed at an isolated tree."""
    import pytest

    rebaseline = _load("dup_ratchet_rebaseline")
    isolated = tmp_path / "deep" / "nest" / "dup_ratchet_rebaseline.py"
    isolated.parent.mkdir(parents=True)
    monkeypatch.setattr(rebaseline, "__file__", str(isolated))

    with pytest.raises(ImportError, match="skill_runtime_bootstrap.py not found"):
        rebaseline._load_skill_runtime_bootstrap()


def test_inproc_restamp_propagates_a_failed_live_scan(tmp_path: Path) -> None:
    """The scan-failed early return: an unreadable inventory must surface the typed
    scan failure, not fall through to compare against an empty family set (which
    would read as "everything was removed") ."""
    repo = _stamped_repo(tmp_path, ("keep",), "0.19.0")

    report = _run_inproc(
        repo, "--code-inventory", str(tmp_path / "absent.json"), "--restamp-tool-version",
    )

    assert report["ok"] is False and report["status"] == "restamp-failed"
    assert any("cannot compute live fingerprints" in m for m in report["messages"])


def test_inproc_restamp_refuses_a_pure_removal(tmp_path: Path) -> None:
    """The refusal claims both directions; addition is pinned above, removal here."""
    repo = _stamped_repo(tmp_path, ("keep", "gone"), "0.19.0")
    code_json = _stamped_inventory(tmp_path / "code.json", ["keep"], "0.20.0")

    report = _run_inproc(repo, "--code-inventory", str(code_json), "--restamp-tool-version")

    assert report["ok"] is False and report["status"] == "restamp-refused"
    assert report["added"] == [] and report["removed"] == ["gone"]


def test_parse_args_refuses_two_baseline_mutation_modes() -> None:
    """`run()` dispatches to the first matching mode, so a second flag was silently
    dropped. Worst case: `--restamp-tool-version --accept-family X` ignored the accept
    and then refused with a message telling the operator to use --accept-family."""
    import pytest

    for extra in (["--write-baseline"], ["--accept-family", "NEWFAM"], ["--accept-rotation", "a=b"]):
        with pytest.raises(SystemExit):
            check.parse_args(["--repo-root", ".", "--restamp-tool-version", *extra])
    # One mode at a time still parses.
    assert check.parse_args(["--repo-root", ".", "--restamp-tool-version"]).restamp_tool_version is True
    assert check.parse_args(["--repo-root", ".", "--write-baseline"]).write_baseline is True
