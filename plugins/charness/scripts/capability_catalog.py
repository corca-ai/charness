#!/usr/bin/env python3
"""Read and refresh Charness' deterministic capability catalog."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

if str(Path(__file__).resolve().parent.parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.capability_catalog_artifact import persist_catalog, read_only_result
from scripts.capability_catalog_resolver import resolve_skill_path
from scripts.capability_catalog_sources import build_inventory


def _repo_root(value: Path | None) -> Path:
    return (value or Path.cwd()).expanduser().resolve()


def list_catalog(repo_root: Path) -> dict[str, object]:
    return {"inventory": build_inventory(repo_root), "artifacts": read_only_result()}


def refresh_catalog(repo_root: Path) -> dict[str, object]:
    inventory = build_inventory(repo_root)
    return {"inventory": inventory, "artifacts": persist_catalog(repo_root, inventory)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect deterministic installed capability inventory and stale skill paths.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    def add_root(command: argparse.ArgumentParser) -> None:
        command.add_argument("--repo-root", type=Path, required=True)
        command.add_argument("--json", action="store_true")
    list_parser = subparsers.add_parser("list", help="Read the installed capability inventory without writing artifacts.")
    add_root(list_parser)
    refresh_parser = subparsers.add_parser("refresh", help="Write the canonical capability catalog current pointers.")
    add_root(refresh_parser)
    resolve_parser = subparsers.add_parser("resolve-skill-path", help="Resolve a stale host-reported skill path after cache rotation.")
    resolve_parser.add_argument("--repo-root", type=Path, required=True)
    resolve_parser.add_argument("--skill-id", required=True)
    resolve_parser.add_argument("--reported-path", type=Path, required=True)
    resolve_parser.add_argument("--home", type=Path, default=Path.home())
    resolve_parser.add_argument("--codex-home", type=Path, default=Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")))
    resolve_parser.add_argument("--marketplace", default="local")
    resolve_parser.add_argument("--plugin", default="charness")
    resolve_parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "list":
        payload = list_catalog(_repo_root(args.repo_root))
    elif args.command == "refresh":
        payload = refresh_catalog(_repo_root(args.repo_root))
    else:
        payload = resolve_skill_path(skill_id=args.skill_id, repo_root=_repo_root(args.repo_root), home=args.home.expanduser().resolve(), codex_home=args.codex_home.expanduser().resolve(), reported_path=args.reported_path.expanduser(), marketplace=args.marketplace, plugin=args.plugin)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.command == "resolve-skill-path" and payload.get("resolved_path") is None:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
