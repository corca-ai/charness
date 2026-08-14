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
3. **Restore owns the whole mutation lifecycle.** A `finally` covers the write
   itself when Python regains control, SIGINT/SIGTERM are converted into that
   restoring path, and a durable repo-local journal written before each mutation
   makes an untrappable SIGKILL detectable and explicitly recoverable. Restoration
   is VERIFIED by comparing bytes before the journal is cleared. It is not
   unconditional: a filesystem that refuses the write back is reported loudly
   with its own exit code rather than silently.

A mutant whose `find` text is absent, or present more than once, is refused
rather than counted: an ambiguous edit that silently hit the wrong occurrence
would be a kill nobody can attribute.

A fourth property, mostly REPORTED rather than enforced: a sweep in which no
mutant was declared a CALL-SITE test says so out loud. `#564` measured three
repairs in one goal that were pinned only at their own function -- delete the
caller and the whole suite stayed green while the repair was dead in production,
and none of the three was visible in the diff. That is also why a second review
round does not reliably catch it: the code reads correctly.

A plan entry opts in with `"call_site": true`, and the tool checks that claim
against the edit: a declared call-site mutant that removed NO call is REFUSED.
That is the one place there are teeth here, and it is a fact the runner can
establish. Whether a call-site mutant was WARRANTED is not -- a sweep over a
constant table has no call to delete -- so the absence is stated and the
judgement is left with the reader.

The declaration is required because INFERENCE was tried and is wrong in both
directions. Attribute calls are keyed by attribute, so an incidental `.join` or
`.elements` removal in a body mutant counted as caller-side proof and SILENCED
this warning. A signal that unreliable must not be allowed to suppress a
finding, so removed calls are reported as corroborating evidence and never as
the trigger.
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

from mutation_plan_semantics import MutationPlanError, removed_calls
from mutation_plan_semantics import mutation_bytes as plan_mutation_bytes
from mutation_recovery import (
    MutationRecovery,
    RecoveryError,
    SweepTerminated,
    atomic_write_bytes,
    run_mutation_command,
    termination_handlers,
)

from yaml_output import emit_yaml

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


SweepError = RecoveryError


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
    # None means "not classified" (the mutant was refused before it was applied, or one
    # side would not parse) and is deliberately distinct from `()`, which means "applied,
    # parsed, removed no call". Collapsing them would let an unclassifiable sweep read as
    # a sweep that looked and found nothing -- this repo's own recurring shape.
    removed_calls: tuple[str, ...] | None = None
    # What the PLAN asserted (`"call_site": true`), kept separate from what the edit did.
    # The pair is the point: a declaration nobody checks is the shape this repo keeps
    # finding, and evidence nobody declared cannot tell an intended caller test from an
    # incidental `.join` removal.
    declared_call_site: bool = False


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

    @property
    def call_site_mutants(self) -> list[MutantResult]:
        """Mutants the PLAN declared as call-site tests AND whose edit removed a call.

        Declaration plus evidence, never evidence alone. Inferring the answer from removed
        calls was tried and is wrong in both directions: `return tuple(sorted(x.elements()))`
        -> `return ()` removes `elements`, so a pure body mutant on a pure helper counted
        as caller-side proof, while a `super().__init__()` deletion -- the textbook dead
        repair -- counted as nothing. An unreliable signal that SILENCES a warning is worse
        than no signal, so the author declares the intent and the tool checks the edit
        against it.

        AND THE RUN MUST HAVE REACHED A VERDICT. A REFUSED mutant established nothing: no
        test ran to an answer, which is the whole premise of property 2 above. Counting one
        as "the caller-side question was asked" silences the non-claim on a mutant that
        produced no answer -- this file's own class, on the new axis. SURVIVED is different
        and is deliberately counted: the question WAS asked and answered badly, and the
        survivor plus the non-zero exit already carry that.
        """
        return [
            m
            for m in self.mutants
            if m.declared_call_site and m.removed_calls and m.verdict in (KILLED, SURVIVED)
        ]


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


