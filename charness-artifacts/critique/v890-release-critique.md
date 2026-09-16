# Release Critique — charness 8.9.0 (v8.9.0)

- **Release Scope**: `8.8.0` → `8.9.0` (tag `v8.9.0`), minor. One-line
  consumer story: a declarative mutation plan entry may set
  `expected_failing_test` so a Node/TAP mutant kills only when the intended
  named test fails; an unrelated failure refuses and a green run survives.
  Closes `corca-ai/charness#820`, unblocking downstream `corca-ai/ceal#830`
  parity (retire the Ceal guard-mutation runner fork).
- **Bump rationale**: minor, not patch: new additive operator-facing
  capability (plan field + payload field + reporter names) that existing
  users adopt without migration; no invocation break, so not major.
- **Reviewed delta**: `v8.8.0..HEAD` product change is commit `96b9c6560`
  (5 files: `mutation_expected_failure.py` new, `mutate_and_restore.py`,
  `mutation_sweep_report.py`, `mutation_test_reporters.py`,
  `test_mutation_test_reporters.py`); the remaining commits in range are
  8.8.0 release bookkeeping.
- **Substrate**: two bounded fresh-eye reviewers (file-backed workers,
  backend `codex exec`, lens `release-critique`), parent-owned
  counterweight below. No same-agent substitution.

## Surface-Lock Inventory

- `scripts/mutation/*` operator surface (plan schema gains optional
  `expected_failing_test`; sweep YAML payload gains per-mutant
  `expected_failing_test`).
- Generated manifests via adapter sync (`sync_root_plugin_manifests.py`) —
  verified, not hand-edited, at publish time by the release helper.
- Release notes / artifact (`charness-artifacts/release/`) derived at
  publish time over the final tree.
- No CLI flag, doctor exit code, README Quick Start, or install
  prerequisite changes.

## Reviewer Verdicts

- Reviewer A (operator/verification angle):
  `workers/review-20260917T030135Z-3406777/result.json` — verdict `block`,
  2 blockers + 1 high.
- Reviewer B (communication/operator-surface angle):
  `workers/review-20260917T030236Z-3407357/result.json` — verdict `block`,
  2 blockers + 2 majors.

## Finding Dispositions (evidence-led)

- **REL-820-1 (blocker) — verifier-defect, refuted with new evidence.**
  Claim: real-Node acceptance tests omit `--test-reporter=tap`, so the
  acceptance path can refuse instead of proving kill/refuse/survive.
  Measurement: all 85 tests in
  `tests/quality_gates/test_mutation_test_reporters.py` pass, including the
  real-`node --test` end-to-end #820 cases (declared name kills,
  unfailed name refuses, file restored); direct probe shows
  `node --test` on node `v22.22.2` emits `TAP version 13` by default, which
  `NodeTestReporter` reads. The `spec`-reporter refusal plus the named
  one-flag fix exists for consumers who explicitly configure
  `--test-reporter=spec`. No tree change; the failure mode does not occur
  on this repo's toolchain.
- **REL-820-2 (blocker) — scope-too-broad; addressed by the release
  helper.** The reviewer demanded manifest-sync/packaging execution
  evidence from a code-only packet. That evidence belongs to the publish
  boundary, which the repo-owned helper performs before tag push (sync,
  both packaging validators, fresh-checkout probes). Recorded as a
  release-time gate, not a code defect; receipts land in the release
  artifact.
- **B1 release-communication-evidence-missing (blocker) —
  scope-too-broad; addressed by the publish + claims-review boundary.**
  Release notes are derived over the FINAL tree at publish time, so no
  code packet can contain them. The communication path is reviewed by the
  claims-review round against the prepared record before publication.
- **B3 downstream-problem-framing-unproven (blocker) — Over-Worry for
  this gate.** Module/test prose foregrounding internal issue numbers is
  engineering documentation, not operator surface; the downstream bridge
  (`ceal#830`) lives in the `corca-ai/charness#820` body, which the
  release notes derive from (commit subject names `#820`) and the issue
  closeout carrier links. No operator behavior changes on reframing.
- **REL-820-3 (high) — Valid but Defer.** Fresh-checkout/doctor evidence
  comes from the publish helper gates; interrupted-journal (SIGKILL)
  recovery simulation is real but beyond this release's scope. Recorded
  as an open risk, not a ship blocker.
- **B2 contract-too-implicit (major) — Valid but Defer.** Refusal text is
  actionable per the reviewer's own evidence; consolidating a
  copy-pasteable operator contract is a docs improvement for a later
  slice, not worth re-cutting the reviewed delta.
- **B4 act-before-ship-checklist (major) — addressed by the release
  helper**, same as REL-820-2 (sync + validators + fresh probes +
  install-refresh readback with receipts).

## Operator Action Required

None beyond the standard publish gates: run the repo-owned publish
helper (sync, quality receipt, fresh probes, tag, push, public release,
distinct-channel readback, install refresh), complete the claims-review
round on the prepared record, then close #820 through the validated
carrier.

## Upgrade Path

No migration. `expected_failing_test` is absent-means-any-failure by
default; existing plans behave exactly as before. Rollback: repin
`8.8.0`; no data format changed.

## Non-claims

- The critique does not establish that the full release quality gate
  passes; that is the publish helper's pre-push receipt.
- Interrupted-mutation recovery is unproven at this boundary (open risk).
- Call-site reachability for `.js` targets remains an explicit non-claim
  (`could not be APPLIED`), by design.
