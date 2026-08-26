"""The non-complete terminal status for the achieve contract (#691).

A goal that ends without completing -- folded into a successor, overtaken, or
abandoned with its remainder handed on -- previously had only bad options: stay
`active` forever, or claim a `complete` it never earned. Both lie to the next
session, and the second lies in the direction that loses work. `corca-ai/ceal`
had already routed around it: its own drift checker accepts `superseded` and the
repo carries goals in that state, so the repo-local gate and the upstream
contract disagreed about what a legal status is -- with the permissive side in
daily use.

The risk in the fix is the fix itself. A terminal status that skips the closeout
floor and asks for nothing in return loses the same work more quietly: a
finished-looking artifact, no successor, no reason. So these tests are mostly
about what `superseded` COSTS.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from .support import ROOT

_ACHIEVE = ROOT / "skills" / "public" / "achieve" / "scripts"
_SOURCE_CHECKER = _ACHIEVE / "check_goal_artifact.py"
_PLUGIN_CHECKER = ROOT / "plugins" / "charness" / "skills" / "achieve" / "scripts" / "check_goal_artifact.py"

_IMPROVING_RETRO = (
    "# Session Retro — x\n"
    "Date: 2026-08-22\n"
    "Mode: goal\n\n"
    "## Next Improvements\n\n"
    "- carry the surfaced improvement into the successor\n"
)
_APPLIED_DISPOSITION = "Retro dispositions: applied: carried the improvement into the successor"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _ACHIEVE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def goal_lib():
    return _load("goal_artifact_lib")


@pytest.fixture(scope="module")
def pursue():
    return _load("goal_artifact_pursue")


def test_superseded_is_a_legal_status(goal_lib) -> None:
    """Pins that the status EXISTS. Without it the behavioural tests below stay
    green against a tree where it was never added, because they call the record
    checker directly and never go through status validation."""
    assert "superseded" in goal_lib.VALID_STATUSES


def test_superseded_is_terminal_so_in_flight_floors_do_not_grade_it(pursue) -> None:
    """Terminal in exactly the sense the predicate means -- nobody is expected to
    repair the record -- even though it is not complete. Leaving it out would
    grade an ended goal against floors whose purpose is to fire on a goal still in
    flight."""
    assert pursue.is_terminal_status("superseded") is True
    assert pursue.is_terminal_status("active") is False


def test_an_annotated_superseded_status_is_still_terminal(pursue) -> None:
    """The repo's house style annotates terminal statuses. A bare equality test
    silently disarms the skip, which is the defect `status_token` already exists
    to prevent for `complete`."""
    assert pursue.is_terminal_status("SUPERSEDED (2026-08-22) — folded into the successor") is True


@pytest.mark.parametrize("status", ["COMPLETE!", "SUPERSEDED!", "complete?", "superseded;"])
def test_terminal_punctuation_is_part_of_the_annotation_boundary(pursue, status: str) -> None:
    assert pursue.is_terminal_status(status) is True


@pytest.mark.parametrize("status", ["historical COMPLETE!", "complete-ish", "superseded_record"])
def test_unrelated_leading_words_and_extended_tokens_are_not_terminal(pursue, status: str) -> None:
    assert pursue.is_terminal_status(status) is False


def test_superseded_is_not_a_shaping_status(pursue) -> None:
    """Shaping floors (backlog recount, closeout binding plan) apply to a goal
    whose scope is still being decided. An ended one is not that."""
    assert pursue.is_shaping_status("superseded") is False


# --------------------------------------------------------------------------- #
# What the status costs
# --------------------------------------------------------------------------- #


def test_superseded_without_a_successor_record_is_refused(goal_lib) -> None:
    """THE guard that keeps this from being an escape hatch. Without it, adding
    the status would let a goal be abandoned with no account of where its
    remainder went -- losing the work more quietly than the lie it replaces."""
    report = goal_lib.check_superseded_record("Status: superseded\n")

    assert report["ok"] is False
    assert "Superseded by:" in report["reason"]


def test_a_punctuation_placeholder_is_not_a_successor_record(goal_lib) -> None:
    """`Superseded by: —` is a filled-looking empty field. The closeout-plan and
    backlog floors both learned this class already; inheriting the lesson is
    cheaper than re-learning it on a third surface."""
    report = goal_lib.check_superseded_record("Superseded by: —\n")

    assert report["ok"] is False
    assert "substantive" in report["reason"]


def test_a_named_successor_satisfies_the_record(goal_lib) -> None:
    report = goal_lib.check_superseded_record(
        "Superseded by: charness-artifacts/goals/2026-09-01-next.md — carried slices B and A\n"
    )

    assert report["ok"] is True


def test_an_explicit_none_satisfies_the_record(goal_lib) -> None:
    """Accepting this is the point, not a loophole: a goal genuinely abandoned
    with nothing downstream should say so out loud rather than be unable to
    close. The floor asks for an ANSWER, not for a successor to exist."""
    report = goal_lib.check_superseded_record(
        "- `Superseded by:` none — remainder dropped; the tracked issues carry it\n"
    )

    assert report["ok"] is True


def test_a_fenced_example_does_not_satisfy_the_record(goal_lib) -> None:
    """The reference documents the line inside a fenced block, and a goal that
    QUOTES the canonical form must not have the quotation read as its own claim.
    This repo has shipped that exact defect on an adjacent floor."""
    text = "Status: superseded\n\n```markdown\nSuperseded by: some/goal.md\n```\n"

    assert goal_lib.check_superseded_record(text)["ok"] is False


# --------------------------------------------------------------------------- #
# The writer refuses the flip, so the record cannot be added afterwards
# --------------------------------------------------------------------------- #


def test_upsert_refuses_to_flip_a_goal_superseded_without_the_record(
    goal_lib, tmp_path: Path
) -> None:
    """Checked at the WRITE, matching how `complete` is guarded. A validator that
    only complains after the fact leaves a window where the artifact already
    reads as terminal."""
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "goals").mkdir(parents=True)
    path = goal_lib.goal_path(repo, "2026-08-22", "demo")
    path.write_text("# Demo\n\nStatus: active\n", encoding="utf-8")

    with pytest.raises(ValueError) as excinfo:
        goal_lib.upsert_goal(
            repo, date="2026-08-22", slug="demo", title="Demo", status="superseded"
        )

    assert "superseded" in str(excinfo.value)


def test_upsert_allows_the_flip_once_the_record_is_present(goal_lib, tmp_path: Path) -> None:
    """The successor must EXIST, not merely be named -- so this fixture writes it.
    The pointer-existence check landing at the write is what made that necessary,
    and this test failing until the successor was created is the check working."""
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "goals").mkdir(parents=True)
    (repo / "charness-artifacts" / "goals" / "2026-09-01-next.md").write_text(
        "# next\n", encoding="utf-8"
    )
    (repo / "charness-artifacts" / "retro").mkdir(parents=True)
    (repo / "charness-artifacts" / "retro" / "2026-08-22-demo.md").write_text(
        _IMPROVING_RETRO, encoding="utf-8"
    )
    path = goal_lib.goal_path(repo, "2026-08-22", "demo")
    path.write_text(
        "# Demo\n\nStatus: active\nCreated: 2026-08-22\n"
        "Activation: `/goal @demo.md`\n\n"
        "Superseded by: charness-artifacts/goals/2026-09-01-next.md\n\n"
        "## Final Verification\n\n"
        "Retro: charness-artifacts/retro/2026-08-22-demo.md\n\n"
        "## Auto-Retro\n\n"
        + _APPLIED_DISPOSITION
        + "\n",
        encoding="utf-8",
    )

    goal_lib.upsert_goal(
        repo, date="2026-08-22", slug="demo", title="Demo", status="superseded"
    )

    assert "Status: superseded" in path.read_text(encoding="utf-8")


def test_upsert_refuses_a_superseded_flip_with_undispositioned_improvement(
    goal_lib, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "goals").mkdir(parents=True)
    (repo / "charness-artifacts" / "retro").mkdir(parents=True)
    (repo / "charness-artifacts" / "retro" / "2026-08-22-demo.md").write_text(
        _IMPROVING_RETRO, encoding="utf-8"
    )
    path = goal_lib.goal_path(repo, "2026-08-22", "demo")
    path.write_text(
        "# Demo\n\nStatus: active\nCreated: 2026-08-22\n"
        "Activation: `/goal @demo.md`\n\n"
        "Superseded by: none — the remainder was intentionally abandoned\n\n"
        "## Final Verification\n\n"
        "Retro: charness-artifacts/retro/2026-08-22-demo.md\n\n"
        "## Auto-Retro\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Auto-Retro|disposition"):
        goal_lib.upsert_goal(
            repo, date="2026-08-22", slug="demo", title="Demo", status="superseded"
        )

    assert "Status: active" in path.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# Round-2 repairs.
# --------------------------------------------------------------------------- #


def test_creating_straight_to_superseded_is_refused(goal_lib, tmp_path: Path) -> None:
    """The round-2 blocker. Both flip guards live inside `if path.exists()`, so
    `--status superseded` on a NEW slug wrote a terminal artifact with no record
    at all -- opening exactly the window the write-time guard exists to close."""
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "goals").mkdir(parents=True)

    with pytest.raises(ValueError) as excinfo:
        goal_lib.upsert_goal(
            repo, date="2026-08-22", slug="fresh", title="Fresh", status="superseded"
        )

    assert "create this goal `superseded`" in str(excinfo.value)
    assert not goal_lib.goal_path(repo, "2026-08-22", "fresh").exists()


def test_a_successor_pointer_that_names_nothing_is_refused(goal_lib, tmp_path: Path) -> None:
    """The successor pointer is the ENTIRE cost of this status -- roughly fourteen
    closeout floors are skipped for it -- and it was the only evidence line in
    this contract never checked for existence. A pointer at a file nobody wrote
    loses the work exactly as quietly as having no status would have."""
    report = goal_lib.check_superseded_record(
        "Superseded by: charness-artifacts/goals/2026-09-01-never-written.md\n",
        repo_root=tmp_path,
    )

    assert report["ok"] is False
    assert "does not exist" in report["reason"]


def test_prose_is_never_treated_as_a_pointer(goal_lib, tmp_path: Path) -> None:
    """`none — remainder dropped` has no `/` and no `.md`, so existence is never
    asserted about it. Guessing that prose is a path would refuse the one answer
    the floor exists to accept."""
    report = goal_lib.check_superseded_record(
        "Superseded by: none — folded into the next unit\n", repo_root=tmp_path
    )

    assert report["ok"] is True


def _run_checker(
    repo: Path,
    status: str,
    record: str = "",
    *,
    retro_text: str | None = None,
    auto_retro: str | None = None,
) -> dict:
    """Drive the REAL validator and return its payload."""
    goals = repo / "charness-artifacts" / "goals"
    goals.mkdir(parents=True, exist_ok=True)
    body = [
        "# Achieve Goal: demo",
        "",
        f"Status: {status}",
        "Created: 2026-08-22",
        "Activation: `/goal @x.md`",
        "",
        record,
        "",
    ]
    if retro_text is not None:
        retro_path = repo / "charness-artifacts" / "retro" / "2026-08-22-x.md"
        retro_path.parent.mkdir(parents=True, exist_ok=True)
        retro_path.write_text(retro_text, encoding="utf-8")
        body.extend([
            "## Final Verification",
            "",
            "Retro: charness-artifacts/retro/2026-08-22-x.md",
            "",
        ])
    if auto_retro is not None:
        body.extend(["## Auto-Retro", "", auto_retro, ""])
    (goals / "2026-08-22-demo.md").write_text("\n".join(body), encoding="utf-8")
    result = subprocess.run(
        ["python3", str(_ACHIEVE / "check_goal_artifact.py"),
         "--repo-root", str(repo), "--slug", "demo", "--date", "2026-08-22"],
        capture_output=True, text=True,
    )
    return yaml.safe_load(result.stdout)


def _readiness_fixture(
    goal_lib,
    status: str,
    record: str = "",
    *,
    retro_text: str | None = None,
    auto_retro: str | None = None,
) -> str:
    lines = [
        "# Achieve Goal: readiness fixture",
        "",
        f"Status: {status}",
        "Created: 2026-08-22",
        "Activation: `/goal @x.md`",
        "",
    ]
    if record:
        lines.extend([record, ""])
    for section in goal_lib.REQUIRED_SECTIONS + goal_lib.PORTABILITY_SECTIONS:
        lines.extend([f"## {section}", f"Written fixture content for {section}.", ""])
        if section == "Final Verification" and retro_text is not None:
            lines.extend(["Retro: charness-artifacts/retro/2026-08-22-x.md", ""])
        if section == "Auto-Retro" and auto_retro is not None:
            lines.extend([auto_retro, ""])
    return "\n".join(lines)


def _run_public_checker(checker: Path, repo: Path, goal: Path, *, pursue_ready: bool) -> dict:
    args = [sys.executable, str(checker), "--repo-root", str(repo), "--goal-path", str(goal)]
    if pursue_ready:
        args.append("--pursue-ready")
    result = subprocess.run(args, capture_output=True, text=True)
    assert result.stdout, result.stderr
    return yaml.safe_load(result.stdout)


def _write_readiness_fixture(
    goal_lib,
    repo: Path,
    status: str,
    record: str = "",
    *,
    retro_text: str | None = None,
    auto_retro: str | None = None,
) -> Path:
    goal = repo / "charness-artifacts" / "goals" / "2026-08-22-readiness.md"
    goal.parent.mkdir(parents=True, exist_ok=True)
    if retro_text is not None:
        retro = repo / "charness-artifacts" / "retro" / "2026-08-22-x.md"
        retro.parent.mkdir(parents=True, exist_ok=True)
        retro.write_text(retro_text, encoding="utf-8")
    goal.write_text(
        _readiness_fixture(
            goal_lib, status, record, retro_text=retro_text, auto_retro=auto_retro
        ),
        encoding="utf-8",
    )
    return goal


def _write_duplicate_readiness_fixture(goal_lib, repo: Path, section: str) -> Path:
    goal = repo / "charness-artifacts" / "goals" / "2026-08-22-duplicate-readiness.md"
    goal.parent.mkdir(parents=True, exist_ok=True)
    goal.write_text(
        _readiness_fixture(goal_lib, "active")
        + f"\n## {section}\nA second substantive statement for {section}.\n",
        encoding="utf-8",
    )
    return goal


@pytest.mark.parametrize(
    "status",
    [
        "superseded",
        "SUPERSEDED (2026-08-22) — folded into the successor",
        "SUPERSEDED!",
        "complete.",
        "COMPLETE!",
    ],
)
def test_terminal_status_never_allows_readiness(goal_lib, status: str) -> None:
    report = goal_lib.pursue_readiness(
        _readiness_fixture(
            goal_lib,
            status,
            "Superseded by: none — remainder is intentionally abandoned",
        )
    )

    assert report["pursue_ready"] is False
    assert report["activation_ready"] is False
    assert report["lifecycle"] == {
        "status": status,
        "status_token": goal_lib.status_token(status),
        "terminal": True,
        "pursuit_allowed": False,
    }
    assert report["hollow_sections"]["evaluated"] is False
    assert report["hollow_blocking_sections"] == []
    assert report["readiness_blockers"][0]["kind"] == "terminal_status"
    assert "historical and cannot be activated" in report["readiness_blockers"][0]["reason"]
    assert "non-pursuable:" in report["reason"]


@pytest.mark.parametrize(
    "record, record_ok",
    [
        ("", False),
        ("Superseded by: none — remainder is intentionally abandoned", True),
    ],
)
def test_full_validation_and_pursue_readiness_share_terminal_permission_boundary(
    goal_lib, tmp_path: Path, record: str, record_ok: bool
) -> None:
    goal = _write_readiness_fixture(
        goal_lib,
        tmp_path,
        "superseded",
        record,
        retro_text=_IMPROVING_RETRO if record_ok else None,
        auto_retro=_APPLIED_DISPOSITION if record_ok else None,
    )

    full = _run_public_checker(_SOURCE_CHECKER, tmp_path, goal, pursue_ready=False)
    pursue = _run_public_checker(_SOURCE_CHECKER, tmp_path, goal, pursue_ready=True)

    assert full["superseded_record"]["ok"] is record_ok
    assert full["superseded_evidence"]["ok"] is record_ok
    assert full["ok"] is record_ok
    assert pursue["pursue_ready"] is False
    assert pursue["activation_ready"] is False
    assert pursue["lifecycle"]["terminal"] is True
    assert pursue["readiness_blockers"][0]["kind"] == "terminal_status"


def test_source_and_plugin_cli_payloads_are_consumer_compatible(goal_lib, tmp_path: Path) -> None:
    goal = _write_readiness_fixture(
        goal_lib,
        tmp_path,
        "superseded",
        "Superseded by: none — remainder is intentionally abandoned",
        retro_text=_IMPROVING_RETRO,
        auto_retro=_APPLIED_DISPOSITION,
    )

    source = _run_public_checker(_SOURCE_CHECKER, tmp_path, goal, pursue_ready=True)
    plugin = _run_public_checker(_PLUGIN_CHECKER, tmp_path, goal, pursue_ready=True)

    assert source == plugin
    assert source["pursue_ready"] is False
    assert source["lifecycle"]["terminal"] is True
    assert source["readiness_blockers"] == [{
        "kind": "terminal_status",
        "status": "superseded",
        "reason": source["readiness_blockers"][0]["reason"],
    }]


@pytest.mark.parametrize("section", ["Goal", "Context Sources"])
def test_source_and_plugin_cli_reject_substantive_duplicate_sections_and_agree(
    goal_lib, tmp_path: Path, section: str
) -> None:
    goal = _write_duplicate_readiness_fixture(goal_lib, tmp_path, section)

    source_full = _run_public_checker(_SOURCE_CHECKER, tmp_path, goal, pursue_ready=False)
    plugin_full = _run_public_checker(_PLUGIN_CHECKER, tmp_path, goal, pursue_ready=False)
    source_pursue = _run_public_checker(_SOURCE_CHECKER, tmp_path, goal, pursue_ready=True)
    plugin_pursue = _run_public_checker(_PLUGIN_CHECKER, tmp_path, goal, pursue_ready=True)

    assert source_full == plugin_full
    assert source_pursue == plugin_pursue
    assert source_full["ok"] is False
    assert source_full["issues"] == [f"duplicate sections: {section}"]
    assert source_pursue["pursue_ready"] is False
    assert source_pursue["activation_ready"] is False
    assert source_pursue["duplicate_sections"] == [section]
    assert source_pursue["readiness_blockers"] == [{
        "kind": "duplicate_sections",
        "sections": [section],
        "reason": "required or portability H2 section appears more than once",
    }]


def test_the_validator_actually_fires_the_record_floor(tmp_path: Path) -> None:
    """The floor's PRODUCTION entry point, exercised end to end.

    A round-2 reviewer found this branch had no behavioural test at all -- every
    other test here calls the checker function directly, so deleting the
    validator wiring left the whole file green. Changed-line coverage agreed and
    named these exact lines as uncovered. An assertion about the validator's
    SOURCE TEXT, which the first repair reached for, is not a test of the branch.
    """
    payload = _run_checker(tmp_path, "superseded")

    assert payload["superseded_record"]["ok"] is False
    assert any("superseded-record floor" in issue for issue in payload["issues"])
    assert payload["ok"] is False


def test_an_annotated_superseded_status_reaches_the_record_floor(tmp_path: Path) -> None:
    """`is_terminal_status` normalizes the leading token, so an annotated status
    skips the cadence floor -- while a bare `== "superseded"` in the validator did
    NOT fire the record floor on the same string. One normalizer, both readers,
    proven by RUNNING the validator rather than by grepping it."""
    payload = _run_checker(tmp_path, "SUPERSEDED (2026-08-22) — folded into the successor")

    assert payload.get("superseded_record", {}).get("ok") is False, payload


def test_a_superseded_goal_with_a_real_successor_clears_the_floor(tmp_path: Path) -> None:
    """The other direction: the floor must not redden a record that answers it."""
    successor = tmp_path / "charness-artifacts" / "goals" / "2026-09-01-next.md"
    successor.parent.mkdir(parents=True, exist_ok=True)
    successor.write_text("# next\n", encoding="utf-8")

    payload = _run_checker(
        tmp_path, "superseded",
        "Superseded by: charness-artifacts/goals/2026-09-01-next.md",
        retro_text=_IMPROVING_RETRO,
        auto_retro=_APPLIED_DISPOSITION,
    )

    assert payload["superseded_record"]["ok"] is True, payload


def test_superseded_checker_refuses_an_improvement_without_disposition(tmp_path: Path) -> None:
    payload = _run_checker(
        tmp_path,
        "superseded",
        "Superseded by: none — the remainder was intentionally abandoned",
        retro_text=_IMPROVING_RETRO,
        auto_retro="",
    )

    assert payload["superseded_record"]["ok"] is True, payload
    assert payload["superseded_evidence"]["ok"] is False, payload
    assert "disposition" in payload["issues"][-1].lower()
    assert "superseded-evidence floor" in payload["issues"][-1]


def test_superseded_evidence_skip_is_an_explicit_non_claim(goal_lib, tmp_path: Path) -> None:
    text = (
        "Status: superseded\nCreated: 2026-08-22\n"
        "Activation: `/goal @x.md`\n\n"
        "## Final Verification\n\n"
        "Retro: skipped: host-log-not-exposed: this host does not expose the retro lane\n\n"
        "## Auto-Retro\n"
    )

    report = goal_lib.check_superseded_evidence(tmp_path, text)

    assert report["ok"] is True, report
    assert report["superseded_non_claim"]["claim"] == (
        "retro contents and surfaced improvements were not verified"
    )


def test_the_write_guard_checks_the_successor_pointer_too(goal_lib, tmp_path: Path) -> None:
    """The release critique's F6. The pointer-existence check reached the
    validator and NEITHER write, so `--status superseded` with a pointer at a file
    nobody wrote succeeded at the write and failed one validator cycle later --
    the exact window the write guard's own docstring says it exists to close, on
    the one check this module calls the entire cost of the status. Round 2 caught
    the sibling form (both guards inside `if path.exists()`); this residual
    survived it."""
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "goals").mkdir(parents=True)
    path = goal_lib.goal_path(repo, "2026-08-22", "demo")
    path.write_text(
        "# Demo\n\nStatus: active\n\nSuperseded by: charness-artifacts/goals/never-written.md\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError) as excinfo:
        goal_lib.upsert_goal(
            repo, date="2026-08-22", slug="demo", title="Demo", status="superseded"
        )

    assert "does not exist" in str(excinfo.value)


def test_the_create_guard_checks_the_successor_pointer_too(goal_lib, tmp_path: Path) -> None:
    """Same omission on the creation arm, which the round-2 repair had just added."""
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "goals").mkdir(parents=True)

    with pytest.raises(ValueError) as excinfo:
        goal_lib.upsert_goal(
            repo, date="2026-08-22", slug="fresh", title="Fresh", status="superseded",
            goal_body="Superseded by: charness-artifacts/goals/never-written.md",
        )

    assert "superseded" in str(excinfo.value)
