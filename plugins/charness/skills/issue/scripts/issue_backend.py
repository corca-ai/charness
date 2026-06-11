"""Shared issue-backend invocation primitives.

`issue_close` and `issue_create` both turn an adapter-resolved backend command
template into a concrete argv and run it without a shell. Keeping the templating
and subprocess primitives here means there is one source of truth for how a
backend op is rendered and invoked — no shell string interpolation anywhere, so
multi-line / Unicode / quote / dollar-sign content in a body file reaches the
backend byte-for-byte.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from typing import Any

BACKEND_TIMEOUT_SECONDS = 60
BACKEND_PROBE_TIMEOUT_SECONDS = 60

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


def run_probe(binary: str, args: list[str]) -> dict[str, Any]:
    try:
        result = subprocess.run(
            [binary, *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=BACKEND_PROBE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "exit_code": 124,
            "stdout": str(exc.stdout or "").strip(),
            "stderr": f"timed out after {BACKEND_PROBE_TIMEOUT_SECONDS}s",
        }
    return {"exit_code": result.returncode, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}


def probe_backend(backend: dict[str, Any]) -> dict[str, Any]:
    binary = backend.get("binary") or backend.get("id")
    if not binary:
        raise RuntimeError(
            "issue_backend produced no binary; configure issue_backend.id and "
            "issue_backend.binary in .agents/issue-adapter.yaml."
        )
    binary_path = shutil.which(binary)
    selected: dict[str, Any] = {
        "id": backend.get("id", "gh"),
        "binary": binary,
        "binary_path": binary_path,
        "found": binary_path is not None,
        "commands": backend.get("commands"),
        "auth_status": None,
        "version": None,
    }
    if binary_path is None:
        return selected
    if selected["id"] == "gh":
        selected["auth_status"] = run_probe(binary, ["auth", "status"])
    else:
        selected["version"] = run_probe(binary, ["--version"])
    return selected


def backend_ok(selected: dict[str, Any]) -> bool:
    if not selected["found"]:
        return False
    if selected["id"] == "gh":
        return bool(selected["auth_status"]) and selected["auth_status"]["exit_code"] == 0
    return True


def build_preflight_payload(resolved: dict[str, Any]) -> dict[str, Any]:
    try:
        selected = probe_backend(resolved["backend"])
    except RuntimeError as exc:
        return {
            "ok": False,
            "error": str(exc),
            "adapter": resolved["adapter"],
            "selected_backend": resolved["backend"],
        }
    ok = resolved["adapter_ok"] and backend_ok(selected)
    payload: dict[str, Any] = {"ok": ok, "selected_backend": selected, "adapter": resolved["adapter"]}
    if selected["id"] == "gh":
        payload.update(gh_found=selected["found"], gh_path=selected["binary_path"], auth_status=selected["auth_status"])
    if not selected["found"]:
        payload["error"] = (
            f"issue_backend binary {selected['binary']!r} not found on PATH. "
            f"Install the declared backend or update issue_backend in "
            f".agents/issue-adapter.yaml so it matches a backend the host exposes."
        )
    return payload
