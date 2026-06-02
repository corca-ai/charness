# Debug: #279 Achieve Activation Discussion Closeout
Date: 2026-06-02
Issue: #279

## Problem

An `achieve` Before-phase artifact can pass `--pursue-ready` when it has a
non-empty `Discuss before activation:` summary, while the operator-facing
closeout can still present the artifact as ready without resolving or asking
about those discussion items in the transcript.

## Correct Behavior

Given a shaped goal with consequential activation decisions, when the
Before-phase closes out, then the user must see those decisions before
activation and the assistant must not imply that `discussion_summary_present`
means the discussion has been completed.

## Observed Facts

- Issue #279 reports a Ceal goal-shaping run where the artifact recorded
  activation discussion items, but the assistant reported readiness instead of
  continuing the discussion.
- `goal_artifact_discussion.py` returns `discussion_ready: true` when a
  consequential goal has a non-empty `Discuss before activation:` summary.
- `goal_artifact_lib.pursue_readiness()` currently reports the true case as
  "safe to pursue via `/goal`", which can be read as resolved rather than
  surfaced.
- `achieve` guidance requires a discussion summary before readiness, but does
  not make the transcript-resolution obligation explicit enough at closeout.

## Reproduction

Create a goal body with a consequential decision and a non-empty
`Discuss before activation:` line, then run:

```bash
python3 skills/public/achieve/scripts/check_goal_artifact.py --repo-root . \
  --goal-path <goal> --pursue-ready
```

The helper reports `pursue_ready: true` and a readiness reason that does not
warn that the summary is not proof of resolved discussion.

## Candidate Causes

- Helper semantics: `discussion_ready` means "summary is present" but reads like
  "human discussion completed".
- Closeout wording: `achieve` guidance asks for a summary but does not require
  resolving or asking about the items before reporting readiness.
- Test gap: existing tests cover hidden or empty summaries, not the
  surfaced-but-unresolved closeout interpretation.

## Hypothesis

If `pursue_readiness()` exposes a separate human-facing activation-discussion
warning when consequential discussion is required, and `achieve` closeout
guidance says to resolve or explicitly ask about the items before offering
activation, then operators can no longer treat `discussion_summary_present` as
discussion completed.

## Verification

- Planned: focused pytest in `tests/quality_gates/test_goal_artifact_lib.py`
  for helper output that distinguishes surfaced discussion from resolved
  discussion.
- Planned: focused pytest in `tests/quality_gates/test_achieve_before_activation.py`
  for closeout guidance requiring transcript resolution before activation.
- Planned: CLI proof for `check_goal_artifact.py --pursue-ready` after the
  helper change.

## Root Cause

The contract encoded the deterministic floor ("discussion summary exists") but
not the human collaboration obligation ("discussion items are resolved or asked
about before readiness is reported"). The helper and prose used readiness
language that made the floor look like completion.

## Invariant Proof

- Invariant: `discussion_summary_present` proves only that activation decisions
  were surfaced in the artifact; it must not be presented as proof that the
  user-facing discussion is resolved.
- Producer Proof: focused tests will pin helper output and `achieve` guidance.
- Final-Consumer Proof: the final goal closeout must show `check_goal_artifact`
  output and the changed guidance that future operators read.
- Interface-Shape Sibling Scan: helper JSON fields, Before-phase response text,
  lifecycle reference text, and tests were identified as the related surfaces.
- Non-Claims: no live replay of the original Ceal transcript is planned.

## Detection Gap

- surfaced-but-unresolved discussion | tests only checked summary presence or
  absence, not whether helper/guidance warned that summary presence is not
  resolution | add focused helper and prose tests.

## Sibling Search

- Mental model: deterministic artifact readiness was mistaken for human
  collaboration completion.
- helper-output axis: `pursue_readiness()` reason can imply activation safety;
  decision: add explicit warning/separate field; proof: focused test.
- prose-closeout axis: `achieve`/lifecycle closeout can omit transcript
  resolution; decision: require resolve-or-ask before readiness/activation;
  proof: focused test.
- host-transcript axis: host runtimes execute the conversation, not this helper;
  decision: do not claim host enforcement; proof: non-claim in goal artifact.

## Seam Risk

- Interrupt ID: issue-279-achieve-activation-discussion-closeout
- Risk Class: none
- Seam: none
- Disproving Observation: none
- What Local Reasoning Cannot Prove: whether a future host transcript follows
  the guidance without a live replay.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/goals/2026-06-02-279-achieve-activation-discussion-closeout.md

## Prevention

Pin the distinction between "discussion surfaced" and "discussion resolved" in
both helper output and `achieve` closeout guidance, with synthetic fixtures
rather than private Ceal context.
