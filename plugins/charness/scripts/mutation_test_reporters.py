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

#: node --test TAP summary keys. `^` anchored under MULTILINE so an echoed line
#: that merely CONTAINS `# pass 5` mid-text cannot supply a count.
_NODE_KEY_RE = re.compile(r"^# (tests|pass|fail|cancelled) (\d+)\s*$", re.MULTILINE)
_NODE_DURATION_RE = re.compile(r"^# duration_ms \d+(?:\.\d+)?\s*$", re.MULTILINE)


@dataclass(frozen=True)
class RunCounts:
    """What the runner REPORTED. Not a verdict; the harness owns that."""

    passed: int
    failed: int
    errors: int
    #: The exact text the counts were read from, so a refusal can quote its
    #: evidence instead of asserting that it looked.
    evidence: str


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
    summary_shape = "a trailing TAP block of `# key value` lines ending in `# duration_ms`"

    @staticmethod
    def summary(output: str) -> str | None:
        """The block from the last `# duration_ms` back through its count keys.

        Anchored on the LAST duration line so a fixture that runs the runner twice
        reports the final run, matching pytest's `reversed()` scan.
        """
        durations = list(_NODE_DURATION_RE.finditer(output))
        if not durations:
            return None
        end = durations[-1].end()
        # Walk back over the contiguous `# ...` lines that precede the duration.
        lines = output[:end].splitlines()
        block: list[str] = []
        for line in reversed(lines):
            if line.startswith("#"):
                block.append(line)
                continue
            break
        if not block:
            return None
        return "\n".join(reversed(block))

    @classmethod
    def read(cls, output: str) -> RunCounts | None:
        block = cls.summary(output)
        if block is None:
            return None
        counts = {key: int(value) for key, value in _NODE_KEY_RE.findall(block)}
        # `# tests` is what makes this block a REPORT rather than a stray comment
        # run. Without it there is no total, and a block carrying only a duration
        # says nothing about how many tests there were.
        if "tests" not in counts:
            return None
        return RunCounts(
            passed=counts.get("pass", 0),
            failed=counts.get("fail", 0),
            errors=counts.get("cancelled", 0),
            evidence=block,
        )


REPORTERS: dict[str, type] = {
    PytestReporter.name: PytestReporter,
    NodeTestReporter.name: NodeTestReporter,
}
#: Unchanged behavior for every existing plan, which names no reporter.
DEFAULT_REPORTER = PytestReporter.name


def resolve(name: str | None):
    """The reporter for a plan's `reporter` key, or None when the name is unknown.

    An unknown name is REFUSED by the caller rather than silently falling back to
    pytest. A plan that asks for `node` and gets pytest's reader would report
    `baseline REFUSED` on a green Node tree and blame the tree -- a misconfigured
    proof surface answering with a verdict about the code instead of about itself.
    """
    return REPORTERS.get(name or DEFAULT_REPORTER)


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
    detail = (
        f"the `{configured}` reporter found no readable count report "
        f"(it looks for {REPORTERS[configured].summary_shape})"
    )
    if others:
        detail += (
            "; this output IS readable by the "
            + ", ".join(f"`{name}`" for name in others)
            + " reporter, so set `\"reporter\"` in the plan"
        )
    else:
        detail += (
            "; no registered reporter could read it either (registered: "
            + ", ".join(f"`{name}`" for name in sorted(REPORTERS))
            + ")"
        )
    return detail
