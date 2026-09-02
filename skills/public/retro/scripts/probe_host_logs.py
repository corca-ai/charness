#!/usr/bin/env python3
"""Collect generic Claude and Codex host metrics."""
from __future__ import annotations

import argparse
import runpy
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
host_log_probe = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.evidence.host_log_probe_lib"
)
render_yaml = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.yaml_output"
).render_yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe generic Claude and Codex host logs")
    parser.add_argument(
        "--home",
        type=Path,
        default=Path.home(),
        help="User home directory containing host log locations",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repo root used to identify the Claude project log",
    )
    parser.add_argument(
        "--claude-session-file",
        type=Path,
        help="Use this Claude session JSONL instead of the newest project session",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = host_log_probe.build_payload(
        home=args.home.expanduser().resolve(),
        repo_root=args.repo_root.expanduser().resolve(),
        claude_session_file=(
            args.claude_session_file.expanduser() if args.claude_session_file else None
        ),
    )
    print(render_yaml(payload), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
