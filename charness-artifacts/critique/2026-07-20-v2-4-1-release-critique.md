# Critique Review
Date: 2026-07-20

## Decision Under Review

Publishing charness v2.4.1, a PATCH release from v2.4.0. Content:

- the #448 dup-ratchet scoped-rebaseline evaluate-parity fix (committed
  45ec7a24; slice critique at
  [2026-07-20-dup-ratchet-scoped-rebaseline-parity-critique.md](2026-07-20-dup-ratchet-scoped-rebaseline-parity-critique.md));
- the #446 CI mutation-baseline root-cause fix, bundled at release critique
  time: `test_standing_pytest_command_replaces_targets_without_losing_xdist`
  hardcoded `-n 16` while `choose_xdist_workers()` returns
  `min(cpu_count, 16)` — deterministic failure on the 4-core CI runner, not
  the previously-diagnosed basetemp flake. Fix pins `cpu_count=36` in-test
  (file idiom); a dedicated fresh-eye reviewer verified correctness,
  right-layer placement, full class drain (all other `-n`/`16` assertions
  pin `cpu_count` or assert core-relative), and comment framing;
- reviewer-prescribed polish: `--accept-rotation`/`--accept-family` `--help`
  strings now name the exemption (twin surface of the fixed reference doc),
  and advisory lines aligned (`ADVISORY (intentional)` prefix + by-design
  reassurance; scoped reduction advisory regained "not new duplication").

Bump rationale (recorded per version-policy guardrail): patch, not minor —
the new `ignored_intentional`/`unnamed_reductions` JSON keys and the
scoped-accept exit-flip are incidental evidence surfaces of a bug fix on a
hand-run maintenance command; the evaluate/CI gate path and public shape are
preserved.

## Execution

Three bounded release angle reviewers (Gawande operational, Minto
communication, Raskin interface) plus one fix-scoped fresh-eye reviewer and
one separate counterweight, all typed read-only `bounded-reviewer` subagents
in the shared worktree. Rail-1 fingerprint: angle-window verify flagged one
worktree drift — `tests/quality_gates/test_standing_pytest_runner.py`, the
parent's own #446 fix applied mid-window via a documented Edit call after the
CI failure landed; `git status` confirmed no other drift and reviewer
envelopes are read-only (one reviewer independently reported the read-only
binding). Attribution: parent edit, not reviewer misconduct; no approvals
quarantined. The tree was re-snapshotted before the counterweight spawn and
that verify returned `ok: true`, `drift: []`.

Fresh-Eye Satisfaction: parent-delegated
Target: release critique (`references/release-critique.md`)

Packet Consumed: charness-artifacts/critique/2026-07-20-131142-packet.md

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/2026-07-20-131142-packet.json
- Packet sha256: 5961c3c76272db039eae2858d02b99f1b3c9c0e8c0780fcb853af04778964a79
- Identity sha256: a4a4281eb4075b02d67b6dd3ed91325355f182f5799f688af8670fc0e860ef8a
- Note: the packet binds the `v2.4.0..HEAD` range at review time
  (HEAD=45ec7a24). The #446 test fix and help/advisory polish reviewed above
  are worktree deltas reviewed directly by the fix-scoped reviewer and the
  counterweight; they commit together with this artifact.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: none — the adapter's `high-leverage` mapping is the
  Codex host contract; on this Claude Code host the per-host split uses typed
  `bounded-reviewer` with session-model inheritance (not a degradation).
- Host exposure state: host-defaulted
- Application state: not-applied (session-model inheritance; no per-spawn
  model/effort fields sent)

## Failure Angles

- Operational: mirror sync completeness, bump honesty, release-time steps the
  helper might miss, upgrade blast radius, whether red #446 CI holds the release.
- Communication: overclaim risk on #448, notes precedents (Non-claims,
  delta-composition honesty), new-JSON-key naming window.
- Interface: first-contact surfaces (`--help`, advisory lines, `--summary`)
  contradicting the new behavior.
- Fix-scoped: determinism of the pinned-cpu assertion, layer correctness,
  class drain, comment framing.

## Counterweight Pass (four-bin triage)

- Act before ship | A: release notes reference `#448` with NO close keyword
  and carry an explicit Non-claims line (within-invocation parity only;
  wrapper cached-inventory hypothesis untouched; Ceal re-verification
  pending). Applied in the publish notes.
- Act before ship | C: conscious KEEP decision on `ignored_intentional` /
  `unnamed_reductions` recorded here — names parallel
  `accepted_rotations`/`accepted_families`; meaning rides on the advisory
  prose; `--summary` surfaces messages, not raw keys. Rename window
  consciously closed.
- Act before ship | F: after publish, verify the minted
  `charness-artifacts/probe/<date>-v2.4.1-release-observer.json` contains
  `distinct_channel_verification.observer` (v2.4.0's lacked it; installed
  helper has since refreshed). Checked at closeout.
- Bundle | B/D/E: delta-composition honesty line (range includes v2.4.0
  post-tag verification + handoff commits), "why patch" rationale (above),
  and the scoped-accept exit-flip call-out — all carried in the notes.
- Bundle | G: ship with the #446 root-cause fix bundled; do NOT hold for the
  next scheduled mutation run, and do NOT claim #446 resolved until a
  scheduled run on a low-core runner confirms green post-merge
  (disconfirmer-scope lesson honored).
- Over-worry (confirmed): `--help` cross-flag reference pattern (one-word
  "described under" tweak applied); `ADVISORY (intentional)` wording already
  reads as by-design; mirror sync (verified byte-identical); real-host proof
  (no adapter trigger matches).
- Valid but defer | J: missing-overlay silent exemption loss stays deferred
  (fail-closed: fewer exemptions → more refusals, never absorption).

## Boundary Ownership

Release surfaces stay owned by the release adapter/helper (bump, sync, tag,
publish, observer probe); the shipped fix's policy stayed in
`dup_ratchet_lib` with the CLI as integration seam (slice critique verdict
carried); the #446 fix corrects the test layer, not the runner, because
`min(cpu_count, cap)` is intended production behavior with
`CHARNESS_PYTEST_WORKERS` as the documented override.

- Verdict: owned-correctly

## Deliberately Not Doing

- Not renaming the two new JSON keys (decision recorded above; a
  post-release rename would be breaking).
- Not holding v2.4.1 for a green scheduled mutation run; the failure class is
  deterministic and root-cause-fixed in this release, and the workflow's
  scheduled-green auto-close remains the only #446 closure path.
- Not adding a missing-overlay advisory in this release (deferred, fail-closed).

## Next Move

Commit the bundled fixes with this artifact, then publish via the repo
helper: dry-run, `--execute --part patch --critique-artifact <this file>`,
distinct-channel verification, observer-field check (F), install refresh,
baton reconcile to 2.4.1.
