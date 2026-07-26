# retro honesty and xdist oversubscription
Date: 2026-07-26
Fresh-eye satisfaction: parent-delegated

## Decision Under Review

Two improvements this session found but had only recorded, now built:

**A — the retro trigger declared completion.** The release helper emitted its
auto-retro with `Mode: session` and a `## Next Improvements` line reading "no
additional follow-up is needed for this trigger instance".
`refresh_recent_lessons.py` promotes that line verbatim into the NEXT session's
opening `## Next-Time Checklist`. So a bounded release-delta detector — which
cannot see the session at all — told the next operator that nothing was owed.
P5 forbids exactly this: a gate may force a question, it may not declare
completion. Observed live: this session's own waste went unrecorded until the
operator asked, with that line in `recent-lessons.md` at session open.

Underneath it, a scoring bug: the lesson index's recurrence boost ran off
`source_count`, so 121 emissions of one template scored as 121 independent
recurrences — boosted *because* it was boilerplate.

**B — `pytest` was oversubscribing its own workers.** `choose_xdist_workers`
used `os.cpu_count()`, the same wrong question this session's headline bug was
about, in a second caller. Under a 4-CPU limit it spawned 16 xdist workers onto
4 usable CPUs.

Both violations were reproduced first: a unit test on the generated markdown
failed on `Mode: session`, and the worker width was **measured** at 94.2s (16
workers) vs 64.1s (4 workers) on the same 4 cores — 32% of wall and ~76s of CPU.

## Failure Angles

One bounded read-only reviewer across both parts: signature classification and
false-positive paths, the independent-count arithmetic, whether rewriting
historical artifacts is honest, whether the duplication justification is
rationalization, worker-width bounds, import-cycle risk, and what should not ship.

Parent-side worktree+index integrity fingerprinted around the review
(`reviewer_boundary_fingerprint.py` snapshot/verify): `{"ok": true, "drift": []}`,
verified before any fix was applied.

## What The Review Changed

**The fix did not work, and the shipped digest proved it.** Collapsing the
recurrence *multiplier* was not enough: every same-day candidate ties at
`selection_weight` 1.0, so ordering fell entirely through to the next sort key —
which was the raw `source_count`. 120 versus 1 put the boilerplate back at rank 1.
The reviewer found the casualty by name: the hand-authored "run the owning
`scaffold_*.py` first" lesson was pushed to 5th of 4 slots and vanished from the
digest. **The fix had moved the displacement from the multiplier to the
tiebreaker**, and the artifact I was about to commit contradicted its own commit
message. Now: tie-break on `independent_source_count`, then prefer a
human-authored candidate over a generator-authored one at equal weight — a scarce
opening-context slot goes to the observation that happened once, not the template
that restates itself every release.

**The 119-file rewrite was reverted entirely, and that is the bigger correction.**
Not finding the tiebreaker, I had "fixed" the ranking by rewriting the boilerplate
line in 119 historical generated artifacts. The reviewer showed the resting state
was indefensible: the rewrite corrected the symptom line while leaving `Mode:
session` — the primary falsehood the change itself identifies — intact on all 120,
producing artifacts that simultaneously claim to be session retros and carry a
line saying they cover only the release delta. Backdated correction with no
amendment marker, on dated records. With the tiebreaker fixed at the real cause,
the rewrite is unnecessary: history is untouched, and the digest is now entirely
hand-authored lessons. Treating the symptom was the error; the reviewer caught
both the symptom-treatment and its collateral.

**A one-quoted-line mute.** `generated_retro_signature` matched with `re.MULTILINE`
over the whole body. Both signatures are header fields, so the next session retro
documenting this very mechanism — quoting the generated title in a fenced block —
would be classified as a template emission. Every one of its lessons would merge
into the generator bucket and contribute zero independent observations. Now scans
the header only, with a test that quotes the header inside the body and asserts
the retro still counts.

**A comment asserting the opposite of its own code.** `run_standing_pytest.py`
said it "consumes that helper rather than repeating the affinity logic" while the
docstring 100 lines above explained why it deliberately does *not*. That is
verbatim the trap this session added to the handoff — cite a precedent, don't
recheck it — committed inside the change that added the warning.

**The dup-review entry claimed a binding it did not have.** It cited
`test_recorder_does_not_define_a_second_profile_derivation`, which constrains a
different module and says nothing about the runner. The precedent it follows
(`89d83f450e19e19b`) is accepted *because* a test binds its copies. Worse, the
runner's `OSError` arm was untested — a bug this repo shipped in v2.10.0, fixed in
v2.11.0, and re-introduced here as a second unguarded copy. Added a parity test
asserting both readers agree under the same patched affinity, both survive a
refusing `sched_getaffinity`, and neither can yield a zero worker width; the
dup-review note now cites it.

**A fallback pointing the wrong way.** `usable_cpu_count() or DEFAULT_XDIST_WORKER_CAP`
is unreachable (both branches end in `or 1`), and had it ever fired it would have
meant "cannot determine CPUs, therefore assume the maximum" — reinstating the exact
oversubscription being removed, from the branch meant to be safe. Removed.

## Counterweight Pass

