# Critique Review
Date: 2026-08-09

## Decision Under Review

Whether the complete `v4.0.0..HEAD` delta can ship as `v4.1.0` without hiding a
breaking installed-command removal, publishing before hosted proof, or calling
locally repaired issue state remote fact.

## Execution

Two bounded read-only release-safety rounds inspected the shared worktree before
any version, tag, push, or public-release mutation. Round 1 reviewed the clean
P2 tip. Round 2 read the first compatibility and handoff repairs. Parent-side
reviewer fingerprints verified both windows; the second is parent-attributed
only to edits made after its result was delivered. The final direct-call
compatibility and remote-phase wording are accepted-unreviewed under the
two-round cap. A separate claims review still owes the drafted release record.

## Failure Angles

- Semver: installed paths, documented syntax, strict exit semantics, and JSON
  consumers must survive a minor release.
- Proof order: local gates, branch push, hosted CI, tag/publication, and public
  readback must remain distinct states.
- Consumer risk: shipped false-verdict issues must be repaired or explicitly
  carried as non-claims.
- Release surfaces: packaging, Claude/Codex plugin versions, marketplace
  versions, update guidance, and fresh-checkout probes must reconcile.

## Findings

- Round 1 found complete deletion of four v4.0.0
  `check_title_slug_drift.py` invocation paths would break installed automation
  and make a minor bump dishonest. The first repair kept the paths but replaced
  strict 0/1 behavior with exit 3 and emitted legacy-clean `drift: []` from a
  checker that did not run; round 2 correctly rejected that as both incompatible
  and false-green-compatible.
- The capped repair retains deprecated direct-call behavior until a future
  major release: legacy advisory exit 0, strict 0/1, and `checked`/`drift` JSON
  fields remain. The filed #563 default-scope bug is repaired by including
  `charness-artifacts/goals`. Standing quality/pre-push/staged-plan wiring and
  public recommendations remain removed, so ordinary repo work pays no checker
  cost. Deprecation is printed on stderr and structured JSON names it.
- Round 1 also found the old handoff held publication until a separate repair
  push; round 2 found the first rewrite still contradicted the goal's
  no-intermediate-push language and the standard helper cannot pause between its
  combined branch/tag push and public creation. The final contract now defines
  the already-authorized final release phase as two remote barriers after the
  release candidate is complete: untagged final-code branch push for hosted
  `Quality Core`, then tag/publication push only after green readback. It forbids
  per-slice, work-in-progress, and intermediate public releases.
- Round 2 confirmed #575 is repaired in the committed delta: arbitrary
  `docs/**` is not a default current-fact population, historical docs without
  declaration render `NOT CONFIGURED FOR DOCS`, and explicit configured docs
  remain enforceable. Its remote closeout remains pending and is not claimed.
- Local release preparation and fresh-checkout probes passed for the recorded
  `v4.0.0..f62e283f` base delta; configured real-host triggers evaluated the
  whole path population and returned `required: false`. This does not claim
  hosted CI, public release visibility, installed-version/doctor readback,
  baton reconciliation, or release-linked issue closure.

## Counterweight Pass

- Act Before Ship: preserve deprecated direct-call semantics and split the
  final remote phase around hosted CI; both are release-boundary requirements.
- Bundle Anyway: release notes must name the title-slug deprecation and the
  remaining #576 no-verdict design gap without presenting either as a green
  checker claim.
- Keep: `v4.1.0` is an honest additive minor once the installed command remains
  compatible; the delta adds consumer-visible planning, diagnosis, and safety
  behavior without requiring migration.
- Over-Worry: configured real-host proof returned not-required for the exact
  release delta; inventing a manual host checklist would overstate the adapter.

## Deliberately Not Doing

No Cautilus evaluation, scheduler tuning, complete title-slug command removal,
major-version migration, remote-green inference from a push exit, or blanket
closure of open issues is included.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: v4.0.0 installed title-slug paths and version-policy.md | action: fix | note: retain deprecated advisory/strict/JSON behavior and correct the default goal-record population
- F2 | bin: act-before-ship | evidence: strong | ref: docs/handoff.md and publish_release_execute.py | action: fix | note: final RC branch push earns hosted CI before a separate tag/publication push
- F3 | bin: bundle-anyway | evidence: strong | ref: issue #575 and regenerable_facts_lib.py | action: document | note: locally repaired, remote closeout still pending
- F4 | bin: over-worry | evidence: strong | ref: exact-range real-host trigger result | action: defer | note: configured trigger evaluation established required=false, not a host proof pass

## Reviewer Tier Evidence

- Requested tier: host default for bounded fresh-eye review.
- Requested spawn fields: existing agent context; no model override requested.
- Host exposure state: host-defaulted
- Application state: both findings delivered; provider-side model metadata not exposed.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated. Both release-safety results were delivered. The first
reviewer-boundary fingerprint was clean; the second recorded only declared
parent-attributed edits after the review result.

Fresh-eye pass: scripts/check_title_slug_drift.py — release review found removal
and then semantic neutering incompatible with a minor release; deprecated
direct-call behavior is retained, default scope is repaired, and standing use
remains absent. The capped final repair is accepted-unreviewed.

Fresh-eye pass: docs/handoff.md — release review found the old and first-repair
push sequences contradictory; final remote barriers now separate RC hosted-CI
evidence from tag/public publication, accepted-unreviewed under the cap.

## Boundary Ownership

- Producer: release delta, adapter, version policy, handoff, and drafted notes.
- Consumer: installed users, hosted CI, release backend, and next-session baton.
- Owning surface: release owns semver and publication order; issue owns remote
  closeout; quality owns the hosted result.
- Verdict: owned-correctly

## Next Move

Validate this artifact and compatibility surface, draft the release record, run
the distinct claims review, prepare the versioned release candidate, then run
the verification lock before the final-code branch push. Do not tag or publish
until hosted `Quality Core` reads green.
