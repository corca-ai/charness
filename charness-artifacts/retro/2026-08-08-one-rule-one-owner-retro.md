# Retro: One rule, one owner; one check, its own voice

Goal: charness-artifacts/goals/2026-08-08-one-rule-one-owner-one-check-its-own-voice.md

## What Happened

Five of eleven planned slice rows were built and closed, each with two delegated
fresh-eye rounds, and the goal closes EARLY at slice 5 rather than pushing six
more rows through. Its five claimed issues are `CLOSED` and verified through the
adapter: `#552`, `#548`, `#555`, `#537`, and — by its successor, which is what
retires this artifact — `#536`.

- **Slice 1 (`#552`)** — a checker required a literal token its own renderer
  never emitted, so `charness_managed` was permanently False and two AGENTS.md
  policy checks could never fire. Signal 6 was rewritten to read the CLAIM rather
  than the token. The writer sweep found FOUR writers, not one.
- **Slice 2 (`#548`)** — `write_artifact_path` meant opposite things in two
  scaffolds. Six implementations of the pointer rule existed; the repair states
  the FACT (`write_artifact_effect`) and leaves the policy to each skill.
- **Slice 3 (`#555`)** — one owner for tracker backend resolution, with BOTH
  refusal contracts kept: `issue` raises, `handoff` returns UNKNOWN, and
  collapsing them would have crashed a staleness reader.
- **Slice 4 (`#537`)** — a correct bundle-preflight refusal reported itself: five
  red tests for one finding became two, each naming the blocker.
- **Slice 5 (`#536`)** — a drift failure that names its cause, its remedy branch,
  and every surface a re-record must touch. Its closeout ran in the successor
  goal and added two more rounds and seven more blockers.

Six issues were filed while working, none planned: `#556`-`#561`. Every one came
from a delegated review or a gate rather than from reading the backlog.

## What Created Waste

- **Asserting where a fact lives instead of opening the file — five times, across
  four rounds, on one message.** Slice 5's cost is the clearest measurement in
  this goal. Version 1 said "copy each payload into the probe file" and would have
  deleted `_provenance`. Version 2 sent the reader to diff the measure scripts
  when three of four thresholds live in the gate module. The closeout's round 1
  found two more surfaces the list omitted; its round 2 found a claim
  (`transcribes no figures at all`) whose refuting evidence I had PRINTED in the
  same session, two steps earlier. The message was twice worse than the bare
  number it replaced before it was better.
- **Repairing before verifying the reviewer boundary.** Inherited from the
  predecessor and repeated on all three of this goal's slices; each window then
  needed after-the-fact reconciliation, which is strictly weaker. Fixed only at
  the `#536` closeout, where both windows were verified the moment the reviewer
  returned.
- **The broad suite run ~13 times at ~12 minutes.** The single largest time cost
  of the run. `./scripts/run-quality.sh --read-only` finishes in ~110s and already
  runs a pytest phase; the broad suite belongs at the commit boundary, once.
- **A guard's POPULATION wrong three times in one slice.** Slice 2's producer
  check was a hand list, then a literal-only glob, then literal-or-delegation, and
  a different reviewer found each. Slice 3 repeated the shape: the guard anchored
  on the CHEAPEST half of the rule, and a live fifth instance passed.

## Decisions That Mattered

- **The premise check as a PHASE, not a step.** Six for six at changing the
  build, and once at changing the SLICE: it refused the plan's own bundling of
  `#536`/`#549`/`#542` on the grounds that they share a FACE and not a REMEDY,
  and re-homed two as new rows. It also corrected `#536`'s own reproduction
  recipe — the issue's steps did not reproduce the issue.
- **Consolidate the MECHANICAL part, leave the POLICY to each caller.** Reached
  independently in slices 2 and 3, from opposite directions. Both issues proposed
  "have A use B instead of reimplementing it", and in both cases A and B REFUSED
  differently — which is usually why the copy was made.
- **Round 2 reads the REPAIRS.** Now 9 for 9 across this goal family. The first
  measured instance where round 2 found a blocker in the REPAIR rather than a gap
  in the original was slice 1; by `#536`'s closeout, BOTH rounds landed entirely
  on repairs and none of the seven findings was mutation-findable.
- **Declining the 913-site sweep in slice 4.** `assert rc == 0, result.stderr` is
  correct wherever failures go to stderr and vacuous only for stdout-reporting
  scripts; a bounded round found the right stream chosen in all 14 of that shape.
  A sweep would have been the wolf-crier trade the Non-Goals forbid.

## Repeat Traps

- **A substring pin over a message cannot see an INVERSION.** Confirmed twice more
  here. Swapping two cause lists, two command pairings, or the CONTENTS of two
  command constants each left every assertion green while making the message
  actively harmful. Pin the PAIRING, the ORDERING, and the distinguishing FLAGS
  by value — never the vocabulary.
- **A test whose subject IS live repo state cannot be mutation-tested by editing
  the worktree.** The edit is itself a state change: the tree goes dirty, the plan
  goes blocked, and the test fails at an EARLIER assertion, which reads like a
  killed mutant. Prove discriminating power by INJECTION.
- **Opening the file is necessary and NOT sufficient.** The sharper form of this
  goal's central lesson, and it is new. The prior statement was "open every
  location an instruction names". At `#536`'s closeout I did open it, printed the
  whole block, read three keys quoting counts — and then wrote the opposite. Write
  the claim from what the read RETURNED, not from the shape the sentence wants.
