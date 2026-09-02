# Goal Lifecycle

> Status: conditional — approved design target, not current implementation
> Source of truth: the active issue-native achieve goal and planning contract
> Last reviewed: 2026-08-26

This page answers one question: how should Charness model a long-running goal
from planning through provider-verified completion?

Until the integrated implementation, exported consumer proof, and live dogfood
are complete, this page describes the intended system. The source tree is in
transition; live #724 target pickup has a verified clean-process roundtrip, so
this page still makes no universal installed-consumer claim.

## Design Center

A long-running goal has two kinds of truth that should not share one mutable
document:

- planning truth is a complete local draft that becomes immutable after approval
- execution truth is the GitHub parent/sub-issue graph observed through the
  selected issue backend

The small record between them proves identity and integrity. The parent also
owns a small mutable execution cursor so a new session can enter the next child
with one read. The cursor is navigation state, not approval provenance or a
second event ledger; explicit sync/closeout remains responsible for full graph
reconciliation.

## Domain Model

| Concept | Owns | Must not own |
| --- | --- | --- |
| Goal Draft | research, decisions, critique dispositions, target architecture, approved child design, briefing | routine progress or current child state |
| Goal Binding | immutable approval identity, exact draft hash, parent identity, and initial approved work-item manifest/digest | observations, active/blocked/completion verdicts, percentages, mutable progress |
| Goal Run | shared execution scope, dependency order, completion policy, sparse contract changes | local planning history |
| Work Item | immediately executable capability contract and routine provider state | umbrella intent or unrelated integration work |
| Provider Observation | typed evidence of preflight, mutation, readback, partial outcome, or refusal | lifecycle policy or a second durable event ledger |

The Goal Run is a real GitHub parent issue. Every Work Item is a real sub-issue;
a Markdown link or checklist is not relationship proof.

## Authority By Phase

| Phase | Authority | Condition |
| --- | --- | --- |
| shaping | mutable Goal Draft | research and bounded interview are incomplete |
| reviewed | Goal Draft plus conditional docs and child specs | both critique rounds and final alignment are complete |
| approved | frozen Goal Draft | operator approved the exact briefing and initial manifest; provider may still be unavailable |
| binding | frozen Goal Draft and immutable V1 Goal Binding | exact parent identity is established or reused |
| bound | GitHub Goal Run plus verified graph | provider readback equals the approved graph exactly |
| active | fresh parent/child provider state | user invoked `/goal #N` and pickup validation passed |
| complete | provider-verified closed parent plus terminal proof | no child remains open or silently detached |

These names describe observed conditions. The binding does not carry a mutable
`phase` or `status` field.

## Planning And Approval

`achieve` first researches code, documentation, adapters, tests, tracker state,
and durable history. It accumulates one full Goal Draft and asks only questions
whose answers are consequential and not discoverable.

The adapter controls `interview.max_questions`; the default is 15. The ceiling
is shared by the initial interview and non-obvious findings from both critique
rounds. Each question supplies options, option-specific tradeoffs, a
recommendation, and its reason. Exhausting the ceiling with unresolved
consequential ambiguity stops planning.

Before approval, the workflow runs:

1. critique of framing, ownership, and architecture
2. conditional to-be documentation and executable child drafting
3. adversarial critique of the repaired whole
4. meticulous current-to-target alignment audit
5. briefing of purpose, target structure, execution order, and proof

Only an explicit approval of that briefing permits draft freeze or provider
mutation.

## Goal Binding

The canonical sidecar path replaces the Goal Draft's `.md` suffix with
`.binding.json`. Its schema id is `charness.goal-binding/v1`.

The complete canonical V1 JSON file is immutable and its SHA-256 is the approval
anchor. It contains:

- complete frozen-draft repository path and SHA-256
- final briefing digest, approval response identity, and approval observation
- exact parent repository, issue number, and canonical URL
- canonical key-sorted `approved_work_items`
- SHA-256 of the canonical work-item JSON representation
- deterministic execution rank and dependency keys for each initial Work Item

