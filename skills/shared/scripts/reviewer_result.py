#!/usr/bin/env python3
"""Diagnostic reader for a bounded reviewer's final message from a host transcript.

THIS IS NOT THE DELIVERY CONTRACT PATH. That path lives in
``skills/shared/references/fresh-eye-subagent-review.md`` ("Result Delivery"):
spawn one-shot bounded reviewers WITHOUT a host addressing or team name and the
findings arrive in the parent's own context. A review recovered with this script
is a *delivery failure to report*, recorded next to the recovered review.

Its only job is telling "the reviewer produced nothing" apart from "delivery
dropped it", once, deterministically. So it never sleeps, retries, or polls -- an
unfinished reviewer returns ``still-running`` once and the caller decides -- and
it never returns the transcript, only the final assistant text block under
``--max-chars``, since parent-context overflow is why guidance warns against
reading these files at all.

Host plurality: the on-disk layout is a host implementation detail, not a
charness contract. Resolution order is ``--transcript-root``, then
``$CHARNESS_REVIEWER_TRANSCRIPT_ROOT``, then the one probed built-in layout
(Claude Code: ``<config>/projects/<slug>/<session>/subagents``). Anything else
gets an honest ``layout-not-found``, never a guess; Codex is not inspected.

Subcommands ``list`` and ``get --agent <name-or-id>``. Exit codes: 0 text
returned (``found``, or ``partial`` under ``--allow-partial``) or list ok,
1 layout resolved but no final block (``still-running`` / ``not-found`` /
``ambiguous`` / ``session-not-found``), 2 usage error, 3 ``layout-not-found``.
"""

from __future__ import annotations

import argparse
import glob
import importlib.util
import json
import os
import re
import sys


def _load_yaml_output():
    """Load the shared YAML renderer from the nearest tree root, by path.

    This file runs from the repo AND from an installed plugin's
    `shared/scripts/`, where no package context exists and the cwd is the
    consuming repository -- so the helper (`<repo>/scripts/yaml_output.py` here,
    `<plugin-root>/scripts/yaml_output.py` there) is walked to rather than
    counted. The walk is BOUNDED for the reason `authoring_script_shim.locate`
    records: an unbounded one climbs past the package into the CONSUMING
    repository and would execute whatever `scripts/yaml_output.py` it found."""
    directory = os.path.dirname(os.path.abspath(__file__))
    for _ in range(5):
        directory = os.path.dirname(directory)
        candidate = os.path.join(directory, "scripts", "yaml_output.py")
        if os.path.isfile(candidate):
            spec = importlib.util.spec_from_file_location("charness_yaml_output", candidate)
            if spec is None or spec.loader is None:
                break
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("scripts/yaml_output.py not found within 5 ancestors of this script")


emit_yaml = _load_yaml_output().emit_yaml

_CONTRACT_NOTE = (
    "diagnostic only: transcript recovery is not the reviewer delivery contract path; "
    "record the delivery failure that made it necessary"
)
_DEFAULT_MAX_CHARS = 4000
# Caps, in order: returned reviewer text default, per-record parse refusal (never
# pull an absurd line into memory), host-supplied metadata string, enumeration
# length. These bound every reviewer-produced and host-metadata value; the
# caller's own arguments (selector, session, transcript root) are echoed as given.
_MAX_LINE_CHARS = 4_000_000
_MAX_FIELD_CHARS = 200
_MAX_AGENTS = 50
_ID_PREFIX = "agent-"


class ResultError(Exception):
    """A usage-level failure: unreadable override path, bad arguments."""


def _slugify_repo_root(repo_root: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(repo_root))


def _claude_projects_dir(repo_root: str) -> str:
    base = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")
    return os.path.join(base, "projects", _slugify_repo_root(repo_root))


def _session_dirs(projects_dir: str) -> list[str]:
    if not os.path.isdir(projects_dir):
        return []
    candidates = (os.path.join(projects_dir, e, "subagents") for e in sorted(os.listdir(projects_dir)))
    return [path for path in candidates if os.path.isdir(path)]


