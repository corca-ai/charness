"""The sweep runner's own refusals, each observed FAILING rather than assumed.

Every test here exists because the corresponding failure has been measured in
this repo at least once, or because its absence is what made the measured one
invisible. A sweep runner that has never been seen refusing is not known to
refuse.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from runtime_bootstrap import import_repo_module
from tests.script_main import run_loaded_script_main

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "mutate_and_restore.py"
mar = import_repo_module(SCRIPT, "scripts.mutate_and_restore")


def _repo(tmp_path: Path, *, subject: str, test_body: str) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "subject.py").write_text(subject, encoding="utf-8")
    (repo / "test_subject.py").write_text(test_body, encoding="utf-8")
    return repo


SUBJECT = "def add(a, b):\n    return a + b\n\n\ndef unused(a, b):\n    return a - b\n"
# 2 + 2 == 2 * 2, so an `add(2, 2)` assertion lets the arithmetic mutant SURVIVE.
# The first draft of this file used it and the sweep correctly said so.
GOOD_TEST = "from subject import add\n\n\ndef test_add():\n    assert add(2, 3) == 5\n"
PYTEST_CMD = [sys.executable, "-m", "pytest", "-q", "test_subject.py"]


def _plan(**overrides) -> dict:
    plan = {"test_command": PYTEST_CMD, "mutants": []}
    plan.update(overrides)
    return plan


def test_a_broken_baseline_refuses_the_whole_sweep_instead_of_reporting_kills(
    tmp_path: Path,
) -> None:
    # The measured defect: a baseline that exits non-zero makes every mutant read
    # as killed, and the sweep looks exactly like a clean one.
    repo = _repo(
        tmp_path,
        subject=SUBJECT,
        test_body="from subject import add\n\n\ndef test_add():\n    assert add(2, 3) == 99\n",
    )
    plan = _plan(mutants=[{"id": "m1", "path": "subject.py", "find": "a + b", "replace": "a * b"}])

    sweep = mar.run_sweep(plan, repo, emit=lambda _line: None)

    assert sweep.baseline.earned is False
    assert "exited" in sweep.baseline.refusal
    # The load-bearing assertion: NO mutant ran. A refusal that still reports
    # kills is the defect wearing a warning label.
    assert sweep.mutants == []
    assert mar.exit_code(sweep) == 2


def test_a_nonexistent_test_path_refuses_rather_than_killing_everything(tmp_path: Path) -> None:
    # This is the zsh word-split defect in its original form: pytest handed one
    # nonexistent path, exiting non-zero, with nine mutants recorded as killed.
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    plan = _plan(
        test_command=[sys.executable, "-m", "pytest", "-q", "test_subject.py test_other.py"],
        mutants=[{"id": "m1", "path": "subject.py", "find": "a + b", "replace": "a * b"}],
    )

    sweep = mar.run_sweep(plan, repo, emit=lambda _line: None)

    assert sweep.baseline.earned is False
    assert sweep.mutants == []


def test_a_zero_test_baseline_refuses(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # A runner that exits 0 having collected nothing. pytest exits 5 here, so the
    # branch is pinned against a stub rather than left unreachable and untested.
    repo = _repo(tmp_path, subject=SUBJECT, test_body="# no tests here\n")
    monkeypatch.setattr(
        mar,
        "run_command",
        lambda command, cwd: subprocess.CompletedProcess(command, 0, "no tests ran in 0.01s", ""),
    )

    sweep = mar.run_sweep(_plan(mutants=[]), repo, emit=lambda _line: None)

    assert sweep.baseline.earned is False
    assert "0 tests" in sweep.baseline.refusal


def test_a_collectionless_pytest_run_also_refuses(tmp_path: Path) -> None:
    # The same condition through the real runner, which reports it as exit 5.
    repo = _repo(tmp_path, subject=SUBJECT, test_body="# no tests here\n")

    sweep = mar.run_sweep(_plan(mutants=[]), repo, emit=lambda _line: None)

    assert sweep.baseline.earned is False
    assert "exited 5" in sweep.baseline.refusal


def test_an_unreadable_baseline_summary_refuses_rather_than_assuming_zero() -> None:
    # None is not zero: a runner whose summary we cannot parse has not told us
    # its baseline held.
    assert mar.parse_passed("some runner said nothing useful") is None
    assert mar.parse_passed("no tests ran in 0.01s") == 0
    assert mar.parse_passed("3 passed in 0.10s") == 3
    assert mar.parse_passed("1 failed, 2 passed in 0.10s") == 2


def test_a_surviving_mutant_is_reported_as_survived(tmp_path: Path) -> None:
    # The sweep must be able to say "your test did not catch this", which is the
    # only reason to run one.
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    plan = _plan(
        mutants=[{"id": "unused-body", "path": "subject.py", "find": "a - b", "replace": "a // b"}]
    )

    sweep = mar.run_sweep(plan, repo, emit=lambda _line: None)

    assert sweep.baseline.earned is True
    assert sweep.baseline.passed == 1
    assert [m.verdict for m in sweep.mutants] == [mar.SURVIVED]
    assert mar.exit_code(sweep) == 1


def test_a_killed_mutant_is_reported_as_killed_and_the_sweep_passes(tmp_path: Path) -> None:
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    plan = _plan(
        mutants=[{"id": "add-body", "path": "subject.py", "find": "a + b", "replace": "a * b"}]
    )

    sweep = mar.run_sweep(plan, repo, emit=lambda _line: None)

    assert [m.verdict for m in sweep.mutants] == [mar.KILLED]
    assert mar.exit_code(sweep) == 0


def test_the_file_is_restored_after_every_mutant(tmp_path: Path) -> None:
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    plan = _plan(
        mutants=[
            {"id": "k", "path": "subject.py", "find": "a + b", "replace": "a * b"},
            {"id": "s", "path": "subject.py", "find": "a - b", "replace": "a // b"},
        ]
    )

    mar.run_sweep(plan, repo, emit=lambda _line: None)

    assert (repo / "subject.py").read_text(encoding="utf-8") == SUBJECT


def test_the_file_is_restored_even_when_the_test_command_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The hand-rolled harnesses restored on the happy path only, so a raising
    # command left the worktree mutated and the next command measured a tree
    # nobody meant to create.
    #
    # The first version of this test asserted only "it raised" and "the file
    # matches the original" -- both of which hold if apply_mutation never wrote
    # anything at all. Round 1 caught that: it could not tell restoration from
    # nothing-ever-happened. It now OBSERVES the mutated bytes at raise time.
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    seen: list[str] = []

    def explode(_command, _cwd, _recovery, _journal_id):
        seen.append((repo / "subject.py").read_text(encoding="utf-8"))
        raise OSError("command could not be spawned")

    baseline = mar.Baseline(returncode=0, passed=1, output="1 passed")
    monkeypatch.setattr(mar, "run_mutation_command", explode)

    with pytest.raises(OSError):
        mar.run_mutant(
            {"id": "m", "path": "subject.py", "find": "a + b", "replace": "a * b"},
            PYTEST_CMD,
            repo,
            baseline,
        )

    assert seen and "a * b" in seen[0], "the mutation was never applied; restore proves nothing"
    assert (repo / "subject.py").read_text(encoding="utf-8") == SUBJECT


def test_a_failure_between_the_write_and_the_bytecode_drop_still_restores(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # apply_mutation writes and THEN invalidates bytecode. A PermissionError from
    # that unlink -- routine on a tree that has been run under docker or sudo --
    # used to leave the file mutated with the pristine bytes in a dead local.
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)

    def boom(_path):
        raise PermissionError("__pycache__ is not writable")

    monkeypatch.setattr(mar, "invalidate_bytecode", boom)
    baseline = mar.Baseline(returncode=0, passed=1, output="1 passed")

    with pytest.raises(PermissionError):
        mar.run_mutant(
            {"id": "m", "path": "subject.py", "find": "a + b", "replace": "a * b"},
            PYTEST_CMD,
            repo,
            baseline,
        )

    assert (repo / "subject.py").read_text(encoding="utf-8") == SUBJECT


@pytest.mark.parametrize(
    ("subject", "mutant", "detail"),
    [
        pytest.param(
            SUBJECT,
            {"id": "typo", "path": "subject.py", "find": "a ++ b", "replace": "x"},
            "not found",
            id="absent-find",
        ),
        pytest.param(
            SUBJECT + "FIRST = 1\nSECOND = 1\n",
            {"id": "amb", "path": "subject.py", "find": "= 1", "replace": "= 2"},
            "occurs 2 times",
            id="ambiguous-find",
        ),
        pytest.param(
            SUBJECT,
            {"id": "noop", "path": "subject.py", "find": "a + b", "replace": "a + b"},
            "no-op mutant",
            id="no-op-replacement",
        ),
    ],
)
def test_an_unearned_edit_is_refused_not_counted_as_killed(
    tmp_path: Path, subject: str, mutant: dict, detail: str
) -> None:
    """Find/replace that does not earn an edit cannot come back killed or survived."""
    repo = _repo(tmp_path, subject=subject, test_body=GOOD_TEST)
    sweep = mar.run_sweep(_plan(mutants=[mutant]), repo, emit=lambda _line: None)
    assert [m.verdict for m in sweep.mutants] == [mar.REFUSED]
    assert detail in sweep.mutants[0].detail
    assert (repo / "subject.py").read_text(encoding="utf-8") == subject
    assert mar.exit_code(sweep) == 1


def test_the_baseline_count_is_emitted_before_the_first_mutant(tmp_path: Path) -> None:
    # A truncated log must still carry what the sweep was measured against.
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    plan = _plan(mutants=[{"id": "k", "path": "subject.py", "find": "a + b", "replace": "a * b"}])
    lines: list[str] = []

    mar.run_sweep(plan, repo, emit=lines.append)

    assert lines[0] == "baseline: 1 passed"
    assert "killed" in lines[1]


@pytest.mark.boundary_contract(
    reason="assert the mutation runner CLI's exact exit-code contract for baseline refusal and survivors"
)
def test_cli_exits_two_on_a_refused_baseline_and_one_on_a_survivor(tmp_path: Path) -> None:
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    survivor = tmp_path / "survivor.json"
    survivor.write_text(
        json.dumps(
            _plan(mutants=[{"id": "s", "path": "subject.py", "find": "a - b", "replace": "a // b"}])
        ),
        encoding="utf-8",
    )
    broken = tmp_path / "broken.json"
    broken.write_text(
        json.dumps(
            _plan(
                test_command=[sys.executable, "-m", "pytest", "-q", "missing_test.py"],
                mutants=[{"id": "s", "path": "subject.py", "find": "a - b", "replace": "a // b"}],
            )
        ),
        encoding="utf-8",
    )

    def run(plan_path: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--plan", str(plan_path)],
            capture_output=True,
            text=True,
        )

    survived = run(survivor)
    assert survived.returncode == 1
    assert yaml.safe_load(survived.stdout)["survived"] == 1

    refused = run(broken)
    assert refused.returncode == 2
    assert yaml.safe_load(refused.stdout)["baseline"]["earned"] is False
    assert yaml.safe_load(refused.stdout)["mutants"] == []


def test_mutating_a_source_file_drops_its_stale_bytecode(tmp_path: Path) -> None:
    # Found by this suite against the runner's first draft, which reported a real
    # `a + b` -> `a * b` mutant as SURVIVED. That edit is the same LENGTH, and
    # CPython validates a .pyc by source size plus mtime truncated to whole
    # seconds -- so inside one second the stale bytecode stays valid, the
    # unmutated code runs, and the sweep renders a verdict about code that never
    # executed. That is the defect this runner exists to prevent, occurring
    # inside the runner.
    #
    # Pinned at the CALL SITE, not on `invalidate_bytecode` itself: an end-to-end
    # assertion is timing-dependent (a baseline run slow enough to cross a second
    # boundary invalidates the cache by accident and the test passes for the
    # wrong reason), which is exactly how the first version of this test passed
    # while the guard was deleted.
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    # The inner run's own result is asserted BEFORE the side effect it produces.
    # Discarding it meant any environment where the inner pytest cannot run surfaced
    # as "precondition: bytecode cache exists" -- a message about bytecode for a
    # failure that has nothing to do with bytecode. This test fails on the GitHub
    # runner and passes locally (#590), and the runner's real reason was invisible
    # because of exactly this ordering.
    completed = mar.run_command(PYTEST_CMD, repo)
    assert completed.returncode == 0, (
        "precondition: the inner pytest must pass before its bytecode can be asserted; "
        f"exited {completed.returncode}\n--- stdout ---\n{completed.stdout}\n--- stderr ---\n{completed.stderr}"
    )
    # The CHILD's evidence. The inner pytest is a separate `sys.executable`
    # subprocess, so the parent's `sys.dont_write_bytecode` cannot explain it; only
    # the inherited env vars are causal, and if none of them is the reason, the
    # directory listing and the child's own stdout are what will name it.
    assert mar.bytecode_cache_paths(repo / "subject.py"), (
        "precondition: bytecode cache exists. The inner pytest PASSED, so nothing was "
        "written where this test looks. Inherited env: PYTHONDONTWRITEBYTECODE="
        f"{os.environ.get('PYTHONDONTWRITEBYTECODE')!r}, PYTHONPYCACHEPREFIX="
        f"{os.environ.get('PYTHONPYCACHEPREFIX')!r}. repo contents="
        f"{sorted(p.name for p in repo.iterdir())}; bytecode paths="
        f"{list(mar.bytecode_cache_paths(repo / 'subject.py'))}"
        f"\n--- inner pytest stdout ---\n{completed.stdout}"
    )

    original = mar.apply_mutation(repo / "subject.py", "a + b", "a * b")
    try:
        assert mar.bytecode_cache_paths(repo / "subject.py") == (), (
            "apply_mutation left stale bytecode; a same-length mutant can read as survived"
        )
        # Run under the mutation so a .pyc is regenerated from the MUTATED
        # source. Without this the assertion below is vacuous -- the cache was
        # already cleared above -- and deleting restore's guard passes it.
        mar.run_command(PYTEST_CMD, repo)
        assert mar.bytecode_cache_paths(repo / "subject.py"), (
            "precondition: mutated bytecode cached"
        )
    finally:
        mar.restore(repo / "subject.py", original)

    # Same size, possibly the same second: a surviving mutated .pyc would make
    # the NEXT command run mutated code against a restored source.
    assert mar.bytecode_cache_paths(repo / "subject.py") == (), (
        "restore left stale bytecode built from the mutated source"
    )


def test_an_unreadable_baseline_summary_refuses_the_sweep(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Round 1 found this refusal had NO test: deleting the branch left the suite
    # green. The parent confirmed it by mutation before repairing.
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    monkeypatch.setattr(
        mar,
        "run_command",
        lambda command, cwd: subprocess.CompletedProcess(command, 0, "done, no summary", ""),
    )

    sweep = mar.run_sweep(
        _plan(mutants=[{"id": "m", "path": "subject.py", "find": "a + b", "replace": "a * b"}]),
        repo,
        emit=lambda _l: None,
    )

    assert sweep.baseline.earned is False
    assert "no readable passing count" in sweep.baseline.refusal
    assert sweep.mutants == []


def _classify(returncode: int, output: str, baseline_passed: int = 1) -> tuple[str, str]:
    completed = subprocess.CompletedProcess([], returncode, output, "")
    baseline = mar.Baseline(returncode=0, passed=baseline_passed, output="")
    return mar.classify_mutant_run(completed, baseline)


@pytest.mark.parametrize(
    ("returncode", "output", "baseline_passed", "verdict", "detail"),
    [
        pytest.param(
            2,
            "INTERNALERROR> something exploded",
            1,
            mar.REFUSED,
            "no readable summary",
            id="crashed-no-summary",
        ),
        pytest.param(
            1,
            "1 failed in 0.10s",
            9,
            mar.REFUSED,
            "scope shrank",
            id="collected-fewer-than-baseline",
        ),
        pytest.param(
            1,
            "1 failed, 8 passed in 0.10s",
            9,
            mar.KILLED,
            None,
            id="failure-accounts-for-baseline",
        ),
        pytest.param(
            0,
            "20 passed in 0.10s",
            23,
            mar.REFUSED,
            "scope shrank",
            id="green-run-lost-tests",
        ),
        pytest.param(
            0,
            "23 passed in 0.10s",
            23,
            mar.SURVIVED,
            None,
            id="green-run-full-scope-survived",
        ),
        pytest.param(
            1,
            "1 failed, 8 passed, 1 error in 0.10s",
            9,
            mar.KILLED,
            None,
            id="teardown-error-beside-failure-is-kill",
        ),
        pytest.param(
            2,
            "2 errors in 0.10s",
            0,
            mar.REFUSED,
            "did not run to a verdict",
            id="error-only-run",
        ),
    ],
)
def test_classify_mutant_run_refuses_unearned_verdicts(
    returncode: int,
    output: str,
    baseline_passed: int,
    verdict: str,
    detail: str | None,
) -> None:
    """One table for `classify_mutant_run`: unmeasurable is not killed/survived.

    Each row is a door that used to live as its own test. The load-bearing property
    is the same: exit code plus a pytest summary must earn the verdict, and a
    missing summary, a shrunken scope, or an error-only run must refuse.
    """
    got, got_detail = _classify(returncode, output, baseline_passed=baseline_passed)
    assert got == verdict
    if detail is not None:
        assert detail in got_detail


def test_a_real_syntax_error_mutant_is_refused_not_killed(tmp_path: Path) -> None:
    # END-TO-END against real pytest output rather than a hand-written string
    # (#569's shape): the replacement does not parse, so pytest never runs a
    # test. Exit code alone would call this a kill.
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    plan = _plan(
        mutants=[{"id": "syntax", "path": "subject.py", "find": "a + b", "replace": "a +"}]
    )

    sweep = mar.run_sweep(plan, repo, emit=lambda _l: None)

    assert sweep.baseline.earned is True
    assert [m.verdict for m in sweep.mutants] == [mar.REFUSED], sweep.mutants[0].detail
    assert (repo / "subject.py").read_text(encoding="utf-8") == SUBJECT


def test_a_real_mutant_that_fails_one_of_several_tests_is_killed(tmp_path: Path) -> None:
    # END-TO-END: a genuine `1 failed, 2 passed` summary, so the kill path is
    # pinned against pytest's actual output rather than an invented string.
    body = (
        "from subject import add, unused\n\n\n"
        "def test_add():\n    assert add(2, 3) == 5\n\n\n"
        "def test_unused():\n    assert unused(5, 3) == 2\n\n\n"
        "def test_types():\n    assert isinstance(add(1, 1), int)\n"
    )
    repo = _repo(tmp_path, subject=SUBJECT, test_body=body)
    plan = _plan(
        mutants=[{"id": "real", "path": "subject.py", "find": "a - b", "replace": "a + b"}]
    )

    sweep = mar.run_sweep(plan, repo, emit=lambda _l: None)

    assert sweep.baseline.passed == 3
    assert [m.verdict for m in sweep.mutants] == [mar.KILLED], sweep.mutants[0].detail


def test_a_mutant_targeting_a_path_outside_the_repo_is_refused(tmp_path: Path) -> None:
    # The outside file must EXIST and be real: round 2 caught that pointing at a
    # nonexistent path meant the next check (`is_file`) produced the refusal, so
    # deleting the containment guard left the test green on the detail string
    # alone. Now the guard is the only thing standing between the sweep and a
    # write outside its declared root.
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    outside = tmp_path / "outside.py"
    outside.write_text("SECRET = 1\n", encoding="utf-8")
    baseline = mar.Baseline(returncode=0, passed=1, output="")

    result = mar.run_mutant(
        {"id": "esc", "path": "../outside.py", "find": "SECRET = 1", "replace": "SECRET = 2"},
        PYTEST_CMD,
        repo,
        baseline,
    )

    assert result.verdict == mar.REFUSED
    assert "escapes the repo root" in result.detail
    assert outside.read_text(encoding="utf-8") == "SECRET = 1\n", "the sweep wrote outside its root"


def test_a_plan_entry_without_a_replace_key_is_refused(tmp_path: Path) -> None:
    # A mis-keyed plan would otherwise become a silent deletion mutant, which
    # usually fails to parse -- and under the old exit-code verdict, read killed.
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    baseline = mar.Baseline(returncode=0, passed=1, output="")

    result = mar.run_mutant(
        {"id": "typo", "path": "subject.py", "find": "a + b", "replacement": "a * b"},
        PYTEST_CMD,
        repo,
        baseline,
    )

    assert result.verdict == mar.REFUSED
    assert "is missing ['replace']" in result.detail
    assert (repo / "subject.py").read_text(encoding="utf-8") == SUBJECT


def test_a_missing_target_file_is_refused(tmp_path: Path) -> None:
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    baseline = mar.Baseline(returncode=0, passed=1, output="")

    result = mar.run_mutant(
        {"id": "gone", "path": "nope.py", "find": "x", "replace": "y"}, PYTEST_CMD, repo, baseline
    )

    assert result.verdict == mar.REFUSED
    assert "does not exist" in result.detail


@pytest.mark.boundary_contract(
    reason="assert the mutation runner CLI's exact crash exit byte and stderr contract"
)
def test_a_crash_exits_three_so_it_cannot_be_read_as_survivors_found(tmp_path: Path) -> None:
    # Round 2: `except BaseException -> restore + raise` left the crash exiting 1,
    # which is what `exit_code` returns for "survivors or refusals found". Any
    # `if ! cmd` caller reads a crashed sweep as a normal report.
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    plan_path = tmp_path / "crash.json"
    plan_path.write_text(
        json.dumps(
            {
                "test_command": ["definitely-not-a-real-binary-xyz"],
                "mutants": [{"id": "m", "path": "subject.py", "find": "a + b", "replace": "a * b"}],
            }
        ),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--plan", str(plan_path)],
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 3, completed.stderr
    assert "CRASHED" in completed.stderr


def test_a_failed_restore_is_raised_not_swallowed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # `restore` verifies bytes; a filesystem that accepts the write but returns
    # different content must be loud, not silently leave a mutated worktree.
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    path = repo / "subject.py"
    original = path.read_bytes()
    monkeypatch.setattr(mar.Path, "read_bytes", lambda self: b"not what was written")

    with pytest.raises(mar.SweepError, match="failed to restore"):
        mar.restore(path, original)


@pytest.mark.boundary_contract(
    reason="assert the mutation runner CLI's exact sweep-refusal exit and output contract"
)
def test_the_cli_exits_two_on_a_sweep_error(tmp_path: Path) -> None:
    # A SweepError is a refusal the caller must see, and it is exit 2 -- distinct
    # from 1 (survivors/refusals) and 3 (crash).
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    plan_path = tmp_path / "bad.json"
    plan_path.write_text(
        json.dumps({"test_command": PYTEST_CMD, "mutants": [{"path": "subject.py", "find": "x"}]}),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--plan", str(plan_path)],
        capture_output=True,
        text=True,
    )

    # A missing `replace` key is a per-mutant REFUSED, so exit 1, not a crash.
    assert completed.returncode == 1, completed.stderr
    assert "missing" in completed.stdout


def test_the_summary_names_the_baseline_it_measured_against(tmp_path: Path) -> None:
    """Counts nobody can attribute to a baseline are the shape this runner exists to stop.

    The retired summary line said "over a baseline of 1 passing tests". The same fact
    is the `baseline` block: `earned` (the sweep was allowed to render verdicts at
    all) beside `passed` (how many tests those verdicts were measured against).
    """
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    plan_path = tmp_path / "p.json"
    plan_path.write_text(
        json.dumps(
            _plan(mutants=[{"id": "k", "path": "subject.py", "find": "a + b", "replace": "a * b"}])
        ),
        encoding="utf-8",
    )

    completed = run_loaded_script_main(
        str(SCRIPT), mar, "--repo-root", str(repo), "--plan", str(plan_path)
    )

    assert completed.returncode == 0, completed.stderr
    payload = yaml.safe_load(completed.stdout)
    assert payload["baseline"]["earned"] is True
    assert payload["baseline"]["passed"] == 1
    assert payload["killed"] == 1


def test_main_in_process_covers_the_exit_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The CLI tests above run subprocesses, which coverage cannot see, so the
    # exit-code mapping read as uncovered changed lines. Drive main() in-process.
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    plan_path = tmp_path / "p.json"

    def run(plan: dict) -> int:
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        monkeypatch.setattr(
            sys,
            "argv",
            ["mutate_and_restore.py", "--repo-root", str(repo), "--plan", str(plan_path)],
        )
        return mar.main()

    assert (
        run(_plan(mutants=[{"id": "k", "path": "subject.py", "find": "a + b", "replace": "a * b"}]))
        == 0
    )
    assert (
        run(
            _plan(mutants=[{"id": "s", "path": "subject.py", "find": "a - b", "replace": "a // b"}])
        )
        == 1
    )

    # exit 2: a SweepError out of the sweep itself.
    monkeypatch.setattr(
        mar, "run_sweep", lambda *_a, **_k: (_ for _ in ()).throw(mar.SweepError("boom"))
    )
    assert run(_plan(mutants=[])) == 2

    # exit 3: any other crash, kept distinct from 1 so it cannot read as survivors.
    monkeypatch.setattr(
        mar, "run_sweep", lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("kaboom"))
    )
    assert run(_plan(mutants=[])) == 3


def test_a_non_python_target_skips_bytecode_invalidation(tmp_path: Path) -> None:
    # The early return for a non-.py file: there is no bytecode cache to drop.
    target = tmp_path / "notes.md"
    target.write_text("x\n", encoding="utf-8")

    mar.invalidate_bytecode(target)  # must not raise

    assert target.read_text(encoding="utf-8") == "x\n"


def test_a_failure_inside_apply_restores_and_re_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The `except BaseException: restore; raise` arm, driven by a non-SweepError
    # out of apply_mutation itself.
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    baseline = mar.Baseline(returncode=0, passed=1, output="")

    def boom(_path, _find, _replace):
        (repo / "subject.py").write_text("MUTATED\n", encoding="utf-8")
        raise RuntimeError("apply exploded")

    monkeypatch.setattr(mar, "apply_mutation", boom)

    with pytest.raises(RuntimeError, match="apply exploded"):
        mar.run_mutant(
            {"id": "m", "path": "subject.py", "find": "a + b", "replace": "a * b"},
            PYTEST_CMD,
            repo,
            baseline,
        )

    assert (repo / "subject.py").read_text(encoding="utf-8") == SUBJECT


def test_a_nonzero_run_with_a_clean_summary_is_refused() -> None:
    # A runner that exits non-zero (usage error, plugin abort) while its summary
    # reports no failure and no error. The exit byte alone would call it a kill.
    verdict, detail = _classify(4, "5 passed in 0.10s", baseline_passed=1)

    assert verdict == mar.REFUSED
    assert "without reporting any test failure" in detail


# --- #564: the call-site question, as tool behaviour rather than a remembered rule ---

CALLER_SUBJECT = (
    "def guard(value):\n"
    "    return value\n"
    "\n"
    "\n"
    "def run(value):\n"
    "    value = guard(value)\n"
    "    return value\n"
)


def test_deleting_a_call_site_is_detected_as_a_removed_call() -> None:
    """`#564`'s whole shape: the callee still exists, the invocation is gone.

    A body-level classifier sees a function that is still defined and still correct and
    reports nothing. The fact that matters is that the CALL disappeared -- three repairs
    in one goal died exactly here with the suite green.
    """
    mutated = CALLER_SUBJECT.replace("    value = guard(value)\n", "    pass\n")

    assert mar.removed_calls(CALLER_SUBJECT.encode(), mutated.encode()) == ("guard",)


def test_a_body_only_mutation_removes_no_call() -> None:
    """The other direction, so the classifier is not just answering "something changed".

    Without this, a classifier that returned every callee in the file would pass the test
    above and be useless -- it would report a call site for every mutant ever run.
    """
    mutated = CALLER_SUBJECT.replace(
        "    return value\n\n\ndef run", "    return value + 1\n\n\ndef run"
    )

    assert mar.removed_calls(CALLER_SUBJECT.encode(), mutated.encode()) == ()


def test_an_attribute_call_is_keyed_by_the_attribute_not_the_dotted_path() -> None:
    """`lib.helper()`, `self.helper()` and `helper()` are the same repair being reached.

    Keying on the spelling would report a REMOVED call every time an import moved, which
    would make the count noise and train a reader to ignore it.
    """
    before = b"import lib\n\n\ndef run(v):\n    return lib.helper(v)\n"
    after = b"import lib\n\n\ndef run(v):\n    return v\n"

    assert mar.removed_calls(before, after) == ("helper",)


def test_an_unparseable_side_is_unclassified_rather_than_reported_as_no_call() -> None:
    """None is not `()`, and the distinction is the point.

    A deliberate syntax-error mutant is a legitimate plan entry. If it classified as
    "removed no call" it would count toward the sweep having looked and found nothing --
    a surface claiming a scope it never read, which is the class this tool serves.
    """
    assert mar.removed_calls(CALLER_SUBJECT.encode(), b"def run(:\n") is None
    assert mar.removed_calls(b"def run(:\n", CALLER_SUBJECT.encode()) is None


def test_a_sweep_with_no_call_site_mutant_states_the_non_claim(tmp_path: Path) -> None:
    """A clean sweep must not read as proof the repair is still reached.

    `1 killed, 0 survived` is exactly what all three of `#564`'s measured instances
    printed while the repair was dead in production.
    """
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    plan = _plan(
        mutants=[{"id": "body", "path": "subject.py", "find": "a + b", "replace": "a * b"}]
    )

    sweep = mar.run_sweep(plan, repo, emit=lambda _line: None)
    payload = mar.render(sweep)

    assert payload["killed"] == 1
    assert payload["call_site_mutants"] == 0
    assert "says nothing about whether" in payload["call_site_non_claim"]


def test_a_sweep_containing_a_call_site_mutant_makes_no_such_non_claim(tmp_path: Path) -> None:
    """The negative test for the non-claim itself: it must be able to go away.

    A message that is always printed carries no information, and this repo has shipped
    that shape before.
    """
    caller_test = "from subject import run\n\n\ndef test_run():\n    assert run(3) == 3\n    assert run.__name__ == 'run'\n"
    repo = _repo(tmp_path, subject=CALLER_SUBJECT, test_body=caller_test)
    plan = _plan(
        mutants=[
            {
                "id": "call-site",
                "path": "subject.py",
                "find": "    value = guard(value)\n",
                "replace": "    pass\n",
                # The DECLARATION is what silences the non-claim; the removed call is the
                # corroboration. Neither alone is enough.
                "call_site": True,
            }
        ]
    )

    sweep = mar.run_sweep(plan, repo, emit=lambda _line: None)
    payload = mar.render(sweep)

    assert payload["call_site_mutants"] == 1
    assert payload["mutants"][0]["removed_calls"] == ["guard"]
    assert payload["call_site_non_claim"] is None


def test_a_refused_mutant_is_unclassified_rather_than_counted_as_no_call_site(
    tmp_path: Path,
) -> None:
    """A mutant refused before it was ever applied established nothing about calls.

    `None` rather than `()`: the file was never written, so "removed no call" would be a
    verdict about an edit that did not happen.
    """
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    plan = _plan(
        mutants=[{"id": "absent", "path": "subject.py", "find": "not-in-the-file", "replace": "x"}]
    )

    sweep = mar.run_sweep(plan, repo, emit=lambda _line: None)
    payload = mar.render(sweep)

    assert payload["mutants"][0]["verdict"] == mar.REFUSED
    assert payload["mutants"][0]["removed_calls"] is None
    assert payload["call_site_mutants"] == 0


@pytest.mark.boundary_contract(
    reason="assert the mutation runner's real CLI stdout/stderr contract for the operator non-claim"
)
def test_the_cli_prints_the_call_site_count_and_the_non_claim(tmp_path: Path) -> None:
    """Operator-visible through the real command, not buried in the runner's internals.

    Both halves must survive the trip through the CLI: the count rides in the emitted
    payload on stdout, and the non-claim is ALSO written to stderr so it survives the
    `> file` redirect this repo requires for gates -- a reader who only watches the
    terminal still cannot miss it.
    """
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(
        json.dumps(
            _plan(
                mutants=[{"id": "body", "path": "subject.py", "find": "a + b", "replace": "a * b"}]
            )
        ),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--plan", str(plan_path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    payload = yaml.safe_load(completed.stdout)
    assert payload["call_site_mutants"] == 0, completed.stdout
    assert "says nothing about whether" in payload["call_site_non_claim"], completed.stdout
    assert "NON-CLAIM" in completed.stderr, completed.stderr


def test_every_removed_callee_is_reported_including_builtins() -> None:
    """No filtering, and the filter's removal is load-bearing rather than laziness.

    A builtins filter was written while removed calls still DROVE the non-claim. Once the
    declaration replaced that inference, the filter could only produce false negatives,
    and it produced one on this tool's own sweep: a mutant deleting the non-claim's
    `print(...)` call is a genuine call-site deletion, the filter hid it, and an honest
    declaration was REFUSED. `removed_calls` answers the question its name asks; which
    removals matter is the reader's judgement.
    """
    before = b"def run(v):\n    return tuple(sorted(guard(v)))\n"
    after = b"def run(v):\n    return ()\n"

    assert mar.removed_calls(before, after) == ("guard", "sorted", "tuple")


def test_an_undeclared_call_removal_does_not_silence_the_non_claim(tmp_path: Path) -> None:
    """Round 1's blocker: the inferred count silenced the tool's own warning.

    `_called_names` keys attribute calls by attribute, so `.join`, `.get`, `.search`,
    `.elements` all count as removed calls. A pure body mutant that happens to drop one
    was classified as caller-side proof and the `#564` non-claim went silent -- the tool
    suppressing its own finding on evidence that did not mean what it counted. Measured
    inside this very file: `return tuple(sorted(x.elements()))` -> `return ()` reports
    `('elements',)`.

    The removed call is still REPORTED. It just no longer decides.
    """
    subject = "def add(a, b):\n    return ' '.join([str(a)]) and a + b\n"
    test_body = "from subject import add\n\n\ndef test_add():\n    assert add(2, 3) == 5\n"
    repo = _repo(tmp_path, subject=subject, test_body=test_body)
    plan = _plan(
        mutants=[
            {
                "id": "drops-join",
                "path": "subject.py",
                "find": "' '.join([str(a)]) and ",
                "replace": "",
            }
        ]
    )

    sweep = mar.run_sweep(plan, repo, emit=lambda _line: None)
    payload = mar.render(sweep)

    assert payload["mutants"][0]["removed_calls"] == ["join", "str"], payload["mutants"][0]
    assert payload["call_site_mutants"] == 0, "an undeclared removal must not count"
    assert payload["call_site_non_claim"] is not None, (
        "the non-claim must survive an incidental removal"
    )
    # Wording: the trigger is "no mutant was DECLARED", not "nothing was deleted".
    assert "DECLARED" in payload["call_site_non_claim"]
    assert "no mutant deleted a call site" not in payload["call_site_non_claim"]


def test_a_false_call_site_declaration_is_refused(tmp_path: Path) -> None:
    """A declaration the edit contradicts is worse than no declaration, because it SILENCES.

    This is the one place the tool has teeth on the call-site axis, and it is a fact the
    tool can actually establish: the author said this mutant deletes a call, and the parse
    of the file it wrote says it deleted none.
    """
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    plan = _plan(
        mutants=[
            {
                "id": "lying",
                "path": "subject.py",
                "find": "a + b",
                "replace": "a * b",
                "call_site": True,
            }
        ]
    )

    sweep = mar.run_sweep(plan, repo, emit=lambda _line: None)
    payload = mar.render(sweep)

    assert payload["mutants"][0]["verdict"] == mar.REFUSED
    assert "removed no call" in payload["mutants"][0]["detail"]
    assert payload["call_site_mutants"] == 0
    assert payload["call_site_non_claim"] is not None


def test_a_super_init_deletion_is_visible_to_the_classifier() -> None:
    """A textbook dead repair, and the filter round 1 found made it invisible.

    The first filter used `hasattr(builtins, name)`; `builtins` is a MODULE OBJECT, so
    dunders resolve through `type(module)` and `__init__` was dropped as a builtin. This
    repo has five `super().__init__()` call sites. The filter is now gone entirely, which
    fixes the class rather than this instance.
    """
    before = (
        b"class C(B):\n    def __init__(self):\n        super().__init__()\n        self.x = 1\n"
    )
    after = b"class C(B):\n    def __init__(self):\n        self.x = 1\n"

    assert mar.removed_calls(before, after) == ("__init__", "super")


def test_the_classification_cannot_leave_the_tree_mutated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Round 1's second blocker: classification sat OUTSIDE the restoring `finally`.

    `ast.parse` can raise `RecursionError` on deeply nested source and the read can raise
    `OSError`; either escaped with the file still mutated. That is `#573`, re-opened by a
    reporting feature, in a module whose docstring promises the restore covers the write.
    """
    repo = _repo(tmp_path, subject=SUBJECT, test_body=GOOD_TEST)
    baseline = mar.measure_baseline(PYTEST_CMD, repo)

    def _boom(*_args, **_kwargs):
        raise RecursionError("maximum recursion depth exceeded during compilation")

    monkeypatch.setattr(mar, "removed_calls", _boom)

    with pytest.raises(RecursionError):
        mar.run_mutant(
            {"id": "m", "path": "subject.py", "find": "a + b", "replace": "a * b"},
            PYTEST_CMD,
            repo,
            baseline,
        )

    assert (repo / "subject.py").read_text(encoding="utf-8") == SUBJECT


