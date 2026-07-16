---
name: prove
description: "Use when a built implementation or contract slice needs its closeout proven before stopping: run the strongest honest verification, sync truth surfaces, bind the required fresh-eye critique, and emit the slice closeout ledger. `impl` loads this at its stop gate; contract-completing work consumes the same ledger."
---
# Prove

Use this when a slice is built and the remaining risk is stopping on unproven
or unrecorded work. `spec` defines the acceptance boundary, `impl` builds the
slice, and `prove` demonstrates it: executed evidence, synchronized truth
surfaces, a bound critique, and the emitted closeout ledger.

`prove` is slice-scoped, reversible-work-scoped. That boundary is what keeps it
one concept:

- the repo's standing quality bar (gate inventory, standing checks) stays in
  `quality`; `prove` consumes those gates as one evidence channel
- applied live-behavior closure (external roundtrip/readback loops) stays in
  `hotl`; `prove` labels the proof level and routes there when live proof is
  the honest bar
- irreversible-boundary ledgers (GitHub issue close, release publish) stay in
  `issue` and `release`; `prove` never absorbs their observables
- the fresh-eye reviewer substrate stays in `critique`; `prove` decides the
  scale and binds the result, never runs the review itself

## Bootstrap

Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`.
Verification preferences and truth surfaces live in the impl adapter
(`<repo-root>/.agents/impl-adapter.yaml`); `impl` owns that file and `prove`
reads it read-only through impl's resolver:

```bash
python3 "$SKILL_DIR/../impl/scripts/resolve_adapter.py" --repo-root .
python3 "$SKILL_DIR/../impl/scripts/survey_verification.py" --repo-root .
git status --short
```

If no adapter exists, continue with inferred defaults and manual capability
discovery, exactly as `impl` does before coding. If the adapter is invalid,
repair it via `../impl/references/adapter-contract.md` before relying on its
verification preferences or `truth_surfaces`.

## Workflow

1. Verify with the strongest honest path. `references/verification-ladder.md`
   owns the per-surface rules — browser output, the lint gate, external /
   third-party APIs, and the completion-report categories. Prefer executed proof
   over code inspection, use installed skill metadata/model judgment for runtime
   support (and `charness catalog list --repo-root .` only for hidden
   availability), and when
   runtime proof is unavailable say explicitly that it did not run.
   - for validation-shaped review, closeout, or operator reading work, run
     deterministic gates first; the repo's cautilus adapter and
     `../quality/references/cautilus-on-demand.md` own when evaluator proof
     is warranted — generic review or closeout wording must not silently launch Cautilus
   - skill self-tests and delegated workflows follow
     `../../shared/references/prescribed-path-self-test.md`; label a worker →
     host → provider seam at its highest executed proof level per
     `../../shared/references/external-capability-proof-ladder.md`
   - when that policy calls for a run, use `cautilus evaluate fixture --repo-root . --adapter-name <repo-owned-adapter>`
     or `cautilus evaluate observation --input <observed.json>`; treat
     source/wiring/guidance checks as mechanism-only, not runtime proof
2. Sync truth surfaces and re-read the contract before closeout.
   - if the slice changed user-visible capability, operating philosophy,
     supported integrations, install/usage surface, or honest stage claims,
     check `<repo-root>/README.md` and the impl adapter's `truth_surfaces` and
     update them before stopping
   - re-read `Fixed Decisions` and named acceptance checks; confirm each is
     reflected in the delivered slice or explicitly deferred or reclassified in
     the contract
3. Run the stop gate.
   - every task-completing repo slice records critique before closeout; scale the pass instead of asking whether it is needed
   - record `Critique: short <scope>` for small local-risk slices, or `Critique: full <artifact-or-subagent-status>` after using standalone `critique` for design, release, workflow, compatibility, host-proof, prompt-surface, public-skill, validator, or export decisions
   - `critique` always means a fresh bounded subagent review, never a same-agent pass; use `Critique: not-applicable <reason>` only for inspect/status/routing-only requests that do not complete repo work
   - if the required critique is blocked because the host cannot provide
     subagents after the capability check, stop and record `Critique: blocked <host-signal>`
   - run a fresh-eye review for runtime behavior, boundary honesty, and
     docs/spec synchronization; the
     [boundary ownership brief](../../shared/references/boundary-ownership-brief.md)
     owns the producer/consumer questions and the disposition this closeout records
   - run `$SKILL_DIR/scripts/check_boundary_escalation.py --repo-root . --json`; if
     it reports `triggered: true`, the changed paths matched the repo's cross-surface
     probe — escalate this slice to a standalone `critique`, and validate that durable
     artifact with the critique validator's `--changed-ref <base>` so the cross-surface
     `single-surface` rejection actually fires (the objective probe overrides a
     self-assessed small slice; presence-only validation would let it through)
4. End with execution status.
   - what changed, what was verified, what truth surfaces moved, what the
     critique found, what contract updates were made, and what remains for the
     next slice
   - if `$SKILL_DIR/../retro/scripts/check_auto_trigger.py` reports `triggered: true`
     for the current repo, run a short `session` retro before the final stop
   - if the user explicitly asked to keep going, treat this as a terse progress
     checkpoint and continue into the next locally decidable slice

## Output Shape

The closeout should usually include:

`Implemented`, `Capability Delivered`, `Contract Source`, `Verification` naming
code/fixture and runtime/evaluator proof, `Lint Gate` per
`## Closeout Vocabulary`, `Truth Surface Sync`, `Boundary Ownership`, `Critique`,
`Contract Updates`, `Residual Risks`, `Next Slice`.

## Closeout Vocabulary

Emittable-verbatim closeout tokens (validator substring-matches these); WHY-prose stays in `references/verification-ladder.md`.

- `Lint Gate` status is one of `ran-pass <command>` / `ran-fail-fixed <command>` / `ran-fail-deferred <command> <issue|anchor>` / `not-detected` / `skipped <reason>`.
- Completion-report categories are `durable` / `external-writes` / `test-only` / `verification` (proof + level `worker_queued`/`provider_roundtrip`/`agent_choice`) / `unverified-future`.
- `Boundary Ownership` verdict is one of `single-surface` / `owned-correctly` / `moved-to-owner` / `escalated-to-issue-spec` — emit-only / eval-judged (`prove` keeps no durable validator; the typed floor lives in the escalated standalone `critique`).

## Guardrails

- Do not call a same-agent review a critique. If the required critique is
  blocked, stop instead of downgrading to a local substitute and still calling
  the slice reviewed.
- Do not absorb another boundary's ledger: `issue`/`release` closeout
  observables, `hotl` live-loop dispositions, and `quality`'s repo-wide bar
  each stay with their owner; `prove` cites them, never re-declares them.

## References

- `references/verification-ladder.md`
- `references/review-gate.md`
- `../quality/references/cautilus-on-demand.md`
- `../../shared/references/boundary-ownership-brief.md`
- `../../shared/references/prescribed-path-self-test.md`
- `../../shared/references/external-capability-proof-ladder.md`
- `../../shared/references/fresh-eye-subagent-review.md`
