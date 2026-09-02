#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
from collections.abc import Callable
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.adapter_lib import (  # noqa: E402
    ADAPTER_RESULT_STATES,
    load_yaml_file_report,
    write_adapter_scaffold,
)
from scripts.adapters.adapter_yaml_render_lib import render_yaml_mapping  # noqa: E402

SCHEMA_VERSION = "charness.adapter-bootstrap/v1"
SUPPORTED_ADAPTER_VERSION = 1


def base_adapter_items(
    repo_name: str,
    output_dir: str,
    *,
    preset_id: str = "portable-defaults",
) -> list[tuple[str, object]]:
    return [
        ("version", 1),
        ("repo", repo_name),
        ("language", "en"),
        ("output_dir", output_dir),
        ("preset_id", preset_id),
        ("customized_from", preset_id),
    ]


def _sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _target_path(repo_root: Path, output: Path) -> Path:
    """Resolve a bootstrap target without allowing a write outside the repo."""
    candidate = output if output.is_absolute() else repo_root / output
    if candidate.is_symlink():
        raise ValueError(f"adapter target must not be a symlink: {candidate}")
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError(f"adapter target must stay inside --repo-root: {output}") from exc
    if resolved == repo_root:
        raise ValueError("adapter target must be a file below --repo-root")
    return resolved


def _structural_state(path: Path, rendered: str) -> tuple[str, str | None]:
    """Classify an existing adapter before a skill-specific resolver is consulted.

    The shared bootstrap can establish readability and version. Skill-specific
    semantics remain with the resolver callback; it must never be guessed here.
    An exact generated file is valid even when no callback exists, which makes
    repeated first-use bootstrap idempotent for the simple skills.
    """
    if path.is_dir():
        return "invalid", "adapter target is a directory, not a regular file"
    try:
        raw, uninterpreted = load_yaml_file_report(path)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        return "unestablished", f"adapter could not be read: {exc}"
    if not isinstance(raw, dict):
        return "invalid", "adapter document is not a mapping"
    if uninterpreted:
        return "unestablished", "adapter contains lines the shared reader could not interpret"
    version = raw.get("version")
    if version is not None and (type(version) is not int or version != SUPPORTED_ADAPTER_VERSION):
        return "invalid", f"adapter version must be {SUPPORTED_ADAPTER_VERSION}"
    try:
        if path.read_text(encoding="utf-8") == rendered:
            return "valid", "generated adapter already matches"
    except (OSError, UnicodeDecodeError) as exc:
        return "unestablished", f"adapter bytes could not be compared: {exc}"
    return "valid", "adapter is readable; skill-specific resolver remains authoritative"


def resolve_existing_adapter_state(path: Path, load_adapter: Callable[[Path], dict[str, Any]]) -> str:
    """Resolve the shared first-use state for an existing target via its public resolver."""
    repo_root = path.parent.parent
    payload = load_adapter(repo_root)
    state = payload.get("state")
    if state not in ADAPTER_RESULT_STATES or state == "absent":
        return "unestablished"
    if state == "configured" and payload.get("path") != str(path):
        return "unestablished"
    return state


def _emit_receipt(
    *,
    repo_root: Path,
    target: Path,
    skill_id: str,
    state: str,
    status: str,
    ok: bool,
    dry_run: bool,
    force: bool,
    mutation_invoked: bool,
    reason: str | None,
    next_action: str | None,
    before_sha256: str | None,
    generated_sha256: str,
) -> None:
    """Emit one machine-readable receipt for every bootstrap outcome."""
    try:
        relative_path = target.relative_to(repo_root).as_posix()
    except ValueError:
        relative_path = None
    items: list[tuple[str, Any]] = [
        ("kind", SCHEMA_VERSION),
        ("skill_id", skill_id),
        ("path", str(target)),
        ("relative_path", relative_path),
        ("state", state),
        ("status", status),
        ("ok", ok),
        ("dry_run", dry_run),
        ("force", force),
        ("mutation_invoked", mutation_invoked),
        ("before_sha256", before_sha256),
        ("generated_sha256", generated_sha256),
        ("reason", reason),
        ("next_action", next_action),
    ]
    print(render_yaml_mapping(items), end="")


