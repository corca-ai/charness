#!/usr/bin/env python3
"""SessionStart hook payload script for contextual session routing hints.

The hook carries context only: pickup follows the handoff, ordinary requests
start their matching workflow from installed skill metadata and model judgment,
and hidden support or integration availability uses the exact read-only
`charness catalog list --repo-root <repo> --summary` inventory. A nonzero result
is reported as a command failure. The hook supplies context for the session.

Wiring (installed at USER level so it fires in every session, pointing at the
released plugin copy of this script — not committed into any one repo):

- Claude Code: a `SessionStart` entry in `~/.claude/settings.json` runs
  `python3 <plugin-source>/scripts/session_start_routing.py --host claude`.
- Codex: a `[[hooks.SessionStart]]` entry in `~/.codex/config.toml` runs the
  same script with `--host codex`.

Both hosts add the emitted `hookSpecificOutput.additionalContext` string to the
session context (Codex confirmed 2026-05-29; see
charness-artifacts/gather/2026-05-22-codex-hooks-surface.md). `--host unknown`
falls back to plain stdout, which both hosts also add to context.

Honest ceiling: a hook injects context the model must still honor; it cannot
invoke a Skill tool directly. This strengthens routing via context-recency but
is not hard execution-forcing; the front-loaded rule text remains contextual.

Failure modes are intentionally silent: hook script errors must never break a
host session. Set `CHARNESS_SESSION_START_DEBUG=1` for stderr diagnostics.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

HANDOFF_ADAPTER_RELATIVE = Path(".agents/handoff-adapter.yaml")
RESOLVER_TIMEOUT_SECONDS = 3

DIRECTIVE = (
    "charness session-start routing: route the opening message directly. (1) "
    "Pickup — a bare handoff mention or no explicit task (if the message also "
    "names a concrete task, the task governs): follow the repo handoff's "
    "`## Workflow Trigger` (docs/handoff.md; skip this branch if the file "
    "doesn't exist) and invoke the workflow it names; for the default charness "
    "handoff that is `charness:handoff`. "
    "(2) Ordinary requests — use installed skill metadata and your own judgment "
    "to start the matching workflow directly. (3) Hidden support/integration inventory "
    "or an unclear availability question — run the read-only `charness catalog "
    "list --repo-root <repo> --summary` command. Treat its facts only as inventory; "
    "if the command returns nonzero, report the command failure."
)


def _handoff_resolver() -> Path | None:
    """Find the handoff resolver in either authoring or shipped-plugin layout."""
    plugin_root = Path(__file__).resolve().parent.parent
    return next(
        (
            candidate
            for candidate in (
                plugin_root / "skills" / "public" / "handoff" / "scripts" / "resolve_adapter.py",
                plugin_root / "skills" / "handoff" / "scripts" / "resolve_adapter.py",
            )
            if candidate.is_file()
        ),
        None,
    )


def _discover_repo_root(cwd: str) -> Path | None:
    """Find the nearest handoff adapter, otherwise the enclosing Git root."""
    candidate = Path(cwd).expanduser().resolve()
    if not candidate.is_dir():
        return None
    git_root: Path | None = None
    while True:
        if (candidate / HANDOFF_ADAPTER_RELATIVE).is_file():
            return candidate
        if git_root is None and (candidate / ".git").exists():
            git_root = candidate
        if candidate.parent == candidate:
            return git_root
        candidate = candidate.parent


def _configured_handoff_state(cwd: object) -> tuple[str, bool] | None:
    """Return the adapter-owned handoff path and whether it is present.

    SessionStart receives a cwd from both supported hosts.  Resolve the same
    handoff adapter the workflow uses instead of deciding presence from the
    author's default path.  This stays deliberately fail-closed: a malformed
    payload, resolver, or path produces no pickup route rather than a route to
    an unrelated artifact.
    """
    if not isinstance(cwd, str) or not cwd.strip():
        return None
    repo_root = _discover_repo_root(cwd)
    if repo_root is None:
        return None
    resolver = _handoff_resolver()
    if resolver is None:
        return None
    try:
        completed = subprocess.run(
            [sys.executable, str(resolver), "--repo-root", str(repo_root)],
            capture_output=True,
            text=True,
            timeout=RESOLVER_TIMEOUT_SECONDS,
            check=False,
        )
        if completed.returncode != 0:
            return None
        payload = json.loads(completed.stdout)
        artifact_path = payload.get("artifact_path") if isinstance(payload, dict) else None
        if not isinstance(artifact_path, str) or not artifact_path.strip():
            return None
        relative = Path(artifact_path)
        if relative.is_absolute():
            return None
        resolved = (repo_root / relative).resolve()
        try:
            resolved.relative_to(repo_root)
        except ValueError:
            return None
        return (relative.as_posix(), resolved.is_file())
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError, ValueError):
        return None


def _debug(message: str) -> None:
    if os.environ.get("CHARNESS_SESSION_START_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}:
        print(f"session_start_routing: {message}", file=sys.stderr)


def build_additional_context(cwd: object | None = None) -> str:
    """Return the front-loaded session-start routing directive.

    With a host-provided cwd, the pickup branch reflects the configured handoff
    artifact's actual presence.  The no-argument default preserves the portable
    context used by direct callers that have no repository state to inspect.
    """
    if not isinstance(cwd, str) or not cwd.strip():
        return DIRECTIVE
    state = _configured_handoff_state(cwd)
    if state is None:
        pickup = (
            "Pickup — the hook could not resolve the configured handoff artifact; "
            "report that routing boundary instead of inventing a handoff path. "
        )
    else:
        artifact_path, exists = state
        if exists:
            pickup = (
                "Pickup — a bare handoff mention or no explicit task (if the message also "
                "names a concrete task, the task governs): follow the repo handoff's "
                f"`## Workflow Trigger` ({artifact_path}) and invoke the workflow it names; "
                "for the default charness handoff that is `charness:handoff`. "
            )
        else:
            pickup = (
                f"Pickup — the configured handoff artifact `{artifact_path}` is absent, "
                "so skip the handoff branch. "
            )
    ordinary = (
        "(2) Ordinary requests — use installed skill metadata and your own judgment "
        "to start the matching workflow directly. (3) Hidden support/integration inventory "
        "or an unclear availability question — run the read-only `charness catalog "
        "list --repo-root <repo> --summary` command. Treat its facts only as inventory; "
        "if the command returns nonzero, report the command failure."
    )
    return "charness session-start routing: route the opening message directly. (1) " + pickup + ordinary


def render_output(host: str, *, directive: str | None = None) -> str:
    """Render the host-appropriate stdout payload that injects the directive.

    Claude Code and Codex both read `hookSpecificOutput.additionalContext` and
    add it to session context. `unknown` falls back to plain stdout, which both
    hosts also add to context.
    """
    text = directive if directive is not None else build_additional_context()
    if host in ("claude", "codex"):
        return json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": text,
                }
            },
            ensure_ascii=False,
        )
    # Grok Build ignores SessionStart stdout today, so keep the plain-text
    # fallback. The host flag is still recorded so installers can pass `--host grok`.
    return text


def _read_payload(stream) -> dict[str, object]:
    try:
        raw = (stream.read() or "").strip()
    except OSError as exc:
        _debug(f"stdin read failed: {exc}")
        return {}
    if not raw:
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        _debug(f"stdin JSON decode failed: {exc}")
        return {}
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--host",
        choices=["claude", "codex", "grok", "unknown"],
        default="unknown",
        help="Host that fired the hook; selects the stdout injection format.",
    )
    args = parser.parse_args(argv)
    try:
        payload = _read_payload(sys.stdin)
        _debug(f"source={payload.get('source')!r} cwd={payload.get('cwd')!r}")
        sys.stdout.write(render_output(args.host, directive=build_additional_context(payload.get("cwd"))) + "\n")
    except Exception as exc:  # pragma: no cover - never propagate hook errors
        _debug(f"unhandled error: {exc!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
