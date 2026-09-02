"""Targeted tests for the #260 preventive teeth.

`scripts/mutation/check_changed_line_mutation_coverage.py` reproduces the mutation gate's
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

import yaml

from scripts.mutation.mutation_changed_files_lib import (
    CHANGED_LINE_COVERAGE_MARKER_SCHEMA,
    CHANGED_LINE_COVERAGE_PRODUCER,
    changed_line_coverage_marker_path,
)

from .changed_line_mutation_fixtures import (
    git as _git,
)
from .changed_line_mutation_fixtures import (
    seed_repo_with_changed_pool_file as _seed_repo_with_changed_pool_file,
)
from .seeding_support import seed_two_changed_pool_files
from .support import ROOT, run_script

_TEETH = "scripts/mutation/check_changed_line_mutation_coverage.py"


def _load_teeth():
    spec = importlib.util.spec_from_file_location(
        "check_changed_line_mutation_coverage", ROOT / _TEETH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_coverage(repo: Path, *, executed: list[int], missing: list[int]) -> Path:
    cov = repo / "coverage.json"
    cov.write_text(
        json.dumps(
            {"files": {"scripts/foo.py": {"executed_lines": executed, "missing_lines": missing}}}
        ),
        encoding="utf-8",
    )
    return cov


def _run(
    repo: Path,
    base: str,
    head: str,
    cov: Path,
    *,
    real_process: bool = False,
) -> subprocess.CompletedProcess[str]:
    return run_script(
        _TEETH,
        "--repo-root",
        str(repo),
        "--base-sha",
        base,
        "--head-sha",
        head,
        "--reuse-coverage",
        "--coverage-json",
        str(cov),
        real_process=real_process,
    )


def _write_two_file_coverage(repo: Path) -> Path:
    """foo's new lines covered, bar's not — bar stands in for the file whose tests
    were outside the focused subset."""
    cov = repo / "coverage.json"
    cov.write_text(
        json.dumps(
            {
                "files": {
                    "scripts/foo.py": {"executed_lines": [1, 2, 5, 6], "missing_lines": []},
                    "scripts/bar.py": {"executed_lines": [1, 2], "missing_lines": [5, 6]},
                }
            }
        ),
        encoding="utf-8",
    )
    return cov


def test_flags_uncovered_changed_lines(tmp_path: Path) -> None:
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    cov = _write_coverage(repo, executed=[1, 2], missing=[5, 6])  # def b left uncovered

    result = _run(repo, base, head, cov, real_process=True)

    assert result.returncode == 1, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
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
    assert yaml.safe_load(result.stdout)["blocking"] == []


def test_untracked_changed_file_blocks(tmp_path: Path) -> None:
    # A changed pool file the suite never tracks (no coverage entry) blocks — the
    # check_goal_artifact subprocess-only / 0%-coverage case from #260.
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    cov = repo / "coverage.json"
    cov.write_text(json.dumps({"files": {}}), encoding="utf-8")

    result = _run(repo, base, head, cov)

    assert result.returncode == 1, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert "scripts/foo.py" in payload["blocking"]
    assert "not tracked" in str(payload["blocking_detail"]["scripts/foo.py"])
    assert payload["blocking_targets"]["scripts/foo.py"] == [
        {"line": 5, "source": "def b():"},
        {"line": 6, "source": "return 2"},
    ]


def test_no_base_sha_is_non_blocking_by_construction(tmp_path: Path) -> None:
    # Mirrors workflow_dispatch (#251 B1): with no base SHA the changed-line
    # classifier returns nothing, so the teeth passes by construction. Since
    # #358 the verdict is loud: the payload carries a machine-readable
    # `changed_line_proof` bit and stderr names the false-proof class, so an
    # `ok: true` here can no longer be silently read as changed-line proof.
    repo, _base, _head = _seed_repo_with_changed_pool_file(tmp_path)

    result = run_script(_TEETH, "--repo-root", str(repo), "--base-sha", "", "--reuse-coverage")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is True
    assert payload["blocking"] == []
    assert "no base_sha" in payload["reason"]
    assert payload["changed_line_proof"] == "not-provable"
    assert "mutation-dispatch-no-base-sha-false-proof" in result.stderr
    assert "check_mutation_run_proof.py" in result.stderr


def test_resolves_relative_coverage_json_under_repo_root(tmp_path: Path) -> None:
    # A RELATIVE --coverage-json resolves as repo_root / args.coverage_json (the
    # is_absolute() else-branch). The other tests pass absolute paths, so without
    # this the Path-division mutants on that line survive (any non-`/` operator on
    # two Paths raises TypeError).
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    (repo / "reports").mkdir()
    (repo / "reports" / "cov.json").write_text(
        json.dumps(
            {"files": {"scripts/foo.py": {"executed_lines": [1, 2, 5, 6], "missing_lines": []}}}
        ),
        encoding="utf-8",
    )

    result = run_script(
        _TEETH,
        "--repo-root",
        str(repo),
        "--base-sha",
        base,
        "--head-sha",
        head,
        "--reuse-coverage",
        "--coverage-json",
        "reports/cov.json",  # relative -> repo_root/reports/cov.json
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert yaml.safe_load(result.stdout)["blocking"] == []


def test_passes_when_no_eligible_pool_file_changed(tmp_path: Path) -> None:
    # A range whose only change is a non-pool file (e.g. docs/*.md) yields an
    # empty eligible-changed set, so the teeth short-circuits to clean.
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    _git(repo, "init", "-q")
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
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is True
    assert payload["blocking"] == []
    assert "no eligible" in payload["reason"]


# Exit 3 = "ran, established nothing": non-blocking like exit 0, but the runner
# renders it UNPROVEN and counts it in neither column. Every assertion below used
# to pin exit 0 on a path its own test name calls a skip, a refusal, or unverified.
UNESTABLISHED_EXIT = 3


def test_skip_if_no_coverage_is_non_blocking_when_absent(tmp_path: Path) -> None:
    # A direct diagnostic with NO coverage source must remain honest without
    # accidentally running the slow producer.
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    absent = repo / "reports" / "mutation" / "test-coverage.json"  # never written

    result = run_script(
        _TEETH,
        "--repo-root",
        str(repo),
        "--base-sha",
        base,
        "--head-sha",
        head,
        "--reuse-coverage",
        "--skip-if-no-coverage",
        "--coverage-json",
        str(absent),
    )

    assert result.returncode == UNESTABLISHED_EXIT, (
        "this run established nothing about a non-empty changed set; exit 0 printed "
        "PASS beside the payload that said so"
    )
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is True
    assert payload["blocking"] == []
    assert "no coverage source" in payload["reason"]
    # #335 recurrence reduction: an unverified skip while eligible files changed is
    # surfaced loudly (non-blocking) instead of reading as a clean pass.
    assert payload["coverage_not_verified"] is True
    assert "scripts/foo.py" in payload["changed_eligible_files"]
    assert "WARNING (changed-line mutation gate)" in result.stderr
    assert "NOT verified for coverage" in result.stderr
    assert "suggest_mutation_coverage_command.py" in result.stderr
    assert "release_changed_line_coverage.py" in result.stderr


def test_coverage_not_verified_warning_names_files_and_fix() -> None:
    # #335: the obligation tripwire names the unverified files, the recurrence, and
    # the exact producer command to run before the change lands.
    teeth = _load_teeth()
    msg = teeth.coverage_not_verified_warning(
        ["scripts/foo.py", "scripts/bar.py"], "no coverage source at reports/mutation/x.json"
    )
    assert "2 eligible mutation-pool file(s) changed" in msg
    assert "NOT verified for coverage" in msg
    assert "#335 recurrence" in msg
    assert "suggest_mutation_coverage_command.py" in msg
    assert "release_changed_line_coverage.py" in msg
    assert "scripts/foo.py" in msg and "scripts/bar.py" in msg


def test_skip_if_no_coverage_still_blocks_when_present(tmp_path: Path) -> None:
    # --skip-if-no-coverage only skips when coverage is ABSENT; when a coverage
    # source exists the teeth still fire on an uncovered changed line (AC-WIRE at
    # the reproducer level — the consumer keeps its teeth once the producer runs).
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    cov = _write_coverage(repo, executed=[1, 2], missing=[5, 6])  # def b left uncovered

    result = run_script(
        _TEETH,
        "--repo-root",
        str(repo),
        "--base-sha",
        base,
        "--head-sha",
        head,
        "--reuse-coverage",
        "--skip-if-no-coverage",
        "--coverage-json",
        str(cov),
    )

    assert result.returncode == 1, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert "scripts/foo.py" in payload["blocking"]


def _fingerprint(repo: Path, base: str) -> str:
    return _load_teeth().changed_pool_fingerprint(repo, base)


def _marker_path(cov: Path) -> Path:
    return changed_line_coverage_marker_path(cov)


def _write_marker(
    cov: Path, fingerprint: str, *, producer: str = CHANGED_LINE_COVERAGE_PRODUCER
) -> None:
    cov.with_name(cov.name + ".changed-line.fingerprint").write_text(
        json.dumps(
            {
                "fingerprint": fingerprint,
                "producer": producer,
                "schema": CHANGED_LINE_COVERAGE_MARKER_SCHEMA,
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def test_require_fresh_coverage_skips_when_marker_absent(tmp_path: Path) -> None:
    # A coverage source with NO producer-qualified `.changed-line.fingerprint`
    # marker is treated as stale: the
    # pre-push teeth skip non-blocking rather than trust coverage that may predate
    # the changed lines (the stale-coverage false-positive class found in the
    # wiring smoke). Without this guard a stale reports/mutation/test-coverage.json
    # would block a legitimate push.
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    cov = _write_coverage(repo, executed=[1, 2], missing=[5, 6])  # would block if trusted
    # no <cov>.changed-line.fingerprint marker written

    result = run_script(
        _TEETH,
        "--repo-root",
        str(repo),
        "--base-sha",
        base,
        "--head-sha",
        head,
        "--reuse-coverage",
        "--require-fresh-coverage",
        "--coverage-json",
        str(cov),
    )

    assert result.returncode == UNESTABLISHED_EXIT, (
        "this run established nothing about a non-empty changed set; exit 0 printed "
        "PASS beside the payload that said so"
    )
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is True
    assert payload["blocking"] == []
    assert "stale" in payload["reason"]
    # #335: the stale-skip path also surfaces the unverified obligation loudly.
    assert payload["coverage_not_verified"] is True
    assert "WARNING (changed-line mutation gate)" in result.stderr


def test_require_fresh_coverage_skips_when_marker_mismatched(tmp_path: Path) -> None:
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    cov = _write_coverage(repo, executed=[1, 2], missing=[5, 6])
    _write_marker(cov, "0" * 64)  # wrong fingerprint

    result = run_script(
        _TEETH,
        "--repo-root",
        str(repo),
        "--base-sha",
        base,
        "--head-sha",
        head,
        "--reuse-coverage",
        "--require-fresh-coverage",
        "--coverage-json",
        str(cov),
    )

    assert result.returncode == UNESTABLISHED_EXIT, (
        "this run established nothing about a non-empty changed set; exit 0 printed "
        "PASS beside the payload that said so"
    )
    payload = yaml.safe_load(result.stdout)
    assert "stale" in payload["reason"]
    assert payload["coverage_not_verified"] is True  # #335: stale skip surfaces too


def test_require_fresh_coverage_fires_when_marker_matches_fingerprint(tmp_path: Path) -> None:
    # The freshness guard does NOT defang the teeth: a coverage source whose
    # producer-qualified `.changed-line.fingerprint` matches the current
    # changed-pool content still blocks
    # an uncovered changed line (AC-WIRE — fresh coverage keeps its teeth).
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    cov = _write_coverage(repo, executed=[1, 2], missing=[5, 6])  # def b uncovered
    _write_marker(cov, _fingerprint(repo, base))

    result = run_script(
        _TEETH,
        "--repo-root",
        str(repo),
        "--base-sha",
        base,
        "--head-sha",
        head,
        "--reuse-coverage",
        "--require-fresh-coverage",
        "--coverage-json",
        str(cov),
    )

    assert result.returncode == 1, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert "scripts/foo.py" in payload["blocking"]


def test_write_fresh_marker_stamps_coverage_fingerprint(tmp_path: Path, monkeypatch) -> None:
    # Producer mode (closeout): after coverage is produced, write the
    # `<coverage-json>.changed-line.fingerprint` marker = a producer-qualified
    # changed-pool content fingerprint
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
            json.dumps(
                {"files": {"scripts/foo.py": {"executed_lines": [1, 2, 5, 6], "missing_lines": []}}}
            ),
            encoding="utf-8",
        )

    monkeypatch.setattr(teeth, "run_test_coverage", fake_probe)
    monkeypatch.setattr(teeth, "read_test_command", lambda config: "python3 -m pytest -q")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "teeth",
            "--repo-root",
            str(repo),
            "--base-sha",
            base,
            "--head-sha",
            head,
            "--coverage-json",
            str(cov_path),
            "--write-fresh-marker",
        ],
    )

    rc = teeth.main()

    assert rc == 0
    assert seen["dynamic_context"] is False, "producer drops dynamic_context (lever A)"
    marker = _marker_path(cov_path)
    assert marker.is_file(), "producer must write the changed-line marker"
    payload = json.loads(marker.read_text(encoding="utf-8"))
    assert payload["producer"] == CHANGED_LINE_COVERAGE_PRODUCER
    assert payload["fingerprint"] == _fingerprint(repo, base)


def _dirty_pool_file(repo: Path) -> None:
    """Append an UNCOMMITTED change to the pool file (worktree, not committed)."""
    foo = repo / "scripts" / "foo.py"
    foo.write_text(
        foo.read_text(encoding="utf-8") + "\n\ndef c():\n    return 3\n", encoding="utf-8"
    )


def test_false_green_warning_fires_for_uncommitted_pool_change(tmp_path: Path) -> None:
    # handoff-4: head resolves to HEAD + an eligible pool file has uncommitted
    # worktree changes -> base..HEAD excludes them -> false-green warning.
    repo, _base, _head = _seed_repo_with_changed_pool_file(tmp_path)
    _dirty_pool_file(repo)
    teeth = _load_teeth()
    warning = teeth.false_green_warning(repo, "HEAD", {"scripts/foo.py"})
    assert warning is not None
    assert "FALSE GREEN" in warning
    assert "scripts/foo.py" in warning


def test_false_green_warning_silent_when_worktree_clean(tmp_path: Path) -> None:
    repo, _base, _head = _seed_repo_with_changed_pool_file(tmp_path)  # committed, clean
    teeth = _load_teeth()
    assert teeth.false_green_warning(repo, "HEAD", {"scripts/foo.py"}) is None


def test_uncommitted_pool_changes_includes_untracked_nonignored_file(tmp_path: Path) -> None:
    repo, _base, _head = _seed_repo_with_changed_pool_file(tmp_path)
    untracked = repo / "scripts" / "new_pool.py"
    untracked.write_text("def new():\n    return 1\n", encoding="utf-8")

    teeth = _load_teeth()
    assert teeth.uncommitted_pool_changes(repo, {"scripts/new_pool.py"}) == ["scripts/new_pool.py"]


def test_false_green_warning_silent_when_change_outside_pool(tmp_path: Path) -> None:
    repo, _base, _head = _seed_repo_with_changed_pool_file(tmp_path)
    _dirty_pool_file(repo)
    teeth = _load_teeth()
    # foo.py is dirty but not in the eligible set -> not a pool concern -> silent.
    assert teeth.false_green_warning(repo, "HEAD", {"scripts/other.py"}) is None


def test_false_green_warning_silent_when_head_is_not_HEAD(tmp_path: Path) -> None:
    repo, base, _head = _seed_repo_with_changed_pool_file(tmp_path)
    _dirty_pool_file(repo)
    teeth = _load_teeth()
    # Analyzing an explicit earlier ref is not the head==HEAD false-green case.
    assert teeth.false_green_warning(repo, base, {"scripts/foo.py"}) is None


def test_a_dirty_pool_still_reports_unestablished_when_the_scope_was_also_partial(
    tmp_path: Path,
) -> None:
    """Both causes at once, and the REFUSABLE one must win.

    Exit 3 is refusable at push time (`--refuse-unestablished`); exit 4 is
    deliberately not. The first cut of the partial repair ordered `unanalyzed`
    above `fg_warning` on the reasoning that "both are non-blocking non-passes, so
    either byte is honest when both hold" — which is false, and turned a push this
    lane used to STOP into one it waves through. The operator's decision that
    created exit 4 was about the unmapped-file cause and said nothing about the
    dirty-pool cause.

    Discriminating: the same run WITHOUT `--limit-to-file` is the control below,
    and a plain limited-and-clean run is exit 4 elsewhere in this file — so this
    asserts the ORDER, not merely that 3 exists.
    """
    repo, base, head = seed_two_changed_pool_files(tmp_path)
    _dirty_pool_file(repo)
    cov = _write_two_file_coverage(repo)

    result = run_script(
        _TEETH,
        "--repo-root",
        str(repo),
        "--base-sha",
        base,
        "--head-sha",
        head,
        "--reuse-coverage",
        "--coverage-json",
        str(cov),
        "--allow-dirty",
        "--limit-to-file",
        "scripts/foo.py",
    )

    assert result.returncode == UNESTABLISHED_EXIT, (
        "a dirty pool must not be downgraded to the non-refusable PARTIAL byte "
        "just because the scope was also limited"
    )
    payload = yaml.safe_load(result.stdout)
    # The narrower fact is NOT lost by losing the byte — both channels still name it.
    assert payload["unanalyzed_changed_pool_files"] == ["scripts/bar.py"]
    assert "says NOTHING about the rest" in result.stderr


def test_false_green_warning_surfaces_in_report_and_stderr(tmp_path: Path) -> None:
    # The late warning is now only reachable under the explicit --allow-dirty
    # advisory read; the default path refuses at startup instead (see
    # test_refuses_fast_before_any_probe_when_pool_is_dirty).
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    _dirty_pool_file(repo)  # uncommitted def c, excluded from base..HEAD
    cov = _write_coverage(repo, executed=[1, 2, 5, 6], missing=[])  # in-range lines covered
    result = run_script(  # --head-sha <HEAD sha> -> resolves to HEAD
        _TEETH,
        "--repo-root",
        str(repo),
        "--base-sha",
        base,
        "--head-sha",
        head,
        "--reuse-coverage",
        "--coverage-json",
        str(cov),
        "--allow-dirty",
    )

    assert result.returncode == UNESTABLISHED_EXIT, (
        "this run established nothing about a non-empty changed set; exit 0 printed "
        "PASS beside the payload that said so"
    )
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is True  # in-range verdict still clean
    assert "warning" in payload and "FALSE GREEN" in payload["warning"]
    assert "scripts/foo.py" in payload["warning"]
    assert "WARNING (changed-line mutation gate)" in result.stderr


def test_refuses_fast_before_any_probe_when_pool_is_dirty(tmp_path: Path) -> None:
    # Refuse-fast: the contaminated-input case used to cost the FULL ~10 minute
    # coverage probe and then emit an after-the-fact `warning` whose clean verdict
    # was indistinguishable from a real green. Now it refuses at startup: exit 2
    # (no verdict, distinct from 1 = real blocker), naming the offending files.
    # No --reuse-coverage here on purpose — if the refusal regressed, the run would
    # fall through to the probe instead of returning immediately.
    repo, base, _head = _seed_repo_with_changed_pool_file(tmp_path)
    _dirty_pool_file(repo)

    result = run_script(_TEETH, "--repo-root", str(repo), "--base-sha", base, "--head-sha", "HEAD")

    assert result.returncode == 2, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert payload["refused"] is True
    assert payload["uncommitted_pool_files"] == ["scripts/foo.py"]
    assert payload["changed_line_proof"] == "refused"
    assert "scripts/foo.py" in payload["reason"] and "--allow-dirty" in payload["reason"]
    assert "REFUSING to run" in result.stderr


def test_refusal_happens_before_the_coverage_probe_runs(tmp_path: Path, monkeypatch) -> None:
    # The point of the refusal is the wasted ~10 minutes, so pin that the probe is
    # never reached: a probe stub that explodes must not be called.
    repo, base, _head = _seed_repo_with_changed_pool_file(tmp_path)
    _dirty_pool_file(repo)
    teeth = _load_teeth()

    def explode(*_args, **_kwargs):
        raise AssertionError("the coverage probe must not run after a startup refusal")

    monkeypatch.setattr(teeth, "run_test_coverage", explode)
    monkeypatch.setattr(teeth, "read_test_command", lambda config: "python3 -m pytest -q")
    monkeypatch.setattr(
        sys,
        "argv",
        ["teeth", "--repo-root", str(repo), "--base-sha", base, "--head-sha", "HEAD"],
    )

    assert teeth.main() == teeth.REFUSED_EXIT


def test_allow_dirty_proceeds_but_records_the_result_as_unverified(tmp_path: Path) -> None:
    # The escape hatch keeps the old advisory read available (run-quality's
    # read-only lane uses it), but the payload must SAY it is unverified so a clean
    # result cannot be cited as changed-line proof for the dirty files.
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    _dirty_pool_file(repo)
    cov = _write_coverage(repo, executed=[1, 2, 5, 6], missing=[])

    result = run_script(
        _TEETH,
        "--repo-root",
        str(repo),
        "--base-sha",
        base,
        "--head-sha",
        head,
        "--reuse-coverage",
        "--coverage-json",
        str(cov),
        "--allow-dirty",
    )

    assert result.returncode == UNESTABLISHED_EXIT, (
        "this run established nothing about a non-empty changed set; exit 0 printed "
        "PASS beside the payload that said so"
    )
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is True  # advisory in-range verdict still stands
    assert payload["dirty_pool_unverified"] is True
    assert payload["uncommitted_pool_files"] == ["scripts/foo.py"]
    assert payload["changed_line_proof"] == "unverified-dirty-worktree"
    assert "FALSE GREEN" in payload["warning"]
