# Phase-Aware Efficiency

Use this when a retro discusses token pressure, tool-call volume, repeated file
reads, broad exploration, or any other efficiency claim.

## Rule

Do not label breadth as waste until the retro identifies the phase intent.
Broad exploration can be valuable when the user asked for unknown-unknown
discovery, fresh-eye critique, or surface mapping. The waste question is where
the session failed to convert that breadth into a locked next action.

## Phase Check

Classify high-cost activity by phase before prescribing a fix:
`Exploration -> Triage -> Implementation -> Verification`.

- `exploration`: mapping surfaces, reading context, gathering candidates, or
  asking reviewers to find unknown risks.
- `triage`: sorting findings into `fix now`, `deferred`, `needs user call`, and
  `false positive`.
- `implementation`: mutating only the `fix now` scope unless the user reopens
  scope.
- `verification`: proving the implemented scope with focused checks first, then
  broader gates when the slice is stable.

If phase is inferred from tool logs, command families, or transcript shape,
mark the claim strength as `strong`, `moderate`, `weak`, or `contested`.

## Triage Lock

Exploration output is a candidate issue list, not a patch plan. Before
implementation, name the triage lock:

- what entered `fix now`
- what moved to `deferred`
- what needs a user decision
- what was rejected as a false positive

After lock, new branches are drift unless the user explicitly reopens scope.
Record them as deferred notes or scope decisions instead of silently adding them
to the implementation loop.

## Evidence Signals

Host-specific cost maps and log probes are evidence pointers, not conclusions.
Keep measured, proxy, and unavailable signals separate:

- `measured`: directly observed counts or fields from the selected source
- `proxy`: command size, repeated families, requested output limits, or inferred
  phases
- `unavailable`: costs the source cannot honestly provide

Do not store one session's scope narrowing, thread ids, or intended breadth in
the adapter. Put that context in the retro narrative or command flags.
For Codex session detail, `$SKILL_DIR/scripts/audit_codex_session.py` may supply
thread-scoped evidence pointers; its phase labels still require this review
before anything is called waste.

Cached input tokens are not a waste conclusion by themselves. Treat them as a
context-pressure signal only when paired with evidence such as compactions,
high-token turns, repeated commands, polling, or rerun-heavy validation cadence.

For goal closeouts, prefer a goal-window audit over a full-thread audit when the
artifact records a `Host metric window:` evidence line with `started_at`,
`completed_at`, and exactly one host session-file field (`codex_session_file`
or `claude_session_file`). A full-thread audit remains a pressure signal, not a
per-goal cost total.

## Gate-Baseline Runtime

Cadence is not the only runtime-waste axis. A broad gate run at the right time
(final-bundle proof) can still be slow *by design* — pre-push, full suite, and
coverage are the usual cases. That cost does not become "necessary safety cost"
just because the gate passed and the cadence was correct: a slow-but-passing
gate is gate-baseline / code-quality debt, and the retro names it under the
`gate-baseline runtime` waste category (`section-guide.md`) instead of letting
its measured seconds sit unflagged in an Evidence line.

- Measure the gate's runtime against a budget; over budget is waste to *route*,
  not to absorb. The structural fix belongs to the gate-implementation owner
  (for example coverage or duplicate-detector cost), so pair the finding with a
  `## Sibling Search` / structural-follow-up destination, never memory-only.
- Honest capture scope: `run_slice_closeout.py` records `elapsed_seconds` only
  for the gates it runs itself (sync / verify / broad-pytest) and surfaces an
  over-budget verdict in its JSON `gate_runtime_advisory` field. The host
  pre-push hook runs as its own process, so its runtime is NOT in that payload —
  surface it as an explicit non-claim (or capture it from the hook) rather than
  implying it was measured.

## Counterfactual Prompts

- Was broad exploration explicitly intended by the user?
- Where should the triage lock have happened?
- Which findings crossed from exploration into `fix now`?
- Which findings should have been deferred or marked false positive?
- After scope lock, which new branches reopened scope without a user decision?
- Was a docs-only push actually required for the issue-resolution carrier, or
  was it a later lifecycle/audit artifact after the carrier was already
  verified?
