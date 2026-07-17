# v2.0.0 Release Critique

Date: 2026-07-17
Verdict: APPROVE major (1.3.0 → 2.0.0), with note conditions folded in

## Decision Under Review

Cut charness 2.0.0 carrying one local commit (`7b20b0ce` — the
operator-approved breaking CLI affordance convergence: worktree string
`next_action`→`next_step`, runtime doctor/update/init host map
`next_steps`→`host_next_steps`, tool aggregate attention
`next_action`→`next_step`, human affordance prefix unified to `NEXT:`), then
push and publish per the operator's "push and release when done" instruction.

## Fresh-Eye Satisfaction

parent-delegated bounded release critique in a different agent context
(bounded-reviewer, read-only Read/Grep/Glob envelope); zero-drift reviewer
boundary fingerprint verified around the review (`ok: true, drift: []`).

## Reviewer Tier Evidence

- Requested tier: high-leverage (release critique class).
- Requested spawn fields: per-host contract (AGENTS.md `Subagent Delegation`,
  split 2026-07-17) — Claude Code host convention applies: typed
  `bounded-reviewer`, session-model inheritance.
- Host exposure state: host-defaulted
- Application state: read-only envelope asserted by agent type (Read/Grep/
  Glob); parent-side boundary fingerprint verify returned `drift: []`.

## Failure Angles

- Bump honesty (major vs minor) against the release version policy.
- Consumer breakage inventory completeness for the release notes.
- Install-surface integrity (mirror parity, hand-edited manifests, secrets).
- Release-notes truthfulness traps (overclaiming "everywhere"/"no impact").
- Old vocabulary breaking at release time (battery, probes, helper, specdown).
- Post-publish reconciliation debt (handoff baton, release state pointer).

## Structured Findings

- F1 | bin: over-worry | evidence: strong | ref: skills/public/release/references/version-policy.md | action: document | note: major is honest and not over-called — published payload fields that automation parses were renamed; minor's "do not break existing callers" clause rules it out; no surface removal argues against anything above major.
- F2 | bin: valid-but-defer | evidence: strong | ref: scripts/worktree_audit_lib.py | action: fix | note: the audit `--doctor` inline annotation also changed `next=`→`next_step=`, a human-text break beyond the advertised prefix unification; folded into the release notes breakage inventory.
- F3 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/spec/cli-output-affordance-contract.md | action: fix | note: notes must not claim "prefix unified everywhere" (a quality-plane advisory script legitimately keeps lowercase `next:`) nor "no consumer impact", and must list the KEPT surfaces (structured `next_action` object, list-shape `next_steps`, `--next-action` flag projection, `next_action_hint` manifest input) so consumers do not over-migrate; folded into the notes.
- F4 | bin: valid-but-defer | evidence: strong | ref: docs/handoff.md | action: fix | note: the handoff Workflow Trigger and Next Session item 1 still route into the now-shipped convergence and pin v1.3.0; reconciled to 2.0.0/shipped as part of this release closeout.
- F5 | bin: valid-but-defer | evidence: moderate | ref: skills/public/release/scripts/current_release.py | action: document | note: pre-existing watch-item — the drift check reads marketplace `metadata.version` but not `plugins[0].version`; post-bump confirmation that `plugins[0].version` also reads 2.0.0 is part of this release's verification.
- F6 | bin: over-worry | evidence: strong | ref: packaging/charness.json | action: defer | note: all version-carrying surfaces read 1.3.0 with no drift and no hand-edited generated manifests; release-time surfaces (battery, fresh-checkout probes, specdown `-no-report` verify, release planner's own structured `next_action`) are migrated or kept, so nothing pins the old vocabulary at release time.

## Release Notes Basis (truthful bullets)

- BREAKING (automation parsing CLI YAML): `charness doctor|update|init`
  host-keyed map `next_steps` → `host_next_steps`; `charness tool
  update|install|repair|sync-support|doctor` aggregate attention string
  `next_action` → `next_step`; `charness worktree
  doctor|prepare|create|cleanup|audit` string `next_action` → `next_step`
  (including per-check entries). These renames ship via the managed-checkout
  root CLI after `charness update`, not via plugin files.
- BREAKING (installed plugin files): the mirrored worktree libs and the
  standalone `install_machine_local.py` installer JSON
  (`next_steps` → `host_next_steps`) carry the same renames.
- BREAKING (human output): affordance lines now print `NEXT:` (worktree
  renderers dropped `next:`, the runtime doctor block header dropped
  `NEXT_ACTION:`); the worktree audit `--doctor` inline annotation changed
  `next=` → `next_step=`.
- KEPT (do not migrate): the structured `next_action` object on runtime
  doctor payloads and skill plan envelopes; list-shape `next_steps` (tool
  doctor, `capability init`, gather advise); the `charness doctor
  --next-action` flag's `{"next_action": <message>}` projection; the
  worktree manifest input key `next_action_hint`.
- No compatibility aliases ship (operator-approved).

## Deliberately Not Doing

- No issue closes at release time (nothing pending closure).
- No compatibility alias or dual-emission window — explicitly rejected by the
  operator's breaking-changes-allowed approval.

## Boundary Ownership

- Verdict: owned-correctly

Release mechanics stay in the repo-owned publish helper; the affordance
vocabulary contract stays in the spec artifact plus the generated CLI
reference and the executable tool-doctor spec.

## Packet Consumed

none — release-boundary critique over the single commit `7b20b0ce` (packet
sections not declared for this ad hoc release scope; changed surfaces
enumerated inline).
