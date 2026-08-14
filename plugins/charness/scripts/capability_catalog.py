#!/usr/bin/env python3
"""Read and refresh Charness' deterministic capability catalog."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

if str(Path(__file__).resolve().parent.parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.capability_catalog_artifact import persist_catalog, read_only_result
from scripts.capability_catalog_resolver import resolve_skill_path
from scripts.capability_catalog_sources import build_inventory
from scripts.yaml_output import emit_yaml


class CatalogRepoRootError(ValueError):
    """Raised when refresh is asked to mutate an invalid repository root."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        if not repo_root.exists():
            reason = "does not exist"
        elif not repo_root.is_dir():
            reason = "is not a directory"
        else:  # pragma: no cover - defensive; callers validate before raising
            reason = "is invalid"
        super().__init__(f"repo root {repo_root} {reason}")


def _repo_root(value: Path | None) -> Path:
    return (value or Path.cwd()).expanduser().resolve()


def list_catalog(repo_root: Path) -> dict[str, object]:
    return {"inventory": build_inventory(repo_root), "artifacts": read_only_result()}


def summarize_catalog(payload: dict[str, object]) -> dict[str, object]:
    """Project the full inventory into the hidden-capability routing view."""

    inventory = payload["inventory"]
    assert isinstance(inventory, dict)

    def project(items: object, fields: tuple[str, ...]) -> list[dict[str, object]]:
        if not isinstance(items, list):
            return []
        return [
            {field: item[field] for field in fields if field in item}
            for item in items
            if isinstance(item, dict)
        ]

    counted_layers = (
        "public_skills",
        "support_skills",
        "support_capabilities",
        "integrations",
        "trusted_skills",
    )
    return {
        "inventory": {
            "adapter": inventory.get("adapter", {}),
            "counts": {
                layer: len(items) if isinstance((items := inventory.get(layer)), list) else 0
                for layer in counted_layers
            },
            "support_skills": project(
                inventory.get("support_skills"),
                ("id", "summary", "path"),
            ),
            "support_capabilities": project(
                inventory.get("support_capabilities"),
                ("id", "summary", "path", "support_skill_path"),
            ),
            "integrations": project(
                inventory.get("integrations"),
                ("id", "summary", "path", "support_state", "support_skill_path"),
            ),
            "trusted_skills": project(
                inventory.get("trusted_skills"),
                ("id", "summary", "path"),
            ),
        },
        "artifacts": payload.get("artifacts", {}),
    }


def refresh_catalog(repo_root: Path) -> dict[str, object]:
    if not repo_root.exists() or not repo_root.is_dir():
        raise CatalogRepoRootError(repo_root)
    inventory = build_inventory(repo_root)
    return {"inventory": inventory, "artifacts": persist_catalog(repo_root, inventory)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect deterministic installed capability inventory and stale skill paths."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_root(command: argparse.ArgumentParser) -> None:
        command.add_argument("--repo-root", type=Path, required=True)

    list_parser = subparsers.add_parser(
        "list", help="Read the installed capability inventory without writing artifacts."
    )
    add_root(list_parser)
    list_parser.add_argument(
        "--summary",
        action="store_true",
        help="Project the inventory down to the hidden support and integration routing view.",
    )
    refresh_parser = subparsers.add_parser(
        "refresh", help="Write the canonical capability catalog current pointers."
    )
    add_root(refresh_parser)
    resolve_parser = subparsers.add_parser(
        "resolve-skill-path", help="Resolve a stale host-reported skill path after cache rotation."
    )
    resolve_parser.add_argument("--repo-root", type=Path, required=True)
    resolve_parser.add_argument("--skill-id", required=True)
    resolve_parser.add_argument("--reported-path", type=Path, required=True)
    resolve_parser.add_argument("--home", type=Path, default=Path.home())
    resolve_parser.add_argument(
        "--codex-home",
        type=Path,
        default=Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")),
    )
    resolve_parser.add_argument("--marketplace", default="local")
    resolve_parser.add_argument("--plugin", default="charness")
    args = parser.parse_args(argv)
    try:
        if args.command == "list":
            payload = list_catalog(_repo_root(args.repo_root))
            if args.summary:
                payload = summarize_catalog(payload)
        elif args.command == "refresh":
            payload = refresh_catalog(_repo_root(args.repo_root))
        else:
            payload = resolve_skill_path(
                skill_id=args.skill_id,
                repo_root=_repo_root(args.repo_root),
                home=args.home.expanduser().resolve(),
                codex_home=args.codex_home.expanduser().resolve(),
                reported_path=args.reported_path.expanduser(),
                marketplace=args.marketplace,
                plugin=args.plugin,
            )
    except CatalogRepoRootError as exc:
        # The message the dropped stderr line carried lives in `error`; emitting it
        # on stdout as well would print the same failure twice.
        emit_yaml({"error": str(exc), "repo_root": str(exc.repo_root)})
        return 2
    emit_yaml(payload)
    if args.command == "resolve-skill-path" and payload.get("resolved_path") is None:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
