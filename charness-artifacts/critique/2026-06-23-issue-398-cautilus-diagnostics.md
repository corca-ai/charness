# issue 398 cautilus diagnostics
Date: 2026-06-23

## Decision Under Review

Resolve #398 by adding a first-class Cautilus diagnostic bundle validator while
leaving `charness-artifacts/cautilus/latest.md` as the passing-proof carrier.

## Failure Angles

- Jackson problem framing: the first draft solved the adjacent "validate bundles
  that already have finding.md" problem, but #398's JTBD is to prevent diagnostic
  verdicts from disappearing as side evidence. The fix now treats changed
  machine evidence files as bundle candidates and keeps `latest.md` out of the
  diagnostic path.
- Weinberg diagnostic: the first draft did not locate the disappearance failure
  because JSON-only diagnostic evidence could be added without `finding.md`.
  The validator now routes changed `observed.v1.json`, `summary.v1.json`, and
  `report.json` to their bundle and fails when `finding.md` is missing.
- Gawande operational checklist: the first draft documented a standing corpus
  check but wired `run-quality.sh` without `--all`. The broad gate now invokes
  `validate_cautilus_diagnostics.py --all`, and tests pin that wiring.

## Counterweight Pass

- Act before ship: none after the reviewer-driven fixes. The broad gate checks
  the existing diagnostic corpus, changed machine evidence cannot bypass the
  finding requirement, and `latest.md` remains separate.
- Bundle anyway: include the new validator and plugin mirror in the commit; a
  wrapper/test-only commit would break `run-quality.sh`.
- Valid but defer: deeper Cautilus schema validation can wait. This slice needs
  a low-noise first-class artifact floor: parseable machine evidence, basic
  outcome/recommendation sanity, a source/verdict finding, and non-claim or
  follow-up context.
- Over-worry: broad recursive artifact abstractions or turning diagnostic
  bundles into another proof pointer. The direct run-directory convention is
  enough for the current corpus.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/validate_cautilus_diagnostics.py | action: fix | note: changed machine evidence files now require sibling finding.md
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/run-quality.sh | action: fix | note: standing run-quality gate now runs diagnostic validation with --all
- F3 | bin: bundle-anyway | evidence: strong | ref: plugins/charness/scripts/validate_cautilus_diagnostics.py | action: fix | note: plugin mirror must include the new validator so exported run-quality can execute it
- F4 | bin: valid-but-defer | evidence: moderate | ref: scripts/validate_cautilus_diagnostics.py | action: defer | note: detailed per-schema Cautilus validation is useful later but not required for #398's artifact-home fix
- F5 | bin: over-worry | evidence: moderate | ref: docs/artifact-policy.md | action: document | note: do not turn diagnostic bundles into a second latest pointer or passing-proof carrier

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: none; parent used `multi_agent_v1.spawn_agent` with
  default inherited model/effort per host tool guidance.
- Host exposure state: host-defaulted
- Application state: host-confirmed: `multi_agent_v1.spawn_agent` returned
  agents `019ef2f1-d8fc-7360-a541-86865840ce2b`,
  `019ef2f1-fc52-7a73-893b-3d6ade1d5ecf`,
  `019ef2f2-1bcd-7600-ae18-c3acdbe250b1`, and counterweight agent
  `019ef2f5-4688-76e3-81e4-c56c2d17f810`; all completed via `wait_agent`.

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated. Three angle reviewers found the same
pre-ship issue in the first draft: `run-quality.sh` needed `--all`, and the
validator needed to fail machine-evidence-only diagnostic directories. A
separate counterweight reviewer accepted the fixed scope and deferred deeper
schema validation.
