---
name: impl
description: "Use when work should move into code, config, tests, or operator-facing artifacts. Consume the current implementation contract when it exists, bootstrap a small honest contract inline when it does not, implement the smallest meaningful slice, then load `prove` to verify it and emit the slice closeout ledger before stopping."
---
# Impl

Use this when the work should move from contract into code, config, tests, or operator-facing artifacts.

`impl` is downstream of `spec`, but direct implementation prompts still get a small honest contract instead of pretending the task is already well-defined.
`impl` owns building the slice; proving and closing it is the sibling `prove` skill, loaded at the stop gate below. Keep sequence discipline in the loop: see `references/sequence-discipline.md` and `references/design-lenses.md`.

## Continuation Default

- When the user explicitly asks for autonomous continuation, do not pause at
  slice boundaries just to report completion; treat commits, verification, and
  contract updates as checkpoints and continue into the next locally decidable slice.
- Ask only for real product/policy decisions, irreversible external side effect,
  unavailable stronger proof, or evidence conflicts you cannot resolve locally.

## Bootstrap

Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`. Read the
current implementation contract before changing code. If no canonical contract
exists, bootstrap a small current-slice contract first.

```bash
# Required Tools: rg
# Missing-binary protocol: ../../shared/references/binary-preflight.md
# 1. current contract and nearby context
rg --files docs skills
sed -n '1,220p' docs/handoff.md 2>/dev/null || true

# 2. impl adapter resolution and verification survey
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/init_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/survey_verification.py" --repo-root .

# 3. locate the canonical spec/design artifact and current target
rg -n "Current Slice|Success Criteria|Acceptance Checks|Fixed Decisions|Probe Questions|Deferred Decisions|requirements|acceptance" .

# 4. bind the planned current-slice paths before the authoritative risk call
rg -n "test|spec|fixture|eval|smoke|integration" .
git status --short

# Freeze every repo-relative path this slice may own: source, tests, generated
# exports, and contract/validation surfaces. Then run the only authoritative
# planner call with that complete path set.
python3 "$SKILL_DIR/../../shared/scripts/plan_risk_interrupt.py" --repo-root . --detail --paths <current-slice-path>...
```

A pathless/global planner observation may be used only to discover whether a
current interrupt exists; it is discovery-only and cannot authorize or refuse
this slice. If the current-slice path set is not known, finish binding the
contract, target, and owned source/test/generated/contract paths before making
the authoritative call above. Interpret that scoped result fail-closed: only
`status: not-applicable` with `required: false`, or
`status: handoff-recorded` with `required: true`, `impl_status: allowed`, and
`chosen_next_step: impl` permits ordinary implementation. Blocked, unknown, or
malformed output, any required result without that valid impl handoff, and an
allowed handoff whose next step is `critique`, `factor-first`, or `hitl` all
stop ordinary implementation.

If the canonical contract artifact is missing, reconstruct the smallest honest
contract first. Do not stop just because `spec` was not run as a separate
session. Stop only if the slice is still too ambiguous to define honestly.

Adapter policy:

- if the impl adapter is missing, continue with inferred defaults and manual
  capability discovery
- if the adapter is invalid, repair it using `references/adapter-contract.md`
  before relying on adapter-defined paths or verification preferences
- if recurring verification expectations matter, create
  `<repo-root>/.agents/impl-adapter.yaml` early
- treat the verification survey as onboarding, not a closing nicety: look for
  the best self-verification path before you code and again before you stop
- run the worktree readiness probe below; when `charness worktree doctor`
  reports a non-pass status, surface the recommended next action (usually
  `charness worktree prepare`) for the operator to run — do not auto-run prepare
  and do not silently proceed past missing hook-manager state

## Worktree Readiness

Run the non-fatal readiness probe before mutating code; skip silently when
`charness` is not on PATH so it never blocks a repo that does not consume charness.

```bash
command -v charness >/dev/null 2>&1 && charness worktree doctor || true
```

## Workflow

1. Ingest the current slice.
   - identify the canonical artifact or write an inline current-slice contract
     before changing code; restate the slice in implementation terms and list
     the acceptance checks that must pass before stopping
   - when the contract names a `Capability Contract`, restate it as the
     user/operator capability and acceptance evidence before coding
   - when user-corrected behavior starts or redirects the work, classify stable
     contract vs better case reading before adding repo rules, tests, or gates
   - interpret only the authoritative path-scoped planner result; a pathless or
     global result is discovery-only and never controls this slice
   - do not continue plain implementation unless the result is explicitly
     `not-applicable`/`required: false` or
     `handoff-recorded`/`required: true`/`impl_status: allowed`/
     `chosen_next_step: impl`; every other, unknown, or malformed result stops
     the slice
   - before replacing a process, runner, protocol adapter, or compatibility
     boundary, write the acceptance envelope: preserved inputs and argument
     boundaries, state/lifecycle, outputs, failure and exit behavior, and the
     real-boundary smoke that must remain. Retired implementation formatting or
     diagnostics stay out unless a current consumer actually depends on them.
2. Keep the contract honest.
   - treat `Fixed Decisions` as fixed for this slice
   - treat `Probe Questions` as explicit learning goals, not as hidden scope
   - keep `Deferred Decisions` visible instead of resolving them accidentally
   - if implementation changes scope, acceptance, or a fixed decision, update
     the contract before stopping
3. Implement the smallest meaningful unit.
   - prefer a slice that proves one user-visible behavior or one structural seam
     and opens the next good move most cleanly; when a probe exists, design the
     slice to answer it cleanly
   - for judgment-quality corrections, preserve the boundary: a direct answer,
     smaller guidance, or no repo change yet may be correct
   - apply `../../shared/references/source-bound-records.md` for multi-source
     external writes, and the prescribed path from `SKILL.md` (not an
     author-composed smoke probe) for skill packages, scheduled workflows, or
     external lookup contracts
   - when an active `achieve` goal artifact exists, treat it as the slice memory
     surface and append slice evidence per `../../shared/references/active-goal-coordination.md`
4. Prove and close the slice.
   - when the build work is done, load the sibling `prove` skill and complete
     its closeout ledger before stopping: the strongest honest verification,
     truth-surface sync, the bound fresh-eye critique, and the emitted
     closeout vocabulary all live there
   - "code written" is not a stop state; a slice without its `prove` ledger is
     unfinished work, not a smaller slice

## Output Shape

The slice closeout ledger — `Implemented`, `Verification`, `Lint Gate`,
`Truth Surface Sync`, `Boundary Ownership`, `Critique`, and the rest — is owned
by `prove`; emit it from there rather than improvising a local summary shape.

## Guardrails

- Do not stop at "code written": a slice ends when its `prove` ledger is
  complete, blocked-with-signal, or the slice is honestly handed back to
  `spec`/`debug`.
- Do not run the `prove` stop gate as a same-agent formality; `prove` owns the
  critique-binding rules and they mean a fresh bounded reviewer context.

## References

- `references/adapter-contract.md`
- `references/contract-consumption.md`
- `references/external-api-contract.md`
- `references/design-lenses.md`
- `references/sequence-discipline.md`
- `references/spec-loop.md`
- `../prove/SKILL.md`
- `../../shared/references/source-bound-records.md`
- `../../shared/references/prescribed-path-self-test.md`
- `../../shared/references/active-goal-coordination.md`
