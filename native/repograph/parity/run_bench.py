#!/usr/bin/env python3
"""Run the bounded issue #745 static-family benchmark protocol."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import platform
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    return parser.parse_args()


def ensure_binary(root: Path) -> Path:
    binary = root / "native" / "repograph" / "target" / "release" / "repograph"
    if binary.is_file():
        return binary
    result = subprocess.run(
        ["cargo", "build", "--release", "--offline"],
        cwd=root / "native" / "repograph",
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "cargo build failed")
    return binary


def load_owners(root: Path) -> tuple[Any, Any]:
    sys.path.insert(0, str(root))
    return (
        importlib.import_module("scripts.check_export_safe_imports"),
        importlib.import_module("scripts.gates.check_standalone_imports"),
    )


def run_command(command: list[str], cwd: Path) -> dict[str, Any]:
    started = time.monotonic()
    result = subprocess.run(
        ["/usr/bin/time", "-v", *command],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    elapsed = time.monotonic() - started
    stderr = result.stderr
    def metric(pattern: str) -> float | None:
        match = re.search(pattern, stderr, re.MULTILINE)
        return float(match.group(1)) if match else None

    wall_text = re.search(r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\):\s*(\S+)", stderr)
    wall_seconds = parse_elapsed(wall_text.group(1)) if wall_text else elapsed
    if wall_seconds <= 0:
        wall_seconds = elapsed
    return {
        "exit_class": result.returncode,
        "wall_seconds": wall_seconds,
        "user_seconds": metric(r"User time \(seconds\):\s*([0-9.]+)"),
        "sys_seconds": metric(r"System time \(seconds\):\s*([0-9.]+)"),
        "peak_rss_kib": metric(r"Maximum resident set size \(kbytes\):\s*([0-9.]+)"),
    }


def parse_elapsed(value: str) -> float:
    pieces = value.split(":")
    try:
        numbers = [float(piece) for piece in pieces]
    except ValueError:
        return 0.0
    if len(numbers) == 3:
        return numbers[0] * 3600 + numbers[1] * 60 + numbers[2]
    if len(numbers) == 2:
        return numbers[0] * 60 + numbers[1]
    return numbers[0]


def git_output(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, check=False, capture_output=True)
    if result.returncode != 0:
        return "unestablished"
    return result.stdout.decode("utf-8", errors="replace")


def identity(root: Path) -> dict[str, Any]:
    porcelain = git_output(root, "status", "--porcelain=v1", "-z").encode("utf-8")
    cpu_model = "unknown"
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.is_file():
        for line in cpuinfo.read_text(errors="replace").splitlines():
            if line.lower().startswith("model name") and ":" in line:
                cpu_model = line.split(":", 1)[1].strip()
                break
    rustc = subprocess.run(["rustc", "--version"], check=False, capture_output=True, text=True)
    uname = subprocess.run(["uname", "-a"], check=False, capture_output=True, text=True)
    return {
        "repo": {
            "head_sha": git_output(root, "rev-parse", "HEAD").strip(),
            "porcelain_sha256": hashlib.sha256(porcelain).hexdigest(),
        },
        "host": {
            "uname_a": uname.stdout.strip() or "unestablished",
            "platform": platform.uname()._asdict(),
            "cpu_model": cpu_model,
        },
        "build": {
            "rustc_version": rustc.stdout.strip() or "unestablished",
            "cargo_profile": "release",
        },
    }


def rust_json(binary: Path, args: list[str], root: Path) -> dict[str, Any]:
    result = subprocess.run([str(binary), *args], cwd=root, check=False, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"benchmark command emitted invalid JSON: {result.stdout!r}") from exc


def surface_args(paths: list[str]) -> list[str]:
    return sum((["--path", path] for path in paths), [])


def comparison_commands(root: Path, binary: Path) -> list[dict[str, Any]]:
    sample = ["README.md", "AGENTS.md", "scripts/check_export_safe_imports.py", "docs/index.md"]
    return [
        {
            "command": "export-safe",
            "python_command": [sys.executable, "scripts/check_export_safe_imports.py", "--repo-root", str(root)],
            "rust_command": [str(binary), "export-safe", "--repo-root", str(root)],
            "bound": "direct owner CLI; full export-safe target universe",
        },
        {
            "command": "standalone-targets",
            "python_command": [
                sys.executable,
                "-c",
                "import sys; from pathlib import Path; sys.path.insert(0, sys.argv[1]); "
                "from scripts.gates.check_standalone_imports import discover_modules; "
                "discover_modules(Path(sys.argv[1]))",
                str(root),
            ],
            "rust_command": [str(binary), "standalone-targets", "--repo-root", str(root)],
            "bound": "static-selection-only; Python owner discovery isolated before runtime probes",
        },
        {
            "command": "match-surfaces",
            "python_command": [
                sys.executable,
                "scripts/gates/check_changed_surfaces.py",
                "--repo-root",
                str(root),
                "--paths",
                *sample,
            ],
            "rust_command": [str(binary), "match-surfaces", "--repo-root", str(root), *surface_args(sample)],
            "bound": "four fixed changed paths via the thinnest Python CLI consumer",
            "sample_paths": sample,
        },
    ]


def analyzed_counts(root: Path, binary: Path, export_owner: Any, standalone_owner: Any) -> dict[str, dict[str, int]]:
    export_count = len(export_owner.iter_python_targets(root))
    standalone_count = len(standalone_owner.discover_modules(root))
    export_payload = rust_json(binary, ["export-safe", "--repo-root", str(root)], root)
    standalone_payload = rust_json(binary, ["standalone-targets", "--repo-root", str(root)], root)
    return {
        "export-safe": {"python": export_count, "rust": export_payload["files_total"]},
        "standalone-targets": {"python": standalone_count, "rust": standalone_payload["discovered"]},
        "match-surfaces": {"python": 4, "rust": 4},
    }


def summarize(runs: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for side in ("python", "rust"):
        values = [run[side]["wall_seconds"] for run in runs]
        result[side] = {
            "wall_min_seconds": min(values),
            "wall_max_seconds": max(values),
            "wall_mean_seconds": sum(values) / len(values),
            "cpu_mean_seconds": sum(
                (run[side]["user_seconds"] or 0.0) + (run[side]["sys_seconds"] or 0.0)
                for run in runs
            )
            / len(runs),
            "peak_rss_max_kib": max(run[side]["peak_rss_kib"] or 0.0 for run in runs),
        }
    result["wall_speedup_worst_case"] = min(
        run["python"]["wall_seconds"] / max(run["rust"]["wall_seconds"], 1e-9) for run in runs
    )
    return result


def main() -> int:
    args = parse_args()
    root = args.repo_root.expanduser().resolve()
    binary = ensure_binary(root)
    export_owner, standalone_owner = load_owners(root)
    report: dict[str, Any] = {
        "schema": "repograph.bench.v1",
        "repo_root": str(root),
        "protocol": {
            "runs_per_side": 6,
            "cold_runs": 3,
            "warm_runs": 3,
            "measurement": "/usr/bin/time -v; cold means the first three fresh processes, warm the next three after OS/process cache priming",
        },
        "identity": identity(root),
        "comparisons": [],
    }
    counts = analyzed_counts(root, binary, export_owner, standalone_owner)
    for comparison in comparison_commands(root, binary):
        runs = []
        for phase in ("cold", "warm"):
            for iteration in range(1, 4):
                runs.append(
                    {
                        "phase": phase,
                        "iteration": iteration,
                        "python": run_command(comparison["python_command"], root),
                        "rust": run_command(comparison["rust_command"], root),
                    }
                )
        report["comparisons"].append(
            {
                "command": comparison["command"],
                "bound": comparison["bound"],
                "analyzed_file_count": counts[comparison["command"]],
                "sample_paths": comparison.get("sample_paths"),
                "runs": runs,
                "summary": summarize(runs),
            }
        )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"schema": "repograph.bench.v1", "error": str(exc)}))
        raise SystemExit(70)