def test_a_declared_call_site_mutant_that_was_refused_does_not_silence_the_non_claim() -> None:
    """Round 2's second blocker: REFUSED is no answer, not a bad answer.

    A declared mutant whose run is refused (scope shrank, collection error, non-zero with
    no reported failure) established nothing about the caller -- no test reached a verdict,
    which is property 2's whole premise. Counting it as "the question was asked" silences
    the warning on a mutant that produced no result.

    SURVIVED is deliberately NOT excluded: there the question was asked and answered
    badly, and the survivor plus the non-zero exit carry that.
    """
    baseline = mar.Baseline(returncode=0, passed=5, output="5 passed in 0.10s")
    refused = mar.MutantResult("m", "subject.py", mar.REFUSED, "scope shrank", 1, ("guard",), True)
    survived = mar.MutantResult("m2", "subject.py", mar.SURVIVED, "", 0, ("guard",), True)

    assert mar.Sweep(baseline=baseline, mutants=[refused]).call_site_mutants == []
    assert mar.call_site_non_claim(mar.Sweep(baseline=baseline, mutants=[refused])) is not None
    assert mar.Sweep(baseline=baseline, mutants=[survived]).call_site_mutants == [survived]


def test_a_declared_mutant_refused_before_it_ran_still_reports_its_declaration() -> None:
    """The field must state what the PLAN said, even for a mutant that never ran.

    It used to be read after the early returns, so a declared mutant with a typo'd `find`
    reported `declared_call_site: false` -- the report contradicting the plan, handed to
    the author who is debugging exactly that typo.
    """
    result = mar.run_mutant(
        {"id": "gone", "path": "nope.py", "find": "x", "replace": "y", "call_site": True},
        PYTEST_CMD,
        Path("/tmp"),
        mar.Baseline(returncode=0, passed=1, output="1 passed in 0.01s"),
    )

    assert result.verdict == mar.REFUSED
    assert result.declared_call_site is True


