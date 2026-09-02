#!/usr/bin/env python3
"""Resolve and execute repograph for quality gates.

The binary is BUILT from the ``native/repograph`` crate that ships in the
charness checkout and installed by ``charness tool install repograph``
(``integrations/tools/repograph.json``). Nothing is downloaded: building from
the checkout that runs the gate makes binary/source skew structurally
impossible instead of merely detectable, which is why the prebuilt-artifact
distribution layer this module used to consult was retired.

Every action this module takes on the operator's behalf -- picking one of three
possible binaries, or spending minutes on a build -- is announced on stderr
before its effect, never inferred from it.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

try:
    from scripts.core.subprocess_guard import run_monitored_phase
except ModuleNotFoundError:  # executed directly from scripts/
    from scripts.core.subprocess_guard import run_monitored_phase

Provenance = Literal["override", "dev-tree", "installed"]

CRATE_RELATIVE_PATH = Path("native") / "repograph"
INSTALL_HINT = "Install it with `charness tool install repograph`."
RUSTUP_HINT = "Install Rust from https://rustup.rs."

# Files whose mtime decides whether the dev-tree binary still represents the
# crate. This is the whole of the staleness vocabulary now: source that is
# present is compared against the binary built from it. There is no version
# table, no tuple key space, and no digest-bound declaration to drift from.
_SOURCE_GLOBS = ("src/**/*.rs", "Cargo.toml", "Cargo.lock", "rust-toolchain.toml")


@dataclass(frozen=True, slots=True)
class NativeGateBinary:
    path: Path
    provenance: Provenance


class NativeGateError(RuntimeError):
    """A repograph binary cannot be resolved for gate execution."""


def announce(message: str) -> None:
    """State an action before taking it.

    stderr, not stdout: ``export-safe``, ``plugin-refs``, and ``classify`` emit
    JSON on stdout that the calling gates parse.
    """
    print(f"native gate: {message}", file=sys.stderr, flush=True)


def cargo_bin_dir() -> Path:
    cargo_home = os.environ.get("CARGO_HOME", "").strip()
    root = Path(cargo_home).expanduser() if cargo_home else Path.home() / ".cargo"
    return root / "bin"


def installed_binary() -> Path | None:
    """Find an installed repograph the same way its manifest's doctor does."""
    found = shutil.which("repograph")
    if found:
        return Path(found)
    # `integrations/tools/repograph.json` prepends this exact directory to PATH
    # in its detect and healthcheck commands, because `cargo install` writes
    # here and the invoking process's PATH may predate that write. Both sides
    # look in the same two places so `charness tool doctor repograph` and this
    # resolver can never disagree about whether the binary is reachable.
    candidate = cargo_bin_dir() / "repograph"
    return candidate if candidate.is_file() else None


def _newest_source_mtime(crate_root: Path) -> tuple[float, Path | None]:
    newest = 0.0
    newest_path: Path | None = None
    for pattern in _SOURCE_GLOBS:
        for path in crate_root.glob(pattern):
            try:
                mtime = path.stat().st_mtime
            except OSError:
                continue
            if mtime > newest:
                newest, newest_path = mtime, path
    return newest, newest_path


def dev_tree_staleness(crate_root: Path, binary: Path) -> Path | None:
    """Return the crate file that outdates ``binary``, or ``None`` if fresh."""
    try:
        binary_mtime = binary.stat().st_mtime
    except OSError:
        return crate_root / "Cargo.toml"
    newest, newest_path = _newest_source_mtime(crate_root)
    return newest_path if newest > binary_mtime else None