- **Is the affinity duplication a dodge of the dup gate?** No, and the reviewer
  agreed on three grounds: the two call sites answer different questions (profile
  *identity contract* vs local *process width*), the alternative was tried and
  measurably broke a coverage-instrumented child with `ModuleNotFoundError`, and
  the shared surface is a 3-line stdlib call rather than a policy. What was
  missing was the binding, not the reasoning; that is now supplied.
- **`independent_source_count` under mixed sources.** Traced and correct: 121
  generator emissions plus 3 human retros yields 4, not 124 and not 3 — the
  template *did* say the thing once, so it counts as one peer.
- **Worker-width bounds.** Zero, negative, and absurd inputs all checked: the
  floor is 1, the cap is unchanged at 16, and macOS/Windows behavior is
  byte-identical to before (no `sched_getaffinity`, so `AttributeError` →
  `os.cpu_count()`).
- **Import cycle from `run_evals`.** None structurally possible; the runner
  imports only stdlib and guards execution behind `__main__`.
- The remaining `## Repeat Traps` slot held by generator boilerplate is correct
  behavior, not a residue: it is the most recent repeat trap and no equally recent
  human one exists, so it wins on recency honestly rather than on manufactured
  recurrence.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/recent_lessons_lib.py:296 | action: fix | note: tiebreaker on raw source_count undid the multiplier fix; boilerplate still ranked 1 and displaced a hand-authored lesson out of the shipped digest
- F2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/retro/ (119 files) | action: fix | note: partial backfill left artifacts claiming Mode: session AND "covers the release delta only"; reverted the whole rewrite once the real cause was fixed
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/recent_lessons_lib.py generated_retro_signature | action: fix | note: MULTILINE body match would classify a retro that QUOTES the generated header, muting every lesson in it
- F4 | bin: act-before-ship | evidence: strong | ref: scripts/run_standing_pytest.py choose_xdist_workers | action: fix | note: comment claimed it consumes the skill helper; the code deliberately does not, contradicting its own docstring
- F5 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/quality/dup-review.json 86638e4edc955d3f | action: fix | note: cited a binding test that constrains a different module; the runner's OSError arm was untested after being a shipped v2.10.0 bug
- F6 | bin: act-before-ship | evidence: moderate | ref: scripts/run_standing_pytest.py | action: fix | note: unreachable `or DEFAULT_XDIST_WORKER_CAP` fallback would have restored max-width oversubscription if it ever fired
- F7 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_standing_pytest_runner.py | action: fix | note: three pre-existing tests patched cpu_count only and failed under taskset; they now pin affinity too
- F8 | bin: over-worry | evidence: moderate | ref: charness-artifacts/retro/ amendment markers | action: defer | note: moot once the rewrite was reverted; would have been required had the backfill been completed instead
- F9 | bin: valid-but-defer | evidence: moderate | ref: scripts/recent_lessons_lib.py title signature | action: defer | follow-up: deferred docs/handoff.md `## Next Session` item 4 | note: if the generated title is reworded, detection silently reverts to counting every emission; an invariant test over `*-release-auto-retro.md` would catch it

## Reviewer Tier Evidence

- Requested tier: `bounded-reviewer` typed read-only subagent, both parts in one scope.
- Requested spawn fields: `subagent_type: bounded-reviewer`, north-star-anchored prompt, session-model inheritance (Claude-host branch of the per-host subagent contract).
- Host exposure state: applied
- Application state: host-confirmed: the reviewer reported `envelope-unbound` with only Read/Grep/Glob visible, made no writes, and named the one evidence channel it could not reach (`git show` of pre-rewrite artifact bodies).
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated`. One bounded read-only reviewer in the shared parent worktree;
`reviewer_boundary_fingerprint.py` snapshot/verify returned
`{"ok": true, "drift": []}`, run on reviewer return before any fix was applied.

## Reviewed Input Identity

<!-- No prepared packet: the reviewer was pointed at the uncommitted worktree with both parts' changed surfaces enumerated, plus docs/design-north-star.md as the governing standard. -->

## Boundary Ownership

- Producer: two generators — the release helper, which emits an auto-retro per publish, and the lesson index, which scores retro bullets into a digest.
- Consumer: the next session, which reads `recent-lessons.md` as opening context and routes from it.
- Owning surface: the retro skill's lesson-selection surface (`scripts/recent_lessons_lib.py`) for scoring, and the release skill's trigger closeout (`publish_release_retro.py`) for what a bounded record may claim.
- Verdict: owned-correctly

## Non-Claims

- **The 32% speedup is measured on one machine and one suite shape** (this repo,
  4 cores via `taskset`, 5363 tests). It is not a general claim about xdist.
- **No speed work was done beyond worker width.** `pytest` is still ~51s of a
  ~54s read-only run on the unrestricted box, where the width was already correct;
  this fix changes nothing there. The profiling item stays open.
- **The title-signature dependency is unguarded.** If the generated title is
  reworded, classification silently reverts to counting every emission (F9).
- **Neither part has been through a mutation run.**

## Next Move

Commit with the slice. F9 is the named residual; the speed item remains open for
the unrestricted path, where the wall is pytest itself rather than its worker count.
