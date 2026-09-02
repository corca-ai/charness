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
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.core.subprocess_guard import run_monitored_phase  # noqa: E402
from scripts.mutation import mutation_test_reporters as _reporters  # noqa: E402
from scripts.mutation.mutation_plan_semantics import (  # noqa: E402
    MutationPlanError,
    removed_calls,
)
from scripts.mutation.mutation_plan_semantics import (  # noqa: E402
    mutation_bytes as plan_mutation_bytes,  # noqa: E402
)
from scripts.mutation.mutation_recovery import (  # noqa: E402
    MutationRecovery,
    RecoveryError,
    SweepTerminated,
    atomic_write_bytes,
    run_mutation_command,
    termination_handlers,
)
from scripts.runtime_bootstrap import import_repo_module  # noqa: E402
from scripts.yaml_output import emit_yaml  # noqa: E402

_sweep_report = import_repo_module(__file__, "scripts.mutation.mutation_sweep_report")
render = _sweep_report.render

# How to READ a runner's count report lives in `mutation_test_reporters` (#689):
# the three properties above are runner-independent, but the pytest summary shape
# was hardcoded, so no Node repository could use this harness.
#
# There is deliberately NO re-export block here. One was written -- the five
# regexes plus `DEFAULT_REPORTER`, justified as "call sites in this module's own
# test file bind them here" -- and a fresh-eye round grepped: nothing read any of
# them, in this module or anywhere else. Six dead aliases whose own comment
# asserted a relationship that did not exist, on the module whose stated rule is
# that an unread alias is a live trap. Reach them through `_reporters`.

KILLED = "killed"
SURVIVED = "survived"
REFUSED = "refused"


SweepError = RecoveryError


@dataclass
class Baseline:
    #: `None` when NO baseline command was spawned. A plan refused for its own
    #: misconfiguration never measured the tree, and reporting `0` there let a
    #: consumer read "the tree is green" out of a run that established nothing --
    #: this file's own class, on the reporting side.
    returncode: int | None
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


def parse_passed(output: str, reporter=_reporters.PytestReporter) -> int | None:
    """Return the passing test count the runner's SUMMARY reported, else None.

    None is not zero. A runner whose summary we cannot read has not told us its
    baseline held, and the sweep refuses on it -- which is the whole point.
    """
    counts = reporter.read(output)
    return None if counts is None else counts.passed


def run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return run_monitored_phase(
        command,
        cwd=cwd,
        phase="mutation-baseline",
        timeout_seconds=None,
        capture=True,
    ).completed_process()


def measure_baseline(command: list[str], cwd: Path, reporter=_reporters.PytestReporter) -> Baseline:
    """Establish that the unmutated tree passes, and by how many tests."""
    completed = run_command(command, cwd)
    output = completed.stdout + completed.stderr
    counts = reporter.read(output)
    passed = None if counts is None else counts.passed
    refusal: str | None = None
    if completed.returncode != 0:
        failed = counts.failed if counts else 0
        refusal = (
            f"baseline test command exited {completed.returncode}"
            + (f" with {failed} failing" if failed else "")
            + "; every mutant would read as killed against it"
        )
    elif passed is None:
        # The measured #689 refusal stopped at this first clause, on a Node tree
        # whose baseline was GREEN (`returncode: 0`). Naming which reporter looked,
        # what it looked for, and which registered reporter CAN read these bytes is
        # the difference between a refusal and a dead end.
        refusal = (
            "baseline produced no readable passing count; an unreadable summary "
            "is indistinguishable from a sweep that killed everything -- "
            + _reporters.unreadable_refusal(reporter.name, output)
        )
    elif passed == 0:
        refusal = "baseline collected 0 tests; there is nothing for a mutant to kill"
    return Baseline(returncode=completed.returncode, passed=passed, output=output, refusal=refusal)


def bytecode_cache_paths(path: Path) -> tuple[Path, ...]:
    """Return local and externally-prefixed bytecode paths for one source file."""
    if path.suffix != ".py":
        return ()
    directories = [path.parent / "__pycache__"]
    prefix = os.environ.get("PYTHONPYCACHEPREFIX") or getattr(sys, "pycache_prefix", None)
    if prefix:
        external = Path(prefix).expanduser().resolve() / path.resolve().as_posix().lstrip("/")
        directories.append(external.parent)
    cached: list[Path] = []
    seen: set[Path] = set()
    for directory in directories:
        if directory in seen:
            continue
        seen.add(directory)
        cached.extend(directory.glob(f"{globlib.escape(path.stem)}.*.pyc"))
    return tuple(cached)


def invalidate_bytecode(path: Path) -> None:
    """Drop cached bytecode, whether Python stores it in-tree or by external prefix.

    Found by this file's own tests. CPython invalidates a `.pyc` by comparing the
    source's SIZE and its mtime truncated to whole seconds, so a same-length edit
    applied within the same second -- `a + b` -> `a * b`, the most ordinary mutant
    there is -- leaves the stale bytecode valid. The unmutated code then runs, the
    suite stays green, and the mutant is reported SURVIVED. That is a sweep
    reporting a verdict about code that never executed, which is the defect this
    runner exists to make unreachable, reproduced inside the runner itself.
    """
    # NOT `cache_from_source` alone: that resolves against THIS process's
    # `cache_tag`, while the plan's `test_command` is an arbitrary interpreter
    # (a venv, `uv run`, another minor version). Clearing every matching tag in
    # both possible storage roots leaves no stale test-runner bytecode valid.
    for cached in bytecode_cache_paths(path):
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


