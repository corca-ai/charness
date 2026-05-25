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
codex_audit = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.codex_session_audit_lib"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a compact Codex session efficiency map.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--source", choices=("auto", "tui", "sqlite"), default="auto")
    parser.add_argument("--thread-id", action="append", default=[])
    parser.add_argument("--list-threads", action="store_true")
    parser.add_argument("--since")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--max-auto-threads", type=int, default=12)
    parser.add_argument("--max-command-len", type=int, default=160)
    parser.add_argument("--max-tui-lines", type=int, default=5000)
    parser.add_argument("--include-command-snippets", action="store_true")
    return parser.parse_args()


def requested_threads(values: list[str]) -> tuple[str, ...]:
    return tuple(part.strip() for value in values for part in value.split(",") if part.strip())


def main() -> int:
    args = parse_args()
    try:
        payload = codex_audit.audit(
            codex_audit.AuditOptions(
                repo_root=args.repo_root.expanduser().resolve(),
                home=args.home.expanduser().resolve(),
                source=args.source,
                thread_ids=requested_threads(args.thread_id),
                list_threads=args.list_threads,
                since=args.since,
                top=args.top,
                max_auto_threads=args.max_auto_threads,
                max_command_len=args.max_command_len,
                max_tui_lines=args.max_tui_lines,
                include_command_snippets=args.include_command_snippets,
            )
        )
    except ValueError as exc:
        print(str(exc))
        return 2
    if args.format == "markdown" and not args.list_threads:
        print(codex_audit.render_markdown(payload))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
