# Session Retro

Date: 2026-08-31

## Context

Continued the Goal 744 Git/subprocess campaign from the uncommitted pickup note.
The operator's own framing drove the session more than the note did: first "there
must be more low-hanging fruit, especially by deleting or merging tests", then
"wall-clock depends on the machine — focus on what is reducible regardless", then
twice more on the real question — *are these tests individually worth their cost,
or is 2400 a number nobody has audited?*

That question turned out to be the valuable one, and my answers to it were wrong
three times before they were right.

## Window

From the pickup note through six commits, `469614d53..addc26ddb`. Standing suite
8423 passed / 0 failed; boundary ratchet green; working tree clean.

## Evidence Summary

- Spawn census, same warm conditions both ends: v49 `5294 spawns / 3297 git /
  910 python3 / 803 git-nodes` → v52 `4998 / 3064 / 834 / 702`.
- The seed-cache axis is invisible in that comparison by construction. Measured
  separately: cold `397` fixture git calls vs warm `65`; after the split, a
  source hash never seen before spends `71`.
- Per-change measurements: setup preflight `79 → 5`; `run_script` real spawns in
  `tests/quality_gates` `112 → 35`; `check_staged_reversion` `38 → 20`;
  `dup_ratchet_edit_advisory` `36 → 25`; three merged files `275 → 261` git while
  their nodes went `79 → 26`.
- Mutation attribution over `reviewed_input_identity.py` + `reviewed_input_nonblob.py`
  against the 70-test #759 pin cluster: 213 mutants, 157 killed, 56 survived.
- Bounded read-only review of all 70 pins: KEEP 62, SUBSUMED 8, STRUCTURAL 0.
- Two fresh-eye critique reviewers (Weinberg, Gawande lenses), both `block`;
  findings triaged into four bins before commit.

## Waste

- **I reported a headline metric before validating its assumptions, and had to
  walk it back three times.** "Exact-argv repeats inside one pytest node" gave
  339 provably-redundant product git calls, which I presented as beating the
  code-reading audit's 97 by 3.5×. It then fell to 134 (a `HEAD:`-relative read
  is not immutable — HEAD moves), then further once the probe was taught to
  record the subprocess `cwd` (identical argv against different fixture repos),
  then to ~35 (a one-sided `diff <sha> -- <paths>` compares against the WORKING
  TREE). The expensive semantic method was the more accurate one all along, and
  I had told the operator the opposite.
- **Two subagents were commissioned on that bad target and both were reverted.**
  `memo1` and `memo2` did careful, correct work — each refused to cache across a
  mutation boundary exactly where I had wrongly told them the fact was immutable —
  and that care is precisely why the measured payoff was `−3` and `+2`. The waste
  is mine: roughly two agent-runs spent because I did not test the target before
  spending it.
- **My own verification instrument shared the blind spot of the work it checked.**
  I proved the test consolidation lost nothing by counting `assert` statements per
  file before and after. That check passes for a helper that is extracted but
  never dispatched: the assertions stay in the file and the count balances while
  nothing runs them. A fresh-eye reviewer found five such helpers with eleven
  unreachable assertions in `test_issue_worker_carrier.py`; I did not.
- **An over-broad predicate during the revert deleted four unrelated merge
  helpers.** Recovered from HEAD's originals, verified by assertion parity — but
  it was a self-inflicted detour inside a cleanup.

## Critical Decisions

- **Isolating the seed-cache axis by measuring cold vs warm separately.** The
  campaign's largest win — ~330 git calls paid again after *every edit* by 147
  seeds that depend on no source — is exactly zero in a warm-to-warm census. It
  would have stayed invisible under the metric the ledger had been using.
- **Reverting both memo agents on measurement rather than on plausibility.** Both
  changes looked principled and were green. Net effect ≈ 0, and `memo2`'s cache
  had no production constructor at all. Keeping them would have added two public
  classes and threaded kwargs across eleven files for nothing.
- **Running fresh-eye critique before the commit, not after.** It is the only
  reason the orphaned dispatcher did not land.
- **Keeping the submodule cleanliness query when a reviewer proved it must stay.**
  Folding it into the superproject status snapshot looked free; the verifier
  demonstrated that `submodule.<name>.ignore = all` makes a dirty submodule vanish
  from that snapshot. A saving that reads as free at the callsite can be a hole at
  the contract.
- **Refusing to share a gitlink/object memo between a capture and its own
  verification**, even though tests had already been rewritten to do it. The drift
  arm still worked; the "capture then verify agrees" arm became self-confirming.

## Trends vs Last Retro

`2026-08-30-session-retro.md` led with: *"I produced defects of the class I was
repairing, at a rate of roughly one per repair, and caught none of them myself."*

Same shape recurred here, once. The class under repair was *test value and
duplication*; the defect I introduced was a test present but unreachable — the
purest form of "looks like it guards, does not". Again I did not catch it; a
fresh-eye reviewer did.

