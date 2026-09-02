"""Public Goal Binding V1 API.

Schema and manifest rules live in the adjacent canonical support module.  This
file owns binding construction, freeze, and readback so callers have one
obvious lifecycle surface in both the public and exported plugin trees.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from goal_binding_support import (  # noqa: E402
    APPROVAL_FIELDS,
    DRAFT_FIELDS,
    SCHEMA,
    BindingError,
    _relative_repo_path,
    _repo_path,
    _require_fields,
    _require_object,
    _require_sha,
    _require_text,
    _validate_identity,
    _validate_item,
    _validate_manifest,
    _validate_relative_text_path,
    canonical_json_bytes,
    sha256_bytes,
    sha256_file,
)


def binding_path_for_draft(draft_path: str | Path) -> Path:
    path = Path(draft_path)
    if path.suffix != ".md":
        raise BindingError("path-invalid", "Goal Draft path must end in .md")
    return path.with_suffix(".binding.json")


def build_binding(
    *,
    draft_path: str,
    draft_sha256: str,
    briefing_sha256: str,
    approval_response: str,
    approval_session_id: str,
    approval_observed_at: str,
    parent: dict[str, Any],
    approved_work_items: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build canonical bytes; file and authority checks happen at freeze/readback."""
    _validate_relative_text_path(draft_path, context="draft.path", suffix=".md")
    _require_sha(draft_sha256, "draft-frozen", "draft.sha256")
    _require_sha(briefing_sha256, "approval-missing", "approval.briefing_sha256")
    _require_text(approval_response, "approval-missing", "approval.response")
    _require_text(approval_session_id, "approval-missing", "approval.session_id")
    _require_text(approval_observed_at, "approval-missing", "approval.observed_at")
    parent_value = _validate_identity(parent, context="parent")
    if not isinstance(approved_work_items, list) or not approved_work_items:
        raise BindingError("schema-invalid", "approved_work_items must be a non-empty list")
    # Planner order is accepted; the producer emits only canonical key order.
    prevalidated = [_validate_item(item, parent=parent_value) for item in approved_work_items]
    items = sorted(prevalidated, key=lambda item: item["key"])
    _validate_manifest(items, parent=parent_value)
    return {
        "kind": SCHEMA,
        "draft": {"path": draft_path, "sha256": draft_sha256},
        "approval": {
            "briefing_sha256": briefing_sha256,
            "response": approval_response,
            "session_id": approval_session_id,
            "observed_at": approval_observed_at,
        },
        "parent": parent_value,
        "approved_work_items": items,
        "approved_work_items_sha256": sha256_bytes(canonical_json_bytes(items)),
    }


def _binding_location(
    root: Path, binding_path: str | Path, *, require_file: bool
) -> tuple[str, Path]:
    relative, candidate, _ = _repo_path(
        root,
        binding_path,
        context="binding path",
        suffix=".json",
        require_file=require_file,
        missing_code="binding-missing",
    )
    return relative, candidate


def _expected_draft_relative(root: Path, value: str | Path) -> str:
    relative, _, _ = _repo_path(
        root,
        value,
        context="expected Goal Draft path",
        suffix=".md",
        require_file=False,
        missing_code="draft-missing",
    )
    return relative


def _ensure_parent_chain(root: Path, parent: Path) -> None:
    try:
        relative = parent.relative_to(root)
    except ValueError as exc:
        raise BindingError("path-invalid", "binding parent directory escapes the repository") from exc
    current = root
    for part in relative.parts:
        current /= part
        if os.path.lexists(current):
            if current.is_symlink() or not current.is_dir():
                raise BindingError("path-invalid", "binding parent directory is not a real directory")
        else:
            try:
                current.mkdir()
            except FileExistsError:
                if current.is_symlink() or not current.is_dir():
                    raise BindingError("path-invalid", "binding parent directory is not a real directory")


