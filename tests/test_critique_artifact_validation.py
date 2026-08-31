from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import pytest

from tests.quality_gates.repo_shapes import install_committed_repo
from tests.quality_gates.support import run_script

ROOT = Path(__file__).resolve().parents[1]

ARTIFACT_RELPATH = "charness-artifacts/critique/2026-06-12-demo-critique.md"





def seed_repo(tmp_path: Path, artifact_body: str) -> Path:
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "critique").mkdir(parents=True)
    (repo / ARTIFACT_RELPATH).write_text(artifact_body, encoding="utf-8")
    return repo


def _multi_violation_artifact() -> str:
    # Breaks two independent checks at once: an unknown structured-finding bin
    # and an unknown reviewer-tier host exposure state. Used to exercise
    # default one-pass vs fail-fast.
    return (
        "\n".join(
            [
                "# Critique Review",
                "Date: 2026-06-12",
                "",
                "## Decision Under Review",
                "",
                "demo decision",
                "",
                "## Structured Findings",
                "",
                "- F1 | bin: bogus-bin | evidence: strong | ref: scripts/demo.py | action: fix | note: demo",
                "",
                "## Reviewer Tier Evidence",
                "",
                "- Requested tier: high-leverage",
                "- Requested spawn fields: none sent",
                "- Host exposure state: bogus-state",
                "- Application state: pending",
                "",
                "## Fresh-Eye Satisfaction",
                "",
                "parent-delegated; reviewer completed the assigned lens.",
                "",
            ]
        )
        + "\n"
    )


def _load_module(relpath: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relpath)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_live_agents_md_does_not_claim_the_legacy_delegation_contract() -> None:
    """The current root contract uses live host capability, not a prose grant.

    The critique validator still understands the explicit delegation record for
    consuming repositories, but this repository's AGENTS.md no longer adopts
    the retired repo-mandated fresh-eye marker. That keeps the test tied to the
    live root contract instead of preserving an obsolete ceremony by fixture.
    """
    validator = _load_module("scripts/validate_critique_artifacts.py", "_vca_real")
    assert validator.has_repo_delegation_contract(ROOT) is False


def test_both_readers_of_the_delegation_contract_agree_on_this_repo() -> None:
    """One contract, two readers, deliberately duplicated text -- pin the parity.

    `issue_critique_observer` restates the markers instead of importing them (it
    is a portable public skill and must not reach into this repo's `scripts/`).
    That duplication is intentional, but it is exactly how the two drifted: the
    observer carried the markup-flattening repair while the validator did not,
    and for that window one reader said this repo had adopted the contract and
    the other said it had not.
    """
    validator = _load_module("scripts/validate_critique_artifacts.py", "_vca_parity")
    observer = _load_module("skills/public/issue/scripts/issue_critique_observer.py", "_ico_parity")
    assert validator.DELEGATION_CONTRACT_MARKERS == observer.DELEGATION_CONTRACT_MARKERS
    assert validator.has_repo_delegation_contract(ROOT) == observer.repo_requires_delegated_observer(ROOT)


def test_delegation_contract_absent_repo_is_not_held_to_it(tmp_path: Path) -> None:
    """The flattening widens MATCHING, not the POPULATION.

    The near-miss case is the one worth pinning, and it is the one that actually
    exercises the flattening path against a non-adopting repo: a repo whose
    AGENTS.md carries the `## Subagent Delegation` heading (marker 1) but never
    the contract sentence (marker 2) must still read False. A repo with no
    AGENTS.md at all returns at the `is_file()` guard without reaching the
    matcher, so on its own it pins nothing about this change.
    """
    validator = _load_module("scripts/validate_critique_artifacts.py", "_vca_absent")
    agents = tmp_path / "AGENTS.md"
    assert validator.has_repo_delegation_contract(tmp_path) is False  # no file at all
    agents.write_text("# Some repo\n\nNo delegation contract here.\n", encoding="utf-8")
    assert validator.has_repo_delegation_contract(tmp_path) is False  # neither marker
    # Marker 1 present and bolded, marker 2 absent -- `all()` must still refuse.
    # This case pins `all()`, NOT the flattening: the assertion is negative, so it
    # also holds for an implementation that never flattens at all.
    agents.write_text(
        "# Some repo\n\n## **Subagent** _Delegation_\n\nWe spawn reviewers ad hoc.\n",
        encoding="utf-8",
    )
    assert validator.has_repo_delegation_contract(tmp_path) is False


