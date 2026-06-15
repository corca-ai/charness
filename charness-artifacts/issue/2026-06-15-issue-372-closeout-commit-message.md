fix(debug): require disconfirmers before diagnosis claims

Close #372.

Classification: bug.
Issue closeout carrier: direct-commit.
Issue: #372 debug skill: add a disconfirmer-first rung for
absence/attribution/liveness/frequency claims.

JTBD: debug and bug-class issue-resolution workflows must not promote absence,
attribution, liveness, or frequency claims from partial evidence before running
the cheapest falsifier; liveness and wired/running claims should prefer runtime
state over source inference.

Root Cause: the debug contract had a named-target runtime verification rule,
but lacked a reusable claim-type gate for absence, attribution, liveness, and
frequency conclusions. That let agents satisfy the narrower named-target rule
while still treating narrow source or recent-window evidence as confirmed
diagnosis.

Debug Artifact:
`charness-artifacts/debug/2026-06-15-issue-372-disconfirmer-first-debug.md`.

Siblings: same-layer named-target verification was complementary, not a
replacement; bug-class issue causal review is the abstraction-up consumer of
debug substrate. Decision: add the disconfirmer-first rung to debug and wire the
same substrate into issue causal review. Proof: the focused debug reference test
asserts the debug workflow hook, the four claim triggers, runtime/source
preference, output fields, and issue causal-review prompt/Lens 1 cite-chain.

Implementation: added `skills/public/debug/references/disconfirmer-first.md`,
linked it from `skills/public/debug/SKILL.md`, added it to
`skills/public/issue/references/causal-review.md`, synced plugin mirrors, and
expanded `tests/quality_gates/test_debug_rca_reference_cite_chain.py`.

Prevention: the quality-gate test now fails if debug drops the
disconfirmer-first hook or if issue causal review stops naming the substrate
needed to prevent premature absence/attribution/liveness/frequency conclusions.

Tests: focused debug RCA/reference tests passed; skill, packaging,
markdown/docs/secrets, deterministic prompt-proof, public-skill validation,
debug artifact/index, critique artifact, and changed-surface checks passed
locally. Broad non-release pytest is deferred to the final bundle proof per the
active goal's slice policy.

Critique: charness-artifacts/critique/2026-06-15-issue-372-disconfirmer-first-resolution.md
