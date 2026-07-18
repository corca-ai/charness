# Dynamic Entrypoint Evidence Critique
Date: 2026-07-18

## Execution

Two parent-delegated angle reviewers and a separate counterweight reviewer read the shared worktree. The initial approvals were quarantined after a parent-side packet/fingerprint race; the final reviews ran against stable snapshots and each boundary verification reported zero drift.

## Packet Consumed

`charness-artifacts/critique/dynamic-entrypoint-evidence-packet.md`

## Target

Code critique of the dead-code advisory's dynamic-entrypoint evidence classifier.

## Decision Under Review

Classify a Vulture finding as `registered_dynamic_entrypoint` only when a conservative AST witness connects the producer symbol to an actual supported dynamic consumer. Keep unrecognized forms as review candidates instead of adding a name allowlist.

## Capability at Stake

Dead-code output should direct maintainer attention to credible cleanup candidates without hiding genuinely dead functions or forcing static imports that weaken portable plugin boundaries.

## Failure Angles

- False exemption: early runpy matching accepted a producer filename nested inside a different path expression. It now accepts only the full caller-sibling `parent / name` or `with_name(name)` form.
- Broken registry flow: early registry matching accepted co-located literals and an unrelated `getattr`. It now requires an uppercase tuple/list registry containing a `*Intent`, a direct or default-bound loop over that registry, an `import_module` assignment from the loop intent, and `getattr` on that same local.
- Coupling and portability: the final design recognizes existing dynamic seams without replacing them with static imports or storing a path/name allowlist.
- Runtime economics: the candidate-only git-visible scan left measured end-to-end advisory time near the 8.92-second baseline; no material regression was observed.

## Findings

The two false-suppression findings were real and fixed before ship. The broad quality run then caught two new lexical duplicate families; a match/case predicate and shared function-node traversal removed them without accepting a baseline rotation. Final correctness, architecture, and counterweight re-reviews all returned SHIP. The first committed-range changed-line consumer then exposed 14 unexecuted fail-closed lines; direct fixtures now cover caller-path variants, default/loop forms, directory mismatch, ignored registry rows, and unreadable/invalid consumers. A manual mutant at the cited recursive caller-path line made its owning test fail. The live repository scan reports two registered dynamic entrypoints and zero review candidates.

## Counterweight Pass

- Act Before Ship: none remain; both evidence-link defects were fixed and re-reviewed.
- Bundle Anyway: none.
- Over-Worry: generic points-to analysis, replacement of the existing dynamic dispatches, and AST caching are unsupported by current behavior or measurements.
- Valid but Defer: add another bounded syntax witness only after a real recurring dynamic-entrypoint form produces advisory noise.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/dynamic_entrypoint_evidence.py | action: fix | note: resolved full-expression runpy path evidence before ship
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/dynamic_entrypoint_evidence.py | action: fix | note: resolved registry-to-import-to-dispatch evidence chain before ship
- F3 | bin: over-worry | evidence: strong | ref: measured dead-code advisory runtime | action: document | note: generic points-to analysis and caching are not justified by current consumers or runtime

## Deliberately Not Doing

- No proof of arbitrary Python dynamic reachability, aliased registries, or runtime branch reachability.
- No broad symbol or path allowlist.
- No replacement of the portable `runpy` and lazy registry seams.
- No new blocking quality floor; the dead-code inventory remains advisory.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: `model=gpt-5.6-terra`, `reasoning_effort=medium`, `service_tier=priority`, `fork_turns=none`
- Host exposure state: requested_fields_sent
- Application state: host accepted the requested fields; provider application metadata was not exposed.

## Fresh-Eye Satisfaction

`parent-delegated`; two final angle reviews and the separate counterweight completed read-only, with parent-side boundary fingerprints verified after each.

## Boundary Ownership

- Producer: Vulture findings plus git-visible source files.
- Consumer: the public quality dead-code advisory and its maintainer-facing summary.
- Owning surface: public quality skill scripts and focused quality-gate tests.
- Verdict: owned-correctly

## Next Move

Sync the checked-in plugin export, run the full closeout gates, and preserve the conservative non-claims in the quality and release records.
