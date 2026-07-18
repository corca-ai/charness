# Gajae-Code Pattern Review
Date: 2026-07-19

## Source

- Canonical source: local sibling checkout `../gajae-code`
- Source revision: `7dc297145f333a00b7e913ce7c8cd5dedeb3fd34`
- Source state: `main`, aligned with `origin/main`, clean at acquisition time
- Requested scope: transferable patterns for Charness architecture, workflow,
  runtime robustness, token efficiency, tests, CI, and release proof

## Knowledge Capability

Let a later Charness maintainer distinguish evidence-backed Gajae-Code patterns
from implementation-specific machinery, then select adoption work without
re-scanning the sibling repository or forgetting the Charness north star.

## Access Mode And Route

- Access mode: direct read-only local filesystem and Git inspection
- Planner input: `file:///home/hwidong/codes/gajae-code`, classified as
  `local_or_unknown`
- Selected attempt: direct local reads; no browser, network, provider, or
  credentialed source was needed
- Review lanes: workflow/state, efficiency/CI/release, and runtime/protocol

## Captured Facts

### Workflow And State

- Gajae-Code exposes four workflow skills and four role agents from source-owned
  defaults rather than checked-in runtime copies. Evidence: `AGENTS.md`,
  `packages/coding-agent/src/defaults/gjc/skills/`, and
  `packages/coding-agent/src/prompts/agents/`.
- `ultragoal` separates canonical goal state from an append-only JSONL proof
  stream and reserves state mutation for the leader. Workers return evidence.
  Evidence:
  `packages/coding-agent/src/defaults/gjc/skills/ultragoal/SKILL.md`.
- `ralplan` joins architect and critic verdicts against the same plan path,
  digest, and stage before finalization. Evidence:
  `packages/coding-agent/src/defaults/gjc/skills/ralplan/SKILL.md`.
- Team tasks carry claim tokens, versions, leases, dependencies, role limits,
  and typed completion evidence. Evidence:
  `packages/coding-agent/src/gjc-runtime/team-runtime.ts` and
  `packages/coding-agent/test/gjc-runtime/team-runtime.test.ts`.
- Task results sent back to a parent are receipts: bounded synopsis, accounting,
  and `agent://` output reference. Raw-output keys are explicitly excluded.
  Evidence: `packages/coding-agent/src/task/receipt.ts`.

### Efficiency, Tests, And CI

- The orchestration benchmark computes deterministic token, cache, prefix,
  receipt/artifact, fork-clone, and spawn-decision metrics from fixtures without
  a provider, network, or clock. Evidence:
  `packages/orchestration-token-benchmark/src/` and its tests.
- Gajae-Code keeps applied and held default reductions with reasons. Its hard
  gate additionally requires benchmark and human-approval evidence. Evidence:
  `packages/orchestration-token-benchmark/src/default-reduction-gate.ts` and
  `default-reductions.ledger.ts`.
- Session statistics use an incremental local SQLite index keyed by source
  identity, size/mtime/offset, and parser version. Evidence:
  `scripts/session-stats/sync.py`, `analyze.py`, and `README.md`.
- Affected CI emits a canonical task plan, maps direct and behavioral test
  owners, broadens on push, fails conservatively when selection inputs are
  uncertain, and validates shard receipts. Evidence:
  `scripts/ci-dev-affected.ts`, `ci-dev-affected.test.ts`, and
  `.github/workflows/dev-ci.yml`.

### Release And Runtime Boundaries

- Multi-package release evidence binds expected packages, versions, hashes,
  dependency closure, registry readback, and bounded tar extraction. Evidence:
  `scripts/release-evidence.ts` and release tests. The npm-specific machinery is
  not directly analogous to Charness packaging.
- Gajae-Code's recorded RPC failures show three portable protocol risks:
  response identity loss, a serial input loop blocking unrelated control work,
  and broad probe-error collapse. Evidence: `issues/01-*`, `issues/13-*`, and
  `issues/19-*`.
