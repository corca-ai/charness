# Codex Hooks Surface

- Source: https://developers.openai.com/codex/hooks
- Fetched: 2026-05-22 (WebFetch direct fetch; `gather_public_url.py` misclassified as login-wall)
- Access mode: direct public web fetch
- Use: design context for charness usage-episodes session tracking

## Available Lifecycle Hooks

| Hook | When | Notes |
|---|---|---|
| `SessionStart` | session begins (startup, resume, clear) | session-scoped, no `turn_id` |
| `UserPromptSubmit` | user submits prompt | turn-scoped |
| `PreToolUse` | before tool execution (Bash, apply_patch, MCP, etc.) | turn-scoped; matcher pattern |
| `PermissionRequest` | approval needed before tool execution | turn-scoped |
| `PostToolUse` | after tool completes | turn-scoped |
| `Stop` | conversation turn stops | turn-scoped; includes `last_assistant_message` |

## Notable Absence

- **No `SessionEnd` hook.** Codex doc explicitly does not list one. Session termination must be inferred from the absence of further `UserPromptSubmit` / `Stop` events, or by other means.

## Configuration Locations

- `~/.codex/hooks.json` — user-level JSON
- `~/.codex/config.toml` — user-level inline TOML
- `<repo>/.codex/hooks.json` — project-level JSON
- `<repo>/.codex/config.toml` — project-level inline TOML

## Payload Common Fields

All hooks receive on stdin (JSON):

- `session_id`
- `transcript_path`
- `cwd`
- `hook_event_name`
- `model`

Turn-scoped hooks additionally include:

- `turn_id`
- `permission_mode`

Event-specific extras vary:

- `PreToolUse`: `tool_name`, `tool_input`, `tool_use_id`
- `Stop`: `last_assistant_message`

## Config Format Example (TOML)

```toml
[[hooks.PreToolUse]]
matcher = "^Bash$"
[[hooks.PreToolUse.hooks]]
type = "command"
command = "python3 /path/to/script.py"
```

## Comparison with Claude Code

The Codex docs do not mention Claude Code. From repo prior knowledge, Claude Code uses `~/.claude/settings.json` and `<repo>/.claude/settings.json` for hook registration with comparable lifecycle events. Cross-host design implication:

- `SessionStart` exists in both hosts (rough symmetry).
- `Stop` (turn-stop) exists in both hosts.
- `UserPromptSubmit`, `PreToolUse`/`PostToolUse` exist in both hosts.
- `SessionEnd` absent in Codex (per this doc) — same gap as Claude Code historically had. Session boundary inference must rely on gap-based detection or explicit `Stop` aggregation.

## Captured vs Human Confirmation

- Captured: hook list, configuration paths, payload fields, config format.
- Not yet confirmed: exact JSON schema for each event, behavior under concurrent sessions, what happens when a hook script exits non-zero (cancel turn? warn?), permission boundary of hook scripts.

## Open Gaps

- Exact `hook_event_name` strings (e.g., is it `"SessionStart"` literal or some other form?). Confirm before wiring an emitter.
- Whether hook scripts can write to the same JSONL safely under concurrent turns/sessions. Likely fine if append-only with a lock, but unverified.
- Whether `session_id` is stable across `resume` of the same session (vs being a new id on each resume). Critical for session-grouping semantics.
- Codex hook discovery precedence when both `hooks.json` and `config.toml` define the same event — first-wins, both-run, or override?
