# PR #419 Adversarial-Verification Fix Closeout
Date: 2026-07-04

## Decision Under Review

Fixing the findings the adversarial verification of PR #419 surfaced — one MAJOR
escape at the issue-close irreversible boundary plus low-risk minors — then
merging PR #419 to main and cutting a release. Shipped: the MAJOR fence-strip fix
and the achieve pointer fix. The bare-close question-exemption advisory (F2) was
authored, fresh-eye-reviewed CLEAN, then **reverted** because the repo dup-ratchet
gate (a mechanism this very PR added) hard-blocked it as P2 displaced duplication
of `issue_close_comment_floor.review_advisory_for_classification`; it is deferred
to D36 rather than bypassed with an intentional-dup accept. This critique covers
only the fix slice; the whole 198-file PR already carries its own three-reviewer
critique record
(`charness-artifacts/critique/2026-07-04-north-star-p1-p3-sweep-branch-north-star-p123.md`).

## Failure Angles

- The fence-strip removal could over-block legitimate commits (false positive on
  a gate that runs on every commit). Checked: raw scanning is correct-by-design —
  any close keyword present WILL auto-close on GitHub — and the failure message
  already tells authors to rewrite to a bare `#N`; the full gate suite stays green
  with no previously-passing case flipping.
- The removal could leave a *different* escape (artifact-path fence-strip, or some
  other sanitization dropping the keyword). Fresh-eye reviewer traced it: the only
  remaining pre-scan step is `_strip_commit_comments`, which matches git's own
  default comment stripping, and the artifact-path fence-strip cannot auto-close.
- The new advisory could change what the gate permits (turn a block into a pass or
  vice-versa). Checked: `advisories` is a separate list never fed into `ok` or the
  return code — structurally and empirically additive.
- The achieve pointer edit could introduce an inaccurate reference. Checked:
  `references/goal-artifact.md` is the single owner of the Remaining Boundary
  Matrix line form (`lifecycle-during.md:137`); SKILL.md lines 42/162 legitimately
  keep the stub-router pointer.

## Counterweight Pass

- Real blocker folded now: the MAJOR fence escape (act-before-ship at an
  irreversible boundary).
- Reverted mid-slice: the question-exemption advisory (F2). It was a purely
  additive visibility nicety, but doing it without duplication needs a shared owner
  the two carriers (`check_issue_closeout_commit_msg` and `issue_close_comment_floor`)
  both import; the dup-ratchet correctly blocked the copy. Respecting the gate over
  bypassing it dogfoods the PR's own new mechanism. Deferred as D36.
- Deferred, not dropped: the announcement same-observer self-attest (D34) and the
  release probe shape-match (D35) are disclosed-residual P4-*depth* items whose
  tightening changes what passes at an irreversible boundary and needs its own
  critique cycle — rushing them into a pre-release commit is itself the
  boundary-regression risk the north star warns against.
- Not a defect: the new-gate advisory's top-level `scripts/` scope is
  documented-intentional (conservative-probe miss), not a bug.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/check_issue_closeout_commit_msg.py:83 | action: fix | note: bare-close path no longer fence-strips the commit message, so a fenced close keyword that GitHub still auto-closes now trips the floor; regression test added and reproduced
- F2 | bin: valid-but-defer | evidence: moderate | ref: scripts/check_issue_closeout_commit_msg.py | action: defer | note: question/decision-needed exemption advisory authored then reverted because dup-ratchet blocked it as P2 duplication; needs a shared owner both carriers import, deferred to D36
- F3 | bin: bundle-anyway | evidence: moderate | ref: skills/public/achieve/SKILL.md:91 | action: fix | note: stale Remaining Boundary Matrix pointer moved from the lifecycle.md stub to its single owner goal-artifact.md
- F4 | bin: valid-but-defer | evidence: moderate | ref: skills/public/announcement/scripts/record_announcement.py | action: defer | note: same-observer self-attested confirmed for an external write is a P4-depth independence gap needing its own critique cycle, deferred to handoff
- F5 | bin: valid-but-defer | evidence: weak | ref: skills/public/release/scripts/publish_release_post_create.py:106 | action: defer | note: distinct-channel probe shape-match is loose against near-identical same-proxy commands; disclosed residual, deferred to handoff
- F6 | bin: over-worry | evidence: weak | ref: scripts/slice_closeout_advisories.py:334 | action: defer | note: new-gate advisory scoped to top-level scripts/ is a documented-intentional conservative-probe miss, not a defect

Fresh-eye satisfaction: parent-delegated — a fresh-eye subagent (general-purpose, id a8a8144d0e05046a3) adversarially reviewed the fix diff and returned CLEAN (no blocker, no residual boundary escape; it independently reproduced the fix and re-ran the gate suite). The shipped change is a strict subset of what it reviewed (F2/advisory reverted afterward for the dup-ratchet block), so its per-axis CLEAN findings for the MAJOR fence fix (axes A/B) and the achieve pointer (axis D) fully cover what ships.

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye subagent in a different agent context, adversarial, read-only in the shared parent worktree
- Requested spawn fields: the full fix diff scope, the three findings, and six adversarial verification axes (A-F: residual escape, false-positive regression, advisory additivity, pointer accuracy, mirror parity, test count)
- Host exposure state: applied
- Application state: host-confirmed: subagent a8a8144d0e05046a3 ran to completion and returned verdict CLEAN with per-axis commands and observations