- Its process postmortem helper makes cleanup idempotent and distinguishes an
  attributable stdout broken pipe from an ordinary fatal error. Evidence:
  `packages/utils/src/postmortem.ts` and related tests.
- TUI sanitization and Bun-specific process machinery are real product needs in
  Gajae-Code, but Charness has no interactive TUI and should not copy them.

## Transfer Decisions

| Candidate | Decision | Charness reason |
| --- | --- | --- |
| One deadline and response correlation per app-server transaction | adopt first | Current `refresh_codex_cache_via_app_server` restarts its timeout whenever an unrelated message arrives, so a notification stream can extend a nominally bounded call indefinitely. |
| Bind critique verdicts to an exact reviewed snapshot | adopt | Current parent-side reviewer fingerprint proves no shared-tree mutation during a review, but the durable critique packet records only `changed_ref`, not a digest of the reviewed packet/artifact state. |
| Formal machine-readable release observer contract | adopt | v2.1.4 already produced an honest observer JSON; promote that successful local pattern into a versioned schema/renderer instead of leaving it ad hoc. |
| Shared efficiency-evidence envelope | adopt as advisory | Existing A/B tooling has correctness-adjacent metrics but deterministic fixtures and live samples lack one explicit comparability/reconstruction vocabulary. |
| Incremental local session-audit index | probe, then adopt if useful | Existing token audit is honest but repeatedly reparses sources; a local index could reduce analysis cost without collecting raw tool results. |
| Affected-CI narrowing | probe only | Charness gates are cross-cutting and no current wall-clock sample proves CI selection is the bottleneck. Start with an explainable plan, not narrower CI behavior. |
| Goal event receipts, leases, and dependencies | defer | Useful for durable cross-session orchestration, but Charness already has goal artifacts and task envelopes. Add only after a concrete stale-claim or state-rewrite failure. |
| Leader-only goal status mutation | retain/clarify | Charness reviewers are already read-only; make parent ownership explicit only at the existing coordination seam. |

## Deliberately Not Transferring

- The tmux team runtime, pane lifecycle, worktree scheduler, and detached-session
  registry: host orchestration owns this in Charness.
- Mandatory planner/architect/critic consensus for all work: it adds teeth to
  reversible work and conflicts with P1.
- File-count or LOC thresholds that force delegation: these are proxy rules,
  not proof that parallelism earns its cost.
- Gajae-Code's hard default-reduction approval gate, especially its fixed PR
  anchor: retain the evidence taxonomy, not a reversible-work block.
- npm tarball closure machinery, Bun process hooks, TUI/ANSI sanitation, and
  TypeScript-specific dispatch types: implementation-shaped, not portable
  Charness concepts.
- Any completion receipt as terminal truth at release, deletion, issue-close,
  or external-write boundaries: Charness P4/P5 still require a different
  observer and evidence channel.

## Captured Vs Human Confirmation

- Captured: repository files and Git revision listed above, plus three bounded
  read-only comparative reviews.
- Inference: the transfer decisions compare those facts with current Charness
  code and `docs/design-north-star.md`; they are maintainer planning judgments,
  not Gajae-Code claims.
- Human confirmation: the user asked for review and a checked-in adoption plan;
  no implementation priority beyond that request was separately confirmed.

## Open Gaps

- No Gajae-Code benchmark or test suite was executed; code/test structure was
  inspected read-only.
- README/report performance numbers were not treated as independently verified
  measurements unless committed raw evidence made them reproducible.
- No Charness CI critical-path baseline was collected, so affected-CI narrowing
  remains a probe.
- No real Codex app-server protocol probe was run; the current timeout-reset
  behavior is proven by code inspection and still needs a regression fixture.

## Canonical Plan

The implementation sequence and acceptance contract live in
`charness-artifacts/spec/2026-07-19-gajae-code-adoption-plan.md`.
