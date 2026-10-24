# Claude task executor

> Status: current
> Source of truth: `scripts/task_run/task_run_claude_sandbox.py` and `task_run_claude_auth.py`
> Last verified: 2026-10-25

`charness task run --executor claude --effort medium` runs `claude -p` with
`claude-haiku-5-5`. Effort stays orchestration metadata; the model is pinned.
The default executor remains Codex. The host currently requires Linux bubblewrap.
No extra host-state writable grants are accepted for Claude.


Claude lanes keep the same result/report, branch, hooks, progress and verification
contracts. Stream JSON remains in `claude.events.log`; terminal text becomes the
report, and steers resume the observed session. The process runs with the lane
worktree as its current directory.

The Claude adapter wraps the entire process in a filesystem sandbox, supplies
per-invocation permission settings, and isolates home/config/cache state under
the private execution runtime. Only the worktree and private runtime are writable.
Private Git storage allows normal commits and hooks without granting the agent
writes into the parent repository; the trusted runner imports the task branch
after execution. Real home configuration and credential files remain protected.
Real provider credentials stay in a parent-side proxy; the child receives an
invocation token. Credential-shaped workspace files are masked from shell reads
as well as denied to file tools. The safety and real-lane evidence record states
the tested host boundary.

Credential masks cover known `.env*`, `.pem`, `.key` and credential filenames,
not arbitrary secret-bearing content. The API proxy forwards only to the fixed
Anthropic HTTPS upstream and requires its per-invocation placeholder token.

The trusted importer reads a no-follow bundle byte copy, verifies its prerequisites
and ancestry, and updates only the current task branch. Hooks stay enabled on
lane commits inside the sandbox. Host metadata import disables hooks and fsmonitor
so agent-edited hook files cannot escape the filesystem boundary during import.

The [task-run contract](./agent-task-runs.md) owns completion and retention.
