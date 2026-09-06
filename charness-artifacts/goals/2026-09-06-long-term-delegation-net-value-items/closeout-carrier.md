<!-- charness-work-item-key: closeout-carrier -->
# A multi-issue closeout is forced into repeated reviews and classification partitions

## Problem and capability

In #798, closing #800 and #803 required separately repackaged final reviews. The shared checker requires one scalar packet label to prefix-match every issue. The commit hook then dispatches one classification for all bare close targets, forcing bug/feature separation. Support direct consumption of one genuinely scoped review and one mixed carrier without dropping per-issue evidence.

Classification: bug
Causing skill: issue, critique

## Fixed decisions and ownership

- No dependencies. Shared code owns generic packet/result/delivery identity; issue owns target membership, per-target classification, behavioral verdict and its closeout policy.
- Existing singleton carriers remain valid. A structured exact target set is the candidate direction, not permission to accept free-text substring membership or weaken old refusals.
- A semantic review may cross caller formatting only if its bound inputs and actual observations cover every requested claim and the consuming owner accepts that scope. A release-state review alone does not prove issue behavior.

## First action and probes

Use debug to reproduce scalar-target and mixed-classification failures against the final issue/hook consumer, then causal review before repair design. Inspect `skills/shared/scripts/reviewer_worker_carrier_support.py`, `skills/public/issue/scripts/issue_critique_observer.py`, and `scripts/gates/check_issue_closeout_commit_msg.py` plus their producer schemas and tests. Freeze legacy migration, ambiguous/missing classification handling and target equality rules in the living contract before code.

## Success criteria and checks

- One source-bound review covering two different issues is consumed without a second semantic review solely for format. A mixed bug/feature carrier exercises both existing evidence floors through draft validation and hook dispatch.
- Negative controls: omitted/extra/duplicate/foreign/swapped target; stale source; wrong packet/result/parent; an uncovered issue added to an otherwise passing bundle; a bug mislabeled or missing its required proof. Fail before publication.
- Independent reviewer observes per-issue behavior through a channel distinct from carrier/closed state. It may reuse actual current observations, never invent them from an aggregate pass.
- Before/after record names removed review/recopy/partition work and all added identity checks and fallback costs. Keep existing paths if proposed consolidation loses capability or is more complex for no gain.

## Boundary and non-goals

This is a proof-surface change; retain distinct review, focused regression/mutation proof and publication/readback. No global review cache, fabricated human approval or unrelated closeout taxonomy rewrite. Parent alone integrates/export-syncs and owns final published closeout. Dependencies mean local proof readiness, not premature tracker closure.
