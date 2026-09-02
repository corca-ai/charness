#!/usr/bin/env python3
"""Measure adapter-owned startup probes for agent-facing or installable CLIs."""

from __future__ import annotations

import argparse
import contextlib
import io
import runpy
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from summary_output_lib import add_output_args, bounded_list, emit_selected  # noqa: E402


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
run_process = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.core.subprocess_guard"
).run_process
_resolve_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter_module.load_adapter
_adapter_version_verdict = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.adapter_version_verdict"
)
DEFAULT_PROBE_TIMEOUT_SECONDS = 20


def _record_runtime_script_path(repo_root: Path) -> Path:
    repo_candidate = repo_root / "scripts" / "record_quality_runtime.py"
    if repo_candidate.is_file():
        return repo_candidate
    for ancestor in Path(__file__).resolve().parents:
        candidate = ancestor / "scripts" / "record_quality_runtime.py"
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("record_quality_runtime.py not found")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repo root whose adapter-declared startup probes should be measured",
    )
    parser.add_argument(
        "--class",
        dest="probe_class",
        choices=("standing", "release", "all"),
        default="all",
        help="Probe class to run (standing, release, or all)",
    )
    add_output_args(
        parser,
        summary_help="Emit compact YAML startup-probe status and failure counts",
        detail_help="Emit the full startup-probe measurement report as YAML",
    )
    parser.add_argument(
        "--record-runtime-signals",
        action="store_true",
        help="Persist the latest elapsed time for each measured probe through scripts/record_quality_runtime.py.",
    )
    parser.add_argument(
        "--state-root",
        type=Path,
        help="External quality runtime-state directory for recorded samples; defaults to <repo>/.charness/quality.",
    )
    return parser.parse_args()


def _selected_probes(probes: list[dict[str, Any]], probe_class: str) -> list[dict[str, Any]]:
    if probe_class == "all":
        return probes
    return [probe for probe in probes if probe.get("class") == probe_class]


def _record_runtime_signal(
    repo_root: Path,
    label: str,
    elapsed_ms: int,
    status: str,
    *,
    state_root: Path | None = None,
) -> None:
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    script_path = _record_runtime_script_path(repo_root)
    command = [
        "--repo-root",
        str(repo_root),
        "--label",
        label,
        "--elapsed-ms",
        str(elapsed_ms),
        "--status",
        status,
        "--timestamp",
        timestamp,
    ]
    if state_root is not None:
        command.extend(("--state-root", str(state_root)))
    recorder = SKILL_RUNTIME.load_repo_module_from_skill_script(
        __file__, "scripts.record_quality_runtime"
    )
    previous_argv = sys.argv
    try:
        sys.argv = [str(script_path), *command]
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            returncode = recorder.main()
    finally:
        sys.argv = previous_argv
    if returncode != 0:
        raise RuntimeError(f"record_quality_runtime exited with status {returncode}")


def _timeout_seconds(probe: dict[str, Any]) -> float:
    try:
        value = float(probe.get("timeout_seconds", DEFAULT_PROBE_TIMEOUT_SECONDS))
    except (TypeError, ValueError):
        return float(DEFAULT_PROBE_TIMEOUT_SECONDS)
    return value if value > 0 else float(DEFAULT_PROBE_TIMEOUT_SECONDS)