def build_dev_tree(crate_root: Path, binary: Path, *, reason: str) -> None:
    """Build the crate in place, saying what is happening before it happens."""
    if shutil.which("cargo") is None:
        raise NativeGateError(
            f"native gate binary is unavailable: {reason}, and `cargo` is not on "
            f"PATH to build it from {crate_root}. {RUSTUP_HINT} {INSTALL_HINT}"
        )
    announce(reason)
    announce(f"building from source: `cargo build --release --locked` in {crate_root}")
    announce("this is a build cost paid once per crate change; later runs reuse the binary")
    started = time.monotonic()
    # Both cargo streams go straight to file descriptor 2 so a multi-minute
    # build is visible while it runs, and so cargo's progress output can never
    # land on the JSON stdout a calling gate parses. `cwd` is the crate root
    # because rustup selects the toolchain from the working directory, and the
    # crate pins one in rust-toolchain.toml.
    completed = run_monitored_phase(
        ["cargo", "build", "--release", "--locked"],
        cwd=crate_root,
        phase="native-build",
        timeout_seconds=None,
        capture=False,
    )
    elapsed = time.monotonic() - started
    if completed.returncode != 0:
        # Deliberately NOT a fallthrough to an installed binary. Substituting a
        # binary built from other source for the source that just failed to
        # build is the silent swap this announcement exists to prevent.
        raise NativeGateError(
            f"native gate binary is unavailable: `cargo build --release --locked` "
            f"failed in {crate_root} with exit code {completed.returncode} after "
            f"{elapsed:.1f}s. Fix the crate build; the gate will not fall back to "
            "an installed binary built from different source."
        )
    if not binary.is_file():
        raise NativeGateError(
            f"native gate binary is unavailable: cargo reported success in "
            f"{crate_root} but produced no binary at {binary}."
        )
    announce(f"built {binary} in {elapsed:.1f}s")


def resolve_native_core(repo_root: str | Path) -> NativeGateBinary:
    """Resolve the binary: override, then dev-tree build, then installed.

    Dev-tree precedes the installed binary so that editing the crate in the
    charness authoring checkout is reflected in the gate verdict. The inverse
    order would let a binary built from other source render a verdict on the
    source you just changed.
    """
    root = Path(repo_root).expanduser().resolve()

    override = os.environ.get("CHARNESS_NATIVE_CORE", "").strip()
    if override:
        path = Path(override).expanduser().resolve()
        if not path.is_file():
            # An explicit override that silently degrades is worse than none.
            raise NativeGateError(
                f"CHARNESS_NATIVE_CORE points to a missing native core file: {path}"
            )
        return NativeGateBinary(path, "override")

    crate_root = root / CRATE_RELATIVE_PATH
    if (crate_root / "Cargo.toml").is_file():
        binary = crate_root / "target" / "release" / "repograph"
        if not binary.is_file():
            build_dev_tree(crate_root, binary, reason=f"repograph is not built at {binary}")
        else:
            stale_source = dev_tree_staleness(crate_root, binary)
            if stale_source is not None:
                build_dev_tree(
                    crate_root,
                    binary,
                    reason=(
                        f"{binary} is older than the crate source "
                        f"({stale_source.relative_to(crate_root)} changed)"
                    ),
                )
        return NativeGateBinary(binary, "dev-tree")

    installed = installed_binary()
    if installed is not None:
        return NativeGateBinary(installed, "installed")

    raise NativeGateError(
        "native gate binary is unavailable: `repograph` is not installed, and "
        f"this repo has no {CRATE_RELATIVE_PATH.as_posix()} crate to build one "
        f"from. {INSTALL_HINT}"
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

    # Always, not only under --probe: resolution now picks between three
    # sources whose verdicts can differ, so which one answered is part of the
    # gate's result rather than a debugging aid.
    announce(f"repograph {resolved.path} (provenance: {resolved.provenance})")
    if args.probe:
        return 0

    try:
        completed = run_monitored_phase(
            [str(resolved.path), *args.repograph_command],
            cwd=args.repo_root.resolve(),
            phase="native-gate",
            timeout_seconds=None,
            capture=False,
        )
    except OSError as exc:
        print(f"native gate could not execute {resolved.path}: {exc}", file=sys.stderr)
        return 1
    return completed.returncode


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