def _validate_payload(  # noqa: C901 -- binding payload validation keeps cross-field refusal semantics together
    root: Path,
    binding_path: Path,
    value: Any,
    *,
    raw: bytes | None,
    expected_parent: dict[str, Any] | None,
    expected_draft_path: str | Path | None,
    expected_draft_sha256: str | None,
    expected_binding_sha256: str | None,
    require_authority: bool,
    binding_must_exist: bool,
) -> dict[str, Any]:
    if require_authority and expected_parent is None:
        raise BindingError("parent-unverified", "exact parent readback is required")
    if require_authority and expected_draft_path is None:
        raise BindingError("draft-frozen", "exact frozen Goal Draft path is required")
    if require_authority and expected_draft_sha256 is None:
        raise BindingError("draft-frozen", "exact frozen Goal Draft hash is required")

    binding_rel, _ = _binding_location(root, binding_path, require_file=binding_must_exist)
    value = _require_object(value, "schema-invalid", "binding")
    _require_fields(value, frozenset({"kind", "draft", "approval", "parent", "approved_work_items", "approved_work_items_sha256"}), "binding")
    if value["kind"] != SCHEMA:
        raise BindingError("schema-unknown", f"unsupported binding kind: {value['kind']!r}")
    rendered = canonical_json_bytes(value)
    if raw is not None and rendered != raw:
        raise BindingError("binding-hash-mismatch", "binding bytes are not canonical JSON")
    actual_binding_sha = sha256_bytes(raw if raw is not None else rendered)
    if expected_binding_sha256 is not None:
        _require_sha(expected_binding_sha256, "binding-hash-mismatch", "expected binding hash")
        if actual_binding_sha != expected_binding_sha256:
            raise BindingError("binding-hash-mismatch", "binding complete-byte hash differs")
    elif require_authority and binding_must_exist:
        raise BindingError("parent-unverified", "parent metadata must bind the complete binding hash")

    draft = _require_object(value["draft"], "schema-invalid", "draft")
    _require_fields(draft, DRAFT_FIELDS, "draft")
    draft_path, draft_file = _relative_repo_path(root, draft["path"], context="draft.path", suffix=".md")
    draft_sha = _require_sha(draft["sha256"], "draft-hash-mismatch", "draft.sha256")
    try:
        actual_draft_sha = sha256_file(draft_file)
    except BindingError:
        raise
    except (OSError, ValueError) as exc:
        raise BindingError("draft-missing", f"could not read frozen draft {draft_file}: {exc}") from exc
    # The binding records the draft hash at approval as the plan's identity.
    # The draft file may be amended afterwards under operator approval; that is
    # reversible, visible in git, and reported rather than refused.
    draft_amended = actual_draft_sha != draft_sha
    if expected_draft_path is not None:
        expected_rel = _expected_draft_relative(root, expected_draft_path)
        if draft_path != expected_rel:
            raise BindingError("parent-mismatch", "binding names a different Goal Draft")
    if expected_draft_sha256 is not None:
        _require_sha(expected_draft_sha256, "draft-frozen", "expected frozen draft hash")
        if draft_sha != expected_draft_sha256:
            raise BindingError("draft-frozen", "binding does not match the approved frozen draft hash")
    if binding_rel != binding_path_for_draft(draft_path).as_posix():
        raise BindingError("path-invalid", "binding is not the deterministic Goal Draft sibling")

    approval = _require_object(value["approval"], "schema-invalid", "approval")
    _require_fields(approval, APPROVAL_FIELDS, "approval")
    _require_sha(approval["briefing_sha256"], "approval-missing", "approval.briefing_sha256")
    for field in ("response", "session_id", "observed_at"):
        _require_text(approval[field], "approval-missing", f"approval.{field}")
    parent = _validate_identity(value["parent"], context="parent")
    if expected_parent is not None:
        _validate_identity(expected_parent, context="expected parent")
        if parent != expected_parent:
            raise BindingError("parent-mismatch", "binding parent identity differs from expected parent")

    items = _validate_manifest(value["approved_work_items"], parent=parent)
    expected_items_sha = _require_sha(
        value["approved_work_items_sha256"], "graph-digest-mismatch", "approved_work_items_sha256"
    )
    if sha256_bytes(canonical_json_bytes(items)) != expected_items_sha:
        raise BindingError("graph-digest-mismatch", "approved work-item digest differs")
    return {
        "ok": True,
        "authority": "parent-bound" if require_authority else "structural-only",
        "kind": SCHEMA,
        "binding_path": binding_rel,
        "binding_sha256": actual_binding_sha,
        "draft_path": draft_path,
        "draft_sha256": draft_sha,
        "draft_amended": draft_amended,
        "draft_current_sha256": actual_draft_sha,
        "briefing_sha256": approval["briefing_sha256"],
        "approval": approval,
        "parent": parent,
        "approved_work_items_sha256": expected_items_sha,
        "approved_work_item_count": len(items),
        "approved_work_items": items,
    }


