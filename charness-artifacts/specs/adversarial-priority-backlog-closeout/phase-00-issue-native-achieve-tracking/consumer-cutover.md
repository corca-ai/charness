# Goal Consumer Cutover Map

Status: draft planning contract
Goal: [issue-native backlog closeout](../../../goals/2026-08-26-adversarial-priority-backlog-closeout.md)
Target architecture: [conditional goal lifecycle](../../../../docs/goal-lifecycle.md)

## Inventory Boundary

The original four-token census was too narrow. The final classifier must inspect
active source, adapter, root/operator docs, generated placements, and tests for
both structural and semantic old-path signals:

```bash
git grep -n -E 'charness-artifacts/goals|goal_path|Status: active|append_slice_log|/goal @|running[- ]memory|single durable|living scratchpad|goal_artifact_template|auto_draft_goal|draft_goal_from_chunk|chunked_routing_auto_draft' HEAD -- README.md .agents docs scripts skills plugins tests
```

On `HEAD` `9c32398c9`, the expanded declared scope contains 122 files mentioning
the goal directory, 65 `goal_path`, 32 `Status: active`, 17
`append_slice_log`, 66 `/goal @`, 7 running-memory/single-durable/living-
scratchpad claims, and 31 producer/template signals. These sets overlap and are
topology measurements, not defect counts.

The unapproved working-tree prototype is not the source of truth. Generated
`plugins/charness/` placements follow their canonical `skills/` or `scripts/`
owner and are verified after synchronization; they are not separate design
decisions.

## Identity Rule

Every consumer must choose one of three identities explicitly:

- semantic provenance: frozen Goal Draft path plus SHA-256
- execution identity: exact Goal Run `(repository, issue number)` plus binding
  path and approved-graph digest
- provider truth: fresh parent/child/relationship observation

No consumer may infer active execution from file presence or `Status: active`.
No consumer may append progress to the frozen Goal Draft.

## Producer And Consumer Map

| Family | Current owning surfaces | Target disposition | Required proof |
| --- | --- | --- | --- |
| Goal Draft creation | `skills/public/achieve/scripts/upsert_goal.py`, `goal_artifact_template.md`, `goal_artifact_scaffold.py`, `goal_artifact_lib.py` | reshape into the one mutable-before-approval Goal Draft producer; freeze complete bytes after approval | one canonical schema/template; create, edit-before-freeze, freeze/hash, and post-freeze refusal tests |
| Duplicate handoff producer | `skills/public/handoff/scripts/draft_goal_from_chunk.py`, `chunked_routing_auto_draft.py`, `templates/auto_draft_goal.md`, chunked-routing references | call the canonical Goal Draft producer/schema; remove copied lifecycle template/renderer | fixture proves handoff output validates identically and no second template owns required fields |
| Draft validation | `check_goal_artifact.py`, `goal_artifact_*` validators, `goal_cli_args.py`, `goal_path_portability.py` | retain planning-shape checks that belong to Goal Draft; replace pursue/status/complete verdicts with binding and Goal Run checks | changed-line tests plus cold validation of draft, binding, mismatch, and unsupported legacy activation |
| Local execution mutation | `append_slice_log.py`, `normalize_goal_closeout.py`, status setters and closeout mutation helpers | remove as execution coordination; child issue state and child-owned proof carry progress | no supported command or skill path writes active/blocked/slice/completion state into a frozen draft |
| Public achieve flow | `skills/public/achieve/SKILL.md`, `references/lifecycle.md`, `references/lifecycle-{before,during,after}.md`, `references/goal-artifact.md`, `references/coordination.md` | replace artifact-as-running-memory with draft → approval/binding → GitHub graph → `/goal #N` pickup | deterministic clean-repo fixture follows the new path without prototype knowledge |
| Active-goal coordination | `skills/shared/references/active-goal-coordination.md`; references in `impl`, `quality`, `critique`, and `issue` | resolve current Goal Run from host objective and binding; read provider state; preserve only frozen draft provenance | each adjacent workflow receives exact parent/child identity and refuses ambiguous or stale local state |
| Adapter policy | `.agents/achieve-adapter.yaml`, `skills/public/achieve/adapter.example.yaml`, `achieve_adapter_policy.py`, adapter contract | own positive integer question ceiling, selected issue backend, repository resolution, and explicit planning-only fallback only | missing/thin/valid/invalid adapter tests; unset differs from explicitly invalid |
| Issue provider boundary | `skills/public/issue/scripts/issue_backend.py`, `issue_tool.py`, adapter example and backend reference | own exact read/update/create/reuse/list/link/unlink/state and dedicated guarded Goal Run close | fake backend typed observations plus live #724 readback only in authorized dogfood slice |
| Premise records | `scripts/premise_preflight_lib.py` and callers | retain Goal Draft provenance; add exact Goal Run/Work Item identity where the premise belongs to execution | stale/mismatched draft hash and wrong issue identity refuse before behavioral claims |
| Slice manifests | `scripts/slice_manifest_lib.py`, `validate_slice_manifest.py`, closeout bundle callers | bind a slice to one Work Item and frozen draft provenance; stop using mutable goal status | manifest roundtrip and wrong-parent/wrong-child negative tests |
| Retro persistence | `scripts/retro_persistence_lib.py`, `skills/public/retro/scripts/persist_retro_artifact.py`, `validate_retro_handoff_wiring.py` | preserve immutable draft provenance and bind retro to Goal Run/Work Item; do not mutate the draft | deterministic identity validation and terminal receipt linkage |
| Closeout evidence | `scripts/closeout_bundle.py`, `final_bundle_preflight_evidence.py`, achieve closeout helpers, prescribed closeout docs | child closeout remains child-owned; parent completion uses issue-owned guarded close plus terminal observation | open-child, detached-deferral, post-close-readback-failure, and exact success cases |
| Host metrics | `scripts/host_log_probe_lib.py`, achieve metric helpers | treat host goal timing as optional evidence keyed to Goal Run; do not make it binding state | missing host metrics remain an explicit non-claim, not a lifecycle refusal |
| Release claims | `skills/public/release/scripts/claims_review_scope.py` and release closeout surfaces | retain frozen target/provenance; use Goal Run only when release claims are an in-scope Work Item | existing release proof floor remains independent of child CLOSED state |
| Root/CLI/operator docs | `README.md`, `docs/cli-reference.md`, `docs/workflow-routes.md`, `docs/readme-proof.md`, `docs/artifact-policy.md`, `docs/prescribed-skill-closeout-contract.md` | document draft/binding/graph separation and `/goal #N`; generated CLI docs follow the implemented command owner | docs graph and deterministic installed operator-reading fixture |
| Handoff docs | `docs/handoff-chunked-routing.md` and handoff skill references | describe Goal Draft creation only; never claim activation or execution authority | cold handoff-to-draft-to-approval scenario |
| Tests and fixtures | `tests/quality_gates/test_goal_*`, `test_achieve_*`, handoff fixtures, `tests/charness_cli/test_goal_helpers.py`, coverage-debt fixtures | replace tests that enshrine mutable runtime state; retain historical fixtures only when explicitly compatibility-scoped | scenario matrix covers new positive path and every typed refusal; no old-path test is silently skipped |

