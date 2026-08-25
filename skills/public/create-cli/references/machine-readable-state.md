# Machine-Readable State

When a CLI mutates install, update, or support state, leave a trail that a
later agent can read directly.

Prefer:

- structured stdout for the current command
- parseable YAML by default for Charness-style agent-first commands, with full
  evidence behind `--detail`; human-first and third-party CLIs keep their
  explicit native machine mode. Keep chatter or progress on stderr while the
  command is still running
- durable local state for the last observed machine condition
- explicit paths for generated artifacts
- enough provenance to tell which runtime binary actually handled the command
- enough host state to tell whether the installed host-visible copy matched the
  exported source

Examples:

- structured output from `doctor`
- lock files that record install/update/support results
- repo-local task envelopes that record claim/submit/abort state for bounded
  agent work
- generated references or wrappers under a predictable directory
- user-scoped version provenance plus last successful update-check metadata
- user-scoped managed-install registries for explicitly tracked repos or local
  surfaces when an aggregate `update all` path needs opt-in fan-out
- host-state snapshots that separate source version, runtime capability, and
  installed host copy when those can drift

Manual-only flows still need structured state.

- record docs URL and notes
- record detect and healthcheck results
- record what remains for the operator

This lets a later agent continue from facts instead of rediscovering the host.

For agent task envelopes, keep the contract deliberately small:

- `claim` should refuse to overwrite a task already owned by another agent or
  already closed
- `submit` should include a summary or one opaque result-carrier pointer
- `review` may record the parent-owned verdict, but must not create a nested task or subagent
- `abort` should require a reason
- `status` should be read-only and structured

Do not turn this into a scheduler unless the repo already has real queue
semantics to preserve.
