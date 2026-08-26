#!/usr/bin/env python3
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
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)







_scripts_host_log_probe_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.host_log_probe_lib")
build_payload = _scripts_host_log_probe_lib_module.build_payload

_goal_metrics_render_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.goal_metrics_render_lib")
render_goal_metrics_block = _goal_metrics_render_lib_module.render_goal_metrics_block
# Command output is unconditionally YAML since the 2026-08-14 --json removal. The
# format CHOICE was renamed with the payload: a flag literally spelled `json` that
# emits YAML is the lying-flag shape the migration exists to remove, and `--format
# json` was invisible to a scan looking only for `--json`.
render_yaml = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output").render_yaml


# argparse and `render_output` read the same tuple, so a new format cannot be
# accepted on the command line without a renderer behind it (or vice versa).
FORMAT_CHOICES = ("yaml", "markdown")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--home", type=Path, default=Path.home(), help="User home directory to probe for host CLI log locations")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repo root used to resolve repo-local log paths")
    parser.add_argument("--goal-path", type=Path, help="Optional goal artifact carrying a `Host metric window:` evidence line")
    parser.add_argument(
        "--goal-lineage-file",
        type=Path,
        help="Optional repo-local Goal Run lineage JSON to attach to the host-metric evidence.",
    )
    parser.add_argument(
        "--claude-session-file",
        type=Path,
        help="Scope the Claude session audit to this project session JSONL instead of the newest-by-mtime file",
    )
    parser.add_argument(
        "--format",
        choices=FORMAT_CHOICES,
        default="yaml",
        help="yaml (default) for the raw payload, or markdown for the standardized provider-safe goal-closeout metrics block",
    )
    return parser.parse_args()


def render_output(payload: dict, output_format: str) -> str:
    """Render the probe payload for one `--format` choice, trailing newline included.

    A lookup rather than an `output_format == "markdown"` branch. With exactly two
    choices, `==` and `>=` are behaviourally identical ("json" sorts before
    "markdown"), so that comparison carries a branch no test can pin — the mutation
    gate reported exactly that as a survivor. A mapping keyed by the same tuple
    argparse validates against has no such blind spot, and adding a third format
    cannot silently reintroduce one.
    """
    renderers = {
        "yaml": lambda: render_yaml(payload),
        "markdown": lambda: render_goal_metrics_block(payload),
    }
    return renderers[output_format]()


def main() -> int:
    args = parse_args()
    try:
        payload = build_payload(
            home=args.home.expanduser().resolve(),
            repo_root=args.repo_root.expanduser().resolve(),
            goal_path=args.goal_path,
            claude_session_file=args.claude_session_file.expanduser() if args.claude_session_file else None,
            goal_lineage_path=args.goal_lineage_file,
        )
    except ValueError as exc:
        print(
            render_yaml(
                {
                    "status": "refused",
                    "error": {"code": "invalid_lineage", "message": str(exc)},
                }
            ),
            end="",
        )
        return 2
    print(render_output(payload, args.format), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
