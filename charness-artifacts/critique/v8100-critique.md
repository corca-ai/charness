# Release Critique — charness v8.10.0 (minor)

- **Kind**: `charness.release-critique` (v1)
- **Prepared for**: v8.10.0-release
- **Scope**: `91ce106e4..HEAD` — #831 typed scope-closure disposition
  (`scope_warnings`, `scope_extension_request`, `rescope_result`, repeated
  `./` normalization, frozen directory matches); #832 lane-env secret scrub
  (secret-pattern names dropped from the lane child env, per-executor auth
  keeps, `CHARNESS_TASK_RUN_KEEP_SECRET_ENV` override, names-only receipt).
- **Reviewers**: three fresh-eye parallel reviewers (operational-safety,
  contract-readability, security) + parent synthesis; read-only, no repo
  mutation
- **Lane evidence**: release lane green, 89 passed, 0 failed
  (`./scripts/run-quality.sh --full --read-only --release` on the final
  staged tree; 4 not-run entries are opt-in-unmet, named in the summary).

Fresh-eye satisfaction: parent-delegated three angle reviewers plus synthesis

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `read-only shared checkout; structured concerns`
- **Host exposure state**: `host-defaulted`
- **Application state**: `three angle reports delivered with concerns triage`
- **Delivery state**: `findings-received`
- **Execution mode**: `typed-subagent`

## Release Scope

v8.10.0 ships two lane-hardening slices. #831: a lane can finish a coherent
behavior seam with a reviewable disposition — preflight/dry-run receipts
carry `scope_warnings` for exact scopes matching no base-tree path, a
scope-mismatch `BLOCKED` lane records a typed `scope_extension_request`
whose next step re-validates the same candidate with the approved addition
(`rescope_result`) instead of relaunching; refresh never admits
lane-created directories as scope roots. #832: the lane child env drops
secret-pattern names (`API_KEY`, `_TOKEN`, `SECRET`, …); codex keeps
`OPENAI_API_KEY`, muse keeps none (stored credentials); the receipt records
scrubbed/kept names, never values.

## Surface-Lock Inventory

- `scripts/task_run/{scope,plan,py,lane_runner,completion_next_step,support,runtime}.py`
- `docs/agent-task-runs.md` (scope-closure + secret-scrub paragraphs, page
  kept under the 1000-word budget by displacing verbose prose)
- `tests/charness_cli/test_task_run_scope_closure_831.py`,
  `tests/charness_cli/test_task_run_lane_env_832.py`
- `plugins/charness/scripts/task_run/*` (generated mirror, synced)
- `packaging/charness.json` + host plugin manifests (publish-time bump+sync)

## Concerns

### Act Before Ship

None. All three reviewers returned ship with no act-before-ship items.

### Watch (accepted residuals)

1. **File-union admits lane-created descendants under `**` globs**
   (safety). For a declared glob such as `pkg*/**`, a lane-created path
   that literally matches the pattern is unioned on refresh — pre-existing
   declared-pattern behavior, pinned by
   `test_glob_scope_freezes_matches_and_allows_new_matching_files`. Only
   the directory-prefix widening is frozen. The refresh comment now states
   both halves precisely.
2. **`requested_paths` from lane-controlled text is unvalidated** (safety).
   Harmless today (display-only, never auto-applied; `rescope_result` has
   no production caller and takes only operator-supplied scopes), but an
   operator copy-pasting the suggestion could be talked into an overbroad
   scope. The next-step guidance says approve-or-refuse explicitly.
3. **Codex keeps `OPENAI_API_KEY` in the lane env** (security). Required
   for codex auth; the key still reaches codex's own process tree. Muse
   lanes carry no secret-pattern names at all. Residual recorded, not
   hidden.
4. **Marker-collision guidance noise** (safety). Any blocker containing the
   scope-mismatch marker yields a request plus an extra next-step sentence.
   No scope effect; acceptable for a warning-only channel.

### Noise

- `resolve_task_inputs` runs one extra `ls-tree` per resolution; negligible.
- `scope_closure_warnings` covers only `exact` specs; unmatched globs
  already raise at resolve time.
- Docs diff includes prose tightening to satisfy the docs-length budget.

## Boundary Ownership

- **Producer**: release critique reviewers (angle findings plus synthesis)
- **Consumer**: release publisher (`publish_release.py --execute`) and operators
  reading the release notes
- **Owning surface**: `charness-artifacts/critique/v8100-critique.md` (this
  record); scope-verdict logic owned by `scripts/task_run/task_run_scope.py`,
  lane env owned by `scripts/task_run/task_run_runtime.py`, wording owned by
  `docs/agent-task-runs.md`
- **Verdict**: `owned-correctly`

## Bump Rationale

minor, not patch: alongside the #831 behavior repair and the #832 leak
fix, the release adds operator-facing surface (preflight `scope_warnings`,
receipt `scope_extension_request`/`lane_env` fields, `rescope_result`
helper, `CHARNESS_TASK_RUN_KEEP_SECRET_ENV`) that existing users adopt
without migration.

Read-only review; no files modified by reviewers.
