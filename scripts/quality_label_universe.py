#!/usr/bin/env python3

"""The set of runtime labels `run-quality.sh` can EVER queue (#546).

A budgeted runtime label with no recorded sample is a `WARN` and the budget gate
exits 0, so a bar nothing exercises reads as protection forever. Three states
produce that, and they are not equally decidable:

- the label was RENAMED or typo'd, so nothing will ever record it again;
- it is queued only under a condition that does not hold on this run;
- it moved behind an opt-in and nobody opts in any more.

Only the first is decidable without operator intent, and it is decidable exactly
by asking whether the runner still knows the name at all. That is what this module
answers. The other two look identical from here -- a release-path budget on a box
that never runs `--release` and a gate abandoned behind an opt-in in 2025 both
report "the runner knows it, it did not run" -- and deciding between them needs an
adapter-declared expectation, not a bigger parser. This module deliberately does
not guess.

Why a static read of the runner rather than the recorded sample window: sample
history cannot distinguish a dead label from an unexercised run mode, because that
information is not in the signals file. A previous repair keyed on that history was
built, measured defective and reverted (it hard-failed a fresh machine's first run,
and permanently failed six legitimately conditional labels whose only escape was
`--no-verify`). Membership in the runner's own text has neither exposure: it reads
no history, so a fresh machine answers identically to one with a year of samples,
and a conditional label is in the file whether or not its condition held.

The parse is not trusted alone, because a silent extraction miss fails in the
harmful direction: the label drops out of the universe, and a budget naming it
then reads as orphaned -- a blocking pre-push red whose remedy tells the operator
to delete a correct bar. So `run-quality.sh` asserts at queue time that every label
it QUEUES is one this reader found (`assert_label_in_universe`), and refuses the
run naming the label otherwise. An extraction miss in source 1 therefore surfaces
as a loud failure at the gate that caused it, not as a wrong verdict about a
correct adapter. That run-local assertion is what lets a regex over bash be
load-bearing here; without it this module would be a guess with a confident tone.

The assertion covers source 1 ONLY, and saying otherwise would be the same
overclaim it was added to retire. The aggregate label is recorded by
`print_final_summary` and the standing probes by `measure_startup_probes.py`;
neither passes through `queue_timed`, so neither is checked at runtime. Their
backstop is a test (`test_this_repo_has_no_orphaned_budget` pins both the budget
count and the standing-probe source), which is weaker than a runtime refusal and
is named here rather than implied away.

Three sources, because the runner has three ways to name a label:

1. `queue_*` CALL SITES with a literal label. Dispatcher bodies are excluded: the
   wrappers forward `queue_timed "$label"`, which is not a name, and a reader that
   accepted it would admit the string `$label` to the universe.
2. the aggregate label, which is COMPUTED (`run-quality-${MODE}` plus a `-release`
   suffix), so it is enumerated as the cross-product rather than read. No single
   run can observe more than one of the four.
3. adapter `startup_probes` with `class: standing`, which are recorded by
   `measure_startup_probes.py` and never pass through the runner's queue at all.
   The class filter matters: `--class standing` is the only invocation, so a probe
   declared with another class is named in the adapter and never measured.
"""

from __future__ import annotations

import argparse
import re
import shlex
import sys
from pathlib import Path
from typing import Any, Callable, TypeVar

try:
    from scripts import adapter_lib
except ModuleNotFoundError:  # direct execution from the shipped scripts directory
    import adapter_lib

from runtime_bootstrap import repo_root_from_script
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)

RUN_QUALITY_PATH = Path("scripts/run-quality.sh")
ADAPTER_PATH = Path(".agents/quality-adapter.yaml")
QUALITY_GATES_PATH = Path(".agents/quality-gates.yaml")
QUALITY_GATES_SCHEMA = "charness/quality-gates/v1"
QUALITY_GATE_LANES = frozenset({"core", "standard", "release-only", "label-only", "opt-in"})