## Change Ownership

The inventory is whole-repository evidence, not one catch-all implementation
child:

- `goal-binding-v1` owns Goal Draft creation/validation and the handoff producer.
- `goal-run-provider` owns issue backend operations and provider observations.
- `achieve-orchestration` owns public achieve flow, adapter policy, active-goal
  coordination, local execution-path removal, and operator route docs.
- `goal-evidence-lineage` owns premise, slice, critique/prove, retro, closeout,
  host-metric, and release lineage plus the final classifier.
- each canonical owner synchronizes its generated placements and current docs;
  the dogfood child proves the integrated live path.

When the classifier finds a defect, it blocks and routes the row to that owner;
the evidence-lineage child does not acquire permission to edit unrelated
surfaces merely because it owns the census.

## Removal Set

The following concepts have no supported target path:

- local `Status: active` or `Status: blocked` as execution authority
- `/goal @<goal-file>` activation for issue-native goals
- Goal Draft as slice log, percentage, current frame, or completion verdict
- minimal receipt replacing the full draft
- current-versus-legacy dual lifecycle in the public skill
- implicit backend fallback when required GitHub operations are absent

Historical files remain readable repository contents. This goal does not migrate
or rewrite them.

## Cutover Order

1. land Goal Draft/Binding schemas and validators without activating a run
2. land issue-owned provider operations and typed observations
3. land achieve approval, reconciliation, and `/goal #N` pickup
4. bind execution-evidence consumers to full Goal Run/Work Item lineage while
   each behavioral owner removes its old execution reader/writer
5. synchronize each owner's generated plugin placements and docs
6. run the classifier and route every residual defect to its owning child
7. prove clean-repo, clean-process, and authorized #724 dogfood paths

The old execution path is removed only in the same coherent change set that
makes every supported consumer use the new identity. A temporary implementation
branch may exist within an unmerged slice, but no completed child may leave two
documented runtime authorities.

## Completeness Check

The evidence-lineage child creates `scripts/classify_goal_consumers.py`. It emits
a machine-readable receipt with every matching path/line, owning family,
classification (`draft-provenance`, `goal-run-identity`, `provider-truth`,
`generated-mirror`, `historical-fixture`, or `defect`), rationale key, and
source/generated pairing. Before implementation closeout, run the classifier
over the expanded scope; any unclassified or `defect` row blocks. Raw grep and
counts are discovery evidence only.
