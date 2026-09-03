#!/usr/bin/env python3
"""Selection and condition evaluation for the declarative quality runner."""

from __future__ import annotations

import os
from collections.abc import Callable, Mapping
from pathlib import Path

from run_quality_engine_model import Gate, GateList, RunnerError


def explicit_labels(raw: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in raw.split(",") if item.strip())


def _condition_matches(
    gate: Gate,
    *,
    repo_root: Path,
    mode: str,
    environment: Mapping[str, str],
    predicates: Mapping[str, Callable[[], bool]],
    release: bool,
    non_claim: str,
) -> bool:
    if not gate.condition:
        return True

    def evaluate(condition: dict[str, object]) -> bool:
        results: list[bool] = []
        for verb, value in condition.items():
            if verb == "any_of":
                results.append(any(evaluate(branch) for branch in value))
            elif verb == "all_of":
                results.append(all(evaluate(branch) for branch in value))
            elif verb == "env":
                results.append(
                    all(
                        (expected == "nonempty" and bool(environment.get(str(name), "")))
                        or environment.get(str(name), "") == str(expected)
                        for name, expected in value.items()
                    )
                )
            elif verb == "file_exists":
                results.append((repo_root / str(value)).is_file())
            elif verb == "mode_in":
                results.append(mode in value)
            elif verb == "release":
                results.append(release is bool(value))
            elif verb == "prior_phases_green":
                # This is resolved at phase execution time. A true condition is
                # provisionally selectable so the engine can preserve the row and
                # skip it after an earlier phase fails.
                results.append(True if value else True)
            elif verb == "non_claim_absent":
                results.append(non_claim != str(value))
            elif verb == "predicate":
                predicate = predicates.get(str(value))
                if predicate is None:
                    raise RunnerError(f"gate {gate.label!r} names unknown predicate {value!r}")
                results.append(predicate())
            else:  # validated by the model, retained for direct callers
                raise RunnerError(f"gate {gate.label!r} names unknown condition {verb!r}")
        return all(results)

    return evaluate(gate.condition)


def _lane_matches(
    gate: Gate,
    *,
    full_queue: bool,
    release: bool,
    include_release_only: bool,
    explicit: frozenset[str],
) -> bool:
    if explicit:
        # An opt-in is enabled by its environment switch even during a filtered
        # run; naming an opt-in is the explicit alternative to that switch.
        return gate.label in explicit or gate.lane == "opt-in"
    if gate.lane == "core":
        return full_queue or not explicit
    if gate.lane == "standard":
        return full_queue
    if gate.lane == "release-only":
        return release or (full_queue and include_release_only)
    if gate.lane == "label-only":
        return False
    return gate.lane == "opt-in"


def select_gates(
    gate_list: GateList,
    *,
    repo_root: Path,
    mode: str,
    full_queue: bool,
    release: bool,
    include_release_only: bool,
    labels: str,
    non_claim: str = "",
    environment: Mapping[str, str] | None = None,
    predicates: Mapping[str, Callable[[], bool]] | None = None,
    excluded_labels: frozenset[str] = frozenset(),
) -> dict[str, tuple[Gate, ...]]:
    environment = os.environ if environment is None else environment
    predicates = {} if predicates is None else predicates
    explicit = frozenset(explicit_labels(labels))
    selected: dict[str, list[Gate]] = {phase.identifier: [] for phase in gate_list.phases}
    claimed_variants: set[str] = set()
    for phase in gate_list.phases:
        for gate in phase.gates:
            if gate.label in excluded_labels:
                continue
            if not _lane_matches(
                gate,
                full_queue=full_queue,
                release=release,
                include_release_only=include_release_only,
                explicit=explicit,
            ):
                continue
            if not (
                explicit
                and gate.label in explicit
                and gate.lane == "opt-in"
            ) and not _condition_matches(
                gate,
                repo_root=repo_root,
                mode=mode,
                environment=environment,
                predicates=predicates,
                release=release,
                non_claim=non_claim,
            ):
                continue
            variant_key = gate.variant_of or gate.label
            if variant_key in claimed_variants:
                continue
            claimed_variants.add(variant_key)
            selected[phase.identifier].append(gate)
    return {identifier: tuple(gates) for identifier, gates in selected.items()}


def selected_count(selected: Mapping[str, tuple[Gate, ...]]) -> int:
    return sum(len(gates) for gates in selected.values())


def requires_prior_phases_green(gate: Gate) -> bool:
    """Whether a selected row is gated on earlier phase success."""
    def find(condition: dict[str, object]) -> bool:
        for verb, value in condition.items():
            if verb == "prior_phases_green" and value is True:
                return True
            if verb in {"any_of", "all_of"} and any(find(branch) for branch in value):
                return True
        return False

    return find(gate.condition)


NOT_RUN_NON_CLAIM = "non-claim"
NOT_RUN_READ_ONLY = "read-only"
NOT_RUN_OPT_IN = "opt-in unmet"
NOT_RUN_CONDITION = "condition unmet"


def _not_run_reason(
    gate: Gate,
    *,
    excluded_labels: frozenset[str],
    mode: str,
    matches: Callable[[Gate, str], bool],
) -> str | None:
    if gate.label in excluded_labels:
        return NOT_RUN_NON_CLAIM
    if matches(gate, mode):
        return None
    if mode == "read-only" and matches(gate, "full"):
        return NOT_RUN_READ_ONLY
    return NOT_RUN_OPT_IN if gate.lane == "opt-in" else NOT_RUN_CONDITION


def not_run_gates(
    gate_list: GateList,
    selected: Mapping[str, tuple[Gate, ...]],
    *,
    repo_root: Path,
    mode: str,
    full_queue: bool,
    release: bool,
    include_release_only: bool,
    labels: str,
    non_claim: str = "",
    environment: Mapping[str, str] | None = None,
    predicates: Mapping[str, Callable[[], bool]] | None = None,
    excluded_labels: frozenset[str] = frozenset(),
) -> tuple[tuple[str, str], ...]:
    """Rows the requested scope asked for that this run did not execute.

    Scope is what was asked for, not the whole gate list: an explicit ``--labels``
    run requests exactly those labels, and an unfiltered run requests the rows its
    lane matches.  A row whose variant sibling ran is not unrun, because the
    variant family's claim was established by that sibling.
    """
    environment = os.environ if environment is None else environment
    predicates = {} if predicates is None else predicates
    explicit = frozenset(explicit_labels(labels))
    ran = {gate.label for gates in selected.values() for gate in gates}
    claimed = {gate.variant_of or gate.label for gates in selected.values() for gate in gates}

    def matches(gate: Gate, candidate_mode: str) -> bool:
        return _condition_matches(
            gate,
            repo_root=repo_root,
            mode=candidate_mode,
            environment=environment,
            predicates=predicates,
            release=release,
            non_claim=non_claim,
        )

    rows: list[tuple[str, str]] = []
    seen: set[str] = set()
    for phase in gate_list.phases:
        for gate in phase.gates:
            if gate.label in ran or gate.label in seen:
                continue
            in_scope = (
                gate.label in explicit
                if explicit
                else _lane_matches(
                    gate,
                    full_queue=full_queue,
                    release=release,
                    include_release_only=include_release_only,
                    explicit=explicit,
                )
            )
            if not in_scope or (gate.variant_of or gate.label) in claimed:
                continue
            reason = _not_run_reason(
                gate, excluded_labels=excluded_labels, mode=mode, matches=matches
            )
            if reason is None:
                continue
            seen.add(gate.label)
            rows.append((gate.label, reason))
    return tuple(rows)
