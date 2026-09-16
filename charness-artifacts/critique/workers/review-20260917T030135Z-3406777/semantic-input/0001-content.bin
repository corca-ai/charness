"""One declarative expected failing test per mutant (#820).

A downstream guard must prove not merely "the suite went red" but "the
intended named test reported failure" -- an unrelated failure must not kill
the mutant. A plan entry opts in with `"expected_failing_test": "<name>"`,
and the verdict narrows to:

- expected test among the reported failures: the kill stands;
- command failed without it: REFUSED (unestablished proof, not a kill);
- command passed: SURVIVED (the expectation only narrows the kill).

Both halves live here: what the PLAN asserted (`parse_expected_failing_test`,
mirroring how `mutation_plan_semantics` owns the find/replace validation and
how `call_site` owns its boolean strictness), and what the RUN reported
(`named_failure_refusal`, read from the reporter's owned failing-test names --
never from a scan of the whole transcript). A reporter that cannot list names
-- pytest is counts-only by design, and any pre-#820 out-of-tree reporter
lacks the method -- refuses rather than guessing.
"""

from __future__ import annotations


class ExpectedFailureError(Exception):
    """The plan's `expected_failing_test` cannot name one attributable test."""


def parse_expected_failing_test(spec: dict) -> str | None:
    """Return the required test name, or None when the plan requires none.

    Absent or null means "any reported failure kills" (unchanged behavior); a
    present value must be one non-empty name. Stripped, because TAP names are
    compared stripped -- and like `call_site`, a mis-typed value raises rather
    than coercing or guessing.
    """
    raw = spec.get("expected_failing_test")
    if raw is None:
        return None
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    raise ExpectedFailureError(
        "`expected_failing_test` must be a non-empty test name string, got "
        f"{raw!r}; an unmatchable expectation could never kill"
    )


def named_failure_refusal(reporter, output: str, expected: str) -> str | None:  # noqa: ANN001
    """None when the expected test failed (the kill stands), else the refusal.

    Matching is exact and case-sensitive against the selected run's owned
    `not ok` names. An unrelated failure is unestablished proof: refused, never
    a kill and never a survivor.
    """
    reader = getattr(reporter, "failed_tests", None)
    name = getattr(reporter, "name", "?")
    if reader is None:
        return (
            f"the mutant requires failing test {expected!r}, but the `{name}` "
            "reporter cannot list failing test names; a kill without the named "
            "evidence would be the defect this runner exists to stop"
        )
    failed_names = reader(output)
    if failed_names is None:
        return (
            f"the mutant requires failing test {expected!r}, but the `{name}` "
            "reporter could not list this run's failing tests; there is no "
            "evidence to call this either way"
        )
    if expected in failed_names:
        return None
    seen = ", ".join(repr(item) for item in failed_names) or "no named failures"
    return (
        f"the command failed without the expected test {expected!r}; "
        f"failing tests were: {seen}"
    )
