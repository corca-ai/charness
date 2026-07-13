# Open Issues #433, #436, and #437 Resolution Critique
Date: 2026-07-14

## Decision Under Review

Close #433 and #436 from their already-landed production fixes and close #437
with a test-only patch that makes the scheduled non-release producer cover the
custom-HOME seam and kills enough reported parser survivors to restore the
fixed-sample score above 80%.

## Execution

Two contrasting code-critique angles ran read-only, followed by a separate
counterweight pass. Parent-side reviewer-boundary verification reported no
worktree, index, or HEAD drift after any reviewer.

## Packet Consumed

`charness-artifacts/critique/2026-07-14-issues-433-436-437-resolution-packet.md`

## Failure Angles

- Problem framing and carrier legibility: distinguish historical production
  fixes from today's proof patch so future issue readers do not attribute all
  behavior to one convenient test-only diff.
- Diagnostic and operational ownership: check the custom-HOME producer,
  `run_claude` transport, doctor consumer, mutation selector, and close boundary
  rather than accepting a producer-local green.
- Counterweight: reject an added production refactor, duplicate live-host proof,
  exhaustive writer audit, or mandatory scheduled rerun unless current evidence
  makes one necessary.

## Findings

- #433 behavior is owned by the complete issue carrier preflight introduced in
  `041aa380` and hardened in `32a15c19`; today's focused release tests re-exercise
  the final commit-message consumer before mutation.
- #436 behavior is owned by `ea810544`: tracked sync drift stops before the first
  verify command, while clean sync and sync-command failure retain their prior
  paths.
- #437's changed-line gap came from correct two-home tests living behind
  `release_only`. The new focused module reaches every named `charness` target
  through the mutation producer's own coverage helper without moving the
  expensive release fixtures into the standing suite.
- A targeted Cosmic Ray session killed all five `required=True` mutants in
  `scripts/capability_catalog.py` plus a reported dispatch comparison. Applied
  to the issue's fixed 117-mutant sample, six fewer survivors changes 89/117 to
  95/117 (81.2%). This is not a fresh scheduled/provider run.

## Counterweight Pass

- Act Before Ship: every closeout carrier must map issue, JTBD, landed fix, and
  current behavior proof; the #437 commit must not claim it introduced the
  #433/#436 production changes.
- Bundle Anyway: carry the targeted mutation arithmetic and the explicit
  scheduled-run non-claim in the #437 carrier.
- Over-Worry: more custom-HOME tests are not justified; direct helper,
  call-site, and doctor-consumer tests already form a three-layer seam proof.
- Over-Worry: no production refactor, release, live Claude host run, or
  exhaustive generated-writer audit is required for these issue boundaries.
- Valid but Defer: none. The next scheduled run is useful monitoring, not an
  unresolved implementation obligation.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/critique/2026-07-14-issues-433-436-437-resolution-packet.md | action: fix | note: bind each issue to its own landed fix and proof in the final carrier
- F2 | bin: over-worry | evidence: strong | ref: tests/charness_cli/test_claude_home_unit.py | action: defer | note: no additional custom-HOME test layer is needed
- F3 | bin: bundle-anyway | evidence: contested | ref: tests/test_capability_catalog.py | action: document | note: carry targeted score arithmetic and do not claim a fresh scheduled run
- F4 | bin: over-worry | evidence: moderate | ref: charness-artifacts/debug/2026-07-13-custom-home-claude-state-leakage.md | action: defer | note: live-host and release proof exceed this test-only slice
- F5 | bin: over-worry | evidence: strong | ref: charness-artifacts/debug/2026-07-11-issue-433-release-closeout-carrier.md | action: defer | note: do not rewrite already-landed production fixes

## Issue Behavior Verdict Recommendations

- #433: confirm through the focused release fixture that stitches a complete
  bug carrier into the final commit-message consumer before release mutation.
- #436: confirm through the dirty-sync and clean-sync executor fixtures, which
  observe whether the broad producer is reached.
- #437: confirm through the repo mutation coverage producer plus targeted Cosmic
  Ray outcomes; disclose that the future scheduled provider run did not run.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `model=gpt-5.5`, `reasoning_effort=medium`, `service_tier=priority`.
- Host exposure state: requested_fields_sent
- Application state: the spawn surface accepted the requested fields; provider application metadata was not exposed.

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

- Producer: the `charness` custom-HOME subprocess seam and capability-catalog argparse surface.
- Consumer: doctor/install/reset observations and the scheduled mutation coverage/score consumers.
- Owning surface: production remains in `charness` and `scripts/capability_catalog.py`; focused repo tests own executable proof.
- Verdict: owned-correctly

## Deliberately Not Doing

- No production refactor, new gate, release, live Claude-host claim, or broad
  generated-writer audit.
- No claim that a new scheduled/provider mutation run passed.

## Next Move

Persist the issue-specific carriers, run focused and repo closeout gates, commit
the #437 patch, push, then verify GitHub state separately from each behavioral
verdict.
