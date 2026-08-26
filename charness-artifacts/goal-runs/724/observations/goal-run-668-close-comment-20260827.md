## Decision — remove the false timing blocker

JTBD: stop a machine-dependent pytest wall-time sample from blocking an
otherwise correct local push or release lane.

Decision: close #668 as a Charness-owned local quality-policy decision. The
profiling and standing-set reduction named by the trigger were measured and
did not move the in-gate signal; another budget relevel would not address the
contention source. The timing arm is therefore advisory in normal and release
`run-quality` orchestration, while direct checker invocation and malformed
configuration/profile/universe errors remain blocking.

Implementation: `8241d9922c37e8e63ab407091931a10ff3c839e6` adds explicit
`--advisory` behavior to the canonical/plugin runtime-budget checkers, routes
the local and release runner through that mode, retains visible `ADVISORY:`
output, and adds focused regression coverage.

Boundary: Charness owns this local checker and runner-policy decision. The
remaining scheduler/concurrency redesign, any CPU-normalized metric, hosted or
remote enforcement, and consumer-repository rollout are separate work.

Behavior #668: local-only-by-contract — the clean named-branch proof returned
`86 passed` in the focused suite, `86 passed` through the standing wrapper, and
`2 passed` in the selected combined quality gate. The advisory fixture retained
the overrun signal while returning success; configuration and universe-error
fixtures remained blocking.

Probe record #668: local-only-by-contract

Verification carrier: the proof receipt is
`charness-artifacts/goal-runs/724/observations/goal-run-668-runtime-budget-advisory-20260827.md`.
The issue body was updated through the #724 Goal Run provider and its
`body_verified: true` readback was recorded before this close.

Explicit non-claims: no scheduler/concurrency redesign, CPU-normalized metric,
4-core rebaseline, hosted/remote CI enforcement, consumer adoption, release
publication, push, tag, installed-host behavior, clean parent worktree, or
fresh-eye review is claimed. Changed-line proof was not used as a universal
implementation gate. Forced fresh-eye, handoff, and micro-slice rituals were
omitted by operator direction.

AI-provenance: authored by an agent session.

Manual fallback reason: operator-directed-manual-close.
