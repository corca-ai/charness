# Release Critique — charness 0.52.6 (dup-ratchet hardening)

- **Kind**: release-surface critique (standalone, bounded fresh-eye)
- **Date**: 2026-06-19
- **Release**: 0.52.5 → 0.52.6 (patch)
- **Scope**: the dup-ratchet hardening goal, slices 1+2 — see
  [goal artifact](../goals/2026-06-19-issue-393-harden-the-dup-ratchet-gate-scope-paths-empty-warning-write.md).
- **Verdict**: **release-safe** (bump level patch confirmed honest; no blockers).

## What ships

- **F** — `dup_ratchet.enabled` with empty `scope_paths` now degrades the whole
  gate to an advisory (was a silent nose `DEFAULT_PATHS` fallback). Advisory,
  never blocks.
- **C** — `check_dup_ratchet.py --write-baseline` refuses a large `family_id`
  delta without `--confirm-baseline-delta` (new flags `--confirm-baseline-delta`,
  `--baseline-delta-threshold` default 50). Maintenance-command guard only; never
  touches the gate evaluate path, so it cannot false-block a push.
- **I** — `validate_gate_baseline` folded into the existing `check_dup_ratchet`
  evaluate path; a present-but-schema-invalid baseline surfaces as a degraded
  advisory through the existing `dup-ratchet` run-quality phase. No new phase.
- in-process coverage for `check_dup_ratchet.py` (attribution 0% → 86%, the #393
  subprocess-only-attribution class).

## Two bounded fresh-eye reviews (different agent contexts, read-only)

1. **Pre-push code critique** → **push-safe**, no blockers. Independently
   verified F/I only append to `degraded` (cannot block), C's refusal is reachable
   only via `--write-baseline` (never the evaluate path), no new phase/floor, the
   plugin mirror is byte-identical, and the 2-id re-baseline is honest (the rotated
   families' members are byte-identical base-vs-HEAD — an unchanged `if x is None:
   return None` idiom and the unchanged `main()` boilerplate). One deferred
   should-fix: the `dup_ratchet_lib` docstring's `family_id`-stability claim is
   narrower than reality (same-file edits also rotate ids) — pre-existing, logged as
   the slice-1 off-goal finding, deferred under Floor-Addition Restraint.
2. **Release-surface critique** → **release-safe**, bump **patch** honest, no
   blockers. Verified the consumer adapter contract is unchanged (no new
   `dup_ratchet` key; gate ships `enabled:false`/inert by default), the plugin
   export mirrors the hardened gate, and the re-baseline does NOT leak
   (`charness-artifacts/quality/dup-ratchet-baseline.json` is authoring-repo-only,
   absent from `plugins/charness/`). One should-fix **folded**: the 0.52.6
   `update_instructions` note "No command/install/invocation change ships" mildly
   overclaimed given the two new flags — reworded to "no operator-facing command or
   install change ships; the only added invocation surface is two opt-in flags on
   the internal `--write-baseline` maintenance command, which consumers never run."

## Bump rationale (patch)

Behavior repairs to an existing gate (F/I close silent-degrade gaps; C hardens a
maintenance command) plus test coverage. The consumer-facing contract is unchanged
and the gate is opt-in/inert by default; the two new flags are on an internal
hand-run maintenance command, not an operator-facing `charness` subcommand. Patch
is the lightest honest bump.

## Verification carried into closeout

- run-quality.sh --read-only: 77 passed / 0 failed (dup-ratchet phase PASS).
- `check_plugin_import_smoke.py` + `validate_packaging_committed.py` green.
- Push `90bab0de..e97a2884`; CI Quality Core success on `e97a2884` (different channel).
- Post-release: confirm CI green on the release SHA + tag, and that install/update
  fetches the hardened gate (different-observer/different-channel per the north-star).
