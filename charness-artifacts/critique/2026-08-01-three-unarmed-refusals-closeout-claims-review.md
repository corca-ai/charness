# Closeout-claims review — three-unarmed-refusals goal (D46/D47/D48)

Date: 2026-08-01
Goal: [get-the-operator-call-on-the-three-unarmed-refusals-d46-adap](../goals/2026-08-01-get-the-operator-call-on-the-three-unarmed-refusals-d46-adap.md)
Scope: the goal's CLOSEOUT CLAIMS, not the correctness of the code six earlier
rounds already reviewed.

## Why this review exists

[The north star](../../docs/design-north-star.md) P4 puts *authoring or changing a
proof surface* inside the irreversible set, and this goal changed several. Its
closeout was written by the same agent that did the work, and its
`Disposition review:` line pointed at that agent's own retro — one channel printed
twice, which is the exact terminal-trust shape the north star's diagnosis names.
This review is the distinct observer that line was supposed to carry.

## Reviewer Tier Evidence

- Requested tier: bounded read-only reviewer (`bounded-reviewer` typed agent)
- Requested spawn fields: agent_type=bounded-reviewer, unnamed spawn, session-model
  inheritance. Per the repo's per-host subagent split this is a Claude Code host, so
  the Codex `gpt-5.6-terra` / `fork_turns` request does not apply and its absence is
  contract-conformant rather than a degradation.
- Host exposure state: requested_fields_sent
- Application state: the spawn was accepted with the requested agent type and
  returned its findings inline.
- Delivery state: findings-received

## Reviewer Provenance

Fresh-eye satisfaction: parent-delegated. One bounded read-only `bounded-reviewer`
subagent, spawned unnamed in the shared parent worktree with Read/Grep/Glob only.
It reported its envelope as bound and performed no worktree or index mutation.
Boundary window `w-20260801T110813Z-1798113`.

## Findings, and what changed

All four blockers and four of the minors were parent-verified before folding; the
verification commands are named so a third reader need not take either of us on
trust.

- **BLOCKER — "five bounded review rounds" was six.** The record's own per-slice
  fields enumerate six, and the retro's parenthetical sums to six inside a sentence
  saying five. Folded: the count is corrected in the goal, the retro, and every
  derived line, and all eight windows (six in-goal plus two after) are now named.
- **BLOCKER — "no new test file" was false, twice.** Verified with
  `git show 8c3b3446:<path>`: both `tests/test_handoff_chunker_adapter_report.py`
  (slice 1, forced out by the 840/800 length cap) and
  `tests/test_inventory_measurement_lib.py` (closeout) are new and neither appeared
  in its slice's change record. Folded into both slices' test-pressure lines — the
  one metric the closeout grades itself on was understated by two modules.
- **BLOCKER — the dup-ratchet win-rate was a helper count wearing a firing count.**
  "Fired FOUR times, each firing produced a real extraction" is false: slice 2's
  firing produced two classifications and a rotation, no extraction. Verified with
  `git diff 8c3b3446..HEAD -- charness-artifacts/quality/dup-review.json` (7 ids
  added, not 5). Folded, and the corrected claim is three firings / four helpers /
  seven overlay entries. This one mattered most: it was the headline lesson carried
  into the handoff and the retro trend line.
- **BLOCKER — `Retro:` and `Disposition review:` were the same self-authored file.**
  Stated plainly by the reviewer: *"this is not a second observer."* Folded by
  writing this artifact and repointing the line at it.
- **MINOR — the non-claims block omitted the session's only external write.** Issue
  #468 was created. Folded into the block, with the honest note that its readback
  used the same tool and observer as the write and is therefore a same-proxy
  re-read by this repo's own standard.
- **MINOR — Non-Goals still recorded the two WITHDRAWN repairs as the operator's
  call**, which would have authorized a later session to retry exactly what this
  run proved unbuildable. Folded.
- **MINOR — the bundle evidence is a RED run** (82 passed / 1 failed) with no green
  full-bundle run recorded, and the User Verification steps did not warn the reader.
  Folded as a new step 4.
- **MINOR — `Host log probe: skipped: host-log-not-exposed` used the wrong reason
  code**: the session log WAS exposed and read; only the per-goal scope was
  missing. Folded, with the enum limitation stated.

## What the reviewer found CLEAN, and it is worth recording

- **The D47 measurement figures are exact and unusually well-pinned** — the goal,
  the probe, and D47 agree digit for digit, the internal arithmetic checks
  (114+47=161, 169−161=8), the corpus denominator reproduces on today's tree, and
  the units discipline is honest: it states the executed answer on the hand count's
  own unit is 4, not 5.
- **The User Verification snippet works as written**, read character by character
  against the real adapter file.
- **No self-serving framing**, checked hard: reverted work is labelled reverted in
  the first person, round 2's harshest finding is stated against the author, the
  wrong first executed number is preserved in the probe with its bias, and every
  reviewer finding is attributed to the round that found it. The three exceptions
  are the blockers above.

## Boundary Ownership

- Verdict: owned-correctly

The defects are claims in a goal artifact, and the goal artifact is where they were
repaired — the producer of a claim owns it. Two findings could have been pushed onto
other surfaces and deliberately were not: the fingerprint helper's overwriting
default `--out` is a real weakness, but the fix belongs to whoever changes that
helper's contract, not to this closeout, so it is recorded as a residual rather than
patched here; and the ~12 uncheckable figures are an argument for the goal-artifact
schema to carry command output, which is a contract change with its own slice and
its own owner. Nothing here was escalated to an issue: #468 already exists for the
adjacent pattern, and inventing a second issue for "a closeout needs a distinct
observer" would duplicate a rule the north star already owns (P4).

## Residual, not closed

- **~12 figures in `## Final Verification` have no recorded command output** — test
  counts, gate timings, per-round finding counts. Not alleged wrong; alleged
  uncheckable without re-running the suites. The D47 numbers show the right pattern
  (recorded probe plus a pinning test); the test and gate counts do not, and making
  them so is not this closeout's job to invent.
- **Every fingerprint snapshot used the helper's default `--out`**, so each
  overwrote the last and only the final window survives on disk. A boundary-integrity
  record that does not persist is weaker evidence than the check itself.
- **`Commits:` and `Metrics:` are empty in every slice**, so no slice can be tied to
  the commit that closed it from the record alone.
