#!/usr/bin/env python3
"""Read and refresh Charness' deterministic capability catalog."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

def _script_root_from_file() -> Path:
    script_path = Path(__file__).resolve()
    for parent in script_path.parents:
        if (parent / "scripts" / "adapter_lib.py").is_file():
            return parent
        if (parent / ".codex-plugin" / "plugin.json").is_file():
            return parent
    return script_path.parent.parent


_script_root = _script_root_from_file()
if str(_script_root) not in sys.path:
    sys.path.insert(0, str(_script_root))

from scripts import check_consumer_validator_catalog  # noqa: E402
from scripts.adapters.capability_catalog_artifact import (  # noqa: E402
    persist_catalog,
    read_only_result,
)
from scripts.adapters.capability_catalog_resolver import resolve_skill_path  # noqa: E402
from scripts.adapters.capability_catalog_sources import build_inventory  # noqa: E402
from scripts.yaml_output import emit_yaml  # noqa: E402


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


def list_catalog(repo_root: Path, *, require_adoption: bool = False) -> dict[str, object]:
    root = _repo_root(repo_root)
    if not root.exists() or not root.is_dir():
        raise CatalogRepoRootError(root)
    return {
        "inventory": build_inventory(root),
        "consumer_validator_catalog": _consumer_validator_catalog(
            root, require_adoption=require_adoption
        ),
        "artifacts": read_only_result(),
    }


def catalog_is_blocked(payload: dict[str, object]) -> bool:
    value = payload.get("consumer_validator_catalog")
    return isinstance(value, dict) and value.get("status") == "blocked"


def _consumer_validator_catalog(
    repo_root: Path, *, require_adoption: bool = False
) -> dict[str, object]:
    """Read the packaged validator contract owned by this Charness checkout."""

    owner_root = _script_root_from_file()
    if (owner_root / "plugins" / "charness").is_dir():
        package_root = owner_root / "plugins" / "charness"
        catalog_path = owner_root / check_consumer_validator_catalog.DEFAULT_CATALOG_REL
    else:
        package_root = owner_root
        catalog_path = owner_root / "skills" / "quality" / "references" / "consumer-validator-catalog.yaml"
    try:
        return check_consumer_validator_catalog.validate_catalog(
            owner_root,
            catalog_path=catalog_path,
            package_root=package_root,
            adoption_path=repo_root / check_consumer_validator_catalog.DEFAULT_ADOPTION_REL,
            require_adoption=require_adoption,
        )
    except check_consumer_validator_catalog.CatalogError as exc:
        return {
            "status": "blocked",
            "catalog_path": str(catalog_path),
            "error": str(exc),
        }


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
        "consumer_validator_catalog": payload.get("consumer_validator_catalog", {}),
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
            payload = list_catalog(_repo_root(args.repo_root), require_adoption=True)
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
    if args.command == "resolve-skill-path" and payload.get(
        "admission_status", "admitted" if payload.get("resolved_path") else None
    ) != "admitted":
        return 1
    if args.command == "list" and catalog_is_blocked(payload):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
