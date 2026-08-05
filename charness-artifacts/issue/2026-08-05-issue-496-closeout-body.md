Closes #496

Classification: deferred-work

JTBD: Quality-bootstrap maintainers need a nested policy refill report and
operator action that preserve configured mutation commands instead of making
inert defaults look like harmful intent loss or advising destructive block
removal.

Boundary: This closeout covers the exact `mutation_testing.commands` fixture,
the narrow omitted-empty-default predicate, its required-slot and meaningful-
empty controls, and the current adapter lifecycle. It does not introduce a
generic empty-value taxonomy, sub-key deliberate-absence contract, top-level
symmetry policy, or a new leaf-warning consumer. The old leaf-warning and
automatic-rewrite path is historical after #507.

Resolution brief: inline (no pause) — verify the already-landed narrow #496
producer repair against the current #507 lifecycle, then close on the current
top-level conflict/advisory contract with a distinct CLI readback.

Implementation: `e7bc7eaf780e7ce89d9866c450d3bc7107907c75` introduced the narrow
producer allowlist. `90bc1f9e` moved the user-facing authorization boundary into
the lifecycle: ordinary bootstrap preserves a conflicting adapter and only
`--migrate` authorizes a write. The current slice adds direct producer controls
to `tests/quality_gates/test_quality_bootstrap_absence.py` and synchronizes the
historical packet/artifact bindings and current critique.

Root cause: The original nested refill report treated omitted empty-string
command defaults as equally meaningful and its consumer paired the finding with
whole-block deletion advice. The later lifecycle refactor removed that consumer
from the live path and made semantic conflict preservation the current safety
boundary; the retained producer filter is now implementation provenance.

Siblings: #493 remains the non-inert nested-refill recursion track; its
meaningful nested reporting is not suppressed. #507 owns the current
consumer-owned adapter conflict and migration authorization. `prompt_asset_policy.exemption_globs: []`
remains reportable as the axis-varying meaningful-empty control.

Prevention: Keep the exact command/default allowlist and direct positive and
negative controls; preserve the top-level conflict-without-write boundary;
keep source/plugin bootstrap modules and complete payload/stderr parity in sync.
Reopen if a future consumer restores leaf-warning behavior, either named slot
gets a different non-empty default or operator meaning, whole-block deletion
advice returns, or source/plugin parity diverges.

Critique #496: charness-artifacts/critique/2026-08-05-issue-496-resolution-critique.md

Behavior #496: current-top-level-conflict-by-contract — distinct real CLI
fixture readback through `skills/public/quality/scripts/bootstrap_adapter.py`
returned `adapter_status=conflict`, requested top-level `mutation_testing`
changes with no dotted `commands.*` surfaces, a `--migrate` next action, no
`commands.dry_run`/`commands.sample` warning names, `stderr` warning output,
and byte-preserved adapter content. This channel is distinct from the focused
pytest implementation suite (75 passed). Local CLI/adapter behavior only;
remote CI and installed-host behavior are not claimed before publish.

AI-provenance: Agent-authored direct-commit carrier; live issue read, resolution
brief, current packet identity verification, four bounded review windows plus
one unnamed delivery retry, clean reviewer boundary fingerprints, focused
pytest proof, standalone CLI readback, critique validation, and closeout-draft
validation are recorded in the referenced artifacts.
