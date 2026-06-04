#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))

SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)




_scripts_quality_bootstrap_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.quality_bootstrap_lib")
BootstrapValidationError = _scripts_quality_bootstrap_lib_module.BootstrapValidationError
bootstrap_quality_adapter = _scripts_quality_bootstrap_lib_module.bootstrap_quality_adapter


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root to bootstrap the quality adapter for")
    parser.add_argument("--output", type=Path, default=Path(".agents/quality-adapter.yaml"), help="Path to write the generated quality adapter YAML")
    parser.add_argument("--report-path", type=Path, default=Path(".charness/quality/bootstrap.json"), help="Path to write the bootstrap report JSON")
    parser.add_argument("--dry-run", action="store_true", help="Plan the bootstrap without writing the adapter or report")
    args = parser.parse_args()

    report = bootstrap_quality_adapter(
        repo_root=args.repo_root.resolve(),
        output_path=args.output,
        report_path=args.report_path,
        dry_run=args.dry_run,
    )
    sys.stdout.write(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    try:
        main()
    except BootstrapValidationError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
