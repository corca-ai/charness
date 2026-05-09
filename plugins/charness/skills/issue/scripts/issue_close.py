from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

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

COMMENT_PLACEHOLDERS: frozenset[str] = frozenset({"repo", "number", "body_file", "reason"})
CLOSE_PLACEHOLDERS: frozenset[str] = frozenset({"repo", "number", "reason"})

_PLACEHOLDER_RE = re.compile(r"\{([a-z_]+)\}")


def _resolve_op(
    backend: dict[str, Any],
    op: str,
    default: list[str],
    allowed: frozenset[str],
    **subs: str,
) -> list[str]:
    extra_subs = sorted(set(subs) - allowed)
    if extra_subs:
        raise RuntimeError(
            f"_resolve_op({op}): caller passed placeholders {extra_subs!r} "
            f"not in op's allowlist {sorted(allowed)!r}"
        )
    binary = backend.get("binary") or backend.get("id") or "gh"
    commands = backend.get("commands") or {}
    template = commands.get(op)
    if template is None:
        if backend.get("id", "gh") != "gh":
            raise RuntimeError(
                f"issue_backend.id={backend.get('id')} did not declare commands.{op}; "
                "configure the adapter command template before calling this op."
            )
        template = default
    used = {match for part in template for match in _PLACEHOLDER_RE.findall(part)}
    unknown = sorted(used - allowed)
    if unknown:
        raise RuntimeError(
            f"_resolve_op({op}): adapter template uses unknown placeholders {unknown!r}; "
            f"allowed for {op}: {sorted(allowed)!r}"
        )
    rendered = [part.format(**subs) if "{" in part else part for part in template]
    return [binary, *rendered]


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
    comment_result = subprocess.run(comment_argv, check=False, capture_output=True, text=True)
    if comment_result.returncode != 0:
        raise RuntimeError(
            f"comment failed: exit={comment_result.returncode} stderr={comment_result.stderr.strip()!r}"
        )
    close_result = subprocess.run(close_argv, check=False, capture_output=True, text=True)
    if close_result.returncode != 0:
        raise RuntimeError(
            "close failed after comment landed; do not re-comment on retry. "
            f"comment_succeeded=True comment_argv={comment_argv!r} "
            f"close_exit={close_result.returncode} close_stderr={close_result.stderr.strip()!r}"
        )
    return {
        "ok": True,
        "repo": repo,
        "number": number,
        "comment_argv": comment_argv,
        "close_argv": close_argv,
        "reason": reason,
    }
