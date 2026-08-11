# session retro
Date: 2026-08-11

## Context

The second work unit of 2026-08-11, distinct from the umbrella-disposition session that
owns `2026-08-11-session-retro.md`. Pickup from the handoff, push excluded: execute the
recorded deletable-surfaces sweep, then take six operator-reserved decisions in
conversation. The unit under review is the whole arc, because the useful lesson is about
what I did NOT catch myself — again.

## Window

`8d4337c5` through `afaaef4e`, all local, eight commits, 27 files, +885/-664. One
13-agent workflow, three bounded reviewer rounds, six rulings recorded, one deprecated
shipped surface deleted, one recurring defect class named.

## Evidence Summary

- `run-quality.sh` executed five times end to end; opening baseline **re-measured** at
  `8d4337c5` (90/0) rather than inherited, closing at 90/0.
- `prepush_focused_changed_line_coverage.py` run three times; `clean` after each commit,
  `blocked` once for the dirty-worktree line-number mismatch it names in its own warning.
- `reviewer_boundary_fingerprint.py` snapshot/verify around all three review windows:
  `clean`, then `parent-attributed` twice with zero undeclared drift.
- Two feasibility measurements written into the rulings artifact rather than left as
  prose: the `charness <token>` false-positive collapse (72 -> 27 -> 3) and the absence
  of call-site line info in the boundary-bypass inventory.
- `git show 7a43c8a4:scripts/boundary-bypass-baseline.json` and `git show 322664d5:...`
  to settle two claims reviewers could not reach.

## Waste

**The first command of the session ran the INSTALLED plugin copy.** I invoked
`~/.agents/src/charness/.../plan_handoff_run.py` against this repo and read its output as
repo state. It still carries `--pickup-target` and `next_session_entry_count`; the source
dropped both at `a24b0155`. Cost: I told the operator a shipped ruling was pending, and
built a scope question around it that they then answered under a false premise.
`recent-lessons.md:11` names this exact trap. A stale `still not executed` banner on the
plan artifact was the accomplice, and only the accomplice got fixed by anything automatic.

**Two of my own repairs shipped the class they were repairing.** In the commit titled
"Three surfaces that could not fail" I replaced a count pin with an assertion that could
not fail — the trigger-presence relation is already raised by a queued validator — and
wrote a comment claiming a total "never could" catch what a total catches immediately.
Then the round-1 repair for that commit silently changed four still-enforced count fields
in the masking direction, by unifying two walks that had disagreed on purpose. Neither was
carelessness; both were verified-then-wrong.

**A deferral on a reason I had not checked.** I parked the `check-markdown` item claiming
its doc target was a dated audit snapshot. It is a live registry appended to through
2026-08-10, and its own process section instructs authors to edit it. The operator asked
one question and the deferral evaporated — and the item turned out to be the session's
best find (540 files, 5.0s, three of four criteria violated, never classified).

**A rule proposed against a channel I had not looked at.** I offered deprecation-window
options as though the default were obvious. The operator asked why versions do not simply
do this, and the answer was that they do: release notes here lead with breaking changes
and give remedies. I had reached for a new rule without checking the existing channel.

## Critical Decisions

- **Mandating the consumer grep inside the schema.** Every triage agent had to emit the
  search command and its result before proposing. Eight of thirteen candidates were
  refused on real consumers found that way. Compare the prior session: seven wrong
  proposals, each refuted by one grep nobody ran.
- **Two review rounds, not one.** Round 1 found the tautology and the luck-dependent
  proof; round 2 found that round 1's own repair had moved four enforced counts. One round
  would have shipped the second defect with a commit message asserting the first was fixed.
- **Refusing rather than skipping in `_rows_with_targets`.** Round 2's finding had two
  fixes; skipping keeps the code shorter and can only ever MASK the arm, because
  `check_payload` fires on `current > baseline`. Choosing refusal over the shorter branch
  is the whole difference between a repair and a quieter defect.
- **Deriving the class instead of shipping the sixth instance.** Three rulings resolved to
  the same shape, and counting the two the repo had already fixed made five. Naming it in
  the owning contract cost one section; not naming it had already cost five slices.

## North Star Alignment

P5 governed the two hardest calls and pointed opposite ways, correctly. `check-markdown`
lost its unscoped commit-time teeth because a wrong pass escapes nowhere a later lane does
not catch — reversible work, P1. `domain_language_contract` was NOT demoted on the same
reasoning, because its scan reaches `skills/public/**/*.md`, which ships; that is teeth for
form on an irreversible surface. The issue's own framing had them as one question.

