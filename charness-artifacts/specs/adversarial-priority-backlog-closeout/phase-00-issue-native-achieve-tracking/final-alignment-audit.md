# Final Alignment Audit: Issue-Native Achieve

Status: complete planning audit — implementation not authorized
Audited: 2026-08-26
Goal: [full Goal Draft](../../../goals/2026-08-26-adversarial-priority-backlog-closeout.md)
To-be docs: [Goal lifecycle](../../../../docs/goal-lifecycle.md)
Child graph: [proposed children](./children/index.md)

## Audit Question

If every proposed child is implemented as written, will the resulting domain
model, architecture, design, code ownership, docs, and operator path form one
coherent system rather than an issue-native branch bolted beside the mutable
local-goal system?

## Inputs Compared

- current `HEAD` achieve, issue, handoff, active-goal coordination, evidence,
  adapter, generated-export, test, and documentation surfaces
- the expanded [consumer map](./consumer-cutover.md), including `.agents`, root
  docs, canonical sources, generated placements, and tests
- all nine confirmed interview decisions
- both critique packets and their framing/ownership/operability/provider/
  counterweight findings
- the conditional evergreen model and all five system child specs
- fresh provider audits of the 26 reused issue identities and the
  [readiness contract](./existing-work-item-readiness.md)
- the provisional #724/#725–#727 graph as external evidence, not authority

## Model Integrity

| Question | Result | Evidence and disposition |
| --- | --- | --- |
| Are concepts minimal and stable? | pass | Goal Draft, Goal Binding, Goal Run, Work Item, and Provider Observation each answer one different question. Binding no longer owns observations or progress. |
| Is mutable truth single-owned? | pass | GitHub parent/child state is the only routine execution truth. Draft and binding freeze; observations prove attempts without becoming a progress ledger. |
| Is planning-only fallback honest? | pass | It creates no parent placeholder or binding and cannot activate, implement, progress, or complete. |
| Can initial approval coexist with later discoveries? | pass | Binding fixes the approved initial graph; verified in-scope amendments/deferrals change parent membership. Semantic purpose/success/proof changes require reapproval. |
| Is completion stronger than issue state? | pass | Each child must expose issue-owned behavioral evidence or a verified successor transfer; guarded parent close rejects state-only closure. |
| Is the user surface minimal? | pass | The only activation input is exact `/goal #N`; repository, metadata, binding, graph, and child selection are resolved internally with typed refusals. |

## Ownership And Dependency Audit

| Capability | One owner | Downstream consumers | Boundary result |
| --- | --- | --- | --- |
| Goal Draft and immutable binding | `goal-binding-v1` | handoff, orchestration, evidence lineage | one producer; no copied handoff template or provider state |
| Provider identity/mutations/observations/close | `goal-run-provider` | orchestration and dogfood | issue backend owns mechanics; achieve owns policy/order |
| Planning, approval, graph policy, pickup, active coordination | `achieve-orchestration` | impl/quality/critique/issue workflows | no host parser and no direct provider client in achieve |
| Premise/slice/review/retro/closeout/host/release lineage | `goal-evidence-lineage` | guarded close and final proof | bounded evidence owner; classifier routes foreign defects back |
| Live #724 composition | `dogfood-724-establishment` | operator and future runs | does not absorb any system capability or backlog implementation |

The earlier broad consumer-cutover child failed this audit because it owned
handoff, orchestration, evidence, docs, exports, and integration at once. The
final graph returns each mutation to its natural owner and leaves the evidence
child only the shared lineage type and completeness classifier.

## Transition Audit

The generic path is complete and monotonic:

1. mutable researched draft
2. bounded questions and two critiques
3. conditional to-be docs, executable child design, alignment, briefing
4. explicit approval and frozen draft
5. exact parent readback and immutable initial binding
6. resumable provider reconciliation and verified establishment
7. exact `/goal #N` pickup and child-owned progress/proof
8. verified graph amendments or successor deferrals
9. guarded close, post-close readback, terminal metadata readback

Every provider invocation has a started/verified/unverified/partial result;
`no-write` is reserved for pre-invocation refusal. Ambiguous create stops after
read-only discovery and cannot create again blindly. Generic update cannot
strip managed metadata and generic close cannot cross the Goal Run boundary.

## First-Dogfood Bootstrap Audit

The first design had a circular dependency: #724 could become authoritative
only after provider/binding/pickup were built, while those capabilities were
supposed to execute as #724 children. The repaired plan makes the exception
explicit and temporary:

