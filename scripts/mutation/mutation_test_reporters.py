"""How to read a test runner's own count report, per runner (#689).

`mutate_and_restore` refuses to report a kill it did not earn, and every one of
its three properties is stated in terms of COUNTS: a baseline must report a
passing count, a kill needs a reported failure count, and a mutant run must
account for the baseline's tests. Those are runner-independent ideas. What was
runner-dependent -- and hardcoded -- is how to READ them.

The hardcoded shape was pytest's: `1 failed, 2 passed in 0.10s`, one line
carrying counts AND a duration. `node --test` prints a trailing TAP block:

    1..2
    # tests 2
    # pass 2
    # fail 0
    # cancelled 0
    # duration_ms 67.239608

No line carries both, so the pytest reader finds no summary at all. Measured
against a two-test `node --test` fixture whose baseline is GREEN (`returncode:
0`), the sweep answered:

    baseline REFUSED: baseline produced no readable passing count; an unreadable
    summary is indistinguishable from a sweep that killed everything

That refusal is CORRECT for an unreadable baseline -- the defect is that the
baseline was unreadable, and that the refusal named no way out. The three Ceal
repositories are all Node and grew a repo-local substitute rather than use this.

## What a reporter owns, and what it does not

A reporter owns exactly one question: given a runner's combined output, what
counts did the runner REPORT, or is there no readable report at all? It does not
decide killed/survived/refused. That classification is the harness's, stays in
one place, and is unchanged by this seam -- which is the point, because it is
where the three properties actually live.

## The scoping rule is per-reporter, and it is load-bearing

Counts must come from the runner's own summary, never from a scan of the whole
transcript. That rule was learned twice here, in both directions: a stray
`no tests ran` inside an echoed failing test turned a real kill into a refusal,
and a stray `N failed` could manufacture a kill from a run where nothing failed.
This runner's own test file contains those literals.

Each reporter therefore carries its own scoping, and the two happen to rhyme:
pytest's summary is the last LINE carrying counts and a duration; node's is the
trailing BLOCK of `# key value` lines ending in `# duration_ms`. Anchoring on the
duration in both cases is not a coincidence -- it is the token a runner emits
once, at the end, and that an echoed test body has no reason to contain.

## One place this reader looks OUTSIDE the summary, and why

`node --test` has no error concept: a test FILE that fails to load is reported as
a failing TEST. Measured, a module-breaking mutant and a real kill emit
byte-identical summaries, so no count-only rule can separate them. The one signal
that does is file-level -- node prints the file process's `exitCode:` in its TAP
diagnostic -- and it lives in the transcript, not the summary.

Reading it there is acceptable HERE and refused for counts because the direction
of error differs: over-counting file failures turns a kill into a REFUSAL, and can
never manufacture one. It costs a false stop; it cannot grant a false pass.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

#: pytest, unchanged from the hardcoded originals so this extraction cannot
#: alter a single existing verdict.
PASSED_RE = re.compile(r"(\d+) passed")
FAILED_RE = re.compile(r"(\d+) failed")
ERROR_RE = re.compile(r"(\d+) error")
NO_TESTS_RE = re.compile(r"no tests ran", re.IGNORECASE)
SUMMARY_RE = re.compile(r"in \d+(?:\.\d+)?s", re.IGNORECASE)

#: node --test summary keys. `^` anchored under MULTILINE so an echoed line that
#: merely CONTAINS `# pass 5` mid-text cannot supply a count.
#:
#: TAP ONLY, deliberately. node picks its reporter by TTY: `tap` writes
#: `# pass 2`, `spec` writes `\u2139 pass 2`. An earlier cut accepted BOTH, so that a
#: consumer whose node emits `spec` would not meet a dead end -- and a second
#: review round found that widening silently reintroduced the false kill the same
#: slice had just repaired, because the file-level/test-level distinction the
#: guard below needs EXISTS ONLY IN TAP.
#:
#: Measured, not reasoned: `node --test --test-reporter=spec` over a
#: module-breaking mutant emits NO `exitCode` line in any form, so the guard has
#: nothing to key on and a broken run reads as a kill again. A dead end that names
#: its own fix is strictly better than a false kill, so `spec` is DETECTED and
#: refused with that fix named, rather than half-read.
_NODE_SUMMARY_KEY_RE = re.compile(
    r"^# (tests|pass|fail|cancelled|skipped|todo|suites) (-?\d+)\s*$",
    re.MULTILINE,
)
_NODE_DURATION_RE = re.compile(r"^# duration_ms \d+(?:\.\d+)?\s*$", re.MULTILINE)
_NODE_TAP_START_RE = re.compile(r"^TAP version \d+\s*$", re.MULTILINE)
_NODE_RESULT_START_RE = re.compile(r"^(?:not )?ok (?P<number>\d+)(?: - .*)?\s*$", re.MULTILINE)
_NODE_PLAN_RE = re.compile(r"^1\.\.(\d+)\s*$", re.MULTILINE)
#: Enough to recognise node's `spec` output so the refusal can be specific.
_NODE_SPEC_RE = re.compile(r"^\u2139 (?:tests|pass|fail) \d+\s*$", re.MULTILINE)
#: A FILE-level failure: node reports a test file whose process exited non-zero.
#: `exitCode:` appears in a subtest's TAP YAML diagnostic only for a file the
#: runner spawned, never for a test that failed inside one -- measured both ways.
_NODE_PROCESS_FAILURE_RE = re.compile(r"^\s*exitCode: \d+\s*$", re.MULTILINE)


@dataclass(frozen=True)
class RunCounts:
    """What the runner REPORTED. Not a verdict; the harness owns that.

    `errors` means "the run did not reach a verdict here" -- pytest's `N error`,
    node's cancelled tests, and node's file-level process failures all land in it,
    because the harness treats it as evidence that no test caught anything.
    """

    passed: int
    failed: int
    errors: int
    #: The exact text the counts were read from, so a refusal can quote its
    #: evidence instead of asserting that it looked.
    evidence: str


@dataclass(frozen=True)
class _NodeRun:
    """One structurally validated TAP run and the summary it owns."""

    text: str
    summary: str
    counts: tuple[tuple[str, int], ...]


class PytestReporter:
    """The historical reader, moved verbatim rather than reimplemented."""

    name = "pytest"
    summary_shape = "a summary line carrying counts and a duration, e.g. `2 passed in 0.10s`"

    @staticmethod
    def summary(output: str) -> str | None:
        for line in reversed(output.splitlines()):
            stripped = line.strip()
            if not SUMMARY_RE.search(stripped):
                continue
            if (
                NO_TESTS_RE.search(stripped)
                or PASSED_RE.search(stripped)
                or FAILED_RE.search(stripped)
                or ERROR_RE.search(stripped)
            ):
                return stripped
        return None

    @classmethod
    def read(cls, output: str) -> RunCounts | None:
        line = cls.summary(output)
        if line is None:
            return None
        if NO_TESTS_RE.search(line):
            passed = 0
        else:
            match = PASSED_RE.search(line)
            passed = int(match.group(1)) if match else 0
        failed_match = FAILED_RE.search(line)
        error_match = ERROR_RE.search(line)
        return RunCounts(
            passed=passed,
            failed=int(failed_match.group(1)) if failed_match else 0,
            errors=int(error_match.group(1)) if error_match else 0,
            evidence=line,
        )


class NodeTestReporter:
    """`node --test`'s trailing TAP summary block.

    `cancelled` maps to `errors`, not to `failed`, and the distinction is the same
    one the harness already draws for pytest: a cancelled test did not run to a
    verdict, so it is a broken run rather than a caught mutation. Mapping it to
    `failed` would manufacture kills out of a runner that crashed -- the exact
    defect `mutate_and_restore` exists to end.

    `skipped` and `todo` are deliberately NOT read. They are neither evidence of a
    catch nor of a break, and folding them into the accounted total would let a
    mutant that turns tests into skips satisfy the baseline-scope check.
    """

    name = "node-test"
    summary_shape = (
        "a trailing TAP block of `# key value` lines ending in `# duration_ms`. "
        "node's `spec` reporter is NOT accepted -- it omits the file-level failure "
        "detail this reader needs to tell a broken module from a caught mutation -- "
        "so add `--test-reporter=tap` to the plan's test_command"
    )

    @staticmethod
    def looks_like_spec(output: str) -> bool:
        """Whether this is node output in the reporter this reader refuses."""
        return _NODE_SPEC_RE.search(output) is not None

    @classmethod
    def _summary_block(cls, selected_run: str) -> str | None:
        """Return the strict summary block immediately before its duration."""
        block: list[str] = []
        for line in reversed(selected_run.splitlines()):
            if _NODE_DURATION_RE.fullmatch(line):
                if block:
                    break
                block.append(line)
                continue
            if _NODE_SUMMARY_KEY_RE.fullmatch(line):
                block.append(line)
                continue
            break
        block.reverse()
        return "\n".join(block) if block else None

    @classmethod
    def _validated_run(cls, output: str, start: int, end: int) -> _NodeRun | None:
        """Validate one candidate's plan, result ownership, and counts."""
        selected_run = output[start:end]
        block = cls._summary_block(selected_run)
        if block is None:
            return None

        summary_matches = list(_NODE_SUMMARY_KEY_RE.finditer(block))
        keys = [match.group(1) for match in summary_matches]
        if len(keys) != len(set(keys)):
            return None
        counts = {match.group(1): int(match.group(2)) for match in summary_matches}
        required = {"tests", "pass", "fail", "cancelled"}
        if not required <= counts.keys():
            return None

        plans = list(_NODE_PLAN_RE.finditer(selected_run))
        if not plans or int(plans[-1].group(1)) != counts["tests"]:
            return None
        tests = counts["tests"]
        if any(value < 0 for value in counts.values()):
            return None
        optional = counts.get("skipped", 0) + counts.get("todo", 0)
        if counts["pass"] + counts["fail"] + counts["cancelled"] + optional != tests:
            return None

        results = list(_NODE_RESULT_START_RE.finditer(selected_run))
        result_numbers = [int(match.group("number")) for match in results]
        if result_numbers != list(range(1, tests + 1)):
            return None
        return _NodeRun(selected_run, block, tuple(counts.items()))

    @classmethod
    def _matches_before(
        cls,
        pattern: re.Pattern[str],
        output: str,
        region_start: int,
        end: int,
    ) -> list[re.Match[str]]:
        """Return matches starting inside one candidate region."""
        return [match for match in pattern.finditer(output, region_start) if match.start() < end]

    @classmethod
    def _candidate_for_region(cls, output: str, region_start: int, end: int) -> _NodeRun | None:
        """Find the first valid header run, then a compact result-owned run."""
        headers = cls._matches_before(_NODE_TAP_START_RE, output, region_start, end)
        for header in headers:
            candidate = cls._validated_run(output, header.start(), end)
            if candidate is not None:
                return candidate

        plans = cls._matches_before(_NODE_PLAN_RE, output, region_start, end)
        results = cls._matches_before(_NODE_RESULT_START_RE, output, region_start, end)
        for plan in reversed(plans):
            tests = int(plan.group(1))
            before = [match for match in results if match.start() < plan.start()]
            after = [match for match in results if match.start() > plan.end()]
            starts: list[int] = []
            if len(after) >= tests:
                starts.append(plan.start())
            if len(before) >= tests:
                starts.append(before[-tests].start() if tests else plan.start())
            for start in starts:
                candidate = cls._validated_run(output, start, end)
                if candidate is not None:
                    return candidate
        return None

    @classmethod
    def _selected_run(cls, output: str) -> _NodeRun | None:
        """Return the latest complete run after complete-duration boundaries."""
        durations = list(_NODE_DURATION_RE.finditer(output))
        if not durations:
            return None

        selected: _NodeRun | None = None
        prior_complete_end = 0
        for duration in durations:
            candidate = cls._candidate_for_region(output, prior_complete_end, duration.end())
            if candidate is None:
                continue
            selected = candidate
            prior_complete_end = duration.end()
        return selected

    @classmethod
    def summary(cls, output: str) -> str | None:
        """The summary block owned by the latest structurally complete run."""
        selected_run = cls._selected_run(output)
        return selected_run.summary if selected_run is not None else None

    @classmethod
    def read(cls, output: str) -> RunCounts | None:
        selected_run = cls._selected_run(output)
        if selected_run is None:
            return None
        counts = dict(selected_run.counts)
        reported_failures = counts["fail"]
        # THE false-kill guard, and the reason this reader looks outside the
        # summary block at all. `node --test` has no error concept: a test FILE
        # that fails to load is reported as a failing TEST, so a mutation that
        # breaks the module reports `# pass 0 / # fail 3` -- byte-identical to a
        # real kill on the same fixture. Measured both ways; the summaries do not
        # differ, so no count-only rule can separate them.
        #
        # What DOES separate them is where the failure sits. A caught mutation
        # fails at test level (`code: 'ERR_ASSERTION'`, no `exitCode`); a broken
        # module fails at FILE level, and node prints the file process's
        # `exitCode:` in that subtest's diagnostic. Counting those and moving them
        # out of `failed` makes the harness's existing scope check fire: accounted
        # drops below the baseline and the mutant is REFUSED, which is what
        # property 2 requires and what the pytest path already did via `N error`.
        #
        # Direction of error is why scanning outside the summary is acceptable
        # HERE where it is refused for counts: over-counting process failures
        # turns a kill into a refusal, and under-counting leaves the pre-existing
        # behavior. Neither can manufacture a kill. The selected run window keeps
        # an earlier run's diagnostics from crossing the summary boundary while
        # retaining the selected run's file-level failure details.
        process_failures = min(
            len(_NODE_PROCESS_FAILURE_RE.findall(selected_run.text)), reported_failures
        )
        return RunCounts(
            passed=counts["pass"],
            failed=reported_failures - process_failures,
            errors=counts["cancelled"] + process_failures,
            evidence=selected_run.summary,
        )


