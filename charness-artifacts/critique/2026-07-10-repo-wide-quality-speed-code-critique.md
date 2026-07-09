# Repo-wide Quality and Speed Code Critique
Date: 2026-07-10

## Execution

- Fresh-eye code critique completed with independent correctness and speed
  angles plus a separate parent-owned counterweight pass.
- Packet Consumed: `charness-artifacts/critique/2026-07-10-repo-wide-quality-speed-code-packet.md`
- Target: `references/code-critique.md`

## Decision Under Review

Accept the S1/S2 implementation diff as the correctness and performance bundle
for the v0.64.0 release candidate.

## Diff Scope

Usage-feedback structural validation/reconciliation and product-review counting;
bootstrap-runtime healthy reuse; concurrent Markdown advisory/blocking scans;
plugin mirrors and focused regressions.

## Capability at Stake

Product-review facts and feedback files must remain trustworthy while common CLI
and proof paths get faster without weakening repair or gate failure semantics.

## Angles

- Weinberg/Gawande reviewed root cause, data ownership, windowing, threshold
  uniqueness, no-write rejection, mirror parity, and regression strength.
- Jackson/Gawande reviewed bootstrap contract/version/module/env/fallback/cache
  behavior and Markdown PID, channel, ordering, and exit semantics.
- Counterweight rejected assertion aesthetics, speculative invalid direct callers,
  and extra shell hardening while retaining one concrete launcher exception bug.

## Findings

- The feedback changes correctly keep delivery-only dimensions and evidence,
  apply delivery and feedback timestamps independently, preserve outcome-only
  friction, deduplicate episode thresholds, and structurally validate history.
- The Markdown overlap preserves advisory-first output, MarkdownLint stderr and
  blocking exit status, and cleans up only still-running child PIDs.
- Act Before Ship: an existing non-executable/corrupt bootstrap launcher caused
  `subprocess.run()` to raise `OSError`, bypassing the promised unhealthy-to-repair
  fallback. The diff now catches `OSError` and a real POSIX regression proves it.
- Bundle: the unused-on-fast-path `requirements_file` shape check now explains
  that it preserves authoritative bootstrap contract eligibility.

## Counterweight Triage

### Act Before Ship

- F1 launcher execution exception fallback — fixed and regression-tested.

### Bundle Anyway

- F2 contract-shape comment — applied.
- F3 out-of-window feedback confidence-gap assertion — not bundled; existing
  tests already prove window exclusion and denominator behavior.

### Over-Worry

- No assertion-style rewrite or additional interrupted-shell mechanism is needed.

### Valid but Defer

- Defensive reconciliation for arbitrary schema-invalid direct callers waits
  until a supported caller bypassing validated readers is identified.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness:1204 | action: fix | note: catch launcher execution OSError and fall through to authoritative bootstrap repair
- F2 | bin: bundle-anyway | evidence: moderate | ref: charness:1173 | action: document | note: explain requirements_file shape validation on the reuse-only path
- F3 | bin: bundle-anyway | evidence: weak | ref: tests/test_usage_episodes_report.py | action: document | note: exact confidence-gap assertion is redundant with current window and denominator proof
- F4 | bin: over-worry | evidence: weak | ref: tests/charness_cli/test_bootstrap_runtime.py | action: document | note: env assertion style does not justify code churn
- F5 | bin: valid-but-defer | evidence: moderate | ref: scripts/usage_episode_feedback.py | action: defer | note: arbitrary invalid direct reconciliation callers are not a supported production path
- F6 | bin: over-worry | evidence: strong | ref: scripts/check-markdown.sh | action: document | note: no extra shell hardening without an interrupted-process reproduction

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `model=gpt-5.5`, `reasoning_effort=medium`, `service_tier=priority`.
- Host exposure state: requested_fields_sent
- Application state: spawn surface accepted requested fields; runtime model metadata was not independently exposed.

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

- Producer: mixed usage event stream, bootstrap contract/launcher, and two Markdown checks.
- Consumer: product-review packets, repo-script calls, and standing quality results.
- Owning surface: shared usage records/reconciliation, existing bootstrap repair
  flow with a read-only root fast path, and mirrored Markdown gate runner.
- Verdict: owned-correctly

## Defect Class Cross-Link

`charness-artifacts/retro/recent-lessons.md` environment leakage and fallback
ownership traps apply to the bootstrap probe isolation and repair handoff.

## Capability Gap

None; existing shared readers, bootstrap repair owner, mirror sync, and quality
gate surfaces own the required behavior.

## Deliberately Not Doing

- No lazy urllib, changed-file Markdown cache, parser rewrite, pytest worker
  change, broad subprocess consolidation, or arbitrary-input reconciliation API.

## Pre-Merge Action

F1 and F2 are complete. Re-run the focused suite, whole-tree critique validator,
repo-copy invariant, and full standing pytest before commit.

## Next Move

Freeze the implementation commit after those gates pass, then produce the final
quality artifact and verification lock before release preparation.
