# Issue #433 Release Closeout Carrier Debug
Date: 2026-07-11

## Problem

`publish_release.py --close-issue 433` constructs a release commit carrying
`Close #433.` that the repo's own commit-msg gate deterministically rejects,
but only after the release-quality phase has already run.

## Correct Behavior

- Given an issue-close carrier requested through the release helper,
- when the helper preflights the exact final commit message,
- then the issue-owned closeout consumer and commit-msg gate accept it before
  expensive release quality or mutation begins.
- Capability restored: one release command can publish a gate-valid closeout
  carrier without a doomed quality run or a hand-authored workaround commit.

## Observed Facts

- GitHub #433 is OPEN and `comments_read: true`; its reported failures name
  missing `jtbd`, `root_cause`, `debug_artifact`, `siblings`, `prevention`,
  critique, and AI-provenance fields.
- `release_commit_body` emits release/quality lines, `Close #N.`, and optional
  behavior lines (`skills/public/release/scripts/release_issue_closeout.py:136`).
- `_commit_release_artifact` converts each emitted line to a `git commit -m`
  paragraph (`skills/public/release/scripts/publish_release_execute.py:107`).
- The commit-msg consumer treats an unbacked close keyword as a bug carrier and
  calls the issue verifier (`scripts/check_issue_closeout_commit_msg.py:129,176`).

## Reproduction

- Loaded `release_commit_body`, generated the exact paragraph body for #433,
  and passed that body to `check_issue_closeout_commit_msg.evaluate` in the
  current repo. Result: `status=failed`; behavior passed, while five bug-ledger
  fields, resolution critique, and AI provenance were missing.
- Focused component proof also passed: the release generator emits the thin
  carrier, the bare-keyword gate rejects thin carriers, and closeout-draft
  validation rejects a missing ledger (`3 passed in 0.55s`).

## Candidate Causes

- Control flow: the exact carrier is not validated before release quality and
  commit mutation.
- Contract drift: the release producer and issue-owned consumer evolved under
  separate schemas, with no shared renderer or compositional parity test.
- Classification: omission of `Classification:` forces the strict bug ledger;
  adding classification alone could reduce some errors but cannot satisfy any
  close-intended issue's full ledger.
- Environment/provider: GitHub state or auth could fail later, but neither can
  explain a deterministic local commit-msg rejection of the generated body.

## Hypothesis

- Falsifiable claim: the helper's unmodified output fails the final consumer
  even when GitHub state and the behavioral verdict are valid; a complete
  issue-owned carrier validated before quality is the missing interface.
  | disconfirmer: feed the exact generated body directly to the commit-msg
  evaluator before changing production code.

## Verification

- confirmed — the direct producer-to-consumer probe returned `ok=false` with
  `bare_close_numbers=[433]`; `behavioral_verdict.ok=true`, isolating the
  missing closeout ledger rather than provider, auth, or behavior-line causes.
- Causal chain: commit rejected -> exact body is a thin close carrier -> the
  gate correctly applies irreversible-boundary floors -> release preflight
  validates provider state/behavior but not the final carrier -> no shared
  producer/consumer validation or stitched regression prevented contract drift.

## Root Cause

The release helper owns a hand-built subset of the issue closeout message while
the commit-msg hook owns the complete carrier contract. The bare-keyword floor
made the hook correctly reject incomplete carriers, but the release producer
was not routed through that final-consumer validator before expensive work.
Structural cause: split ownership without an executable interface contract at
the producer boundary.

## Invariant Proof

- Invariant: when the release producer emits an issue-closing commit message,
  the issue-owned final consumer must accept that exact message before release
  quality or repository mutation can claim readiness.
- Producer Proof: local `release_commit_body` probe emitted `Close #433.` plus
  the requested behavior line and no closeout ledger.
- Final-Consumer Proof: `check_issue_closeout_commit_msg.evaluate` rejected that
  exact output with the full missing-field report.
- Interface-Shape Sibling Scan: searched close-keyword producers, closeout-draft
  validators, release preflights, manual close carriers, and current-pointer
  scaffold producers across `skills/public/` and `scripts/`.
- Non-Claims: no live release, push, GitHub close, provider mutation, installed
  plugin, or generated mirror roundtrip ran; all proof is local source/fixture.

## Detection Gap

- generator test (`test_release_issue_closeout_behavioral_floor.py:138`) |
  asserts `Close` and behavior presence but not final-consumer acceptance |
  stitch the generator output into the issue-owned draft/commit-msg consumer.
- release preflight (`release_issue_closeout.py:159`) | checks behavior and
  GitHub issue state only | validate the exact final carrier before quality.
- commit-msg hook (`.githooks/commit-msg:7`) | fires correctly, but only after
  the expensive release phase | reuse its owner contract in early preflight.

## Sibling Search

- Mental model: a producer-local presence check is treated as proof that a
  downstream owner will accept the emitted carrier.
- same layer: `release_commit_body` is the only Python close-keyword generator
  found | decision: same bug, fix now | proof: local payload proof.
- specialization down: preflight validates behavior/state but not the message
  passed to `git commit` | decision: same bug, fix now | proof: local payload proof.
- abstraction up: debug scaffold returned a resolved `latest.md` symlink target
  as the write path for a fresh investigation | decision: same class,
  diagnostic-only for this slice; active goal Slice 2 owns disposition |
  proof: local payload proof.
- mental-model sibling: release manual fallback closes through a post-release
  API/state-verification path, not the commit-msg consumer | decision:
  intentional plain-text or non-rendering boundary | proof: static scan only.
- cross-file: `scripts/check_issue_closeout_commit_msg.py` and
  `skills/public/debug/scripts/scaffold_debug_artifact.py` are structural
  consumer/path siblings outside the release producer.

## Seam Risk

- Interrupt ID: issue-433-release-closeout-carrier
- Risk Class: contract-freeze-risk
- Seam: release producer -> git commit paragraphs -> issue closeout verifier
- Disproving Observation: exact generated payload fails locally before GitHub
- What Local Reasoning Cannot Prove: live release/provider/installed behavior
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/debug/2026-07-11-issue-433-release-closeout-carrier.md

## Prevention

Route a complete issue-owned closeout carrier through the final consumer before
expensive release work, add one stitched regression that proves the old output
fails and the accepted carrier passes, and keep release source plus generated
plugin mirrors synchronized. Do not weaken the commit-msg floor or synthesize a
second closeout schema inside release.
