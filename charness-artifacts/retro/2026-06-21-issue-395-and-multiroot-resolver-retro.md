## Mode

session

## Context

One pickup session that resolved three user-sequenced picks: GitHub **#395**
(dup-ratchet `family_id` churn, bug), **chunk-2** (nose 0.14.0 `--root` multi-root
clone resolver — a quality-contract change), and **chunk-1** (nose 0.14.0 rollout,
ops). What matters next: the deferred **D30** id-rotation affordance and the
other-machine `charness update all` rollout.

## Evidence Summary

- Commits: `6658acec` (#395), `91aae959` (chunk-2), `67fb6ef7` (handoff).
- Artifacts: debug `2026-06-21-dup-ratchet-family-id-rotation.md`; critiques
  `2026-06-21-issue-395-dup-ratchet-resolution.md` +
  `2026-06-21-quality-nose-multiroot-resolver.md`; `deferred-decisions.md` D30.
- The gate/validator failure-loop counts below are **direct lived-session
  observation** (a proxy), not a host-log-probed token/turn measurement.

## Waste / The Miss

1. **Re-baseline churn from un-batched scanned-file edits.** Editing scanned
   clone-member files (`dup_ratchet_lib.py`, `nose_baseline_lib.py`) rotated
   `family_id`s and forced a re-baseline + re-verify cycle **three** times in #395
   (initial edits, then critique-fix edits, then more) where batching all doc edits
   before a single `--write-baseline` would have cost one cycle. The irony: this is
   exactly the #395 bug (any scanned-file edit rotates ids) biting my own fix. I
   only started batching after already paying for two cycles.
2. **Strict-validator artifacts authored freeform, then shape discovered via serial
   gate failures.** The #395 closeout hit four gate failures in series: anchor guard
   (`#395` inside a portable package) → `validate-closeout-draft` (missing
   JTBD/root_cause/prevention/siblings markers + behavioral verdict + AI-provenance)
   → `validate_critique_artifacts` (missing reviewer-tier-evidence section) →
   `validate-debug-artifact` (canonical 9-section shape — a full rewrite). Each was a
   discover→fix→retry loop; reading the required-shape contract first would have
   collapsed them into one authoring pass.
3. **Minor:** a markdown inline-code-span line-wrap was caught at commit twice.

## Critical Decisions

1. **Reproduced the bug empirically before designing (#395).** Two controlled
   temp-copy experiments (EOF comment → no rotation; line-shift above span →
   rotation) located the offset-folding root cause precisely and **falsified
   solution (a)** — without that proof I might have trusted the issue's hypothesis or
   chased a content-only re-key nose cannot support.
2. **Escalated chunk-2 to the user when its premise broke.** "Collapse the loop"
   turned out to be a per-root→global semantic change (491→525, a quality-contract
   shift). Owning the #395 (b)-over-(a) scope but **asking** on chunk-2 was the right
   reversible/irreversible boundary — chunk-2 changes what the gate enforces.
3. **Adversarial counterweight caught a false-positive finding.** The chunk-2
   critique's "timeout fail-open regression" rested on misreading the old code (which
   degraded the whole gate on any error identically); the counterweight verified the
   old source and killed it, preventing an unnecessary timeout-config change.

## Expert Counterfactuals

- **Don Reinertsen (flow / batch size):** would have framed the re-baseline churn as
  a batch-size problem — small edit batches each paying a fixed, expensive
  regen+verify transaction cost. Batch all scanned-file edits before the single
  re-baseline and ~2 cycles vanish. I learned this mid-session, only after paying twice.
- **Bertrand Meyer (design by contract):** the closeout artifacts are *suppliers*
  with strict machine contracts (required sections, fields, markers). Meyer's lens:
  read the supplier's contract up front and author to it, instead of authoring
  freeform and letting the validator reject you clause-by-clause.

## Next Improvements

- **workflow:** when a task will edit several scanned clone-member files (e.g. a doc
  sweep across `skills/public/quality/scripts/`), batch ALL edits — including
  critique-driven fixes — before a single `--write-baseline`, not one re-baseline per
  edit round. Applied late this session; make it the default next time.
- **workflow:** for strict-validator artifacts (debug, critique, closeout carrier),
  read the required-shape contract FIRST (`describe_closeout_draft_shape.py --stub`,
  the debug `REQUIRED_SECTIONS`, the `validate_critique_artifacts` reviewer-tier
  fields) and author to it. Applied to *this* retro (read the validator before writing).
- **capability:** an authoring-time `check_artifact_surface_preflight.py
  --report-all` over a *draft* artifact (before staging) would surface all
  required-shape gaps in one pass instead of one commit-attempt at a time. Tracked as
  a follow-up, not built here — the commit-time preflight already backstops it.
- **memory:** "any edit to a scanned clone-member file rotates nose `family_id`s →
  forces a re-baseline" is now both the #395 fix's documented contract and a
  session-workflow constraint: expect rotation, batch the re-baseline.

## Sibling Search

The re-baseline-churn waste is a transferable "small-batch edits to an
expensive-to-regenerate derived surface" pattern. Siblings in this repo's
edit→regenerate→verify loops: the plugin mirror (`sync_root_plugin_manifests`, run
~5× this session), the debug-seam-risk-index, and the two id-set baselines. The
generalizable habit — batch source edits before the single regen+verify — covers all
three; none warrants a new gate (cost is real but bounded), so the lesson is the
batching habit recorded above. The "read the validator contract before authoring"
miss is a parallel sibling for every strict-shape artifact family
(debug/critique/retro/goal/closeout), already covered by Next Improvements #2.

## Persisted
