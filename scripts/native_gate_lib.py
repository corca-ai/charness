#!/usr/bin/env python3
"""Resolve and execute repograph for authoring-repository quality gates.

This is a GATE-EXECUTION policy layered on top of the product resolver.
``runtime_bootstrap.native_core_path()`` and the
``CHARNESS_ALLOW_DEV_NATIVE_CORE`` semantics are deliberately not modified.
The gate needs an authoring-checkout dev-tree fallback even while the product
resolver correctly reports that no distributed artifact exists yet.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import runtime_bootstrap

Provenance = Literal["override", "managed", "dev-tree"]


@dataclass(frozen=True, slots=True)
class NativeGateBinary:
    path: Path
    provenance: Provenance


class NativeGateError(RuntimeError):
    """A repograph binary cannot be resolved for gate execution."""


def _managed_result(repo_root: Path):
    """Ask the product resolver for a managed result without reusing the override."""
    # native_core_path lazily imports `scripts.native_core_resolution_lib`;
    # route that import through the repo-module loader so the repo root is on
    # sys.path regardless of how this script was invoked.
    runtime_bootstrap.import_repo_module(__file__, "scripts.native_core_resolution_lib")
    override = os.environ.pop("CHARNESS_NATIVE_CORE", None)
    try:
        return runtime_bootstrap.native_core_path(repo_root=repo_root)
    finally:
        if override is not None:
            os.environ["CHARNESS_NATIVE_CORE"] = override


def resolve_native_core(repo_root: str | Path) -> NativeGateBinary:
    """Resolve the binary according to the gate-only D1 resolution order."""
    root = Path(repo_root).expanduser().resolve()
    override = os.environ.get("CHARNESS_NATIVE_CORE", "").strip()
    if override:
        path = Path(override).expanduser().resolve()
        if not path.is_file():
            raise NativeGateError(
                "CHARNESS_NATIVE_CORE points to a missing native core file: "
                f"{path}"
            )
        return NativeGateBinary(path, "override")

    try:
        managed = _managed_result(root)
    except (OSError, RuntimeError, ValueError):
        managed = None
    if (
        managed is not None
        and getattr(managed, "status", None) == "healthy"
        and getattr(managed, "provenance", None) == "managed"
    ):
        path = Path(managed.path)
        if path.is_file():
            return NativeGateBinary(path, "managed")

    crate_root = root / "native" / "repograph"
    binary = crate_root / "target" / "release" / "repograph"
    if (crate_root / "Cargo.toml").is_file():
        if binary.is_file():
            return NativeGateBinary(binary, "dev-tree")
        raise NativeGateError(
            "native gate binary is unavailable: the repograph crate source is "
            f"present at {crate_root}, but the release binary is missing at {binary}. "
            f"Run `cargo build --release` in `{crate_root}`."
        )

    raise NativeGateError(
        "native gate binary is unavailable: this checkout has no native core "
        "and no source to build one; the native artifact is not yet distributed. "
        "Run `charness update` once the native artifact is distributed."
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Resolve and run the repograph binary for a quality gate."
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--probe", action="store_true", help="resolve and report without running")
    parser.add_argument("repograph_command", nargs=argparse.REMAINDER)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if not args.repograph_command:
        _parser().error("a repograph command is required")

    try:
        resolved = resolve_native_core(args.repo_root)
    except NativeGateError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.probe:
        print(f"native core: {resolved.path} (provenance: {resolved.provenance})")
        return 0

    try:
        completed = subprocess.run(
            [str(resolved.path), *args.repograph_command],
            check=False,
        )
    except OSError as exc:
        print(f"native gate could not execute {resolved.path}: {exc}", file=sys.stderr)
        return 1
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
