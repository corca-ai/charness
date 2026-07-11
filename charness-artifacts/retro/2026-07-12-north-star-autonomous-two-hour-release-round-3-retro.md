# Round Three North-Star Autonomous Release Retro
Date: 2026-07-12

## Mode

session

## Context

This reviews goal `north-star-autonomous-two-hour-release-round-3`: eight
evidence-admitted slices, final exact-bundle proof, and public v0.66.4 release.

## Evidence Summary

- Goal slice log, v0.66.4 release artifact, and quality readiness record.
- Final lock: 4,592 broad tests passed; exact-base mutation consumer returned
  `blocking=[]`; release quality took 82.9s.
- Public proof: helper HTTPS 200 plus a distinct reviewer confirmed content,
  tag `233dc25b`, public release, install 0.66.4, and clean worktree.

## Waste

- Several reviewer envelopes were not behaviorally binding: one reviewer
  spawned an unauthorized child and an earlier worker committed despite a
  no-commit brief. Fingerprint verification quarantined those approvals, but
  replacement reviews cost extra turns.
- The first final lock correctly stopped on generated SLOC drift after the last
  code slice. Two later locks exposed quality-artifact evidence-shape defects:
  inventory fields were paraphrased and a gitignored runtime source lacked its
  reproduction marker. Existing gates caught both, but only after one 40.7s
  broad run.
- The release planner initially emitted a seven-step nose checklist for
  unrelated plugin scripts. The broad integrations surface was valid for
  validation/retro but too broad as a release real-host subscription.

## Critical Decisions

- Kept issue lifecycle separate: #433 and #436 remain OPEN while shipped
  behavior and tracker state are described independently.
- Turned the observed real-host false positive into the exact
  `external-tool-control-plane` surface rather than deleting host proof or
  adding raw-glob duplication.
- Preserved the final broad/public teeth while removing reversible false starts:
  sync writers moved earlier, mutation evidence became copyable, and telemetry
  stayed best-effort.

## Expert Counterfactuals

- Douglas Engelbart would design method and tooling together: the trigger
  surface, regression fixture, release planner, and operator notes must form one
  learning loop. That counterfactual produced the narrow named surface instead
  of leaving “ignore the nose checklist” as session memory.
- A direct sequencing lens would run artifact-consumption/durability checks
  immediately after authoring the quality record. The repo already owns those
  deterministic teeth; future runs should invoke them before the expensive lock
  whenever the quality artifact changes.

## Sibling Search

- axis: adapter surface subscriptions | decision: applied in this slice | proof:
  release now subscribes to `external-tool-control-plane`; retro intentionally
  keeps the broader integrations surface | follow-up: repo-local guard
  `tests/quality_gates/test_release_real_host.py`
- axis: inventory citations in durable artifacts | decision: existing guard
  already owns the class | proof: `validate_inventory_consumption.py` found the
  paraphrase and the quality record now names six fields | follow-up: none — no
  new validator is justified.

## Next Improvements

- workflow: applied — run the existing inventory-consumption and evidence-
  durability checks immediately after changing a quality record; this session
  repaired and proved both before the final successful lock.
- capability: applied — exact external-tool trigger ownership plus a negative
  derived-plugin regression prevents the measured seven-step false positive.
- memory: applied — refresh `docs/handoff.md` to remove completed round-two
  work and preserve only issue lifecycle/nonclaims for the next pickup.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-12-north-star-autonomous-two-hour-release-round-3-retro.md