# Every wrapper that can reach `queue_timed`. Adding a fourth wrapper without
# adding it here does not fail silently: its labels drop out of the universe, and
# the runner's queue-time assertion (`assert_label_in_universe`) refuses the run
# naming the missing label rather than letting the shrunk set reach a verdict.
QUEUE_FUNCTIONS = ("queue_selected", "queue_timed", "queue_agent_browser_runtime_gate")
_QUEUE_CALL_RE = re.compile(r"^\s*(?P<fn>" + "|".join(QUEUE_FUNCTIONS) + r")\s+(?P<rest>\S+)")
_FUNCTION_OPEN_RE = re.compile(r"^(?P<name>[A-Za-z_][A-Za-z0-9_]*)\(\)\s*\{")
_FUNCTION_CLOSE_RE = re.compile(r"^\}")
_LITERAL_LABEL_RE = re.compile(r'^"(?P<label>[^"$]+)"$')
# A label is a queue-line literal, so the runner's own comment ("Gate labels are
# double-quoted literals in this file") is the contract. Refusing anything outside
# this shape is what keeps `$label` and other non-names out of the universe when a
# future dispatcher is added outside `QUEUE_FUNCTIONS`.
_LABEL_SHAPE_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")

T = TypeVar("T")

AGGREGATE_MODES = ("read-only", "full")
AGGREGATE_RELEASE_SUFFIXES = ("", "-release")


class UniverseError(RuntimeError):
    """A queue call site the reader cannot resolve to a name.

    Raised rather than skipped: a silently shrunk universe turns a correct budget
    into a blocking false red, and the operator's only escape from the pre-push
    gate is `--no-verify`. Failing here names the file and line instead.
    """


def _validate_quality_gate_row(row: object, where: str) -> dict[str, Any]:
    if not isinstance(row, dict):
        raise UniverseError(f"{QUALITY_GATES_PATH}: `{where}` must be a mapping")
    label = row.get("label")
    if not isinstance(label, str) or not _LABEL_SHAPE_RE.fullmatch(label):
        raise UniverseError(f"{QUALITY_GATES_PATH}: `{where}.label` must be a runtime label")
    command = row.get("command")
    if (
        not isinstance(command, list)
        or not command
        or any(not isinstance(token, str) for token in command)
    ):
        raise UniverseError(
            f"{QUALITY_GATES_PATH}: `{where}.command` must be a non-empty "
            "block-style list of strings"
        )
    if row.get("lane") not in QUALITY_GATE_LANES:
        raise UniverseError(
            f"{QUALITY_GATES_PATH}: `{where}.lane` must be one of {sorted(QUALITY_GATE_LANES)}"
        )
    return row


def _quality_gate_rows(data: object) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        raise UniverseError(f"{QUALITY_GATES_PATH} must contain a mapping")
    phases = data.get("phases")
    if not isinstance(phases, list):
        raise UniverseError(f"{QUALITY_GATES_PATH}: `phases` must be a list")
    rows: list[dict[str, Any]] = []
    for phase_index, phase in enumerate(phases):
        if not isinstance(phase, dict):
            raise UniverseError(f"{QUALITY_GATES_PATH}: `phases[{phase_index}]` must be a mapping")
        gates = phase.get("gates")
        if gates in (None, {}):
            gates = []
        if not isinstance(gates, list):
            raise UniverseError(
                f"{QUALITY_GATES_PATH}: `phases[{phase_index}].gates` must be a list"
            )
        for gate_index, gate in enumerate(gates):
            rows.append(
                _validate_quality_gate_row(gate, f"phases[{phase_index}].gates[{gate_index}]")
            )
    return rows


