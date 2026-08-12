# Release Preflight Retro
Date: 2026-08-13
Goal: charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md

## Context

The final release attempt repaired #608's missing pre-publication claims-review
stage, reconciled the duplicate-ratchet backlog, and then ran a locked release
closeout. The release was deliberately not pushed or published: the changed-line
mutation-coverage gate still found uncovered lines across the accumulated
unreleased range.

## Window

`860abdc3..a17526dc`, with final verification evaluated against `origin/main`.
The original 22 tracker issues remain OPEN; this retro makes no issue-closure,
hosted-CI, push, tag, GitHub-release, or installed-consumer claim.

## Evidence Summary

- `f149ad0b` adds the marked prepared-record / claims-review / resume boundary;
  `264ed7a2` declares its cross-namespace evidence ownership.
- Two bounded repair rounds found remote tag/branch topology and claims
  post-publication validation gaps before the implementation was committed.
- `6e95aecf` records the duplicate-ratchet backlog disposition. Its explicit
  scoped baseline update and ordinary gate rerun both report clean.
- `tests/quality_gates/test_release_publish.py`,
  `test_release_publish_resilience.py`, and
  `test_release_publish_critique_artifact.py` passed: **72 passed**.
- The locked closeout's generated coverage report was fresh, but
  `check_changed_line_mutation_coverage.py --base-sha origin/main
  --reuse-coverage` returned nonzero for 11 files, including the new release
  claims-review modules and earlier unreleased work. That is the release
  blocker.

## Waste

The first locked closeout exposed a stale duplicate-ratchet baseline; its 18
families mixed three #608-adjacent shapes with fifteen older changes. The
baseline was reconciled only after an explicit family-by-family triage and a
fresh-eye check, rather than bypassing the gate.

The focused release suite initially failed one legacy closeout-recovery
expectation because the fixture had not supplied the newly mandatory review
artifact. Supplying the fixture's already-committed review record restored the
test's intended assertion. This was useful compatibility discovery, not proof
that the whole unreleased range is publishable.

## Critical Decisions

1. **Preserve the #608 pause.** A committed local release record is now a
   reviewable state, never permission to tag, push, or create a release.
2. **Keep the full changed-line gate authoritative.** The 72 focused tests prove
   the release subsystem; they do not discharge coverage for the other nine
   blocked source surfaces.
3. **Record historical duplicate backlog honestly.** Independent idioms were
   classified in the overlay, while nine non-identical maintenance candidates
   were named in a scoped baseline action instead of called intentional.

## Trends vs Last Retro

The earlier session retro correctly warned against treating local proof as a
terminal publication claim. This window repeated the same boundary in a sharper
form: a focused green suite and a clean duplicate gate still cannot substitute
for the full range's changed-line evidence.

## North Star Alignment

The release remained aligned with the north star's irreversible-boundary rule:
the #608 review uses a distinct reviewer/evidence commit, and the later
coverage refusal is treated as a reason to stop rather than as a documentation
defect to explain away. The cost was additional local work, but no wrong public
state escaped.

## Expert Counterfactuals

**Douglas Engelbart — system-improving-itself.** The release helper (tool), the
claims-review record and coverage receipt (language), and the closeout sequence
(method) must be designed together. The next release candidate should produce
changed-line coverage early, before final-release critique and bump preparation,
so the method routes effort to missing proof while the diff is still small.

**Falsification-first operator lens.** Ask “what exact unreleased source line
has no executed proof?” before treating any subsystem suite as a release gate.
That question would have found the 11-file failure before the final closeout.

## Sibling Search

- same layer: `scripts/check_changed_line_mutation_coverage.py` and its
  producing closeout command | decision: follow up in this goal | proof: the
  producer was fresh but the reported range still names eleven files |
  follow-up: restore coverage before release.
- abstraction up: `scripts/run_slice_closeout.py` pre-lock advisory | decision:
  valid capability follow-up | proof: it warns about new mutation-pool modules
  but does not expose accumulated-range gaps until the final check |
  follow-up: defer design until the required coverage is restored.
- specialization down: release focused tests | decision: keep | proof: the
  fixture repair returned 72 passing tests but correctly did not suppress the
  full-range coverage blocker | follow-up: none.

Structural pattern: a focused proof result was narrower than the final changed
range. Triggering instance(s): the 72-pass release suite and 11-file
changed-line refusal. Destination: active goal final-verification slice.

## Next Improvements

- **workflow**: Run the changed-line self-check immediately after the first
  mutation-coverage producer for an accumulated release candidate, before final
  release critique or deployment preparation.
- **capability**: Evaluate a bounded closeout report that summarizes uncovered
  changed files at pre-lock time without weakening the final gate.
- **memory**: Keep this retro and `docs/handoff.md` explicit that the next action
  is coverage restoration, not push/release.

## Packet Consumed

`charness-artifacts/retro/2026-08-12-195646-packet.md` was produced but showed
an intentionally clean working tree, so it did not inform changed-range claims;
the committed range and coverage receipt above did.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-13-release-preflight-retro.md
