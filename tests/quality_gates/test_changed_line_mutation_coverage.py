"""Targeted tests for the #260 preventive teeth.

`scripts/check_changed_line_mutation_coverage.py` reproduces the mutation gate's
*blocking* changed-line signal locally. These tests pin its wiring (base/head
resolution, eligible-pool changed-file derivation, coverage loading, exit code)
by injecting a coverage JSON via --reuse-coverage so no slow real probe runs.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from .support import ROOT, run_script

_TEETH = "scripts/check_changed_line_mutation_coverage.py"


def _load_teeth():
    spec = importlib.util.spec_from_file_location(
        "check_changed_line_mutation_coverage", ROOT / _TEETH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()


def _seed_repo_with_changed_pool_file(tmp_path: Path) -> tuple[Path, str, str]:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    foo = repo / "scripts" / "foo.py"
    foo.write_text("def a():\n    return 1\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    base = _git(repo, "rev-parse", "HEAD")
    # add a new function -> changed lines 3-6 (def b / return 2 are statements)
    foo.write_text("def a():\n    return 1\n\n\ndef b():\n    return 2\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "head")
    head = _git(repo, "rev-parse", "HEAD")
    return repo, base, head


def _write_coverage(repo: Path, *, executed: list[int], missing: list[int]) -> Path:
    cov = repo / "coverage.json"
    cov.write_text(
        json.dumps({"files": {"scripts/foo.py": {"executed_lines": executed, "missing_lines": missing}}}),
        encoding="utf-8",
    )
    return cov


def _run(repo: Path, base: str, head: str, cov: Path) -> subprocess.CompletedProcess[str]:
    return run_script(
        _TEETH,
        "--repo-root", str(repo),
        "--base-sha", base,
        "--head-sha", head,
        "--reuse-coverage",
        "--coverage-json", str(cov),
    )


def test_flags_uncovered_changed_lines(tmp_path: Path) -> None:
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    cov = _write_coverage(repo, executed=[1, 2], missing=[5, 6])  # def b left uncovered

    result = _run(repo, base, head, cov)

    assert result.returncode == 1, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "scripts/foo.py" in payload["blocking"]
    assert payload["blocking_detail"]["scripts/foo.py"]["changed_and_missing"] == [5, 6]
    assert payload["blocking_targets"]["scripts/foo.py"] == [
        {"line": 5, "source": "def b():"},
        {"line": 6, "source": "return 2"},
    ]
    assert payload["targeted_mutant_proof"]["required"] is True
    assert "mutate that exact line" in payload["targeted_mutant_proof"]["contract"]


def test_passes_when_changed_lines_are_covered(tmp_path: Path) -> None:
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    cov = _write_coverage(repo, executed=[1, 2, 5, 6], missing=[])

    result = _run(repo, base, head, cov)

    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["blocking"] == []


def test_untracked_changed_file_blocks(tmp_path: Path) -> None:
    # A changed pool file the suite never tracks (no coverage entry) blocks — the
    # check_goal_artifact subprocess-only / 0%-coverage case from #260.
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    cov = repo / "coverage.json"
    cov.write_text(json.dumps({"files": {}}), encoding="utf-8")

    result = _run(repo, base, head, cov)

    assert result.returncode == 1, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert "scripts/foo.py" in payload["blocking"]
    assert "not tracked" in str(payload["blocking_detail"]["scripts/foo.py"])
    assert payload["blocking_targets"]["scripts/foo.py"] == [
        {"line": 5, "source": "def b():"},
        {"line": 6, "source": "return 2"},
    ]


def test_no_base_sha_is_non_blocking_by_construction(tmp_path: Path) -> None:
    # Mirrors workflow_dispatch (#251 B1): with no base SHA the changed-line
    # classifier returns nothing, so the teeth passes by construction.
    repo, _base, _head = _seed_repo_with_changed_pool_file(tmp_path)

    result = run_script(_TEETH, "--repo-root", str(repo), "--base-sha", "", "--reuse-coverage")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["blocking"] == []
    assert "no base_sha" in payload["reason"]


def test_resolves_relative_coverage_json_under_repo_root(tmp_path: Path) -> None:
    # A RELATIVE --coverage-json resolves as repo_root / args.coverage_json (the
    # is_absolute() else-branch). The other tests pass absolute paths, so without
    # this the Path-division mutants on that line survive (any non-`/` operator on
    # two Paths raises TypeError).
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    (repo / "reports").mkdir()
    (repo / "reports" / "cov.json").write_text(
        json.dumps({"files": {"scripts/foo.py": {"executed_lines": [1, 2, 5, 6], "missing_lines": []}}}),
        encoding="utf-8",
    )

    result = run_script(
        _TEETH, "--repo-root", str(repo), "--base-sha", base, "--head-sha", head,
        "--reuse-coverage", "--coverage-json", "reports/cov.json",  # relative -> repo_root/reports/cov.json
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["blocking"] == []


def test_passes_when_no_eligible_pool_file_changed(tmp_path: Path) -> None:
    # A range whose only change is a non-pool file (e.g. docs/*.md) yields an
    # empty eligible-changed set, so the teeth short-circuits to clean.
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    (repo / "docs" / "note.md").write_text("base\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    base = _git(repo, "rev-parse", "HEAD")
    (repo / "docs" / "note.md").write_text("base\nmore\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "head")
    head = _git(repo, "rev-parse", "HEAD")

    result = run_script(
        _TEETH, "--repo-root", str(repo), "--base-sha", base, "--head-sha", head, "--reuse-coverage"
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["blocking"] == []
    assert "no eligible" in payload["reason"]


def test_skip_if_no_coverage_is_non_blocking_when_absent(tmp_path: Path) -> None:
    # Pre-push (read-only) wiring: a changed pool file with NO coverage source must
    # skip non-blocking rather than fall through to the slow probe. This is what
    # keeps run-quality.sh --read-only cheap at the pre-push boundary.
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    absent = repo / "reports" / "mutation" / "test-coverage.json"  # never written

    result = run_script(
        _TEETH, "--repo-root", str(repo), "--base-sha", base, "--head-sha", head,
        "--reuse-coverage", "--skip-if-no-coverage", "--coverage-json", str(absent),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["blocking"] == []
    assert "no coverage source" in payload["reason"]


def test_skip_if_no_coverage_still_blocks_when_present(tmp_path: Path) -> None:
    # --skip-if-no-coverage only skips when coverage is ABSENT; when a coverage
    # source exists the teeth still fire on an uncovered changed line (AC-WIRE at
    # the reproducer level — the consumer keeps its teeth once the producer runs).
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    cov = _write_coverage(repo, executed=[1, 2], missing=[5, 6])  # def b left uncovered

    result = run_script(
        _TEETH, "--repo-root", str(repo), "--base-sha", base, "--head-sha", head,
        "--reuse-coverage", "--skip-if-no-coverage", "--coverage-json", str(cov),
    )

    assert result.returncode == 1, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "scripts/foo.py" in payload["blocking"]


def _fingerprint(repo: Path, base: str) -> str:
    return _load_teeth().changed_pool_fingerprint(repo, base)


def _marker_path(cov: Path) -> Path:
    return cov.with_name(cov.name + ".fingerprint")


def test_require_fresh_coverage_skips_when_marker_absent(tmp_path: Path) -> None:
    # A coverage source with NO `.fingerprint` marker is treated as stale: the
    # pre-push teeth skip non-blocking rather than trust coverage that may predate
    # the changed lines (the stale-coverage false-positive class found in the
    # wiring smoke). Without this guard a stale reports/mutation/test-coverage.json
    # would block a legitimate push.
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    cov = _write_coverage(repo, executed=[1, 2], missing=[5, 6])  # would block if trusted
    # no <cov>.fingerprint marker written

    result = run_script(
        _TEETH, "--repo-root", str(repo), "--base-sha", base, "--head-sha", head,
        "--reuse-coverage", "--require-fresh-coverage", "--coverage-json", str(cov),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["blocking"] == []
    assert "stale" in payload["reason"]


def test_require_fresh_coverage_skips_when_marker_mismatched(tmp_path: Path) -> None:
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    cov = _write_coverage(repo, executed=[1, 2], missing=[5, 6])
    _marker_path(cov).write_text("0" * 64, encoding="utf-8")  # wrong fingerprint

    result = run_script(
        _TEETH, "--repo-root", str(repo), "--base-sha", base, "--head-sha", head,
        "--reuse-coverage", "--require-fresh-coverage", "--coverage-json", str(cov),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "stale" in json.loads(result.stdout)["reason"]


def test_require_fresh_coverage_fires_when_marker_matches_fingerprint(tmp_path: Path) -> None:
    # The freshness guard does NOT defang the teeth: a coverage source whose
    # `.fingerprint` marker matches the current changed-pool content still blocks
    # an uncovered changed line (AC-WIRE — fresh coverage keeps its teeth).
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    cov = _write_coverage(repo, executed=[1, 2], missing=[5, 6])  # def b uncovered
    _marker_path(cov).write_text(_fingerprint(repo, base), encoding="utf-8")

    result = run_script(
        _TEETH, "--repo-root", str(repo), "--base-sha", base, "--head-sha", head,
        "--reuse-coverage", "--require-fresh-coverage", "--coverage-json", str(cov),
    )

    assert result.returncode == 1, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "scripts/foo.py" in payload["blocking"]


def test_write_fresh_marker_stamps_coverage_fingerprint(tmp_path: Path, monkeypatch) -> None:
    # Producer mode (closeout): after coverage is produced, write the
    # `<coverage-json>.fingerprint` marker = the changed-pool content fingerprint
    # so the pre-push consumer's --require-fresh-coverage can later trust it. The
    # producer probe drops dynamic_context (lever A), so the stub records the kwarg.
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    teeth = _load_teeth()
    cov_path = repo / "reports" / "mutation" / "test-coverage.json"
    seen = {}

    def fake_probe(repo_root, test_command, coverage_json, *, dynamic_context=True) -> None:
        seen["dynamic_context"] = dynamic_context
        Path(coverage_json).parent.mkdir(parents=True, exist_ok=True)
        Path(coverage_json).write_text(
            json.dumps({"files": {"scripts/foo.py": {"executed_lines": [1, 2, 5, 6], "missing_lines": []}}}),
            encoding="utf-8",
        )

    monkeypatch.setattr(teeth, "run_test_coverage", fake_probe)
    monkeypatch.setattr(teeth, "read_test_command", lambda config: "python3 -m pytest -q")
    monkeypatch.setattr(
        sys,
        "argv",
        ["teeth", "--repo-root", str(repo), "--base-sha", base, "--head-sha", head,
         "--coverage-json", str(cov_path), "--write-fresh-marker"],
    )

    rc = teeth.main()

    assert rc == 0
    assert seen["dynamic_context"] is False, "producer drops dynamic_context (lever A)"
    marker = _marker_path(cov_path)
    assert marker.is_file(), "producer must write the .fingerprint marker"
    assert marker.read_text(encoding="utf-8").strip() == _fingerprint(repo, base)


def test_runs_coverage_probe_when_not_reusing(tmp_path: Path, monkeypatch) -> None:
    # Covers the run-the-probe branch (the default, no --reuse-coverage): the
    # heavy gate probe + config read are stubbed so the test stays fast while the
    # branch executes and the produced coverage drives a clean verdict. Without
    # --write-fresh-marker the consumer probe keeps dynamic_context (the faithful
    # path).
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    teeth = _load_teeth()
    called = {}

    def fake_probe(repo_root, test_command, coverage_json, *, dynamic_context=True) -> None:
        called["probe"] = True
        called["dynamic_context"] = dynamic_context
        Path(coverage_json).parent.mkdir(parents=True, exist_ok=True)
        Path(coverage_json).write_text(
            json.dumps({"files": {"scripts/foo.py": {"executed_lines": [1, 2, 5, 6], "missing_lines": []}}}),
            encoding="utf-8",
        )

    monkeypatch.setattr(teeth, "run_test_coverage", fake_probe)
    monkeypatch.setattr(teeth, "read_test_command", lambda config: "python3 -m pytest -q")
    monkeypatch.setattr(
        sys,
        "argv",
        ["teeth", "--repo-root", str(repo), "--base-sha", base, "--head-sha", head,
         "--coverage-json", str(repo / "cov.json")],
    )

    rc = teeth.main()

    assert called.get("probe") is True  # the run-the-probe branch executed
    assert called["dynamic_context"] is True
    assert rc == 0
