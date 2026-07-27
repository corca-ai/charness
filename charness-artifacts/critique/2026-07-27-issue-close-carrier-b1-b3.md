# Issue-close carrier B1-B3
Date: 2026-07-27

## Decision Under Review

Fixing B1, B2 and B3 from the evidence-surface bug hunt — the three defects on the
GitHub issue-close carrier, where a false PASS closes a real issue on GitHub.
B1: the declared `n/a` placeholder was unreachable, so an all-`N/A` ledger passed
every rung-1 floor. B2: the caller manufactures the allowed skip head, so a
17-character excuse skipped the mandatory fresh-eye critique. B3: the word
`Answer:` anywhere in a staged artifact inferred the fully-exempt `question`
classification.

## Failure Angles

- **The fix relocates the hole instead of closing it.** B2's enum check is
  vacuous *by construction* on this carrier — the caller supplies the constant
  being validated. Any fix that leaves length as the only tooth is selling a
  typing-effort floor as a proof floor. Bit: a 40-character excuse passes.
- **A shared predicate re-baselines unrelated surfaces.** `_has_substantive_value`
  gates every ledger, behavioral, provenance, HOTL and source-preservation floor
  on all carriers; `_validate_skip_reason` is shared by achieve, issue and
  release closeouts. A tightening at the shared layer lands on callers nobody
  looked at. Bit twice: an initial 40-char *detail* floor broke five goal-closeout
  fixtures, and B1 flipped `Source origin: N/A` from refused to exempt.
- **Fail-closed has a cost paid by real authors.** Removing an inference branch
  blocks commits that used to pass. Bit: the removal downgraded real bug closeouts
  to `feature`.
- **Hardening one sibling and not the other is the defect's own shape.** B3 *is*
  "the hardening was applied to `_bare_classification` and not `_infer_classification`".
  A fix that repeats that asymmetry in the other direction has learned nothing.
  Bit: the bare path still read the classification from unstripped text.
- **Length floors invite fabrication.** Setting a floor above observed honest
  usage buys padding, not signal.

## Counterweight Pass

- Real blockers, all folded in: the `root cause:` branch removal (a genuine
  regression, restored), the fenced-`Classification:` escape on the bare path,
  the 40-char detail floor over-tightening (lowered to 20 with the rationale
  recorded), and the buried advisory on the `verify-closeout` carrier.
- Over-worry: the `N/A`-collides-with-real-text concern. The only newly-refused
  strings are bare dismissals (`N/A`, `n.a.`, `N-A`); a dismissal carrying a
  reason stays substantive, and no in-repo value collides.
- Deferred, not ignored: `none` is still not a placeholder and is a likelier
  hand-written empty than `N/A` was; the release publish carrier is the same
  manufactured-head shape and got the floor but no advisory. Both are recorded as
  leads in the bug-hunt record rather than folded into a B1-B3 slice.
- Accepted and stated rather than fixed: B2's fluent-excuse residual cannot be
  closed at rung-1. Saying so is the honest move; claiming B2 closed would not be.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/check_issue_closeout_commit_msg.py:130 | action: fix | note: dropping the `root cause:` -> bug branch as redundant downgraded real bug closeouts to `feature`, silently removing the debug_artifact and siblings floors; branch restored ahead of `feature` with a regression test
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/check_issue_closeout_commit_msg.py:151 | action: fix | note: the bare close-keyword path read the classification from fence-unstripped text, so `Classification: question` inside a pasted code fence asserted the exemption; close keywords now read raw and the classification reads stripped
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/check_prescribed_skill_executed_lib.py:30 | action: fix | note: a 40-char detail floor sat above the repo's own 24-39 char honest host signals and broke five goal-closeout fixtures; set to MIN_SKIP_DETAIL_LENGTH = 20, which still closes the confirmed 17-char cliff
- F4 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/scripts/issue_verify_closeout.py:295 | action: fix | note: the skip advisory sat three levels down beside a top-level `ok: true` on the carrier the skill's own verify command uses; surfaced at the top level on the same key the sibling carriers use
- F5 | bin: bundle-anyway | evidence: strong | ref: skills/public/issue/scripts/issue_verify_closeout_body.py:238 | action: document | note: making `N/A` a placeholder flips `Source origin: N/A` from refused to exempt, because the predicate is a gate-opener there; the reading is correct but it is a floor moving toward PASS inside a tightening fix, so it is pinned by its own test rather than left silent
- F6 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md:148 | action: defer | note: B5 absorbs a bare placeholder into the following line, so an all-`N/A` ledger is still not uniformly refused; B1 stays PARTIAL rather than being claimed FIXED
- F7 | bin: valid-but-defer | evidence: moderate | ref: skills/public/release/scripts/publish_release_preflight.py:257 | action: defer | note: the publish boundary is the same manufactured-head carrier and received the floor but no advisory; recorded as a lead, out of B1-B3 scope
- F8 | bin: over-worry | evidence: weak | ref: scripts/check_prescribed_skill_executed_lib.py:43 | action: defer | note: concern that normalizing the placeholder set would refuse legitimate short field values; no in-repo value collides, and a dismissal carrying a reason stays substantive

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (typed read-only agent, three independent spawns — one per defect).
- Requested spawn fields: subagent_type=bounded-reviewer, per-defect scope prompt with named review angles, no host addressing name, session-model inheritance.
- Host exposure state: applied
- Application state: host-confirmed: Claude Code accepted all three `bounded-reviewer` spawns and returned findings inline; `reviewer_boundary_fingerprint.py verify` reported `ok: true` with `drift: []` and no undeclared worktree or index mutation across window `w-20260727T124158Z-2339125`.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated` — three bounded read-only reviewers ran in separate agent
contexts, one per defect, and returned findings the parent then reproduced by
execution before folding. The B3 reviewer explicitly requested `git show HEAD:`
evidence it could not obtain read-only; the parent ran it and confirmed the
reviewer's inference that the removed branch preceded the `feature` branch.

## Reviewed Input Identity

<!-- Packet-bound critiques replace this comment with three bullets copied from prepare_packet.py after the reviewed packet is final: Packet path, exact Packet SHA256, and Identity SHA256. Leave this section comment-only when no packet was consumed. -->

## Boundary Ownership

- Producer: `check_prescribed_skill_executed_lib._validate_skip_reason` and `issue_verify_closeout_body._has_substantive_value` — two shared predicates behind every closeout floor.
- Consumer: the GitHub issue-close carriers (`verify-closeout`, `close-with-comment`, the commit-msg pre-commit hook) and, for the skip predicate, the achieve and release closeouts too.
- Owning surface: the shared closeout-evidence library, not the per-carrier callers — both defects were single predicates reached by many carriers, which is why per-carrier patches would have left siblings live.
- Verdict: owned-correctly