def resolve_root(repo_root: str, session: str | None, override: str | None) -> dict:
    """Resolve the reviewer transcript directory, reporting WHICH directory answered.

    ``root`` is None when unresolved; ``sessions`` is present only when the host
    layout resolved but the requested session id did not.
    """
    explicit = override or os.environ.get("CHARNESS_REVIEWER_TRANSCRIPT_ROOT")
    if explicit:
        if not os.path.isdir(explicit):
            raise ResultError(f"transcript root is not a directory: {explicit}")
        layout = "explicit" if override else "env"
        root = os.path.abspath(explicit)
        return {"root": root, "layout": layout, "session": session, "session_resolution": "override"}

    projects_dir = _claude_projects_dir(repo_root)
    candidates = _session_dirs(projects_dir)
    if session:
        found = os.path.join(projects_dir, session, "subagents")
        if os.path.isdir(found):
            return {"root": found, "layout": "claude-code", "session": session, "session_resolution": "explicit"}
        # The layout resolved; only this session id did not. Reporting
        # "layout-not-found" here would let a typo be recorded as a host claim.
        unresolved = {"root": None, "session": session, "session_resolution": "explicit"}
        if not candidates:
            return {**unresolved, "layout": None}
        sessions = [os.path.basename(os.path.dirname(path)) for path in candidates]
        return {**unresolved, "layout": "claude-code", "sessions": sessions}

    if not candidates:
        return {"root": None, "layout": None, "session": None, "session_resolution": None}
    root = max(candidates, key=os.path.getmtime)
    session_id = os.path.basename(os.path.dirname(root))
    return {"root": root, "layout": "claude-code", "session": session_id, "session_resolution": "most-recent"}


def _read_meta(transcript_path: str) -> dict:
    try:
        with open(transcript_path[: -len(".jsonl")] + ".meta.json", encoding="utf-8") as handle:
            meta = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}
    return meta if isinstance(meta, dict) else {}


def _agent_id(transcript_path: str) -> str:
    stem = os.path.basename(transcript_path)[: -len(".jsonl")]
    return stem[len(_ID_PREFIX) :] if stem.startswith(_ID_PREFIX) else stem


def _text_blocks(message: dict) -> tuple[str, bool]:
    """Joined text blocks, plus whether the same message also issued a tool call."""
    content = message.get("content")
    if isinstance(content, str):
        return content, False
    if not isinstance(content, list):
        return "", False
    blocks = [block for block in content if isinstance(block, dict)]
    parts = [block.get("text", "") for block in blocks if block.get("type") == "text"]
    tool_use = any(block.get("type") == "tool_use" for block in blocks)
    return "\n".join(part for part in parts if part), tool_use


def _finished_turn(message: dict, tool_use: bool) -> bool:
    """Text alongside a tool call is a mid-loop preamble, not a result, however
    the record happens to be positioned. An absent ``stop_reason`` means the host
    does not report one: fall back to position rather than invent a claim."""
    if tool_use:
        return False
    return message.get("stop_reason", "__absent__") not in ("tool_use", None)


def scan_transcript(path: str) -> dict:
    """Last assistant text block plus whether it actually terminates the transcript.

    Terminality separates ``found`` from ``still-running``. It still cannot
    distinguish "still running" from "died mid-turn", and does not claim to.
    """
    text: str | None = None
    text_index, last_turn_index, records, skipped = -1, -1, 0, 0
    stop_reason, finished = None, False
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            for index, line in enumerate(handle):
                if not line.strip():
                    continue
                records += 1
                if len(line) > _MAX_LINE_CHARS:
                    skipped += 1
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(record, dict) or record.get("type") not in ("assistant", "user"):
                    continue
                # Only turn records decide terminality. A host that appends
                # trailing summary/usage records after the final message must not
                # make a finished reviewer look like it is still working.
                last_turn_index = index
                if record.get("type") != "assistant":
                    continue
                message = record.get("message")
                if not isinstance(message, dict):
                    continue
                block, tool_use = _text_blocks(message)
                if block:
                    text, text_index = block, index
                    stop_reason = message.get("stop_reason")
                    finished = _finished_turn(message, tool_use)
    except OSError as exc:
        raise ResultError(f"unreadable transcript {path}: {exc}") from exc
    return {
        "text": text,
        "terminal": text is not None and text_index == last_turn_index and finished,
        "records": records,
        "stop_reason": stop_reason,
        "skipped_oversized_records": skipped,
    }