def _quality_gate_declaration(repo_root: Path) -> dict[str, Any] | None:
    """Read the declarative gate list, or return ``None`` when it is absent.

    The data file is a migration seam, so its presence must never degrade to the
    shell fallback when it is malformed or empty. Both cases would let readers
    disagree about the gates while reporting a plausible green result. The
    adapter-owned block YAML reader is used here so the source and exported
    readers accept exactly the same dialect.
    """
    path = repo_root / QUALITY_GATES_PATH
    if not path.is_file():
        return None
    try:
        data, uninterpreted = adapter_lib.load_yaml_file_report(path)
    except Exception as error:
        raise UniverseError(f"{QUALITY_GATES_PATH} could not be read: {error}") from error
    if uninterpreted:
        raise UniverseError(
            f"{QUALITY_GATES_PATH} has line(s) this reader dropped, so its gate list "
            "cannot be trusted:\n  "
            + "\n  ".join(adapter_lib.uninterpreted_warnings(uninterpreted))
        )
    if not isinstance(data, dict):
        raise UniverseError(f"{QUALITY_GATES_PATH} must contain a mapping")
    if data.get("schema") != QUALITY_GATES_SCHEMA:
        raise UniverseError(
            f"{QUALITY_GATES_PATH} has schema {data.get('schema')!r}; "
            f"expected {QUALITY_GATES_SCHEMA!r}"
        )
    rows = _quality_gate_rows(data)
    if not rows:
        raise UniverseError(
            f"{QUALITY_GATES_PATH} is present but declares zero gates; refusing to "
            "fall back to the shell or report an empty universe"
        )
    labels: set[str] = set()
    for index, row in enumerate(rows):
        label = row["label"]
        variant_of = row.get("variant_of")
        if label in labels and variant_of != label:
            raise UniverseError(
                f"{QUALITY_GATES_PATH}: duplicate label {label!r} at gate row {index} "
                "must name itself in `variant_of`"
            )
        labels.add(label)
    data["_gate_rows"] = rows
    return data


def quality_gate_rows(repo_root: Path) -> list[dict[str, Any]] | None:
    """Return declared rows, or ``None`` when the data file is absent."""
    declaration = _quality_gate_declaration(repo_root)
    if declaration is None:
        return None
    return list(declaration["_gate_rows"])


def _declared_gate_labels(rows: list[dict[str, Any]]) -> list[str]:
    labels: dict[str, None] = {}
    for row in rows:
        labels.setdefault(row["label"], None)
    return list(labels)


def _dispatcher_names() -> frozenset[str]:
    return frozenset(QUEUE_FUNCTIONS)


def _logical_lines(text: str) -> list[tuple[int, str]]:
    """Bash lines with backslash continuations joined, keyed by first line number.

    A long queue line wrapped across two source lines is ordinary bash, and a
    reader that scanned raw lines saw the label on a line whose head was the
    previous one -- so it either missed the gate silently or refused a correct file
    with a remedy ("spell the label literally") that did not apply to what was
    wrong. Joining first makes the wrap invisible to every rule below.
    """
    joined: list[tuple[int, str]] = []
    pending: str | None = None
    pending_lineno = 0
    for lineno, raw in enumerate(text.splitlines(), start=1):
        if pending is None:
            pending, pending_lineno = raw, lineno
        else:
            pending = f"{pending} {raw.strip()}"
        if pending.endswith("\\") and not pending.lstrip().startswith("#"):
            pending = pending[:-1].rstrip()
            continue
        joined.append((pending_lineno, pending))
        pending = None
    if pending is not None:
        joined.append((pending_lineno, pending))
    return joined


def queue_call_labels(text: str, repo_root: Path | None = None) -> list[str]:
    """Literal labels from `queue_*` call sites outside dispatcher bodies.

    First-seen order, de-duplicated. Raises `UniverseError` for a call site whose
    label is not a literal, unless it is inside a `queue_*` function definition --
    those forward a variable by construction and are the plumbing, not a gate.

    When ``repo_root`` is supplied, a present declarative gate list is authoritative
    and its row labels are returned. The optional argument keeps this function's
    shell-text API for consumer repos and for migration parity, while every in-tree
    reader can opt into the data source explicitly.
    """
    if repo_root is not None:
        rows = quality_gate_rows(repo_root)
        if rows is not None:
            return _declared_gate_labels(rows)
    return list(dict.fromkeys(label for label, _argv in queue_call_pairs(text)))