def run_init_adapter(
    *,
    default_output: Path,
    build_items: Callable[[str, argparse.Namespace], list[tuple[str, object]]],
    add_arguments: Callable[[argparse.ArgumentParser], None] | None = None,
    existing_adapter_is_valid: Callable[[Path], bool] | None = None,
    existing_adapter_state: Callable[[Path], str] | None = None,
    render_contents: Callable[[Path, argparse.Namespace], str] | None = None,
) -> Path:
    parser = argparse.ArgumentParser(description="Initialize one repository-local skill adapter")
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=default_output)
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report the bootstrap decision without writing the adapter",
    )
    if add_arguments is not None:
        add_arguments(parser)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    contents = (
        render_contents(repo_root, args)
        if render_contents is not None
        else render_yaml_mapping(build_items(repo_root.name, args))
    )
    generated_sha256 = hashlib.sha256(contents.encode("utf-8")).hexdigest()
    skill_id = default_output.name.removesuffix("-adapter.yaml")
    try:
        resolved_output = _target_path(repo_root, args.output)
    except ValueError as exc:
        target = args.output if args.output.is_absolute() else repo_root / args.output
        _emit_receipt(
            repo_root=repo_root,
            target=target.resolve(strict=False),
            skill_id=skill_id,
            state="unestablished",
            status="refused",
            ok=False,
            dry_run=args.dry_run,
            force=args.force,
            mutation_invoked=False,
            reason=str(exc),
            next_action="choose a regular file below --repo-root and rerun",
            before_sha256=None,
            generated_sha256=generated_sha256,
        )
        raise SystemExit(2)

    if not resolved_output.exists():
        if args.dry_run:
            _emit_receipt(
                repo_root=repo_root,
                target=resolved_output,
                skill_id=skill_id,
                state="absent",
                status="would-initialize",
                ok=True,
                dry_run=True,
                force=args.force,
                mutation_invoked=False,
                reason="adapter is absent",
                next_action="rerun without --dry-run to initialize the adapter",
                before_sha256=None,
                generated_sha256=generated_sha256,
            )
            return resolved_output
        write_adapter_scaffold(repo_root, resolved_output, contents, force=False)
        _emit_receipt(
            repo_root=repo_root,
            target=resolved_output,
            skill_id=skill_id,
            state="absent",
            status="initialized",
            ok=True,
            dry_run=False,
            force=args.force,
            mutation_invoked=True,
            reason="adapter was absent",
            next_action=None,
            before_sha256=None,
            generated_sha256=generated_sha256,
        )
        return resolved_output

    before_sha256 = _sha256(resolved_output)
    state, reason = _structural_state(resolved_output, contents)
    if state == "valid" and existing_adapter_state is not None:
        try:
            resolved_state = existing_adapter_state(resolved_output)
            if resolved_state != "configured":
                state = resolved_state if resolved_state in {"invalid", "unestablished"} else "unestablished"
                reason = "skill-specific resolver rejected the existing adapter"
        except (Exception, SystemExit) as exc:
            state = "unestablished"
            reason = f"skill-specific resolver could not establish adapter state: {exc}"
    elif state == "valid" and existing_adapter_is_valid is not None:
        try:
            if not existing_adapter_is_valid(resolved_output):
                state = "invalid"
                reason = "skill-specific resolver rejected the existing adapter"
        except (Exception, SystemExit) as exc:
            state = "unestablished"
            reason = f"skill-specific resolver could not establish adapter state: {exc}"

    if state == "valid":
        _emit_receipt(
            repo_root=repo_root,
            target=resolved_output,
            skill_id=skill_id,
            state=state,
            status="unchanged",
            ok=True,
            dry_run=args.dry_run,
            force=args.force,
            mutation_invoked=False,
            reason=reason,
            next_action=None,
            before_sha256=before_sha256,
            generated_sha256=generated_sha256,
        )
        return resolved_output

    if not args.force:
        _emit_receipt(
            repo_root=repo_root,
            target=resolved_output,
            skill_id=skill_id,
            state=state,
            status="refused",
            ok=False,
            dry_run=args.dry_run,
            force=False,
            mutation_invoked=False,
            reason=reason,
            next_action="repair the adapter or rerun with explicit --force after reviewing the replacement",
            before_sha256=before_sha256,
            generated_sha256=generated_sha256,
        )
        raise SystemExit(1)

    if args.dry_run:
        _emit_receipt(
            repo_root=repo_root,
            target=resolved_output,
            skill_id=skill_id,
            state=state,
            status="would-overwrite",
            ok=True,
            dry_run=True,
            force=True,
            mutation_invoked=False,
            reason=reason,
            next_action="rerun without --dry-run to apply the explicit replacement",
            before_sha256=before_sha256,
            generated_sha256=generated_sha256,
        )
        return resolved_output

    write_adapter_scaffold(repo_root, resolved_output, contents, force=True)
    _emit_receipt(
        repo_root=repo_root,
        target=resolved_output,
        skill_id=skill_id,
        state=state,
        status="overwritten",
        ok=True,
        dry_run=False,
        force=True,
        mutation_invoked=True,
        reason=reason,
        next_action=None,
        before_sha256=before_sha256,
        generated_sha256=generated_sha256,
    )
    return resolved_output
