#!/usr/bin/env python3
"""SessionStart hook payload script for the charness session-start routing trigger.

2026-07-04 revision: this hook now carries the ROUTING RULE directly instead of
only pointing at `charness:find-skills`. It injects the pickup ->
`docs/handoff.md` `Workflow Trigger` -> `charness:handoff` route, the
capability-discovery -> `charness:find-skills` route, and the otherwise ->
matching-installed-skill route in one directive, so most sessions no longer pay
for a full `find-skills` invocation just to re-confirm a cached inventory.
Capability-discovery and recommendation intelligence still lives in
`find-skills`, which still drives the routed workflow whenever it is invoked
(discovery, a missing/stale capability map, or a genuinely unclear route). This
front-load design was considered and rejected in #240 because a hook cannot
hard-force a Skill invocation; it was adopted now that session-cost data showed
`find-skills` running on effectively every session open. The three #240
protections are carried over into the directive text itself. See
`skills/public/find-skills/references/session-start-routing.md`.

Wiring (installed at USER level so it fires in every session, pointing at the
released plugin copy of this script — not committed into any one repo):

- Claude Code: a `SessionStart` entry in `~/.claude/settings.json` runs
  `python3 <plugin-source>/scripts/session_start_find_skills.py --host claude`.
- Codex: a `[[hooks.SessionStart]]` entry in `~/.codex/config.toml` runs the
  same script with `--host codex`.

Both hosts add the emitted `hookSpecificOutput.additionalContext` string to the
session context (Codex confirmed 2026-05-29; see
charness-artifacts/gather/2026-05-22-codex-hooks-surface.md). `--host unknown`
falls back to plain stdout, which both hosts also add to context.

Honest ceiling: a hook injects context the model must still honor; it cannot
invoke a Skill tool directly. This strengthens routing via context-recency but
is not hard execution-forcing — the same ceiling as before, now applied to the
front-loaded rule text rather than only to the find-skills pointer.

Failure modes are intentionally silent: hook script errors must never break a
host session. Set `CHARNESS_SESSION_START_DEBUG=1` for stderr diagnostics.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

DIRECTIVE = (
    "charness session-start routing: route the opening message directly. (1) "
    "Pickup — a bare handoff mention or no explicit task (if the message also "
    "names a concrete task, the task governs): follow the repo handoff's "
    "`## Workflow Trigger` (docs/handoff.md; skip this branch if the file "
    "doesn't exist) and invoke the workflow it names; for the default charness "
    "handoff that is `charness:handoff`. "
    "(2) Capability discovery — a named skill/support/integration or a 'which "
    "skill handles X' question: invoke `charness:find-skills`. (3) Otherwise "
    "start the installed charness skill that matches the task. Use "
    "`charness-artifacts/find-skills/latest.md` as the capability map when "
    "present; invoke `charness:find-skills` when the map is missing or stale "
    "or the route is genuinely unclear."
)


def _debug(message: str) -> None:
    if os.environ.get("CHARNESS_SESSION_START_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}:
        print(f"session_start_find_skills: {message}", file=sys.stderr)


def build_additional_context() -> str:
    """Return the front-loaded session-start routing directive."""
    return DIRECTIVE


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
        choices=["claude", "codex", "unknown"],
        default="unknown",
        help="Host that fired the hook; selects the stdout injection format.",
    )
    args = parser.parse_args(argv)
    try:
        payload = _read_payload(sys.stdin)
        _debug(f"source={payload.get('source')!r} cwd={payload.get('cwd')!r}")
        sys.stdout.write(render_output(args.host) + "\n")
    except Exception as exc:  # pragma: no cover - never propagate hook errors
        _debug(f"unhandled error: {exc!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