def queue_call_pairs(text: str) -> list[tuple[str, tuple[str, ...]]]:
    """Return literal ``(label, argv)`` pairs from legacy shell queue sites."""
    dispatchers = _dispatcher_names()
    seen: dict[tuple[str, tuple[str, ...]], None] = {}
    current_function: str | None = None
    for lineno, line in _logical_lines(text):
        opened = _FUNCTION_OPEN_RE.match(line)
        if opened is not None:
            current_function = opened.group("name")
            continue
        if current_function is not None and _FUNCTION_CLOSE_RE.match(line):
            current_function = None
            continue
        call = _QUEUE_CALL_RE.match(line)
        if call is None:
            continue
        if current_function in dispatchers:
            continue
        literal = _LITERAL_LABEL_RE.match(call.group("rest"))
        if literal is None:
            raise UniverseError(
                f"{RUN_QUALITY_PATH}:{lineno}: {call.group('fn')} call site has a "
                f"non-literal label {call.group('rest')!r}; the universe reader "
                "cannot resolve it. Spell the label literally, or add the enclosing "
                "function to QUEUE_FUNCTIONS if it is a dispatcher."
            )
        label = literal.group("label")
        if not _LABEL_SHAPE_RE.match(label):
            raise UniverseError(
                f"{RUN_QUALITY_PATH}:{lineno}: label {label!r} is not a runtime "
                "label shape (lowercase alphanumerics, dots, dashes, underscores)."
            )
        try:
            tokens = shlex.split(line, comments=True)
        except ValueError as error:
            raise UniverseError(
                f"{RUN_QUALITY_PATH}:{lineno}: queue call cannot be parsed as argv: {error}"
            ) from error
        if len(tokens) < 3 or tokens[0] not in QUEUE_FUNCTIONS or tokens[1] != label:
            raise UniverseError(
                f"{RUN_QUALITY_PATH}:{lineno}: queue call for {label!r} has no command argv"
            )
        seen.setdefault((label, tuple(tokens[2:])), None)
    return list(seen)


def aggregate_labels() -> list[str]:
    """The four `run-quality-<mode>[-release]` labels.

    Computed at `print_final_summary` time from the run's own mode, so a single run
    can only ever record one of them. Enumerating the cross-product is what keeps
    the other three from reading as renamed.
    """
    return [
        f"run-quality-{mode}{suffix}"
        for mode in AGGREGATE_MODES
        for suffix in AGGREGATE_RELEASE_SUFFIXES
    ]


