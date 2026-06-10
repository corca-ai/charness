# Session Retro — next-queue goal: #342 adapter-schema pull + #343 hook lifecycle + deferred proofs

Mode: session

## Context

The activated goal `charness-artifacts/goals/2026-06-10-342-343-adapter-schema-hook-lifecycle-deferred-proofs.md`
ran start-to-finish in one session: slice 1 closed #342 (integration-schema
validation pulled into `validate_adapters.py`, commit 76909cc8), slice 2
closed #343 (liveness + posture + registry, commit 7f835610, repair
f084c875), slice 3 consumed the three deferred proofs read-only (quality-core
first remote run GREEN at run 27249353164; the edit-time anchor guard
observed BLOCKING a live scratch `PostToolUse` edit; #335 confirmed closed by
the github-actions bot marker). Bundle proof: broad gate 73/0 and the
changed-line producer confirming 0 uncovered after one repair.

## Evidence Summary

Slice logs + commits in this repo; `gh run list/view` outputs recorded in the
goal artifact; host-log probe (thread-wide, no goal window line on this
Claude host): 429 function calls, 4 context compactions, 4 subagent spawns,
no repeated broad gates, git status x26 as the dominant repeated VCS command.

## Waste

- **W1 — producer DISCOVERED 3 uncovered changed lines at the bundle boundary
  (~6.7 min extra instrumented broad-pytest run, per the producer proof record).** The `_import_module`
  ImportError fallback in the NEW `scripts/host_hook_registry.py`. The
  carried lesson (cover degrade branches in the introducing slice) WAS
  applied inside slice 1 (`validate_adapters` ImportError/YAMLError branches
  covered up front) but missed in slice 2's new module, because the
  lazy-import fallback only fires when `scripts/` is off `sys.path` — a
  branch the default in-process test pattern never executes. Trend improving
  (3 lines vs 4 prior vs 7 before) but still discovery, not confirmation.
- **W2 — first cut of slice 1 parsed adapters with the minimal
  `adapter_lib` parser instead of the runtime owner's `yaml.safe_load`**
  (~3 min, caught by the slice's own test before commit). Ironic-but-cheap:
  the slice existed to close a two-owner drift and nearly introduced a
  two-parser drift; the fidelity rule is now in the slice log and the commit
  message.
- **W3 — two parse attempts lost in closeout scripting against the
  changed-line consumer's output** — caused by this session capturing
  `2>&1` into one stream; the consumer's stdout is already pure JSON
  (disposition review verified the single `_emit` print), so there is
  nothing to fix in the script. Session-local; not an improvement.

## Critical Decisions

- **Seam choice for #342:** extend `validate_adapters.py` rather than a new
  `_timing_layer_gates` bridging validator — because validate-adapters
  already runs as the same command at commit time and the broad gate, one
  rule covered all timings with zero new wiring. Recorded in the slice log
  BEFORE wiring (the goal boundary), survived fresh-eye review.
- **Honest scope language for #343:** the reviewer caught the docs claiming
  dangling detection for DELETED checkouts, which the state-tracked design
  cannot see (the state file dies with the checkout). Reworded to
  moved-checkout/missing-script detection with the deleted case as a named
  non-claim. Claims now match the mechanism.
- **Floor-test fixture made honest instead of weakening semantics:** the
  54-test suite's status-mode test installed hooks at nonexistent script
  paths; under liveness semantics that repo is genuinely dangling, so the
  fixture seeds the scripts rather than the check learning an exemption.

## Expert Counterfactuals

- **Per-branch checklist lens (a mutation-testing practitioner):** when a
  slice ADDS a new pool module, walk the file's branches as a checklist and
  run the documented base->worktree producer+consumer self-check BEFORE the
  slice commit. Changed action: the early check (already documented in
  implementation-discipline.md) fires as a step, not a memory — structurally
  routed to issue #344's closeout nudge.
- **Gary Klein premortem on slice 2:** "imagine the registry refactor shipped
  and a month later reconcile silently changed behavior" — the answer (pin
  payload key order + per-host isolation with dedicated tests) was done; the
  premortem the session actually needed was on the NEW module's coverage,
  reinforcing the first lens rather than a different action.

## Next Improvements

- **I1 (workflow/capability): issue #344** — deterministic closeout nudge
  when a slice adds a new eligible mutation-pool file, naming the early
  producer self-check, so confirm-not-discover stops depending on recall.

## Sibling Search

W1 names a transferable pattern (environment-dependent fallback branches in
new modules escaping in-process tests). Scan: `host_hook_install_lib`'s
module-top import fallback carries a no-cover pragma (the prior convention);
`reconcile_usage_episodes_host_hooks._import_lib/_import_registry` are
exercised via CLI subprocess tests; the new registry fallback now has a real
test (f084c875) instead of a pragma. Remaining sibling class is FUTURE new
modules — destination: issue #344 (recurs: the confirm-not-discover trap has
now fired three goals running, each time on a different new surface).

## Persisted

Persisted: yes — charness-artifacts/retro/2026-06-10-342-343-next-queue-goal-retro.md
