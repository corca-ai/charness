from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


def _load_local(module_name: str, alias: str | None = None):
    module_path = Path(__file__).resolve().parent / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(alias or module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_BACKEND = _load_local("issue_backend", "issue_close_backend")
_run_backend = _BACKEND.run_backend
_resolve_op = _BACKEND.resolve_op
BACKEND_TIMEOUT_SECONDS = _BACKEND.BACKEND_TIMEOUT_SECONDS

GH_COMMENT_DEFAULT = [
    "issue",
    "comment",
    "--repo",
    "{repo}",
    "{number}",
    "--body-file",
    "{body_file}",
]

GH_CLOSE_DEFAULT = [
    "issue",
    "close",
    "--repo",
    "{repo}",
    "{number}",
    "--reason",
    "{reason}",
]
GH_VIEW_DEFAULT = [
    "issue",
    "view",
    "--repo",
    "{repo}",
    "{number}",
    "--json",
    "{json_fields}",
]

COMMENT_PLACEHOLDERS: frozenset[str] = frozenset({"repo", "number", "body_file", "reason"})
CLOSE_PLACEHOLDERS: frozenset[str] = frozenset({"repo", "number", "reason"})
VIEW_PLACEHOLDERS: frozenset[str] = frozenset({"repo", "number", "json_fields"})


def close_with_comment(
    repo: str,
    number: int,
    body_file: Path,
    *,
    backend: dict[str, Any] | None = None,
    reason: str = "completed",
) -> dict[str, Any]:
    backend = backend or {"id": "gh", "binary": "gh", "commands": None}
    if not body_file.is_file():
        raise RuntimeError(f"close-comment body file not found: {body_file}")
    comment_argv = _resolve_op(
        backend,
        "comment",
        GH_COMMENT_DEFAULT,
        COMMENT_PLACEHOLDERS,
        repo=repo,
        number=str(number),
        body_file=str(body_file),
        reason=reason,
    )
    close_argv = _resolve_op(
        backend,
        "close",
        GH_CLOSE_DEFAULT,
        CLOSE_PLACEHOLDERS,
        repo=repo,
        number=str(number),
        reason=reason,
    )
    commands = backend.get("commands") or {}
    view_argv = None
    if backend.get("id", "gh") != "gh" and commands.get("view") is None:
        raise RuntimeError(
            "close state verification requires backend commands.view; "
            "comment plus close command success is not issue closeout"
        )
    if backend.get("id", "gh") == "gh" or commands.get("view") is not None:
        view_argv = _resolve_op(
            backend,
            "view",
            GH_VIEW_DEFAULT,
            VIEW_PLACEHOLDERS,
            repo=repo,
            number=str(number),
            json_fields="number,state,url",
        )
    comment_result = _run_backend(comment_argv)
    if comment_result.returncode != 0:
        raise RuntimeError(
            f"comment failed: exit={comment_result.returncode} stderr={comment_result.stderr.strip()!r}"
        )
    close_result = _run_backend(close_argv)
    if close_result.returncode != 0:
        raise RuntimeError(
            "close failed after comment landed; do not re-comment on retry. "
            f"comment_succeeded=True comment_argv={comment_argv!r} "
            f"close_exit={close_result.returncode} close_stderr={close_result.stderr.strip()!r}"
        )
    verified_state: dict[str, Any] | None = None
    if view_argv is not None:
        view_result = _run_backend(view_argv)
        if view_result.returncode != 0:
            raise RuntimeError(
                "close state verification failed after close command succeeded; "
                f"view_exit={view_result.returncode} view_stderr={view_result.stderr.strip()!r}"
            )
        try:
            verified_state = json.loads(view_result.stdout)
        except Exception as exc:
            raise RuntimeError(f"close state verification returned invalid JSON: {exc}") from exc
        if verified_state.get("state") != "CLOSED":
            raise RuntimeError(
                f"close state verification failed: {repo}#{number} is {verified_state.get('state')!r}"
            )
    return {
        "ok": True,
        "repo": repo,
        "number": number,
        "comment_argv": comment_argv,
        "close_argv": close_argv,
        "view_argv": view_argv,
        "verified_state": verified_state,
        "reason": reason,
    }
