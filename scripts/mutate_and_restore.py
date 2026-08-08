#!/usr/bin/env python3
"""Run a mutation sweep that cannot report a kill it did not earn.

A sweep is a verdict about other code, so a sweep that cannot fail is the same
shape as a gate that cannot fail. Hand-authored inline sweeps have been the norm
here, and one of them reported NINE FALSE KILLS: `python3 -m pytest -q $T` with
two space-separated paths in `T`, which zsh does not word-split, so pytest
received one nonexistent path, exited non-zero, and every mutant read as
`killed`. Re-run correctly, three of nine had SURVIVED.

Three properties, each narrower than "this cannot be fooled":

1. **No kill without an earned baseline.** The unmutated tree must first report
   a PASSING TEST COUNT. A non-zero exit, an unparseable summary, or zero tests
   collected all refuse the whole sweep before any mutant is applied.
2. **No kill without evidence a TEST failed.** A bare non-zero exit is not a
   kill: a syntax error from the replacement, a collection error, an exit-5 with
   nothing collected, or a crashed runner all exit non-zero without any test
   catching anything. A kill needs a reported failure count AND a run that
   accounts for the baseline's tests, or the mutant is REFUSED. Reading a bare
   exit code as a kill is the very defect this file exists to end, so it is not
   reproduced per-mutant here.
3. **Restore runs in a `finally` that covers the write itself**, including when
   the test command raises, and the restoration is VERIFIED by comparing bytes.
   It is not unconditional: a filesystem that refuses the write back is reported
   loudly with its own exit code rather than silently.

A mutant whose `find` text is absent, or present more than once, is refused
rather than counted: an ambiguous edit that silently hit the wrong occurrence
would be a kill nobody can attribute.
"""

from __future__ import annotations

import argparse
import glob as globlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

PASSED_RE = re.compile(r"(\d+) passed")
FAILED_RE = re.compile(r"(\d+) failed")
ERROR_RE = re.compile(r"(\d+) error")
NO_TESTS_RE = re.compile(r"no tests ran", re.IGNORECASE)
# A summary line carries counts AND a duration. Scanning the whole transcript
# instead matched these words inside a failing test's echoed source -- and this
# runner's own test file contains the literals, so a real kill read as REFUSED.
SUMMARY_RE = re.compile(r"in \d+(?:\.\d+)?s", re.IGNORECASE)

KILLED = "killed"
SURVIVED = "survived"
REFUSED = "refused"


class SweepError(Exception):
    """A refusal the caller must see rather than a result it can misread."""


@dataclass
class Baseline:
    returncode: int
    passed: int | None
    output: str
    refusal: str | None = None

    @property
    def earned(self) -> bool:
        return self.refusal is None


@dataclass
class MutantResult:
    id: str
    path: str
    verdict: str
    detail: str = ""
    returncode: int | None = None


@dataclass
class Sweep:
    baseline: Baseline
    mutants: list[MutantResult] = field(default_factory=list)

    @property
    def survived(self) -> list[MutantResult]:
        return [m for m in self.mutants if m.verdict == SURVIVED]

    @property
    def refused(self) -> list[MutantResult]:
        return [m for m in self.mutants if m.verdict == REFUSED]


def summary_line(output: str) -> str | None:
    """Return the runner's last summary line, or None if it printed none.

    Counts must be read from the summary ALONE. Scanning the whole transcript
    let a failing test's echoed source supply the evidence -- in both directions:
    a stray `no tests ran` turned a real kill into a refusal, and a stray
    `N failed` could manufacture a kill from a run where nothing failed.
    """
    for line in reversed(output.splitlines()):
        stripped = line.strip()
        if not SUMMARY_RE.search(stripped):
            continue
        if NO_TESTS_RE.search(stripped) or PASSED_RE.search(stripped) or FAILED_RE.search(stripped) or ERROR_RE.search(stripped):
            return stripped
    return None


def parse_passed(output: str) -> int | None:
    """Return the passing test count the runner's SUMMARY reported, else None.

    None is not zero. A runner whose summary we cannot read has not told us its
    baseline held, and the sweep refuses on it -- which is the whole point.
    """
    line = summary_line(output)
    if line is None:
        return None
    if NO_TESTS_RE.search(line):
        return 0
    match = PASSED_RE.search(line)
    return int(match.group(1)) if match else 0


def run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True)