def _match_fields(transcript_path: str, meta: dict) -> list[str]:
    fields = [
        _agent_id(transcript_path),
        os.path.basename(transcript_path)[: -len(".jsonl")],
        meta.get("name"),
        meta.get("agentType"),
        meta.get("customAgentType"),
        meta.get("description"),
    ]
    return [str(value).lower() for value in fields if value]


def list_agents(root: str) -> list[dict]:
    agents = []
    for path in sorted(glob.glob(os.path.join(root, "*.jsonl"))):
        meta = _read_meta(path)
        agents.append({
            "id": _agent_id(path),
            "name": meta.get("name"),
            "agent_type": meta.get("customAgentType") or meta.get("agentType"),
            "description": meta.get("description"),
            "file": path,
            "mtime": int(os.path.getmtime(path)),
            "match_fields": _match_fields(path, meta),
        })
    return agents


def select_agents(agents: list[dict], selector: str) -> list[dict]:
    needle = selector.lower()
    exact = [agent for agent in agents if needle in agent["match_fields"]]
    return exact or [a for a in agents if any(needle in field for field in a["match_fields"])]


def _clip(key: str, value: object) -> object:
    """Clip host-supplied free text, never identifiers or paths: a silently
    truncated id or file path is a wrong value, not a bounded one."""
    if key in ("id", "file") or not isinstance(value, str):
        return value
    return value[:_MAX_FIELD_CHARS] if len(value) > _MAX_FIELD_CHARS else value


def _public(agent: dict) -> dict:
    return {key: _clip(key, value) for key, value in agent.items() if key != "match_fields"}


def _public_list(agents: list[dict]) -> tuple[list[dict], int]:
    """An unbounded agent list is an unbounded stdout, so cap the enumeration too."""
    return [_public(agent) for agent in agents[:_MAX_AGENTS]], len(agents)


def _envelope(resolved: dict) -> dict:
    keys = {"layout": "layout", "session": "session", "session_resolution": "session_resolution"}
    envelope = {out: resolved[src] for out, src in keys.items()}
    envelope["transcript_root"] = resolved["root"]
    return {**envelope, "diagnostic_only": True, "contract": _CONTRACT_NOTE}


def _unresolved(repo_root: str, resolved: dict) -> tuple[dict, int]:
    """Keep "this host's layout is unknown" separate from "that session id is not
    here": collapsing the second into the first would let a mistyped session id be
    recorded as a host portability claim."""
    base = {"ok": False, "transcript_root": None, "diagnostic_only": True, "contract": _CONTRACT_NOTE}
    if resolved.get("sessions") is not None:
        return {
            **base,
            "status": "session-not-found",
            "layout": resolved["layout"],
            "session": resolved["session"],
            "session_count": len(resolved["sessions"]),
            "sessions": resolved["sessions"][:_MAX_AGENTS],
            "note": "the host layout resolved; this session id has no reviewer transcripts.",
        }, 1
    return {
        **base,
        "status": "layout-not-found",
        "layout": None,
        "note": (
            "no reviewer transcript layout resolved on this host; pass --transcript-root or set "
            "CHARNESS_REVIEWER_TRANSCRIPT_ROOT. Probed Claude Code layout: "
            f"{_claude_projects_dir(repo_root)}/<session>/subagents. Other hosts, including Codex, "
            "are not inspected and are not claimed to persist reviewer transcripts."
        ),
    }, 3


