# Machine-Readable State

When a CLI mutates install, update, or support state, leave a trail that a
later agent can read directly.

Prefer:

- structured stdout for the current command
- durable local state for the last observed machine condition
- explicit paths for generated artifacts

Examples:

- JSON output from `doctor`
- lock files that record install/update/support results
- generated references or wrappers under a predictable directory

Manual-only flows still need structured state.

- record docs URL and notes
- record detect and healthcheck results
- record what remains for the operator

This lets a later agent continue from facts instead of rediscovering the host.