def measure_baseline(command: list[str], cwd: Path) -> Baseline:
    """Establish that the unmutated tree passes, and by how many tests."""
    completed = run_command(command, cwd)
    output = completed.stdout + completed.stderr
    passed = parse_passed(output)
    refusal: str | None = None
    if completed.returncode != 0:
        failed = FAILED_RE.search(output)
        refusal = (
            f"baseline test command exited {completed.returncode}"
            + (f" with {failed.group(1)} failing" if failed else "")
            + "; every mutant would read as killed against it"
        )
    elif passed is None:
        refusal = (
            "baseline produced no readable passing count; an unreadable summary "
            "is indistinguishable from a sweep that killed everything"
        )
    elif passed == 0:
        refusal = "baseline collected 0 tests; there is nothing for a mutant to kill"
    return Baseline(returncode=completed.returncode, passed=passed, output=output, refusal=refusal)


def invalidate_bytecode(path: Path) -> None:
    """Drop the cached bytecode for a source file we just rewrote.

    Found by this file's own tests. CPython invalidates a `.pyc` by comparing the
    source's SIZE and its mtime truncated to whole seconds, so a same-length edit
    applied within the same second -- `a + b` -> `a * b`, the most ordinary mutant
    there is -- leaves the stale bytecode valid. The unmutated code then runs, the
    suite stays green, and the mutant is reported SURVIVED. That is a sweep
    reporting a verdict about code that never executed, which is the defect this
    runner exists to make unreachable, reproduced inside the runner itself.
    """
    if path.suffix != ".py":
        return
    # NOT `cache_from_source` alone: that resolves against THIS process's
    # `cache_tag`, while the plan's `test_command` is an arbitrary interpreter
    # (a venv, `uv run`, another minor version). Clearing only our own tag leaves
    # the test runner's stale .pyc valid and the mutation unexecuted.
    for cached in path.parent.glob(f"__pycache__/{globlib.escape(path.stem)}.*.pyc"):
        cached.unlink(missing_ok=True)


def apply_mutation(path: Path, find: str, replace: str) -> bytes:
    """Replace exactly one occurrence, returning the original bytes for restore."""
    original = path.read_bytes()
    text = original.decode("utf-8")
    occurrences = text.count(find)
    if occurrences == 0:
        raise SweepError("mutation text not found; the mutant would be a no-op reported as killed")
    if occurrences > 1:
        raise SweepError(
            f"mutation text occurs {occurrences} times; an ambiguous edit produces a kill "
            "nobody can attribute to a line"
        )
    path.write_bytes(text.replace(find, replace, 1).encode("utf-8"))
    invalidate_bytecode(path)
    return original


def restore(path: Path, original: bytes) -> None:
    """Put the file back and PROVE it, rather than assuming the write landed."""
    path.write_bytes(original)
    if path.read_bytes() != original:
        raise SweepError(f"failed to restore {path}; the worktree is left mutated")
    invalidate_bytecode(path)


def classify_mutant_run(completed: subprocess.CompletedProcess, baseline: Baseline) -> tuple[str, str]:
    """Decide killed / survived / refused from EVIDENCE, not from the exit byte.

    `#565` was a broken run read as a clean sweep. Reading a mutant's bare
    non-zero exit as a kill is the same mistake one level in: a replacement that
    does not parse, a collection error, or a crashed runner all exit non-zero
    with no test having caught anything.
    """
    line = summary_line(completed.stdout + completed.stderr)
    if line is None:
        return REFUSED, (
            f"the mutated run exited {completed.returncode} and printed no readable summary; "
            "there is no evidence to call this either way"
        )
    passed = parse_passed(line) or 0
    failed_match = FAILED_RE.search(line)
    failed = int(failed_match.group(1)) if failed_match else 0
    accounted = passed + failed
    # SURVIVED is a verdict about other code exactly as much as KILLED is, so it
    # gets the same scope accounting. A mutant that shrinks collection while
    # staying green would otherwise be reported as an uncaught survivor.
    if baseline.passed is not None and accounted < baseline.passed:
        return REFUSED, (
            f"the mutated run accounted for {accounted} of {baseline.passed} baseline tests; "
            "the scope shrank rather than the mutation being resolved either way"
        )
    if completed.returncode == 0:
        return SURVIVED, "the suite stayed green with this code mutated"
    if failed:
        # Checked BEFORE the error branch: pytest reports a teardown/fixture
        # error alongside a genuine `failed`, and refusing that would throw away
        # a real kill.
        return KILLED, ""
    errors = ERROR_RE.search(line)
    if errors:
        return REFUSED, (
            f"the mutated run reported {errors.group(1)} error(s) and no failure, so tests did "
            "not run to a verdict; a broken run is not a kill"
        )
    return REFUSED, (
        f"the mutated run exited {completed.returncode} without reporting any test failure; "
        "a non-zero exit alone is the defect this runner exists to stop"
    )


