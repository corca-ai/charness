from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from scripts.claim_fidelity_lib import (
    ALLOWLIST_PATH,
    PLANNER_FORCED_READ_EXTRACTORS,
    _handoff_planner_forceable,
    cross_check_conditional_reads,
)
from scripts.public_skill_validation_lib import ValidationError
from tests.repo_copy import REPO_COPY_IGNORE

from .test_claim_fidelity_specs import _ea, _od, _scaffold_skill, _write_registry

ROOT = Path(__file__).resolve().parents[2]
HANDOFF_SKILL_DIR = ROOT / "skills" / "public" / "handoff"
HANDOFF_FIDELITY_DIR = ROOT / "evals" / "cautilus" / "handoff-claim-fidelity"

# continuation-sequence.md left this set on 2026-08-11: the operator ruling deleted
# the pickup-ambiguity heuristic AND the planner string literal that made the
# reference forceable regardless of branch, so ordering plausible pickups is now
# SKILL.md prose the agent opens by judgment rather than a planner-forced read.
HANDOFF_FORCEABLE = {
    "chunked-routing.md",
    "workflow-trigger.md",
    "spill-targets.md",
    "adapter-contract.md",
    "state-selection.md",
}


def _write_allowlist(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_engage_always_coverage_passes(tmp_path: Path) -> None:
    entry = _scaffold_skill(tmp_path, "alpha", {"a.md": _ea()}, rcf=["a.md"])
    _write_registry(tmp_path, [entry])
    report = cross_check_conditional_reads(tmp_path, extractors={"alpha": lambda root: {"a.md"}})
    assert report["skills"]["alpha"]["flagged"] == []


def test_unforced_on_demand_reference_is_flagged(tmp_path: Path) -> None:
    entry = _scaffold_skill(tmp_path, "alpha", {"a.md": _ea(), "b.md": _od()}, rcf=["a.md"])
    _write_registry(tmp_path, [entry])
    with pytest.raises(ValidationError, match="b.md"):
        cross_check_conditional_reads(tmp_path, extractors={"alpha": lambda root: {"a.md", "b.md"}})


def test_waived_via_class_tag(tmp_path: Path) -> None:
    entry = _scaffold_skill(tmp_path, "alpha", {"a.md": _ea(), "b.md": _od(class_tag="INLINE")}, rcf=["a.md"])
    _write_registry(tmp_path, [entry])
    report = cross_check_conditional_reads(tmp_path, extractors={"alpha": lambda root: {"a.md", "b.md"}})
    assert report["skills"]["alpha"]["flagged"] == []
    assert report["skills"]["alpha"]["waived_class_tag"] == ["b.md"]


def test_waived_via_allowlist(tmp_path: Path) -> None:
    entry = _scaffold_skill(tmp_path, "alpha", {"a.md": _ea(), "b.md": _od()}, rcf=["a.md"])
    _write_registry(tmp_path, [entry])
    allowlist_path = tmp_path / "conditional-reads.allowlist.txt"
    _write_allowlist(allowlist_path, "alpha:b.md:decided waiver+reason for the test fixture\n")
    report = cross_check_conditional_reads(
        tmp_path,
        extractors={"alpha": lambda root: {"a.md", "b.md"}},
        allowlist_path=allowlist_path,
    )
    assert report["skills"]["alpha"]["flagged"] == []
    assert report["skills"]["alpha"]["waived_allowlist"] == ["b.md"]


def test_no_extractor_reports_not_yet_covered(tmp_path: Path) -> None:
    entry = _scaffold_skill(tmp_path, "alpha", {"a.md": _ea()}, rcf=["a.md"])
    _write_registry(tmp_path, [entry])
    report = cross_check_conditional_reads(tmp_path, extractors={})
    assert report["not_yet_covered"] == ["alpha"]


def test_stale_allowlist_entry_is_advisory_not_error(tmp_path: Path) -> None:
    entry = _scaffold_skill(tmp_path, "alpha", {"a.md": _ea()}, rcf=["a.md"])
    _write_registry(tmp_path, [entry])
    allowlist_path = tmp_path / "conditional-reads.allowlist.txt"
    # a.md is already engage-always covered, so waiving it too is unnecessary.
    _write_allowlist(allowlist_path, "alpha:a.md:no longer needed once a.md went engage-always\n")
    report = cross_check_conditional_reads(
        tmp_path,
        extractors={"alpha": lambda root: {"a.md"}},
        allowlist_path=allowlist_path,
    )
    assert report["skills"]["alpha"]["flagged"] == []
    assert report["stale_allowlist"] == [
        {"skill_id": "alpha", "ref": "a.md", "reason": "no longer needed once a.md went engage-always"}
    ]


def test_malformed_allowlist_line_rejected(tmp_path: Path) -> None:
    entry = _scaffold_skill(tmp_path, "alpha", {"a.md": _ea()}, rcf=["a.md"])
    _write_registry(tmp_path, [entry])
    allowlist_path = tmp_path / "conditional-reads.allowlist.txt"
    _write_allowlist(allowlist_path, "alpha:a.md\n")  # missing reason field
    with pytest.raises(ValidationError, match="malformed allowlist entry"):
        cross_check_conditional_reads(
            tmp_path,
            extractors={"alpha": lambda root: {"a.md"}},
            allowlist_path=allowlist_path,
        )


def test_extractor_registry_and_forceable_set_pin() -> None:
    # Falsifiable pin: a planner adding a new forced reference must update this
    # assertion AND cover/waive the ref, so the change cannot slip through quietly.
    assert set(PLANNER_FORCED_READ_EXTRACTORS) == {"handoff"}
    assert _handoff_planner_forceable(ROOT) == HANDOFF_FORCEABLE


def test_live_repo_conditional_reads_cross_check_is_clean() -> None:
    report = cross_check_conditional_reads(ROOT)
    assert report["skills"]["handoff"]["flagged"] == []
    assert "state-selection.md" in report["skills"]["handoff"]["waived_class_tag"]
    assert "adapter-contract.md" in report["skills"]["handoff"]["waived_allowlist"]
    # workflow-trigger.md is forced ONLY by judge_from_user_request, which no scenario
    # exercises. Its INLINE classTag lived in the two pickup specs deleted on
    # 2026-08-11; rather than re-home a CONTENT classification as a COVERAGE waiver,
    # the waiver moved to the allowlist, which carries a written reason AND goes
    # stale-advisory the moment coverage appears. This assertion is a record of a
    # known GAP, not a property worth preserving: adding a judge-intent scenario is
    # expected to red it, alongside the stale_allowlist advisory naming the same line.
    assert "workflow-trigger.md" in report["skills"]["handoff"]["waived_allowlist"]
    # Deliberately NOT asserting `report["stale_allowlist"] == []`: staleness is an
    # ADVISORY signal the validator prints and never raises on, pinned as such by
    # test_stale_allowlist_entry_is_advisory_not_error above. Blocking on it here
    # would make pytest and validate_scenario_conditional_reads.py disagree about
    # the same state — and a consumer repo vendoring the validator would get the
    # opposite verdict from the one this repo enforces.


def test_incident_reconstruction_flags_a_scenario_whose_coverage_disappeared(tmp_path: Path) -> None:
    # Reconstructs the incident this validator guards against, against the REAL handoff
    # fixtures rather than a synthetic skill: an eval scenario stops covering a
    # planner-forced reference, so a regression on that branch escapes every eval.
    #
    # The subject used to be continuation-sequence.md — unlink pickup-ambiguous.spec.json
    # and its engage-always coverage vanished. That reconstruction died with the
    # 2026-08-11 ruling: the planner literal is gone, so the reference is no longer
    # forceable and no fixture deletion can reproduce the gap through it. Re-keyed onto
    # chunked-routing.md, whose engage-always coverage lives in the DEFAULT spec.json:
    # deregistering that scenario is the same subtraction the deleted test made, on a
    # reference that is still forced. Deliberately NOT re-keyed onto an allowlist-waived
    # reference — that would test the waiver channel, which already has both arms in
    # test_waived_via_allowlist and test_unforced_on_demand_reference_is_flagged, and
    # would lose the "a real scenario went away" class this test exists for.
    shutil.copytree(HANDOFF_SKILL_DIR, tmp_path / "skills" / "public" / "handoff", ignore=REPO_COPY_IGNORE)
    shutil.copytree(
        HANDOFF_FIDELITY_DIR,
        tmp_path / "evals" / "cautilus" / "handoff-claim-fidelity",
        ignore=REPO_COPY_IGNORE,
    )
    (tmp_path / ALLOWLIST_PATH).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / ALLOWLIST_PATH, tmp_path / ALLOWLIST_PATH)
    _write_registry(
        tmp_path,
        [
            {
                "skill_id": "handoff",
                "scenario_id": "refresh",
                "spec_path": "evals/cautilus/handoff-claim-fidelity/refresh.spec.json",
                "fan_out_fit": "incident-reconstruction fixture",
            },
        ],
    )
    # Anchored on the cross-check's OWN message. A bare `match="chunked-routing.md"`
    # would also be satisfied by a validate_registry/validate_spec error that merely
    # names the file — e.g. renaming references/chunked-routing.md makes
    # `declaredReferences not present under references/` match, and this test would
    # pass green having never reached the cross-check at all.
    with pytest.raises(ValidationError, match=r"conditional-reads cross-check:.*chunked-routing\.md"):
        cross_check_conditional_reads(tmp_path)


