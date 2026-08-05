fix: close hollow refill behavior under current bootstrap lifecycle

Closes #496
Classification: deferred-work
JTBD: Maintainers need nested refill reporting and a safe operator action that preserve configured mutation commands instead of making inert defaults look like intent loss or advising destructive block removal.
Boundary: Exact mutation_testing.commands fixture, narrow omitted-empty-default predicate, required-slot and meaningful-empty controls, and current adapter lifecycle; no generic empty-value taxonomy, sub-key absence contract, or new leaf-warning consumer. The old leaf-warning/automatic-rewrite path is historical after #507.
Resolution brief: inline (no pause) — verify the landed narrow #496 producer repair against the current #507 lifecycle, then close on the current top-level conflict/advisory contract with a distinct CLI readback.
Implementation: e7bc7eaf780e7ce89d9866c450d3bc7107907c75 introduced the narrow producer allowlist; 90bc1f9e moved current authorization into the lifecycle; this slice adds direct producer controls, current critique, and synchronized packet/artifact bindings.
Root Cause: The original nested refill report treated omitted empty-string command defaults as meaningful and paired the finding with whole-block deletion advice. #507 removed that live consumer path and made conflict preservation the current safety boundary; the retained producer filter is implementation provenance.
Siblings: #493 remains the non-inert nested-refill track; #507 owns current adapter conflict/migration authorization; prompt_asset_policy.exemption_globs: [] remains reportable.
Prevention: Keep the exact command/default allowlist, direct positive/negative controls, top-level conflict-without-write boundary, source/plugin parity, and complete payload/stderr parity. Reopen on a restored leaf-warning consumer, changed slot semantics, destructive advice, or parity drift.
Critique #496: charness-artifacts/critique/2026-08-05-issue-496-resolution-critique.md
Behavior #496: current-top-level-conflict-by-contract — distinct real CLI fixture readback returned conflict, top-level mutation_testing change(s), no dotted commands.* surfaces, --migrate next action, no hollow-leaf warning names, stderr warning output, and byte-preserved adapter content; distinct from the 75-test focused implementation suite.
AI-provenance: Agent-authored direct-commit carrier with live issue read, resolution brief, current packet identity, delegated fresh-eye critique/retry, clean boundary fingerprints, focused proof, standalone CLI readback, and validated closeout ledger. Local behavior only; remote CI and installed-host behavior are not claimed before publish.
