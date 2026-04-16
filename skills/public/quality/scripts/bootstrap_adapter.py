#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


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
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)




_scripts_quality_bootstrap_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.quality_bootstrap_lib")
BootstrapValidationError = _scripts_quality_bootstrap_lib_module.BootstrapValidationError
bootstrap_quality_adapter = _scripts_quality_bootstrap_lib_module.bootstrap_quality_adapter


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path(".agents/quality-adapter.yaml"))
    parser.add_argument("--report-path", type=Path, default=Path(".charness/quality/bootstrap.json"))
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
    try:
        main()
    except BootstrapValidationError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
