"""Catalog commands."""

from __future__ import annotations

import argparse


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.cli.bootstrap_state import (  # noqa: E402
    emit_yaml,
)
from scripts.cli.process import (  # noqa: E402
    _load_catalog_lib,
)


def cmd_catalog_list(args: argparse.Namespace) -> int:
    catalog = _load_catalog_lib()
    try:
        payload = catalog.list_catalog(args.repo_root.resolve(), require_adoption=True)
    except catalog.CatalogRepoRootError as exc:
        emit_yaml({"error": str(exc), "repo_root": str(exc.repo_root)})
        return 2
    if args.summary:
        payload = catalog.summarize_catalog(payload)
    emit_yaml(payload)
    return 1 if catalog.catalog_is_blocked(payload) else 0


def cmd_catalog_refresh(args: argparse.Namespace) -> int:
    catalog = _load_catalog_lib()
    try:
        payload = catalog.refresh_catalog(args.repo_root.resolve())
    except catalog.CatalogRepoRootError as exc:
        error = {"error": str(exc), "repo_root": str(exc.repo_root)}
        emit_yaml(error)
        return 2
    emit_yaml(payload)
    return 0


def cmd_catalog_resolve_skill_path(args: argparse.Namespace) -> int:
    catalog = _load_catalog_lib()
    payload = catalog.resolve_skill_path(
        skill_id=args.skill_id,
        repo_root=args.repo_root.resolve(),
        home=args.home.expanduser().resolve(),
        codex_home=args.codex_home.expanduser().resolve(),
        reported_path=args.reported_path.expanduser(),
        marketplace=args.marketplace,
        plugin=args.plugin,
    )
    emit_yaml(payload)
    return 0 if payload.get("resolved_path") else 1
