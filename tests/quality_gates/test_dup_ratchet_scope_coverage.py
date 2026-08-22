"""Slice 4 ("gate by property, not by enumeration"): dup_ratchet names its own
uncovered set (tracked files outside `scope_paths`) as a computed number, in its
own output, alongside the pre-existing `degraded_reasons` axis becoming legible
as a plain boolean (`degraded`).

Covers:
- `dup_ratchet_lib.scope_coverage` (pure, path-segment-aware diff of tracked
  files against scope_paths).
- `dup_ratchet_git.tracked_files` (the git seam: `git ls-files`, or `None` when
  git cannot answer).
- `dup_ratchet_lib.evaluate`'s new `degraded` boolean.
- `check_dup_ratchet`'s CLI-layer wiring: `scope_paths`, `scope_coverage`, and
  `did_not_judge` on the real verdict payload, additive only.
"""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import yaml

from .support import ROOT, run_script

SCRIPTS = ROOT / "skills" / "public" / "quality" / "scripts"
CHECK_SCRIPT = SCRIPTS / "check_dup_ratchet.py"


def _load(name: str):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"{name}_scope_coverage_inproc", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


lib = _load("dup_ratchet_lib")
baseline_lib = _load("dup_ratchet_baseline_lib")
gitmod = _load("dup_ratchet_git")


def _evaluate(**over):
    base = dict(
        code_family_ids=set(), gate_baseline_ids=set(), doc_drift_signatures=set(),
        intentional_code_ids=set(), intentional_doc_signatures=set(),
        fixable_ceiling=0, floor_F=0, escalation_K=3,
        stagnation=0, anchor="anchorsha", anchor_is_ancestor=True, degraded_reasons=None,
    )
    base.update(over)
    return lib.evaluate(**base)


# Imported from the sibling module, NOT copied. The first cut of this file carried
# byte-identical copies of all four helpers, and a fresh-eye round pointed out the
# irony precisely: this is the slice that makes the ratchet report `tests/` as scope it
# never judges, and it shipped fresh copy-paste INTO that blind spot in the same
# change. The ratchet cannot see it, so the discipline has to.
from tests.quality_gates.test_dup_ratchet import (  # noqa: E402
    _code_inventory,
    _doc_inventory,
    _git,
    _write_json,
)


def _consumer_repo(tmp_path: Path, *, scope_paths: tuple[str, ...] = ("src",)) -> Path:
    """A minimal consumer-style fixture repo: adapter + review + baseline, no
    charness internals -- matching the shape `_consumer_repo` in test_dup_ratchet.py
    builds, scoped down to what this file's tests need."""
    repo = tmp_path / "consumer"
    (repo / ".agents").mkdir(parents=True)
    _write_json(repo / "q" / "dup-review.json", {
        "schemaVersion": "charness.quality.dup_review.v1",
        "fixable_ceiling": 0, "entries": [],
    })
    _write_json(
        repo / "q" / "dup-ratchet-baseline.json",
        baseline_lib.build_gate_baseline({"known1": ["known1"]}),
    )
    lines = [
        "version: 1", "repo: consumer", "dup_ratchet:", "  enabled: true",
        "  floor_F: 0", "  escalation_K: 10", "  scope_paths:",
    ]
    lines.extend(f"    - {path}" for path in scope_paths)
    lines.extend([
        "  review_artifact_path: q/dup-review.json",
        "  gate_baseline_path: q/dup-ratchet-baseline.json", "",
    ])
    (repo / ".agents" / "quality-adapter.yaml").write_text("\n".join(lines), encoding="utf-8")
    return repo


