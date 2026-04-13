#!/usr/bin/env python3
# ruff: noqa: E402
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
sys.path[:0] = [str(SCRIPT_PATH.parents[4]), str(SCRIPT_PATH.parents[3])]

from scripts.quality_bootstrap_lib import bootstrap_quality_adapter


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path(".agents/quality-adapter.yaml"))
    parser.add_argument("--report-path", type=Path, default=Path("skill-outputs/quality/bootstrap.json"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    report = bootstrap_quality_adapter(
        repo_root=args.repo_root.resolve(),
        output_path=args.output,
        report_path=args.report_path,
        dry_run=args.dry_run,
    )
    sys.stdout.write(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
