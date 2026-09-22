# Release Critique — charness v8.9.8 (patch)

- **Kind**: `charness.release-critique` (v1)
- **Prepared for**: v8.9.8-release
- **Scope**: `v8.9.7..f1b790c8f` — #825 sampled-mutant coverage; #826/#827/#828/#829
  report-only lane, typed goal edges, lane retry, deletion-tolerant checkpoint;
  #830 persisted-data-loss lens; critique follow-ups (fail-closed lens, precise
  stall matcher, timeout help)
- **Packet**: `charness-artifacts/critique/2026-09-22-215724-packet.json`
  (sha256 `634dcbd276217b8d5c5ce9a14bdcfce185c5669ff37947fd8142ce6c1dcfa974`,
  identity `f3f05340e05de6a9f0de980caf692dc72e839aa15a600a7b2dbe269568b2fabe`)
- **Reviewers**: two fresh-eye parallel reviewers (Gawande-operational,
  Minto-Raskin readability) + synthesis; read-only, no repo mutation

Fresh-eye satisfaction: parent-delegated two angle reviewers plus synthesis

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `labels=gawande-reviewer,minto-raskin-reviewer,synthesis; read-only shared checkout; structured concerns schema`
- **Host exposure state**: `host-defaulted`
- **Application state**: `two angle reports plus synthesis delivered with concerns and four-bin triage`
- **Delivery state**: `findings-received`
- **Execution mode**: `typed-subagent`
- **Lane evidence**: release lane green, 89 passed, 0 failed
  (`./scripts/run-quality.sh --full --read-only --release`)

## Release Scope

v8.9.8 ships a persistence-risk lens (blocking DROP/TRUNCATE/unscoped-delete
reads as needs-review, ineligible) plus stall-retry and report-only lanes.

## Surface-Lock Inventory

- `scripts/task_run/{persistence,state,completion,attempts,git}.py`
- `docs/agent-task-runs.md`, `docs/cli-reference.md`
  (`--timeout-seconds` per-attempt budget note)
- `skills/public/achieve` goal edge/amendment contracts,
  `skills/public/issue` goal-run contract
- `packaging/charness.json` + host plugin manifests (publish-time bump+sync)

## Concerns

### Act Before Ship

1. **Persistence-lens blocking has no operator-visible note.** The lens turns
   previously-green lanes red with no docs lead.
   Evidence: `scripts/task_run/task_run_persistence.py:17-22,43-61`;
   `docs/agent-task-runs.md`, `docs/cli-reference.md` lacked DROP/TRUNCATE text.
   Operator action: FIXED before ship — `docs/agent-task-runs.md` now names the
   blocked shapes, the green-to-red change, and the
   `MAX_ATTEMPTS` x `--timeout-seconds` wall-time budget; release notes must
   lead with the same paragraph.

### Bundle Anyway

2. **Manifests read 8.9.6 pre-publish.** Confirm the publish-time bump+sync
   covers `packaging/charness.json` and both plugin manifests.
3. **Worst-case wall time is multiplicative.** State the
   `MAX_ATTEMPTS` x timeout formula in the release notes (also fixed in docs
   by item 1).

### Valid but Defer

4. **Legit DROP-migration lanes block with no in-lens escape.** Real but next
   release: replacement detection or an explicit escape hatch.

### Over-Worry

5. **Advisory shapes stay non-blocking; the narrowed stall matcher is
   correct.** No action.

## Upgrade Path

`charness update`, then read the GitHub release notes for behavior changes,
migrations, or rollback notes. No migration step: the lens only adds a review
gate, it does not change install prerequisites or CLI invocation.

## Verdict

Ship v8.9.8 (patch) once item 1 is in the tree and the notes lead with it.
Unresolved: none.

## Boundary Ownership

- **Producer**: release critique reviewers (angle findings plus synthesis)
- **Consumer**: release publisher (`publish_release.py --execute`) and operators
  reading the release notes
- **Owning surface**: `charness-artifacts/critique/v898-critique.md` (this
  record); doc wording owned by `docs/agent-task-runs.md`
- **Verdict**: `owned-correctly`
