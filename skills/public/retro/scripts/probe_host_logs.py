#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
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







_scripts_host_log_probe_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.host_log_probe_lib")
build_payload = _scripts_host_log_probe_lib_module.build_payload

_goal_metrics_render_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.goal_metrics_render_lib")
render_goal_metrics_block = _goal_metrics_render_lib_module.render_goal_metrics_block


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--home", type=Path, default=Path.home(), help="User home directory to probe for host CLI log locations")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repo root used to resolve repo-local log paths")
    parser.add_argument("--goal-path", type=Path, help="Optional goal artifact carrying a `Host metric window:` evidence line")
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="json (default) for the raw payload, or markdown for the standardized provider-safe goal-closeout metrics block",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(
        home=args.home.expanduser().resolve(),
        repo_root=args.repo_root.expanduser().resolve(),
        goal_path=args.goal_path,
    )
    if args.format == "markdown":
        print(render_goal_metrics_block(payload), end="")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
