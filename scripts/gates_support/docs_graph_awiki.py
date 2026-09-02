#!/usr/bin/env python3
"""awiki 0.5.0 as a PROCESS and an OUTPUT FORMAT, for `check_docs_graph.py`.

Everything here is the contract with the external binary: the argv the gate
declares, the timeout that turns a hang into NOT-RUN, the two exit codes that
mean a scan completed, the console lifecycle line, and the shape of the summary
and finding blocks the gate reads. None of it decides a verdict. The metrics,
the bars, the ratchet record and the pass/fail/not-run rendering stay in the
gate, so this module can be read against the installed awiki alone and the gate
against its declared bars alone.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_monitored_phase = _subprocess_guard.run_monitored_phase

# awiki exits 0 on a clean graph and 1 on lint findings. This gate does not read
# the code as its verdict -- findings are why it parses the summary instead --
# but a code OUTSIDE this set means awiki did not complete a scan, and a summary
# it may have printed on the way out describes a graph it did not finish reading.
OBSERVED_EXIT_CODES = frozenset({0, 1})
_SUMMARY_RE = re.compile(r"^//\s*(?P<verdict>\w+)\s+(?P<fields>.*)$")
_FIELD_RE = re.compile(r"(?P<key>[a-z_]+)=(?P<value>[0-9.]+)")
# awiki's own token for "every rule passed". It is the only thing that licenses
# reading an ABSENT orphan/island count as zero, and even then only alongside the
# ratios below.
PASSING_VERDICT = "ok"
# Present on both the passing and failing summary lines (captured at 0.5.0 in
# tests/fixtures/), so they can corroborate a passing verdict that omits the
# counts themselves.
_CLEAN_COROBORATION = {"orphan_rate": 0.0, "largest_component_ratio": 1.0}


def corroborates_clean(summary: dict[str, float]) -> bool:
    """Do the ratios awiki always prints agree that nothing is orphaned or split?

    Required before an absent count is read as zero. If awiki ever says `ok` while
    printing a non-zero orphan rate, that is a contradiction, and the gate reports
    NOT-RUN rather than picking whichever half it prefers.
    """
    return all(summary.get(key) == expected for key, expected in _CLEAN_COROBORATION.items())


# A hung `awiki` would hang the whole quality run with no verdict at all. The
# timeout turns that into a TimeoutExpired, which the guard in `evaluate` renders
# as NOT-RUN -- the honest answer for a scan that never finished.
AWIKI_TIMEOUT_SECONDS = 120


# awiki exits 1 whenever lint has FINDINGS. That is an observed outcome this gate
# judges by the named metrics above (a tree over none of its bars still exits 1
# on link-only lines), not a phase failure. The monitored-phase guard renders any
# non-zero exit as `FAIL [phase]`, so the console carried a red line for a gate
# whose verdict was pass, and `docs-graph` is label-only: no aggregate reads that
# line, only the operator does. The guard keeps echoing exit codes for every
# other phase; this caller rewrites only its own terminal line, and only for the
# findings code. Timeout (124) and any other code keep the guard's FAIL, which
# matches the NOT-RUN verdict `_evaluate` gives them.
AWIKI_FINDINGS_EXIT = 1
AWIKI_PHASE = "docs-graph-awiki"


class _AwikiLifecycle:
    """Forward the guard's lifecycle lines, holding back only the terminal one.

    RUN and HEARTBEAT reach the operator live, so a hung scan is still visible
    before the timeout fires. The `PASS|FAIL` line is held until the exit code
    is known, then rendered by `_run_awiki` from what the code means to THIS gate.
    """

    def __init__(self, target) -> None:
        self._target = target
        self._pending = ""
        self.terminal: str | None = None

    def write(self, text: str) -> int:
        self._pending += text
        while "\n" in self._pending:
            line, self._pending = self._pending.split("\n", 1)
            if line.startswith((f"PASS [{AWIKI_PHASE}]", f"FAIL [{AWIKI_PHASE}]")):
                self.terminal = line
            else:
                print(line, file=self._target, flush=True)
        return len(text)

    def flush(self) -> None:
        self._target.flush()


def run_awiki(repo_root: Path, scan_root: str) -> tuple[int, str]:
    # `sys.stderr` read here, not at import: the guard resolves its default the
    # same way, and a test that captures stderr must see this line.
    lifecycle = _AwikiLifecycle(sys.stderr)
    outcome = run_monitored_phase(
        ["awiki", "lint", "-root", scan_root, "-recursive"],
        cwd=repo_root,
        phase=AWIKI_PHASE,
        timeout_seconds=AWIKI_TIMEOUT_SECONDS,
        stream=lifecycle,
    )
    terminal = lifecycle.terminal
    if outcome.returncode == AWIKI_FINDINGS_EXIT:
        terminal = (
            f"OBSERVED [{AWIKI_PHASE}] {outcome.elapsed_seconds:.1f}s {outcome.display} "
            "(exit 1 is lint findings; the verdict is the gate's, from the named metrics)"
        )
    if terminal is not None:
        print(terminal, file=sys.stderr, flush=True)
    return outcome.returncode, f"{outcome.stdout}\n{outcome.stderr}"


def parse_summary(output: str) -> tuple[str, dict[str, float]] | None:
    """Read awiki's `// <verdict> documents=.. orphans=.. ...` summary line.

    Returns `(verdict, fields)`, or None when no summary line is present, which
    the caller treats as NOT-RUN. The format is not a declared stable interface
    upstream, so failing to parse it must never resolve to a pass.
    """
    for line in output.splitlines():
        match = _SUMMARY_RE.match(line.strip())
        if not match:
            continue
        fields: dict[str, float] = {}
        for field in _FIELD_RE.finditer(match.group("fields")):
            try:
                fields[field.group("key")] = float(field.group("value"))
            except ValueError:
                # `[0-9.]+` accepts strings float() rejects (`1.2.3`, `.`). A
                # value this gate cannot read is drift, and drift must reach the
                # NOT-RUN path -- an uncaught ValueError would exit 1, which the
                # runner renders as FAIL: the gate asserting a broken docs graph
                # on a run where it observed nothing.
                return None
        if fields:
            return match.group("verdict"), fields
    return None


# awiki annotates each finding block with guidance lines (`// why:`, `// fix:`,
# `// example:`). They are NOT section headers, and treating them as such ends the
# block immediately -- which made a failing run report the count while naming no
# page, the one thing an operator needs from it.
#
# The rule is STRUCTURAL rather than a list of the annotations seen so far: a
# header is a bare token or `token=value` (`// orphan`, `// link_only_line`,
# `// island=1`, all captured in tests/fixtures/), while an annotation carries a
# COLON before any `=`. Keyed on an allowlist, a new `// note:` upstream would
# silently reintroduce the bug this replaced; keyed on `[a-z_]+:` alone, so would
# a multi-word `// see also:` or a capitalised `// Note:`.
_ANNOTATION_RE = re.compile(r"^//[^=]*:")


def _block_header(line: str) -> str | None:
    """The block name for an awiki section header line, else None."""
    if not line.startswith("//") or _ANNOTATION_RE.match(line):
        return None
    return line[2:].strip().split("=", 1)[0].strip() or None


def named_pages(output: str, block: str) -> list[str]:
    """The pages awiki listed under `block`, so a failure says WHICH.

    Deduplicated in first-seen order, with ` x<n>` appended when a page carries
    more than one finding. A connectivity block names each page once, so this is
    a no-op there; `link_only_line` is PER LINE and named one page 41 times in a
    row on the tree that added it, which is a list an operator scrolls past
    rather than reads.
    """
    counts: dict[str, int] = {}
    in_block = False
    for line in output.splitlines():
        stripped = line.strip()
        header = _block_header(stripped)
        if header is not None:
            in_block = header == block
            continue
        if stripped.startswith("//"):
            continue
        if in_block and stripped.startswith("[["):
            name = stripped.split("]]", 1)[0].lstrip("[")
            counts[name] = counts.get(name, 0) + 1
    return [name if count == 1 else f"{name} x{count}" for name, count in counts.items()]