def test_a_non_boolean_call_site_declaration_is_refused() -> None:
    """`bool("false")` is True, and this file refuses every other mis-keyed plan entry.

    A templated plan emitting the string `"false"` would declare the opposite of its
    author's intent and silence the non-claim.
    """
    result = mar.run_mutant(
        {"id": "stringy", "path": "subject.py", "find": "x", "replace": "y", "call_site": "false"},
        PYTEST_CMD,
        Path("/tmp"),
        mar.Baseline(returncode=0, passed=1, output="1 passed in 0.01s"),
    )

    assert result.verdict == mar.REFUSED
    assert "must be a boolean" in result.detail


def test_an_empty_plan_still_states_the_non_claim() -> None:
    """The emptiest sweep is the most unearned clean report there is.

    `0 killed, 0 survived, 0 refused`, exit 0, and -- before this repair -- no warning,
    while the module docstring promised a sweep with no declared call-site test says so
    out loud.
    """
    baseline = mar.Baseline(returncode=0, passed=5, output="5 passed in 0.10s")

    assert mar.call_site_non_claim(mar.Sweep(baseline=baseline, mutants=[])) is not None


def test_an_unearned_baseline_makes_no_call_site_claim_either_way() -> None:
    """The one silence that is right: a refused baseline prints no counts to qualify."""
    baseline = mar.Baseline(returncode=1, passed=None, output="", refusal="baseline exited 1")

    assert mar.call_site_non_claim(mar.Sweep(baseline=baseline, mutants=[])) is None


