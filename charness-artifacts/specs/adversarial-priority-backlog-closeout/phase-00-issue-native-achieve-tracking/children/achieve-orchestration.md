# Child: Orchestrate Research Through `/goal #N` Pickup

Status: proposed executable spec
Proposed disposition: rewrite and reuse `corca-ai/charness#727` after approval
Target docs: [Goal lifecycle](../../../../../docs/goal-lifecycle.md)

## Purpose

Make `achieve` own one comprehensible lifecycle: research and draft, bounded
decisions, two critiques, to-be design, alignment and briefing, explicit
approval, verified graph establishment, then simple `/goal #N` pickup.

## Current State

The current public skill shapes a local artifact and later treats that same file
as running memory. It asks a few high-leverage questions but has no shared hard
ceiling or structured option/tradeoff/recommendation contract. `/goal` pursuit
expects a file path. The prototype adds some interview and tracker behavior but
creates the parent too early and reduces the full draft to a receipt.

## Target State

The public skill remains one concept: operating a long-running auditable goal.
It coordinates `ideation`, `spec`, `critique`, `issue`, `impl`, `prove`,
`quality`, and `retro`; it does not absorb their engines. Host and repository
specifics stay in adapters or the issue backend.

## Owning Surfaces

- `skills/public/achieve/SKILL.md` and lifecycle/coordination references
- achieve adapter example, resolver, and policy module
- interview, approval, graph-plan, establish, pickup, and active-child helpers
- shared active-goal coordination consumed by adjacent workflows
- maintained public-skill dogfood/scenario record
- synchronized `plugins/charness/` export and focused tests

## Dependencies

- proven Goal Draft/Binding V1 capability
- proven issue-backend Goal Run operations
- adapter-resolved current repository and issue backend
- existing standalone critique and implementation/proof workflows

## Before-Approval Contract

1. Research code, docs, tracker, adapters, tests, and history before asking.
2. Accumulate a full local Goal Draft; never replace it with a receipt.
3. Resolve `interview.max_questions`, default 15; require a positive integer and
   distinguish unset from invalid.
4. Share the ceiling across initial questions and non-obvious findings from both
   critique rounds; stop early when ambiguity is gone.
5. Each question records options, option-specific tradeoffs, recommendation,
   reason, answer, and rejected-alternative reason.
6. Run critique round 1, conditional to-be docs/child specs, critique round 2,
   meticulous alignment, and a purpose/structure/execution/proof briefing.
7. Apply obvious findings and record them without consuming question capacity.
8. Ask consequential findings within the remaining ceiling.
9. Without explicit approval, perform no final GitHub reconciliation or
   implementation.

Planning-only fallback may reach the briefing only when explicitly enabled by
the adapter. It must return a typed blocked next action and cannot activate,
implement, record child progress, or complete.

## Approval And Establishment Contract

Approval binds the exact final briefing, complete Goal Draft bytes, parent
identity, and initial approved work-item manifest. The immutable binding is
created only after exact parent readback. `achieve` calls only issue-owned
provider operations, persists each provider observation, and claims `bound`
only after exact graph equality.

After establishment, the GitHub parent owns verified in-scope graph evolution.
A newly discovered independent Work Item is added with a typed parent graph
amendment; a deferral records exact old/new parent identities, durable reason,
and remove/add readbacks. These do not rewrite the frozen binding's initial
manifest. A change to purpose, success criteria, architecture, or approved
scope is semantic and returns to explicit operator approval.

For provisional #724, approval also authorizes recording the premature
bootstrap/planning reset and reconciling—not erasing—its history.

## `/goal #N` Pickup Contract

Accept only objective text whose trimmed value matches `^/goal[ ]+#([1-9][0-9]*)$`.
The number is not sufficient identity by itself:

1. resolve the exact current repository from the adapter; if absent, accept one
   and only one compatible configured git remote; never guess from cwd basename
2. return `repository-unresolved` or `repository-ambiguous` before issue read
3. read issue `#N`; parse exactly one canonical Goal Run metadata block or
   return `not-a-goal-run`, `metadata-missing`, or `metadata-ambiguous`
4. load the named binding and draft; validate every identity/hash
5. require verified establishment and current-membership observations; derive
   the expected graph from the immutable initial manifest plus verified parent
   graph amendments and deferrals, then compare exact fresh provider state
6. refuse a closed parent, unresolved observation, or any identity mismatch
7. select from open children whose body carries an executable Work Item key,
   purpose, owned surfaces, dependencies, acceptance criteria, exact proof
   commands, and non-claims; reject stale premises before selection
