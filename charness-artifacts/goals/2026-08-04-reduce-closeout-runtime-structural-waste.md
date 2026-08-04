# Achieve Goal: Reduce closeout runtime by removing structural waste

Status: complete
Created: 2026-08-04
Activation: `/goal @charness-artifacts/goals/2026-08-04-reduce-closeout-runtime-structural-waste.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current disposition: closeout-ready; the bounded `tests/charness_cli` family
  is measured and rejected, the broad nested-CLI migration is a no-safe-change
  candidate, and all remaining follow-up is explicitly routed.
- Current slice: D — lock proof and prepare the next decision.
- Current slice intent: synchronize durable evidence, obtain the final claims /
  disposition review, and close with no production remedy claimed.
- Next action: write the final review artifact, run the complete validator, and
  commit the synchronized goal, retro, probes, critique, and issue references.
- Verification cadence: cheap deterministic checks at each boundary; fresh-eye
  proof for any proof-surface or contract change; full local proof at closeout.
- Gate cadence: candidate spikes use the narrowest honest checks; final proof
  uses the applicable locked quality path. Do not spend a full closeout ritual
  on a candidate that has already missed the materiality bar.
- History boundary: move completed measurements and rejected candidates into the
  Slice Log and Auto-Retro; do not leave the next session to rediscover them.

## Goal

Aggressively reduce the real local closeout journey by removing structural waste
before attempting parallelism. The search order is deliberate:

1. delete duplicated or low-signal execution;
2. remove unnecessary code and dead setup that lies on a recurring path;
3. remove or collapse avoidable bootstrap and process-start overhead;
4. only then consider bounded parallelism as a separate follow-up.

The goal is about actual elapsed time, not a smaller source listing or a faster
isolated helper. A candidate is worth shipping only when it preserves the proof
contract and produces material end-to-end relief on the current host. The user
has already judged an approximately eight-second saving with roughly an hour of
rollback cost to be economically poor; this goal therefore uses a fixed initial
materiality bar of at least ten seconds on the real closeout path, chosen before
implementation. If the measured path does not support that bar, the candidate
is rejected or the goal records that the target has changed rather than
accumulating more ceremony.

The goal may end with a structural cleanup that is both materially faster and
proof-preserving, or with an evidence-backed no-safe-change disposition for the
candidate actually tested.

## Non-Goals

- Do not weaken, skip, downgrade, relocate, or hide a proof gate to obtain a
  green or faster run.
- Do not make global worker-count changes, cache-reuse claims, CI relocation, or
  test-suite pruning the first move. Parallelism is explicitly deferred until
  the structural pass is exhausted.
- Do not delete a test merely because it is slow. First identify whether it
  duplicates a cheaper proof; retain a thin real-boundary smoke when the process,
  packaging, isolation, or CLI contract is what the test proves.
- Do not treat clone totals, dead-code advisories, or bootstrap-copy counts as
  reduction targets. They choose inspection points; runtime and behavior decide.
- Do not collapse intentional portability/generated surfaces without proving
  source-tree and installed-plugin entrypoints still work.
- Do not publish, push, release, close issues, run remote CI, or run Cautilus.
- Do not turn a local Linux result into a cross-host runtime promise.

## Boundaries

- This is local, reversible work on the current host/runtime profile. The real
  target is the closeout journey, including its expensive standing and proof
  phases, not an arbitrary microbenchmark.
- The current proof facts remain invariant: changed scope, freshness, coverage,
  failure visibility, recovery evidence, and consumer verdict must remain
  observable through the same or a stronger channel.
- A duplicate candidate must have a named owner and a clear structural response:
  deletion, in-process extraction with a thin boundary smoke, shared helper, or
  generated/machine-owned surface. “The scanner found it” is not an owner.
- A bootstrap candidate must distinguish removable per-run setup from the
  intentional portability fence. The existing canonical shim consistency gate
  is evidence that some copied bootstrap is deliberate, not permission to
  preserve every copy forever.
- Any change to a validator, runner, gate, or verdict renderer is a proof-surface
  change. It requires delegated fresh-eye review; a verdict-logic repair owes a
  second review of the repaired surface.
- If a candidate misses the ten-second end-to-end bar, is too expensive to
  revert, or changes the proof being measured, restore it promptly and record
  the exact rejection. Do not rescue it with a longer ritual or parallelism.

## User Acceptance

The user can inspect one durable goal record and answer:

1. Which real closeout phase was targeted, and what repeated structural cost made
   it a better target than parallelism or a micro-optimization?
2. Which duplicated execution, unnecessary code, or bootstrap work was removed?
3. Did at least three comparable before/after observations show at least ten
   seconds of end-to-end relief on the same command, corpus, and host profile?
4. Do focused correctness and controlled failure checks show that proof was not
   weakened or hidden?
5. If no change shipped, which candidates were falsified, why was the search
   stopped, and what exact observation would reopen it?

Acceptance check matrix:

| Criterion | Decisive check | Required evidence |
| --- | --- | --- |
| Valuable target | Compare the real closeout journey and phase timings | command/corpus identity, phase owner, frequency, serial position, and proof sensitivity |
| Structural remedy | Inspect the owning code and candidate scorecard before editing | named owner, deletion/dedup/bootstrap rationale, blast radius, rollback path, and expected elapsed-time contribution |
| Material relief | Three comparable interleaved or alternating before/after observations | raw samples, fixed statistic, ten-second threshold, host/profile facts, and exclusions |
| Proof preservation | Separate correctness and controlled-failure channels | same failure visibility, freshness/coverage facts, recovery receipt, and consumer verdict |
| Honest closeout | Fresh-eye review and strongest applicable local gate | review artifact, final quality result, retro, claims check, and complete goal validator |

## Agent Verification Plan

### Low-Cost Checks

- Read the completed closeout goal, its retro, claims review, D51, recent
  lessons, and the North Star before selecting a remedy.
- Reproduce the current local closeout journey and split its elapsed time by
  named phase. Record command, base/head, corpus, environment, cache state when
  available, and whether the phase is standing, release-only, or proof-only.
- Run the structural inventories as advisory inputs: standing-test economics,
  nose clone families, dead-code candidates, structural-waste candidates, and
  hardcoded discovery. Rank candidates by likely end-to-end seconds, not by
  duplicate-line count.
- Read the exact implementation before shaping a remedy. In particular inspect
  repeated subprocess/CLI test paths, shared adapter/bootstrap loaders, and the
  current bootstrap-shim consistency contract.
- Fill the per-candidate quality scorecard before changing code. Stop a
  candidate early if no plausible path to ten seconds exists.

### High-Confidence Checks

- Pick one bounded candidate only after the scorecard names the producer,
  consumer, preservation invariant, falsifier, and rollback operation.
- Prefer deleting duplicate executable proof, moving ordinary behavior below a
  process boundary while retaining a thin boundary smoke, removing dead setup,
  or collapsing genuinely repeated bootstrap work. Do not hide assertions in a
  helper just to satisfy a duplicate scanner.
- Measure the candidate on the real closeout command with at least three
  comparable before and after observations. If the candidate is below ten
  seconds, revert immediately; do not spend an hour polishing a low-value
  result.
- Run correctness and controlled failure fixtures separately from timing. Check
  success, producer failure, stale/unproven evidence, non-zero status, failure
  names, recovery receipts, and no-fresh-marker behavior where applicable.
- If the change touches a proof surface, obtain the delegated fresh-eye review
  before locking claims. If verdict logic changed, perform the required second
  repaired-surface review.
- Finish with the strongest applicable local quality gate, a bound retro,
  claims review, synchronized artifacts, and the complete goal validator.

### External Or Live Proof

N/A — no remote, provider, release, publication, issue, or live behavior claim
is in scope.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Map the real closeout cost and rank structural candidates | A small speed delta is not enough; the next move must attack recurring structure | phase timing, candidate scorecards, and a stop/choose decision | completed |
| B | Spike the highest-value deletion/dedup/bootstrap candidate | Test economic value before a broad refactor | narrow before/after timing, preservation checks, and immediate revert decision | completed |
| C | Implement the smallest structural remedy | Ship only a change whose owner, boundary, and proof contract are clear | focused tests, generated/plugin sync where needed, and three comparable runs | completed — no safe remedy identified |
| D | Lock proof and prepare the next decision | Runtime relief is provisional until separately observed and reviewed | final quality, fresh-eye review, retro, claims review, validator, and next-session handoff | completed |

## Candidate Order and Current Leads

These are inspection leads, not preselected fixes:

- **Repeated executable proof/process starts:** the standing-test inventory found
  232 subprocess-bearing test files overall, 212 nested CLI files, and 194
  standing files. First determine which repeated process bodies duplicate
  in-process proof and which genuinely prove a delivery boundary.
- **Bootstrap work:** the clone inventory found a 22-member repeated bootstrap
  family. Inspect whether the per-process work beyond the intentional portability
  fence is removable or shareable; preserve the source/installed-tree contract.
- **Repeated adapter validation:** a 17-member family around
  `validate_adapter_data` is large enough to inspect, but it may be
  design-shaped rather than safely extractable. Measure startup and import cost
  before proposing a shared abstraction.
- **Unnecessary code:** dead-code advisory findings are candidates only. Remove
  a finding in this goal only if it lies on a recurring closeout/test path or its
  deletion unlocks a measurable reduction elsewhere.
- **Parallelism:** explicitly deferred until the above candidates are either
  shipped or honestly falsified.

## Prior Closeout Audit

The previous closeout-related goal was strong on proof discipline but weak on
economic targeting.

What was done well:

- It measured the current critical path instead of trusting old telemetry.
- It separated timing, correctness, controlled failure, and claims review.
- It preserved the focused proof after the worker-cap candidate failed the fixed
  materiality test; it did not weaken a gate to manufacture relief.
- The first claims review caught stale or mismatched evidence, and the repaired
  claims received a final independent read.

What needs to change:

- The chosen candidate could at most produce a small improvement, while the
  investigation and rollback burden became large. That is a selection failure,
  not a proof failure.
- A packet-path mismatch and stale timing details created avoidable closeout
  repair work. The next goal freezes command, artifact path, and timing bundle
  before broad validation.
- The structural inventories should have been used before spending another
  long cycle on a low-yield runner-shape experiment.

## Operator Decision Queue

none — the ten-second bar, full read-only target, and structural-first order
were resolved in activation; this no-safe-change closeout adds no operator-only
decision.

## Coordination Cues

Routing: quality first for runtime/candidate selection; critique and impl join
only after one structural candidate is fixed. Use retro at closeout and handoff
to carry rejected candidates and the next owner.

Gather: n/a — no external source is being introduced.

Release: n/a — no release surface is in scope.

Issue closeout: n/a — no tracked issue is being resolved.

## Discuss Before Activation

- Discuss before activation: RESOLVED in this session — the user supplied the
  main direction: structural deletion and deduplication first, bootstrap cleanup
  next, parallelism later. The initial ten-second bar, the largest recurring
  local phase as the default target, and inspection of both removable setup and
  intentional bootstrap fences are the stated defaults. The goal remains local,
  reversible, and does not authorize any external or irreversible action.

## Slice Log

 Slice A replaces the earlier low-value broad-vs-focused equivalence experiment
 as the active goal's first measurement slice.

### Slice 1: A — Map closeout runtime and rank structural candidates

- Objective: Map the real local closeout journey and rank structural runtime-waste candidates before changing code.
- Why this approach: The current goal fixes a ten-second end-to-end materiality bar and explicitly puts duplicate execution, unnecessary setup, and bootstrap inspection before parallelism. A clean current baseline was required because the prior worker-cap experiment is a different candidate and historical runtime is only a lead.
- Commits: 23f60313 — activated the goal and repaired the pre-existing source-owned retro lesson-selection index drift; no production or proof-surface implementation changed.
- What changed: The goal status/frame changed and `charness-artifacts/retro/lesson-selection-index.json` was regenerated from the repository-owned helper. No test, runner, gate, validator, generated plugin, or bootstrap behavior changed.
- Alternatives rejected: Rejected the 22-member bootstrap clone family as an immediate runtime target because the scouts confirmed it is an intentional source/installed portability fence. Rejected `validate-adapters` as the first implementation target because its current phase is 3.9–4.2s. Rejected the `tests/charness_cli` family because its exact standing subset is 3.62s. Kept the 194-file nested-CLI surface as a material candidate pending a bounded structural spike; parallelism, CI relocation, cache reuse, and gate weakening remain out of scope.
- Targeted verification: The initial full read-only run at the pre-activation tree was refused after 84 passes because `validate-retro-lesson-index` detected stale generated state; the repository-owned `python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write` repaired it and `--check` passed. Three matched clean `./scripts/run-quality.sh --read-only` runs at immutable baseline commit `23f60313ca9c58a4bac235166966b87a5f3bbb37` passed 85/0: totals 124.20s, 123.37s, 123.51s; standing pytest 45.1s, 48.9s, 50.4s; changed-line mutation 120.8s, 120.1s, 120.2s; `validate-adapters` 4.2s, 3.9s, 3.9s. The three-run medians are 123.51s overall, 48.9s standing pytest, and 120.2s mutation. The inventory-derived 194-file nested-CLI standing subset ran 3,443 tests in 31.60s; the `tests/charness_cli` subset ran 155 tests in 3.62s. Runtime source was `.charness/quality/runtime-signals.json`, profile `local-linux-x86_64-36cpu`; host was Linux x86_64, 36 CPUs, Python 3.10.12, empty `PYTEST_ADDOPTS`; warm-cache/load details were not instrumented.
- Test duplication pressure: No tests were added or expanded in Slice A; duplicate-pressure sample is not applicable. The standing-test economics inventory remains advisory and reports 480 test files, 194 standing nested-CLI files, 14 mixed release-only files, and 1 all-release-only file.
- Critique: Two unnamed Codex scouts independently inspected the candidate families read-only. Their shared boundary finding is that bootstrap copies are intentional portability, adapter validation has distinct schemas and only ~4s measured phase cost, and CLI subprocesses can be delivery-boundary proof rather than redundant assertions. No fresh-eye implementation critique is owed because no implementation or verdict logic changed in this slice.
- Off-goal findings: The stale retro lesson-selection index was a supporting gate repair, not a runtime optimization. No issue was filed; no external source, push, release, remote CI, issue close, or Cautilus run occurred. The prior focused worker-cap no-safe-change result remains historical context, not a re-opened candidate.
- Lessons carried forward: The current closeout is still mutation-dominated, but the mutation mapper selects goal/retro quality tests rather than the CLI family, so nested-CLI work cannot be assumed to improve the 120.2s mutation lane. A 31.60s nested-CLI subset is material enough to inspect, but deleting or in-process-converting it would risk process, packaging, environment, and CLI-boundary proof; the next slice must name one bounded family and preserve a thin real-boundary smoke.
- Metrics: Host timing source: three direct `/usr/bin/time -p ./scripts/run-quality.sh --read-only` receipts under `/tmp/charness-structural-goal-baseline-{2,3,4}.log`; nested-CLI receipt `/tmp/charness-structural-goal-nested-cli-1.log`; CLI receipt `/tmp/charness-structural-goal-cli-1.log`. These temporary receipts are reproduction sources only; no host token/tool/turn total is claimed. Current runtime summary reports latest `run-quality-read-only` 122.015s, recent median 96.074s, and changed-line mutation latest 118.996s, recent median 143.757s; those rolling signals corroborate hotspot selection but do not replace the matched samples.

### Slice A candidate scorecard

| Candidate | Owner / boundary | Expected end-to-end contribution | Proof sensitivity | Rollback / falsifier | Decision |
| --- | --- | ---: | --- | --- | --- |
| 194-file nested-CLI standing surface | `tests/*` subprocess helpers and the standing pytest phase | 31.60s subset upper bound; a ten-second saving is plausible only through a broad in-process migration | High: process, packaging, environment, and CLI delivery-boundary behavior | Preserve thin real-binary smokes; reject if the selected family is boundary-only or matched relief is under 10s | Selected for bounded spike |
| `tests/charness_cli` launcher family | `tests/charness_cli/support.py`, standing pytest | 3.62s measured for 155 tests | High for CLI entrypoint contract | Reject on measured upper bound below 10s | Rejected early |
| `validate-adapters` resolver subprocesses | `scripts/validate_adapters.py`, adapter resolver entrypoints | 3.9–4.2s measured phase | Medium/high: resolver isolation and schema-specific fallback behavior | Reject on measured phase below 10s; preserve valid/invalid adapter fixtures | Rejected early |
| 22-member bootstrap shim family | public skill entrypoints plus generated plugin copies | Not established; clone count is not runtime | High: source/installed portability and foreign-copy refusal | Reject unless direct source/installed entrypoint probe shows removable per-run work | Rejected as intentional portability fence |
| Current mutation mapper test corpus | `scripts/prepush_focused_changed_line_coverage.py` and mapped quality tests | 120.1–120.8s phase; CLI family is not in its current mapped corpus | Very high: changed-line coverage, freshness, and consumer verdict | Any remedy must retain mapped scope, marker, failure visibility, and consumer semantics | Hold for later; nested-CLI spike cannot claim this lane |

### Slice 2: B — Bound the nested-CLI candidate and reject broad migration

- Objective: Test whether the material nested-CLI runtime signal resolves to one owned family with a proof-preserving path to ten-second full-closeout relief.
- Why this approach: Slice A found a 31.60s standing subset but also showed a mutation-dominated full command, heterogeneous boundary purposes, and no reproducible node-level migration manifest. The bounded decision had to separate a real owner from a file-count upper bound before implementation.
- Commits: None; this slice made no production, test, gate, validator, generated, or export change.
- What changed: Recorded the delegated premortem and its boundary-ownership decision in charness-artifacts/critique/2026-08-04-critique-review.md. Updated this goal frame and ledger only.
- Alternatives rejected: Rejected a broad in-process harness, test pruning, global runner change, cache reuse, and parallelism. Rejected treating the ad hoc 209-target exclusion as a migration manifest because no repository producer emits it. The release-only clean boundary-bypass sample was not generalized to standing closeout tests.
- Targeted verification: The inventory-derived standing nested-CLI subset ran 3,443 tests in 31.60s. The corrected test-module-only exclusion probe ran 3,554 tests in 18.91s, but is explicitly non-causal because its target manifest is ad hoc. The quality-gates exclusion probe ran 2,691 tests in 17.11s, with the same scope limitation. Current boundary-bypass inventory reported 57 candidates, 1 convertible sample, 37 internal-boundary candidates, and 31 keep-boundary candidates; the convertible sample is release-only. Three matched full read-only runs remained clean at medians of 123.51s total, 48.9s standing pytest, and 120.2s mutation.
- Test duplication pressure: No tests were added, removed, or expanded. No mutation or proof-surface verdict logic changed, so the second repaired-surface review rule was not triggered.
- Critique: The delegated high-leverage premortem used three distinct angle reviewers plus a separate counterweight. It produced act-before-ship findings requiring a node-level manifest, full-command timing, and retained process/package/failure proof. Boundary snapshots structural-runtime-premortem-20260804 and structural-runtime-counterweight-20260804 both verified clean through their explicit /tmp before snapshots; an initial default verify read an older snapshot and was discarded.
- Off-goal findings: No issue, remote, provider, release, push, issue-close, Cautilus, or live-behavior action occurred. D51 remains deferred until a selected family proves both mapping and materiality.
- Lessons carried forward: A subset timing result is a selection signal, not causal end-to-end relief. A safe in-process conversion must name its node-level owner and preserve a thin real-boundary success, controlled-failure, and packaging contract. If no standing family satisfies those conditions, the correct result is no-safe-change rather than a repo-wide harness.
- Metrics: Receipts: /tmp/charness-structural-goal-nested-cli-1.log, /tmp/charness-structural-goal-no-nested-2.log, /tmp/charness-structural-goal-quality-gates-no-nested.log, and baseline receipts /tmp/charness-structural-goal-baseline-{2,3,4}. Critique binding is carried by the current `Reviewed Input Identity` section in `charness-artifacts/critique/2026-08-04-critique-review.md`; superseded packet files remain as audit history and are not current proof claims. The named-family manifest is charness-artifacts/quality/2026-08-04-reduce-closeout-runtime-structural-waste-cli-manifest.md.

### Slice 3: B repair — Produce the named CLI-family manifest and falsify it

- Objective: Satisfy the fresh-eye requirement for one named family by binding collected nodeids to process classification, boundary owner, retained proof, and measured cost.
- Why this approach: The midpoint claims review blocked closure because Slice B had rejected only a broad proposal. The exact `tests/charness_cli` standing family was already measured at 3.62s, so a node-level manifest could test the family honestly without inventing a migration.
- Commits: None; no production, test, gate, validator, generated plugin, or export logic changed.
- What changed: Added `charness-artifacts/quality/2026-08-04-reduce-closeout-runtime-structural-waste-cli-manifest.md`, a 155-node read-only manifest with an explicit boundary ledger and collection identity. The source-owned inventory-marker probe was refreshed after that new quality artifact changed its measured corpus; no gate logic changed.
- Alternatives rejected: Rejected converting the 94 in-process-only nodes merely because they share a directory with 58 main-CLI-delivery nodes; rejected treating mocked internal calls as real CLI startup savings; rejected broad migration from the 31.60s heterogeneous subset.
- Targeted verification: `python3 -m pytest --collect-only -q -m 'not release_only' tests/charness_cli` collected 155 nodes and deselected 46 release-only nodes. The canonical focused runner receipt `/tmp/charness-structural-goal-cli-1.log` reports 155 passed in 3.62s, below the fixed 10.0s bar. The manifest records 58 main-CLI-delivery, 3 internal-process, and 94 in-process-test classifications and retains the real boundary for the process-bearing nodes.
- Test duplication pressure: No tests were added, removed, or expanded. No verdict logic changed.
- Critique: The midpoint fresh-eye claims review initially blocked closure because the named-family evidence was absent and closeout text was stale. Its explicit boundary verify was clean: `/tmp/charness-reviewer-boundary-structural-goal-claims.json`, window `structural-runtime-goal-claims-20260804`, `drift: []`, no parent paths, staged paths, or HEAD movement. This repair addresses the blocker; a final claims review will read the completed closeout state.
- Off-goal findings: No issue, remote, provider, release, push, issue-close, Cautilus, or live-behavior action occurred. D51 remains a deferred owner for mutation/quality-gate runtime work.
- Lessons carried forward: A named family can be falsified by its measured upper bound before a migration is shaped. The manifest also shows why file co-location is not ownership: boundary-bearing nodes and in-process nodes must not be collapsed by directory pattern.
- Metrics: Collection receipt `/tmp/charness-structural-goal-cli-nodeids.txt`; nodeid SHA256 `56afd5bdfd97d1f661a9e4c6bd349843050399270bafdb0a9a4673decda634d9`; checked-in manifest SHA256 `3606059c0e69077134f4247af839294efe79fb6db836c0c64b90144cc77e2d9c`.

## Context Sources

1. [Design North Star](../../docs/design-north-star.md) — judgment on
   reversible work, and distinct evidence at proof boundaries.
2. [Completed bottleneck goal](2026-08-04-reduce-current-closeout-bottleneck.md)
   — local baseline, falsified worker-cap candidate, and closeout proof record.
3. [Bound retro](../retro/2026-08-04-reduce-current-closeout-bottleneck-retro.md)
   and [claims review](../critique/2026-08-04-reduce-current-closeout-bottleneck-claims-review.md)
   — recorded waste, repairs, and no-safe-change disposition.
4. [Recent lessons](../retro/recent-lessons.md) — repeat traps around stale
   artifacts, broad verification cost, and proof-boundary review.
5. [D51](../../docs/deferred-decisions.md#d51-release-branchci-barrier-and-quality-gate-runtime)
   — owner and reopen context for quality-gate runtime work.
6. Current quality inventories — standing-test economics, structural waste,
   clone families, dead-code advisory, and runtime summary; all are advisory
   signals pending candidate-level measurement.
7. [Named CLI-family manifest](../quality/2026-08-04-reduce-closeout-runtime-structural-waste-cli-manifest.md)
   — 155 collected nodes, boundary classifications, and the 3.62s family
   falsifier.

## Interview Decisions

- User priority: actual speed improvement over an elegant microbenchmark.
- User priority: duplicate execution/code removal and bootstrap cleanup before
  parallelism.
- Economic rule: an approximately eight-second saving with an hour-scale
  rollback burden is not a success; the initial end-to-end bar is ten seconds.
- Proof rule: preserve the closeout contract and use separate timing,
  correctness, failure, and independent-review channels.
- Superseded direction: broad-vs-focused semantic equivalence is not the next
  session's goal unless a later structural change makes it necessary.

## Plan Critique Findings

The first draft was too conservative: it turned an observed small speed delta
into a long equivalence investigation before asking whether the candidate could
ever repay the effort. This revision moves economic triage and structural
deletion ahead of equivalence work. Equivalence remains a preservation check
only when a selected candidate changes producer/consumer shape.

## Off-Goal Findings

The portability bootstrap fence, global runner policy, CI relocation, release
ordering, and historical telemetry remain separate concerns unless the selected
structural candidate directly proves they are on the measured path.

## Final Verification

- Disposition: broad nested-CLI migration rejected; the named `tests/charness_cli`
  family is falsified by its 3.62s measured upper bound. No production remedy
  was safe to implement under the ten-second full-closeout bar.
- Strong local evidence: three clean full read-only runs at immutable baseline
  commit `23f60313ca9c58a4bac235166966b87a5f3bbb37` passed 85/0; medians were 123.51s
  total, 48.9s standing pytest, and 120.2s changed-line mutation. The focused
  family manifest collected 155 nodes and its canonical runner passed 155 in
  3.62s. Sources are the Slice Log receipts and the checked-in manifest.
- Final quality gate: `./scripts/run-quality.sh --read-only` passed 85/0 in
  123.6s from `/tmp/charness-structural-goal-final-quality-final-3.log`, including
  pytest, changed-line mutation coverage, critique validation, and documentation
  and structural checks; only advisory warnings were emitted.
- Proof boundary: no child-process, packaging, environment, stderr/exit-code,
  generated-surface, validator, or mutation verdict contract was changed. One
  source-owned measurement probe was synchronized after the quality corpus
  changed. No remote,
  provider, release, push, issue-close, Cautilus, or live behavior claim is
  made.
Retro: charness-artifacts/retro/2026-08-04-reduce-closeout-runtime-structural-waste-retro.md
Host log probe: charness-artifacts/probe/2026-08-04-reduce-closeout-runtime-structural-waste.json
Disposition review: charness-artifacts/critique/2026-08-04-reduce-closeout-runtime-structural-waste-disposition-review.md

## User Verification Instructions

Review the structural-first order, the fixed ten-second economic bar, the
node-level manifest, and the no-safe-change disposition. The tested named family
was below the bar, so no code remedy was authorized; issues #505 and #506 carry
the separately owned runtime and reviewer-tool follow-ups.

For reference, the activation command was:

    /goal @charness-artifacts/goals/2026-08-04-reduce-closeout-runtime-structural-waste.md

Activation authorizes local measurement and reversible implementation only. It
does not authorize publication, push, release, issue close, Cautilus, or proof
weakening.

## Auto-Retro

Retro disposition: applied: node-level candidate manifest and stale closeout-state reconciliation
Retro disposition: issue #506 (recurs: #461 reviewer-boundary snapshot/window-binding class)
Retro disposition: applied: corpus-pinned measurement probes were synchronized after the quality corpus changed
Retro disposition: issue #505 (recurs: gate-baseline-runtime and D51 quality-gate owner)
Structural follow-up: issue #505 (recurs: gate-baseline-runtime is a transferable quality-gate runtime pattern)
