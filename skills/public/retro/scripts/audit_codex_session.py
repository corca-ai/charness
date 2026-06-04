#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
codex_audit = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.codex_session_audit_lib"
)
jsonl_audit = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.codex_session_jsonl_audit"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a compact Codex session efficiency map.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repo root used to resolve repo-local hits")
    parser.add_argument("--home", type=Path, default=Path.home(), help="User home directory holding ~/.codex logs and sessions")
    parser.add_argument("--source", choices=("auto", "tui", "sqlite"), default="auto", help="Aggregate log source for thread-level audit (default: auto)")
    parser.add_argument("--session-id", help="Read the full rollout JSONL whose filename contains this session id, instead of the tail-limited sqlite/tui source")
    parser.add_argument("--session-file", help="Explicit path to a Codex rollout JSONL to audit directly (overrides --session-id)")
    parser.add_argument("--started-at", help="Only include rollout JSONL events at or after this ISO timestamp")
    parser.add_argument("--completed-at", help="Only include rollout JSONL events at or before this ISO timestamp")
    parser.add_argument("--thread-id", action="append", default=[], help="Restrict the aggregate audit to one or more thread ids (repeatable)")
    parser.add_argument("--list-threads", action="store_true", help="List candidate threads in the aggregate source instead of auditing")
    parser.add_argument("--since", help="Only include log lines at or after this ISO timestamp")
    parser.add_argument("--format", choices=("json", "markdown"), default="json", help="Output format (default: json)")
    parser.add_argument("--top", type=int, default=20, help="Cap how many ranked rows to include (default: 20)")
    parser.add_argument("--max-auto-threads", type=int, default=12, help="Cap auto-selected threads when none are named (default: 12)")
    parser.add_argument("--max-command-len", type=int, default=160, help="Truncate command snippets to this length (default: 160)")
    parser.add_argument("--max-tui-lines", type=int, default=5000, help="Tail limit when reading the TUI log source (default: 5000)")
    parser.add_argument("--include-command-snippets", action="store_true", help="Include raw command snippets in the aggregate report")
    return parser.parse_args()


def run_session_jsonl(args: argparse.Namespace) -> int:
    home = args.home.expanduser().resolve()
    path = jsonl_audit.resolve_session_path(home, session_id=args.session_id, session_file=args.session_file)
    if path is None:
        target = args.session_file or args.session_id
        print(f"No Codex rollout JSONL found for {target!r} under {home}/.codex/sessions")
        return 2
    payload = jsonl_audit.audit_session_jsonl(
        path,
        top=args.top,
        started_at=args.started_at,
        completed_at=args.completed_at,
    )
    if args.format == "markdown":
        print(jsonl_audit.render_markdown(payload))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def requested_threads(values: list[str]) -> tuple[str, ...]:
    return tuple(part.strip() for value in values for part in value.split(",") if part.strip())


def main() -> int:
    args = parse_args()
    if args.session_id or args.session_file:
        return run_session_jsonl(args)
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