8. choose by satisfied dependencies, then approved rank, Work Item key, exact
   repository, and number; return a typed refusal instead of guessing on ties
9. brief the selected purpose, mutation surface, verification, and stop gates

The sidecar path is never user input. The host needs no Charness parser and
stores no Charness execution state beyond ordinary objective text.

## Execution And Completion Contract

Routine progress is child state. `achieve` reads provider truth before each
slice, writes the resolved parent/child lineage into shared active-goal
coordination, delegates implementation to the owning workflow, and requires
issue-owned child behavioral proof before issue closeout. Parent body mutation
is limited to managed metadata, graph amendments/deferrals, and shared contract
changes. Parent completion invokes the issue-owned guarded close after
whole-system proof, docs reconciliation, and final fresh-eye review.

## Atomic Runtime Cutover

Once binding and provider prerequisites are proven, replace the public
`achieve` skill, lifecycle-before/during/after references, adapter policy,
active-goal coordination, operator route docs, and generated mirrors as one
coherent behavior change. Then remove the supported execution roles of the
prototype receipt helpers, local `Status: active|blocked|complete`, local slice
appends, and `/goal @file`. Historical artifacts remain untouched. No old
runtime reader or dual branch survives the close of this child.

The whole-repository classifier is owned by the evidence-lineage child; any
orchestration-owned defect it finds routes back here and blocks this child.

## Acceptance Criteria

- Facts discoverable from fixtures/repo/tracker are not emitted as questions.
- Default ceiling is 15; valid adapter override works; bool/zero/negative/string/
  fraction are typed invalid values.
- Ceiling exhaustion with consequential ambiguity blocks before approval or
  provider mutation.
- Deterministic critique repairs do not consume question count.
- No path creates/reconciles the final graph before explicit approval.
- Planning-only fallback refuses activation and implementation.
- `/goal #724` resolves the parent and pointers; `/goal @binding`, `/goal #0`,
  extra prose, a child issue, ambiguous repo, multiple/malformed metadata
  blocks, mismatched hash, partial graph, and closed parent refuse distinctly.
- A child missing any executable-body field cannot be selected even if open.
- Verified graph amendment/deferral changes expected membership without
  mutating the immutable initial binding; semantic changes require reapproval.
- Warm pickup selects from fresh child state without replaying the interview.
- A clean agent can understand and execute the first child using only installed
  skill instructions, parent metadata, binding/draft, and child body.

## Verification Commands

Create/reshape focused tests and run:

```bash
python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_achieve_interview_contract.py
python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_achieve_issue_goal_lifecycle.py
python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_goal_binding_v1.py
python3 scripts/sync_root_plugin_manifests.py --repo-root .
```

Create a clean fixture repository with one configured remote, exact parent
metadata, binding/draft, three dependency-ranked children, and deterministic
fake-provider observations. Run the repo-owned clean-consumer harness against
`/goal #724`; retain the structured selected-child/refusal receipt. Repeat with
zero and two compatible remotes, malformed/multiple metadata, stale premise,
and a missing proof-command field. If no repo-owned harness exists, creating it
is part of this child; an informal prompt transcript cannot satisfy closeout.
Cautilus remains ask-before-run and is not implied by this spec.

## Adversarial Stimuli

- research fixture already answers a would-be question
- cap reached with one consequential decision remaining
- approval omitted, vague, or tied to an older draft hash
- provider unavailable under default and explicit planning-only policies
- `/goal #N` in a repo with ambiguous/no repository identity
- parent metadata points to another draft/binding
- establishment receipt names only a same-count wrong graph
- verified lazy addition followed by pickup, and semantic scope change without
  reapproval
- open child omits one executable-body field or has a stale premise
- process restart between approval and each reconciliation readback
- current child closed externally before pickup

## Documentation Impact

Update public skill/lifecycle references, active-coordination and operator route
docs, and maintained dogfood evidence owned by orchestration. Evidence-specific
artifact/closeout docs remain with the evidence-lineage child.

## Closeout Evidence

Focused lifecycle/refusal tests, realistic clean-repo consumer prompt,
source/export sync, and fresh-eye public-skill critique. Live #724 activation is
proved separately by the dogfood child.

## Non-Goals And Non-Claims

- no new autonomous run engine
- no host `/goal` implementation
- no local progress mirror
- no legacy runtime compatibility
- no provider success claim from fake-backend tests
