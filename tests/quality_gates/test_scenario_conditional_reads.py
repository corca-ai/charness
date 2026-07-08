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

HANDOFF_FORCEABLE = {
    "chunked-routing.md",
    "workflow-trigger.md",
    "continuation-sequence.md",
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


def test_incident_reconstruction_flags_unforced_continuation_sequence(tmp_path: Path) -> None:
    # Reconstructs the incident this validator guards against: the pickup planner
    # branch conditionalized continuation-sequence.md and no scenario forced the
    # ambiguous arm. Deleting pickup-ambiguous.spec.json from a copy of the real
    # handoff fixtures reproduces that gap.
    shutil.copytree(HANDOFF_SKILL_DIR, tmp_path / "skills" / "public" / "handoff", ignore=REPO_COPY_IGNORE)
    shutil.copytree(
        HANDOFF_FIDELITY_DIR,
        tmp_path / "evals" / "cautilus" / "handoff-claim-fidelity",
        ignore=REPO_COPY_IGNORE,
    )
    (tmp_path / "evals" / "cautilus" / "handoff-claim-fidelity" / "pickup-ambiguous.spec.json").unlink()
    (tmp_path / ALLOWLIST_PATH).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / ALLOWLIST_PATH, tmp_path / ALLOWLIST_PATH)
    _write_registry(
        tmp_path,
        [
            {
                "skill_id": "handoff",
                "spec_path": "evals/cautilus/handoff-claim-fidelity/spec.json",
                "fan_out_fit": "incident-reconstruction fixture",
            },
            {
                "skill_id": "handoff",
                "scenario_id": "pickup",
                "spec_path": "evals/cautilus/handoff-claim-fidelity/pickup.spec.json",
                "fan_out_fit": "incident-reconstruction fixture",
            },
            {
                "skill_id": "handoff",
                "scenario_id": "refresh",
                "spec_path": "evals/cautilus/handoff-claim-fidelity/refresh.spec.json",
                "fan_out_fit": "incident-reconstruction fixture",
            },
        ],
    )
    with pytest.raises(ValidationError, match="continuation-sequence.md"):
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
