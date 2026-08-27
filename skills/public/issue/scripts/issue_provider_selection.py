"""Resolve the issue provider once for one repository operation.

Provider selection used to be a two-step ``select_backend``/``bind`` protocol
that carried a second, mostly duplicated ``provider_selection`` envelope through
every caller.  The only decisions that matter to an operation are the validated
adapter, the selected backend, and the explicit target repository.  Resolve
those together so callers cannot accidentally invoke a backend before binding
the target or pay the adapter read twice.
"""

from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))["sibling_loader"](
    __file__
)
ADAPTER = _load_local("resolve_adapter", "issue_provider_selection_adapter")


def _normalise_target(target_repo: str) -> str:
    if not isinstance(target_repo, str) or not target_repo.strip() or "/" not in target_repo:
        raise RuntimeError("provider selection requires an explicit owner/repo target")
    owner, name = (part.strip() for part in target_repo.strip().split("/", 1))
    if not owner or not name or "/" in name:
        raise RuntimeError("provider selection target must be an owner/repo slug")
    return f"{owner}/{name}"


def resolve_backend(
    repo_root: Path,
    *,
    target_repo: str | None = None,
    adapter: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve one adapter/backend pair and optionally bind its target.

    ``adapter`` is injectable for callers that already loaded it while resolving
    a repository (notably Goal Run pickup).  That keeps the normal path to one
    adapter read without weakening invalid-adapter refusal.
    """
    selected_adapter = adapter if adapter is not None else ADAPTER.load_adapter(repo_root)
    backend = dict(selected_adapter["data"].get("issue_backend") or ADAPTER.default_backend())
    if target_repo is not None and selected_adapter["valid"]:
        target = _normalise_target(target_repo)
        scoped = backend.get("repo_scoped")
        if isinstance(scoped, str) and scoped.strip() and scoped.strip().lower() != target.lower():
            raise RuntimeError(
                f"provider backend is scoped to {scoped.strip()!r}, not the requested {target!r}"
            )
    return {
        "adapter": selected_adapter,
        "backend": backend,
        "adapter_ok": bool(selected_adapter["valid"]),
    }