1. after approval, already-linked #726 implements only minimum graph primitives
   with local/fake-backend proof;
2. those primitives reconcile all approved #724 bodies and relationships and
   record `pending-target-roundtrip`;
3. GitHub child state then owns routine progress, but target pickup remains
   blocked;
4. after all four system capabilities are proven, the target commands re-read
   and reconcile the same graph, replace the marker with verified
   establishment, and prove clean `/goal #724` pickup.

This does not enter adapters, evergreen docs, or later runs. Direct ad hoc REST,
prototype success claims, and implementation of any other child before the
bootstrap graph are not allowed.

## Child Executability Audit

- All five system children state purpose, current/target state, owner,
  dependencies, implementation contract, acceptance criteria, exact target
  commands, adversarial stimuli, docs impact, closeout evidence, and non-claims.
- The 23 open reused issues receive managed executable addenda derived from the
  approved readiness rows and focused proof map. Their exact desired body bytes
  are materialized and hashed after approval but before the binding is created;
  premise drift stops for reapproval.
- Closed #721, #694, and #628 remain linked only with exact issue-owned closeout
  evidence and explicit channel limits. Their bodies are not falsely claimed as
  managed equality.
- An incomplete or stale child can exist in provider history but cannot pass
  establishment or selection.
- The final graph has 31 direct children—five system capabilities and 26 reused
  identities—and no catch-all implementation child.

## Current-To-Target Cutover Audit

The current mutable local artifact spreads execution authority through public
achieve instructions, handoff's duplicate producer, active-goal coordination,
premise/slice/retro/closeout records, adapters, docs, tests, and generated
exports. The target removes that seam rather than preserving a dual reader:

- binding owns canonical Goal Draft production and handoff
- orchestration atomically replaces public lifecycle, active coordination,
  adapter behavior, operator routes, local status/slice writers, and old pickup
- provider replaces direct or incomplete graph mutation paths
- evidence lineage binds durable proof without changing each workflow's domain
  ownership
- each canonical owner synchronizes generated code and current docs
- the classifier audits the whole topology and routes defects; it is not a
  semantic proof by token absence

Other goal files are ignored and untouched. They create no migration,
compatibility, or acceptance dependency.

## Documentation Audit

`docs/goal-lifecycle.md` owns one question, is explicitly conditional, names
its source of truth, and covers vocabulary, authority, planning, binding,
activation, provider recovery, graph evolution, closeout, ownership, removal,
and proof boundaries. It is reachable from `docs/index.md`. Promotion to
`current` is blocked until implementation, clean-consumer proof, and live #724
readback agree.

`bash scripts/check-docs.sh` passed after the planning changes: Markdown,
internal/plugin links, command docs, graph reachability, and internal link checks
had zero errors. It reported 20 existing advisory inline-code warnings outside
the new goal-lifecycle page. `git diff --check` passed for the planning surfaces.
These checks prove structure, not architectural truth; this audit supplies the
semantic comparison.

## Residual Risks And Stop Gates

| Risk | Containment |
| --- | --- |
| Current provider cannot support the minimum bootstrap slice | stop before graph mutation; do not improvise another client |
| Existing issue body/premise drifts after approval | fresh read, exact fingerprint, and reapproval on semantic drift |
| Create succeeds but identity/readback is uncertain | persist unverified result, discover read-only, never recreate blindly |
| Bootstrap is mistaken for target success | explicit marker; pickup and dogfood close remain blocked until target roundtrip |
| Round-2 repair introduces a new defect | no third review is claimed; changed verdict surfaces owe implementation-time fresh-eye review, and provider verdict logic owes the repo-required second repaired-surface round |
| Broad quality passes while relevant proof skipped | changed-line and focused proof run first; skipped gates remain skipped, not passed |
| Docs are promoted early | conditional status is an acceptance gate tied to integrated proof |

## Audit Verdict

Ready for the operator briefing, not for implementation by implication.

No unresolved consequential architecture choice remains. The final deterministic
repair was the one-time #724 bootstrap sequence. It follows the already-approved
requirements that GitHub be the sole execution tracker, the local draft remain
frozen planning evidence, and this goal be the first dogfood case. Question use
therefore remains 9 of 15, with 6 unused.

This verdict does not authorize or claim implementation, GitHub mutation,
commit, push, release, issue closure, live provider success, clean installed
consumer behavior, or target `/goal #724` pickup.