def _measure_probe(
    repo_root: Path,
    probe: dict[str, Any],
    *,
    record_runtime_signals: bool,
    state_root: Path | None = None,
) -> dict[str, Any]:
    elapsed_samples: list[int] = []
    last_result: subprocess.CompletedProcess[str] | None = None
    timeout_error = False
    timeout_seconds = _timeout_seconds(probe)
    for _ in range(int(probe["samples"])):
        start_ns = time.perf_counter_ns()
        result = run_process(list(probe["command"]), cwd=repo_root, timeout_seconds=timeout_seconds)
        timed_out = result.returncode == 124 and result.stderr.startswith("timed out after ")
        if timed_out:
            timeout_error = True
            elapsed_samples.append(int((time.perf_counter_ns() - start_ns) / 1_000_000))
            break
        elapsed_ms = int((time.perf_counter_ns() - start_ns) / 1_000_000)
        elapsed_samples.append(elapsed_ms)
        last_result = result
        if result.returncode != 0:
            break
    latest_elapsed_ms = elapsed_samples[-1]
    status = (
        "command-timeout"
        if timeout_error
        else "ok"
        if last_result and last_result.returncode == 0
        else "command-failed"
    )
    if record_runtime_signals:
        _record_runtime_signal(
            repo_root,
            str(probe["label"]),
            latest_elapsed_ms,
            "pass" if status == "ok" else "fail",
            state_root=state_root,
        )
    payload = {
        "label": probe["label"],
        "command": probe["command"],
        "class": probe["class"],
        "startup_mode": probe["startup_mode"],
        "surface": probe["surface"],
        "samples_requested": probe["samples"],
        "samples_ran": len(elapsed_samples),
        "timeout_seconds": timeout_seconds,
        "elapsed_samples_ms": elapsed_samples,
        "latest_elapsed_ms": latest_elapsed_ms,
        "median_elapsed_ms": int(statistics.median(elapsed_samples)),
        "status": status,
    }
    if timeout_error:
        payload["returncode"] = 124
        payload["stdout"] = result.stdout or ""
        payload["stderr"] = ""
    elif last_result and last_result.returncode != 0:
        payload["returncode"] = last_result.returncode
        payload["stdout"] = last_result.stdout
        payload["stderr"] = last_result.stderr
    return payload


def evaluate(
    repo_root: Path,
    *,
    probe_class: str,
    record_runtime_signals: bool,
    state_root: Path | None = None,
) -> dict[str, Any]:
    # GUARDED AT THE READ SITE. Measured on the real CLI at `00c50ed3f`: a repo declaring
    # one `startup_probes` entry under `version: 9` printed
    # `No startup probes matched the selected class.`, exit 0 -- the reader reporting the
    # repo declared none, over a repo that declared one.
    refusal = _adapter_version_verdict.unspeakable_version_message(
        load_adapter, repo_root, adapter_name="quality-adapter.yaml"
    )
    if refusal is not None:
        raise SystemExit(refusal)
    adapter = load_adapter(repo_root)
    probes = adapter["data"].get("startup_probes", []) or []
    selected = _selected_probes(probes, probe_class)
    measured = [
        _measure_probe(
            repo_root,
            probe,
            record_runtime_signals=record_runtime_signals,
            state_root=state_root,
        )
        for probe in selected
    ]
    failures = [probe for probe in measured if probe["status"] != "ok"]
    return {
        "adapter_path": adapter.get("path"),
        "probe_class": probe_class,
        "probes_configured": len(probes),
        "probes_measured": len(measured),
        "measured": measured,
        "failures": failures,
    }


def _format_human(report: dict[str, Any]) -> str:
    if report["probes_measured"] == 0:
        return "No startup probes matched the selected class."
    lines: list[str] = []
    for probe in report["measured"]:
        line = (
            f"{probe['status'].upper():<14} {probe['label']}: "
            f"latest {probe['latest_elapsed_ms']}ms, median {probe['median_elapsed_ms']}ms "
            f"({probe['class']}, {probe['startup_mode']}, {probe['surface']})"
        )
        if probe["status"] != "ok":
            line += f", rc {probe['returncode']}"
        lines.append(line)
    return "\n".join(lines)


def summarize(report: dict[str, Any]) -> dict[str, Any]:
    measured = report.get("measured", [])
    failures = report.get("failures", [])
    summary = {
        "summary_note": "summary is triage output; use --detail for per-sample probe timings",
        "adapter_path": report.get("adapter_path"),
        "probe_class": report["probe_class"],
        "probes_configured": report["probes_configured"],
        "probes_measured": report["probes_measured"],
        "status_counts": {
            "ok": sum(1 for probe in measured if probe.get("status") == "ok"),
            "failed": len(failures),
        },
    }
    summary.update(bounded_list({"failures": failures}, "failures"))
    return summary


def main() -> int:
    args = _parse_args()
    report = evaluate(
        args.repo_root.resolve(),
        probe_class=args.probe_class,
        record_runtime_signals=args.record_runtime_signals,
        state_root=args.state_root.resolve() if args.state_root else None,
    )
    if not emit_selected(report, args, summarize=summarize):
        print(_format_human(report))
    return 1 if report["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
