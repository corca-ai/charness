#!/usr/bin/env python3

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any


def support_state_for_manifest(manifest: dict[str, Any], *, sync_strategy: str | None = None) -> str:
    if manifest.get("kind") == "support_runtime":
        return "native-support"
    support = manifest.get("support_skill_source")
    if not support:
        return "integration-only"
    strategy = sync_strategy or support["sync_strategy"]
    if strategy == "generated_wrapper" or support["source_type"] == "local_wrapper":
        return "wrapped-upstream"
    if strategy == "copy":
        return "forked-local"
    return "upstream-consumed"


def inspect_support_sync(repo_root: Path, previous_lock: dict[str, Any] | None) -> dict[str, Any]:
    support = previous_lock.get("support") if previous_lock else None
    if not support:
        return {
            "status": "not-tracked",
            "expected_paths": [],
            "missing_paths": [],
        }
    expected_paths = support.get("materialized_paths", [])
    missing_paths = [path for path in expected_paths if not (repo_root / path).exists()]
    return {
        "status": "ok" if not missing_paths else "missing",
        "expected_paths": expected_paths,
        "missing_paths": missing_paths,
    }


def parse_upstream_checkout(value: str) -> tuple[str, Path]:
    upstream_repo, separator, raw_path = value.partition("=")
    if not separator or not upstream_repo.strip() or not raw_path.strip():
        raise ValueError("`--upstream-checkout` must look like `owner/name=/abs/path/to/checkout`")
    checkout_root = Path(raw_path).expanduser().resolve()
    if not checkout_root.is_dir():
        raise ValueError(f"`--upstream-checkout` path does not exist: `{checkout_root}`")
    return upstream_repo.strip(), checkout_root


def resolve_support_source_path(
    repo_root: Path,
    manifest: dict[str, Any],
    *,
    upstream_checkouts: dict[str, Path],
) -> Path:
    support = manifest.get("support_skill_source")
    if not support:
        raise ValueError(f"{manifest['tool_id']}: manifest has no support_skill_source")
    relative_source_path = Path(support["path"])
    source_type = support["source_type"]
    if source_type == "local_wrapper":
        source_path = repo_root / relative_source_path
    elif source_type == "upstream_repo":
        checkout_root = upstream_checkouts.get(manifest["upstream_repo"])
        if checkout_root is None:
            raise ValueError(
                f"{manifest['tool_id']}: sync strategy `{support['sync_strategy']}` requires "
                f"`--upstream-checkout {manifest['upstream_repo']}=/abs/path/to/checkout`"
            )
        source_path = checkout_root / relative_source_path
    else:
        raise ValueError(f"{manifest['tool_id']}: unsupported source_type `{source_type}`")
    if not source_path.exists():
        raise ValueError(
            f"{manifest['tool_id']}: support source `{source_path}` does not exist "
            f"for `{manifest['upstream_repo']}`"
        )
    return source_path


def clear_materialized_target(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    if path.is_dir():
        shutil.rmtree(path)


def effective_sync_strategy(manifest: dict[str, Any], *, local_dev_symlink: bool) -> str:
    support = manifest.get("support_skill_source")
    if not support:
        return "none"
    declared = support["sync_strategy"]
    if local_dev_symlink and declared == "copy":
        return "symlink"
    return declared


def materialize_copy(source_path: Path, dest_root: Path, repo_root: Path) -> list[str]:
    if source_path.is_dir():
        clear_materialized_target(dest_root)
        dest_root.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_path, dest_root)
        return [str(dest_root.relative_to(repo_root))]

    dest_path = dest_root / source_path.name
    clear_materialized_target(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, dest_path)
    return [str(dest_path.relative_to(repo_root))]


def materialize_symlink(source_path: Path, dest_root: Path, repo_root: Path) -> list[str]:
    if source_path.is_dir():
        clear_materialized_target(dest_root)
        dest_root.parent.mkdir(parents=True, exist_ok=True)
        dest_root.symlink_to(source_path, target_is_directory=True)
        return [str(dest_root.relative_to(repo_root))]

    dest_path = dest_root / source_path.name
    clear_materialized_target(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.symlink_to(source_path)
    return [str(dest_path.relative_to(repo_root))]
