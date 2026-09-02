"""Worktree, limit, and scope cases split from test_changed_line_mutation_coverage.py (length cap).

Targeted tests for the #260 preventive teeth.

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
from types import SimpleNamespace

import yaml

from .changed_line_mutation_fixtures import (
    git as _git,
)
from .changed_line_mutation_fixtures import (
    seed_repo_with_changed_pool_file as _seed_repo_with_changed_pool_file,
)
from .seeding_support import seed_two_changed_pool_files
from .support import ROOT, run_script
from .test_changed_line_mutation_coverage import (  # noqa: E402
    UNESTABLISHED_EXIT,
    _dirty_pool_file,
    _write_two_file_coverage,
)

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


def test_clean_worktree_does_not_refuse_and_reports_the_pinned_head(tmp_path: Path) -> None:
    # No false positive on a clean tree, and `--head-sha HEAD` is pinned once to a
    # concrete SHA that the payload reports (so the reader knows which tree the
    # line numbers were mapped against).
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    cov = _write_coverage(repo, executed=[1, 2, 5, 6], missing=[])

    result = run_script(
        _TEETH,
        "--repo-root",
        str(repo),
        "--base-sha",
        base,
        "--head-sha",
        "HEAD",
        "--reuse-coverage",
        "--coverage-json",
        str(cov),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert "refused" not in payload
    assert payload["head_sha"] == "HEAD"  # unchanged field contract for consumers
    assert payload["resolved_head_sha"] == head


def test_mid_run_commit_marks_the_result_untrusted(tmp_path: Path, monkeypatch) -> None:
    # The run-3 trap: the parent commits WHILE the probe runs, so the coverage and
    # the changed-line mapping come from different trees and the reported line
    # attributions look plausible and are wrong. That must never render ok: true.
    repo, base, _head = _seed_repo_with_changed_pool_file(tmp_path)
    teeth = _load_teeth()
    cov_path = repo / "cov.json"

    def commit_during_probe(
        repo_root, test_command, coverage_json, *, dynamic_context=True
    ) -> None:
        foo = repo / "scripts" / "foo.py"
        foo.write_text(
            foo.read_text(encoding="utf-8") + "\n\ndef d():\n    return 4\n", encoding="utf-8"
        )
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "mid-run")
        Path(coverage_json).write_text(
            json.dumps(
                {"files": {"scripts/foo.py": {"executed_lines": [1, 2, 5, 6], "missing_lines": []}}}
            ),
            encoding="utf-8",
        )

    monkeypatch.setattr(teeth, "run_test_coverage", commit_during_probe)
    monkeypatch.setattr(teeth, "read_test_command", lambda config: "python3 -m pytest -q")
    captured: list[dict] = []
    monkeypatch.setattr(teeth, "_emit", captured.append)
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
            "HEAD",
            "--coverage-json",
            str(cov_path),
        ],
    )

    rc = teeth.main()

    assert rc == teeth.REFUSED_EXIT
    payload = captured[-1]
    assert payload["ok"] is False
    assert payload["untrusted"] is True
    assert payload["changed_line_proof"] == "untrusted"
    assert "HEAD moved" in payload["untrusted_reason"]


def test_run_state_drift_is_silent_on_a_settled_tree(tmp_path: Path) -> None:
    repo, base, _head = _seed_repo_with_changed_pool_file(tmp_path)
    teeth = _load_teeth()
    pinned = teeth._pin_run_state(repo, base, "HEAD")

    assert teeth.run_state_drift(repo, base, "HEAD", pinned) is None

    _dirty_pool_file(repo)  # worktree edit to a changed pool file mid-run
    drift = teeth.run_state_drift(repo, base, "HEAD", pinned)
    assert drift is not None and "worktree content changed" in drift


def test_contaminating_pool_changes_is_the_single_detector(tmp_path: Path) -> None:
    # The refusal and the legacy late warning must never disagree about what is
    # contaminated, so both read this one function.
    repo, base, _head = _seed_repo_with_changed_pool_file(tmp_path)
    _dirty_pool_file(repo)
    teeth = _load_teeth()

    assert teeth.contaminating_pool_changes(repo, "HEAD", {"scripts/foo.py"}) == ["scripts/foo.py"]
    # An explicit older ref used to return [] here, and this assertion pinned that
    # as an invariant. It was the under-approximation, not a property: coverage is
    # collected from the live worktree whatever head is analyzed, so a dirty pool
    # file contaminates the run either way. Reproduced before the change.
    assert teeth.contaminating_pool_changes(repo, base, {"scripts/foo.py"}) == ["scripts/foo.py"]
    assert "scripts/foo.py" in teeth.false_green_warning(repo, "HEAD", {"scripts/foo.py"})
    # The WARNING stays scoped to head==HEAD, because its wording asserts exactly
    # that; the older-ref shape is reported by `probe_run_trust` in its own words.
    assert teeth.false_green_warning(repo, base, {"scripts/foo.py"}) is None


def test_runs_coverage_probe_when_not_reusing(tmp_path: Path, monkeypatch) -> None:
    # Covers the run-the-probe branch (the default, no --reuse-coverage): the
    # heavy gate probe + config read are stubbed so the test stays fast while the
    # branch executes and the produced coverage drives a clean verdict.
    #
    # dynamic_context is False here even WITHOUT --write-fresh-marker (#696). It
    # used to be True on this arm, justified as "the faithful path" -- faithful to
    # the scheduled gate's probe, which collects contexts because the cosmic-ray
    # sampler reads them. This gate does not: its verdict consumes
    # executed/missing lines only. Preserving an input dimension no reader
    # consults cost a measured 671x in corpus size and 276x in load time, so the
    # flag became explicit (--collect-test-contexts) instead of a side effect of
    # a marker-stamping flag.
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    teeth = _load_teeth()
    called = {}

    def fake_probe(repo_root, test_command, coverage_json, *, dynamic_context=True) -> None:
        called["probe"] = True
        called["dynamic_context"] = dynamic_context
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
            str(repo / "cov.json"),
        ],
    )

    rc = teeth.main()

    assert called.get("probe") is True  # the run-the-probe branch executed
    assert called["dynamic_context"] is False
    assert rc == 0


# --------------------------------------------------------------------------- #
# --limit-to-file (D40): the incremental pre-push producer collects coverage from a
# FOCUSED test subset, so the blocking set has to narrow with it. Focused coverage is
# a subset of full coverage, so an unlimited run over it would report files the full
# suite covers as uncovered — a false block, which is how a gate gets bypassed.
# --------------------------------------------------------------------------- #


def test_limit_to_file_narrows_the_blocking_set_and_names_the_rest(tmp_path: Path) -> None:
    repo, base, head = seed_two_changed_pool_files(tmp_path)
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
        "--limit-to-file",
        "scripts/foo.py",
    )

    # Exit 4 (PARTIAL). It used to be 0 -- the same byte as a run with no blind
    # spot at all -- while stderr said "A clean verdict says NOTHING about the
    # rest". The scope now reaches the verdict; it still does not refuse.
    assert result.returncode == 4, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["blocking"] == []
    # Scoped on all THREE channels now: stderr, the payload, and the exit code.
    assert payload["changed_line_proof"] == "partial"
    assert payload["unanalyzed_changed_pool_files"] == ["scripts/bar.py"]
    assert "says NOTHING about the rest" in result.stderr
    assert "scripts/bar.py" in result.stderr


def test_without_the_limit_the_same_coverage_still_blocks(tmp_path: Path) -> None:
    """The discriminating control. If this passed too, the test above would prove
    only that the coverage fixture was clean, not that the limit did anything."""
    repo, base, head = seed_two_changed_pool_files(tmp_path)
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
    )

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["blocking"] == ["scripts/bar.py"]
    assert "unanalyzed_changed_pool_files" not in payload


def test_a_limit_that_matches_nothing_refuses_to_report_an_empty_range(tmp_path: Path) -> None:
    """An empty ANALYZED set is not an empty CHANGED set.

    Saying "no eligible mutation-pool files changed in this range" here would be the
    vacuous-green class verbatim: a verdict rendered over a scope that was never read,
    on the very gate whose recurring failure is exactly that.
    """
    repo, base, head = seed_two_changed_pool_files(tmp_path)
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
        "--limit-to-file",
        "scripts/absent.py",
    )

    assert result.returncode == UNESTABLISHED_EXIT, (
        "this run established nothing about a non-empty changed set; exit 0 printed "
        "PASS beside the payload that said so"
    )
    payload = yaml.safe_load(result.stdout)
    assert "fell OUTSIDE --limit-to-file" in payload["reason"]
    assert "proves nothing about them" in payload["reason"]
    assert sorted(payload["unanalyzed_changed_pool_files"]) == ["scripts/bar.py", "scripts/foo.py"]


def test_an_absent_limit_analyzes_everything(tmp_path: Path) -> None:
    """`--limit-to-file` is absent on every pre-existing caller, so an empty list must
    mean "analyze all", never "analyze none". Getting this backwards would silently
    disarm the gate for every existing invocation."""
    teeth = _load_teeth()
    args = SimpleNamespace(limit_to_file=[])

    analyzed, unanalyzed = teeth._apply_file_limit(args, ["scripts/foo.py", "scripts/bar.py"])

    assert analyzed == ["scripts/foo.py", "scripts/bar.py"]
    assert unanalyzed == []


def test_probe_run_trust_separates_could_not_look_from_looked_and_found_nothing() -> None:
    """The distinction this module's docstring demanded and the code did not have.

    A failed git command returned `[]`, identical to a clean pool, so a run whose
    inputs could not be inspected still rendered a clean verdict. Reproduced
    before the fix by probing a directory that is not a git repo at all.
    """
    import tempfile

    teeth = _load_teeth()
    probe = teeth.probe_run_trust(Path(tempfile.mkdtemp()), "HEAD", {"scripts/foo.py"})
    assert probe.contaminated == []
    assert probe.unestablished_reason is not None
    assert "could not inspect" in probe.unestablished_reason
    # An inspection failure is REFUSED, not the lenient "ran, established nothing":
    # exit 3's leniency is granted because a dirty worktree is normal mid-work, and
    # a broken git is never that.
    assert probe.unestablished_kind == teeth.INSPECTION_FAILED


def test_probe_run_trust_reports_an_analyzed_head_that_is_not_HEAD(tmp_path: Path) -> None:
    """Coverage comes from the HEAD worktree whatever head is analyzed.

    When they differ the mapping and the measurement describe different trees, so
    the run establishes nothing — previously it short-circuited to `[]` and the
    dirty pool went unreported entirely.
    """
    repo, base, _head = _seed_repo_with_changed_pool_file(tmp_path)
    teeth = _load_teeth()

    clean_at_head = teeth.probe_run_trust(repo, "HEAD", {"scripts/foo.py"})
    assert clean_at_head.contaminated == []
    assert clean_at_head.unestablished_reason is None
    assert clean_at_head.unestablished_kind is None

    older = teeth.probe_run_trust(repo, base, {"scripts/foo.py"})
    assert older.unestablished_reason is not None
    assert "is not the checked-out HEAD" in older.unestablished_reason
    assert older.unestablished_kind == teeth.SCOPE_MISMATCH

    _dirty_pool_file(repo)
    dirty_older = teeth.probe_run_trust(repo, base, {"scripts/foo.py"})
    assert dirty_older.contaminated == ["scripts/foo.py"]
    assert dirty_older.unestablished_reason is not None


def test_the_gate_refuses_when_it_could_not_inspect_the_tree(tmp_path: Path, monkeypatch) -> None:
    """Wiring, not just the helper, and the RIGHT code.

    A git command that will not run is "no verdict" (exit 2), the same family as
    a mid-run drift. Exit 3's leniency exists because a dirty worktree is the
    normal mid-work state; a broken git inheriting that leniency would be one
    cause borrowing another's justification.
    """
    from scripts.gates_support.changed_line_run_trust import INSPECTION_FAILED, TrustProbe

    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    cov = _write_coverage(repo, executed=[1, 2, 5, 6], missing=[])
    teeth = _load_teeth()
    monkeypatch.setattr(
        teeth,
        "probe_run_trust",
        lambda *_a, **_k: TrustProbe([], "probe forced unestablished", INSPECTION_FAILED),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "check_changed_line_mutation_coverage.py",
            "--repo-root",
            str(repo),
            "--base-sha",
            base,
            "--head-sha",
            head,
            "--reuse-coverage",
            "--coverage-json",
            str(cov),
        ],
    )
    assert teeth.main() == teeth.REFUSED_EXIT


def test_a_scope_mismatch_does_not_make_an_empty_changed_set_refusable(tmp_path: Path) -> None:
    """Exit 3's own contract: an EMPTY changed set still exits 0.

    The first version of this check returned 3 before the changed set was known,
    so a docs-only range analyzed against an older head became refusable under
    `--refuse-unestablished` — which the consumer names as an incoherent blocker
    on the gate whose credibility is the point. Reproduced before the fix.
    """
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "scripts").mkdir()
    _git(repo, "init", "-q")
    (repo / "scripts" / "foo.py").write_text("def a():\n    return 1\n", encoding="utf-8")
    (repo / "docs" / "n.md").write_text("a\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    base = _git(repo, "rev-parse", "HEAD")
    (repo / "docs" / "n.md").write_text("a\nb\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "head")

    # base..base is empty AND the analyzed head is not the checked-out HEAD.
    result = run_script(
        _TEETH, "--repo-root", str(repo), "--base-sha", base, "--head-sha", base, "--reuse-coverage"
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "no eligible" in yaml.safe_load(result.stdout)["reason"]


def test_a_scope_mismatch_over_an_empty_scope_still_discloses_itself(tmp_path: Path) -> None:
    """Exit 0 is right; silence is not.

    Moving the scope-mismatch check below the changed-set computation (so an
    empty scope stopped being refusable) initially dropped the disclosure with
    it: the same tree judged against the checked-out HEAD exits 1 with a real
    blocker, while this path printed `clean` and said nothing about why the two
    disagree. Round 2 found it; reproduced before the repair.
    """
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "docs").mkdir()
    _git(repo, "init", "-q")
    (repo / "scripts" / "foo.py").write_text("def a():\n    return 1\n", encoding="utf-8")
    (repo / "docs" / "n.md").write_text("a\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    base = _git(repo, "rev-parse", "HEAD")
    (repo / "docs" / "n.md").write_text("a\nb\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "mid")
    mid = _git(repo, "rev-parse", "HEAD")
    (repo / "scripts" / "foo.py").write_text(
        "def a():\n    return 1\n\n\ndef b():\n    return 2\n", encoding="utf-8"
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "head")
    cov = _write_coverage(repo, executed=[1, 2], missing=[5, 6])

    result = _run(repo, base, mid, cov)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    # `reason` must NOT change: the consumer prefix-matches it to recognise an
    # empty scope, and rewriting it would turn this into a refusable blocker.
    assert payload["reason"].startswith("no eligible mutation-pool files changed")
    assert "is not the checked-out HEAD" in payload["analyzed_head_not_checked_out_head"]
    assert "not the checked-out HEAD" in result.stderr

    # Same base, same tree, honest head: a real blocker. This is the contrast the
    # silent version hid.
    honest = _run(repo, base, "HEAD", cov)
    assert honest.returncode == 1, honest.stdout + honest.stderr


def test_the_scope_mismatch_return_carries_the_limit_disclosure_too(
    tmp_path: Path, monkeypatch
) -> None:
    """Two unestablished causes at once must not mask each other.

    The scope-mismatch return sits between `_apply_file_limit` and the limit's
    own disclosure, so returning there dropped `unanalyzed_changed_pool_files`
    and the operator saw one reason and not the other.
    """
    from scripts.gates_support.changed_line_run_trust import SCOPE_MISMATCH, TrustProbe

    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    _git(repo, "init", "-q")
    for name in ("foo.py", "bar.py"):
        (repo / "scripts" / name).write_text("def a():\n    return 1\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    base = _git(repo, "rev-parse", "HEAD")
    for name in ("foo.py", "bar.py"):
        (repo / "scripts" / name).write_text(
            "def a():\n    return 1\n\n\ndef b():\n    return 2\n", encoding="utf-8"
        )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "head")
    head = _git(repo, "rev-parse", "HEAD")
    cov = repo / "coverage.json"
    cov.write_text(
        json.dumps(
            {"files": {"scripts/foo.py": {"executed_lines": [1, 2, 5, 6], "missing_lines": []}}}
        ),
        encoding="utf-8",
    )

    teeth = _load_teeth()
    monkeypatch.setattr(
        teeth,
        "probe_run_trust",
        lambda *_a, **_k: TrustProbe(
            [], "analyzed head is not the checked-out HEAD", SCOPE_MISMATCH
        ),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "check_changed_line_mutation_coverage.py",
            "--repo-root",
            str(repo),
            "--base-sha",
            base,
            "--head-sha",
            head,
            "--reuse-coverage",
            "--coverage-json",
            str(cov),
            "--limit-to-file",
            "scripts/foo.py",
        ],
    )
    emitted: list[dict] = []
    monkeypatch.setattr(teeth, "_emit", lambda report: emitted.append(report))

    assert teeth.main() == teeth.UNESTABLISHED_EXIT
    payload = emitted[-1]
    assert payload["changed_line_proof"] == "unestablished-untrustworthy-input"
    assert payload["unanalyzed_changed_pool_files"] == ["scripts/bar.py"]
    # This return sits between the limit split and the rest of the run, so it is the
    # one path whose count pair depends on the scope rebind landing FIRST. A future
    # edit that moves the rebind below this check would silently emit the startup
    # not-computed pair here, and nothing else would notice.
    assert payload["changed_pool_file_counts"] == {"analyzed": 1, "changed": 2}


def test_an_unresolvable_head_sha_is_inspection_failed_not_a_clean_probe(tmp_path: Path) -> None:
    """A `--head-sha` git cannot resolve is "could not look", not "looked and found nothing".

    Distinct arm from the worktree-inspection failure: this one fires before any
    diff runs, so a caller that mistyped a ref would otherwise get a probe that
    reports no contamination for a comparison that never happened.
    """
    repo, _base, _head = _seed_repo_with_changed_pool_file(tmp_path)
    teeth = _load_teeth()

    probe = teeth.probe_run_trust(repo, "no-such-ref-here", {"scripts/foo.py"})

    assert probe.contaminated == []
    assert probe.unestablished_kind == teeth.INSPECTION_FAILED
    assert "could not resolve" in probe.unestablished_reason


# --- #465: subprocess-only coverage advisory on the blocking payload -------------
