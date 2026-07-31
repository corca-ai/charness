# Decline D44 blocking-targets subprocess coverage

Date: 2026-08-01

## Decision Under Review

Dispositioning the three-times-carried capability request
`blocking-targets-subprocess-coverage` as **DECLINED** ([D44](../../docs/deferred-decisions.md)),
plus a text-only repair of the changed-line gate's `blocking_detail` string, which
still asserted the cause the 2026-07-30 measurement narrowed.

## Failure Angles

- **The premise is not actually falsified, and I am declining a real capability.**
  Checked against the measurement lineage rather than the summary: the
  [#465 critique](./2026-07-30-issue-465-resolution.md) records the confounded
  first measurement being retracted and replaced with a purpose-built control, and
  the surviving conclusion is that an inherited-env in-repo spawn IS attributed.
- **The residue is claimed shipped but is not wired.** Executed rather than read:
  `subprocess_coverage_advisory_report` fires today on a blocked file, keyed on the
  union of `blocking_targets` and `blocking`, carrying `blocked_lines`.
- **The decline drops something the ask wanted.** It did — see F2; the origin form
  named a different surface and asked for REMEDY information, which no ground
  falsifies.
- **The repaired string introduces its own inaccuracy**, or points at a payload key
  that is absent exactly when read.
- **Declining leaves a silent proof surface.** North-star check: the literal ask
  would have printed doubt onto TRUE blocks; the decline removes a falsified cause
  and adds no green. The advisory never suppresses a blocker.

## Counterweight Pass

- **Real blocker:** the retro this decision cites as its correction carrier still
  printed the retracted `143 lines` figure. Same class as the repair being shipped,
  one file over, in the file D44 points a future reader at. Fixed in place with a
  dated amendment rather than dodged by re-citing a different source.
- **Real, and the most valuable finding:** the origin form of the ask (remedy-side
  candidate-test NAMES) survives all three decline grounds. Recorded as an explicit
  open residual in D44 rather than landed, because surfacing it changes an advisory
  payload on a blocking gate and would owe its own review rounds — smuggling that
  into a decision slice is the move D42/D43 refuse.
- **Over-worry, correctly:** demanding a second bounded round. Nothing here changes
  verdict logic — `blocking`, `blocking_targets`, and every exit code are identical;
  only a human-facing string moved, and the one test pin asserts `"not tracked"`,
  which still holds. Grep confirms no surface keys on the removed wording.
- **Over-worry, correctly:** turning `blocking_detail` into a dict to carry the
  changed line numbers it already computes. A payload-shape change inside a decline
  slice is the same smuggling move; recorded as a note for the next toucher.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/retro/2026-07-30-session-retro.md:49 | action: fix | note: the retracted, confounded "143 lines" figure was still live in the very entry D44 cites as its ground-1 correction carrier; amended in place with the retraction lineage
- F2 | bin: act-before-ship | evidence: strong | ref: docs/deferred-decisions.md | action: document | note: the ask's ORIGIN form (per-blocked-file candidate-test NAMES as remedy info, on suggest_mutation_coverage_command.py) survives all three decline grounds and was silently dropped; now recorded as an explicit STILL-OPEN residual with its own reopen clause
- F3 | bin: act-before-ship | evidence: moderate | ref: docs/deferred-decisions.md | action: fix | note: "verified by execution" under-disclosed that the input was a synthetic blocking_targets, not a live BLOCK, and the demo test is also in-process-covered at nine sites; both now disclosed
- F4 | bin: act-before-ship | evidence: moderate | ref: scripts/check_changed_line_mutation_coverage.py | action: fix | note: the repaired string pointed only at subprocess_coverage_advisory, which is `{}` in the ordinary case; now also names the _scope sibling that speaks when the advisory is empty
- F5 | bin: valid-but-defer | evidence: moderate | ref: scripts/subprocess_only_coverage_advisory.py | action: document | note: a path reaching the advisory via `blocking` alone gets blocked_lines: [] although _blocking_report computed those numbers; and the two single-key entrypoints take no `blocking` arg, so a future caller silently reverts to targets-only keying — recorded in D44 for the next toucher
- F6 | bin: over-worry | evidence: strong | ref: docs/conventions/operating-contract.md | action: defer | note: a second bounded round was considered and is not owed — no verdict logic, exit code, or pinned assertion changed; comment/docstring/message-string only

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (Claude Code typed read-only agent, session-model inheritance per the per-host split)
- Requested spawn fields: subagent_type=bounded-reviewer, unnamed one-shot spawn, run_in_background=false
- Host exposure state: applied
- Application state: host-confirmed: agentId a03d7639252b949a7 returned findings inline; reviewer self-reported tools Read/Grep/Glob only
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated`. One round, bounded read-only reviewer, findings returned inline
and folded above. Boundary proven independently of reviewer self-report:
`reviewer_boundary_fingerprint.py` snapshot before the spawn and `verify` after
returned `{"ok": true, "verdict": "clean", "drift": []}` on window
`w-20260731T181737Z-300545`.

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed; the reviewer was given an inline scope listing the changed files, the decision's three grounds, and five adversarial questions. -->

## Boundary Ownership

- Producer: `scripts/check_changed_line_mutation_coverage.py` `_blocking_report` (the `blocking_detail` reason string) and `scripts/subprocess_only_coverage_advisory.py` (the advisory payload it now points at).
- Consumer: the agent or operator reading a changed-line BLOCK and deciding whether to doubt it, plus `changed_line_run_trust.py` narration.
- Owning surface: the changed-line mutation-coverage gate; the decision record itself is owned by `docs/deferred-decisions.md`, the repo's declared closure surface for deferrals.
- Verdict: owned-correctly

## Non-Claims

- No live gate BLOCK was reproduced; the advisory firing was executed on a synthetic
  `blocking_targets` input. The one full gate run over the committed range
  (`--base-sha cb35991e --reuse-coverage`) returned `ok: true`, and re-running it
  with `--require-fresh-coverage` showed that green was built on STALE coverage
  (`coverage_not_verified: true`) — so it is not cited as proof of anything.
- No new coverage-attribution measurement was taken; the 2026-07-30 control is cited.
- Declining does not claim every BLOCK is a genuinely untested line, and does not
  upgrade the advisory, which stays file-granular and non-exhaustive.
