# closing four verified-resolved issues

Date: 2026-08-18

## Decision Under Review

Closing #629, #628, #608 and #528 as resolved by carriers that landed in earlier
sessions, on the strength of behavioral re-verification run today rather than a diff read.

## Failure Angles

- A close that lands is not undoable by pushing again, so a close claiming more than its
  evidence supports is the irreversible half of this decision.
- The verifications were run by the same agent that decided to close, so a probe shaped to
  the expected answer would confirm itself. This is what the fresh-eye round was for.
- Three of the four issues were broadened after filing — #628 by a comment, #528 by a
  second smaller instance in its own body — so a close reading only the title resolves a
  narrower issue than the one filed.
- Two issues name consumer repos this session cannot reach, so "the producer is fixed" and
  "the consumers are green" are different claims.

## Counterweight Pass

- The reviewer refuted one of my measurements outright and was right: I probed #528's
  resolver with `deliberately_absent` written as a LIST, which is not the vocabulary. With
  the MAPPING shape the resolver drops the declared sub-keys, so the half of #528 I had
  called still-open is closed by removal. The re-measurement is in F1.
- Two of my mechanism summaries were loose rather than wrong. For #628 I wrote that four
  families "return create_new_file for a different subject"; three of them reach that
  through a stronger rule (refuse ANY occupied record path), not through subject identity.
  The conclusion survives, the wording does not, so the close comments carry the mechanism
  the code actually implements.
- The residual gaps the reviewer found (bare links outside `## References`; the claims lane
  running no release-surface gate; a reference sample that still hard-indexes sub-keys a
  repo may now declare absent) are real but none of them is the issue's ask. They belong in
  the close as stated non-claims, not as reasons to hold the issue open.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/quality_bootstrap_absence.py | action: fix | note: my #528 resolver probe used a list-shaped `deliberately_absent`; re-measured with the mapping shape, the resolver drops the three sub-keys, and the close text was corrected before posting
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/references/coverage_floor_inventory.py | action: document | note: the shipped reference sample still hard-indexes `gate_script_pattern` and three thresholds, which traceback if a repo declares them absent; carried as a #528 non-claim
- F3 | bin: bundle-anyway | evidence: moderate | ref: skills/public/handoff/scripts/handoff_bullet_ownership.py | action: document | note: a bare markdown link still satisfies the ownership rule in `## Current State`/`## Next Session`, so #629 reduces link-only lines rather than proving zero
- F4 | bin: bundle-anyway | evidence: strong | ref: skills/public/release/scripts/publish_release_resume_publish.py | action: document | note: the claims lane deliberately runs no release-surface gate or focused adapter preflight; carried as a #608 non-claim
- F5 | bin: over-worry | evidence: moderate | ref: scripts/artifact_subject_identity.py | action: defer | note: #628's same-subject continue-in-place reads like residue but is designed and recorded, reachable only through an explicit matching title
- F6 | bin: valid-but-defer | evidence: weak | ref: charness-artifacts/critique/2026-08-18-closing-four-verified-resolved-issues.md | action: defer | note: the umbrellas #582/#583/#584 were NOT reviewed here and are not being closed; their children were never individually verified by this session

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer, read-only (Read/Grep/Glob), one round over all four closes.
- Requested spawn fields: subagent_type `bounded-reviewer`, no host addressing name, per-issue ask/verification/carrier packet inline in the prompt.
- Host exposure state: applied
- Application state: host-confirmed: the reviewer returned a per-issue verdict and reported `envelope-unbound: no`, naming Read/Grep/Glob as its only tools.
- Delivery state: findings-received
- Fresh-Eye Satisfaction: parent-delegated
- Reviewer boundary: snapshot/verify run around the review with `reviewer_boundary_fingerprint.py`.

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed; the reviewer was briefed inline with the
per-issue ask, verification and carrier. The binding floor is therefore off by construction
rather than by omission. -->

## Boundary Ownership

- Producer: the four carrier commits, landed in earlier sessions by other slices.
- Consumer: the GitHub issue tracker, and consuming repos that read the shipped surfaces.
- Owning surface: issue closeout.
- Verdict: owned-correctly

## References

- [issue closeout discipline](../../skills/public/issue/references/closeout-discipline.md) — the verified ledger, behavior verdict and final state proof this close must clear.
- [fresh-eye subagent review](../../skills/shared/references/fresh-eye-subagent-review.md) — the bounded reviewer contract the round above ran under.
