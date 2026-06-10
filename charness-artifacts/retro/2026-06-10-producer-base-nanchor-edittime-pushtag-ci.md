# Session Retro

Date: 2026-06-10

## Mode

session — one `achieve` goal
(`charness-artifacts/goals/2026-06-10-producer-base-nanchor-edittime-pushtag-ci.md`)
run end-to-end in a single session: activation, four slices, bundle boundary,
closeout.

## Context

The operator-selected next queue, four independent per-slice-closed-out
slices: (1) `run_slice_closeout.py --base` committed-range ergonomics; (2) the
#N-anchor edit-time guard auto-firing via the adapter-declared host-hook
machinery; (3) light push/tag CI + the CI-PR changed-line mutation mirror;
(4) the source-guard timing audit with the favorable subset pulled to commit
time and the `docs/conventions/validator-timing-layers.md` doctrine.

## Evidence Summary

- Slice commits: `6340e00a` (slice 1), `08119de4` (slice 2), `b233a5b2`
  (slice 3), `72f74b7f` (slice 4), `581cbd64` (bundle-boundary fixes),
  `2bbd8a40` (changed-line coverage fixes).
- Per-slice fresh-eye bounded subagent critiques: 4× SHIP-WITH-NITS, all
  must-fix nits applied in-slice.
- Bundle boundary: `run_slice_closeout.py --base --produce-mutation-coverage
  --verification-lock` completed (coverage + fingerprint over the
  auto-detected committed range, NO manual `--paths` — the slice-1 acceptance
  proven live); changed-line consumer `ok: true`, 8 pool files verified, 0
  blocking; broad gate `run-quality.sh --read-only` 73 passed / 0 failed.
- Off-goal findings filed: corca-ai/charness#342 (adapter-vs-integration-schema
  commit-time validation gap), corca-ai/charness#343 (host-hook lifecycle
  robustness: dangling checkout, multi-checkout coverage, reconcile registry).

## Waste

- **W1 — slice-2 escape paid two slices later (~25 min).** The
  `skill_anchor_edit_guard` adapter section passed commit-time
  `validate-adapters` but violated the usage-episodes integration's
  `additionalProperties: false` jsonschema; the usage-episode emitter failed
  with `invalid_adapter`, surfaced only by slice 4's wider test run and fixed
  forward in `72f74b7f` plus a wasted full producer run that died at the
  surface-match block. Root cause: an adapter file has two validation owners
  and only the weaker one runs at the commit boundary. Filed as #342 with a
  timing-pull destination.
- **W2 — parity watchdog fired at the bundle, two slices after the workflow
  was authored (~12 min producer re-run).** `quality-core.yml` was authored in
  slice 3; the CI/local-gate parity watchdog
  (`test_real_repo_workflows_or_zero_parity_issues`) only fired inside the
  bundle's instrumented broad pytest. Resolution used the doctrine's own
  extension path (`local-gate-subset-mirror` policy). The structural fix is a
  slice-4-class timing pull: workflow edits now run the parity inventory with
  `--require-canonical-gate-match` at commit time (applied this session).
- **W3 — producer DISCOVERED four uncovered changed lines at the boundary
  (~10 min re-run), the standing recent-lessons repeat trap.** Slices 1–2
  added branch tests per the carried lesson, but the reconcile
  `HostHookError` branch, the non-dict-payload fail-open return, and the
  guard's `__main__` process entry were missed; the consumer flagged them and
  one more producer run was paid. Partial improvement over prior sessions
  (4 lines vs 7/85), still discovery rather than confirmation.

## Critical Decisions

- Slice 1: `--base` affects only changed-path collection; the producer's
  fingerprint anchor (merge-base origin/main HEAD) was deliberately left
  untouched so producer == gate holds by construction (rejected: re-anchoring
  the fingerprint to the explicit ref — the consumer would always read it
  stale).
- Slice 2: adapter-declared host hook via the existing parallel-hook pattern
  (rejected: checked-in `.claude/settings.json` preset — no opt-out, no state
  tracking; plugin-shipped hooks — consumer-reaching).
- Slice 3: subset-mirror CI invoking repo-owned validators step-by-step
  (rejected: wholesale `run-quality.sh --read-only` in CI — specdown/host
  binary coupling, not light); after the watchdog fired, the new
  `local-gate-subset-mirror` policy category via the doctrine's sanctioned
  lib+doc extension path (rejected: mislabeling it `scheduled-deeper-check` —
  dishonest cadence; anchoring on the canonical gate — loses "light" and adds
  heavy CI env).
- Slice 4: pull only the measured-cheap five (then six, with the parity
  inventory) guards; `check-python-runtime-inheritance` (0.75s) and
  `check-command-docs` (3.3s) recorded as stays with reasons.

## Expert Counterfactuals

- A schema-first reviewer (the Hickey-style "who owns this shape?" lens) would
  have asked at slice 2: "who VALIDATES this adapter section?" — the
  integration schema would have surfaced immediately instead of two slices
  later. The transferable move: when adding a section to an adapter, grep for
  the schema that consumes it before committing (now structural via #342's
  destination).
- Running the just-authored artifact's own watchdog in-slice (here: the parity
  inventory right after authoring the workflow) is the cheap counterfactual
  for W2 — generalized by the commit-time parity pull, so the next workflow
  edit cannot defer the verdict to the bundle.

## Sibling Search

W1's class (two validation owners, only the weaker at the boundary) has known
siblings: every `integrations/*/manifest.schema.json` that validates an
`.agents/*-adapter.yaml` consumed elsewhere (usage-episodes today; tools/
t-events/worktree manifests follow the same ownership split). Destination
recorded in #342 (a changed-scoped commit-time jsonschema pull through the
existing dispatcher) rather than hand-fixing one instance.

## Next Improvements

- I1 — adapter-vs-integration-schema commit-time validation gap: `issue #342`.
- I2 — host-hook lifecycle robustness (dangling-checkout noise, one-logical-
  hook-per-machine coverage gap, reconcile fan-out registry refactor before a
  fourth hook): `issue #343`.
- I3 — coverage confirm-not-discover (W3): applied — in-process branch tests +
  one ratchet-exempted subprocess proof for the guard's stdin/exit-code
  contract (`2bbd8a40`), and the re-run producer + consumer confirmed green;
  the recurring class stays a recent-lessons repeat trap (recurrence noted,
  trend improving: 4 lines this run vs 7 prior).
- I4 — parity watchdog timing (W2): applied — workflow edits now run
  `inventory-ci-local-gate-parity --require-canonical-gate-match` at commit
  time via `_timing_layer_gates` (+ dispatcher test + doctrine table row).

## Persisted

- `docs/conventions/validator-timing-layers.md` (the timing-layer doctrine +
  classification table — the durable decision frame).
- `skills/public/quality/references/maintainer-local-enforcement.md`
  (`local-gate-subset-mirror` policy section).
- `docs/conventions/authoring-preflight.md` (edit-time anchor-guard
  auto-firing).
- Issues #342, #343 (structural destinations for W1/I2).
- This retro; goal artifact Slice Log + Auto-Retro dispositions.