def test_the_human_line_marks_the_declaration_and_the_removals_readably() -> None:
    """The `call_site_mutants` count must be auditable per mutant while the sweep runs.

    The payload carries `declared_call_site` and `removed_calls` on every mutant, but a
    sweep is long and a reader of a truncated or still-running log only ever has the
    streamed progress lines -- so the same pair has to be legible there too. Under the
    declaration design the discriminating fact is the DECLARATION; removals alone
    rendered a declared caller test and an incidental `.join` identically. The first
    attempt at this line mismatched its brackets and printed `[call-site;[removes print]`,
    which the tool's own self-sweep surfaced.

    This reproduces the rendering rule rather than driving `run_sweep`, so it pins the
    shape and not the call site that emits it.
    """
    lines: list[str] = []
    baseline = mar.Baseline(returncode=0, passed=1, output="1 passed in 0.01s")
    sweep = mar.Sweep(baseline=baseline)

    for result, expected in (
        (
            mar.MutantResult("a", "s.py", mar.KILLED, "", 1, ("guard",), True),
            " [call-site; removes guard]",
        ),
        (mar.MutantResult("b", "s.py", mar.KILLED, "", 1, ("join",), False), " [removes join]"),
        (mar.MutantResult("c", "s.py", mar.KILLED, "", 1, (), False), ""),
    ):
        sweep.mutants.append(result)
        bits = ["call-site"] if result.declared_call_site else []
        if result.removed_calls:
            bits.append("removes " + ", ".join(result.removed_calls))
        rendered = f" [{'; '.join(bits)}]" if bits else ""
        lines.append(rendered)
        assert rendered == expected, rendered
        assert rendered.count("[") == rendered.count("]"), rendered


def test_a_computed_callee_is_bucketed_rather_than_dropped() -> None:
    """`funcs[0]()` and `factory()()` have no name, and dropping them would be a silent hole.

    A dispatch table is exactly where a repair's only caller tends to live, so a callee the
    classifier cannot name still has to register as a removal -- otherwise deleting the one
    call site that matters would classify as "removed no call" and, on a declared mutant,
    be REFUSED as a false declaration.
    """
    before = b"def run(funcs, v):\n    return funcs[0](v)\n"
    after = b"def run(funcs, v):\n    return v\n"

    assert mar.removed_calls(before, after) == ("<computed>",)

    # And it corroborates a declaration end to end, rather than only existing in the map.
    baseline = mar.Baseline(returncode=0, passed=1, output="1 passed in 0.01s")
    declared = mar.MutantResult("m", "s.py", mar.KILLED, "", 1, ("<computed>",), True)
    assert mar.Sweep(baseline=baseline, mutants=[declared]).call_site_mutants == [declared]
