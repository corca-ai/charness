# Final release-boundary retro
Date: 2026-08-13
Goal: charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md

## Context

This final pre-publication review covers the frozen `origin/main..0ac9260d`
candidate after the all-range changed-line closeout passed and #608's prepared
claims-review topology was repaired. It replaces the earlier preflight retro's
then-correct coverage-failure stop with the current release decision. No push,
tag, GitHub release, hosted CI, issue closure, or installed-tool readback has
occurred.

## Window

`a17526dc..0ac9260d`, interpreted with the earlier release-preflight retro for
the initial failure. The fixed 22-issue cohort remains OPEN by design.

## Evidence Summary

- `run_slice_closeout.py --verification-lock --refresh-broad-pytest-proof
  --produce-mutation-coverage` completed after the recovery; its final receipt
  records the full changed-line proof rather than relying on focused suites.
- `tests/quality_gates/test_release_claims_review.py` and
  `test_release_resume_state_validation.py` passed **19 tests** after the
  exact-one-parent prepared-record repair. The source and shipped-plugin
  claims-review modules compare byte-identically.
- The final release critique's Gawande, Minto, and counterweight readings
  caught a merge-marker bypass, stale routing, an impossible CI-before-release
  claim, and stale packet identity before publication.
- `check_real_host_proof.py` evaluated the frozen changed range and returned
  `required: false`; none of the configured external-tool trigger paths moved.

## Waste

The first final critique bound an earlier packet and an old candidate endpoint.
Two review findings then changed topology logic and handoff/goal state, making
that packet stale. This was recoverable bookkeeping, but it showed that a
release critique packet must be prepared only after all verdict-logic repairs
and route updates are complete.

The earlier 11-file coverage refusal was useful stop-the-line evidence. It was
not waste to rerun the locked full-range closeout: focused release tests could
not prove the accumulated candidate.

## Critical Decisions

1. **Keep the claims boundary topological.** A prepared record must introduce
   its marker on a single-parent commit; its review record is its exact direct
   child. This prevents inherited-marker descendants and merge parents from
   shifting the reviewer boundary.
2. **Claim only evidence the helper can actually sequence.** Public release
   observer and installed readbacks are post-publication channels; no direct
   CI-before-release claim is inserted where the helper has no pause.
3. **Refresh current routing with released proof.** The goal and handoff now
   say that coverage passed while still distinguishing preparation, claims
   review, push, publication, and installed readback.

## Trends vs Last Retro

The preflight retro correctly rejected focused-test substitution for the full
candidate. Its next improvement has now been applied: full-range coverage is
locked before the release protocol starts. The new recurrence is more specific:
review packets must be regenerated after a reviewer-driven verdict repair.

## North Star Alignment

The design north star's irreversible-boundary rule held: different fresh
readers found failures local tests did not expose, and no public state escaped
while the evidence identity or release sequencing was wrong. The avoided
failure signature is “a green local helper becomes permission to publish”;
the marked prepared record remains a stop, not a publish authorization.

## Expert Counterfactuals

**Douglas Engelbart — system-improving-itself.** The helper topology check
(tool), the packet identity/record schema (language), and the review sequence
(method) must evolve together. The next move should automate final-packet
invalidation on any verdict-logic change so the method exposes, rather than
rediscovers, the stale-binding boundary.

**Falsification-first release lens.** Before making a release step mandatory,
ask which executable helper stage produces its evidence. That would have
rejected the impossible “CI before create-release” wording when it was first
written.

## Sibling Search

- same layer: `skills/public/critique/scripts/prepare_packet.py` packet binding | decision: valid capability follow-up outside this release | proof: reviewer-driven source and route repairs invalidated a manually refreshed packet | follow-up: deferred docs/handoff.md#Next-Session
- abstraction up: `skills/public/release/scripts/publish_release_claims_review.py` marker topology | decision: same waste, fix now | proof: both descendant and merge-parent paths could move the prepared boundary | follow-up: applied in this candidate
- specialization down: focused release suites | decision: keep | proof: 19 focused topology tests proved the repaired local invariant but did not replace the full closeout | follow-up: none

Structural pattern: release evidence packets can become stale after a verdict
repair. Triggering instance(s): final critique identity changed after #608
topology and routing repairs. Destination: deferred docs/handoff.md#Next-Session.

## Next Improvements

- workflow: regenerate and validate the release critique packet immediately
  after the final code/doc repair, before the last fresh-eye read.
- capability: defer a packet freshness preflight that names uncommitted
  reviewed paths before a release critique is declared complete.
- memory: retain this retro, the refreshed critique, and the handoff's exact
  prepare → claims-review → resume route; all 22 issues remain OPEN.

## Packet Consumed

`charness-artifacts/retro/final-release-boundary-retro-packet.md`

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-13-final-release-boundary-retro.md
