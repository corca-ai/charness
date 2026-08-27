"""Single owner for adapter-to-provider selection and target binding."""

from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))["sibling_loader"](
    __file__
)
ADAPTER = _load_local("resolve_adapter", "issue_provider_selection_adapter")


def select_backend(repo_root: Path) -> dict[str, Any]:
    """Select one configured provider without hiding invalid configuration."""
    adapter = ADAPTER.load_adapter(repo_root)
    backend = dict(adapter["data"].get("issue_backend") or ADAPTER.default_backend())
    valid = bool(adapter["valid"])
    return {
        "adapter": adapter,
        "backend": backend,
        "adapter_ok": valid,
        "provider_selection": {
            "provider_id": backend.get("id"),
            "binary": backend.get("binary") or backend.get("id"),
            "source": "invalid-adapter" if not valid else ("adapter" if adapter["found"] else "default"),
            "target_repo": None,
            "operations": None,
            "status": "adapter-invalid" if not valid else "unbound",
        },
    }


def bind_provider_selection(
    resolved: dict[str, Any], *, target_repo: str, operations: list[str] | None = None
) -> dict[str, Any]:
    """Bind one selection to the exact target before any provider invocation."""
    if not isinstance(target_repo, str) or not target_repo.strip() or "/" not in target_repo:
        raise RuntimeError("provider selection requires an explicit owner/repo target")
    if operations is not None and (
        not isinstance(operations, list)
        or any(not isinstance(operation, str) or not operation.strip() for operation in operations)
    ):
        raise RuntimeError("provider selection operations must be a list of non-empty strings")

    selection = dict(resolved.get("provider_selection") or {})
    existing_target = selection.get("target_repo")
    if isinstance(existing_target, str) and existing_target.strip():
        if existing_target.strip().lower() != target_repo.strip().lower():
            raise RuntimeError(
                "provider selection is already bound to a different repository: "
                f"{existing_target!r}"
            )
    backend = resolved.get("backend") or {}
    selection.setdefault("provider_id", backend.get("id"))
    selection.setdefault("binary", backend.get("binary") or backend.get("id"))
    selection.setdefault("source", "injected")
    selection["target_repo"] = target_repo.strip()
    selection["operations"] = (
        list(operations) if operations is not None else selection.get("operations")
    )
    selection["status"] = "adapter-invalid" if not resolved.get("adapter_ok") else "ready"
    return {**resolved, "provider_selection": selection}
