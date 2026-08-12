# Issue 589 Preset Reconciliation Resolution
Date: 2026-08-13

## Decision Under Review

Replace the permanent `declared-only` preset-lineage gap with a truthful state
model: only a validator-accepted, repo-contained machine-readable prescription
can be reconciled; sample or absent prescriptions remain advisory metadata.

## Failure Angles

- Producer/consumer mismatch: a lifecycle-only parser could mark a preset clean
  that the repo's preset validator rejects.
- Boundary escape: a preset file or its containing directory could be symlinked
  outside the repository and silently become an adoption source.
- Reader usability: an advisory state without its reason, or a multi-command
  gap collapsed to one opaque finding, gives an operator no actionable outcome.

## Counterweight Pass

- Both review rounds found concrete false-green or escape paths and changed the
  implementation; they were repaired before verification.
- Existing preset prose and technology detectors are provenance, not a claim
  of policy adoption; migrating them or auto-rewriting adapters remains out of
  scope.
- No source/shipped plugin drift was observed after mirror synchronization.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/validate_presets.py | action: fix | note: made lifecycle consume the same complete, strict-fenced preset contract accepted by the validator; added bidirectional fixture coverage
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/quality_declaration_lifecycle.py | action: fix | note: reject external preset-file and symlinked-presets-directory resolution before reconciliation
- F3 | bin: bundle-anyway | evidence: strong | ref: skills/public/quality/scripts/quality_run_plan_render.py | action: fix | note: render metadata advisory reasons and emit one named gap for each missing required adapter command
- F4 | bin: over-worry | evidence: moderate | ref: plugins/charness/skills/quality/scripts/quality_declaration_lifecycle.py | action: defer | note: source and shipped plugin copies were byte-identical after sync; no separate repair is warranted
- F5 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/spec/2026-08-13-preset-lineage-reconciliation-contract.md | action: defer | note: existing sample presets remain metadata until a maintainer supplies a deliberate prescription; automatic migration and adapter rewrite are not proven in this slice

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye reviewer, two required rounds for a verdict-logic surface plus a ledger-state review.
- Requested spawn fields: host-defaulted model and effort; separate read-only review scopes for rounds 1 and 2, then an independent goal/ledger scope.
- Host exposure state: host-defaulted
- Application state: host-confirmed: `/root/issue589_r1`, `/root/issue589_r2`, and `/root/issue589_goal_sync` each returned findings in the parent context.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated. All three reviewer result messages were received; the round-2
and ledger-state fingerprints verified `ok: true`, parent-attributed only.

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/2026-08-12-152909-packet.md`
- Packet path: `charness-artifacts/critique/2026-08-12-152909-packet.json`
- Packet SHA256: `2aec45a5dd0d822d5cb208a7a03bdf216b75c8db76ca6eec042447853b405491`
- Identity SHA256: `56a708a4eaa512c698040d6200048433cbbea5e042431ef869950243063a77ff`

Round 1 found validator, human-advisory, strict-fence, containment, and
per-command-gap defects; those repairs were read in round 2 through
`2026-08-12-151434-packet.md`. The current packet additionally binds the final
goal/ledger state and the cohesive module extraction; the independent ledger
review found no premature-close claim. Round 2 then found
the invalid-preset false green and the directory-symlink escape. Its repairs are
accepted-unreviewed under the mandatory two-round cap; focused tests, preset
validation, planner detail output, mirror comparison, and `git diff --check`
are the post-repair evidence, not a claim of a third review.

## Boundary Ownership

- Producer: quality-adapter `preset_lineage`, local preset front matter, and declared adapter commands.
- Consumer: `plan_quality_run.py` lifecycle payload and the human/structured run-plan renderers.
- Owning surface: quality declaration lifecycle, with `validate_presets.py` as its shared contract boundary.
- Verdict: owned-correctly
