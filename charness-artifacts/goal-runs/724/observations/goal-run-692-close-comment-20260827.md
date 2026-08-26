Closes #692

JTBD: make every shipped public-skill adapter initializer predictable: fresh
state initializes once, valid existing state is unchanged, and invalid or
unestablished state refuses before mutation unless explicit force is requested.

Root cause: idempotence was implemented only in the `impl` adapter while the
other 15 entrypoints retained wrapper-specific output or writers, leaving no
single lifecycle owner or uniform refusal receipt.

Debug artifact: `charness-artifacts/debug/2026-08-27-issue-692-adapter-idempotence.md`

Siblings: decision: keep the common initializer as the sole lifecycle owner and
keep every public wrapper thin; proof: the clean named-worktree contract matrix
exercised every initializer, the consumer-classification target passed its full
target, and source/plugin parity matched. `skills/public/issue/scripts/issue_tracker_cli.py`
is an adjacent direct adapter consumer, not an initializer; it received
classification proof only and remains behaviorally outside this slice.

Resolution brief: route every public wrapper through the common
`charness.adapter-bootstrap/v1` lifecycle, preserve resolver-specific data,
and make invalid/unestablished, path-escaping, symlink, dry-run, and force
decisions explicit in one receipt.

Implementation: commit `47f5ddc30179f9a3a20954d69678b01c47319ef1` updates the
canonical common initializer, checked-in plugin mirror, all 16 wrapper pairs,
classification declarations, and contract tests.

Prevention: retain the 16-entrypoint matrix and consumer-classification gate;
keep wrappers thin and lifecycle ownership in the common initializer. The
stale aggregate skill-contract checker, scheduler/hosted enforcement,
conditional-trigger execution, installed adoption, and consumer rollout are
deliberately not addressed here.

Boundary #692: owned-correctly — Charness owns the source/plugin bootstrap
contract and local consumer classification; downstream host and consumer
behavior remains a separate boundary.

Verification: base `55026bdb6b5423fdaadffff218f32bff3b0f5811`, target
`47f5ddc30179f9a3a20954d69678b01c47319ef1`, branch
`proof/issue-692-adapter-20260827`, path
`/tmp/charness-692-proof-20260827`; focused `32 passed`, related `76 passed`,
standing classification `37 passed`, combined `69 passed`, selected adapter
evals `10/10 passed`, source/plugin parity and final clean postflight passed.
The no-`--verify` pre-commit passed all 20 hook commands using a temporary
unstaged proof-only compatibility overlay for the stale checker; the overlay
was removed before postflight and is not in the target commit.

Behavior #692: local-only-by-contract — these are source, test, plugin-export,
and classification proofs only; no installed-host or provider roundtrip is
claimed.

Aggregate eval non-claim: exact target `scripts/run_evals.py --jobs 4` exits at
the pre-existing `representative-skill-contracts` checker because it still
requires the two critique phrases already removed from the current source;
18 scenario lines passed before that failure. #692 does not restore those
stale constraints and does not claim the aggregate eval green.

Critique #692: blocked explicit operator direction omits forced fresh-eye review and this host exposes no Agent/subagent capability
AI-provenance: authored by an agent session.
Manual fallback reason: operator-directed-manual-close.

Explicit non-claims: no universal changed-line proof, forced fresh-eye review,
handoff update, micro-slice record, installed-host behavior, hosted/provider
roundtrip, scheduler or conditional-trigger change, consumer-repository
adoption, remote CI, push, release, or tag is claimed. Parent dirty state and
the frozen goal/handoff surfaces were preserved.
