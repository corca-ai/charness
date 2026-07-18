# Release issue close evidence ordering Debug
Date: 2026-07-19

## Problem

The release helper claims distinct-channel evidence is recorded before a
release-linked GitHub issue closes, but the initial release commit already
carries `Close #N` and is pushed to the default branch before the release is
created or independently observed.

## Correct Behavior

Given a release-linked issue, when publication and a distinct observer are not
yet proven, then no default-branch commit carrying its close keyword is pushed.
The evidence record must be shared first; only a later carrier push may close
the issue, followed by a separate state readback.

## Observed Facts

- `_commit_release_artifact` builds the initial release commit from the validated
  closeout paragraphs, including `Close #N`.
- `_publish_and_finalize` pushes the branch and tag before `create_release`,
  backend verification, distinct-channel verification, install refresh, and
  observer persistence.
- The later `ensure_release_issues_closed` call is not the earliest close
  mutation: GitHub can auto-close on the earlier default-branch push.
- This is an internal control-flow defect with no external error string; source
  ordering and the fake Git/GitHub event log are the authoritative evidence.

## Reproduction

Use the existing release fake backend with `--close-issue 44`. Its event log
shows a release commit body containing `Close #44`, then `git push origin main
vX`, and only afterward release creation and distinct-channel observation.

## Candidate Causes

- The explicit `ensure_release_issues_closed` call closes too early.
- The initial release commit is incorrectly serving both publication and
  post-publication issue-carrier roles.
- GitHub does not auto-close from a pushed default-branch close keyword.
- The observer exists in the worktree early enough to be durable before push.

## Hypothesis

- confirmed candidate: splitting publication and issue-carrier commits will
  move the only close-keyword push after a shared observer/evidence commit;
  disconfirmer: any event trace still shows a default-branch close keyword before
  distinct-channel proof or evidence persistence.

## Verification

- confirmed — `publish_release_execute.py` pushes the initial close-keyword
  commit before calling `run_release_closeout_tail`.
- confirmed repair — initial release commits contain no close keywords; focused
  integration tests exercise observer-bearing carrier order, failures before
  and after remote receipt, post-carrier readback recovery, final-push recovery,
  and refusal of evidence-free lookalike commits.

## Root Cause

One commit was assigned two incompatible lifecycle roles: immutable release
content and post-publication issue closure. Because the tag/branch publication
phase pushes that commit, the later observer floor cannot govern the actual
earliest close boundary.

## Invariant Proof

- Invariant: when the distinct observer produces release evidence, the release
  workflow must push that evidence before any default-branch carrier can close a
  linked issue, and must read GitHub state after the carrier push.
- Producer Proof: `test_release_distinct_channel.py` proves the release-content
  commit omits close keywords and the observer-bearing carrier is produced first.
- Final-Consumer Proof: `test_release_publish_resilience.py` proves remote SHA,
  carrier artifact/observer content, issue-state readback, and final artifact
  recovery across both sides of ambiguous pushes.
- Interface-Shape Sibling Scan: normal publish and resume both call the shared
  closeout tail; release-verification failure already commits evidence without
  attempting issue close.
- Non-Claims: a fake backend proves ordering, not GitHub availability or webhook
  timing; public behavior remains verified by the release helper's readback.

## Detection Gap

- release ordering tests | asserted the explicit close call followed the
  observer but did not inspect the earlier close-keyword branch push | add an
  event-log assertion over commit body, evidence push, carrier push, and state
  readback

## Sibling Search

- Mental model: the named mutation call was mistaken for the earliest
  irreversible effect; data-bearing commits can mutate external state on push.
- same layer: normal publish | decision: same bug, fix now | proof: static call
  trace plus fake event log
- same layer: resume publish | decision: same bug, fix now through the shared
  closeout owner | proof: shared-tail call trace
- abstraction up: release verification failure | decision: intentional
  non-closing boundary | proof: artifact commit has no successful closeout path
- cross-file: `skills/public/release/scripts/publish_release_resume.py`

## Seam Risk

- Interrupt ID: release-issue-close-evidence-ordering
- Risk Class: external-seam
- Seam: git default-branch push -> GitHub issue auto-close -> release observer
- Disproving Observation: a close-keyword branch push before durable distinct
  evidence
- What Local Reasoning Cannot Prove: GitHub's delivery timing after ref update
- Generalization Pressure: factor-now

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-07-19-release-close-evidence-ordering.md

## Prevention

Separate publication and issue-carrier commits, persist a typed pending-close
record before the carrier push, and test the earliest external effect rather
than only the explicitly named close function.

### Verification-Lock Follow-up

- Observation: the first full locked suite exposed four resume/delta failures
  after 4,912 passes. A one-commit fixture had no `HEAD^`, and a release commit
  without a tag had no `HEAD^^`; both are valid partial states, not corrupt repos.
- Hypothesis: ancestry used for optional phase classification was being resolved
  as mandatory state. Disconfirmer: a seed-only or one-parent partial release
  still exits through raw `git rev-parse` failure instead of a typed resume refusal.
- Repair: optional ancestor probes now return absence, and grandparent lookup is
  skipped unless a tag makes the final-carrier phase possible. Delta failure
  injection moved to the shared delta owner and retains command/exit diagnostics.
- Focused proof: the real-host-delta and resilience files pass 53 tests,
  including missing-tag reconstruction, remote-tag ambiguity, no-partial-state
  refusal, and forced NUL-diff failure.
- The second lock passed all 4,916 broad tests, then the changed-line consumer
  correctly rejected 29 unobserved failure/recovery lines across six release
  modules. Direct tests now exercise carrier evidence mismatch, ambiguous push
  receipt, dry-run recovery, issue-helper absence, YAML/summary compatibility,
  binary Git diagnostics, noncanonical object IDs, and all published-state
  ancestry refusals; no exclusion or baseline was added.
- Final locked proof passed the 73.0s broad suite, a focused release coverage
  producer, and the authoritative changed-line consumer with an empty blocking
  set. The real-process smoke is an explicit boundary-ratchet exemption because
  startup/`__main__`/exit behavior is the subject; all logic remains in-process.
