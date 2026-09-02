#!/usr/bin/env python3
"""Validated in-memory model for the declarative quality gate list."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module

_adapter_lib = import_repo_module(__file__, "scripts.adapter_lib")
load_yaml_file = _adapter_lib.load_yaml_file

LANES = frozenset({"core", "standard", "release-only", "label-only", "opt-in"})
SCHEMA = "charness/quality-gates/v1"
LABEL_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


class RunnerError(ValueError):
    """A gate-list or runner contract refusal."""


@dataclass(frozen=True)
class Gate:
    label: str
    command: tuple[str, ...]
    lane: str
    condition: dict[str, Any]
    variant_of: str | None
    unestablished_capable: bool
    native_preflight: bool
    timing_layer: str | None
    docs_only: bool
    note: str | None
    timeout_seconds: float | None = None


@dataclass(frozen=True)
class Phase:
    identifier: str
    isolation: str
    fail_fast: bool
    fail_message: str | None
    gates: tuple[Gate, ...]


@dataclass(frozen=True)
class GateList:
    phases: tuple[Phase, ...]
    runner_variables: frozenset[str]

    @property
    def gates(self) -> tuple[Gate, ...]:
        return tuple(gate for phase in self.phases for gate in phase.gates)


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RunnerError(f"{label} must be a mapping")
    return value


def _string(value: Any, label: str, *, required: bool = True) -> str | None:
    if value is None and not required:
        return None
    if not isinstance(value, str) or (required and not value):
        raise RunnerError(f"{label} must be a non-empty string")
    return value


def _bool(value: Any, label: str) -> bool:
    if value is None:
        return False
    if not isinstance(value, bool):
        raise RunnerError(f"{label} must be true or false")
    return value


def _command(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or any(not isinstance(item, str) for item in value):
        raise RunnerError(f"{label} must be a non-empty argv list of strings")
    return tuple(value)


def _condition(value: Any, label: str) -> dict[str, Any]:
    if value is None:
        return {}
    condition = _mapping(value, label)
    if len(condition) != 1:
        raise RunnerError(f"{label} must contain exactly one condition verb")
    verb = next(iter(condition))
    if verb not in {"env", "file_exists", "mode_in", "predicate"}:
        raise RunnerError(f"{label} uses unsupported condition {verb!r}")
    if verb == "env" and not isinstance(condition[verb], dict):
        raise RunnerError(f"{label}.env must be a mapping")
    if verb == "mode_in" and (
        not isinstance(condition[verb], list)
        or any(not isinstance(item, str) for item in condition[verb])
    ):
        raise RunnerError(f"{label}.mode_in must be a list of strings")
    if verb in {"file_exists", "predicate"} and not isinstance(condition[verb], str):
        raise RunnerError(f"{label}.{verb} must be a string")
    return condition


def _gate(raw: Any, phase: str, index: int) -> Gate:
    data = _mapping(raw, f"phases[{phase}].gates[{index}]")
    prefix = f"phases[{phase}].gates[{index}]"
    label = _string(data.get("label"), f"{prefix}.label")
    if not LABEL_RE.fullmatch(label or ""):
        raise RunnerError(f"{prefix}.label {label!r} is not a runtime label shape")
    command = _command(data.get("command"), f"{prefix}.command")
    lane = _string(data.get("lane"), f"{prefix}.lane")
    if lane not in LANES:
        raise RunnerError(f"{prefix}.lane {lane!r} is not one of {sorted(LANES)}")
    variant = _string(data.get("variant_of"), f"{prefix}.variant_of", required=False)
    if variant is not None and not LABEL_RE.fullmatch(variant):
        raise RunnerError(f"{prefix}.variant_of {variant!r} is not a runtime label shape")
    timeout = data.get("timeout_seconds")
    if timeout is not None and (not isinstance(timeout, (int, float)) or timeout <= 0):
        raise RunnerError(f"{prefix}.timeout_seconds must be a positive number")
    return Gate(
        label=label,
        command=command,
        lane=lane,
        condition=_condition(data.get("condition"), f"{prefix}.condition"),
        variant_of=variant,
        unestablished_capable=_bool(
            data.get("unestablished_capable"), f"{prefix}.unestablished_capable"
        ),
        native_preflight=_bool(data.get("native_preflight"), f"{prefix}.native_preflight"),
        timing_layer=_string(data.get("timing_layer"), f"{prefix}.timing_layer", required=False),
        docs_only=_bool(data.get("docs_only"), f"{prefix}.docs_only"),
        note=_string(data.get("note"), f"{prefix}.note", required=False),
        timeout_seconds=float(timeout) if timeout is not None else None,
    )


def _phase(raw: Any, index: int) -> Phase:
    data = _mapping(raw, f"phases[{index}]")
    identifier = _string(data.get("id"), f"phases[{index}].id")
    isolation = _string(data.get("isolation"), f"phases[{index}].isolation")
    if isolation not in {"alone", "concurrent"}:
        raise RunnerError(f"phases[{index}].isolation must be alone or concurrent")
    gates_raw = data.get("gates")
    if not isinstance(gates_raw, list):
        raise RunnerError(f"phases[{index}].gates must be a block list")
    if "fail_fast" not in data:
        raise RunnerError(f"phases[{index}].fail_fast is required")
    return Phase(
        identifier=identifier,
        isolation=isolation,
        fail_fast=_bool(data.get("fail_fast"), f"phases[{index}].fail_fast"),
        fail_message=_string(
            data.get("fail_message"), f"phases[{index}].fail_message", required=False
        ),
        gates=tuple(
            _gate(item, identifier, item_index) for item_index, item in enumerate(gates_raw)
        ),
    )


def load_gate_list(path: Path) -> GateList:
    try:
        raw = load_yaml_file(path)
    except (OSError, ValueError) as exc:
        raise RunnerError(f"could not read gate list {path}: {exc}") from exc
    data = _mapping(raw, "gate list")
    if data.get("schema") != SCHEMA:
        raise RunnerError(f"gate list schema must be {SCHEMA!r}")
    phases_raw = data.get("phases")
    if not isinstance(phases_raw, list) or not phases_raw:
        raise RunnerError("gate list phases must be a non-empty block list")
    variables = data.get("runner_variables", {})
    variables = _mapping(variables, "runner_variables")
    if any(not isinstance(name, str) or not name for name in variables):
        raise RunnerError("runner_variables keys must be non-empty strings")
    if any(
        not isinstance(value, str) or "\n" in value or "\r" in value for value in variables.values()
    ):
        raise RunnerError("runner_variables values must be one-line string meanings")
    phases = tuple(_phase(item, index) for index, item in enumerate(phases_raw))
    phase_ids = [phase.identifier for phase in phases]
    if len(phase_ids) != len(set(phase_ids)):
        raise RunnerError("phase ids must be unique")
    all_gates = [gate for phase in phases for gate in phase.gates]
    labels = [gate.label for gate in all_gates]
    if len(labels) != len(set(labels)):
        # Duplicate labels are allowed only when their rows explicitly form a variant.
        for label in set(labels):
            rows = [gate for gate in all_gates if gate.label == label]
            groups = {gate.variant_of or gate.label for gate in rows}
            if len(groups) != 1:
                raise RunnerError(f"duplicate gate label {label!r} is not variant-qualified")
    return GateList(phases=phases, runner_variables=frozenset(variables))