def test_missing_planner_script_raises_clean_validation_error(tmp_path: Path) -> None:
    # A repo that registers the handoff extractor but ships no planner script
    # must get a clean ValidationError, not a bare FileNotFoundError traceback.
    entry = _scaffold_skill(tmp_path, "handoff", {"a.md": _ea()}, rcf=["a.md"])
    _write_registry(tmp_path, [entry])
    with pytest.raises(ValidationError, match="plan_handoff_run"):
        cross_check_conditional_reads(tmp_path)


def test_validator_script_main_runs_green_on_live_repo(monkeypatch, capsys) -> None:
    # In-process pin of the thin wrapper itself (argv/stdout contract), so the
    # script surface carries coverage, not only the lib underneath.
    import importlib.util
    import sys as _sys

    spec = importlib.util.spec_from_file_location(
        "validate_scenario_conditional_reads_inproc",
        ROOT / "scripts" / "validate_scenario_conditional_reads.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(
        _sys, "argv", ["validate_scenario_conditional_reads.py", "--repo-root", str(ROOT)]
    )
    rc = module.main()
    out = capsys.readouterr().out
    assert rc == 0
    assert "Validated conditional-reads cross-check" in out
    assert "not cross-checked" in out  # not-yet-covered advisories stay visible


def test_validator_script_prints_stale_allowlist_and_uncovered_advisories(monkeypatch, capsys) -> None:
    # Directed pin for the per-line advisory prints: the live-repo run above only
    # exercises "not cross-checked" (the repo currently HAS an uncovered skill), but
    # its allowlist happens to be clean, so the stale_allowlist print line has no
    # coverage from that run. Monkeypatch the loaded module's
    # cross_check_conditional_reads to a canned report carrying one stale_allowlist
    # entry + one not_yet_covered skill and assert both advisory lines print.
    import importlib.util
    import sys as _sys

    spec = importlib.util.spec_from_file_location(
        "validate_scenario_conditional_reads_inproc2",
        ROOT / "scripts" / "validate_scenario_conditional_reads.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(
        module,
        "cross_check_conditional_reads",
        lambda repo_root: {
            "skills": {"alpha": {}},
            "not_yet_covered": ["beta"],
            "stale_allowlist": [{"skill_id": "alpha", "ref": "a.md", "reason": "no longer needed"}],
        },
    )
    monkeypatch.setattr(_sys, "argv", ["validate_scenario_conditional_reads.py", "--repo-root", str(ROOT)])
    rc = module.main()
    out = capsys.readouterr().out
    assert rc == 0
    assert "`beta` has no forced-read extractor yet" in out and "not cross-checked" in out
    assert f"{module.ALLOWLIST_PATH} entry `alpha:a.md` looks stale" in out
