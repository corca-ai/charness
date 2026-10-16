"""Path, adapter, and argument helpers for the reviewer worker runner."""

from __future__ import annotations

import argparse
import hashlib
import json
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


def runtime_scratch_module():
    """Load the package-owned runtime receipt/path contract."""
    return _runtime().import_repo_module(__file__, "scripts.runtime_scratch")


def repo_path(repo_root: Path, value: Path) -> Path:
    """Resolve runner paths against the explicit repo root, never launch cwd."""
    return (value if value.is_absolute() else repo_root / value).resolve()


def validate_owned_run_reference(
    repo_root: Path,
    *,
    owner_run_id: str | None,
    owner_receipt_file: Path | None,
    attempt_id: str,
    scope: str,
    packet_identity: str,
    reviewed_input_identity: str,
    parent_receipt_identity: str,
    backend: str,
    boundary_mode: str,
    boundary_fingerprint: str | None,
    runtime_environment: dict[str, str],
) -> tuple[Any | None, dict[str, Any] | None]:
    """Bind a runner to the live owner receipt and canonical plan, without locking it."""
    if bool(owner_run_id) != bool(owner_receipt_file):
        raise ValueError("owner-run-id and owner-receipt-file must be supplied together")
    if owner_run_id is None or owner_receipt_file is None:
        return None, None
    try:
        scratch = runtime_scratch_module()
        probe = scratch.OwnedScratch(
            repo_root,
            "critique-review",
            run_id=owner_run_id,
            runtime_root_path=scratch.runtime_root(repo_root, runtime_environment),
        )
        if probe.receipt_path.is_symlink() or not probe.receipt_path.is_file():
            raise ValueError("owned scratch receipt is missing or unsafe")
        plan_path = probe.path / "run-plan.json"
        if plan_path.is_symlink() or not plan_path.is_file():
            raise ValueError("owned scratch run plan is missing or unsafe")
        try:
            owner_plan = json.loads(plan_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"owned scratch run plan is unreadable: {exc}") from exc
        if not isinstance(owner_plan, dict):
            raise ValueError("owned scratch run plan must be a mapping")
        owner, _ = scratch.validate_owned_scratch_reference(
            repo_root,
            owner_receipt_file,
            producer="critique-review",
            run_id=owner_run_id,
            expected_fields={
                "attempt_id": attempt_id,
                "plan_sha256": sha256(plan_path),
                "packet_identity": packet_identity,
                "reviewed_input_identity": reviewed_input_identity,
                "parent_receipt_identity": parent_receipt_identity,
            },
            runtime_environment=runtime_environment,
        )
    except (ImportError, RuntimeError) as exc:
        raise ValueError(f"owned scratch reference is invalid: {exc}") from exc
    expected_plan_fields = (
        ("kind", "charness.review_run_plan.v1"),
        ("attempt_id", attempt_id),
        ("owner_run_id", owner_run_id),
        ("scope", scope),
        ("packet_sha256", packet_identity),
        ("reviewed_input_identity_sha256", reviewed_input_identity),
        ("parent_receipt_identity", parent_receipt_identity),
        ("backend", backend),
        ("boundary_mode", boundary_mode),
        ("boundary_fingerprint", boundary_fingerprint),
    )
    for field, expected in expected_plan_fields:
        if owner_plan.get(field) != expected:
            raise ValueError(f"owned scratch run plan {field} does not match the runner request")
    return owner, owner_plan


def resolve_runner_path(
    repo_root: Path,
    value: Path,
    *,
    label: str,
    owner: Any | None = None,
) -> Path:
    """Resolve a repo path or a path inside the exact, already-verified owner."""
    raw = value.expanduser()
    if owner is not None and raw.is_absolute():
        lexical = Path(os.path.abspath(raw))
        try:
            owner_relative = lexical.relative_to(owner.path)
        except ValueError:
            owner_relative = None
        if owner_relative is not None:
            current = owner.path
            for part in owner_relative.parts:
                current = current / part
                if current.is_symlink():
                    raise ValueError(f"runner {label} crosses an owned scratch symlink: {current}")
            resolved = raw.resolve()
            try:
                resolved.relative_to(owner.path)
            except ValueError as exc:
                raise ValueError(
                    f"runner {label} resolves outside the exact owned scratch root: {resolved}"
                ) from exc
            return resolved
    resolved = repo_path(repo_root, raw)
    try:
        resolved.relative_to(repo_root)
        return resolved
    except ValueError as exc:
        if owner is None or not raw.is_absolute():
            raise ValueError(
                f"runner path resolves outside --repo-root without owned scratch proof: {resolved}"
            ) from exc
        raise ValueError(f"runner {label} is outside the exact owned scratch root: {resolved}") from exc


def require_distinct_runner_paths(paths: tuple[Path, ...]) -> None:
    """Refuse input/output aliasing before any runner artifact is written."""
    if len(set(paths)) != len(paths):
        raise ValueError("runner input and output paths must resolve to distinct files")


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
    result.add_argument(
        "--reviewer-tier", choices=("high-leverage", "medium", "standard")
    )
    result.add_argument(
        "--expected-target",
        action="append",
        default=None,
        help=(
            "Opaque admitted target the result must observe; repeat for bundled targets. "
            "Declaring the set opts the attempt into the coverage floor: a schema-valid "
            "result that silently drops a target fails as ReviewerCoverageError instead "
            "of passing on shape alone. The runner never embeds item names beyond "
            "this declaration; the contract only enforces set coverage."
        ),
    )
    result.add_argument("--execution-mode", choices=("file-backed-worker", "typed-subagent"))
    result.add_argument("--timeout-seconds", type=float)
    result.add_argument("--run-id")
    result.add_argument("--owner-run-id")
    result.add_argument("--owner-receipt-file", type=Path)
    return result


def select_runner(
    args: argparse.Namespace, repo_root: Path
) -> tuple[str, str | None, float, dict[str, Any]]:
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
    tier = getattr(args, "reviewer_tier", None)
    tier_fields: dict[str, Any] = {}
    if tier is not None:
        tiers = adapter_data.get("reviewer_tiers") or {}
        if not isinstance(tiers, dict):
            raise ValueError("reviewer_tiers must be a mapping")
        tier_fields = tiers.get(tier) or {}
        if not isinstance(tier_fields, dict):
            raise ValueError(f"reviewer_tiers.{tier} must be a mapping")
    model = tier_fields.get("model")
    effort = tier_fields.get("reasoning_effort")
    for name, value in (("model", model), ("reasoning_effort", effort)):
        if value is not None and (not isinstance(value, str) or not value.strip()):
            raise ValueError(f"reviewer_tiers.{tier}.{name} must be a non-empty string")
    return configured_mode, backend, timeout, {
        "tier": tier,
        "model": model,
        "reasoning_effort": effort,
        "unsupported_fields": {
            name: tier_fields[name]
            for name in ("service_tier", "fork_turns")
            if name in tier_fields
        },
    }


def reviewer_worker_arguments(
    *,
    tier: str | None,
    model: str | None,
    reasoning_effort: str | None,
    unsupported_fields: dict[str, Any],
) -> list[str]:
    """Build only the adapter-resolved reviewer-specific worker arguments."""
    arguments: list[str] = []
    if tier is not None:
        arguments.extend(["--reviewer-tier", tier])
    if model is not None:
        arguments.extend(["--reviewer-model", model])
    if reasoning_effort is not None:
        arguments.extend(["--reviewer-reasoning-effort", reasoning_effort])
    for name, value in unsupported_fields.items():
        arguments.extend(["--unsupported-reviewer-field", f"{name}={value}"])
    return arguments
