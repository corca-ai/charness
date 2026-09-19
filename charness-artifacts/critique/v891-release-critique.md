# Release Critique — charness 8.9.1 (v8.9.1)

- **Release Scope**: `8.9.0` → `8.9.1` (tag `v8.9.1`), patch. One-line
  consumer story: establishing an issue-native Goal Run no longer requires
  reverse-engineering the binding freeze, the bootstrap body block, the
  attempt-id rule, the progress cursor shape, or the planning-section writer.
  Closes `corca-ai/charness#821`.
- **Bump rationale**: patch, not minor: every change repairs the Goal Run
  establishment path the skill surface already promised (`freeze and hash`,
  first-`update-body` bootstrap, single-use attempts, parent cursor, planning
  writer). The new `freeze` subcommand restores documented behavior rather
  than adding an adoptable capability; no invocation breaks, so not major.
- **Reviewed delta**: commit `4b7722b02` (8 files: `goal_binding.py` freeze
  dispatcher plus dependency canonicalization, new `goal_binding_freeze.py`,
  `issue_tracker_observation.py` reuse hint, three skill docs, new freeze
  CLI tests); plus a repair commit answering the reviewers below
  (pre-read draft validation, `--binding-path` removal, parent-readback
  transcription note, regression tests).
- **Substrate**: two bounded fresh-eye reviewers (file-backed workers,
  backend `codex exec`, lenses below), parent-owned counterweight here. No
  same-agent substitution.

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/2026-09-19-050038-packet.json
- Packet SHA256: daa8d78a88ab7201a9a29877c96d58f4c1815f8b9c6f56cd303981efa217e7a5
- Identity SHA256: 7f0311e26d5963157a9bc6ad5f0f3ecdf4c5c686849ce610b33c34380f04a82f
- Verify command: `python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/2026-09-19-050038-packet.json --packet-sha256 daa8d78a88ab7201a9a29877c96d58f4c1815f8b9c6f56cd303981efa217e7a5 --identity-sha256 7f0311e26d5963157a9bc6ad5f0f3ecdf4c5c686849ce610b33c34380f04a82f`
  (verified `current` before reviewer start; the repair commit on top is
  covered by focused tests and the release lane, stated as non-claim below).

## Reviewer Verdicts

- Reviewer A (operator verification and release safety):
  `workers/v891-release-critique-a/result.json` — verdict `block`,
  1 high + 1 medium.
- Reviewer B (communication and operator surface clarity):
  `workers/v891-release-critique-b/result.json` — verdict `block`,
  2 blockers.

## Finding Dispositions (evidence-led)

- **R1 (A-high) — valid but deferred to a follow-up slice.** Claim: corrupt
  started receipts are skipped by `find_unresolved_create`, permitting a
  second create without establishing the first mutation. The code reading is
  accurate (malformed receipts `continue` past recovery). Not repaired here:
  the recovery path is pre-existing behavior outside this slice's changed
  lines, receipts are written atomically (temp file plus hard link), and a
  fail-closed redesign needs its own provider-behavior design, not a release
  rider. Follow-up: file the fail-closed recovery hardening separately.
- **R2 (A-medium) — addressed by repair.** Claim: the freeze CLI hashed the
  draft before validating the path, reading out-of-repository files before
  refusal. Repair: `resolve_draft_for_read` validates spelling and
  containment before any open; absolute, traversal, and symlink-escape
  drafts refuse as `path-invalid`. Proof: new in-process tests
  (`test_freeze_rejects_out_of_repo_draft_before_read`,
  `test_resolve_draft_for_read_refuses_symlink_escape`) plus the release
  lane green.
- **CLARITY-001 (B-blocker) — addressed by documentation, the permitted
  option.** Claim: the CLI builds parent identity from flags without the
  provider readback the skill orders first. Repair: `SKILL.md` now states
  the read is an external prerequisite whose repo/number are transcribed
  into `--parent-repo`/`--parent-number`, and that provider authority is
  enforced later by `goal-run-apply` against live parent metadata.
- **CLARITY-002 (B-blocker) — addressed by deletion.** Claim:
  `--binding-path` promised an override the validator always refuses.
  Repair: the flag is removed; the binding always lands at the deterministic
  sibling and the success payload reports it. Proof: new test asserting the
  flag is rejected as unrecognized, plus the release lane green.

## Fresh-Eye Satisfaction

parent-delegated — two file-backed workers delivered block verdicts with evidence-backed findings; the parent counterweight dispositioned every finding and no same-agent substitution occurred.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: fork_turns=none, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority
- Host exposure state: host-defaulted
- Host detail: this host ran both reviewers through `run_review.py` file-backed workers (backend `codex exec`, read-only); no provider-confirmed model or effort application claim
- Application state: file-backed read-only workers delivered; two block verdicts with findings received, approval not inferred
- Delivery state: findings-received
- Worker A report: charness-artifacts/critique/workers/v891-release-critique-a/worker-report.yaml (verdict block, 1 high + 1 medium)
- Worker B report: charness-artifacts/critique/workers/v891-release-critique-b/worker-report.yaml (verdict block, 2 blockers)

## Boundary Ownership

- **Producer:** the achieve skill owns the freeze CLI (`goal_binding.py`
  dispatcher plus `goal_binding_freeze.py`), the cursor reference
  (`lifecycle-during.md`), and the writer rule (`goal-artifact.md`); the
  issue skill owns the bootstrap/attempt-id contract (`issue-backend.md`)
  and the observation hint (`issue_tracker_observation.py`).
- **Consumer:** operators and agents establishing issue-native Goal Runs,
  who previously reverse-engineered these contracts from old run artifacts.
- **Owning surface:** the Goal Run establishment surface — each repair
  lives in the module that owns the contract it clarifies, with standing
  tests beside the changed behavior.
- **Verdict:** `owned-correctly` — each clarified contract is produced and
  consumed by its correct owner; no shared or generic layer carries
  caller-specific establishment knowledge.

## Counterweight

Both `block` verdicts named real defects inside this slice's changed lines,
and all three in-scope findings are repaired above with regression tests
rather than argued away. The one deferral (R1) is pre-existing code with an
atomic-write mitigation and a concrete follow-up, not a ship-blocker for a
docs-and-CLI repair that never touches the recovery path. The repair commit
itself was re-read by the parent against both result files; that reread is
parent judgment, not independent evidence (see non-claims).

## Non-claims

- No provider roundtrip, host exposure, or external issue-state verification
  was performed.
- The repair commit on top of the reviewed packet was not re-reviewed by a
  fresh eye; its proof is focused tests plus the release lane.
- No claim is made about unreviewed files or the complete Goal Run
  implementation.