def classify_mutant_run(
    completed: subprocess.CompletedProcess, baseline: Baseline, reporter=_reporters.PytestReporter
) -> tuple[str, str]:
    """Decide killed / survived / refused from EVIDENCE, not from the exit byte.

    `#565` was a broken run read as a clean sweep. Reading a mutant's bare
    non-zero exit as a kill is the same mistake one level in: a replacement that
    does not parse, a collection error, or a crashed runner all exit non-zero
    with no test having caught anything.
    """
    output = completed.stdout + completed.stderr
    counts = reporter.read(output)
    if counts is None:
        return REFUSED, (
            f"the mutated run exited {completed.returncode} and printed no readable summary; "
            "there is no evidence to call this either way -- "
            + _reporters.unreadable_refusal(reporter.name, output)
        )
    passed = counts.passed
    failed = counts.failed
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
    if counts.errors:
        return REFUSED, (
            f"the mutated run reported {counts.errors} error(s) and no failure, so tests did "
            "not run to a verdict; a broken run is not a kill"
        )
    return REFUSED, (
        f"the mutated run exited {completed.returncode} without reporting any test failure; "
        "a non-zero exit alone is the defect this runner exists to stop"
    )


def run_mutant(
    spec: dict,
    command: list[str],
    repo_root: Path,
    baseline: Baseline,
    reporter=_reporters.PytestReporter,
) -> MutantResult:
    # Key guard FIRST: a mis-keyed plan (`replacement`, `to`) would otherwise
    # become a silent DELETION mutant, and a missing `path`/`find` would raise a
    # bare KeyError that aborts the whole sweep and discards collected results.
    missing_keys = [key for key in ("path", "find", "replace") if key not in spec]
    if missing_keys:
        label = spec.get("id") or spec.get("path", "<unnamed>")
        return MutantResult(
            label, spec.get("path", "?"), REFUSED, f"plan entry is missing {missing_keys}"
        )
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
            spec.get("id") or spec["path"],
            spec["path"],
            REFUSED,
            f"`call_site` must be a boolean, got {declared_raw!r}; a truthy string would "
            "declare a caller test nobody wrote and silence the caller-side non-claim",
        )
    declared = declared_raw
    path = (repo_root / spec["path"]).resolve()
    mutant_id = spec.get("id") or f"{spec['path']}:{spec['find'][:40]}"
    if not path.is_relative_to(repo_root.resolve()):
        return MutantResult(
            mutant_id, spec["path"], REFUSED, "target escapes the repo root", None, None, declared
        )
    if not path.is_file():
        return MutantResult(
            mutant_id, spec["path"], REFUSED, "target file does not exist", None, None, declared
        )
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
                mutant_id,
                spec["path"],
                REFUSED,
                "declared `call_site` but the edit removed no call; a false declaration is "
                "worse than none, because it SILENCES the caller-side non-claim",
                None,
                removed,
                declared,
            )
        completed = run_mutation_command(command, repo_root, recovery, journal_id)
        verdict, detail = classify_mutant_run(completed, baseline, reporter)
        return MutantResult(
            mutant_id, spec["path"], verdict, detail, completed.returncode, removed, declared
        )
    finally:
        restore(path, original)
        # The journal is cleared only AFTER restore's byte-for-byte verification.
        # A failed restore therefore leaves the recovery consumer armed.
        recovery.clear(journal_id)


def run_sweep(plan: dict, repo_root: Path, emit=print) -> Sweep:
    MutationRecovery(repo_root).assert_clear()
    command = plan["test_command"]
    # An unknown reporter name is REFUSED, never silently defaulted. A plan asking
    # for a reader this harness does not have, answered with pytest's, reports
    # `baseline REFUSED` on a healthy tree and blames the tree -- a proof surface
    # rendering a verdict about the code when the fault is its own configuration.
    requested = plan.get("reporter")
    reporter = _reporters.resolve(requested)
    if reporter is None:
        refusal = (
            f"plan requested reporter {requested!r}, which is not registered; "
            "available: " + ", ".join(f"`{name}`" for name in sorted(_reporters.REPORTERS))
        )
        emit(f"baseline REFUSED: {refusal}")
        return Sweep(baseline=Baseline(returncode=None, passed=None, output="", refusal=refusal))
    baseline = measure_baseline(command, repo_root, reporter)
    # The count goes out BEFORE the first mutant, so a reader of a truncated log
    # still sees what the sweep was measured against.
    if baseline.earned:
        emit(f"baseline: {baseline.passed} passed")
    else:
        emit(f"baseline REFUSED: {baseline.refusal}")
        return Sweep(baseline=baseline)
    sweep = Sweep(baseline=baseline)
    for spec in plan["mutants"]:
        result = run_mutant(spec, command, repo_root, baseline, reporter)
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
        emit(
            f"  {result.verdict:<8} {result.id}{calls}"
            + (f" -- {result.detail}" if result.detail else "")
        )
    return sweep


def call_site_non_claim(sweep: Sweep) -> str | None:
    return _sweep_report.call_site_non_claim(sweep)


def exit_code(sweep: Sweep) -> int:
    return _sweep_report.exit_code(sweep)


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
            'JSON: {"test_command": [...], "reporter": "pytest"|"node-test", '
            '"mutants": [{"path":..., "find":..., "replace":..., "call_site": true}]}. '
            "`reporter` selects how the runner's COUNTS are read and defaults to "
            "`pytest`; a Node repository needs `node-test`, or the sweep refuses a "
            "green baseline it cannot parse. Set `call_site` on the mutant that "
            "deletes the repair's CALLER; without one the sweep reports what it did "
            "not establish (#564)."
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
