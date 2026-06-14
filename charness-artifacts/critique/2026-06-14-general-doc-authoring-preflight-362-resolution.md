# Critique Review
Date: 2026-06-14

## Decision Under Review

Resolution critique for GitHub issue #362: shipping
`scripts/check_doc_authoring_preflight.py` (an aggregate author-time preflight
for general doc/markdown surfaces) plus its authoring-flow wiring, as the fix
that resolves the #362 churn class. Recurrence-focused: does the fix resolve
the issue's class without introducing drift or a regression, and does it stay
the describe-first affordance the issue asked for rather than a new blocking
floor?

## Failure Angles

- **Drift between forecast and gate.** If the preflight re-implemented or
  hand-copied any check, its verdict could diverge from what the commit gate
  enforces — the worst failure for a forecast tool (it would train false
  confidence). The reviewer probed markdownlint (the only subprocess/parse
  path), the doc-link parity, and the live length constant.
- **Silent-skip reads as a pass.** A missing markdownlint binary, an unreadable
  file, or a non-`.md` path could exit 0 and look clean.
- **Affordance becomes a precondition.** A future hand could wire the tool into
  the blocking commit gate, converting the absorb into a serial floor — the
  exact anti-pattern the issue's Floor-Addition Restraint framing warns against.
- **Recurrence not actually closed.** The forecast might miss one of the four
  classes the issue named (markdownlint incl. MD004 + wrapped span, doc-link
  pathy-ref, length cap), leaving part of the churn uncovered.

## Counterweight Pass

- The drift angle is the real one and was the reviewer's hardest probe; it held
  (no-drift confirmed across all four classes — see Fresh-Eye Satisfaction). Not
  a blocker.
- Silent-skip: probed live — non-`.md`/missing/outside-repo paths exit 2 with an
  error; missing markdownlint degrades to an explicit `WARN` (not a silent
  pass). Not a blocker.
- Affordance-becomes-precondition is a *future* risk, already fenced by a test
  asserting absence from `staged_commit_gate_plan.py`. Over-worry for now;
  the guard exists.
- Recurrence coverage: all four classes verified surfaced in one pass by the
  broken-fixture test and the reviewer. Closed.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: bundle-anyway | evidence: moderate | ref: scripts/check_doc_authoring_preflight.py:141 | action: document | note: single-file markdownlint scope relies on per-file rule semantics; documented with a code comment so a future cross-file rule does not silently diverge (applied this run).
- F2 | bin: over-worry | evidence: weak | ref: scripts/slice_closeout_advisories.py:128 | action: defer | note: advisory fires for any docs/*.md incl. docs/generated/*; harmless (running the preflight there is low-value, not wrong). No change.
- F3 | bin: valid-but-defer | evidence: strong | ref: cff2ad07 | action: file-issue | follow-up: https://github.com/corca-ai/charness/issues/363 | note: #362 was auto-closed early by a close-keyword in a non-fix commit body — a distinct, pre-existing process gap outside this fix's scope; filed as the off-goal finding #363.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage bounded fresh-eye reviewer (separate agent context, read-only shared worktree).
- Requested spawn fields: intent, changed files + owning/generated surfaces, expected invariants, non-claims, out-of-scope lines, four reviewer questions (Q1 markdownlint drift, Q2 length-cap drift, Q3 doc-link parity, Q4 crash/silent-pass).
- Host exposure state: applied
- Application state: host-confirmed: subagent a33aa4c99291a6468 completed; returned a structured verdict (BLOCKERS/NITS/Q1-Q4/recommendation) citing file:line evidence and live reproductions.

## Fresh-Eye Satisfaction

Reviewer verdict: **SHIP — no blockers.** Concrete signals behind it:
- Q1 (markdownlint drift): NO drift — reproduced markdownlint-cli2 v0.21.0 output
  (violations on stderr, banner on stdout; both scanned; banner no-matches the
  regex); `MD013: false` config applies with `--no-globs` from `cwd=repo_root`
  (verified: a 170-char line → 0 errors with config, 1 without). Could not
  construct a doc where forecast disagrees with the gate.
- Q2 (length-cap drift): NO — cap read live via `MAX_ARTIFACT_LINES` and enforced
  through the gate's own `validate_max_lines`; handoff 70/70 correct, general doc
  resolves to no floor (no invented cap).
- Q3 (doc-link parity): exact — identical indices + the identical three reused
  checks as `check_doc_links.main()`; collect-all is a superset of the gate's
  fail-fast, not a fork.
- Q4 (crash/silent-pass): none — non-`.md`/missing/outside-repo → exit 2; missing
  markdownlint → explicit `WARN`; exit code mirrors `report.blocked` (RC=1 when
  only length is over).
Nits were cosmetic; F1 was applied this run (the per-file-rule comment).