REPORTERS: dict[str, type] = {
    PytestReporter.name: PytestReporter,
    NodeTestReporter.name: NodeTestReporter,
}
#: Unchanged behavior for every existing plan, which names no reporter.
DEFAULT_REPORTER = PytestReporter.name


def resolve(name: object):
    """The reporter for a plan's `reporter` key, or None when it is unusable.

    An unknown name is REFUSED by the caller rather than silently falling back to
    pytest. A plan that asks for `node` and gets pytest's reader would report
    `baseline REFUSED` on a green Node tree and blame the tree -- a misconfigured
    proof surface answering with a verdict about the code instead of about itself.

    ONLY AN ABSENT KEY means "default". An earlier cut wrote
    `REPORTERS.get(name or DEFAULT_REPORTER)`, which short-circuits on every FALSY
    value: `{"reporter": ""}` -- exactly what a templated plan with an unset
    variable emits -- silently selected pytest and defeated this refusal on the one
    input most likely to produce it. A truthy unhashable value was worse:
    `{"reporter": ["node-test"]}` made `dict.get` raise and crashed the sweep.

    Same guard `run_mutant` already applies to `call_site`, for the same recorded
    reason: a templated plan can declare the opposite of what its author meant.
    """
    if name is None:
        return REPORTERS[DEFAULT_REPORTER]
    if not isinstance(name, str) or not name:
        return None
    return REPORTERS.get(name)


