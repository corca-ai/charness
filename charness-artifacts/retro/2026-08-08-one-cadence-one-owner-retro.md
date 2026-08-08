# Retro: One cadence, one owner — stop the harness contradicting itself to the agent

Goal: charness-artifacts/goals/2026-08-08-one-cadence-one-owner-stop-contradicting-the-agent.md

## What Happened

Three of nine planned slices were built, each with delegated fresh-eye review
(two rounds on every one), and the goal closed EARLY by operator direction rather
than pushing six more slices through an exhausted session.

- **Slice 1** — the cadence contradiction. `## Active Operating Frame`'s
  `Gate cadence:` line now has one owner; the achieve template no longer invites
  `## User Acceptance` to restate it; a new validator floor refuses the pair at
  `--pursue-ready` and at the default check; three live artifacts repaired.
- **Slice 2** — one owner for a sweep's population.
  `check_current_pointer_writes` delegates to `repo_file_listing`. Population 683
  before, 683 after, identical set.
- **Slice 3** — a consolidation ledger states population and removals as two
  labeled numbers, so the arithmetic that blocked three of four consecutive
  closeouts becomes unwritable rather than detectable.

## What Created Waste

- **Chasing a rotated duplicate hash.** The dup ratchet's FIRST block was right
  and caught a real defect (a sixth copy of a section walk). Reshaping code to
  clear a LATER rotated hash is what routed two `complete`-state floors onto a
  level-aware section walk — a latent false green at a terminal boundary, caught
  only by round 2. The chase cost more than the duplication did.
- **Repairing before verifying the reviewer boundary.** Done on every slice.
  Each window then needed after-the-fact reconciliation by declaring parent
  paths, which is strictly weaker: it cannot distinguish reviewer writes from the
  parent's, and only the reviewers' lack of write tools makes it sound.
- **A cross-goal blast radius nobody could see at the slice gate.** A one-line
  change to `run-quality.sh` (and later two more files) invalidated a checked-in
  source-freeze receipt for issues this goal does not own. The cheap slice gate
  is green; three tests are red.

## Decisions That Mattered

- **Shape over parser, twice.** Slice 1 repaired the template that kept
  reproducing a sentence rather than adding a louder gate. Slice 3 made the
  ledger ambiguity unwritable rather than building an English arithmetic judge.
  Both follow the north star's "fix the surface that misled the judge".
- **Refusing to re-stamp the freeze.** A refreeze would have turned three tests
  green by asserting an inspection that never happened, of issues this goal does
  not claim. Reported instead.
- **Exempting the read-only quality gate on MEASURED COST, not command scope.**
  Scope was the wrong argument — that script does queue the standing pytest
  runner — and a maintainer believing otherwise would have "fixed" the exclusion.

## Repeat Traps

- **A substring pin over a message cannot see an INVERSION.** Swapping two cause
  lists or two command pairings leaves every assertion green while making the
  message actively harmful. Pin the PAIRING and the ORDERING by value, not the
  vocabulary. Applied here: slice 1's refusal binds the frame line and the
  acceptance line to distinct roles, and an inversion mutant is killed by
  comparing line numbers rather than by matching text.
- **A test whose subject IS live repo state cannot be mutation-tested by editing
  the worktree.** The edit is itself a state change: the test then fails at an
  earlier assertion and the mutant looks killed. Prove discriminating power by
  INJECTION instead — add to the population rather than editing the code.
- **Every measured slice shipped a fix carrying the class it fixed.** Now 3 for 3
  in this goal, on top of the predecessor's 5 for 5. Round 2 is not optional on a
  verdict surface, and none of its blockers were mutation-findable.
- **Verify the remedy's premise AND the owner it names.** All three premise
  checks were refuted or corrected at design time. Slice 2's goal named the wrong
  owner outright: the script it called "the precedent" was itself a hand-rolled
  copy, so building to the letter would have shipped an eighth one.
- **Derive a matcher's vocabulary from the surface that PRODUCES the text.**
  Slice 3's verb list was written from the one measured sentence and missed the
  verb the repo's own authoring reference instructs authors to use, so the gate
  passed every test while being nearly inert on real ledgers.

## Next-Time Checklist

- Verify the reviewer boundary the moment a reviewer returns, before repairing.
- Classify a rotated duplicate hash with a reason; never let it design a proof
  surface.
- Budget two review rounds for any slice touching verdict logic.
- Run the premise check against the remedy's named OWNER, not only its diagnosis.
- Mutate every REPAIR, not only the original code: seven survived first here.

## North Star Alignment

The goal's teeth went where a wrong answer escapes: instruction surfaces an agent
obeys, and gate populations that decide what gets looked at. No gate that cries
wolf was added — each new floor fires only on a measured shape and discloses when
it did not evaluate. At the one irreversible boundary reached (a frozen evidence
artifact), success was treated as provisional and the refusal was reported rather
than stamped away.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-08-one-cadence-one-owner-retro.md
