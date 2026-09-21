# Claims Review — charness 8.9.6 (v8.9.6)

Subject: `charness-artifacts/release/latest.md` at prepared commit a4f73f8f8eeb for target version 8.9.6 (second prepare; first abandoned pre-push; hash bound by the scaffold record, not by this text).
Observer: file-backed worker `v896-claims`
(`charness-artifacts/critique/workers/v896-claims/`, backend `codex exec`,
verdict block with 2 record findings, no code findings).

## Version claim

- Record claims target `8.9.6` from previous `8.9.5`. Verified: prepared
  commit carries `"version": "8.9.6"` in `packaging/charness.json` and the
  marketplace manifest. The per-executor plugin manifests regenerate at
  publish sync; their absence from the prepared commit matches the
  helper's stated order, not a gap.
- Bump rationale rendered verbatim as passed (patch, not minor).

## Verification lines

- Record says the read-only quality command exited 0 (163.5 s) and states
  `pytest-release pending final resume`, i.e. quality explicitly
  unestablished pending resume — no premature green claimed. Verified
  against the helper output.
- Fresh-checkout probes reported passed (3/3). No release-notes figures
  are asserted by the record, so there is nothing to bind.
- Full release-lane evidence for the shipped code exists independently:
  `run-quality.sh --full --release`, 89 passed, 0 failed, on the fix
  commits (receipt-matched), plus focused fixture suites.

## Closeout linkage (worker F1)

- Worker is right that `Issue closeout verification: pending or not
  requested` conflates two states. Exact state: closeout REQUESTED for
  #815 and #822 (bundled bug carrier validated pre-publish with no
  missing fields or bindings), verification PENDING the resume run, which
  performs it and rewrites this record. No silent not-applicable is
  claimed. Advisory only; no code or carrier change required.

## Review-proof linkage (worker F2)

- Worker is right the critique artifact was outside its three semantic
  inputs. Verified directly: `charness-artifacts/critique/v896-release-critique.md`
  exists, is committed, cites #815 and #822, records all six worker
  verdicts (five blocks answered in code, final narrow pass with no
  findings), and carries the final packet/identity pair
  (`v896-critique-d-packet.json`,
  packet `6880c98f…`, identity `f7d118a8…`; verify command in the
  artifact). The final release record already names it under Review
  Proof. Advisory only.

## Non-claims

- Tag push, branch push, GitHub release creation, public readback, and
  install refresh are all pending resume — the record claims none of
  them. Closeout states on GitHub (#815, #822) are unverified until the
  resume's `verify-closeout` re-reads them as CLOSED.
