#!/usr/bin/env python3
"""Measure adapter-owned startup probes for agent-facing or installable CLIs."""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_resolve_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter_module.load_adapter


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
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--class", dest="probe_class", choices=("standing", "release", "all"), default="all")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument(
        "--record-runtime-signals",
        action="store_true",
        help="Persist the latest elapsed time for each measured probe through scripts/record_quality_runtime.py.",
    )
    return parser.parse_args()


def _selected_probes(probes: list[dict[str, Any]], probe_class: str) -> list[dict[str, Any]]:
    if probe_class == "all":
        return probes
    return [probe for probe in probes if probe.get("class") == probe_class]


def _record_runtime_signal(repo_root: Path, label: str, elapsed_ms: int, status: str) -> None:
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    script_path = _record_runtime_script_path(repo_root)
    subprocess.run(
        [
            "python3",
            str(script_path),
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
        ],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )


def _measure_probe(repo_root: Path, probe: dict[str, Any], *, record_runtime_signals: bool) -> dict[str, Any]:
    elapsed_samples: list[int] = []
    last_result: subprocess.CompletedProcess[str] | None = None
    for _ in range(int(probe["samples"])):
        start_ns = time.perf_counter_ns()
        result = subprocess.run(
            list(probe["command"]),
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
        elapsed_ms = int((time.perf_counter_ns() - start_ns) / 1_000_000)
        elapsed_samples.append(elapsed_ms)
        last_result = result
        if result.returncode != 0:
            break
    assert last_result is not None
    latest_elapsed_ms = elapsed_samples[-1]
    status = "ok" if last_result.returncode == 0 else "command-failed"
    if record_runtime_signals:
        _record_runtime_signal(
            repo_root,
            str(probe["label"]),
            latest_elapsed_ms,
            "pass" if last_result.returncode == 0 else "fail",
        )
    payload = {
        "label": probe["label"],
        "command": probe["command"],
        "class": probe["class"],
        "startup_mode": probe["startup_mode"],
        "surface": probe["surface"],
        "samples_requested": probe["samples"],
        "samples_ran": len(elapsed_samples),
        "elapsed_samples_ms": elapsed_samples,
        "latest_elapsed_ms": latest_elapsed_ms,
        "median_elapsed_ms": int(statistics.median(elapsed_samples)),
        "status": status,
    }
    if last_result.returncode != 0:
        payload["returncode"] = last_result.returncode
        payload["stdout"] = last_result.stdout
        payload["stderr"] = last_result.stderr
    return payload


def evaluate(repo_root: Path, *, probe_class: str, record_runtime_signals: bool) -> dict[str, Any]:
    adapter = load_adapter(repo_root)
    probes = adapter["data"].get("startup_probes", []) or []
    selected = _selected_probes(probes, probe_class)
    measured = [
        _measure_probe(repo_root, probe, record_runtime_signals=record_runtime_signals)
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


def main() -> int:
    args = _parse_args()
    report = evaluate(
        args.repo_root.resolve(),
        probe_class=args.probe_class,
        record_runtime_signals=args.record_runtime_signals,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(_format_human(report))
    return 1 if report["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