def mutation_bytes(original: bytes, find: str, replace: str) -> bytes:
    try:
        return plan_mutation_bytes(original, find, replace)
    except MutationPlanError as exc:
        raise SweepError(str(exc)) from exc


def apply_mutation(path: Path, find: str, replace: str) -> bytes:
    """Replace exactly one occurrence, returning the original bytes for restore."""
    original = path.read_bytes()
    atomic_write_bytes(path, mutation_bytes(original, find, replace))
    invalidate_bytecode(path)
    return original


def restore(path: Path, original: bytes) -> None:
    """Put the file back and PROVE it, rather than assuming the write landed."""
    atomic_write_bytes(path, original)
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
    # Read BEFORE the early returns, so `declared_call_site` reports what the plan said
    # even for a mutant refused on its path or its find text. It used to be read after
    # them, so a declared mutant with a typo'd `find` reported `declared_call_site: false`
    # -- the field stating the opposite of the plan to the author debugging that typo.
    #
    # A non-bool is REFUSED, not coerced. `bool("false")` is True, so a templated plan
    # could declare the opposite of what its author meant and silence the non-claim;
    # every other mis-keyed plan entry in this file is refused loudly rather than guessed.
    declared_raw = spec.get("call_site", False)
    if not isinstance(declared_raw, bool):
        return MutantResult(
            spec.get("id") or spec["path"], spec["path"], REFUSED,
            f"`call_site` must be a boolean, got {declared_raw!r}; a truthy string would "
            "declare a caller test nobody wrote and silence the caller-side non-claim",
        )
    declared = declared_raw
    path = (repo_root / spec["path"]).resolve()
    mutant_id = spec.get("id") or f"{spec['path']}:{spec['find'][:40]}"
    if not path.is_relative_to(repo_root.resolve()):
        return MutantResult(mutant_id, spec["path"], REFUSED, "target escapes the repo root", None, None, declared)
    if not path.is_file():
        return MutantResult(mutant_id, spec["path"], REFUSED, "target file does not exist", None, None, declared)
    # Read the pristine bytes BEFORE any write, so the restore in `finally`
    # covers the write itself. Taking them from apply_mutation's return left a
    # window where a failure after the write had no copy to restore from.
    original = path.read_bytes()
    try:
        expected_mutated = mutation_bytes(original, spec["find"], spec["replace"])
    except SweepError as exc:
        return MutantResult(mutant_id, spec["path"], REFUSED, str(exc), None, None, declared)
    recovery = MutationRecovery(repo_root)
    journal_id = recovery.begin(path, original, expected_mutated)
    try:
        apply_mutation(path, spec["find"], spec["replace"])
    except SweepError as exc:
        restore(path, original)
        recovery.clear(journal_id)
        return MutantResult(mutant_id, spec["path"], REFUSED, str(exc), None, None, declared)
    except BaseException:
        # apply_mutation writes and THEN invalidates bytecode; a failure between
        # those two would otherwise leave the tree mutated with no restore.
        restore(path, original)
        recovery.clear(journal_id)
        raise
    try:
        # INSIDE the restoring `try`, not above it. Sitting between `apply_mutation` and
        # this block left a window the module's own property 3 says does not exist: a
        # `RecursionError` from `ast.parse` on deeply nested source, or an `OSError` on
        # the read, would escape with the file still mutated. That is `#573`, which this
        # session hit three times, re-opened by a REPORTING feature.
        #
        # Read back the file we just wrote rather than re-deriving the mutated text: a
        # second in-memory `replace` would copy `apply_mutation`'s logic with nothing
        # reconciling the two, and would classify an edit that never reached disk.
        removed = removed_calls(original, path.read_bytes())
        if declared and removed == ():
            return MutantResult(
                mutant_id, spec["path"], REFUSED,
                "declared `call_site` but the edit removed no call; a false declaration is "
                "worse than none, because it SILENCES the caller-side non-claim",
                None, removed, declared,
            )
        completed = run_mutation_command(command, repo_root, recovery, journal_id)
        verdict, detail = classify_mutant_run(completed, baseline)
        return MutantResult(mutant_id, spec["path"], verdict, detail, completed.returncode, removed, declared)
    finally:
        restore(path, original)
        # The journal is cleared only AFTER restore's byte-for-byte verification.
        # A failed restore therefore leaves the recovery consumer armed.
        recovery.clear(journal_id)


