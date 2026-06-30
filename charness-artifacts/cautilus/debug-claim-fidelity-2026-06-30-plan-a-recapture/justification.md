# Operator Log — debug claim-fidelity RE-CAPTURE (post Plan A internalization)

- source-kind: operator-log

## Approval

- Operator (bae.hwidong@corca.ai) authorized this run on 2026-06-30 with the
  explicit request "라이브 재캡처 합시다" (run the live re-capture). This is the
  log-backed behavior-proof request the ask-before-run policy requires:
  `plan_cautilus_proof.py --json` returned `next_action: "none"` (working tree is
  clean post-commit) and `must_ask_before_running: true`; this log is the
  `--justification-log` override naming the failing basis below.

## Failing log under test (the basis)

- The 2026-06-30 re-capture
  (`charness-artifacts/cautilus/debug-claim-fidelity-2026-06-30-recapture/finding.md`)
  graded `falsifiable-hypothesis-before-fix` **FAIL**: a real /charness:debug run
  authored its conclusion from `static scan only` with no reproduction and no
  cheapest-disconfirming check, because the `## Reproduction`/`## Hypothesis`/
  `## Verification` scaffold seeds were bare `TODO`. That is the failing behavior
  under test here.

## What changed (why re-capture now)

- Plan A (commit ce3caa6c): the scaffold now seeds those three sections with method
  hints (`falsifiable claim ... | disconfirmer:`, smallest-repro-or-
  `n/a — could not reproduce`), and `validate_debug_artifact.py` requires the
  current `latest.md` `## Hypothesis` to carry a `disconfirmer:` honesty marker.
  This re-capture tests whether a competent run now fills `disconfirmer:` with a
  REAL cheapest-refutation (→ `falsifiable-hypothesis-before-fix` PASS) rather than
  static-only (→ FAIL).
- Plan B (commit 853a5174): reference docs compressed (anti-patterns deleted,
  sibling-search/detection-gap slimmed). Floor unchanged
  (`requiredCommandFragments` = [five-steps.md, debug-memory.md]).

## Honest reading guard

- The debug prompt is a TEMPLATE bug CLASS (a non-gitignore-aware scanner); a
  faithful run does real RCA on the repo's scanner code. PASS on the substance set
  requires the run to actually reproduce or run a cheapest disconfirmer before its
  conclusion — NOT just emit the `disconfirmer:` marker with `n/a`. A static-only
  run that fills `disconfirmer: n/a` legitimately still FAILS the OUTCOME assertion;
  the marker is the structure, the assertion is the bar. A MISS is a real
  skill-shape signal — never soften the matcher, the floor, or the assertion.
