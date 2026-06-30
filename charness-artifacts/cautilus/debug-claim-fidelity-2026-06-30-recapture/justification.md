# Operator Log — debug claim-fidelity RE-CAPTURE (post resolved-state fix)

- source-kind: operator-log

## Approval

- Operator (bae.hwidong@corca.ai) authorized this run on 2026-06-30 via the
  achieve goal's gated Slice 3 question: "Run full re-capture + judge". This is the
  operator-backed log-backed behavior-proof request the ask-before-run policy
  requires; `plan_cautilus_proof.py --json` returned `next_action: "none"`,
  `must_ask_before_running: true`, and this log is the `--justification-log` override.

## Failing log under test (the basis)

- The 2026-06-30 capture was a MISS:
  charness-artifacts/cautilus/debug-claim-fidelity-2026-06-30/finding.md. A real
  /charness:debug run honored the TASK but skipped its planner-required reads
  (five-steps.md, debug-memory.md), aggravated by the planner mis-moding to
  continue-existing-artifact (a stale closed current pointer hijacked the fresh bug).

## What changed (why re-capture now)

- Slice 2 (commit 9981d7a22ab4a3a98804461ecc706f5b71ad3201) added a resolved-state planner guard: the debug
  planner now continues only when Resolution != resolved, so the migrated closed
  #365 current pointer routes fresh-investigation-with-prior-memory and emits
  five-steps.md + debug-memory.md as required reads (unburied). This re-capture
  tests whether a competent run now HONORS that routing → a PASS attempt.
- Slice 1 added evals/cautilus/debug-claim-fidelity/outcome-assertions.json, which
  grades SUBSTANCE (Detection Gap / Sibling Search / Prevention) via the judge.

## Honest reading guard

- PASS = the run opens the floor reads (five-steps.md + debug-memory.md) AND the
  outcome judge confirms substantive Detection Gap / Sibling Search / Prevention.
  A MISS on any axis is a real skill-shape signal — NEVER soften the matcher or the
  floor. The debug prompt is a TEMPLATE bug CLASS (a non-gitignore-aware scanner);
  a faithful run does real RCA on the repo's scanner code (repo_file_listing.py etc).