def run_sweep(plan: dict, repo_root: Path, emit=print) -> Sweep:
    MutationRecovery(repo_root).assert_clear()
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
        # The removed callees go in the streamed progress line, not only in the final
        # payload. Without them an operator reads `1 call-site` and cannot tell an
        # intended caller test from an incidental `.join` -- which is exactly how the
        # inferred version of this feature went wrong, invisibly, in its own self-sweep.
        # The DECLARATION is the discriminating fact under the current design, so it is
        # what the progress line must show; removals alone rendered a declared caller
        # test and an incidental `.join` identically, leaving the `N call-site` count
        # unauditable until the sweep finished.
        bits = ["call-site"] if result.declared_call_site else []
        if result.removed_calls:
            bits.append("removes " + ", ".join(result.removed_calls))
        calls = f" [{'; '.join(bits)}]" if bits else ""
        emit(f"  {result.verdict:<8} {result.id}{calls}" + (f" -- {result.detail}" if result.detail else ""))
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
                "removed_calls": list(m.removed_calls) if m.removed_calls is not None else None,
                "declared_call_site": m.declared_call_site,
            }
            for m in sweep.mutants
        ],
        "killed": sum(1 for m in sweep.mutants if m.verdict == KILLED),
        "survived": len(sweep.survived),
        "refused": len(sweep.refused),
        "call_site_mutants": len(sweep.call_site_mutants),
        "call_site_non_claim": call_site_non_claim(sweep),
    }


