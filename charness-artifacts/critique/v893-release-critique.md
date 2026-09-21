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

## Reviewed Input Identity

- Packet A: charness-artifacts/critique/v893-release-critique-a-packet.json
  (sha256 `170827c8ddb01456…`, 51 reviewed paths in
  charness-artifacts/v893-reviewed-paths.txt)
- Packet B: charness-artifacts/critique/v893-release-critique-b-packet.json
  (sha256 `06c1566f0e31b6ca…`, same reviewed set)
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

## Non-claims

- The A-001 repair commit postdates A's packet; its proof is the
  fail-before/pass-after regression test and the 118-test focused run,
  not A's verdict.
- No live muse-lane roundtrip re-proves #814 on this tree; the workspace
  construction is held by unit tests and receipts only.
- Observer distinctness for any post-publication readback is recorded at
  that boundary, not inferred here.
