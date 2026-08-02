# Closeout Claims Review — close-the-unreachable-file-class-and-widen-the-claims-round

Date: 2026-08-03
Goal: [charness-artifacts/goals/2026-08-04-close-the-unreachable-file-class-and-widen-the-claims-round.md](../goals/2026-08-04-close-the-unreachable-file-class-and-widen-the-claims-round.md)
Reviewer: bounded read-only fresh-eye subagent (`bounded-reviewer`), delegated.
Fresh-eye satisfaction: parent-delegated — this claims round ran in a separate
bounded `bounded-reviewer` context that had not seen the work being reviewed,
and it is the THIRD delegated context on this goal (two code rounds preceded it).
Boundary: `reviewer_boundary_fingerprint.py` snapshot before / verify immediately
on return — `ok: true, verdict: clean, drift: []`.

## Why This Round Exists

A claims reviewer reads the RECORD, not the code. Two code rounds had already
run on this work and their findings were fixed. This round asks a different
question: **does what the record CLAIMS match what the tree shows?** On its first
outing (2026-08-02) this class found five record blockers that four code rounds
had missed. It found three more here, one of them in the goal's own headline
artifact.

## Findings And Dispositions

| # | Finding | Disposition |
| --- | --- | --- |
| 1 | **BLOCKER.** The sweep artifact's arming table still read `A2 — NOT ARMED YET … 6 source + 6 mirror, all live` after slice C armed the rule and repaired all 12 sites. The A1 row had been updated; A2 was left behind. | **FIXED.** Row now reads ARMED / 0 remaining. The bitter part: that table was ADDED in response to round 1 catching the opposite overclaim, and then went stale in the other direction. |
| 2 | **BLOCKER.** `Disposition review:` bound a path that did not exist — a claim written ahead of its evidence. | **FIXED** by writing this file, which is that path. |
| 3 | **BLOCKER.** `Host log probe:` bound the retro, which carries no host-log data — one artifact standing in for two independent evidence channels. Noted as an inherited habit from the preceding goal, not a one-off. | **FIXED.** Now binds a real `probe_host_logs.py` JSON persisted beside the goal artifact. |
| 4 | Round 1's finding count was given as "6 lower findings" in the Slice Log and "five lower findings" in Final Verification. | **FIXED.** Six is correct; Final Verification corrected and the discrepancy noted inline. |
| 5 | A4 was 30 in the audit and 29 in the goal and retro, with no ruler note — in a goal whose thesis is "state the ruler beside every count". | **FIXED, and it was a real difference, not a typo.** `skills/support/README.md:26` was an A1 instance AND an A4 candidate; slice B's A1 repair removed it from A4. Now stated in the audit. |
| 6 | The `## User Acceptance` bar says "five live sites prove it fires"; the run found six. | **FIXED by annotation, not by rewriting the bar.** The bullet now records that five was #479's line-anchored count and six is the widened ruler's, and that the criterion is over-met. Silently editing a bar to match the result is the failure this goal is about. |
| 7 | "14 tests" vs 16 `def test_` functions — stale after two tests were added post-review. | **FIXED** with the reason for the difference. |
| 8 | No commit SHA anywhere in the record; all four `Commits:` fields empty. | **FIXED at commit time** — the closeout commit SHA is recorded in the frame after the commit exists. Deliberately not pre-filled, which is finding 2's shape. |
| 9 | Ship-state fields still reading pre-flip (`Status: active`, slice F `pending`, Auto-Retro `TODO`, empty `## Plan Critique Findings`, empty `## User Verification Instructions`) — and `## Off-Goal Findings` EMPTY while the Slice Log records #480 being filed. | **FIXED.** The off-goal section was the substantive member: a reader navigating to the section named for off-goal findings found nothing and would conclude there were none. |
| 10 | The pre-activation cut order names B as highest-value while Interview Decision 1 chose A (the ruler) as load-bearing, and omits A entirely. | **NOT FIXED — left as history.** It is a pre-activation line written before A was split out; everything shipped, so nothing was mis-sequenced. Rewriting it would erase the evidence that the slice plan changed shape. |
| 11 | A duplicated half-sentence in the `## Coordination Cues` template text, at the spot explaining what the floor requires. | **FIXED.** |

## Verified Clean By This Reviewer

Recorded because a claims review that only lists defects gives no signal about
what was actually checked:

- **Slice E's inherited claim holds.** The goal asserts the claims round was
  widened to release before activation; both named surfaces carry it —
  `skills/public/release/references/critique-boundary.md` *Claims Review* and
  `docs/conventions/operating-contract.md`'s surface list. The goal correctly
  does NOT claim the trigger has ever fired.
- **A1's arming claim verified on every surface it names**: `run-quality.sh`,
  the commit-time plan, `quality-core.yml`, plus the mirror of each.
- **Both cited A1 repairs are real in the mirror**, including the kind-flattening
  one that a relative link cannot express and was rewritten as prose.
- **The A2 sentence-scoping story is checkable in the tree** — `spill-targets.md`
  reads exactly as the record describes, and paragraph scoping really would have
  glued two independent bullets into a fabricated contradiction.
- **The non-claim appears in three places, one of them executable** — the gate
  counts and prints what it skipped on both the pass and the refusal path.
- **The retro is not softened relative to the Slice Log.** The reviewer looked
  specifically for the self-flattering drift the last outing found, and reported
  the drift here running the other way: the audit lagged behind the good news
  rather than the record running ahead of it.

## Non-Claims Of This Review

