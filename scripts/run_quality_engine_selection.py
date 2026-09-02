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
) -> bool:
    if not gate.condition:
        return True
    verb, value = next(iter(gate.condition.items()))
    if verb == "env":
        return all(
            environment.get(str(name), "") == str(expected) for name, expected in value.items()
        )
    if verb == "file_exists":
        return (repo_root / str(value)).is_file()
    if verb == "mode_in":
        return mode in value
    predicate = predicates.get(str(value))
    if predicate is None:
        raise RunnerError(f"gate {gate.label!r} names unknown predicate {value!r}")
    return predicate()


def _lane_matches(
    gate: Gate,
    *,
    full_queue: bool,
    release: bool,
    include_release_only: bool,
    explicit: frozenset[str],
) -> bool:
    if explicit:
        return gate.label in explicit
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
            if not _condition_matches(
                gate,
                repo_root=repo_root,
                mode=mode,
                environment=environment,
                predicates=predicates,
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