The Taste rung held at its stated precondition. Deleting `domain_language_contract` is only
justified because a derived check replaces its capability first — at equal capability,
prefer less. The plan artifact records four prior failures of exactly that precondition, and
the ordering constraint ("the derived check works BEFORE the deletion") is written into the
ruling because of them.

## Trends vs Last Retro

**The trend is flat, and that is the finding.** The prior retro's third improvement was
"run the adversarial pass before the operator asks. Every correction this session was
operator-initiated." This session: six corrections, zero self-initiated. Two came from the
operator, three from bounded reviewers I spawned because the contract requires them, one
from a workflow I ran because the handoff said to. The contract's mandated reviews are
carrying the load that the improvement asked me to carry.

Second trend, improving: the prior retro's sharpest lesson — a removal proposal must carry
its consumer search — did transfer, and measurably (8 of 13 refused on found consumers).
It transferred because it was written into the workflow's schema as a required field, not
because it was remembered.

## Expert Counterfactuals

**Douglas Engelbart — treat (Human + Language/Artifacts/Methodology + Tooling) as one unit;
design T alongside LAM.** The class I named lands entirely in LAM. `Declared Where
Derivable` is a prose section asking a future author to notice, at authoring time, that a
literal has an upstream authority. Engelbart's objection is immediate: I shipped the L and
skipped the T, on a repo whose own issue `#562` records the general form — *"a method
requiring the agent to remember to search has no tool, so it degrades to memory."*

What he would have done differently, concretely: ship the smallest T with the section. The
five instances share a machine-checkable shape — a literal in a `*_lib.py` constant, an
assert, or an adapter list whose value equals something a sibling command already prints.
Even a `--suspect-literals` advisory over the five known shapes would convert the rule from
"remember this" into "the tree tells you." I have the counter-argument and it is weak: the
discriminator is a judgment call, so a detector would false-fire. That is an argument for
an ADVISORY, which is what this repo's floor-addition restraint prescribes anyway, not an
argument for prose alone.

**The second lens, deliberately not a name: the operator's own.** Twice the decisive move
was refusing my framing rather than choosing among my options — "why can't we just delete
it? that's what versions are for", and "I thought it was already a content fingerprint".
Both times I had presented a menu that presupposed the thing worth questioning. The
transferable form: when I offer three options, check whether all three share a premise, and
say so in the question.

## Next Improvements

- workflow: when the first command of a session resolves a repo-owned script, resolve it
  from the repo root explicitly and say which copy ran. The installed/source confusion has
  now cost two release attempts and one false operator claim across three sessions.
- workflow: before presenting options, name the premise all of them share. Two of six
  rulings were settled by the operator rejecting a shared premise I had not surfaced.
- capability: a `--suspect-literals` advisory for the `Declared Where Derivable` class,
  seeded from the five recorded instances. Structural pattern: a rule that asks the author
  to notice a shape at authoring time has no tool, so it degrades to memory — the exact
  form issue `#562` already records. Triggering instance(s): five shipped instances, four
  fixed independently without recognising the class. Destination: new issue.
- capability: the recent-lessons SELECTION policy needs a design, not another filter. The
  top two `next_improvement` candidates by weight are content-free bookkeeping ("This retro
  plus the recent-lessons digest", "this artifact and the digest refresh it drives") out of
  884 candidates, because every retro emits that line and recurrence boost rewards it. The
  operator has a design in hand and reserved it for the next session; adding a
  content-free filter would have stacked a heuristic on a heuristic. Destination: next
  session, operator-led.
- workflow: `>= 35` is a ratchet floor implemented in this repo's worst available form — an
  inline magic number plus a prose instruction to bump it. Every other ratchet here has a
  baseline file and an accept command. Either give it that form or drop it.
- memory: this artifact, and `Declared Where Derivable` in implementation discipline, which
  is where the class lives rather than here.

## Sibling Search

The named class IS a sibling scan result: five instances across three surfaces
(`should_fire_chunker`, dup-ratchet ids, `domain_language_contract`, D47's figures,
boundary-bypass keys), recorded in the owning contract with the discriminator that keeps
form validators and written-reason waivers out of it.

One further axis scanned during the session and worth recording: **test fixtures that
hardcode a value a library owns.** Raising the handoff budget from 58 to 78 silently turned
`handoff_body(current_lines=60)` from an `over_limit` fixture into a passing one — the test
kept its name and stopped testing it. Fixed by deriving both fixtures from
`module.MAX_CONTENT_LINES`. Decision: local fix applied; a broader sweep for fixtures
pinning library-owned constants is a plausible follow-up but was not run, so no claim is
made about how many exist.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-11-six-rulings-and-the-declared-where-derivable-class.md
