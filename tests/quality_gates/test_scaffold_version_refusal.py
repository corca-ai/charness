"""Four scaffolds refuse an unhonored adapter declaration instead of RELOCATING the
artifact they are about to write.

This family does not degrade its answer under an unhonored declaration — it moves the
target. Measured on the real CLIs at `0bcb6b227`, one repo per skill declaring its own
`output_dir` under `version: 9`, every one returned the charness default path at exit 0:

    quality   docs/mine-quality   -> charness-artifacts/quality/latest.md
    retro     docs/mine-retro     -> charness-artifacts/retro/<date>-probe.md
    debug     docs/mine-debug     -> charness-artifacts/debug/latest.md
    critique  docs/mine-critique  -> charness-artifacts/critique/<date>-probe.md

Each row is measured on its own CLI, not asserted from a shared shape. The table below is
the same five stimuli, run against each surface's own `main()`.

"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from .support import ROOT, run_script

# `(skill, declared_output_dir, default_path_fragment)`.
SCAFFOLDS = (
    ("quality", "docs/mine-quality", "charness-artifacts/quality"),
    ("retro", "docs/mine-retro", "charness-artifacts/retro"),
    ("debug", "docs/mine-debug", "charness-artifacts/debug"),
    ("critique", "docs/mine-critique", "charness-artifacts/critique"),
)


# The five paths, LITERAL. Not decoration: `suggest_mutation_coverage_command` maps a
# source file to the standing tests that reference it BY NAME, and the first cut of this
# file built every path from an f-string. It referenced none of them, so the mapper could
# not see it, so the changed-line producer ran a test subset that excluded it and reported
# all five `raise SystemExit(refusal)` lines uncovered — while the suite was green and the
# lines were, in fact, exercised. A test the mapper cannot see is a test the coverage lane
# does not have. `test_the_script_table_matches_the_derived_paths` keeps this honest.
SCRIPT_PATHS = {
    "quality": "skills/public/quality/scripts/scaffold_quality_artifact.py",
    "retro": "skills/public/retro/scripts/scaffold_retro_artifact.py",
    "debug": "skills/public/debug/scripts/scaffold_debug_artifact.py",
    "critique": "skills/public/critique/scripts/scaffold_critique_artifact.py",
}


def _script(skill: str) -> Path:
    return ROOT / SCRIPT_PATHS[skill]


def test_the_script_table_matches_the_derived_paths() -> None:
    """The table above exists so a name-based mapper can see this file, so it must stay
    true. Deriving the paths instead would restore the invisibility it fixes."""
    for skill in SCRIPT_PATHS:
        assert _script(skill).is_file(), skill
        assert _script(skill).name == f"scaffold_{skill}_artifact.py"
    assert set(SCRIPT_PATHS) == {row[0] for row in SCAFFOLDS}


def _repo(tmp_path: Path, skill: str, adapter: str | None) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    if adapter is not None:
        (repo / ".agents").mkdir(parents=True, exist_ok=True)
        (repo / ".agents" / f"{skill}-adapter.yaml").write_text(adapter, encoding="utf-8")
    return repo


def _run(skill: str, repo: Path) -> subprocess.CompletedProcess:
    return run_script(str(_script(skill)), "--repo-root", str(repo), "--title", "probe")


@pytest.mark.parametrize(("skill", "declared", "default"), SCAFFOLDS, ids=[s[0] for s in SCAFFOLDS])
def test_an_unhonored_declaration_refuses_rather_than_relocating(
    tmp_path: Path, skill: str, declared: str, default: str
) -> None:
    repo = _repo(tmp_path, skill, f"version: 9\nrepo: demo\noutput_dir: {declared}\n")
    result = _run(skill, repo)
    assert result.returncode == 1, result.stdout
    assert "does not speak" in result.stderr
    assert f"{skill}-adapter.yaml" in result.stderr
    # The relocation must not be reported alongside the refusal.
    assert default not in result.stdout


@pytest.mark.parametrize(("skill", "declared", "default"), SCAFFOLDS, ids=[s[0] for s in SCAFFOLDS])
def test_a_parser_refusal_refuses_at_the_same_place(
    tmp_path: Path, skill: str, declared: str, default: str
) -> None:
    """The second door, the one round 2 of this slice found escaping five guards.

    TWO SHAPES, and the difference is recorded rather than smoothed over. Three of these
    five reach a resolver that CATCHES the parse failure and records it in `errors`, so
    they render this repo's `could not be parsed` refusal. `quality` and `critique` reach
    one that lets the `ValueError` out, so they refuse with a raw TRACEBACK.

    Both stop the run and neither relocates the artifact, which is this row's claim. The
    traceback is a worse operator experience and is a REAL residual — it is named in this
    row's probe record's non-claims and filed rather than silently accepted here, because
    widening the fix to that resolver is a different change than the one this row makes.
    """
    repo = _repo(tmp_path, skill, f"version: !!int 9\nrepo: demo\noutput_dir: {declared}\n")
    result = _run(skill, repo)
    assert result.returncode != 0, result.stdout
    # KEYED ON THE SKILL, not a disjunction. A round-1 bounded review over these rows
    # pointed out that `A or B` for all five leaves the published "two of five" count
    # unfalsifiable: fix `quality`'s resolver or regress `retro`'s and the test stays
    # green while the record drifts. This asserts which surface renders which shape.
    # CONVERGED by `#673`. The keyed branch this replaces was right to refuse a
    # disjunction -- `A or B` for all five left the published "two of five" count
    # unfalsifiable -- and it is now a single shape asserted for all five, which is
    # falsifiable in the same way: regress any one resolver and its case fails alone.
    assert "could not be parsed" in result.stderr, result.stderr
    assert "Traceback" not in result.stderr, result.stderr
    # Empty, not merely free of the default path: the refusal raises before any emit, so
    # `default not in stdout` was near-vacuous against a blank stream.
    assert result.stdout.strip() == "", result.stdout


@pytest.mark.parametrize(("skill", "declared", "default"), SCAFFOLDS, ids=[s[0] for s in SCAFFOLDS])
def test_a_speakable_version_still_writes_where_the_repo_said(
    tmp_path: Path, skill: str, declared: str, default: str
) -> None:
    """The polarity control. If this assertion cannot fail, the refusal above proves
    nothing."""
    repo = _repo(tmp_path, skill, f"version: 1\nrepo: demo\noutput_dir: {declared}\n")
    result = _run(skill, repo)
    assert result.returncode == 0, result.stderr
    assert declared in result.stdout, result.stdout


@pytest.mark.parametrize(("skill", "declared", "default"), SCAFFOLDS, ids=[s[0] for s in SCAFFOLDS])
def test_no_adapter_at_all_is_not_a_refusal(
    tmp_path: Path, skill: str, declared: str, default: str
) -> None:
    """These are opt-in surfaces. A repo that declared nothing is not a repo whose
    declaration could not be read, and refusing it would break every consumer that never
    wrote an adapter."""
    repo = _repo(tmp_path, skill, None)
    result = _run(skill, repo)
    assert result.returncode == 0, result.stderr
    assert default in result.stdout, result.stdout


@pytest.mark.parametrize(("skill", "declared", "default"), SCAFFOLDS, ids=[s[0] for s in SCAFFOLDS])
def test_payload_for_itself_raises_in_process(
    tmp_path: Path, skill: str, declared: str, default: str
) -> None:
    """The same refusal, IN PROCESS.

    The four tests above drive each real CLI through `subprocess`, which is the right
    shape for a behavioral claim and the wrong shape for coverage: the changed-line proof
    reported `status: blocked` with `raise SystemExit(refusal)` uncovered in all five
    files, because nothing it can see ever executed that line. A guard whose refusal line
    the suite cannot observe is a guard a refactor can delete quietly.

    This also proves the guard is inside `payload_for` rather than `main()`. That matters
    for retro and debug, whose `payload_for` IS called by `plan_retro_run` and
    `plan_debug_run`; for quality and critique the only importers are tests, and
    a round-1 bounded review over these rows refuted the claim that said otherwise.
    """
    from tests.script_main import load_script_module

    module = load_script_module(f"scaffold_{skill}_for_refusal_coverage", _script(skill))
    repo = _repo(tmp_path, skill, f"version: 9\nrepo: demo\noutput_dir: {declared}\n")
    with pytest.raises(SystemExit) as excinfo:
        module.payload_for(repo, title="probe")
    assert "does not speak" in str(excinfo.value)


@pytest.mark.parametrize(
    ("planner", "skill"),
    [
        ("skills/public/retro/scripts/plan_retro_run.py", "retro"),
        ("skills/public/debug/scripts/plan_debug_run.py", "debug"),
    ],
)
def test_the_planner_behavior_change_this_slice_caused_is_pinned(
    tmp_path: Path, planner: str, skill: str
) -> None:
    """A COLLATERAL behavior change these rows made outside their own files, found by a
    bounded review and pinned here so it cannot drift back unnoticed.

    `plan_retro_run` and `plan_debug_run` call the guarded `payload_for` before building
    their envelope. Before these rows, an unhonored declaration produced a full diagnostic
    plan at exit 1 — `ok: false`, an `adapter-readiness` gate packet with `status: fail`,
    and a `references/adapter-contract.md` required read — while ALSO carrying a
    `write_artifact_path` computed from charness defaults. Now it produces the guard's
    one-line refusal at exit 1 and no plan at all.

    Exit code unchanged; the defaulted path no longer leaks; the diagnostic is gone.
    Whether to restore the diagnostic for this input class is an operator design call,
    staged in the goal's decision queue. This test asserts the SHAPE that ships today.
    """
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    for version, expected in (("9", "does not speak"), ("!!int 9", "could not be parsed")):
        (repo / ".agents" / f"{skill}-adapter.yaml").write_text(
            f"version: {version}\nrepo: demo\noutput_dir: docs/mine-{skill}\n", encoding="utf-8"
        )
        result = subprocess.run(
            [sys.executable, str(ROOT / planner), "--repo-root", str(repo)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1, result.stdout
        assert expected in result.stderr, result.stderr
        # `stdout.strip() == ""` rather than two absent tokens. A round-2 bounded review
        # pointed out that asserting `"adapter-readiness" not in stdout` is satisfied by a
        # degraded plan that merely drops that packet — so the published claim ("no plan at
        # all") was weaker than its pin. `build_plan` raises before `emit_yaml`, so the
        # exact claim is directly assertable.
        assert result.stdout.strip() == "", result.stdout
    # Both doors, because the collateral-change claim is stated unconditionally in the
    # census reasons, the probe non-claim and the operator decision queue.
