from __future__ import annotations

import json
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


@pytest.mark.parametrize("class_tag", ["INLINE", "DUP"])
def test_class_tag_does_not_waive_coverage(tmp_path: Path, class_tag: str) -> None:
    # INVERTED 2026-08-11. This used to assert a DUP/INLINE classTag waived the
    # cross-check; now it asserts the opposite, because the tag answers "is this DOC
    # redundant with SKILL.md" and the cross-check asks "does any scenario exercise
    # this planner BRANCH". A redundant doc on an uncovered branch still lets a
    # regression there escape every eval. The allowlist is the only waiver channel
    # left: one line, one written reason, and a stale advisory when it stops being
    # needed -- none of which the tag had.
    entry = _scaffold_skill(tmp_path, "alpha", {"a.md": _ea(), "b.md": _od(class_tag=class_tag)}, rcf=["a.md"])
    _write_registry(tmp_path, [entry])
    with pytest.raises(ValidationError, match=r"conditional-reads cross-check:.*b\.md"):
        cross_check_conditional_reads(tmp_path, extractors={"alpha": lambda root: {"a.md", "b.md"}})


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
    # The unhealthy-adapter branch still has the one live waiver. The route-neutral
    # judge-intent fixture owns the two former route-coverage gaps, so retaining
    # their historical allowlist records deliberately produces stale advisories.
    assert report["skills"]["handoff"]["waived_allowlist"] == ["adapter-contract.md"]
    assert report["stale_allowlist"] == [
        {
            "skill_id": "handoff",
            "ref": "state-selection.md",
            "reason": "DISCHARGED 2026-08-12 by handoff/judge-intent, which engage-always forces this former judge_from_user_request coverage gap. Retained intentionally so the validator reports a stale-advisory record rather than silently deleting waiver history.",
        },
        {
            "skill_id": "handoff",
            "ref": "workflow-trigger.md",
            "reason": "DISCHARGED 2026-08-12 by handoff/judge-intent, which engage-always forces this former judge_from_user_request coverage gap. Retained intentionally so the validator reports a stale-advisory record rather than silently deleting waiver history.",
        },
    ]


def test_judge_intent_scenario_covers_the_route_undetermined_branch() -> None:
    spec_path = HANDOFF_FIDELITY_DIR / "judge-intent.spec.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    registry = json.loads((ROOT / "evals" / "cautilus" / "claim-fidelity-registry.json").read_text(encoding="utf-8"))

    assert spec["scenarioId"] == "judge-intent"
    assert spec["prompt"] == "/charness:handoff The correct route is not specified. Before deciding or declaring pickup, refresh, or chunked routing, run the handoff planner with --intent auto and use its safety-net reads to judge the next action."
    assert spec["requiredCommandFragments"] == []
    assert spec["requiredOpenedReferences"] == ["workflow-trigger.md", "state-selection.md"]
    assert {ref for ref, engagement in spec["referenceEngagement"].items() if engagement["engagement"] == "engage-always"} == {
        "workflow-trigger.md",
        "state-selection.md",
    }
    assert "correct route is not specified" in spec["prompt"].lower()
    assert "--intent auto" in spec["prompt"]
    assert "--intent pickup" not in spec["prompt"]
    assert "--intent refresh" not in spec["prompt"]
    assert "--intent chunked_routing" not in spec["prompt"]
    assert {
        "skill_id": "handoff",
        "scenario_id": "judge-intent",
        "spec_path": "evals/cautilus/handoff-claim-fidelity/judge-intent.spec.json",
        "fan_out_fit": "yes — an undeclared route reaches the planner's judge_from_user_request safety-net branch, which unconditionally reads workflow-trigger.md and state-selection.md before any route is declared; neither the chunked-routing nor refresh scenario covers both reads.",
    } in registry["specs"]


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