Each approved work item declares a stable key, create-or-reuse intent, existing
issue identity when known, dependency keys, execution rank, and body ownership.
Optional body-policy fields are retained only for compatibility with older
bindings. A child is identified by its Work Item marker and issue identity;
prose may be corrected without invalidating the run. Reused closed issues
retain `preserve-closed-evidence`, which protects state-owned evidence rather
than prose bytes.

A valid binding contains no observation references, progress, percentage,
current-child pointer, host-goal identity, provider-state cache, or copied
parent body.

Provider-less planning fallback creates no binding. After readiness and exact
parent readback, any frozen-draft, approval, parent, or initial-manifest change
requires explicit re-approval and a new binding. Unknown schema, missing files,
path escape, byte-hash mismatch, parent mismatch, binding-byte mismatch, and
initial-graph mismatch are typed refusals.

Provider observations are separate immutable
`charness.goal-run-observation/v1` receipts. Each binds the binding/draft/parent,
operation and attempt, target key/identity, before state, returned identity,
readback, outcome, and next action. This is bounded proof of one provider
attempt, not an event-sourced progress ledger.

## Parent Metadata

The Goal Run body contains exactly one machine-managed block beginning
`<!-- charness-goal-run:v1` and ending `-->`. Its interior is canonical JSON
with:

- binding schema, repository-relative binding path, and complete binding SHA-256
- frozen draft path and SHA-256
- initial graph SHA-256 and current provider membership
- mutable `progress` cursor: schema, revision, reconciled counts, and one exact
  next-child identity
- establishment and optional terminal observation path/SHA-256; terminal
  fields are written only after the immutable terminal receipt exists
- a planning-reset note when a provisional parent is being reconciled

The rest of the body is normal human-readable Markdown. During bootstrap, the
metadata block establishes the parent identity without binding surrounding
prose bytes. After the block exists, parent `update-body` preserves the
machine-managed identity and cursor; provider edit history owns reversible
prose changes. A consumer may carry the optional
`amendment_authorization_file` for a parent/binding identity, reason, and
explicit approval response/session/timestamp. The bound validator checks that
receipt only after reading the live body and before provider mutation. Duplicate,
malformed, foreign-version, stripped, or identity-mutated blocks refuse before
provider mutation.

## Activation And Pickup

The user-facing command is intentionally only:

```text
/goal #724
```

Issue-native pickup accepts only trimmed objective text matching
`^/goal[ ]+#[1-9][0-9]*$`. The host stores ordinary objective text. `achieve`
resolves the repository from an
explicit adapter identity or one unambiguous provider-compatible Git remote;
it never fabricates `<default-org>/<cwd-basename>`. It then asks the
adapter-resolved `issue` backend to read the exact `(repository, number)` and:

1. reads the parent and its managed metadata
2. reads and validates the Goal Binding and frozen Goal Draft
3. verifies parent ↔ binding ↔ draft identity
4. validates the establishment observation
5. reads the parent's managed progress cursor
6. enters the cursor's next executable child

The sidecar path is never entered by the user and no host-specific binding-file
parser is required.

The cursor is produced by bootstrap or explicit progress sync from the full
reconciler. It records an already-validated open child; pickup does not read
all child bodies or recompute dependency order. The binding retains rank and
dependency provenance for sync and closeout.

Pickup refuses with an actionable type for malformed objective, unresolved or
ambiguous repository, non-Goal-Run issue, invalid metadata, missing/mismatched
draft or binding, unestablished/invalid graph, missing/stale parent progress,
no next child, or closed parent. It never falls through to a local execution-
state fallback or a hidden full graph scan.

## Provider Operations

`issue` owns provider mechanics; `achieve` owns lifecycle policy and order.
Required issue-backend operations are:

- preflight adapter validity, binary/auth, exact repository, and the complete
  primitive capability closure needed by the planned operation
