#!/usr/bin/env python3
"""Concurrent declarative gate phase execution through subprocess_guard."""

from __future__ import annotations

import sys
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import dataclass
from typing import TextIO

from run_quality_engine_model import Gate, Phase
from run_quality_engine_runtime import RuntimeContext, substitute_command

from runtime_bootstrap import import_repo_module

_guard = import_repo_module(__file__, "scripts.subprocess_guard")
run_monitored_phase = _guard.run_monitored_phase


class _QuietStream:
    def write(self, value: str) -> int:
        return len(value)

    def flush(self) -> None:
        return None


_GUARD_STREAM = _QuietStream()


@dataclass(frozen=True)
class GateResult:
    gate: Gate
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
    elapsed_ms: int
    status: str

    @property
    def log(self) -> str:
        return self.stdout + self.stderr


def _run_gate(gate: Gate, command: list[str], context: RuntimeContext, phase: Phase) -> GateResult:
    try:
        outcome = run_monitored_phase(
            command,
            cwd=context.repo_root,
            phase=phase.identifier,
            timeout_seconds=gate.timeout_seconds,
            heartbeat_seconds=0.1,
            env=context.environment,
            stream=_GUARD_STREAM,
        )
        returncode = int(outcome.returncode)
        stdout = outcome.stdout or ""
        stderr = outcome.stderr or ""
        elapsed_ms = max(0, round(float(outcome.elapsed_seconds) * 1000))
    except Exception as exc:  # a child-launch failure is a gate failure, not a runner crash
        returncode, stdout, stderr, elapsed_ms = (
            2,
            "",
            f"run-quality: could not start {gate.label}: {exc}\n",
            0,
        )
    if returncode == 0:
        status = "pass"
    elif returncode in {3, 4} and gate.unestablished_capable:
        status = "unestablished"
    else:
        status = "fail"
    return GateResult(gate, tuple(command), returncode, stdout, stderr, elapsed_ms, status)


def _heartbeat(
    phase: Phase,
    labels: list[str],
    started: dict[str, float],
    remaining: set[str],
    stream: TextIO,
) -> None:
    now = time.monotonic()
    running = [
        f"{label}:{_format_elapsed(round((now - started[label]) * 1000))}"
        for label in labels
        if label in remaining
    ][:5]
    if len(remaining) > len(running):
        running.append(f"+{len(remaining) - len(running)}-more")
    print(
        f"run-quality: HEARTBEAT remaining={len(remaining)} running={','.join(running) or 'none'}",
        file=stream,
    )


def _format_elapsed(elapsed_ms: int) -> str:
    if elapsed_ms >= 1000:
        return f"{elapsed_ms // 1000}.{(elapsed_ms % 1000) // 100}s"
    return f"{elapsed_ms}ms"


def run_phase(
    phase: Phase,
    gates: tuple[Gate, ...],
    *,
    context: RuntimeContext,
    variables: dict[str, list[str] | str],
    heartbeat_seconds: int,
    stream: TextIO | None = None,
) -> tuple[list[GateResult], int]:
    stream = sys.stderr if stream is None else stream
    if not gates:
        return [], 0
    commands = [substitute_command(gate.command, variables) for gate in gates]
    started = {gate.label: time.monotonic() for gate in gates}
    for gate in gates:
        print(f"run-quality: CHECK_START label={gate.label}", file=stream)
    print(
        f"run-quality: BATCH_START checks={len(gates)} first={gates[0].label} last={gates[-1].label}",
        file=stream,
    )
    max_workers = 1 if phase.isolation == "alone" else len(gates)
    results: list[GateResult] = []
    pending_labels = {gate.label for gate in gates}
    next_heartbeat = time.monotonic() + heartbeat_seconds
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_run_gate, gate, command, context, phase): gate.label
            for gate, command in zip(gates, commands)
        }
        order = {gate.label: index for index, gate in enumerate(gates)}
        unfinished = set(futures)
        while unfinished:
            timeout = 0.1
            if heartbeat_seconds > 0:
                timeout = min(timeout, max(0.0, next_heartbeat - time.monotonic()))
            done, unfinished = wait(unfinished, timeout=timeout, return_when=FIRST_COMPLETED)
            if not done:
                if heartbeat_seconds > 0 and time.monotonic() >= next_heartbeat:
                    _heartbeat(
                        phase, [gate.label for gate in gates], started, pending_labels, stream
                    )
                    next_heartbeat = time.monotonic() + heartbeat_seconds
                continue
            completed = sorted(
                (future.result() for future in done), key=lambda result: order[result.gate.label]
            )
            for result in completed:
                results.append(result)
                pending_labels.discard(result.gate.label)
            if heartbeat_seconds > 0 and time.monotonic() >= next_heartbeat and unfinished:
                _heartbeat(phase, [gate.label for gate in gates], started, pending_labels, stream)
                next_heartbeat = time.monotonic() + heartbeat_seconds
    by_label = {result.gate.label: result for result in results}
    phase_rc = 0
    for gate in gates:
        result = by_label[gate.label]
        if result.status == "fail":
            phase_rc = result.returncode
    return results, phase_rc
