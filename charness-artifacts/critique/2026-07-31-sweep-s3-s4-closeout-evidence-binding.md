# Sweep S3 S4 closeout evidence binding

Date: 2026-07-31

## Decision Under Review

Close triage-sweep rows S3 and S4 by moving closeout evidence binding into
`check()` — the shared choke point every achieve/issue/release closeout passes
through — instead of leaving it in the two callers that happened to call the
predicate by hand; and decide what to do about S3's stub half.

## Failure Angles

- **Fixing where it is convenient.** S4's own text names three unguarded
  surfaces. A fix that wires the generic CLI and stops there closes the two
  paths that had nothing while leaving the two highest-traffic closeouts —
  the ones that actually close GitHub issues and flip goals to `complete` —
  at their pre-fix strength.
- **Answering a coarse check with another coarse check.** S3 says the verdict
  is keyed on `st_size == 0`. A byte floor is the obvious reply and is equally
  coarse in the direction that matters.
- **A floor that fails the repo's own corpus.** Any bar set above how this repo
  already writes its evidence is the bar-moving shape, and the test suite is
  where that shows up first.
- **A false refusal at a publish boundary.** Tightening token matching can
  reject the artifacts the gate exists to accept, and a correctness gate that
  refuses correct input earns a bypass.
- **A repair carrying the class it fixes.** The tightening and its own
  correction are both matcher edits on a shared predicate; either can widen
  what binds.

## Counterweight Pass

- **Real blockers, fixed before shipping:** binding at the choke point; the
  release gate binding to the version it is publishing; dotted versions
  boundary-matched; the `v?` correction scoped to versions only; the issue
  wrapper's report contradicting itself; the release gate's report reaching
  the published artifact.
- **Withdrawn rather than shipped:** both byte floors. The first guarded only
  the basename channel on an argument that was simply wrong — a reviewer
  defeated it in four bytes through the cheaper content channel. The second
  was universal and defensible, and failed 34 existing tests, which is the
  measurement saying the bar sat above the repo's own evidence.
- **Over-worry:** that scoping `v?` off by default would re-break release
  binding. It does not — versions are compound clusters and keep the prefix.
- **Accepted and recorded, not closed:** S3's stub half. A stub that cites its
  context still passes. The honest fix is per-kind artifact shape on the accept
  path, which is a contract change this policy-free generic library is the wrong
  layer to make unilaterally.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/check_prescribed_skill_executed_lib.py | action: fix | note: binding was defined but never called by check(); moved to the choke point so it no longer depends on which caller remembered
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_preflight.py | action: fix | note: release publish gate had no binding at all; now binds to the target version, closing what the contract recorded as a follow-up
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/check_prescribed_skill_executed_lib.py | action: fix | note: a dotted version fell through to substring containment, so 2.12.0 bound a critique merely mentioning a dependency at 12.12.0
- F4 | bin: act-before-ship | evidence: strong | ref: scripts/check_prescribed_skill_executed_lib.py | action: fix | note: the v-prefix repair for F3 was global and let bare issue token 2 bind the checked-in v2-1-4-release-packet.md; scoped to compound clusters
- F5 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/scripts/issue_resolution_critique.py | action: fix | note: the wrapper bound externally while its report said binding_checked false, inverting the field added to stop exactly that confusion
- F6 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_cli.py | action: fix | note: the gate report was discarded by its only caller, so a presence-only publish left no durable record; now carried into the published payload
- F7 | bin: valid-but-defer | evidence: strong | ref: scripts/check_prescribed_skill_executed_lib.py | action: document | note: S3's stub half stays OPEN; two byte floors were written and withdrawn, and the real fix is per-kind shape on the accept path
- F8 | bin: act-before-ship | evidence: moderate | ref: tests/quality_gates/test_prescribed_skill_executed.py | action: fix | note: the residual was first pinned as a passing assertion, which would make a future fix read as a regression; reshaped as a non-strict xfail
- F9 | bin: over-worry | evidence: moderate | ref: scripts/check_prescribed_skill_executed_lib.py | action: defer | note: scoping the v-prefix off by default does not re-break release binding, because versions are compound clusters

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (typed read-only Claude Code subagent).
- Requested spawn fields: subagent_type bounded-reviewer, session-model inheritance, no host addressing name.
- Host exposure state: applied
- Application state: host-confirmed: both reviewers reported seeing only Read/Grep/Glob and no Bash/Edit/Write/Agent tool.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

Two rounds. Round 1 produced F1's partial-scope finding, the four-byte
counterexample that killed the first floor, and F3. Round 2 read the repaired
surface and produced F4, F5, F6 and F8 — F4 being a false acceptance the round-1
repairs themselves introduced, confirmed against checked-in filenames.

## Reviewed Input Identity

<!-- Packet-bound critiques replace this comment with `- Packet consumed: <packet-path>` plus three bullets copied from prepare_packet.py after the reviewed packet is final: Packet path, exact Packet SHA256, and Identity SHA256. That `Packet consumed:` line is what turns the binding floor on. Leave this section comment-only when no packet was consumed. -->

## Boundary Ownership

- Producer: `scripts/check_prescribed_skill_executed_lib.py` decides whether closeout evidence is present and bound.
- Consumer: the achieve, issue, and release closeout wrappers, plus any repo vendoring the skills.
- Owning surface: the shared closeout guard, with its contract in `docs/prescribed-skill-closeout-contract.md`.
- Verdict: owned-correctly

## Non-Claims

- **S3 is PARTIAL, not closed.** The stale-unrelated-artifact half is closed by
  binding; the stub half is open and pinned as an xfail. No claim that a byte
  count would have closed it.
- A pre-existing hole was found and NOT fixed: a bare issue token binds an
  interior version segment, so token `1` binds the checked-in
  `v1-0-1-retired-hook-ledger-packet.md`. Verified present at HEAD before this
  slice, so it is not a regression from it — and it is not repaired here.
- The generic CLI's `--context-token` is opt-in and no in-repo caller passes it.
  The CLI path is closable, not closed.
- Round 2 raised residuals left unaddressed: a CalVer release version would
  boundary-match any artifact's `Date:` header; a two-component version like
  `1.2` binds prose; a pre-release version such as `2.12.0-rc.1` contains
  letters and so degrades to substring containment. None affect this repo's
  current versioning; all three affect consuming repos.
- No claim that `_gate_target_version`'s broad `except Exception` was narrowed.
- The reviewer boundary fingerprint was snapshotted at `7ae5bd04` before the
  reviews; no path was declared to it, so a `verify` will report parent-authored
  drift. Both reviewers were read-only by their own report.
