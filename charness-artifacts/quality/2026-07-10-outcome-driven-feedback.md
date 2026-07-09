# Quality Review
Date: 2026-07-10

## Scope

Target boundary: outcome-driven self-improvement through a privacy-safe,
append-only `usage_feedback` event, its validator/reporter consumers, and the
checked-in plugin export.

Ambient repo findings: the broad gate first exposed inherited read-only test
state and 13 new clone fingerprints. Both were repaired before closeout; the
standing argparse-help and file-length advisories remain outside this slice.

## Current Gates

- Healthy: `./scripts/run-quality.sh --read-only` passed 81 gates with zero
  failures after the repairs.
- Healthy: focused feedback/report/schema/slice-closeout tests passed (104
  tests in the final focused rerun).
- Healthy: dup-ratchet is clean without widening its accepted baseline.
- Weak: changed-line mutation evidence is stale until the final committed
  verification-lock producer runs.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json`
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `pytest` 30.7s latest / 30.7s median, budget 140.0s;
  `dead-code-advisory` 7.8s / 7.8s; `check-coverage` 7.5s / 7.4s, budget
  55.0s; `check-markdown` 6.1s / 5.9s, budget 11.0s; `check-secrets` 5.0s /
  5.0s, budget 6.0s.
- coverage gate: broad deterministic gate passed; final changed-line mutation
  proof is intentionally deferred to the committed verification lock.
- evaluator depth: deterministic gates only. The Cautilus planner returned no
  required live action; no evaluator spend was authorized or needed for this
  schema/reconciliation contract.

## Healthy

- Delivery episodes and feedback events have separate denominators; 1,331
  existing deliveries still report zero feedback rather than inferred success.
- One shared record reader now owns JSONL schema, timestamp, and semantic
  validation for both validator and reporter, preventing a looser report path.
- The writer defaults to dry-run, rejects unlinked/unsafe/conflicting records,
  and permits read-only preview while blocking execution in quality mode.
- Source/plugin scripts and schemas are synchronized and plugin smoke covers a
  linked feedback event.

## Weak

- No real observer-owned feedback event has yet been observed in this checkout.
- The append path has no cross-process lock; concurrent identical executions
  can race and are detected only by subsequent validation.
- Test-production ratio remains 1.01 versus the 1.00 advisory threshold.

## Missing

- Missing: consumer-repo or remote evidence that an operator uses the feedback
  path and that the resulting signal changes a product decision.
- Missing: automatic issue/release/repository observers and stream-aware
  reconciliation across rotated JSONL files.
- Missing: pushed-branch or remote-CI proof; this work remains local.

## Deferred

- Deferred: automatic observers until one explicit/manual event proves the
  vocabulary and operator flow in real use.
- Deferred: append locking until concurrent/automatic writers create a real
  trigger, and rotation support until stream growth requires it.
- Deferred: prompt-vocabulary demotion pending its own integrated live capture;
  deterministic N=2 candidate evidence is insufficient.

## Advisory

- structural review result: command: `plan_quality_run.py`; the missing
  capability was honest outcome evidence, not another delivery gate. Existing
  schema/writer/validator/reporter centers were extended; no new quality gate
  or public skill was added.
- duplicate review result: command: `check_dup_ratchet.py`; the
  meaningful JSONL/counter/path clones were extracted, while 12 low-value or
  deliberately distinct fingerprints received specific intentional notes in
  `dup-review.json`; no full or scoped baseline accept was used.
- prose/public-skill review result: command: `suggest_public_skill_dogfood.py`
  for `quality` and `setup`; their routing and scenario contracts did not
  change, and the adapter template addition is covered by deterministic tests.
- claim-fidelity result: artifact: [feedback code critique](../critique/2026-07-10-usage-feedback-code-critique.md); a
  fresh-eye reviewer reproduced duplicate feedback inflating satisfaction above
  100%, and the shared semantic reader now makes that stream invalid everywhere.

## Delegated Review

- Delegated Review: executed — a lower-power worker implemented and hardened
  the code; two fresh-eye code lenses plus a counterweight reviewed privacy,
  compatibility, and producer/consumer ownership. All act-before-ship findings
  were repaired or explicitly dispositioned.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof):
  reviewed without a new delegation because gate topology did not change;
  runtime stayed within budgets, focused fixtures remained under nine seconds,
  and duplicated proof was reduced to one shared record reader.

## Commands Run

- command: `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --json`
- command: focused usage/report/schema/plugin/slice-closeout pytest runs.
- command: `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --json`
- command: `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --json`
- command: `./scripts/run-quality.sh --read-only`
- command: source/plugin compare, `ruff`, `py_compile`, packaging, and
  `git diff --check` checks.

## Recommended Next Quality Moves

- active first-real-feedback-dogfood — capability_needed=observer-owned outcome evidence; next_center=`record_usage_feedback.py`; transformation=record the first legitimate closed-enum event only when an operator/issue/release observation exists; proof_boundary=writer dry-run plus validator and reporter readback; enforcement_posture=advisory.
- passive automatic-feedback-observers because manual evidence semantics must be proven before adding producers; capability_needed=trusted lifecycle observers; next_center=issue/release adapters; transformation=map authoritative transitions to the existing event contract; proof_boundary=fixture roundtrip plus distinct observer readback; enforcement_posture=no-gate until one real event exists.
- passive concurrent-append-hardening until automatic or concurrent writers are introduced; capability_needed=idempotent multi-process append; next_center=feedback writer storage seam; transformation=lock or atomic append with replay proof; proof_boundary=race fixture plus validator readback; enforcement_posture=no-gate because the current explicit CLI is single-operator.

## History

- [2026-07-03 pytest suite test-value audit](./history/2026-07-03-pytest-suite-test-value-audit.md)
