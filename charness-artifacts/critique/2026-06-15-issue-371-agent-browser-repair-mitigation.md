# Issue #371 agent-browser repair mitigation critique

## Verdict

mitigation-valid-release-blocked.

`charness tool repair agent-browser` is shaped as downstream recovery, not a
#371 closure proof. The current diff runs the existing
`scripts/agent_browser_runtime_guard.py --cleanup-orphans` path and refreshes
doctor state; it does not prove invocation-bound teardown for normal
completion, cancellation, provider failure, or timeout, and it does not prove
`agent-browser-chrome-*` profile directory lifecycle ownership.

Do not close #371 from this bundle. It can ship only as an operator mitigation
after the generated/plugin surface drift is synchronized and the operator output
makes the mitigation boundary explicit.

Evidence reviewed:

- `git diff -- charness docs/generated/cli-reference.md scripts/render_cli_reference.py tests/charness_cli/test_tool_lifecycle.py`
- `./charness tool repair --help`
- `./charness tool repair --repo-root . --json specdown`
- `./charness tool repair --repo-root . specdown`
- `./charness tool repair --repo-root . --json agent-browser`
- `./charness tool repair --repo-root . agent-browser`
- `pytest -q tests/charness_cli/test_tool_lifecycle.py -q`

## Act Before Ship

- Sync the checked-in plugin/install surface before any release or push
  closeout. The focused lifecycle suite fails during installed-plugin setup
  because `validate_packaging.py` reports drift at
  `plugins/charness/scripts/render_cli_reference.py` and instructs running
  `python3 scripts/sync_root_plugin_manifests.py`. This is release-blocking
  because installed Charness users would not receive the generated CLI reference
  change consistently.

- Add an operator-visible mitigation caveat to the repair output or command
  help before using this as the #371 follow-up. The current clean-state text says
  `REPAIR: preview (preview)`, `DOCTOR: ok`, and `NEXT: agent-browser is ready`;
  the JSON likewise reports readiness. That is correct for doctor state, but it
  does not remind the operator that profile-dir teardown remains upstream and
  unproven. Add a stable JSON/text field or next-step sentence such as
  "runtime repair is post-hoc mitigation only; invocation-bound Chrome/profile
  lifecycle remains upstream/unproven."

- Re-run the lifecycle test after plugin sync. The current run shows the new
  repair command paths passing far enough to expose the packaging drift, but the
  full file is not green until the installed-plugin fixture can initialize.

## Bundle Anyway

- The command boundary is appropriately narrow. `REPAIRABLE_TOOL_IDS` contains
  only `agent-browser`, unsupported tools return a structured
  `repair.status: unsupported`, and the unsupported JSON/text UX is clear.

- The implementation uses the existing owned cleanup path instead of inventing
  a second reaper. `_repair_agent_browser` calls
  `agent_browser_runtime_guard.py --cleanup-orphans --json`, appends
  `--execute` only when requested, and then runs doctor with `--write-locks`
  only for execution.

- Root generated CLI docs include `charness tool repair`, and
  `scripts/render_cli_reference.py` now renders that help surface. Once the
  plugin mirror is synced, the generated-doc shape is acceptable.

- The added tests cover preview, execute, unsupported tools, and doctor
  next-step preference from runtime cleanup drift. That is enough to support a
  mitigation release after the blocking sync/output-caveat items are addressed.

## Over-Worry

- It is not necessary for this mitigation command to prove normal completion,
  cancellation, provider failure, and timeout teardown. That proof is required
  to close #371, not to ship an explicit post-hoc recovery command.

- It is not a defect that `repair` does not support every external tool. A
  scoped repair registry is safer than a generic command that implies Charness
  owns lifecycle repair for tools it only detects.

- It is not necessary to add profile-directory deletion to this command unless
  Charness can prove ownership of the exact profile lease. Cleaning arbitrary
  `agent-browser-chrome-*` directories would risk converting an upstream
  lifecycle gap into a local unsafe deletion surface.

## Valid But Defer

- A real #371 fix still needs an invocation-owned handle, host lifecycle hook, or
  upstream `agent-browser` fix that proves both the process tree and matching
  profile directory are torn down at invocation end.

- A more precise no-op status would improve UX. In a clean `--execute` run, the
  command can currently report `executed` even when no target PIDs existed. That
  is not a release blocker for mitigation, but `noop` would be easier to reason
  about.

- The JSON `repair.command` field is joined with spaces and is not shell-quoted
  for paths containing spaces. Treat it as diagnostic display for now; quote it
  later if operators are expected to copy/paste it.

- Add explicit tests for failed post-doctor and `init_reap`/reparented guidance
  when this command becomes the main operator recovery path. The current code
  appears to preserve the guard's next-step guidance through `tool_next_step`,
  but the edge is not locked by tests.

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated.

I was directly assigned as the bounded fresh-eye resolution reviewer and did
not spawn nested reviewers. I used read-only git inspection plus non-mutating CLI
help/preview checks and a focused pytest run. I did not run mutating git
commands and left unrelated worktree state alone.

## Reviewer Tier Evidence

- requested tier: default
- requested spawn fields: inherited parent model and reasoning settings
- host exposure state: host-defaulted
- application state: this reviewer was directly assigned as the bounded
  fresh-eye resolution reviewer; no nested spawn was requested.

## Disposition

- Act Before Ship: plugin/install surface sync fixed by running
  `python3 scripts/sync_root_plugin_manifests.py --repo-root .`; the generated
  plugin mirror now includes `plugins/charness/scripts/render_cli_reference.py`,
  and `validate_packaging.py` plus `validate_packaging_committed.py` pass.
- Act Before Ship: mitigation boundary UX fixed. `charness tool repair
  agent-browser` now carries a stable `repair.caveat` JSON field and text
  next-step language: runtime repair is post-hoc mitigation only, while
  invocation-bound Chrome/profile teardown remains upstream/unproven.
- Re-run: `pytest -q tests/charness_cli/test_tool_lifecycle.py` passed after
  sync and caveat updates.

Resolution: release blocker cleared for the mitigation. #371 remains open.
