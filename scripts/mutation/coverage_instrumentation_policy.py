"""What may be instrumented under coverage, and how each channel renders it.

THE one owner of that decision (SC18). Two builders wrap "run pytest under
coverage" -- `mutation_sampling_lib.coverage_run_command` (argv, used by the
changed-line mutation gate) and
`mutation_coverage_producer.instrument_broad_command` (shell string, used by
the release producer) -- and until 2026-08-15 they held OPPOSITE policies on the standing
pytest runner. The gate used the refusing one, so the repo's longest proof
spawned serial bare pytest while its fast path was already measured, budgeted,
and blocking.

Split out of `mutation_sampling_lib` when that file crossed its length cap. The
seam is the subject, not the line count: sampling is about WHICH files to mutate
and which lines coverage reached; this module is about whether a command can be
instrumented at all. `mutation_sampling_lib` re-exports these names, so callers
and tests keep binding them at the old address.
"""

from __future__ import annotations

import re
import shlex
import sys
from pathlib import Path

#: Any flag with this prefix makes the standing runner PRINT something and exit
#: instead of running the suite. Matched by PREFIX, not by an enumerated set:
#: argparse accepts unambiguous abbreviations, so `--print-last` reaches the same
#: early exit as `--print-last-run`, and an enumerated set is silently bypassed by
#: the abbreviation and by the next print flag someone adds. Instrumenting one
#: yields an EMPTY coverage set that reads exactly like a suite covering nothing.
STANDING_RUNNER_HELPER_FLAG_PREFIX = "--print"

PYTEST_KIND = "pytest"
STANDING_RUNNER_KIND = "standing-runner"

INSTRUMENTABLE_COMMAND_REFUSAL = (
    "mutation coverage instrumentation supports pytest commands shaped as "
    "`python3 -m pytest ...`, `pytest ...`, or an invocation of the standing pytest "
    "runner (`run_standing_pytest.py`, optionally prefixed by an interpreter). The "
    "command must START with one of those -- a wrapper such as `env VAR=x ...` cannot "
    "be instrumented, because `coverage run` would try to execute the wrapper as the "
    "script. A `--print*` flag is refused too: the runner prints and exits, which "
    "produces empty coverage that reads like a suite covering nothing."
)

# Anchored at the start on purpose: a command with anything BEFORE the interpreter
# (`env VAR=x python3 ...`, `nice`, `timeout 300`) renders into
# `coverage run env ...`, which makes coverage try to exec the wrapper as a Python
# script. Both builders refuse it rather than emitting an unrunnable command.
_PYTEST_PREFIX_RE = re.compile(r"^\s*(?:(?P<interp>\S*python[0-9.]*)\s+-m\s+)?pytest(?=\s|$)")
_STANDING_RUNNER_PREFIX_RE = re.compile(
    r"^\s*(?:(?P<interp>\S*python[0-9.]*)\s+)?(?P<script>\S*run_standing_pytest\.py)(?=\s|$)"
)


def _tokens(command: str) -> list[str]:
    try:
        return shlex.split(command)
    except ValueError:
        # An unterminated quote is still enough to see a `--print*` flag, and
        # acceptance must not depend on quoting the caller got wrong. The
        # RENDERING builders re-split and refuse it there with a message.
        return command.split()


def classify_instrumentable_command(command: str) -> tuple[str, str | None, str] | None:
    """THE one policy on what may be instrumented under coverage (SC18).

    Returns ``(kind, interpreter, remainder)`` where ``kind`` is
    :data:`PYTEST_KIND` or :data:`STANDING_RUNNER_KIND`, ``interpreter`` is the
    caller's leading interpreter token if the command named one (``None``
    otherwise), and ``remainder`` is the RAW tail of the command (unsplit, so a
    `tests/test_*.py` glob survives for the shell-string builder). ``None`` when
    the command is not instrumentable.

    The interpreter is RETURNED rather than re-derived, because a round-2
    reviewer measured the alternative: the argv builder re-applied the regex to
    recover it while the string builder hardcoded `python3`, so
    `/usr/bin/python3 -m pytest ...` was accepted by both and then measured under
    two different interpreters — a second decision procedure inside the repair
    that removed the first one.

    Both in-repo coverage builders decide here rather than each carrying its own
    answer: this module's :func:`coverage_run_command` (argv, used by the
    changed-line gate) and `mutation_coverage_producer.instrument_broad_command`
    (shell string, used by the release producer). They held OPPOSITE policies on the standing
    runner until 2026-08-15 — the gate used the refusing one, so the repo's
    longest proof spawned serial bare pytest while its fast path was already
    measured and enforced.

    The two builders still RENDER differently on purpose (argv here; a string
    there, whose glob must stay unquoted for bash). What is shared is this
    classification. A first repair shared only a boolean while each builder kept
    its own inline shape test, and the two answered differently for `pytest`,
    `python3 -m pytest` with no arguments, and `python -m pytest ...` — a round-1
    reviewer measured it, which is why the split point is the classifier and not
    a predicate.
    """
    match = _PYTEST_PREFIX_RE.match(command)
    if match is not None:
        return PYTEST_KIND, match.group("interp"), command[match.end() :]
    match = _STANDING_RUNNER_PREFIX_RE.match(command)
    if match is None:
        return None
    if any(token.startswith(STANDING_RUNNER_HELPER_FLAG_PREFIX) for token in _tokens(command)):
        return None
    return STANDING_RUNNER_KIND, match.group("interp"), command[match.start("script") :]


def is_standing_pytest_runner_command(command: str) -> bool:
    """See :func:`classify_instrumentable_command`."""
    classified = classify_instrumentable_command(command)
    return classified is not None and classified[0] == STANDING_RUNNER_KIND


def is_instrumentable_pytest_command(command: str) -> bool:
    """See :func:`classify_instrumentable_command`."""
    return classify_instrumentable_command(command) is not None


def coverage_run_command(test_command: str, data_file: Path) -> list[str]:
    """Argv form of the instrumented command, for callers that exec without a shell.

    NOTE, because it is a real difference the shared classifier does NOT remove:
    this builder splits the remainder into argv, so a shell glob (`tests/test_*.py`)
    reaches pytest as a literal path. The producer's string form is run through a
    shell and expands it. Same acceptance, different channel; a globbed command
    belongs to the string builder.
    """
    classified = classify_instrumentable_command(test_command)
    if classified is None:
        raise SystemExit(INSTRUMENTABLE_COMMAND_REFUSAL)
    kind, interpreter, remainder = classified
    try:
        rest = shlex.split(remainder)
    except ValueError as exc:
        raise SystemExit(f"cannot split {test_command!r} into arguments: {exc}") from exc
    prefix = [interpreter or sys.executable, "-m", "coverage", "run", "--data-file", str(data_file)]
    if kind == PYTEST_KIND:
        return [*prefix, "-m", "pytest", *rest]
    # `coverage run <script>` rather than `-m`: the runner is a script, not a
    # module. Its pytest child is measured through COVERAGE_PROCESS_START /
    # sitecustomize (see `coverage_subprocess_env`), which is the same mechanism
    # that already measures xdist workers, so the parallel path does not become a
    # coverage blind spot.
    return [*prefix, *rest]
