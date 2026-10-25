# Claude Git discovery contract

Task-run linked worktrees use ordinary Git discovery. Native mode discovers the
existing linked `.git`; private mode overlays a read-only `gitdir:` pointer in the
sandbox namespace. No process-wide GIT_DIR, GIT_WORK_TREE or GIT_COMMON_DIR is
exported to Claude. Private preparation/finalization may target private metadata
for one Git invocation. Explicit mode metadata selects finalization without
reusing Git discovery overrides, including a private-to-native continuation.

Acceptance: real Git under both sandbox profiles reads a foreign repository by
cwd and -C, commits to the intended task Git, preserves host main, and finalizes
private commits. One bounded a405 Claude native readback must distinguish host
and task HEAD. No new dispatch refusal or product mutation.

## Critique

Pointer source and destination must both be read-only; protecting only the mounted
`.git` leaves a writable source alias. Existing ancestor mounts prevent replacement.
Native finalization must skip stale private identity. Tests exercise stale marker
continuation. Independent review found no blocker. Real native Claude readback distinguishes task and host HEAD; both foreign cwd and -C agree with independent host observation. Evidence: ../debug/2026-10-25-claude-git-discovery.md.
