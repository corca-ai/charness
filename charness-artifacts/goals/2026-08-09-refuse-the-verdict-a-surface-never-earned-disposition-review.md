# Disposition Review — refuse-the-verdict-a-surface-never-earned closeout

Date: 2026-08-10
Reviewer: bounded read-only fresh-eye subagent (`bounded-reviewer`), spawned
unnamed and synchronous, in a context separate from the retro's author.
Worktree/index integrity fingerprinted `clean` around the review window.

## Verdict as returned

**DISPOSITIONS REFUSED**, with one clear overclaim, one route the reviewer could
not verify from the title alone, one partial, and a padded sibling count.

## Findings and what was done

**1. `applied:` the successor goal's slice 2 — OVERCLAIMED.** The disposition said
slice 2 "specifies backlog re-verification as an extension of the existing recount
seam rather than a second backlog reader". The reviewer grepped the successor goal
and found the phrase, the constraint, and the non-goal absent — correctly
predicting that the Engelbart counterfactual was written after the goal and
backdated onto a commit that did not carry it.

Resolved by landing the constraint rather than watering down the claim: the
successor goal now carries a `### Slice 2 design` block making the recount-seam
extension binding, and its non-goal reads "no gate that auto-closes an issue, and
no second backlog reader".

**2. The same review found a defect in slice 2's own specification.** As written,
the tool emitted `premise-holds` / `premise-refuted`, and a refuted premise read as
a close candidate. That signal would have pushed the WRONG way on `#554`, the very
instance the slice exists for: its premise was genuinely refuted and the correct
answer was still do-not-close, because part 2 was live and the shipping goal's own
slice log said so. The typed state set now distinguishes `premise-refuted-clean`
from `premise-refuted-with-live-residue`, and the residue check is one grep of the
issue number across the goals directory — the command that would have caught `#554`
before a reviewer round was spent. This finding is the review's most valuable
output and it was not in its assigned scope.

**3. `issue #571` — UNVERIFIABLE from the title; now verified from the body.** The
reviewer refused to grade a route it could only judge by title, and said so rather
than guessing. Fetching the body settles it: `#571`'s instance 2 is `#567`,
"already fully repaired… the session's first disposition was re-scope — based on
the issue body rather than on the commit that fixed it". That is the `#554` shape,
so the destination is correct and the disposition now cites the body.

**4. Digest disposition — PARTIALLY REAL.** The digest was refreshed and carries
both improvement lines, but its `## Repeat Traps` slot still shows only the older
"spoke before measuring" phrasing. The reviewer noted the mitigating fact that the
slot is filled by a recency/recurrence policy rather than by the retro. The
disposition was reworded to claim only what the file shows.

**5. Sibling count padded.** Four surfaces were listed; three were evidenced in the
retro's own body, and one evidenced instance (the different-tree framing) had been
silently dropped from the list while two unmeasured surfaces were added. Corrected
to three, all this run's, with the related-but-unmeasured surfaces named as
explicitly not counted.

**6. Retro metrics contradicted the probe they were bound to.** The retro quoted
304 function calls / 477 token snapshots; the persisted probe said 314 / 489,
because the session kept running between the read and the write. Corrected by
citing the command and the persisted artifact instead of transcribing a moving
number — this repo's own regenerable-fact stance, applied to its own retro.

**7. Goal self-contradiction.** The forced-completion block said the goal-level
retro and the Auto-Retro disposition pass "did NOT run", while the Final
Verification section binds a retro and the Auto-Retro section is filled. Corrected
to state what is actually absent.

## Non-claims

- This review read the dispositions and their targets. It did not re-verify the
  release, the twelve issue closes, or the four earlier bounded reviewer rounds;
  those carry their own records.
- The reviewer could not run commands, so `b7d93729`'s existence and the `#571`
  body were verified by the parent afterward rather than by the reviewer.
- Round 2 of this review was not run. The corrections above are recorded as
  accepted-unreviewed.
