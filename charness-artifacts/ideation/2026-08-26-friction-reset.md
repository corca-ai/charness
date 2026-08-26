# Goal Amendment Proposal: Charness Friction Reset

Status: approved-active-amendment; execution amendment for Goal Run #724
Date: 2026-08-26
Source of truth: the five issue records in
`../gather/2026-08-26-charness-new-issues-728-732.md`, current source, and
`docs/design-north-star.md`

## Reason for the amendment

The approved #724 goal assumed that more explicit issue-native planning,
provider binding, and child-graph bookkeeping would improve execution. Issues
#728–#732 are new counter-evidence. Across reviewer lifecycle, file-backed
review, adapter bootstrap, partial worker progress, and prove cadence, the
operator is paying more ceremony than the protected risk warrants. Charness is
currently optimizing for auditable procedure on ordinary local work instead of
helping a capable developer finish it.

This proposal changes the goal direction before any further #724 graph or
provider mutation. The old approved goal remains byte-for-byte historical
planning evidence; this document is the proposed replacement/amendment.

## Findings from #728–#732

1. Reviewer preflight failure, worker timeout, delivered `block`, and partial
   progress are different states, but their distinction is buried in a large
   carrier/ledger path. The safety need is a truthful terminal state, not the
   ceremony used to construct it (#728, #731).
2. File-backed review asks the operator to hand-assemble packet hashes,
   identities, paths, capability envelopes, ledgers, receipts, and carriers.
   These should be derived from a small semantic input at one command boundary;
   identity and approval checks must remain (#729).
3. Sixteen public skills carry separate adapter init/resolve/example surfaces
   totalling 3,487 lines. The repeated bootstrap contract is platform ceremony,
   not sixteen distinct product capabilities (#730).
4. `prove` unconditionally records critique for every task-completing slice, and
   `critique` defaults to multiple angle workers plus a counterweight. This
   makes reversible cleanup and local repairs pay an irreversible-boundary cost
   (#731, #732).
5. The issue-native slice already added 9,143 lines and 63 files in one commit.
   That is not proof that all of it is wrong, but it is strong evidence that
   adding more tracking machinery before measuring capability parity would
   deepen the failure.

## Goal direction

Make Charness a fast development aid whose default path is judgment-led and
small. The goal is to remove or collapse workflow machinery until a normal
local change has one obvious command path and one honest closeout, while
retaining teeth only where a wrong answer escapes the editable session.

### Candidate deletions or collapses

These are deletion candidates, not yet executed:

- Remove the unconditional `prove` critique obligation for reversible local
  edits. Permit `Critique: not-required <reason>` when no objective authority,
  durability, external-write, security, release, compatibility, or proof-
  surface boundary is crossed.
- Replace the default multi-angle-plus-counterweight review with one risk
  decision. Escalate only when the changed surface crosses a named boundary;
  do not recursively review removal of review machinery.
- Collapse file-backed worker preparation into one semantic-input command and
  one typed lifecycle carrier. Keep process-group cleanup, timeout truth,
  partial-result non-approval, subject identity, and explicit authority at the
  boundaries that need them.
- Replace sixteen skill-local adapter bootstrap paths with one optional,
  manifest-driven shared lifecycle, or remove bootstrap ceremony where no
  adapter is needed. Existing valid configuration must remain a no-op; invalid
  or conflicting configuration must refuse clearly.
- Suspend the #724 31-child graph, binding sidecar, and planned provider work
  until the friction reset proves they are needed. Do not turn #728–#732 into
  five more bureaucracy-shaped children.
- After a consumer census and capability-parity proof, retire obsolete
  issue-native planning/binding code and artifacts. A line-count reduction by
  itself is not an acceptance criterion.

### Safety that remains

The reset does not remove the north-star boundary. Retain a distinct observer
and a distinct evidence channel for external writes, issue/PR closure, release,
push/tag, installed-host mutation, deletions, and authoring or changing proof
surfaces. Retain typed process cleanup and ensure a partial worker result can
never become approval. These are cliffs, not ordinary friction.

## Proposed execution order

1. Freeze the current #724 external state and stop creating the binding or
   children; record the new issue cluster as a goal requalification.
2. Measure a small baseline: commands, manual inputs, wall time, and failure
   states for a trivial local edit, a reversible cleanup, and one high-risk
   boundary.
3. Implement the risk-adaptive prove/critique cadence and its truthful
   `not-required` disposition.
4. Simplify the file-backed worker carrier while preserving the safety facts
   listed above.
5. Consolidate or delete adapter bootstrap paths after testing valid,
   invalid, absent, and unestablished configuration.
6. Run a consumer census; delete obsolete #724/binding artifacts only after
   their consumers and replacement capability are proven.

Each deletion of a proof surface or policy requires one bounded fresh-eye
review before the deletion is accepted. Ordinary reversible edits do not
inherit that review requirement. No push, release, tag, installed-host
mutation, issue closure, or remote CI mutation is part of this proposal.

## Success criteria

- A trivial local edit can run focused verification and close with either a
  concise proof or a truthful `Critique: not-required` reason, without packet,
  carrier, or multi-worker ceremony.
- A high-risk boundary still has a distinct observer, distinct evidence channel,
  explicit authority, and a readback/non-claim record.
- A file-backed run can be started from semantic inputs in one command and
  returns a typed state that distinguishes preflight refusal, not-started,
  started timeout, partial progress, and delivered verdict.
- Valid adapter configuration is cheap and idempotent; absent optional
  configuration does not block ordinary work.
- The measured normal-path setup and closeout cost is materially lower, with no
  loss of the retained boundary capabilities.

## Operator decision

- Decision: approved for inclusion in the current Goal Run #724.
- Exact operator response: `이번 골에 포함 잘 시켜서 진행`.
- Observed: 2026-08-26 Asia/Seoul.
- Scope: requalify the goal around #728–#732 and execute the deletion-first
  friction reset described here.
- First implementation slice: risk-adaptive `prove`/`critique` cadence.
- Boundary: no GitHub graph reconciliation, issue mutation, push, release,
  tag, remote CI mutation, or installed-host mutation until the first slice and
  its capability-parity review complete.
- Historical integrity: the approved frozen Goal Draft remains unchanged;
  this file is the active execution amendment and does not rewrite that
  planning snapshot.

## Current implementation contract: ownership cutover

### Current slice

Move the default closeout decision for ordinary reversible work from mandatory
`critique` execution to judgment owned by `prove`. `prove` records deterministic
verification plus either `Critique: not-required <reason>` or an explicit
high-risk review result. `critique` remains available as an explicit owner for
named risk boundaries; this slice does not invent a second risk engine.

### Fixed decisions

- Reversible local edits, cleanup, typing, tests, and ordinary documentation
  changes do not require fresh-eye execution by default.
- External writes, issue/PR closure, release/push/tag, installed-host mutation,
  deletion, proof-surface authoring, and shared/public contract changes remain
  high-risk boundaries with their existing evidence owners.
- A blocked required review remains a typed block; it is never silently turned
  into approval. `not-required` is valid only with a reason naming the boundary
  classification.
- Do not change the reviewer result schema, process cleanup, identity binding,
  or partial-result non-approval in this cutover.
- Update the source skill/docs surfaces and their checked-in plugin mirrors
  together. Do not update `docs/handoff.md`, the frozen Goal Draft, GitHub, or
  installed-host state as part of this slice.

### Acceptance checks

- `skills/public/prove/SKILL.md`, `skills/public/critique/SKILL.md`, their
  cadence/review-gate references, `docs/operating-contract.md`, and
  `docs/implementation-discipline.md` all describe risk-adaptive ownership and
  no longer state an unconditional critique obligation for every local slice.
- The source/plugin pairs are synchronized and the contract tests assert the
  new `not-required` path plus the retained high-risk boundary language.
- Focused public-skill contract tests and the documentation composite gate pass;
  no reviewer process is invoked for this implementation by operator scope.
- The closeout records this slice as locally verified only: no external,
  installed, hosted, GitHub, or fresh-eye proof is claimed.

### Explicit non-goals

- Do not implement the file-backed one-command worker or the 16-adapter
  consolidation in this same cutover; they remain the next ownership moves
  after this contract is exercised.
- Do not reconcile the #724 issue graph or create/update/close issues.

## Implementation evidence: ownership cutover

Date: 2026-08-26 Asia/Seoul

The first cutover is implemented. `prove` now owns the closeout risk decision:
ordinary reversible local work records deterministic proof and
`Critique: not-required <reason>`; selected authority, durability, external,
security, release, compatibility, install/update, deletion, migration, and
proof-surface boundaries retain an explicit review owner. The old universal
task-completing critique and multi-slice midpoint obligations were removed
from the current operating contract. The proof-surface verdict-logic second
round rule remains conditional on that boundary actually being changed.

Changed truth surfaces are synchronized in source and checked-in plugin form:

- `skills/public/{critique,impl,prove}/`
- `plugins/charness/skills/{critique,impl,prove}/`
- `docs/operating-contract.md`
- `docs/implementation-discipline.md`
- `scripts/check_skill_contracts.py` and its plugin mirror
- `tests/quality_gates/test_critique_skill.py`

The file-backed worker carrier, adapter bootstrap paths, reviewer result
schema, process cleanup, identity binding, and partial-result non-approval
were not changed in this cutover. #724 graph/provider state, GitHub, push,
release, tags, remote CI, installed-host state, and `docs/handoff.md` were not
changed by this slice.

## Closeout status

- `Implemented`: risk-adaptive prove/critique ownership cutover.
- `Capability Delivered`: ordinary reversible work can close on deterministic
  proof with an explicit `Critique: not-required <reason>` disposition; named
  high-risk boundaries still route to their owning review surface.
- `Contract Source`: this amendment's `## Current implementation contract:
  ownership cutover` and the retained north-star boundary in
  `../../docs/design-north-star.md`.
- `Verification`: focused standing pytest `99 passed`; skill contract
  validator passed; changed-skill core-headroom preflight passed; the explicit
  changed-path boundary probe returned `state: evaluated`, `triggered: false`;
  source/plugin parity and `git diff --check` passed.
- `Lint Gate`: `ran-pass bash scripts/check-docs.sh`; the full-tree
  `bash scripts/check-secrets.sh` found one redacted gitleaks finding in the
  existing dirty population and is recorded as `ran-fail-deferred` pending
  path attribution. The staged cutover scope passed
  `gitleaks protect --staged`; no target-scope leak was found. The commit hook's
  final `check_boundary_bypass_ratchet` is also `ran-fail-deferred`: its one new
  candidate belongs to the pre-existing unstaged
  `tests/quality_gates/test_python_length_gates.py` and
  `scripts/check_python_lengths.py` changes, not this cutover's 17-file index.
- `Truth Surface Sync`: source skill/docs surfaces and checked-in plugin
  mirrors are synchronized; no handoff or frozen-goal rewrite was made.
- `Boundary Ownership`: `moved-to-owner` — `prove` owns the risk disposition;
  `critique`, `issue`, and `release` retain their selected high-risk boundary
  ownership.
- `Critique`: not-run operator-directed exception; this slice changes a
  proof-surface policy, so no fresh-eye review is claimed. The user explicitly
  directed that forced fresh-eye, handoff update, and micro-slice execution be
  omitted for this cutover.
- `Contract Updates`: removed universal closeout review and midpoint review
  taxes, added the typed `not-required` disposition, and kept the explicit
  high-risk and proof-surface paths.
- `Residual Risks`: the whole dirty-tree secret finding is not attributed yet;
  the pre-existing boundary-bypass candidate prevents a verified commit until
  its owner resolves it; the follow-on provider, lineage, worker-carrier, and
  adapter cuts are implemented-uncommitted, while the census still has open
  ownership rows; no live, hosted, installed, or external-boundary proof is
  claimed.
- `Next Slice`: continue from the provider-selected child after the follow-on
  ownership cutovers recorded below; do not recreate a five-issue ceremony for
  #728–#732.

## Follow-on implementation update

Date: 2026-08-27 Asia/Seoul

The amendment's deletion-first direction was carried into the approved #724
Goal Run without rewriting the frozen draft or `docs/handoff.md`:

- #726 now owns the file-backed Goal Run provider boundary; #727 owns clean
  `/goal #N` pickup; #733 owns the shared `goal_lineage` identity; #729 owns
  semantic-input review setup and its typed lifecycle carrier.
- #730's 16 public adapter entrypoints share one first-use lifecycle with
  absent/valid/invalid/unestablished states, dry-run, idempotent no-op, force,
  safe target resolution, and one YAML receipt. Skill-specific fields remain
  local rather than being falsely collapsed.
- Obsolete local tracker-receipt and closeout-normalizer bridges, the removed
  top-level `goal check` CLI path, and its stale compatibility test were
  deleted. Generic CLI help now uses `/goal #N`; direct artifact validation, when
  needed, names its actual helper path.
- Local proof, live issue readback, source/plugin sync, skill/docs gates, and
  evaluator coverage are recorded in the two implementation closeouts linked
  from the current goal run. Forced fresh-eye review, handoff mutation,
  issue closure, push, release, tag, remote CI, and installed-host mutation
  remain explicitly unclaimed under the user-directed execution mode.
