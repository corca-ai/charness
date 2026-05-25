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

## Counterfactual Prompts

- Was broad exploration explicitly intended by the user?
- Where should the triage lock have happened?
- Which findings crossed from exploration into `fix now`?
- Which findings should have been deferred or marked false positive?
- After scope lock, which new branches reopened scope without a user decision?