def _cap(text: str, max_chars: int) -> tuple[str, bool, int]:
    full = len(text)
    if full <= max_chars:
        return text, False, full
    return text[:max_chars], True, full


def _text_payload(args: argparse.Namespace, common: dict, scan: dict) -> dict:
    text, truncated, full = _cap(scan["text"] or "", args.max_chars)
    payload = {
        "ok": True,
        "status": "found" if scan["terminal"] else "partial",
        **common,
        "stop_reason": scan["stop_reason"],
        "text": text,
        "text_chars": full,
        "truncated": truncated,
    }
    if not scan["terminal"]:
        payload["note"] = (
            "transcript does not end on a finished assistant turn; this is the last text block "
            "written, not a confirmed final result"
        )
    return payload


def _get_payload(args: argparse.Namespace, resolved: dict) -> tuple[dict, int]:
    matches = select_agents(list_agents(resolved["root"]), args.agent)
    base = {**_envelope(resolved), "selector": args.agent}
    if not matches:
        return {"ok": False, "status": "not-found", **base}, 1
    if len(matches) > 1:
        candidates, total = _public_list(matches)
        return {"ok": False, "status": "ambiguous", **base, "agent_count": total, "agents": candidates}, 1

    agent = matches[0]
    scan = scan_transcript(agent["file"])
    common = {**base, "agent": _public(agent), "records": scan["records"]}
    if scan["skipped_oversized_records"]:
        common["skipped_oversized_records"] = scan["skipped_oversized_records"]
    if scan["terminal"] or (args.allow_partial and scan["text"]):
        return _text_payload(args, common, scan), 0
    return {
        "ok": False,
        "status": "still-running",
        **common,
        "text": None,
        "note": (
            "no finished assistant text turn at the end of this transcript. On-disk state cannot "
            "distinguish still-running from died mid-turn. Read once: this is not an invitation "
            "to poll. Use --allow-partial to see the last text block written."
        ),
    }, 1


def _list_payload(_args: argparse.Namespace, resolved: dict) -> tuple[dict, int]:
    agents, total = _public_list(list_agents(resolved["root"]))
    return {"ok": True, "status": "listed", **_envelope(resolved), "agent_count": total, "agents": agents}, 0


def _run(args: argparse.Namespace, build) -> int:
    resolved = resolve_root(args.repo_root, args.session, args.transcript_root)
    payload, code = _unresolved(args.repo_root, resolved) if not resolved["root"] else build(args, resolved)
    emit_yaml(payload)
    return code


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo-root", default=".", help="Repository root (default: .)")
    parser.add_argument("--session", default=None, help="Host session id (default: most recent)")
    parser.add_argument("--transcript-root", default=None, help="Transcript directory, overriding host layout resolution.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Diagnostic reader for a bounded reviewer's final message. Not the delivery "
            "contract path: reviewers spawned without a host addressing/team name return "
            "their findings inline, and a result recovered here is a delivery failure to report."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    listing = subparsers.add_parser("list", help="List reviewer transcripts for a session.")
    _add_common(listing)
    listing.set_defaults(func=lambda args: _run(args, _list_payload))

    get = subparsers.add_parser("get", help="Return one reviewer's final assistant text block.")
    _add_common(get)
    get.add_argument("--agent", required=True, help="Reviewer name, agent type, or transcript id.")
    get.add_argument("--max-chars", type=int, default=_DEFAULT_MAX_CHARS, help=f"Cap on returned text (default: {_DEFAULT_MAX_CHARS}).")
    get.add_argument("--allow-partial", action="store_true", help="Return the last text block even when the transcript does not end on a finished turn.")
    get.set_defaults(func=lambda args: _run(args, _get_payload))

    args = parser.parse_args(argv)
    if getattr(args, "max_chars", 1) < 1:
        emit_yaml({"ok": False, "error": "--max-chars must be >= 1"})
        return 2
    try:
        return args.func(args)
    except ResultError as exc:
        emit_yaml({"ok": False, "error": str(exc)})
        return 2


if __name__ == "__main__":
    sys.exit(main())
