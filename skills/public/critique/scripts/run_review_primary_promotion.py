"""Preserve finalized critique carriers beyond a linked worktree's lifetime."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _primary_worktree(support: Any, root: Path) -> Path:
    """Return the shared repository's primary worktree for a linked checkout."""
    from scripts.core.git_checkout import layout_from_files

    resolved_root = root.resolve()
    layout = layout_from_files(resolved_root)
    if layout is None or layout.git_dir == layout.common_dir:
        return resolved_root

    from scripts.worktree.worktree_audit_lib import run_audit

    audit = run_audit(resolved_root)
    value = audit.get("primary_worktree")
    if not isinstance(value, str) or not value:
        raise support.RunReviewError(
            "promotion-primary-unavailable",
            "linked-worktree review could not resolve the primary worktree",
            details={"worktree_audit": audit},
        )
    primary = Path(value).resolve()
    primary_layout = layout_from_files(primary)
    if (
        primary == resolved_root
        or primary_layout is None
        or primary_layout.git_dir != layout.common_dir
        or primary_layout.common_dir != layout.common_dir
    ):
        raise support.RunReviewError(
            "promotion-primary-unavailable",
            "linked-worktree review resolved an invalid primary worktree",
            details={"primary_worktree": str(primary)},
        )
    return primary


def _tree_files(support: Any, root: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise support.RunReviewError(
                "stale-artifact-refused",
                f"refusing linked-worktree promotion through a symlink: {path}",
            )
        if path.is_dir():
            continue
        if not path.is_file():
            raise support.RunReviewError(
                "stale-artifact-refused",
                f"refusing non-file durable reviewer content: {path}",
            )
        files[path.relative_to(root).as_posix()] = path
    return files


def _verify_tree(support: Any, source: Path, destination: Path) -> None:
    if destination.is_symlink() or not destination.is_dir():
        raise support.RunReviewError(
            "stale-artifact-refused",
            f"refusing to replace primary reviewer attempt: {destination}",
        )
    source_files = _tree_files(support, source)
    destination_files = _tree_files(support, destination)
    if source_files.keys() != destination_files.keys():
        raise support.RunReviewError(
            "stale-artifact-refused",
            f"primary reviewer attempt does not match linked-worktree closure: {destination}",
        )
    for relative, source_path in source_files.items():
        if source_path.read_bytes() != destination_files[relative].read_bytes():
            raise support.RunReviewError(
                "stale-artifact-refused",
                f"primary reviewer attempt conflicts at {destination / relative}",
            )


def _copy_or_verify_tree(
    support: Any, storage: Any, source: Path, destination: Path
) -> None:
    if destination.is_symlink() or (destination.exists() and not destination.is_dir()):
        raise support.RunReviewError(
            "stale-artifact-refused",
            f"refusing to replace primary reviewer attempt: {destination}",
        )
    if destination.exists():
        _verify_tree(support, source, destination)
        return

    destination.mkdir(parents=True)
    try:
        source_files = _tree_files(support, source)
        manifest = source_files.pop("attempt-manifest.json", None)
        for relative, source_path in source_files.items():
            storage.copy_or_verify(source_path, destination / relative)
        if manifest is None:
            raise support.RunReviewError(
                "promotion-readback-failed",
                "finalized reviewer attempt has no attempt manifest",
            )
        # The manifest is the attempt's commit point, so it becomes visible last.
        storage.copy_or_verify(manifest, destination / "attempt-manifest.json")
        _verify_tree(support, source, destination)
    except Exception:
        # This directory did not exist before this promotion. Its partial bytes
        # cannot be a prior consumer's evidence, so remove them before retaining
        # the authoritative scratch run for retry.
        import shutil

        shutil.rmtree(destination, ignore_errors=True)
        raise


def _primary_destination(
    support: Any, primary: Path, relative: Path, *, label: str
) -> Path:
    destination = primary / relative
    try:
        destination.resolve(strict=False).relative_to(primary)
    except ValueError as exc:
        raise support.RunReviewError(
            "path-invalid", f"{label} escaped the primary worktree"
        ) from exc
    return destination


def promote_finalized_closure(
    support: Any,
    storage: Any,
    worker_reports: Path,
    root: Path,
    attempt: str,
    paths: dict[str, Path],
) -> dict[str, str]:
    """Copy one exact packet and attempt closure to the primary worktree."""
    root = root.resolve()
    primary = _primary_worktree(support, root)
    if primary == root:
        return {"status": "current-worktree", "root": str(root)}

    source_attempt = root / worker_reports / attempt
    if not source_attempt.is_dir() or source_attempt.is_symlink():
        raise support.RunReviewError(
            "promotion-readback-failed",
            "finalized linked-worktree reviewer attempt is unavailable",
        )
    packet = paths.get("packet")
    if packet is None or not packet.is_file() or packet.is_symlink():
        raise support.RunReviewError(
            "promotion-readback-failed",
            "finalized linked-worktree review packet is unavailable",
        )
    try:
        packet_relative = packet.relative_to(root)
    except ValueError as exc:
        raise support.RunReviewError(
            "path-invalid", "review packet escaped the linked worktree"
        ) from exc

    destination_attempt = _primary_destination(
        support, primary, worker_reports / attempt, label="reviewer attempt"
    )
    destination_packet = _primary_destination(
        support, primary, packet_relative, label="review packet"
    )
    critique_root = worker_reports.parent
    if not packet_relative.is_relative_to(critique_root):
        if (
            destination_packet.is_symlink()
            or not destination_packet.is_file()
            or destination_packet.read_bytes() != packet.read_bytes()
        ):
            raise support.RunReviewError(
                "promotion-primary-refused",
                "linked-worktree packet outside the critique artifact owner is not present in the primary worktree",
            )

    # Preflight both existing owners before writing either side of the closure.
    if destination_attempt.exists() or destination_attempt.is_symlink():
        _verify_tree(support, source_attempt, destination_attempt)
    if destination_packet.exists() or destination_packet.is_symlink():
        storage.copy_or_verify(packet, destination_packet)

    storage.copy_or_verify(packet, destination_packet)
    _copy_or_verify_tree(support, storage, source_attempt, destination_attempt)
    if destination_packet.read_bytes() != packet.read_bytes():
        raise support.RunReviewError(
            "promotion-readback-failed", "primary review packet changed during read-back"
        )
    _verify_tree(support, source_attempt, destination_attempt)
    return {
        "status": "promoted-to-primary",
        "root": str(primary),
        "packet": packet_relative.as_posix(),
        "attempt": (worker_reports / attempt).as_posix(),
    }
