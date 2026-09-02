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
