# Retired Hook Ledger Cleanup Debug
Date: 2026-07-13

## Problem

After publishing and installing v1.0.0, `charness session-capture status --json` reports `in_sync: false` because host-state still tracks `codex:find_skills_routing` and the deleted `session_start_find_skills.py` path.

## Correct Behavior

Given host state created by a pre-v1 install, when v1.0.0 update or session-capture reconcile runs, then retired Charness-owned hook settings and ledger keys are deleted, canonical session-routing entries remain installed, and status reports `in_sync: true`.

## Observed Facts

- `charness update` installed version 1.0.0 and both host settings contain only canonical `session_start_routing.py` plus usage capture.
- `session-capture status` still lists state key `codex:find_skills_routing` with a missing script and reports drift.
- `session-capture install` is a noop and does not delete the retired state key.
- `session-capture uninstall` followed by install removes/recreates current host settings but the retired state key still survives.

## Reproduction

- On the v1.0.0 maintainer install, run `charness session-capture uninstall --json`, `charness session-capture install --json`, then `charness session-capture status --json`; the last command still reports the retired key and `in_sync: false`.

## Candidate Causes

- Retired hook cleanup removes matching host configuration entries but never removes the corresponding host-state ledger key.
- The ledger key is owned by a different install-state section than session-capture install/uninstall reads.
- Cleanup is present but keyed only by retired script basename in settings, so it skips state-only records after settings were already cleaned.

## Hypothesis

- Falsifiable claim: reconciliation mutates host settings and canonical state entries but omits an explicit deletion of retired ledger keys; adding state-only cleanup at the shared host-hook lifecycle boundary will make the minimal roundtrip end with no `find_skills_routing` key and `in_sync: true`. Disconfirmer: find an executed ledger-pruning branch that already targets retired keys, or observe the key disappear under an existing supported command.

## Verification

- confirmed and resolved — source inspection found no retired ledger-key deletion. Four seeded state-only regressions now cover both hosts and install/uninstall; `python3 -m pytest -q tests/test_session_routing_host_hook_reconcile.py tests/test_host_hook_registry.py` passed 35 tests. Applying the new deletion-only helper to the live managed checkout removed `codex:find_skills_routing`, after which installed `charness session-capture status --json` returned `in_sync: true`, `drift: []`, and no dangling hooks.

## Root Cause

`host_hook_session_routing.py` deleted retired JSON/TOML hook entries but called `_clear_state_entry` only for canonical `*:session_routing` keys. A state-only residue therefore survived once settings were already clean. Install/update could report canonical settings ready while the aggregate status consumer still found the pre-v1 ledger key and missing script.

## Invariant Proof

- Invariant: when the hook lifecycle retires a Charness-owned hook kind, the final status consumer must see both host settings and the state ledger without that retired entry before reconcile claims success.
- Producer Proof: v1.0.0 update and session-capture commands produce canonical host settings while leaving the retired state key.
- Final-Consumer Proof: `session-capture status --json` surfaces the dangling ledger entry and refuses `in_sync`.
- Interface-Shape Sibling Scan: tests cover Claude/Codex plus install/uninstall; the shared reconcile path consumes those operations, and the plugin mirror is byte-identical.
- Non-Claims: no claim that all user machines contained this stale key; the maintainer install is one confirmed migrated-state roundtrip.

## Detection Gap

- Real-host release readback | doctor passed but session-capture status exposed the ledger drift only after publication | add a seeded retired-state lifecycle regression and keep session-capture status in release readback.

## Sibling Search

- Mental model: deleting a retired config entry was treated as equivalent to retiring the lifecycle state that tracks it.
- same layer: Claude and Codex retired ledger keys | decision: same bug, fix now | proof: seeded local payload proof for both, runtime roundtrip for Codex.
- abstraction up: usage-capture and skill-anchor canonical state entries | decision: same class, diagnostic-only for this slice | proof: static scan confirms those state-key names were not retired or renamed | no action needed because deletion inventory does not apply to canonical, unrenamed keys.
- specialization down: state-only residue after settings cleanup | decision: same bug, fix now | proof: runtime/provider roundtrip.
- cross-file: `scripts/host_hook_install_lib.py` and the session-capture status consumer are the initial producer/consumer seam.

## Seam Risk

- Interrupt ID: retired-hook-ledger-survives-reconcile
- Risk Class: external-seam
- Seam: installed host settings and Charness host-state ledger
- Disproving Observation: repository gates and fresh-checkout probes passed, but the installed-machine status consumer remained red.
- What Local Reasoning Cannot Prove: every historical ledger shape present on other installations.
- Generalization Pressure: factor-now

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-07-13-retired-hook-ledger-cleanup.md

## Prevention

Keep retired names deletion-only, but make every retirement inventory cover settings and ledger state together. Seed state-only lifecycle regressions and retain installed `session-capture status` as the final-consumer readback after release refresh.