- The reviewer's envelope had no shell, so figures needing a command (510 files,
  236/46%, 873 links, 2802 docs, 4591 tests, ~0.17s) were listed as evidence
  requests rather than verified. The parent had run each of those commands and
  their outputs are the record's basis, but **this reviewer did not independently
  re-run them** — so on those specific figures the second-observer requirement is
  not met, and the record rests on a single channel.
- This review reads the record. It does not re-review the gate logic; two earlier
  rounds did that, and their findings are recorded separately.

## Reviewer Tier Evidence

- Requested tier: n/a — this is a Claude Code host. Per `AGENTS.md` `## Subagent Delegation`, the per-host split says to use the host's own subagent controls here (typed `bounded-reviewer` with session-model inheritance) and NOT to request the Codex model/effort pair; its omission is contract-conformant rather than a degradation.
- Requested spawn fields: `subagent_type: bounded-reviewer` (read-only: Read/Grep/Glob), no host addressing/team `name` (per the #458 spawn-shape rule), `run_in_background: false` so the findings return to the parent rather than as an idle notification.
- Host exposure state: applied
- Application state: host-confirmed: the spawn returned a full findings report inline, and the envelope bound held — the reviewer reported having only Read/Grep/Glob and listed the shell-dependent figures it could not verify instead of asserting them.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — the claims round ran in a separate bounded `bounded-reviewer`
context that had not seen the work, and it is the THIRD delegated context on this
goal. `reviewer_boundary_fingerprint.py` snapshot/verify around it returned
`ok: true, verdict: clean, drift: []`.

## Boundary Ownership

- Producer: this goal's run — it produced the counts, the arming claims, and the
  evidence bindings that the record asserts.
- Consumer: a reader outside this session — a future enumeration of the same
  class starting from this sweep, and an operator deciding whether #479 can close.
- Owning surface: the goal artifact and its measurement artifact
  (`charness-artifacts/goals/`, `charness-artifacts/audit/`); the standing
  claims-round contract itself is owned by `docs/conventions/operating-contract.md`
  *Critique Discipline* and `skills/public/release/references/critique-boundary.md`.
- Verdict: single-surface

## Decision Under Review

Whether this goal's closeout record can ship as written — that is, whether every
count, arming claim, evidence binding, and status field matches what the tree
actually shows.

## Failure Angles

- A status table added to correct an overclaim goes stale in the OTHER direction
  once the work it tracks lands (this is what happened, finding 1).
- An evidence line is written before the artifact it cites exists (finding 2).
- One artifact is cited for two independent evidence channels (finding 3).
- A figure appears with two values in two sections and no ruler note, in a goal
  whose whole thesis is stating the ruler (findings 4, 5, 7).
- An acceptance bar is quietly rewritten to match the result rather than
  annotated as superseded (finding 6).
- A section named for a class of finding is empty while a slice log records one
  (finding 9).

## Counterweight Pass

Real blockers: findings 1, 2, 3 — each teaches a reader outside this session
something false about what shipped. Finding 1 is the most damaging because it
lives in the artifact the goal exists to produce.

Unreconciled-but-not-false: findings 4, 5, 6, 7 — each is a number or a bar that
is defensible once explained, and the defect is that the explanation was missing,
not that the figure was wrong. Fixed by annotation rather than by changing values.

Over-worry, not folded: finding 10 (the pre-activation cut order naming B rather
than A as load-bearing). Everything shipped, nothing was mis-sequenced, and
rewriting it would erase the evidence that the slice plan changed shape during
planning. Left as history, deliberately.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/audit/2026-08-04-unreachable-file-denominator-sweep.md | action: fix | note: arming table said A2 NOT ARMED after slice C armed it and repaired all 12 sites
- F2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/goals/2026-08-04-close-the-unreachable-file-class-and-widen-the-claims-round.md | action: fix | note: `Disposition review:` bound a path that did not exist — a claim written ahead of its evidence
- F3 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/goals/2026-08-04-close-the-unreachable-file-class-and-widen-the-claims-round.md | action: fix | note: `Host log probe:` bound the retro, which carries no host-log data — one artifact for two evidence channels
- F4 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/goals/2026-08-04-close-the-unreachable-file-class-and-widen-the-claims-round.md | action: fix | note: round 1 finding count given as six in the Slice Log and five in Final Verification
- F5 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/audit/2026-08-04-unreachable-file-denominator-sweep.md | action: fix | note: A4 is 30 in the audit and 29 in the goal/retro with no ruler note; the difference is real (slice B's A1 repair removed one) and is now stated
- F6 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/goals/2026-08-04-close-the-unreachable-file-class-and-widen-the-claims-round.md | action: document | note: acceptance bar says five live sites, run found six; annotated as superseded rather than silently rewritten
- F7 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_check_plugin_doc_links.py | action: fix | note: record said 14 tests, file has 16 after two were added post-review
- F8 | bin: bundle-anyway | evidence: moderate | ref: charness-artifacts/goals/2026-08-04-close-the-unreachable-file-class-and-widen-the-claims-round.md | action: fix | note: no commit SHA anywhere in the record; filled at commit time rather than pre-filled
- F9 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/goals/2026-08-04-close-the-unreachable-file-class-and-widen-the-claims-round.md | action: fix | note: `## Off-Goal Findings` empty while the Slice Log records #480 being filed
- F10 | bin: over-worry | evidence: moderate | ref: charness-artifacts/goals/2026-08-04-close-the-unreachable-file-class-and-widen-the-claims-round.md | action: defer | note: pre-activation cut order names B not A as load-bearing; left as history, nothing was mis-sequenced | follow-up: deferred — no handoff anchor needed, it is a closed planning artifact
- F11 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/goals/2026-08-04-close-the-unreachable-file-class-and-widen-the-claims-round.md | action: fix | note: duplicated half-sentence in the Coordination Cues template text
