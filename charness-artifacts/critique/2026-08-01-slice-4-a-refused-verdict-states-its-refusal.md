# Slice 4 critique — S23 and S2, "a refused verdict states its refusal"

Date: 2026-08-01
Goal: [close-the-sweeps-remaining-high-rows-by-class](../goals/2026-08-01-close-the-sweeps-remaining-high-rows-by-class.md)
Slice: batch D — sweep rows S23 and S2.

## Reviewer Tier Evidence

- Requested tier: bounded read-only reviewer (`bounded-reviewer` typed agent)
- Requested spawn fields: agent_type=bounded-reviewer, unnamed spawn, session-model
  inheritance. Claude Code host, so the Codex model/effort request does not apply.
- Host exposure state: requested_fields_sent
- Application state: both spawns accepted and returned findings inline.
- Delivery state: findings-received

## Reviewer Provenance

Fresh-eye satisfaction: parent-delegated

Two bounded `bounded-reviewer` subagents, one round, spawned unnamed in the shared parent
worktree with Read/Grep/Glob only: correctness of the repaired surfaces, and blast radius
plus claim honesty.

Worktree integrity: snapshot opened window `slice4-round1` at HEAD `dac61db7`.
**Non-claim:** the matching `verify` was not run — the parent edits in-tree during the
window by design and `--parent-path` was not used. Integrity rests on
`git status --porcelain`.

## The prediction this slice falsified

The goal's plan critique and a round-1 reviewer independently concluded that S23 could
not reproduce: `confirmation["line"]` carries an `if ok else None` guard introduced
2026-07-20, before the sweep. **Both were wrong.** The guard runs before
`_fold_proof_mismatch`, which flips `ok` to False and `status` to `failed` afterward and
never touches the sentence. The reproduction refuted the refutation. Had the slice
trusted the prediction, S23 would have closed as REFUTED with the defect intact.

## Round 1 — findings folded

- **BLOCKER: the S23 class was open one level up.**
  `release_issue_closeout_message` performs a SECOND post-hoc flip on the same
  `verify_closeout` payload — `ok = False` on unexpected close keywords — without syncing
  the confirmation. An existing checked-in test already exercised that path and asserted
  only the flip. Repaired and pinned.
- **BLOCKER (both reviewers, independently): S2's new violation reported the wrong line
  with the wrong sentence.** The leftover is the tail of a shifted pairing, so pointing an
  operator at it with "collapse this wrap" sends them to a line where nothing wraps. The
  unterminated case now has its own message and its own reason token.
- **The measured zero was not a safety argument.** `check-markdown.sh` treats this checker
  as ADVISORY and exits with markdownlint's status alone, so nothing here can block a
  commit. The zero means the new class adds no noise, and the code comment now says that
  instead of implying an arming decision was made safe.
- The measurement counted untracked files and the docstring promised an `iff` the code
  enforces in one direction only. Both corrected.

## Round 2 — NOT RUN

Only one round ran for this slice. The two-round rule is triggered by a first round that
produced repairs, and this one did. **This is a recorded gap, not a discharge:** the
slice's repairs — the release-carrier sync, the message split, the scope narrowing — have
had no fresh eye on them. Slices 1 and 2-3 each had round 2 catch defects created by
round 1's repairs, so the base rate for this class is not low. Carried to the handoff.

## Boundary Ownership

- Verdict: owned-correctly

`verify_closeout` PRODUCES the verdict and the sentence describing it; the consumers
(`release_issue_closeout_message`, `issue_validate_closeout_draft`) receive the payload
and, in one case, mutate the verdict. Putting the sync in the producer's module and
calling it from the mutating consumer keeps one definition of the invariant. The
alternative — having each consumer re-derive the verb rule — is what the 2026-07-20
additive-migration critique already rejected.

## Non-claims

S23 CLOSED with its row's `surface:line` corrected; S2 NARROWED with three residuals
named on the row. Round 2 did not run. No push, no CI dispatch, no cautilus run.
