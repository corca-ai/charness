Closed by [charness 6.0.0](https://github.com/corca-ai/charness/releases/tag/v6.0.0).

**What shipped.** The drift message no longer instructs edits to the surfaces #596
superseded; it names the surface a reader can actually change.

**How this verdict was reached, stated exactly.** This issue has NO fresh reproduction
in the slice that closes it. Nor does any review carry a finding about this issue's
OWN surface: the 2026-08-14 cohort closeout covered the #618-#624 range without a
per-issue entry for it, and the release critique's F13 records the same class recurring
elsewhere rather than a finding about the drift message. What supports this close is the repair itself, readable in the
tree and pinned by `tests/test_probe_drift_message.py`, which asserts the superseded
surfaces now sit under the do-not-touch heading. That is weaker than an executed
reproduction, and it is recorded here rather than presented as equivalent.

Behavior #624: not verified by fresh reproduction in this slice and named by no
per-issue finding; carried on the shipped message-surface repair and its standing test,
named above.

Critique #624: charness-artifacts/critique/2026-08-16-s7-6-0-0-release-execution.md

AI-provenance: agent-drafted by Claude (Opus 5) operating the charness `issue` skill; every verdict above was produced by executing the named command in this worktree or is cited to the review that produced it.
