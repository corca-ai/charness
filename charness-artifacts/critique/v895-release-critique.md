# Release Critique — charness 8.9.5 (v8.9.5)

- **Release Scope**: `8.9.4` → `8.9.5` (tag `v8.9.5`), patch. One-line
  consumer story: task-run persistence can no longer commit out-of-scope
  residue, release resume packets name their notes-file hole, staged
  eviction violations refuse at commit time, and reviewer results can
  declare the target set they must observe.
- **Bump rationale**: patch, not minor: six tooling repairs (persist
  scoping, resume placeholder, staged eviction owner, worker target
  flag, packet wiring prose, lane declaration) plus regression tests;
  the one additive flag (`--expected-target`) only completes the #819
  contract's disclosed residual and breaks no existing invocation.
- **Reviewed delta**: `107f89c8c..HEAD` — six slice commits plus this
  record; 19 files across `scripts/task_run/`, `scripts/hooks/`,
  `scripts/gates/`, `skills/shared/`, `skills/public/{release,critique}/`,
  `.githooks/`, and their standing tests.
- **Substrate**: two bounded fresh-eye file-backed workers (codex_exec),
  lenses below, parent-owned integration here. No same-agent substitution.
  First production run with packet prepared-targets declared to the
  coverage floor: both workers returned `coverage_ok: True` with all six
  targets observed exactly once.

## Lenses and verdicts

- **Worker A** (correctness and refusal safety): verdict `block`.
  Per-target: `task-run-persist-scope` block, `staged-eviction-owner`
  block, other four pass. Packet `v895-release-critique-a-packet.md`
  (+ `.json`); worker dir `workers/v895-release-critique-a/`.
- **Worker B** (operator surface and failure messaging): verdict `block`.
  Per-target: `worker-expected-targets` block, other five pass. Packet
  `v895-release-critique-b-packet.md` (+ `.json`); worker dir
  `workers/v895-release-critique-b/`.

## Blocks and answers (all repaired before release)

1. Unclassifiable persist candidates fell back to stage-everything —
   production persist now skips instead; direct unclassified callers keep
   the historical shape under test.
2. Staged-scope owners judged worktree bytes while the commit takes index
   bytes — `run_cheap_owners` refuses an unstable staged scope with a
   restage remedy; explicit `--paths` judgment is unaffected.
3. Thin-result coverage refusals named a count but not the dropped targets
   and stated no remedy — both refusals now name exact targets plus one
   shared remedy sentence; pre-existing exact-match tests pass unchanged.

Answers land in `84378441c`; each repair carries its own regression test.

## Reviewer Tier Evidence

- **Requested tier**: `n/a` (no tier requested; host-defaulted)
- **Host exposure state**: `host-defaulted`
- **Execution mode**: `file-backed-worker`, backend `codex_exec`
- **Coverage floor**: declared 6 targets on both attempts;
  `coverage_ok: True`, `expected_targets` recorded in both reports and
  joined through the ledger/provenance digests
- **Delivery state**: `findings-received` on both attempts; identity
  checks matched on packet, reviewed input, and parent receipt

## Boundary Ownership

- **Producer:** task-run completion/persistence, staged commit hooks,
  release planner packets, reviewer worker contract and critique lane.
- **Consumer:** lane operators relying on candidate commits carrying only
  scoped paths; committers relying on pre-commit owners judging committed
  bytes; review authors declaring coverage floors.
- **Verdict:** `owned-correctly` — each repair lives in the module that
  owns the refused behavior, with standing tests beside it; the length-cap
  split (persist helper beside the WIP checkpoint; floor tests in their
  own module) follows the repo's split rule.

## Open Risks and residuals

- Critique-lane promotion does not re-enforce per-target coverage on
  lanes without the worker floor; recorded as a residual, no measured
  failure behind a mechanical rule there.
- The standing pytest runner takes nodeids but no `-k` filter; targeted
  repair loops use repeated `--pytest-target` instead.
- A deliberately bypassed claims marker (deleting the marker line and
  amending) still skips the claims floor; the floor prices carelessness,
  not sabotage (standing residual, restated).
