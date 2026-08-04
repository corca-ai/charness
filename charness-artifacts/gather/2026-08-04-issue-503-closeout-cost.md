# Gathered GitHub issue #503

Source: https://github.com/corca-ai/charness/issues/503
Canonical source identity: GitHub issue 503 in corca-ai/charness
Knowledge Capability: Preserve the primary observed problem, evidence, candidate direction, scope, and non-claims for the #503 closeout-cost decision.
Freshness: captured 2026-08-04 from GitHub issue JSON; issue state at capture was OPEN.
Access Mode: authenticated `gh issue view --repo corca-ai/charness --json number,title,state,body,labels,createdAt,updatedAt,url,author`.
Route: the generic public URL route was attempted first and returned a GitHub captcha; the authenticated `gh` route supplied the captured source.

## Captured source facts

### Observed problem

The local closeout telemetry stream keeps recording recurring gate-runtime and
over-slice costs after the related efficiency work was considered complete.
The issue is not that a gate failed: the gates pass, but the recurring cost is
not carried into a tracked owner for deciding whether the cadence, scope, or
implementation should change.

### Evidence

`python3 /home/hwidong/.codex/plugins/cache/local/charness/3.1.1/skills/retro/scripts/mine_closeout_telemetry.py --repo-root .`
reported 1320 records and four recurring findings:

- the standing quality suite: 16 occurrences, peak 475.46 seconds;
- the release-test bundle: 4 occurrences, peak 152.15 seconds;
- the standing pytest runner: 4 occurrences, peak 208.32 seconds;
- over-slice closeouts: 37 occurrences, with a peak run of 4.

The current Slice B standing run was 7028 passed in 42.76 seconds, but that
single run does not explain or retire the recurring historical signal.

Related completed work includes #367 (local-gate-cost vs CI-recoverability
triage and command-timing ingestion) and #434 (an execution-efficiency
baseline for goals). The recurring post-closeout signal remains observable in
the repo's own telemetry after those issues closed, so this is a follow-up
observation rather than a claim that either issue was ineffective in its
original scope.

### Impact

Maintainers repeatedly pay slow verification cost and carry slices beyond the
intended work-unit boundary without a durable decision about ownership or
budget. The recent-lessons digest is not a sufficient destination for a
recurring item because it decays and does not assign tracked work.

### Candidate direction (non-binding)

Give the recurring telemetry class an owning quality/achieve decision: for
example, define a measured budget and route each recurring command to a phase
owner, or record why its cost is intentionally retained. The issue does not
choose batching, parallelism, CI relocation, or a gate rewrite in advance.

### Scope and non-claims

This is local Charness telemetry only. It does not establish that the gates are
wrong, that a particular optimization is safe, or that another repository sees
the same cost. It records a recurring signal for a future bounded decision.

## Captured vs human confirmation

Captured: issue number, title, body, state, labels, timestamps, URL, and author
through authenticated `gh`.
Human confirmation: none required for reading this public issue record.

## Open gaps

Issue #503 is context and candidate direction, not the Slice A decision. The
local stream, its producer, the final consumer, and the preservation boundary
still need to be measured and named by the goal.
