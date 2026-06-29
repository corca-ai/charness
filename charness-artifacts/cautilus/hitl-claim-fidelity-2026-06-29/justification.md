# Operator Log — hitl claim-fidelity BASELINE capture (first live run)

- source-kind: operator-log

## Approval

- Operator (bae.hwidong@corca.ai) authorized this capture explicitly this session
  (2026-06-29): "hitl 캡처 합시다" — execute item 3 (capture-prioritized rollout)
  START HERE per `docs/handoff.md`: capture `hitl` first, one at a time. This is
  that capture.

## Why this run

- This is the FIRST live capture of the `hitl` claim-fidelity floor. hitl is one
  of the two planner-absent public skills (the other, retro, was just captured and
  given a planner). The static sweep (v0.57.0) calibrated hitl's floor
  `requiredCommandFragments: ["chunk-contract.md"]` but no live run has ever
  exercised it — the floor is a HYPOTHESIS until this capture proves it.
- The claim under test: does a real `/charness:hitl` run honor its central claim —
  route every bounded chunk presentation to `references/chunk-contract.md` at the
  point of need (open the doc, author each chunk against it), or does it author
  chunks from the SKILL.md step-5 inline summary and never open the contract (the
  retro failure shape: a passive prose pointer the run skips)?
- Planner consult (read-only, verbatim): `python3 scripts/plan_cautilus_proof.py
  --repo-root . --json` → `next_action: "none"`, `must_ask_before_running: true`,
  `run_mode: "ask"`. Authorization is the operator's explicit request above; this
  log is the `--justification-log` override the wrapper requires.

## Subject under evaluation (read-only)

- `skills/public/hitl/SKILL.md` + `skills/public/hitl/references/chunk-contract.md`
  (+ the other declared references) at ref `HEAD` (17d05065), via an isolated
  installed-plugin worktree capture. No shared install clone is mutated (#258 hazard).

## Honest reading guard

- PASS = the run opens `chunk-contract.md` (requiredCommandFragments met) AND,
  ideally, presents the first bounded chunk per the contract (line-anchored
  original-material excerpt + Agent Assessment + non-binding Recommended
  Disposition + concrete decision, then pause).
- A MISS is a real signal — the same class as retro's first capture: hitl has a
  passive-pointer shape and needs a deterministic planner that makes
  chunk-contract.md a `required_read`. Escalate to a planner; NEVER soften the
  matcher. A failing baseline here is the EXPECTED, informative outcome that
  drives the item-3 rollout, not a defect in the test.