def standing_probe_labels(adapter_text: str) -> list[str]:
    """`startup_probes` labels whose `class` is `standing`.

    The runner invokes `measure_startup_probes.py --class standing`, and
    `_selected_probes` filters on that field, so a probe with any other class is
    declared in the adapter and never measured. Admitting it here would pass a bar
    that can never be exercised -- the defect this module exists to find.

    Read through the repo's shared adapter reader rather than a hand-rolled
    indentation walk. The first cut here DID hand-roll one, and it was wrong in the
    direction that costs an operator a push: a list written flush against its key
    (`startup_probes:` then `- label:` at column 0, equally valid YAML) made the
    reader decide the block had ended, drop every probe, and orphan
    `charness-version` -- which is budgeted in all four blocks, so the result was a
    blocking red with a remedy naming the wrong repair. The sibling gate in this
    same slice already used the shared reader; two readers for one file is how the
    disagreement gets in.
    """
    try:
        data = adapter_lib.load_yaml(adapter_text)
    except Exception as error:  # adapter_lib raises bare ValueError on shapes it refuses
        # Named, not raw. The reader is consumed by `run-quality.sh` at startup, so an
        # unnamed exception here aborts the ENTIRE run with a traceback blaming the
        # queue lines -- for an edit to a block scalar three hundred lines away in the
        # adapter. Before this reader existed the same adapter defect surfaced as one
        # red gate with an accurate message, and a repair must not make a diagnostic
        # worse than the thing it replaced.
        raise UniverseError(
            f"{ADAPTER_PATH} could not be parsed, so the startup-probe labels it "
            f"declares cannot be resolved: {error}"
        ) from error
    if not isinstance(data, dict) or "startup_probes" not in data:
        return []
    probes = data.get("startup_probes")
    if not isinstance(probes, list):
        raise UniverseError(
            f"{ADAPTER_PATH}: `startup_probes` is declared but is not a list, so the "
            "labels it names cannot be resolved."
        )
    labels: list[str] = []
    for index, probe in enumerate(probes):
        # Declared-but-unreadable RAISES rather than shrugging. The queue-call source
        # already refuses what it cannot resolve; a probe source that silently returned
        # `[]` would drop `charness-version` -- budgeted in every block -- and turn the
        # budget gate red for a correct adapter, with a remedy naming the wrong repair.
        # A probe that is simply not `standing` is not this case: it is readable, and
        # the answer to "is it measured" is no.
        if (
            not isinstance(probe, dict)
            or not isinstance(probe.get("label"), str)
            or not probe["label"]
        ):
            raise UniverseError(
                f"{ADAPTER_PATH}: `startup_probes[{index}]` carries no readable "
                "`label`, so the reader cannot tell whether it names a measured bar."
            )
        if probe.get("class") == "standing":
            labels.append(probe["label"])
    return labels


def label_universe(repo_root: Path) -> dict[str, object]:
    """The union of the three sources, with each source reported separately.

    A present gate declaration resolves the queue even when the legacy runner is
    absent. Otherwise `resolved` is false when the runner is absent -- a consumer
    repo that installs the quality skill without vendoring `run-quality.sh`.
    Callers must treat that as "no universe to check against", never as an empty
    universe: refusing every budget in a repo whose runner this module cannot see
    would be a blocking false red whose remedy tells the operator to delete
    correct bars.
    """
    rows = quality_gate_rows(repo_root)
    if rows is not None:
        queue_labels = _declared_gate_labels(rows)
        source = "data"
    else:
        runner = repo_root / RUN_QUALITY_PATH
        if not runner.is_file():
            return {
                "resolved": False,
                "reason": f"{RUN_QUALITY_PATH} is absent; this repo does not vendor the run-quality surface",
                "labels": [],
                "source": "shell",
                "sources": {},
            }
        queue_labels = queue_call_labels(runner.read_text(encoding="utf-8"))
        source = "shell"
    adapter = repo_root / ADAPTER_PATH
    probes = standing_probe_labels(adapter.read_text(encoding="utf-8")) if adapter.is_file() else []
    aggregates = aggregate_labels()
    merged: dict[str, None] = {}
    for label in [*queue_labels, *aggregates, *probes]:
        merged.setdefault(label, None)
    return {
        "resolved": True,
        "reason": None,
        "labels": list(merged),
        "source": source,
        "sources": {
            "queue_call_sites": queue_labels,
            "aggregate": aggregates,
            "standing_startup_probes": probes,
        },
    }


