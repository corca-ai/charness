# Planning evidence only: current open-issue Goal Run architecture

Date: 2026-08-30 (Asia/Seoul)

This is a read-only planning memo. It creates no Goal Draft, binding, execution
tracker, or GitHub mutation. The recommendation is to reuse #744 as the Goal Run
parent after explicit approval and exact provider reconciliation.

## Evidence boundary

The selected repo backend is `gh` (`corca-ai/charness`), resolved from
`.agents/issue-adapter.yaml`. `issue_tool.py read` was run for every requested
issue with `comments_read: true`; the read path reports the comment counts below.
This memo does not make a stronger pagination-completeness claim than that
backend read contract. `docs/goal-lifecycle.md`, `docs/operating-contract.md`,
`docs/parallel-execution.md`, the Codex host notes, and the prior close-all-open-
issues goal artifacts were also read.

## Exact activation snapshot

All fourteen requested issues were `OPEN` in the 2026-08-30 read. Timestamps are
provider `updatedAt` values in UTC; labels are the observed labels.

| issue | title | updatedAt | comments | labels |
| --- | --- | --- | ---: | --- |
| [#709](https://github.com/corca-ai/charness/issues/709) | summarize()'s new_doc_family_count is pinned only on the arm that returns zero | 2026-08-23T05:01:30Z | 0 | — |
| [#731](https://github.com/corca-ai/charness/issues/731) | Reduce bounded-review friction and make partial worker progress first-class | 2026-08-26T11:38:42Z | 0 | feature request, operations |
| [#744](https://github.com/corca-ai/charness/issues/744) | Umbrella: consolidate Charness repository analysis into a typed Rust core | 2026-08-28T09:41:24Z | 0 | operations, enhancement |
| [#748](https://github.com/corca-ai/charness/issues/748) | Migration: retire duplicated Python repository-boundary owners through the Rust core | 2026-08-28T13:09:34Z | 1 | enhancement |
| [#749](https://github.com/corca-ai/charness/issues/749) | Follow-up: reduce and type-check retained Python after native-core migration | 2026-08-28T03:07:49Z | 0 | Future Work, enhancement |
| [#751](https://github.com/corca-ai/charness/issues/751) | Critique reviewed-path packets can omit all semantic review input | 2026-08-28T04:43:00Z | 0 | bug |
| [#752](https://github.com/corca-ai/charness/issues/752) | worktree prepare can skip declared setup when doctor does not cover dependency readiness | 2026-08-28T06:25:40Z | 0 | bug, operations |
| [#753](https://github.com/corca-ai/charness/issues/753) | Prune the test corpus with graph and mutation evidence: meta-layer concentration and change-detector pins | 2026-08-28T09:40:50Z | 0 | operations, test |
| [#756](https://github.com/corca-ai/charness/issues/756) | Split the backend boundary out of `reviewer_worker_runtime` | 2026-08-29T10:21:10Z | 0 | enhancement |
| [#758](https://github.com/corca-ai/charness/issues/758) | Mutation test regression on main | 2026-08-29T12:41:21Z | 0 | mutation-test |
| [#759](https://github.com/corca-ai/charness/issues/759) | A change range containing deletions cannot be declared as bounded-review input | 2026-08-29T13:52:55Z | 0 | bug |
| [#760](https://github.com/corca-ai/charness/issues/760) | No gate asserts the two changed-path enumerators agree | 2026-08-29T23:30:12Z | 0 | — |
| [#761](https://github.com/corca-ai/charness/issues/761) | Submodule identity binding is unprobed in dirty, nested, and absent-directory states | 2026-08-30T01:20:09Z | 1 | — |
| [#762](https://github.com/corca-ai/charness/issues/762) | A committed critique packet inside a range cannot be declared through the default path | 2026-08-29T23:30:47Z | 0 | — |

Observed comment facts: #748's one comment records a landed first migration slice,
but leaves `repo_file_listing.py` and `surfaces_lib.match_surfaces` deferred behind
consumer release/artifact and `CHARNESS_SUPPORT_DIR` decisions. #761's one comment
records eight review rounds and says nested submodules, conflicted index entries,
and a gitlink in a non-`HEAD` tree remain unprobed; it explicitly points remaining
precision at a real consumer repository.

## Existing graph and local state

The exact `list-sub-issues` read for #744 returned seven direct children, `4`
closed, `3` open, `57%` complete:

- closed: #743, #745, #746, #747;
- open: #748, #749, #753;
- every returned child carried `parent_issue_url` for #744.

Recommended graph ownership is therefore:

```text
#744  (reuse as Goal Run parent)
├─ existing nested children: #748, #749, #753  [do not reparent]
├─ existing direct Work Items: #709, #751, #752, #756, #759, #760, #761, #762
└─ new managed successor Work Items for source issues: #731, #758
```

The four already-closed children remain historical graph members. No Markdown
link substitutes for the real relationships. The proposed successor items have
no issue numbers yet and must not be created in this planning pass.

Before this memo was written, the clean local branch had `HEAD=86d867381`,
`origin/main=dc77742f2`, and ten commits ahead of `origin/main`:

```text
e59bc71e7 submodule deleted from disk must not crash identity construction
dd0b4d17a fall back only for an absent checkout, not for any OSError
e2b892a01 record the #759 resolution review and strengthen its control
455c553b4 fix: a failure is not a state, and an index gitlink is not a checkout
ded8eac8c a read failure is not a deletion, and a deletion carries its mode
c62120c68 refuse a dirty submodule, and see a staged gitlink removal
fde9c7f96 an unestablished cleanliness check is not a clean submodule
6dac81127 the deletion marker must mean what the identity binds
86d867381 a directory is not a record, and exists() follows a symlink
```

These are implementation/review history around #759/#761, not issue closeout
proof. The memo commit itself is intentionally excluded from this ten-commit
snapshot.

## Classification and Work Item disposition

| issue | classification | recommendation |
| --- | --- | --- |
| #709 | bug: missing non-zero projection proof; current code is reported correct | reuse as direct Work Item |
| #731 | feature/deferred workflow capability; four separable worker concerns | preserve as source issue; close only after a new managed Work Item decomposition is created and read back |
| #744 | consolidated architecture umbrella | reuse as the Goal Run parent, not as a child |
| #748 | deferred migration feature | keep nested under #744 exactly as-is |
| #749 | deferred retained-Python/type-boundary work | keep nested under #744 exactly as-is |
| #751 | bug: false-ready semantic review packet | reuse as direct Work Item |
| #752 | bug: false-ready worktree preparation | reuse as direct Work Item |
| #753 | deferred quality/test-corpus work | keep nested under #744 exactly as-is |
| #756 | behavior-preserving structural refactor | reuse as direct Work Item |
| #758 | bug/report: mutation run was unmeasured collateral, not a mutation result | preserve as source issue; close only after a new managed Work Item owns baseline/collateral repair |
| #759 | bug: deletion-containing ranges are undeclarable | reuse as direct Work Item; current local repairs still owe proof and provider closeout |
| #760 | bug: two changed-path answers can drift | reuse as direct Work Item |
| #761 | deferred probe/decision: unprobed submodule states | reuse as direct Work Item with explicit live-consumer boundary |
| #762 | decision-needed friction: exact manifest exists but default refusal is opaque | reuse as direct Work Item |

For #731 and #758, “source issue” means provenance is retained and the source is
not declared fixed merely because a successor exists. A future close must use an
explicit superseded/not-planned disposition, successor identity, exact parent
relationship readback, and source-preservation evidence. No source issue is
closed in this memo.

## Generative dependency DAG and lanes

The sequence is a dependency hypothesis, not an execution tracker:

```text
#752 ───────────────► all consumer-facing implementation/proof lanes
#756 ──┐
#751 ──┼────────────► managed #731 successor(s)
#752 ──┘

#760 ───────────────► #759 ───────────┬──► #761
                                     └──► #762

#709 ──┐
#758 successor ─────┴───────────────► #753 ──┐
#748 ───────────────────────────────────────┴──► #749

#744 parent closeout waits for every direct, nested, and successor Work Item.
```

Parallel partition after the read-only parent preflight:

1. **Native/test lane:** #748 can proceed because #746/#747 are closed. Repair
   the #758 mutation-baseline signal and #709's non-zero summary proof in
   parallel; then #753; then #749 after #748 and #753.
2. **Worker lane:** #752 establishes honest consumer setup readiness. #756 and
   #751 may be authored in disjoint isolated worktrees, then serially integrated;
   their combined result enables the #731 successor decomposition.
3. **Reviewed-input lane:** #760 first establishes one changed-path answer;
   #759 then proves deletion-range binding; #761 and #762 can follow in parallel,
   with #761's real-consumer proof remaining a separate pause.
4. **Parent lane:** the parent owns graph reconciliation, generated/export sync,
   integrated verification, and final closeout; it does not delegate a shared
   index, generated mirror, or provider cursor.

## Cluster acceptance and proof

- **#709/#758/#753 test and mutation cluster:** #709 requires a non-zero
  `new_doc_family_count` and value-checked sample. #758 is not closed from the
  existing `UNMEASURED` report: sampler failure, skipped mutation, and missing
  Stryker output must be separated. #753 accepts deletion only when graph
  inventory, mutation evidence, and retained behavioral proof agree; its prior
  island census is structural, not deadness proof. Proof is the focused fixture,
  a genuinely executed mutation run, before/after behavior, and no ratio-floor
  weakening.
- **#748/#749/#744 native-core cluster:** #748 must finish the deferred inventory/
  matcher ownership and consumer artifact boundary while deleting absorbed Python
  owners and preserving plugin/source parity. #749 must produce a role-based
  retained-Python census, narrow type-check boundary, CLI compatibility proof,
  and non-ratchet metrics. #744 closes only after exact real sub-issue graph,
  child evidence, docs reconciliation, and parent readback all agree.
- **#752/#756/#731/#751 worker cluster:** #752 must distinguish doctor health
  from per-command preparation readiness. #756 must preserve behavior while
  separating backend command/normalization from lifecycle/receipt ownership.
  #751 must make every hash-bound reviewed path semantically reachable. #731's
  successor must prove typed accepted/running/partial/timed-out/interrupted/
  terminal states, process-group cleanup, preflight guidance, and that partial
  output is never approval. Proof is fresh consumer fixtures, timeout/no-descendant
  observation, schema/identity validation, and source/plugin parity.
- **#760/#759/#761/#762 reviewed-input cluster:** #760 needs agreement fixtures
  for merge commits, staged-vs-worktree deletion, non-ASCII paths, renames, and
  submodules. #759 needs range-bound deletion records/pre-image hashes and a
  negative control against the weaker prepared-for path. #761 needs the remaining
  state matrix and a real consumer boundary for the strong claim. #762 needs an
  actionable default refusal or an explicitly reconciled sweep, while preserving
  exact-manifest range binding. Proof must be input-bound and clean-process;
  current local code and a `CLOSED` state are not sufficient.

Every issue gets its own carrier, behavior verdict or typed non-claim, and
provider readback. Shared implementation is allowed; shared closeout evidence is
not.

## Explicit pauses

- **Provider pause:** before any Goal Run bootstrap, re-read #744 and the exact
  graph, run `issue_tool.py tracker-preflight --repo corca-ai/charness --number
  744`, and obtain approval of the frozen plan. Create successor items and add
  only the proposed direct relationships; never remove or reparent #748/#749/#753.
  Each provider operation needs a typed attempt and exact readback. An unavailable
  or unverified provider stops activation; there is no local execution fallback.
- **Push pause:** this memo does not push the ten local commits, create a PR, or
  publish. A future run may use one final authorized push only after integrated
  carriers, focused proof, generated sync, and the relevant quality gate are
  locked. Push exit status is not remote-CI proof.
- **Live-proof pause:** issue state/readback proves tracker state only. Remote CI,
  installed consumer behavior, native artifact distribution, external analyzer
  availability, and live submodule behavior require their own observer/channel.
  In particular, #748/#749 owe consumer/release-boundary evidence, #758 owes a
  real workflow result, and #761 owes a real consumer with submodules. If that
  proof is unavailable, leave the item open or record a typed non-claim.

## Risks and non-claims

- #744 is an existing umbrella, not yet a verified Goal Run with binding metadata;
  reuse is recommended, not observed.
- The old close-all-open-issues artifacts are planning history, not scope: the
  2026-06-01 run established matrix/carrier discipline; the 2026-08-05 17-issue
  plan and 2026-08-06 eight-issue draft are stale snapshots; the 2026-08-07
  19-issue plan reinforces root-before-consumer and instrument-before-decision.
  None authorizes silently reviving their issue sets.
- The local #759/#761 repair chain is valuable premise evidence, but it does not
  prove issue closure, remote CI, consumer installation, or live provider state.
- `git diff --check` passed. The read-only docs composite did not establish a
  clean result because this checkout has no generated `plugins/` mirror and the
  existing `docs/host-packaging.md` link therefore fails; the artifact-surface
  preflight likewise reports no registered validator for the `design-studies`
  family. No docs-wide green claim is made.
- No claim is made that all comments were exhaustively paginated beyond the
  backend read result, that synthetic tests establish consumer behavior, or that
  fewer tests/lines/issues is inherently better.
- No Goal Draft, Goal Binding, execution tracker, new issue, issue comment, issue
  relationship, issue close, push, PR, release, or other external mutation was
  performed.