- read and byte-verify parent body
- update parent body and read it back
- create or reuse a child with exact identity
- list, add, and remove real sub-issue relationships with readback
- inspect exact parent and child state
- persist one typed provider-attempt observation
- close a Goal Run through a dedicated guarded operation

The provider implementation keeps those concerns on explicit seams:

- `issue_identity` proves the repository and issue named by provider answers;
- `issue_backend` renders and probes adapter-declared commands;
- `issue_json_pages` decodes provider JSON and pagination without policy;
- `issue_tracker_capabilities` proves the complete bootstrap operation set;
- `issue_tracker_discovery` owns Work Item discovery and source-bound child sets;
- `issue_tracker_relationships` owns real sub-issue reads and mutations;
- `issue_tracker_outcome` owns unresolved-write result shape;
- `issue_tracker` owns Goal Run metadata, child creation, and body update rules;
- `issue_tracker_cli` owns immutable observation orchestration,
  `issue_tracker_cli_preflight` owns read-only readiness, and
  `issue_tracker_cli_parser` owns only tracker command grammar;
- `issue_tool` composes command behavior while `issue_tool_parser` composes the
  tracker and ordinary issue command grammars.

The entrypoint re-exports established constants and call names for compatibility,
but state-changing behavior remains owned by the modules above. New provider
behavior extends its owning seam instead of accreting into the entrypoint.

Every mutation returns a typed Provider Observation: started, no write, verified
write, unverified write, or partial graph write. `no write` is legal only before
provider invocation. Missing, unavailable, and unknown readiness all refuse
before mutation. Alternate backends must declare every primitive explicitly;
command absence is not permission to improvise with another client.

## Reconciliation And Recovery

Graph establishment is resumable, not transactional. Before every mutation the
workflow re-reads current provider state and persists a bounded started attempt
with target/key/submitted digest. Already-correct objects are reused; only
missing or mismatched managed elements are changed.

| Observation | Claim allowed | Next action |
| --- | --- | --- |
| started | invocation may occur | never advance; collect the terminal observation |
| no write | provider was not invoked | repair readiness or input, then retry |
| verified write | exact intended object/relationship observed | continue to next manifest item |
| unverified write | provider may have changed | stop and re-read in a clean process |
| partial graph | named subset verified, remainder unresolved | preserve identities, re-read all, reconcile remainder |

Create-or-reuse uses a stable Work Item key in managed child metadata and
read-only provider discovery. If an invoked create has no discoverable identity,
the workflow stops for operator disposition and never retries create blindly.

Tests interrupt reconciliation after every mutation boundary and retry from a
clean process. Initial establishment succeeds only when exact child identities
and relationships equal the immutable initial manifest, not merely when counts
match.

An adapter may explicitly allow planning-only fallback when GitHub is
unavailable. Drafting, critique, docs, alignment, and briefing may continue;
neither parent nor binding is created, and activation, implementation, child
progress, and completion may not.

After establishment the GitHub parent owns current graph membership. An in-scope
new Work Item or deferral updates the real relationships and records an
approved parent-metadata amendment with an exact reason, successor mapping when
applicable, and provider observation. The immutable binding remains the initial approved
baseline. Objective, non-goal, success-criterion, or proof-policy changes require
explicit operator approval before the parent contract changes.

## Execution And Closeout

Routine execution enters the Work Item named by the parent cursor and follows
its own implementation/proof workflow. Closing a child is provider progress,
not behavioral proof; the child issue's closeout comment/provider receipt names
and binds the required evidence. The parent cursor advances with the published
transition; there is no second local child-acceptance ledger.

Parent body updates preserve the machine-managed identity and cursor contract;
prose edits are reversible and do not invalidate a run. An authorized bound
update may record a parent-metadata amendment with its identity, reason, and
approval. Bootstrap and later updates validate current and desired metadata
against the immutable binding, while provider readback proves the target
identity. One agent owns those updates;
optimistic concurrency is not part of the default model. Full graph
reconciliation remains explicit rather than running on every ordinary pickup.

