# Release Critique — charness 8.9.2 (v8.9.2)

- **Release Scope**: `8.9.1` → `8.9.2` (tag `v8.9.2`), patch. One-line
  consumer story: create recovery fails closed on unreadable receipts
  instead of risking a duplicate child, and quoting the Goal Run marker
  in code no longer blocks a routine issue close.
- **Bump rationale**: patch, not minor: two refusal-behavior repairs with
  no new surface and no invocation break; the close guard accepts strictly
  more legitimate closes, create recovery strictly fewer silent retries.
- **Reviewed delta**: commit `a5309008c` (4 files: close-guard code-span
  stripping, `find_unresolved_create` fail-closed, guard tests, receipt
  tests); plus a repair commit answering the reviewers below (tilde
  fences, closed-pair-only stripping, non-mapping target guard,
  regression tests).
- **Substrate**: two bounded fresh-eye reviewers (file-backed workers,
  backend `codex exec`, lenses below), parent-owned counterweight here. No
  same-agent substitution.

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/2026-09-19-080551-packet.json
- Packet SHA256: 3804d3b768126d5f6e88c5fa0368f57fc9d29728407fb143e0d6a5c9fc1985f7
- Identity SHA256: 290f6cf08a7678f6af14bd030e0486dfcb633750fa4511bfd61725dd6b87b4e5
- Verify command: `python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/2026-09-19-080551-packet.json --packet-sha256 3804d3b768126d5f6e88c5fa0368f57fc9d29728407fb143e0d6a5c9fc1985f7 --identity-sha256 290f6cf08a7678f6af14bd030e0486dfcb633750fa4511bfd61725dd6b87b4e5`
  (verified `current` before reviewer start; the repair commit on top is
  covered by focused tests and the release lane, stated as non-claim below).

## Reviewer Verdicts

- Reviewer A (correctness and refusal safety):
  `workers/v892-release-critique-a/result.json` — verdict `block`,
  1 medium + 1 high.
- Reviewer B (operator surface and failure messaging):
  `workers/v892-release-critique-b/result.json` — verdict `block`,
  2 highs (one shared root cause with A) + 1 medium.

## Finding Dispositions (evidence-led)

- **CRITIQUE-001 (A-medium) — addressed.** Tilde fences unrecognized.
  Repair: fence pairing per style (backtick and tilde); only closed pairs
  strip. Proof: tilde-fence regression test plus the release lane green.
- **CRITIQUE-002 + operator-valid-receipt-malformed-target-crash (A-high,
  B-high, same defect) — addressed.** Hash-valid receipt with a
  non-mapping target crashed nested access. Repair: mapping check before
  dereference, explicit `started-observation-schema-invalid` unresolved
  reason. Proof: parametrized null/scalar/list target tests plus the
  release lane green.
- **close-guard-unclosed-fence-fail-open (B-medium) — addressed.**
  Unclosed fence hid later blocks under toggle stripping. Repair: closed
  pairs only; a trailing unpaired opener stays scannable, so it can never
  hide a later block (documented cost: a mention after an unclosed fence
  still refuses). Proof: both regression tests plus the release lane
  green.

## Fresh-Eye Satisfaction

parent-delegated — two file-backed workers delivered block verdicts with evidence-backed findings; the parent counterweight repaired every finding with regression tests and no same-agent substitution occurred.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: fork_turns=none, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority
- Host exposure state: host-defaulted
- Host detail: this host ran both reviewers through `run_review.py` file-backed workers (backend `codex exec`, read-only); no provider-confirmed model or effort application claim
- Application state: file-backed read-only workers delivered; two block verdicts with findings received, approval not inferred
- Delivery state: findings-received
- Worker A report: charness-artifacts/critique/workers/v892-release-critique-a/worker-report.yaml (verdict block, 1 medium + 1 high)
- Worker B report: charness-artifacts/critique/workers/v892-release-critique-b/worker-report.yaml (verdict block, 2 highs + 1 medium)

## Boundary Ownership

- **Producer:** the issue skill owns both repairs — the close guard
  (`issue_goal_run_guard.py`, used only by the generic-close ingress)
  and create recovery (`issue_tracker_observation.py`, consumed only by
  the create paths).
- **Consumer:** operators closing marker-quoting issues and every
  Goal Run create retry.
- **Owning surface:** the issue-provider ingress/recovery surface — the
  shared metadata parser is untouched, so provider read/write semantics
  do not move with this change.
- **Verdict:** `owned-correctly` — each repair lives in the module that
  owns the refused behavior, with standing tests beside it.

## Counterweight

Both `block` verdicts named real defects inside this slice's changed
lines (one shared root cause counted twice), and all four are repaired
above with regression tests rather than argued away. The repair commit
itself was re-read by the parent against both result files; that reread
is parent judgment, not independent evidence (see non-claims).

## Non-claims

- No provider roundtrip, host exposure, or external issue-state verification
  was performed.
- The repair commit on top of the reviewed packet was not re-reviewed by a
  fresh eye; its proof is focused tests plus the release lane.
- No claim is made about unreviewed files or the complete Goal Run
  implementation.
