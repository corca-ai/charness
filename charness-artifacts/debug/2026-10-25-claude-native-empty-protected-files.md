# Debug: Claude native empty protected files
Date: 2026-10-25

## Problem

The real Haiku pilot returned `completed-needs-review`: fifteen unexpected empty
files appeared, and all three native Bash calls failed despite process exit 0.
Canonical receipt: `/tmp/charness/runtime/dfde85cabc08db6d/task-run/claude-haiku-proof-20261025/result.json`.

## Correct Behavior

Given a clean lane worktree, when native Claude executes a Bash command under the
outer sandbox, the command succeeds and leaves only intentional task changes.
The operator's home and shared Git administration remain protected.

## Observed Facts

All fifteen empty files share mtime `1792878561115395255`. They include `.env`
variants, package-manager configuration and lockfiles, and `.gitmodules`.
Sanitized tool-error classification identifies missing `socat`, required by the
native sandbox. The model edited documentation through Edit; parent completion
persisted its candidate. Native Bash did not commit it.

Prior memory `2026-09-12-issue-813-temp-output-ownership.md` distinguishes owned
runtime output from incidental worktree pollution. Upstream reports describe the
same filename burst: [46165](https://github.com/anthropics/claude-code/issues/46165)
and [51405](https://github.com/anthropics/claude-code/issues/51405).

The subsequent clean pilot returned `validated-partial-result`: two multiline
Python Bash calls were rejected before execution (`reject/config/mode`), while
simple commands were accepted (`accept/config/rule`). Native comparison
`/tmp/claude-native-permission-uizeppqc/summary.json` refuted replacing `Bash(*)`
with `Bash`: both rejected the same input. Removing only
`blockReadsOutsideWorkingDirectories` accepted it within unchanged OS confinement.

All three initial Codex preflights inherited HOME/CODEX_HOME; exact reviewer
identities matched three new real-home session files absent from the initial
snapshot. The private cleanup manifest is
`/tmp/claude-haiku-pilot-evidence/owned-review-session-cleanup.private.json`.
Workspace-trash refused those paths; all three files remain. Concurrent
`.claude.json` changes are unattributed; no global unchanged-home claim is made.

## Reproduction

Four clean temporary repositories exercised a two-by-two matrix: subprocess scrub
flag present/absent and `allowUnsandboxedCommands=false` present/absent. Each
snapshotted preparation, outer sandbox no-op, sandboxed Git query, and one real
native Bash invocation. Logs remain private; machine observations are under
`/tmp/charness-claude-native-boundary-matrix/*/observation.json`.

## Candidate Causes

- Charness preparation or private Git export creates files: disconfirmed; every
  pre-native phase produced zero files in all four cases.
- `allowUnsandboxedCommands=false` forces the native sandbox: disconfirmed;
  removing only this setting did not change the failure.
- `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` forces native sandbox initialization:
  confirmed by the independent matrix axis and native dependency errors.

## Hypothesis

Removing the redundant scrub flag, while retaining whole-process bwrap and the
auth proxy, permits native Bash without missing-dependency failures or ghost
files. Disconfirmer: either flag-absent matrix case still fails or creates files.

## Verification

Confirmed runtime/provider roundtrip, Claude 2.1.302, model `claude-haiku-5-5`:

| Scrub flag | Strict setting | Bash calls/errors | New files |
| --- | --- | --- | --- |
| present | present | 1/1 | 17 |
| present | absent | 1/1 | 17 |
| absent | present | 1/0 | 0 |
| absent | absent | 1/0 | 0 |

The minimal repositories lack two files already present in the pilot, explaining
seventeen versus fifteen new files. Parent integration now passes 135 tests. The final isolated lane completed
with a clean docs-only commit, hooks and VERIFY; private reviewer storage was
observed before normal retention. See the [pilot proof](../impl/2026-10-25-claude-executor-pilot.md).

## Root Cause

Pattern: a flag presented as credential scrubbing also enables mandatory native
Linux sandboxing. Pattern of patterns: local safety mechanisms were composed
without exercising their combined live tool behavior. The no-tool auth probe
and direct outer-sandbox tests both passed while the first native Bash failed.

Why it arose: the helper set a native flag whose side effects exceeded its name.
The parent auth proxy already keeps genuine credentials outside the child, so
this second sandbox was redundant. Native initialization prepared protected-path
placeholders before refusing the missing dependency. Why caught late: fake events
and a tool-free native request cannot observe Bash startup. Why fixed late: the
first actual tool invocation occurred in the final pilot; matrix isolation
resolved attribution within this investigation without installing dependencies
or deleting evidence.

## Invariant Proof

- Invariant: native Bash must work inside the mandatory outer OS boundary without
  changing the worktree merely to initialize a second sandbox.
- Producer Proof: `configure_claude_environment` now removes the native flag,
  including inherited values.
- Final-Consumer Proof: both flag-absent native matrix cases execute Bash and
  retain zero new files.
- Interface-Shape Sibling Scan: outer bwrap, native Bash startup, auth transport,
  and private Git import were independently observed.
- Non-Claims: no arbitrary upstream filename classification or native internal
  implementation is inferred; the original polluted pilot is retained.

## Detection Gap

- invocation-local environment unit test | asserted the problematic flag was set
  | assert it is absent even when inherited.
- native auth probe | disabled tools | require a real Bash result and clean-tree
  observation in pilot acceptance.
- final receipt | correctly refused clean completion | subject-defect; preserve
  the verifier instead of ignoring generated files or cleaning them blindly.

## Sibling Search

- Mental model: independently safe settings compose without operational effects.
- same layer: inherited scrub flag in environment configuration | decision: same
  bug, fix now | proof: runtime/provider roundtrip.
- abstraction up: auth proxy plus native safety flag | decision: same class,
  diagnostic-only for this slice | proof: proxy tests and live request; removing
  the redundant flag leaves genuine auth outside the child.
- specialization down: `allowUnsandboxedCommands=false` | decision: intentional
  plain-text or non-rendering boundary | proof: matrix disconfirmed causality.
- cross-file: `task_run_claude_auth.py` and `task_run_execution.py` | decision:
  intentional plain-text or non-rendering boundary | proof: parent-side auth
  context and mandatory OS command wrapper remain unchanged.

## Seam Risk

- Interrupt ID: claude-native-empty-protected-files
- Risk Class: external-seam
- Seam: native Claude Bash startup to lane filesystem
- Disproving Observation: a real Bash command succeeds with zero incidental files
- What Local Reasoning Cannot Prove: behavior of a future native CLI release
- Generalization Pressure: factor-now

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-10-25-claude-native-sandbox-composition.md

## Prevention

Fewer next time: use one whole-process sandbox and parent-owned auth transport;
remove redundant native activation flags at the environment owner. Earlier next
time: the inherited-flag regression catches reintroduction cheaply, and real
acceptance requires successful native Bash plus clean-tree readback.

Scoped critique: removing scrubbing would be unsafe with real child credentials;
the proxy substitutes a disposable token before process creation, while bwrap
continues to constrain every tool and hook. Counterweight: installing socat or
suppressing incidental files would retain redundant isolation and hide the
composition error. Preserve original evidence and rerun a fresh real lane.

The narrower composition repair removes the redundant read-boundary setting;
Read/Edit denials and OS credential masks remain. Claude-selected preflights now
use runtime-owned private HOME/CODEX_HOME and XDG/temp roots, inherit only needed
auth with mode 0600, and remove shell startup overrides. The subsequent OS
invocation masks that reviewer home after granting runtime writes. Tests cover
executor selection and the real mask; final acceptance must locate the new
review session privately with no corresponding real-home file. Other executors
retain their behavior. The original detection gap covered the main executor
but omitted its auxiliary writer; the same home invariant now names both.
