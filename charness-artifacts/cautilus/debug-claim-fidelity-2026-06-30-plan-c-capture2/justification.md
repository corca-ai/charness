# Operator Log — debug claim-fidelity capture #2 (Plan C n=2 gate)

- source-kind: operator-log

## Approval

- Operator (bae.hwidong@corca.ai) authorized this run on 2026-06-30 with the
  explicit request "1 합시다. 코틸러스 캡처 허용" (do handoff item 1; allow the
  Cautilus capture). This is the log-backed behavior-proof request the
  ask-before-run policy requires: `plan_cautilus_proof.py --json` returned
  `next_action: "none"` (working tree is clean post-commit) and
  `must_ask_before_running: true`; this log is the `--justification-log` override
  naming the failing basis below.

## Failing log under test (the basis)

- The 2026-06-30 re-capture
  (`charness-artifacts/cautilus/debug-claim-fidelity-2026-06-30-recapture/finding.md`)
  graded `falsifiable-hypothesis-before-fix` **FAIL**: a real /charness:debug run
  authored its conclusion from `static scan only` with no reproduction and no
  cheapest-disconfirming check, because the `## Reproduction`/`## Hypothesis`/
  `## Verification` scaffold seeds were bare `TODO`. That is the failing behavior
  the Plan A internalization fixed.

## What this capture proves (n=2 gate)

- Capture #1 (`debug-claim-fidelity-2026-06-30-plan-a-recapture/finding.md`)
  flipped `falsifiable-hypothesis-before-fix` FAIL → **PASS** at n=1 after Plan A
  (ce3caa6c) + Plan B (853a5174) landed: the run built a real reproduction and ran
  an explicit cheapest-disconfirmer before its conclusion.
- This is **capture #2**: an independent clean live `/charness:debug` capture on
  the SAME spec prompt at HEAD (carrying Plan A + Plan B). A second confirming PASS
  is the gate the handoff sets before retiring `five-steps.md` from the floor
  (let the substance assertion be the bar; doc-opening is the weak proxy).

## Honest reading guard

- The debug prompt is a TEMPLATE bug CLASS (a non-gitignore-aware scanner); a
  faithful run does real RCA on the repo's scanner code. PASS on the substance set
  requires the run to actually reproduce or run a cheapest disconfirmer before its
  conclusion — NOT just emit the `disconfirmer:` marker with `n/a`. A static-only
  run that fills `disconfirmer: n/a` legitimately still FAILS the OUTCOME assertion;
  the marker is the structure, the assertion is the bar. A MISS is a real
  skill-shape signal — never soften the matcher, the floor, or the assertion. The
  floor doc-skip (coverage ~1/10) is the EXPECTED, consistent result, not a
  regression: the thesis is that a competent run reaches the structural outcome via
  the scaffold STRUCTURE without opening the canonical reference docs.