def test_delegation_contract_matches_through_inline_markup(tmp_path: Path) -> None:
    """The POSITIVE case that actually witnesses the flattening.

    A synthetic repo carrying BOTH markers wrapped in emphasis must read True.
    This is the assertion that discriminates: it fails if the flattening is
    removed (the markup blocks the match) and it fails if the flattening is too
    aggressive and also collapses whitespace (`subagentdelegation` no longer
    contains `subagent delegation`). The negative cases above can do neither.
    """
    validator = _load_module("scripts/validate_critique_artifacts.py", "_vca_markup")
    (tmp_path / "AGENTS.md").write_text(
        "# Repo\n\n## **Subagent** _Delegation_\n\n"
        "- Repo-mandated bounded fresh-eye subagent reviews are **already delegated** by contract.\n",
        encoding="utf-8",
    )
    assert validator.has_repo_delegation_contract(tmp_path) is True


def test_delegation_contract_unreadable_agents_md_is_not_adopted(tmp_path: Path) -> None:
    """Unreadable is not adopted, and must not escape as a bare OSError.

    `is_file()` can pass on a file the process cannot read. The sibling reader
    already returned False here; without the matching guard the validator raised
    OSError instead -- which is not a ValidationError, so the run's handler would
    not render it as a validation failure at all.
    """
    validator = _load_module("scripts/validate_critique_artifacts.py", "_vca_unreadable")
    agents = tmp_path / "AGENTS.md"
    agents.write_text("## Subagent Delegation\n", encoding="utf-8")
    agents.chmod(0o000)
    try:
        if os.access(agents, os.R_OK):  # running as root: the mode is not enforced
            pytest.skip("cannot make a file unreadable for this user")
        assert validator.has_repo_delegation_contract(tmp_path) is False
    finally:
        agents.chmod(0o644)


def test_validate_critique_artifact_fail_fast_stops_at_first_violation(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, _multi_violation_artifact())
    result = run_script(
        str(ROOT / "scripts" / "validate_critique_artifacts.py"),
        "--repo-root",
        str(repo),
        "--paths",
        ARTIFACT_RELPATH,
        "--fail-fast",
    )
    assert result.returncode == 1
    assert "unknown bin `bogus-bin`" in result.stderr
    assert "rule violation(s)" not in result.stderr
    assert "host exposure state" not in result.stderr


def test_validate_critique_artifact_default_mode_lists_every_violation(tmp_path: Path) -> None:
    # D28 polarity unification: one-pass is now the DEFAULT here too.
    repo = seed_repo(tmp_path, _multi_violation_artifact())
    result = run_script(
        str(ROOT / "scripts" / "validate_critique_artifacts.py"),
        "--repo-root",
        str(repo),
        "--paths",
        ARTIFACT_RELPATH,
    )
    assert result.returncode == 1
    assert "rule violation(s)" in result.stderr
    assert "unknown bin `bogus-bin`" in result.stderr
    assert "host exposure state `bogus-state`" in result.stderr


def test_empty_artifact_set_does_not_run_the_cross_surface_probe(tmp_path: Path) -> None:
    """A commit touching no critique artifact stays a cheap silent pass.

    The shared runner builds the per-run validate factory, and critique's factory
    resolves the cross-surface probe by shelling out to git. With zero artifacts
    that work is pure cost -- and an unresolvable base sha (shallow clone,
    grafted history) raises SurfaceError, which is not a ValidationError, so it
    would turn a silent pass into an uncaught traceback.
    """
    repo = install_committed_repo(tmp_path / "repo", {"README.md": "seed\n"}, message="init")
    result = run_script(
        str(ROOT / "scripts" / "validate_critique_artifacts.py"),
        "--repo-root",
        str(repo),
        "--changed-ref",
        "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef..HEAD",
    )
    assert result.returncode == 0, result.stderr
    assert "Validated 0 critique artifact(s)." in result.stdout
