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


The invocation must omit `permissions.blockReadsOutsideWorkingDirectories`:
Claude 2.1.302 rejected otherwise-allowed multiline Python in `dontAsk` with this
setting, while removing only the setting allowed the identical native probe.
`Bash(*)` remains the broad rule; changing it to bare `Bash` did not fix the
failure. Credential-file masks and the whole-process OS boundary remain the
security owners; interpreter commands cannot write outside the lane/runtime.

Auxiliary Codex preflight is part of the Claude lane's home-safety boundary.
For Claude-selected lanes only, it gets a runtime-owned private HOME/CODEX_HOME,
XDG and temp roots. It may inherit authentication with mode 0600, but not host
configuration, plugins, sessions or shell startup overrides. The subsequent
Claude invocation must mask that reviewer home after granting runtime writes.
Acceptance locates the review session under its private CODEX_HOME and confirms
no corresponding session in the real home. Earlier owned review sessions are
eligible only for exact-identity cleanup; never infer ownership from timestamps
or clean shared session databases. Do not claim a globally unchanged home when
concurrent writers were observed.
