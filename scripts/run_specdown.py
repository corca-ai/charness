#!/usr/bin/env python3
"""Run specdown using an ephemeral configuration as a normal argv gate."""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

from runtime_bootstrap import import_repo_module

_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _guard.run_process


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    output_dir = args.output_dir.resolve()
    if shutil.which("specdown") is None:
        print(
            "specdown is required for executable specs. Install from "
            "https://github.com/corca-ai/specdown or run charness tool doctor specdown "
            "for current readiness.",
            file=os.sys.stderr,
        )
        return 1
    output_dir.mkdir(parents=True, exist_ok=True)
    config = run_process(
        [
            "python3",
            "scripts/plugin_export/specdown_ephemeral_config.py",
            "--repo-root",
            str(root),
            "--out-dir",
            str(output_dir),
        ],
        cwd=root,
        env=os.environ.copy(),
        timeout_seconds=None,
    )
    if config.stdout:
        print(config.stdout, end="")
    if config.stderr:
        print(config.stderr, end="", file=os.sys.stderr)
    if config.returncode != 0:
        return config.returncode
    config_path = config.stdout.strip().splitlines()[-1] if config.stdout.strip() else ""
    if not config_path:
        print("run-quality: specdown config command returned no path", file=os.sys.stderr)
        return 1
    try:
        result = run_process(
            [
                "specdown",
                "run",
                "-config",
                config_path,
                "-jobs",
                "4",
                "-out",
                str(output_dir),
            ],
            cwd=root,
            env=os.environ.copy(),
            timeout_seconds=None,
        )
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=os.sys.stderr)
        return result.returncode
    finally:
        try:
            Path(config_path).unlink()
        except OSError:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
