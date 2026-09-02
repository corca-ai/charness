#!/usr/bin/env python3
"""Capture every quality-gate file universe in one diffable YAML artifact."""

from __future__ import annotations

import argparse
import json
import shlex
import sys
from pathlib import Path
from typing import Sequence

try:
    import yaml
except ImportError:  # yaml_output has the same JSON fallback on minimal hosts
    yaml = None

from scripts.core.subprocess_guard import run_process
from scripts.yaml_output import emit_yaml, render_yaml

BASELINE_RELATIVE_PATH = "charness-artifacts/quality/2026-09-02-gate-universes-before-770.yaml"
PREMISES_RELATIVE_PATH = "charness-artifacts/quality/2026-09-02-scripts-packaging-premises.md"


def _python_command(*parts: str) -> list[str]:
    return [sys.executable, *parts]


def _bespoke_commands() -> list[tuple[str, Sequence[str] | str]]:
    detector_patterns = (
        "scripts/check_*.py",
        "scripts/validate_*.py",
        "skills/public/*/scripts/inventory_*.py",
        "skills/public/*/scripts/check_*.py",
        "skills/public/*/scripts/validate_*.py",
    )
    detector_code = (
        'import glob; print("\\n".join(sorted({p for pat in '
        f'{detector_patterns!r} for p in glob.glob(pat) if not p.endswith("_lib.py")}})))'
    )
    return [
        (
            "unreferenced_scripts",
            _python_command("-m", "tools.check_unreferenced_scripts", "--repo-root", "."),
        ),
        (
            "code_lengths_headroom",
            _python_command("scripts/check_code_lengths.py", "--repo-root", ".", "--headroom"),
        ),
        (
            "adapter_gate_design",
            _python_command(
                "skills/public/quality/scripts/inventory_adapter_gate_design.py",
                "--repo-root",
                ".",
                "--detail",
            ),
        ),
        (
            "python_compile_array",
            [
                "bash",
                "-c",
                'shopt -s nullglob globstar; printf "%s\\n" scripts/*.py scripts/**/*.py '
                "skills/public/*/scripts/*.py skills/public/*/scripts/**/*.py "
                "skills/support/*/scripts/*.py skills/support/*/scripts/**/*.py "
                "skills/shared/scripts/*.py skills/shared/scripts/**/*.py "
                "skills/support/*/vendor/*.py | sort -u",
            ],
        ),
        (
            "shell_discovery",
            [
                "bash",
                "-c",
                'find . -maxdepth 1 -type f -name "*.sh"; '
                'find scripts -maxdepth 1 -type f -name "*.sh"; '
                'find tests -type f -name "*.sh"; '
                "find .githooks -maxdepth 1 -type f | sort",
            ],
        ),
        (
            "empty_scope_detectors",
            _python_command("-c", detector_code),
        ),
    ]


def _render_command(command: Sequence[str] | str) -> str:
    return command if isinstance(command, str) else shlex.join(command)


def _parsed_output(stdout: str) -> object:
    if yaml is not None:
        return yaml.safe_load(stdout)
    return json.loads(stdout)


def _files_from_output(name: str, stdout: str) -> list[str]:
    if (
        name == "python_compile_array"
        or name == "shell_discovery"
        or name == "empty_scope_detectors"
    ):
        return sorted(line for line in stdout.splitlines() if line)
    payload = _parsed_output(stdout)
    if name == "quality_universes":
        families = payload.get("files", {}) if isinstance(payload, dict) else {}
        return sorted(
            path
            for values in families.values()
            if isinstance(values, list)
            for path in values
            if isinstance(path, str)
        )
    if name == "unreferenced_scripts":
        rows = payload.get("files", []) if isinstance(payload, dict) else []
        return sorted(row["path"] for row in rows if isinstance(row, dict) and "path" in row)
    if name == "code_lengths_headroom":
        rows = payload.get("headroom", []) if isinstance(payload, dict) else []
        return sorted(row["path"] for row in rows if isinstance(row, dict) and "path" in row)
    if name == "adapter_gate_design":
        paths = payload.get("reviewed_paths", []) if isinstance(payload, dict) else []
        return sorted(path for path in paths if isinstance(path, str))
    raise ValueError(f"unknown snapshot output: {name}")


def _without_output_path(stdout: str, repo_root: Path, output: Path | None) -> str:
    excluded = {BASELINE_RELATIVE_PATH, PREMISES_RELATIVE_PATH}
    if output is not None:
        try:
            excluded.add(output.resolve().relative_to(repo_root).as_posix())
        except ValueError:
            pass
    return "\n".join(
        line for line in stdout.splitlines() if line.strip().removeprefix("- ") not in excluded
    ) + ("\n" if stdout.endswith("\n") else "")


def snapshot(repo_root: Path, *, output: Path | None = None) -> dict[str, object]:
    generic_command = _python_command(
        "scripts/quality_universes_lib.py", "--repo-root", ".", "--files"
    )
    commands: list[tuple[str, Sequence[str] | str]] = [
        ("quality_universes", generic_command),
        *_bespoke_commands(),
    ]
    results: list[dict[str, object]] = []
    for name, command in commands:
        result = run_process(command, cwd=repo_root, timeout_seconds=1800)
        stdout = _without_output_path(result.stdout, repo_root, output)
        results.append(
            {
                "name": name,
                "command": _render_command(command),
                "returncode": result.returncode,
                "files": _files_from_output(name, stdout) if result.returncode == 0 else [],
                "stderr": result.stderr,
            }
        )
    return {
        "schema": "scripts-gate-universes/v1",
        "commands": results,
        "ok": all(result["returncode"] == 0 for result in results),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    out = args.out.expanduser()
    if not out.is_absolute():
        out = Path.cwd() / out
    artifact = snapshot(args.repo_root.resolve(), output=out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_yaml(artifact), encoding="utf-8")
    emit_yaml({"out": str(out), "ok": artifact["ok"]})
    return 0 if artifact["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
