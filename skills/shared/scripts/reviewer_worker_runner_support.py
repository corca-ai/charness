"""Path, adapter, and argument helpers for the reviewer worker runner."""

from __future__ import annotations

import argparse
import hashlib
import os
import runpy
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import yaml


def package_root() -> Path:
    """Find the source or installed plugin root from this module's location."""
    for candidate in Path(__file__).resolve().parents:
        has_schema = (
            candidate / "shared/references/bounded-review-result.schema.json"
        ).is_file() or (
            candidate / "skills/shared/references/bounded-review-result.schema.json"
        ).is_file()
        if has_schema and (
            (candidate / "skills/public/critique/scripts/resolve_adapter.py").is_file()
            or (candidate / "skills/critique/scripts/resolve_adapter.py").is_file()
        ):
            return candidate
    raise RuntimeError("cannot locate Charness package root for reviewer runner")


ROOT = package_root()
WORKER = Path(__file__).resolve().with_name("reviewer_worker.py")
DEFAULT_SCHEMA = next(
    path
    for path in (
        ROOT / "shared/references/bounded-review-result.schema.json",
        ROOT / "skills/shared/references/bounded-review-result.schema.json",
    )
    if path.is_file()
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _runtime():
    bootstrap = next(
        (
            ancestor / "scripts" / "runtime_bootstrap.py"
            for ancestor in Path(__file__).resolve().parents
            if (ancestor / "scripts" / "runtime_bootstrap.py").is_file()
        ),
        None,
    )
    if bootstrap is None:
        raise ImportError("runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


def repo_path(repo_root: Path, value: Path) -> Path:
    """Resolve runner paths against the explicit repo root, never launch cwd."""
    return (value if value.is_absolute() else repo_root / value).resolve()


def atomic_write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".pending", dir=path.parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(yaml.safe_dump(payload, sort_keys=False))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise


def adapter(repo_root: Path) -> dict[str, Any]:
    adapter_scripts = (
        ROOT / "skills/public/critique/scripts/resolve_adapter.py",
        ROOT / "skills/critique/scripts/resolve_adapter.py",
    )
    resolver = next((path for path in adapter_scripts if path.is_file()), None)
    if resolver is None:
        raise ValueError("cannot locate critique adapter resolver in the installed package")
    resolver_module = _runtime().load_path_module("charness_reviewer_resolve_adapter", resolver)
    payload = resolver_module.load_adapter(repo_root) or {}
    if not isinstance(payload, dict) or payload.get("valid") is not True:
        raise ValueError("critique adapter is invalid")
    return payload


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Run one canonical file-backed review attempt.")
    result.add_argument("--repo-root", type=Path, default=ROOT)
    result.add_argument("--prompt-file", type=Path, required=True)
    result.add_argument("--capability-file", type=Path, required=True)
    result.add_argument("--scope", required=True)
    result.add_argument("--packet-identity", required=True)
    result.add_argument("--reviewed-input-identity", required=True)
    result.add_argument("--attempt-id", required=True)
    result.add_argument("--parent-receipt-identity", required=True)
    result.add_argument("--boundary-fingerprint")
    result.add_argument(
        "--boundary-mode", choices=("read-only-worker", "shared-tree-fingerprint"), default=None
    )
    result.add_argument("--ledger-file", type=Path, required=True)
    result.add_argument("--output-file", type=Path, required=True)
    result.add_argument("--receipt-file", type=Path, required=True)
    result.add_argument("--report-file", type=Path, required=True)
    result.add_argument("--schema-file", type=Path, default=DEFAULT_SCHEMA)
    result.add_argument("--stdout-file", type=Path)
    result.add_argument("--stderr-file", type=Path)
    result.add_argument("--backend", choices=("codex_exec", "claude_p"))
    result.add_argument("--execution-mode", choices=("file-backed-worker", "typed-subagent"))
    result.add_argument("--timeout-seconds", type=float)
    result.add_argument("--run-id")
    return result


def select_runner(args: argparse.Namespace, repo_root: Path) -> tuple[str, str | None, float]:
    adapter_data = adapter(repo_root).get("data") or {}
    runner = adapter_data.get("reviewer_runner") or {}
    configured_mode = runner.get("mode", "file-backed-worker")
    if args.execution_mode is not None and args.execution_mode != configured_mode:
        raise ValueError(
            f"adapter reviewer_runner.mode={configured_mode!r} is authoritative; "
            f"caller requested {args.execution_mode!r}"
        )
    configured_backend = runner.get("backend")
    if configured_backend == "host-defaulted":
        backend = args.backend
    else:
        if args.backend is not None and args.backend != configured_backend:
            raise ValueError(
                f"adapter reviewer_runner.backend={configured_backend!r} is authoritative; "
                f"caller requested {args.backend!r}"
            )
        backend = configured_backend
    configured_timeout = runner.get("timeout_seconds")
    if (
        configured_timeout is not None
        and args.timeout_seconds is not None
        and args.timeout_seconds != configured_timeout
    ):
        raise ValueError(
            f"adapter reviewer_runner.timeout_seconds={configured_timeout!r} is authoritative; "
            f"caller requested {args.timeout_seconds!r}"
        )
    timeout = (
        configured_timeout
        if configured_timeout is not None
        else (args.timeout_seconds if args.timeout_seconds is not None else 900)
    )
    return configured_mode, backend, timeout
