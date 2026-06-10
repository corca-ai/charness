# 343 host-hook lifecycle robustness slice critique
Date: 2026-06-10

## Decision Under Review

Close #343 with three bounded moves: (1) a dangling-hook liveness check
(`hook_state_liveness`) added to the existing
`reconcile_usage_episodes_host_hooks.py --mode status` surface; (2) the
multi-checkout posture decision (one logical hook per machine + commit-sweep
backstop) documented where the hooks are documented; (3) the
`reconcile_host_hooks` sibling fan-out factored into a registry table
(`host_hook_registry.SIBLING_HOOK_INTENTS`) so a fourth hook intent is a row,
not a third copied lazy-import block.

## Failure Angles

- The registry could silently change reconcile ordering, payload keys, or the
  per-host error-isolation semantics the three existing intents rely on.
- Liveness could leak into install/update flows as a new exit-1 hard gate
  (the issue asked for status/doctor surfacing only).
- The floor-test fixture change (seeding hook scripts) could mask a real
  operator regression instead of keeping the test about drift.
- The slice could claim to fix dangling-checkout noise while structurally
  unable to see the main dangling case (a deleted checkout's state file dies
  with it).
- Status JSON payload-shape changes could break `charness session-capture
  status` consumers.

## Counterweight Pass

- Real and folded: the docs + registry docstring overclaimed detection of
  *deleted* checkouts — reworded to claim moved-checkout/missing-script
  detection and to name the deleted case as undetectable from a surviving
  checkout's state (remedy: uninstall/reinstall; settings-scan deferred).
- Over-worry: payload-shape hazard (status JSON is sort_keys, the new
  `hook_liveness` key is additive, the only CLI consumer reads preserved keys
  and sees dangling via the merged `drift` list); install/update blast radius
  (`charness init`/`update` call reconcile mode only, which always exits 0).

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: docs/conventions/authoring-preflight.md:205 | action: fix | note: the posture paragraph and the registry docstring promised dangling detection for DELETED checkouts, which the state-tracked design cannot deliver (the state file dies with the checkout). Fixed: both now claim moved-checkout/missing-script detection and name the deleted case as a non-claim with the uninstall/reinstall remedy.
- F2 | bin: bundle-anyway | evidence: weak | ref: scripts/host_hook_registry.py:92 | action: fix | note: _command_script_path skips tokens[0], so a command shaped without a python3 prefix would flag a loud false positive; all tracked commands come from build_command. Fixed: comment recording the contract.
- F3 | bin: over-worry | evidence: moderate | ref: charness CLI cmd_session_capture_status | action: defer | note: status payload consumers read in_sync/hosts/find_skills_routing/drift by key — all preserved; hook_liveness is additive and sort_keys ordering was never consumer-visible.
- F4 | bin: over-worry | evidence: strong | ref: tests/test_usage_episodes_host_hooks.py:498 | action: document | note: the floor-test fixture change is legitimate — the old fixture installed hooks at nonexistent script paths, which under liveness semantics is genuinely dangling; seeding the scripts keeps the test about intent-vs-actual drift and the added dangling==[] assertion pins liveness.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: bounded fresh-eye subagent reviewer (separate agent context, read-only, shared parent worktree, prior state via git show HEAD).
- Requested spawn fields: subagent_type=general-purpose, name=slice2-critique, bounded slice packet (intent, changed files, invariants, tests/proof, non-claims, out-of-scope, reviewer questions).
- Host exposure state: applied
- Application state: host-confirmed: Agent tool returned reviewer verdict with agentId a41e2d3ff6b13b606 (25 tool uses; independently compared git show HEAD:scripts/host_hook_install_lib.py against the working tree, audited the charness CLI call sites, and re-ran the hook family 91/91 green).

## Fresh-Eye Satisfaction

Verdict: SHIP-WITH-NITS, no blockers (reviewer agentId a41e2d3ff6b13b606).
The reviewer confirmed the registry is behavior-preserving (same intent
order, same lazy-import point, no added try/except, per-host isolation
untouched inside the sibling reconciles), the floor-test fixture change is
legitimate, install/update flows see no new exit-1 surface, and the issue's
stated Destination (state-tracked liveness in status) is satisfied. Nits
folded before commit: the deleted-checkout doc overclaim (F1) and the
_command_script_path contract comment (F2).
