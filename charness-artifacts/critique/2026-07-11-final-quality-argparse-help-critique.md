# Critique Review — Final Quality Argparse Help Campaign
Date: 2026-07-11

## Decision Under Review

Clear the final 23 missing-help findings across ten quality-owned CLIs without
changing their scan, ratchet, baseline, migration, or planning behavior.

## Failure Angles

- Semantic safety: write, execute, accept, baseline, and dry-run controls must
  not be described more safely or broadly than their code behaves.
- Operator UX: defaults, precedence, repeatability, ranking, and JSON/human
  output must be legible without source inspection.
- Verification ownership: each option needs wrapping-safe proof in an existing
  owning test boundary, with source/plugin parity and unchanged parser metadata.

## Counterweight Pass

- UX review found two real caveats: `--top` is ignored by nose baseline writes,
  and release-sentinel `--summary` overrides `--json`; both are now documented.
- Full help snapshots, a shared parser abstraction, and a new global blocking
  floor would add churn without strengthening these local parser contracts.
- Repeated test helpers remain local until they cause measurable maintenance
  drift.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/inventory_nose_clones.py | action: fix | note: document that --write-baseline ignores --top and scans all families; fixed and re-reviewed.
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/inventory_release_only_sentinels.py | action: fix | note: document that --summary selects compact output over --json; fixed and re-reviewed.
- F3 | bin: bundle-anyway | evidence: strong | ref: skills/public/quality/scripts | action: document | note: all 23 option descriptions match code and preserve parser contracts across ten CLIs and mirrors.
- F4 | bin: over-worry | evidence: strong | ref: tests | action: defer | note: snapshots, a generic parser, or a global help floor would widen this additive help-only campaign.

## Reviewer Tier Evidence

- Requested tier: high-leverage multi-angle quality/code review.
- Requested spawn fields: typed read-only reviewer plus semantic, operator-UX,
  verification/maintainability, and separate counterweight lenses.
- Host exposure state: unsupported
- Application state: typed reviewer was rejected as unknown; default fresh
  contexts ran read-only. The first rail result was quarantined after parent
  edits preceded verification; final semantic/verification and counterweight
  passes ran from a new snapshot and verified with zero drift.

## Fresh-Eye Satisfaction

nested-delegated — semantic, UX, and verification contexts inspected the
prepared packet and diff; UX was retried after one interruption, found two
fixes, and final clean-rail verification plus counterweight approved them.

## Boundary Ownership

- Producer: each quality CLI's argparse parser produces its own help contract.
- Consumer: maintainers and agents running inventories, ratchets, migrations,
  provenance checks, and quality planning.
- Owning surface: each source script, packaged mirror, and existing focused
  in-process test boundary.
- Verdict: owned-correctly