def _run_gate(repo: Path, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    code_json = _code_inventory(tmp_path / "code.json", ["known1"])
    doc_json = _doc_inventory(tmp_path / "doc.json", [])
    return run_script(
        str(CHECK_SCRIPT), "--repo-root", str(repo),
        "--code-inventory", str(code_json), "--doc-inventory", str(doc_json),
        "--detail", cwd=ROOT,
    )


# --------------------------------------------------------------------------- #
# dup_ratchet_lib.scope_coverage — pure
# --------------------------------------------------------------------------- #
def test_scope_coverage_counts_uncovered_files_and_respects_path_segments() -> None:
    tracked = {
        "scripts/a.py", "skills/public/x.py", "skills/public-2/y.py",
        "tests/test_a.py", "skills/shared/z.py",
    }
    coverage = lib.scope_coverage(tracked, ["scripts", "skills/public"])
    assert coverage == {
        "tracked_file_count": 5,
        "uncovered_file_count": 3,
        "uncovered_top_level": ["skills", "tests"],
    }


def test_scope_coverage_returns_none_when_tracked_files_unknown() -> None:
    assert lib.scope_coverage(None, ["scripts"]) is None


# --------------------------------------------------------------------------- #
# dup_ratchet_git.tracked_files — git seam
# --------------------------------------------------------------------------- #
def test_git_tracked_files_reads_committed_paths(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    _git(repo, "init")
    (repo / "a.py").write_text("a = 1\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "seed")
    assert gitmod.tracked_files(repo) == {"a.py"}


def test_git_tracked_files_none_outside_a_repo(tmp_path: Path) -> None:
    not_a_repo = tmp_path / "plain"
    not_a_repo.mkdir()
    assert gitmod.tracked_files(not_a_repo) is None


# --------------------------------------------------------------------------- #
# dup_ratchet_lib.evaluate — the fail-open branch's own state, legible
# --------------------------------------------------------------------------- #
def test_evaluate_verdict_carries_degraded_boolean() -> None:
    clean = _evaluate()
    assert clean["degraded"] is False

    degraded = _evaluate(degraded_reasons=["overlay missing"])
    assert degraded["degraded"] is True
    assert degraded["status"] == "degraded"
    assert degraded["ok"] is True and degraded["block"] is False


# --------------------------------------------------------------------------- #
# check_dup_ratchet CLI — additive-only wiring on a real verdict
# --------------------------------------------------------------------------- #
def test_cli_echoes_scope_paths_and_computes_uncovered_count(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, scope_paths=("src",))
    (repo / "src").mkdir(parents=True, exist_ok=True)
    (repo / "src" / "a.py").write_text("a = 1\n", encoding="utf-8")
    (repo / "tests").mkdir(parents=True, exist_ok=True)
    (repo / "tests" / "b.py").write_text("b = 1\n", encoding="utf-8")
    (repo / "docs").mkdir(parents=True, exist_ok=True)
    (repo / "docs" / "c.md").write_text("# c\n", encoding="utf-8")
    _git(repo, "init")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "seed")

    result = _run_gate(repo, tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    verdict = yaml.safe_load(result.stdout)

    assert verdict["scope_paths"] == ["src"]
    coverage = verdict["scope_coverage"]
    assert coverage["tracked_file_count"] == 6
    assert coverage["uncovered_file_count"] == 5
    assert coverage["uncovered_top_level"] == [".agents", "docs", "q", "tests"]
    assert any("5 tracked file" in entry for entry in verdict["did_not_judge"])
    # Additive only: the real verdict is untouched by sizing the gap.
    assert result.returncode == 0


def test_cli_scope_coverage_unknown_without_git_stays_honest(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, scope_paths=("src",))
    result = _run_gate(repo, tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    verdict = yaml.safe_load(result.stdout)

    assert verdict["scope_paths"] == ["src"]
    assert verdict["scope_coverage"] is None
    assert any("git could not be asked" in entry for entry in verdict["did_not_judge"])


def test_empty_scope_paths_does_not_claim_the_whole_tree_was_never_judged() -> None:
    """The branch that repaired a FALSE claim, and had no test until the gate said so.

    With `scope_paths` empty, `scope_coverage` marks every tracked file uncovered --
    but the code scan falls back to the scanner's own DEFAULT_PATHS and really does
    scan and really does form families. Rendering that as "N files this scan never
    formed a family from" is a gate added to report its gap honestly overstating it.

    The changed-line coverage gate named these exact lines as unproven, which is how
    the omission surfaced rather than by anyone noticing.
    """
    module = _load("check_dup_ratchet")
    coverage = {
        "tracked_file_count": 7785,
        "uncovered_file_count": 7785,
        "uncovered_top_level": ["scripts", "docs"],
    }

    entries, messages = module._scope_did_not_judge([], coverage)

    joined = " ".join(entries) + " " + " ".join(messages)
    assert "scanner defaults" in joined
    # It must NOT report the whole tree as never-judged, which is the false claim.
    assert "7785 tracked file(s)" not in joined
    assert "never forms a CODE family" not in joined

    # Control: with a real scope, the count IS reported and is scoped to CODE families.
    entries, messages = module._scope_did_not_judge(["scripts"], coverage)
    joined = " ".join(entries) + " " + " ".join(messages)
    assert "7785 tracked file(s)" in joined
    assert "never forms a CODE family" in joined
    assert "the doc arm scans the repo root" in joined
