"""Shared issue-backend invocation primitives.

`issue_close` and `issue_create` both turn an adapter-resolved backend command
template into a concrete argv and run it without a shell. Keeping the templating
and subprocess primitives here means there is one source of truth for how a
backend op is rendered and invoked — no shell string interpolation anywhere, so
multi-line / Unicode / quote / dollar-sign content in a body file reaches the
backend byte-for-byte (corca-ai/charness#232).
"""

from __future__ import annotations

import re
import subprocess
from typing import Any

BACKEND_TIMEOUT_SECONDS = 60

PLACEHOLDER_RE = re.compile(r"\{([a-z_]+)\}")


def run_backend(argv: list[str]) -> subprocess.CompletedProcess[str]:
    """Run a backend argv with no shell, capturing text output.

    `argv` is a list passed straight to the OS — body/title content lives in the
    args or in a `--body-file`, never in a shell command string, so there is no
    quoting layer to corrupt it.
    """
    try:
        return subprocess.run(
            argv,
            check=False,
            capture_output=True,
            text=True,
            timeout=BACKEND_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        return subprocess.CompletedProcess(
            argv,
            124,
            str(exc.stdout or ""),
            f"timed out after {BACKEND_TIMEOUT_SECONDS}s",
        )


def resolve_op(
    backend: dict[str, Any],
    op: str,
    default: list[str],
    allowed: frozenset[str],
    required: frozenset[str] = frozenset(),
    **subs: str,
) -> list[str]:
    """Render one backend op template into a concrete argv.

    Uses the adapter's `commands.<op>` template when present, else the `gh`
    default for the default backend. Validates the template's placeholders
    against the op's allowlist and required set so an adapter cannot smuggle an
    unknown placeholder or omit a required one.
    """
    extra_subs = sorted(set(subs) - allowed)
    if extra_subs:
        raise RuntimeError(
            f"resolve_op({op}): caller passed placeholders {extra_subs!r} "
            f"not in op's allowlist {sorted(allowed)!r}"
        )
    binary = backend.get("binary") or backend.get("id")
    if not binary:
        raise RuntimeError(
            "issue_backend produced no binary; configure issue_backend.id and "
            "issue_backend.binary in .agents/issue-adapter.yaml."
        )
    commands = backend.get("commands") or {}
    template = commands.get(op)
    if template is None:
        if backend.get("id", "gh") != "gh":
            raise RuntimeError(
                f"issue_backend.id={backend.get('id')} did not declare commands.{op}; "
                "configure the adapter command template before calling this op."
            )
        template = default
    used = {match for part in template for match in PLACEHOLDER_RE.findall(part)}
    unknown = sorted(used - allowed)
    if unknown:
        raise RuntimeError(
            f"resolve_op({op}): adapter template uses unknown placeholders {unknown!r}; "
            f"allowed for {op}: {sorted(allowed)!r}"
        )
    missing_required = sorted(required - used)
    if missing_required:
        raise RuntimeError(
            f"resolve_op({op}): adapter template is missing required placeholders "
            f"{missing_required!r}"
        )
    rendered = [part.format(**subs) if "{" in part else part for part in template]
    return [binary, *rendered]