def call_site_non_claim(sweep: Sweep) -> str | None:
    """What a clean sweep with no call-site mutant does NOT establish (`#564`).

    Reported, never refused, and the boundary is deliberate. The tool can see that no
    mutant was DECLARED a call-site test; it CANNOT see whether one was warranted -- a
    sweep over a constant table or a pure predicate legitimately has none. Refusing on
    that would make the runner assert something about the plan it never established,
    which is the class it exists to stop, so this states the gap and leaves the judgement
    with the reader. P5: force the question, do not declare completion.

    Silenced ONLY by a declaration the edit corroborates. An earlier cut let the inferred
    removed-call count silence it, which meant an incidental `.join` deletion in a body
    mutant turned the warning off -- the tool suppressing its own finding on evidence that
    did not mean what it counted.
    """
    # An EMPTY plan still gets the non-claim. It used to be silenced alongside an unearned
    # baseline, which made the emptiest possible sweep -- `0 killed, 0 survived`, exit 0,
    # no warning -- the most unearned clean report this tool can print, while the module
    # docstring promised that a sweep with no declared call-site test says so out loud.
    # An unearned baseline is different: it already refuses loudly and prints no counts.
    if not sweep.baseline.earned:
        return None
    if sweep.call_site_mutants:
        return None
    # Says DECLARED, because that is the condition above. The first wording said "no
    # mutant deleted a call site" -- vocabulary left over from the inference design -- and
    # this tool's own suite has a run where that sentence is printed while the per-mutant
    # line reads `[removes join, str]`. Two contradictory statements in one report, and
    # the operator-facing one was the false one, on a surface whose whole thesis is not
    # reporting what it did not establish.
    return (
        "no mutant was DECLARED a call-site test (`\"call_site\": true`), so a clean result "
        "here says nothing about whether these repairs are still REACHED in production: a "
        "repair pinned only at its own function survives deletion of its caller with the "
        "suite green (#564, measured three times in one goal, none visible in the diff)"
    )


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
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument(
        "--plan",
        type=Path,
        help=(
            'JSON: {"test_command": [...], "mutants": [{"path":..., "find":..., "replace":..., '
            '"call_site": true}]}. Set `call_site` on the mutant that deletes the repair\'s '
            "CALLER; without one the sweep reports what it did not establish (#564)."
        ),
    )
    action.add_argument(
        "--check-recovery",
        action="store_true",
        help="exit 2 when an interrupted mutation journal requires operator attention",
    )
    action.add_argument(
        "--recover",
        action="store_true",
        help="restore the exact interrupted mutation when the target still matches its journal",
    )
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    recovery = MutationRecovery(repo_root)
    if args.check_recovery:
        if recovery.pending:
            print(
                "mutate-and-restore: interrupted mutation recovery is REQUIRED; "
                f"record: {recovery.state_dir}; run with --recover",
                file=sys.stderr,
            )
            return 2
        print("mutate-and-restore: no interrupted mutation recovery is pending")
        return 0
    if args.recover:
        try:
            print(f"mutate-and-restore: {recovery.recover(restore)}")
        except SweepError as exc:
            print(f"mutate-and-restore: {exc}", file=sys.stderr)
            return 2
        return 0
    assert args.plan is not None
    plan = json.loads(args.plan.read_text(encoding="utf-8"))

    # Progress goes to STDERR now that stdout carries one YAML document. The stream
    # matters: a sweep is long, and the baseline count plus the per-mutant verdicts
    # are what a reader of a truncated or still-running log has. Discarding them --
    # which is what the retired `--json` mode did, appending them to a list nothing
    # printed -- would make an interrupted sweep unreadable.
    def emit(line: str) -> None:
        print(line, file=sys.stderr)

    try:
        with termination_handlers():
            sweep = run_sweep(plan, repo_root, emit=emit)
    except SweepTerminated as exc:
        sys.stdout.flush()
        print(
            f"mutate-and-restore INTERRUPTED by signal {exc.signum}; any active mutation was restored",
            file=sys.stderr,
        )
        return 128 + exc.signum
    except SweepError as exc:
        sys.stdout.flush()
        print(f"mutate-and-restore: {exc}", file=sys.stderr)
        return 2
    except BaseException as exc:  # noqa: BLE001 - a crash must not read as a result
        # Exit 3, never 1. A crash that exits 1 is indistinguishable from
        # "survivors found" to any `if ! cmd` caller, which is how a broken
        # sweep gets read as a report.
        # Same flush, same reason as the non-claim below: without it a `2>&1` log shows
        # the crash ABOVE the baseline and per-mutant lines that preceded it, reading as
        # a crash before the sweep ever started.
        sys.stdout.flush()
        print(f"mutate-and-restore CRASHED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 3
    payload = render(sweep)
    # Unconditional YAML. The retired summary line was a strict projection of
    # `killed`, `survived`, `refused`, `call_site_mutants`, and `baseline.passed`.
    emit_yaml(payload)
    if sweep.baseline.earned and payload["call_site_non_claim"]:
        # Flushed before the stderr write, because the ordering claim this comment used to
        # make was false: under `cmd > f 2>&1` stdout is BLOCK-buffered while stderr is
        # not, so the non-claim landed in the log ABOVE the summary it qualifies. Stderr
        # is still the right stream -- a `2>&1` gate log keeps it and a bare `$(cmd)`
        # capture must not silently swallow a warning into a variable. It is ALSO in the
        # payload as `call_site_non_claim`; a reader who parses gets it either way, and a
        # reader who only watches the terminal still cannot miss it.
        sys.stdout.flush()
        print(f"mutate-and-restore NON-CLAIM: {payload['call_site_non_claim']}", file=sys.stderr)
    return exit_code(sweep)


if __name__ == "__main__":
    raise SystemExit(main())
