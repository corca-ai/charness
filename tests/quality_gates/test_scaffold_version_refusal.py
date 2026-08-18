"""Five scaffolds refuse an unhonored adapter declaration instead of RELOCATING the
artifact they are about to write.

This family does not degrade its answer under an unhonored declaration — it moves the
target. Measured on the real CLIs at `0bcb6b227`, one repo per skill declaring its own
`output_dir` under `version: 9`, every one returned the charness default path at exit 0:

    quality   docs/mine-quality   -> charness-artifacts/quality/latest.md
    retro     docs/mine-retro     -> charness-artifacts/retro/<date>-probe.md
    debug     docs/mine-debug     -> charness-artifacts/debug/latest.md
    critique  docs/mine-critique  -> charness-artifacts/critique/<date>-probe.md
    handoff   docs/mine           -> docs/handoff.md

Each row is measured on its own CLI, not asserted from a shared shape. The table below is
the same five stimuli, run against each surface's own `main()`.

The `handoff` row is a correction worth keeping visible: the first cut of that probe
declared `artifact_path`, which its resolver ignores — it derives the path from
`output_dir` plus a fixed filename. So the speakable-version CONTROL also returned the
default, and could not distinguish "honored the declaration" from "fell back to ours". A
control that cannot fail proves nothing, and this one was re-measured on the field the
contract actually reads.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from .support import ROOT

# `(skill, declared_output_dir, default_path_fragment)`.
SCAFFOLDS = (
    ("quality", "docs/mine-quality", "charness-artifacts/quality"),
    ("retro", "docs/mine-retro", "charness-artifacts/retro"),
    ("debug", "docs/mine-debug", "charness-artifacts/debug"),
    ("critique", "docs/mine-critique", "charness-artifacts/critique"),
    ("handoff", "docs/mine", "docs/handoff.md"),
)


def _script(skill: str) -> Path:
    return ROOT / "skills" / "public" / skill / "scripts" / f"scaffold_{skill}_artifact.py"


def _repo(tmp_path: Path, skill: str, adapter: str | None) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    if adapter is not None:
        (repo / ".agents").mkdir(parents=True, exist_ok=True)
        (repo / ".agents" / f"{skill}-adapter.yaml").write_text(adapter, encoding="utf-8")
    return repo


def _run(skill: str, repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(_script(skill)), "--repo-root", str(repo), "--title", "probe"],
        capture_output=True,
        text=True,
    )


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
    assert (
        "could not be parsed" in result.stderr
        or "unsupported YAML construct" in result.stderr
    ), result.stderr
    assert default not in result.stdout


@pytest.mark.parametrize(("skill", "declared", "default"), SCAFFOLDS, ids=[s[0] for s in SCAFFOLDS])
def test_a_speakable_version_still_writes_where_the_repo_said(
    tmp_path: Path, skill: str, declared: str, default: str
) -> None:
    """The polarity control, and the one that catches a fixture declaring a field the
    contract does not read — which is exactly what the `handoff` row did on its first
    cut. If this assertion cannot fail, the refusal above proves nothing."""
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