A deferred child moves to a successor Goal Run with a durable reason and exact
remove/add readback. Merely unlinking it cannot make the current parent closable.

Every Charness-owned generic update or close/comment-close reads and parses the
target first. Generic update refuses to strip/alter Goal Run metadata; generic
close refuses before any comment or provider write. Only the dedicated close
operation may reach the internal close primitive. It:

1. reads every linked child
2. refuses any open child
3. verifies that every approved issue-owned closeout comment identity still
   exists on its child, including historical closed children
4. validates the separately bound final-proof index before provider selection;
   the index hash-binds the expected-child file, parent-obligation bytes, and
   role-labelled evidence artifacts selected by the Goal agent
5. persists the terminal attempt and closes the parent
6. performs distinct post-close provider readback
7. finalizes the immutable terminal observation
8. updates only mutable parent terminal metadata with its path/hash through
    the binding-aware update, and independently reads the still-closed parent
    back again

Comment-written/close-failed, close-invoked/readback-unknown, and
closed/readback-failed are distinct partial outcomes. A terminal metadata
update or its independent CLOSED readback is also a distinct
`unverified-write` outcome; it is not atomic with close. Retry reads first,
resumes close without posting a second comment when the prior receipt proves
the comment landed, and repairs terminal metadata without re-closing when the
provider now reads `CLOSED`. It never re-closes an already-closed parent. An
already-closed result is valid only when its
local terminal receipt pair is hash- and identity-verified. Failed exact
readback is `unverified`, never completion.

The close ingress validates artifact identity and byte binding, not the
Goal-specific meaning of CI, docs, or whole-system evidence. The agent running
the Goal owns that composition and records its selected artifacts in the
generic role-labelled index.

## Ownership And Portability

- `achieve`: Goal Draft/Binding producer; research/interview, critique
  orchestration, approval, graph policy/order, pickup, child selection, and
  closeout policy
- `issue`: provider identity, readiness, mutation, relationship, state, and
  guarded-close operations plus Provider Observation serialization
- Work Item capability owner: executable/verifiable child body; GitHub owns
  mutable state; implementing agent and guarded close consume it
- adapter: question ceiling, selected issue backend, repository resolution, and
  explicit planning-only fallback policy
- host: ordinary `/goal` objective persistence only
- `docs/`: evergreen vocabulary, authority, and operator path
- generated plugin placement: synchronized export of canonical skill sources,
  never an independent implementation

GitHub is an external declared capability. Local tests can prove schema,
planning, refusals, and fake-backend behavior; only provider roundtrip proves a
real graph mutation.

## Cutover And Removal

The existing mutable goal artifact currently owns planning, active/blocked
status, slice history, closeout, and host activation. The target does not add a
permanent issue-native branch beside it.

The cutover must:

- retain the full Markdown artifact only as Goal Draft and semantic provenance
- remove local status/slice mutation as execution coordination
- replace file-addressed activation guidance with `/goal #N`
- make Goal Run activation use the canonical Goal Draft producer instead of a copied template
- move active-goal consumers to parent/binding/provider identity
- keep evidence records linked to frozen draft provenance and Goal Run identity
- remove or explicitly mark unsupported old activation, progress, and completion
  paths

Other existing goal artifacts remain untouched and are not migration inputs,
supported runtimes, or acceptance constraints.

## Proof And Non-Claims

Implementation is not complete until all canonical and generated surfaces are
synchronized; deterministic schema/refusal/retry tests pass; a clean consumer
can execute from `/goal #N` and a child body; the provisional #724 graph is
reconciled and read back; conditional docs become honest current-state docs; and
fresh-eye review verifies the repaired proof surfaces.

This design does not claim concurrent-human merge handling, offline execution,
transactional provider writes, generic cross-host activation, legacy-goal
migration, or live GitHub success from fake-backend tests.