- **A new entry in a list must be checked against the LIST'S OWN CONTRACT.**
  Pairing a counterfactual command with a prose sentence passed every
  neighbour-shaped test and violated the header's definition of what a pairing
  means. Executed, that instruction pins the wrong threshold — a rule change
  wearing a corpus change's clothes.
- **A guard is only as good as what it matches ON, and on what it SELECTED.**
  Both halves bit in this goal. When a check claims "every X", the next question
  is always "selected how", and the population belongs in an assertion.
- **The commit-msg gate reads prose for GitHub close keywords.** `a fix: #536`
  inside a sentence blocked two commits, and it was right to: on push it would
  have auto-closed the issue with no ledger.

## Next-Time Checklist

1. Verify the reviewer boundary the MOMENT a reviewer returns, before repairing.
2. Run `./scripts/run-quality.sh --read-only` at slice boundaries; the broad suite
   once, at the commit boundary.
3. Premise-check every slice, including which OWNER the remedy names, at
   DEFINITION sites rather than by grep count.
4. Budget round 2 on any slice touching verdict logic; it has never been wasted.
5. For any claim about where a fact lives, quote the read back into the claim.

## North Star Alignment

`docs/design-north-star.md` governs where this goal's teeth belong, and the run
tracks it in three places and misses it in one.

Held: **P4, at the irreversible boundary.** Every one of the five issue closes
paired a `CLOSED` readback with a behavioural verdict from a distinct channel —
a constructed seeded repo, a detached worktree running the shipped CLIs, a real
stub binary logging argv, the issue's own reproduction recipe, and a live
`pytest` reproduction against a constructed corpus write. No close rested on a
terminal green.

Held: **fix the surface that misled the judge.** Slice 2 made the payload state
the FACT rather than renaming keys; slice 1 repaired four WRITERS rather than
tightening one reader. Both chose the misleading surface over a louder gate.

Held: **judgment on reversible work, teeth where a wrong answer escapes.** The
913-site sweep was declined and recorded with its measurement rather than built.

Mis-applied: the **failure signature of a proof surface asserting what it did not
establish** is the class this goal exists to repair, and the goal's own repairs
carried it nine times out of nine. That is not a fluke of one slice; it is the
strongest evidence in this repo that a single round on a verdict surface is not a
review, and it is why the successor budgets two rounds per slice by default.

## Sibling Search

- axis: same layer | location: `charness-artifacts/probe/2026-08-01-inventory-consumption-floor.json` and `charness-artifacts/probe/2026-08-01-inventory-marker-rule.json` — equality-pinned probes over a corpus ordinary work writes | decision: valid follow-up outside the slice | proof: a THIRD probe at `tests/quality_gates/test_measure_evidence_residual.py:103` pins the INVARIANT (`min_residual >= floor`) instead and has never needed a refresh, so the recurring tax is a property of the pin STYLE rather than of the measurement | follow-up: issue #561
- axis: abstraction up | location: `tests/test_issue_source_freeze.py` and the `#514/#515/#518` source-freeze receipt | decision: valid follow-up outside the slice | proof: the same mechanical-re-stamp reflex, measured — 6 of 20 locators changed in one day, five prior re-stamps, all five incidental to the issues' scope, an observed 0/5 true-positive rate, and `refreeze` is one command that records no basis | follow-up: issue #562
- axis: specialization down | location: `scripts/issue_source_capture_lib.py` and `skills/public/release/scripts/publish_release_helpers.py` — the fourth and fifth implementations of the tracker-backend rule | decision: valid follow-up outside the slice | proof: `#559`'s copy had ALREADY drifted from the owner when it was filed (`if subs and "{" in part` versus `if "{" in part`), so the two disagree on an input both accept | follow-up: issues #557, #559
- axis: mental-model siblings | location: `scripts/setup_agent_docs_lib.py:160` — a finding gated on `repo_root.name == "charness"` | decision: valid follow-up outside the slice | proof: static scan plus the reasoning that no consumer repo can satisfy the predicate, so it is a permanent green for every repo but this one — the same class as `#552`, one function family over | follow-up: issue #556

## Next Improvements

- workflow: applied — the successor goal plans FIVE slices rather than nine, on
  this goal's own evidence that it reached five of eleven and that the five were
  good because each got two delegated rounds. It also makes "verify the reviewer
  boundary before repairing" a slice-level obligation rather than a habit.
- capability: issue #561 — Structural pattern: a pinned measurement that asserts
  EQUALITY against a corpus ordinary work mutates converts every routine write
  into a hand re-record, and the re-record is indistinguishable from laundering a
  rule regression. Triggering instance(s): the two inventory probes refreshed
  three times in seven days, versus the residual probe pinning `>= floor` and
  never refreshed. Destination: issue #561 (recurs: measured across three probes
  and five re-stamps).
- capability: issue #562 — Structural pattern: an owner-inspection locator pin
  cannot distinguish "the file I reasoned about changed meaningfully" from
  "someone edited it elsewhere", so its remediation is one mechanical command
  that records no basis — training the exact reflex that will fire on the day the
  semantics genuinely change. Triggering instance(s): 6 of 20 locators changed in
  a day; five re-stamps, 0/5 true positives. Destination: issue #562 (recurs:
  five measured instances).
- memory: applied — this artifact, plus the successor goal's `## Active Operating
  Frame`, which carries the two lessons a gate cannot hold (a substring pin cannot
  see an INVERSION; a live-repo-state test needs INJECTION) and the sharpened
  form discovered at `#536`'s closeout (opening the file is necessary and not
  sufficient).

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-08-one-rule-one-owner-retro.md
