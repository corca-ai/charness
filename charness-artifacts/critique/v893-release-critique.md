# Release Critique — charness 8.9.3 (v8.9.3)

- **Release Scope**: `8.9.2` → `8.9.3` (tag `v8.9.3`), patch. One-line
  consumer story: an interrupted task-run lane never persists harness
  residue or an empty tree as its WIP candidate, and release plans quote a
  declared lane command verbatim instead of recomposing its argument
  forwarding.
- **Bump rationale**: patch, not minor: two bug repairs (scoped WIP
  checkpoint, verbatim lane commands) plus repair-posture docs folded into
  implementation discipline; no new surface and no invocation break.
- **Reviewed delta**: `849119829..HEAD` at review time (commits for #816,
  #817, and the discipline merge; the A-001 repair below landed on top and
  is covered by focused tests plus the release lane, stated as non-claim).
- **Substrate**: two bounded fresh-eye reviewers (file-backed workers,
  backend `codex exec`, lenses below), parent-owned counterweight here. No
  same-agent substitution.

Fresh-eye satisfaction: parent-delegated — two file-backed workers delivered (A block with 2 findings, B defer with 1 evidence gap); the parent counterweight repaired A-001 with a regression test, refreshed receipts for A-002, and sequenced B-001 to claims review; no same-agent substitution occurred.

## Reviewer Tier Evidence

- Requested tier: n/a (no tier requested; host-defaulted)
- Requested spawn fields: n/a (run_review.py defaults; no explicit fork/model/effort ask)
- Host exposure state: host-defaulted
- Host detail: this host ran both reviewers through `run_review.py` file-backed workers (backend `codex exec`, read-only); no provider-confirmed model or effort application claim
- Application state: file-backed read-only workers delivered; A block with 2 findings and B defer with 1 gap received, approval not inferred
- Delivery state: findings-received
- Execution mode: file-backed-worker
- Worker A report: charness-artifacts/critique/workers/v893-release-critique-a/worker-report.yaml (verdict block, 1 high + 1 medium)
- Worker B report: charness-artifacts/critique/workers/v893-release-critique-b/worker-report.yaml (verdict defer, 1 blocking-evidence-gap)

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/v893-release-critique-a-packet.json
- Packet SHA256: 170827c8ddb01456eb08552530544cc59b46d8048ca91a89628772fca2f99994
- Identity SHA256: a91b1b080a6be7c8da5251b2280597e0087254780d6e5cde7ea48c35eb174ac5
- Verify command: `python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/v893-release-critique-a-packet.json --packet-sha256 170827c8ddb01456eb08552530544cc59b46d8048ca91a89628772fca2f99994 --identity-sha256 a91b1b080a6be7c8da5251b2280597e0087254780d6e5cde7ea48c35eb174ac5`
- Reviewer B packet: charness-artifacts/critique/v893-release-critique-b-packet.json
  (same 51 reviewed paths in charness-artifacts/v893-reviewed-paths.txt)
- Worker reports: `workers/v893-release-critique-a/worker-report.yaml` and
  `workers/v893-release-critique-b/worker-report.yaml`

## Reviewer Verdicts

- Reviewer A (correctness and refusal safety):
  `workers/v893-release-critique-a/result.json` — verdict `block`,
  1 high + 1 medium.
- Reviewer B (operator surface and failure messaging):
  `workers/v893-release-critique-b/result.json` — verdict `defer`,
  1 blocking-evidence-gap (8.9.3 notes absent from the reviewed input by
  sequencing; notes are derived at prepare, legibility audited at claims
  review).

## Finding Dispositions (evidence-led)

- **CRITIQUE-A-001 (high) — repaired.** The scoped WIP commit carried the
  scope only at `git add` time; `git commit` then committed the whole
  index, so content the lane had staged outside the scope rode along.
  Repair: the commit itself carries the scope pathspec
  (`git commit -- <paths>`); prestaged out-of-scope content stays staged
  and out of the commit. Regression test
  `test_timeout_with_prestaged_out_of_scope_change_keeps_it_out_of_wip`
  fails on the old shape and passes on the new one. Landed as
  `be43866db` after A's review; covered by the focused suites below.
- **CRITIQUE-A-002 (medium) — addressed.** Approval receipts predated the
  final helper move and attention declaration. Fresh receipts on the final
  tree: 118 passed across the five task-run suites plus the planner
  suite; `validate_attention_state_visibility` valid; ruff clean.
- **CRITIQUE-B-001 (evidence gap) — sequenced, not waived.** Operator
  legibility of the 8.9.3 notes cannot be judged before the notes exist.
  The notes are derived at prepare and audited by the claims review
  before execute; this artifact does not claim their legibility.

## Boundary Ownership

- **Producer:** the task-run lane owns the WIP checkpoint
  (`task_run_lane_runner.py`, consumed only by the abnormal-exit path);
  the release skill owns lane-command rendering
  (`adapter-contract.md`, read-only guidance); the quality skill owns the
  attention-state declaration.
- **Consumer:** operators running repository-changing lanes and release
  planners quoting declared lane commands.
- **Owning surface:** the task-run execution surface and the release
  planner contract — the scope verdict, receipt schema, and adapter
  machinery are untouched, so their semantics do not move with this
  change.
- **Verdict:** `owned-correctly` — each repair lives in the module that
  owns the refused behavior, with standing tests beside it.

## Non-claims

- The A-001 repair commit postdates A's packet; its proof is the
  fail-before/pass-after regression test and the 118-test focused run,
  not A's verdict.
- No live muse-lane roundtrip re-proves #814 on this tree; the workspace
  construction is held by unit tests and receipts only.
- Observer distinctness for any post-publication readback is recorded at
  that boundary, not inferred here.