def unreadable_refusal(configured: str, output: str) -> str:
    """Why no counts were read, and -- when knowable -- what would read them.

    This is the half of #689 that is not the parser. The measured refusal said the
    summary was unreadable and stopped there, so an operator on a green Node tree
    was told their baseline could not be trusted and given nothing to act on. When
    another registered reporter CAN read the same bytes, that is not a guess to be
    acted on silently; it is a fact worth stating while still refusing.
    """
    others = [
        reporter.name
        for reporter in REPORTERS.values()
        if reporter.name != configured and reporter.read(output) is not None
    ]
    # `.get`, not `[...]`. The reporter parameter is duck-typed on purpose, so the
    # first out-of-tree reporter class would otherwise turn "no readable summary,
    # here is why" into a KeyError mid-sweep -- the refusal machinery failing at
    # exactly the moment it is needed.
    known = REPORTERS.get(configured)
    shape = known.summary_shape if known is not None else "an unregistered summary shape"
    detail = f"the `{configured}` reporter found no readable count report (it looks for {shape})"
    if NodeTestReporter.looks_like_spec(output):
        # The one unreadable case with a precise cause and a one-flag fix. Without
        # this the operator gets a generic "nothing could read it" over output that
        # is obviously node's, which is the dead end this whole seam exists to end.
        return (
            detail + "; this IS node output, in the `spec` reporter. That format omits the "
            "file-level failure detail needed to tell a broken module from a caught "
            "mutation, so it is refused rather than half-read -- add "
            "`--test-reporter=tap` to the plan's test_command"
        )
    if others:
        detail += (
            "; this output IS readable by the "
            + ", ".join(f"`{name}`" for name in others)
            + ' reporter, so set `"reporter"` in the plan'
        )
    else:
        detail += (
            "; no registered reporter could read it either (registered: "
            + ", ".join(f"`{name}`" for name in sorted(REPORTERS))
            + ")"
        )
    return detail
