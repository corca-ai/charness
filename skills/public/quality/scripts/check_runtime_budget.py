#!/usr/bin/env python3
"""Enforce per-command runtime budgets recorded in runtime-signals.json."""
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
load_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter").load_adapter
runtime_budget_lib = SKILL_RUNTIME.load_local_skill_module(__file__, "runtime_budget_lib")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument(
        "--top-runtime-count",
        type=int,
        default=runtime_budget_lib.DEFAULT_TOP_RUNTIME_COUNT,
        help="Number of recent runtime hot spots to include in the report.",
    )
    args = parser.parse_args()

    report = runtime_budget_lib.evaluate(
        args.repo_root.resolve(),
        load_adapter,
        top_runtime_count=max(args.top_runtime_count, 0),
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(runtime_budget_lib.format_human(report))

    if report["violations"]:
        if not args.json:
            for v in report["violations"]:
                print(
                    "runtime budget exceeded: "
                    f"{v['label']} recent median {v['median_recent_elapsed_ms']}ms "
                    f"(latest {v['latest_elapsed_ms']}ms, budget {v['budget_ms']}ms)",
                    file=sys.stderr,
                )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