Two things did move. The fresh-eye pass ran **before** the commit rather than
after seven rounds of repair, so the defect cost one edit instead of a series.
And the sibling scan ran this time instead of being skipped, which is the
discipline the previous retro named as missing.

What did not move: my *checking* instrument was as blind as my *building* one.
Last session the gap was between repair and review; this session it was inside
the verification I built for myself.

## North Star Alignment

Charness ships composable capabilities; consuming repos own their Git and
workflow. Three of the six commits are repo-internal test economics and carry no
consumer surface. The one that does — `fix(critique)` — is a genuine capability
repair: every deletion-only working-tree review was refusing, because a portable
skill script restated a digest framing across the boundary it cannot import
across, and the two sides drifted. That is the failure mode the portability
boundary creates, and it now has a guard that drives both real binders instead of
restating the constant a third time.

The campaign's stated intent also held: Git counts fell as a *result* of better
structure (a cache that stops lying about what invalidates it, a preflight that
does not ask Git about a non-repo), not as the goal. Where structure did not
reduce Git — test merging, `−14` — the commit message says so rather than
claiming the node count as the win.

## Expert Counterfactuals

**Gary Klein (pre-mortem, applied to the metric rather than the plan).** Before
publishing "339 provably redundant", ask the pre-mortem question about the
*measurement*: it is six hours later and this number is wrong — why? The three
answers were all reachable in minutes: `HEAD` is not a fixed ref; the probe never
recorded the subprocess `cwd`; a one-sided diff reads the working tree. Klein's
move is to run that hostile pass **before** the number leaves my mouth, not after
the operator has acted on it. Concretely: I would have spent five minutes
classifying my own verb buckets adversarially and never commissioned `memo1` or
`memo2` on a target that dissolved.

**Douglas Engelbart (design T alongside the work).** The assertion-count check was
tooling I invented for myself mid-session and trusted immediately. Engelbart's
frame says the tool that checks the change is part of the same system as the
change and deserves the same scrutiny — including "what state passes this check
while being wrong?" One sentence of that would have produced the reachability
question, because the answer is obvious once asked: an orphaned function keeps
its assertions. The wider move is that this check should not be a throwaway shell
one-liner at all; a consolidation that promises "assertions preserved" needs a
repo-owned gate, which is why it is in Next Improvements rather than in my scroll
history.

## Next Improvements

- **capability — `novel:` add an orphaned-`_case_`-helper gate.** Five files now
  carry `_case_*` dispatch families and nothing detects a helper that loses its
  caller. A ~15-line check (helpers defined, names referenced, difference empty)
  would have failed this session's diff. Destination: a repo quality gate beside
  the other structural checks.
  Structural pattern: a consolidation shape whose failure mode is silent
  unreachability. Triggering instance(s): `test_issue_worker_carrier.py`, five
  helpers, eleven assertions.
- **workflow — `recurs:` never quote a derived metric until its assumptions have
  had one adversarial pass.** The rule that would have caught all three errors:
  for any "this call is redundant" claim, state what would have to be true for the
  answer to change between the two calls, and test that statement. This recurs
  against the previous retro's lesson about characterizing a class before
  repairing instances — same failure, one level up, on measurement instead of code.
- **workflow — spend a subagent only after the target survives its own check.**
  Both reverted agents were commissioned before I had validated the target. A
  single measurement on one call site would have shown `−3` before two agents ran.
- **memory — record that verification instruments need their own negative
  control.** The reachability fix was only trustworthy because I broke a restored
  assertion and confirmed the dispatcher failed. That step, not the assert count,
  is what proved it. Applies to any future "nothing was lost" claim.
- **capability — teach the spawn probe to record `cwd`** (done this session in
  `/tmp`, not durable). Without it, identical argv against different fixture repos
  is indistinguishable from asking the same question twice, which is a measurement
  error the census will keep making.

## Sibling Search

The transferable pattern: *a verification instrument that shares the blind spot of
the artifact it verifies.*

- Axis 1 — same shape elsewhere in tests: 5 files carry `_case_*` families
  (`test_premise_preflight`, `test_check_staged_worktree_consistency`,
  `test_artifact_referents`, `test_seed_lesson_transitions`,
  `test_issue_worker_carrier`); all now 0 orphaned. **Decision: verified clean, no
  further repair, gate proposed above.**
- Axis 2 — a repo gate for it: none exists. **Decision: convert to Next
  Improvements capability item.**
- Axis 3 — count-based preservation claims in product code: searched; the repo's
  proof surfaces bind digests and receipts rather than counts, so the specific
  "count balances while nothing runs" hazard is local to test consolidation.
  **Decision: no sibling.**
- Axis 4 — other self-built session instruments trusted without a negative
  control: the spawn-repeat classifier, which is exactly the one that failed three
  times. **Decision: same root, folded into the workflow item above rather than
  filed twice.**

## Packet Consumed

`charness-artifacts/retro/2026-08-31-123034-packet.md`

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-31-session-retro.md