def write_immutable_binding(
    path: Path,
    payload: dict[str, Any],
    *,
    repo_root: Path | None = None,
    expected_parent: dict[str, Any] | None = None,
    expected_draft_path: str | Path | None = None,
    expected_draft_sha256: str | None = None,
) -> str:
    """Freeze one validated binding with an exclusive, durable atomic create."""
    if repo_root is None or expected_parent is None:
        raise BindingError("parent-unverified", "exact parent readback is required before binding creation")
    if expected_draft_path is None or expected_draft_sha256 is None:
        raise BindingError("draft-frozen", "exact frozen Goal Draft identity is required before binding creation")
    root = repo_root.resolve()
    _, candidate = _binding_location(root, path, require_file=False)
    if os.path.lexists(candidate):
        raise BindingError("binding-frozen", f"binding already exists: {candidate}")
    rendered = canonical_json_bytes(payload)
    _validate_payload(
        root,
        candidate,
        payload,
        raw=rendered,
        expected_parent=expected_parent,
        expected_draft_path=expected_draft_path,
        expected_draft_sha256=expected_draft_sha256,
        expected_binding_sha256=None,
        require_authority=True,
        binding_must_exist=False,
    )
    _ensure_parent_chain(root, candidate.parent)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=candidate.parent,
            prefix=f".{candidate.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = handle.name
            handle.write(rendered)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, candidate)
        except FileExistsError as exc:
            raise BindingError("binding-frozen", f"binding already exists: {candidate}") from exc
        os.unlink(temporary)
        temporary = None
        directory_fd = os.open(candidate.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except BindingError:
        raise
    except (OSError, ValueError) as exc:
        raise BindingError("binding-write-failed", f"could not atomically freeze binding: {exc}") from exc
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)
    return sha256_bytes(rendered)


def validate_structural_binding(
    repo_root: Path,
    binding_path: Path,
    *,
    expected_parent: dict[str, Any] | None = None,
    expected_draft_path: str | Path | None = None,
    expected_draft_sha256: str | None = None,
    expected_binding_sha256: str | None = None,
) -> dict[str, Any]:
    """Validate local bytes only; this intentionally makes no authority claim."""
    root = repo_root.resolve()
    _, path = _binding_location(root, binding_path, require_file=True)
    try:
        raw = path.read_bytes()
    except (OSError, ValueError) as exc:
        raise BindingError("binding-missing", f"could not read binding file {path}: {exc}") from exc
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BindingError("schema-invalid", f"binding is not valid UTF-8 JSON: {exc}") from exc
    return _validate_payload(
        root,
        path,
        payload,
        raw=raw,
        expected_parent=expected_parent,
        expected_draft_path=expected_draft_path,
        expected_draft_sha256=expected_draft_sha256,
        expected_binding_sha256=expected_binding_sha256,
        require_authority=False,
        binding_must_exist=True,
    )


def validate_binding(
    repo_root: Path,
    binding_path: Path,
    *,
    expected_parent: dict[str, Any] | None = None,
    expected_draft_path: str | Path | None = None,
    expected_draft_sha256: str | None = None,
    expected_binding_sha256: str | None = None,
) -> dict[str, Any]:
    """Validate a binding at the lifecycle authority boundary."""
    if expected_parent is None or expected_binding_sha256 is None:
        raise BindingError("parent-unverified", "exact parent readback and binding hash are required")
    if expected_draft_path is None or expected_draft_sha256 is None:
        raise BindingError("draft-frozen", "exact frozen Goal Draft identity is required")
    return validate_structural_binding(
        repo_root,
        binding_path,
        expected_parent=expected_parent,
        expected_draft_path=expected_draft_path,
        expected_draft_sha256=expected_draft_sha256,
        expected_binding_sha256=expected_binding_sha256,
    ) | {"authority": "parent-bound"}
