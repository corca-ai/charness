# Claude native sandbox composition

Status: current acceptance handoff

The Claude executor uses mandatory whole-process bwrap and a parent-side auth
proxy. Native Bash, file tools, and hooks inherit the OS write boundary. Genuine
auth stays outside the child's files, environment, and PID namespace.

`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` must be absent, including inherited values: in
Claude 2.1.302 on Linux it forces an additional native sandbox and its dependency
initialization despite `sandbox.enabled=false`. The flag is redundant once the
proxy substitutes auth and the process is already isolated.

Acceptance requires a fresh real task lane to execute a successful native Bash
command, edit documentation, commit on its task branch with hooks enabled, emit
VERIFY and a full report, and produce a terminal clean result.json. Check the
worktree for untracked and ignored incidental files; process exit 0 alone does
not establish tool success. Retain failed pilots as evidence without speculative
cleanup. The tiny branch remains unlanded.

Diagnosis and measured discriminator: [debug record](../debug/2026-10-25-claude-native-empty-protected-files.md).