def run_mutant(
    spec: dict, command: list[str], repo_root: Path, baseline: Baseline
) -> MutantResult:
    # Key guard FIRST: a mis-keyed plan (`replacement`, `to`) would otherwise
    # become a silent DELETION mutant, and a missing `path`/`find` would raise a
    # bare KeyError that aborts the whole sweep and discards collected results.
    missing_keys = [key for key in ("path", "find", "replace") if key not in spec]
    if missing_keys:
        label = spec.get("id") or spec.get("path", "<unnamed>")
        return MutantResult(label, spec.get("path", "?"), REFUSED, f"plan entry is missing {missing_keys}")
    path = (repo_root / spec["path"]).resolve()
    mutant_id = spec.get("id") or f"{spec['path']}:{spec['find'][:40]}"
    if not path.is_relative_to(repo_root.resolve()):
        return MutantResult(mutant_id, spec["path"], REFUSED, "target escapes the repo root")
    if not path.is_file():
        return MutantResult(mutant_id, spec["path"], REFUSED, "target file does not exist")
    # Read the pristine bytes BEFORE any write, so the restore in `finally`
    # covers the write itself. Taking them from apply_mutation's return left a
    # window where a failure after the write had no copy to restore from.
    original = path.read_bytes()
    try:
        apply_mutation(path, spec["find"], spec["replace"])
    except SweepError as exc:
        restore(path, original)
        return MutantResult(mutant_id, spec["path"], REFUSED, str(exc))
    except BaseException:
        # apply_mutation writes and THEN invalidates bytecode; a failure between
        # those two would otherwise leave the tree mutated with no restore.
        restore(path, original)
        raise
    try:
        completed = run_command(command, repo_root)
        verdict, detail = classify_mutant_run(completed, baseline)
        return MutantResult(mutant_id, spec["path"], verdict, detail, completed.returncode)
    finally:
        restore(path, original)


def run_sweep(plan: dict, repo_root: Path, emit=print) -> Sweep:
    command = plan["test_command"]
    baseline = measure_baseline(command, repo_root)
    # The count goes out BEFORE the first mutant, so a reader of a truncated log
    # still sees what the sweep was measured against.
    if baseline.earned:
        emit(f"baseline: {baseline.passed} passed")
    else:
        emit(f"baseline REFUSED: {baseline.refusal}")
        return Sweep(baseline=baseline)
    sweep = Sweep(baseline=baseline)
    for spec in plan["mutants"]:
        result = run_mutant(spec, command, repo_root, baseline)
        sweep.mutants.append(result)
        emit(f"  {result.verdict:<8} {result.id}" + (f" -- {result.detail}" if result.detail else ""))
    return sweep


def render(sweep: Sweep) -> dict:
    return {
        "baseline": {
            "earned": sweep.baseline.earned,
            "passed": sweep.baseline.passed,
            "returncode": sweep.baseline.returncode,
            "refusal": sweep.baseline.refusal,
        },
        "mutants": [
            {
                "id": m.id,
                "path": m.path,
                "verdict": m.verdict,
                "detail": m.detail,
                "returncode": m.returncode,
            }
            for m in sweep.mutants
        ],
        "killed": sum(1 for m in sweep.mutants if m.verdict == KILLED),
        "survived": len(sweep.survived),
        "refused": len(sweep.refused),
    }


def exit_code(sweep: Sweep) -> int:
    if not sweep.baseline.earned:
        return 2
    if sweep.survived or sweep.refused:
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a mutation sweep that refuses to report a kill without a passing baseline."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--plan",
        type=Path,
        required=True,
        help='JSON: {"test_command": [...], "mutants": [{"path":..., "find":..., "replace":...}]}',
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    lines: list[str] = []
    emit = lines.append if args.json else print
    try:
        sweep = run_sweep(plan, repo_root, emit=emit)
    except SweepError as exc:
        print(f"mutate-and-restore: {exc}", file=sys.stderr)
        return 2
    except BaseException as exc:  # noqa: BLE001 - a crash must not read as a result
        # Exit 3, never 1. A crash that exits 1 is indistinguishable from
        # "survivors found" to any `if ! cmd` caller, which is how a broken
        # sweep gets read as a report.
        print(f"mutate-and-restore CRASHED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 3
    payload = render(sweep)
    if args.json:
        print(json.dumps(payload, indent=2))
    elif sweep.baseline.earned:
        print(
            f"mutate-and-restore: {payload['killed']} killed, {payload['survived']} survived, "
            f"{payload['refused']} refused, over a baseline of {sweep.baseline.passed} passing tests"
        )
    return exit_code(sweep)


if __name__ == "__main__":
    raise SystemExit(main())