def parity(repo_root: Path) -> dict[str, object]:
    """Validate the migration seam without making the retired queue authoritative.

    Consumer repositories may still have a shell queue, so compare it there. This
    repository's wrapper intentionally has no queue call sites; its declared rows
    are the source of truth and the empty legacy surface is therefore a successful
    migration state rather than a false mismatch.
    """
    rows = quality_gate_rows(repo_root)
    if rows is None:
        raise UniverseError(f"{QUALITY_GATES_PATH} is absent; migration parity cannot be measured")
    runner = repo_root / RUN_QUALITY_PATH
    data_labels = set(_declared_gate_labels(rows))
    data_pairs = {(row["label"], tuple(row["command"])) for row in rows}
    shell_text = runner.read_text(encoding="utf-8") if runner.is_file() else ""
    legacy_shell_pairs = set(queue_call_pairs(shell_text)) if "queue_" in shell_text else set()
    shell_pairs = legacy_shell_pairs or data_pairs
    shell_labels = {label for label, _argv in shell_pairs}
    return {
        "data_labels": data_labels,
        "shell_labels": shell_labels,
        "symmetric_difference": data_labels ^ shell_labels,
        "data_pairs": data_pairs,
        "shell_pairs": shell_pairs,
        "pair_symmetric_difference": data_pairs ^ shell_pairs,
    }


def _parity_payload(comparison: dict[str, object]) -> dict[str, object]:
    return {
        key: sorted(
            [list(pair[:1]) + [list(pair[1])] for pair in value]
            if key.endswith("pairs") or key == "pair_symmetric_difference"
            else value
        )
        for key, value in comparison.items()
    }


def read_or_refuse(gate_name: str, compute: Callable[[], T]) -> tuple[int, T | None]:
    """Run `compute`, turning a `UniverseError` into a named refusal on stderr.

    Every consumer of this reader owes exactly this handling, and duplicating it is
    how one of them forgets. One did: `check_timing_layer_completeness` is queued at
    COMMIT time and had no handler, so an unresolvable queue line surfaced as a
    Python traceback inside the pre-commit hook, from a gate whose subject is the
    timing table. A helper rather than three copies, so the next consumer inherits
    the refusal instead of re-deriving it -- and so the failure mode cannot be
    reintroduced one call site at a time.

    Returns `(exit_code, value)`; `value` is None exactly when the code is nonzero.
    """
    try:
        return 0, compute()
    except UniverseError as error:
        print(f"{gate_name}: {error}", file=sys.stderr)
        return 1, None


def main() -> int:
    parser = argparse.ArgumentParser(description="Print the run-quality label universe.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--labels-only", action="store_true", help="print labels one per line")
    parser.add_argument(
        "--parity",
        action="store_true",
        help="compare declared row labels with labels still queued by the shell",
    )
    args = parser.parse_args()
    if args.parity:
        code, comparison = read_or_refuse(
            "quality label parity", lambda: parity(args.repo_root.resolve())
        )
        if comparison is None:
            return code
        emit_yaml(_parity_payload(comparison))
        return (
            1
            if (comparison["symmetric_difference"] or comparison["pair_symmetric_difference"])
            else 0
        )
    code, universe = read_or_refuse(
        "quality label universe", lambda: label_universe(args.repo_root.resolve())
    )
    if universe is None:
        return code
    # Without --labels-only, stdout remains ONE YAML document. The old bare-label
    # lines were a machine contract with a shell consumer, and the `resolved: false` case answered
    # on stderr with an EMPTY stdout so that consumer's "empty means do not assert"
    # degrade would fire. Both facts now live in the payload -- `resolved` and
    # `reason` say exactly what the stderr sentence said, and `labels` is the list --
    # so a consumer reads the document instead of counting lines. A line-counting
    # consumer must be updated with this change; it cannot be left to guess.
    if args.labels_only:
        if not universe["resolved"]:
            # Keep unresolved distinct from a resolved empty set. The labels-only
            # transport has no status field, so retain the existing diagnostic on
            # stderr while preserving the non-fatal exit used by consumer repos.
            print(
                f"quality label universe: not derivable -- {universe['reason']}",
                file=sys.stderr,
            )
            return 0
        for label in universe["labels"]:
            print(label)
        return 0

    emit_yaml(universe)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
