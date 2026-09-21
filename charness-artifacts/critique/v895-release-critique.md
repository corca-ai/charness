# Release Critique — charness 8.9.5 (v8.9.5)

- **Release Scope**: `8.9.4` → `8.9.5` (tag `v8.9.5`), patch. One-line
  consumer story: task-run persistence can no longer commit out-of-scope
  residue, release resume packets name their notes-file hole, staged
  eviction violations refuse at commit time, and reviewer results can
  declare the target set they must observe through an explicit opt-in.
- **Bump rationale**: patch, not minor: tooling repairs (persist scoping,
  resume placeholder, staged eviction owner, worker target flag, lane
  declaration, explicit floor opt-in, round-1/2 answers) plus regression
  tests; additive flags only complete the coverage-floor residual and
  break no existing invocation.
- **Reviewed delta**: `107f89c8c..HEAD` at review time across two rounds.
  Round 1 (`a`/`b`) reviewed the six slices; round 2 (`a2`/`b2`) reviewed
  the same delta plus the round-1 answers, the explicit opt-in correction,
  and the portable-anchor repair. The round-2 answers below landed on top
  and are covered by focused fail-old/pass-new tests plus the release
  lane, stated as non-claim.
- **Substrate**: four bounded fresh-eye reviewers (file-backed workers,
  backend `codex exec`, lenses below), parent-owned counterweight here. No
  same-agent substitution. Both rounds declared six prepared targets to
  the coverage floor with `coverage_ok: True` and every target observed
  exactly once.

Fresh-eye satisfaction: parent-delegated — four file-backed workers delivered (round 1: A block with 2 findings, B block with 1 finding; round 2: A2 block with 1 finding, B2 block with 1 finding); the parent counterweight repaired all five with regression tests and the release lane re-proves every changed line; no same-agent substitution occurred.

## Reviewer Tier Evidence

- Requested tier: n/a (no tier requested; host-defaulted)
- Requested spawn fields: n/a (run_review.py defaults; no explicit fork/model/effort ask)
- Host exposure state: host-defaulted
- Host detail: this host ran all four reviewers through `run_review.py` file-backed workers (backend `codex exec`, read-only); no provider-confirmed model or effort application claim
- Application state: file-backed read-only workers delivered; round 1 block/block and round 2 block/block received, approval not inferred
- Delivery state: findings-received
- Execution mode: file-backed-worker
- Worker A report: charness-artifacts/critique/workers/v895-release-critique-a/worker-report.yaml (verdict block, 2 findings)
- Worker B report: charness-artifacts/critique/workers/v895-release-critique-b/worker-report.yaml (verdict block, 1 finding)
- Worker A2 report: charness-artifacts/critique/workers/v895-release-critique-a2/worker-report.yaml (verdict block, 1 finding)
- Worker B2 report: charness-artifacts/critique/workers/v895-release-critique-b2/worker-report.yaml (verdict block, 1 finding)

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/v895-release-critique-a2-packet.json
- Packet SHA256: cf8bec24ffb7da50349880fef61f76f6e257ca525b4c425f47c1c583236a6dff
- Identity SHA256: 61980aa61e018101fb70232df87fea73a8a46e7fde7183a960ab68164cb6e20f
- Verify command: `python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/v895-release-critique-a2-packet.json --packet-sha256 cf8bec24ffb7da50349880fef61f76f6e257ca525b4c425f47c1c583236a6dff --identity-sha256 61980aa61e018101fb70232df87fea73a8a46e7fde7183a960ab68164cb6e20f`
- Reviewer B2 packet: charness-artifacts/critique/v895-release-critique-b2-packet.json
- Reviewer B2 packet SHA256: cfdc66e1ebdbab061d27fc4e8c5b0147ea7d3ce7f3efb097e21f9bb3d40d7d60
- Round-1 packets (superseded delta, retained as evidence): `v895-release-critique-a-packet.json`, `v895-release-critique-b-packet.json` with worker dirs `workers/v895-release-critique-a/` and `workers/v895-release-critique-b/`
- Worker reports: `workers/v895-release-critique-a2/worker-report.yaml` and `workers/v895-release-critique-b2/worker-report.yaml`

## Reviewer Verdicts

- Reviewer A (correctness and refusal safety):
  `workers/v895-release-critique-a/result.json` — verdict `block`,
  persist-scope unclassifiable fallback and eviction TOCTOU.
- Reviewer B (operator surface and failure messaging):
  `workers/v895-release-critique-b/result.json` — verdict `block`,
  coverage refusal precision.
- Reviewer A2 (round-1 answers, correctness):
  `workers/v895-release-critique-a2/result.json` — verdict `block`,
  denied-set classification strictness.
- Reviewer B2 (round-1 answers, operator surface):
  `workers/v895-release-critique-b2/result.json` — verdict `block`,
  remedy coverage across all five refusal messages.

## Finding Dispositions (evidence-led)

- **Round-1 A (persist-scope) — repaired.** Completed-lane persistence
  staged everything while the scope verdict failed on disallowed paths.
  Repair: commit only the verdict's admitted set; skip on empty or
  unclassifiable. Regression tests fail on the old shape and pass on the
  new one.
- **Round-1 A (eviction) — repaired.** Staged-scope owners judged worktree
  bytes while the commit takes index bytes. Repair: refuse an unstable
  staged scope with a restage remedy; explicit `--paths` judgment
  unaffected. Regression tests pin both directions.
- **Round-1 B (worker-expected-targets) — repaired.** Thin-result refusals
  named a count but not the dropped targets. Repair: name exact targets
  plus one shared remedy sentence; pre-existing exact-match tests pass
  unchanged.
- **Round-2 A2 (denied-set strictness) — repaired.** The skip handled a
  missing changed-paths but admitted everything on a missing/malformed
  denied set. Repair: both lists must be lists; the completion fixture
  states the denied set like production. Two new tests pin both shapes.
- **Round-2 B2 (remedy everywhere) — repaired.** The remedy rode only two
  of five refusal messages. Repair: all five name targets plus the shared
  remedy; the substance/singularity test requires the remedy text.
- **Round-2 answers — termination stated.** No round 3: every repair above
  is pinned by fail-old/pass-new regression tests and re-proven by the
  release lane's changed-line proof over the full delta.

## Boundary Ownership

- **Producer:** task-run completion/persistence, staged commit hooks,
  release planner packets, reviewer worker contract, critique lane, and
  the release procedure itself.
- **Consumer:** lane operators relying on candidate commits carrying only
  scoped paths; committers relying on pre-commit owners judging committed
  bytes; review authors declaring coverage floors through explicit opt-in.
- **Verdict:** `owned-correctly` — each repair lives in the module that
  owns the refused behavior, with standing tests beside it; the two
  length-cap splits (persist helper beside the WIP checkpoint; floor tests
  in their own module) follow the repo's split rule.

## Open Risks and residuals

- Critique-lane promotion does not re-enforce per-target coverage on
  lanes without the worker floor; recorded as a residual, no measured
  failure behind a mechanical rule there.
- The standing pytest runner takes nodeids but no `-k` filter; targeted
  repair loops use repeated `--pytest-target` instead.
- A deliberately bypassed claims marker (deleting the marker line and
  amending) still skips the claims floor; the floor prices carelessness,
  not sabotage (standing residual, restated).
- Coverage exact-string compliance rests on backends emitting the declared
  target strings verbatim; observed 4/4 in production, stated as the
  residual tail risk of the opt-in floor.
