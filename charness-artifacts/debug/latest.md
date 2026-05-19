# Issue 176 Debug Review
Date: 2026-05-19

## Problem

`issue resolve` can finish repo work without a machine-checkable verifier that
the auto-close carrier or fallback ledger exists for every selected issue.

## Correct Behavior

Given an operator asks Charness to resolve GitHub issues end-to-end, when the
workflow reaches commit, push, or PR closeout, then a repo-owned verifier should
prove that every selected issue has either a GitHub auto-close carrier with a
classification-specific closeout ledger or an explicit manual-fallback reason
after remote verification.

## Observed Facts

- GitHub issue #176 reports that `corca-ai/ceal` issue resolution on
  2026-05-19 produced direct-to-main commits `7fe6d423` and `2fda41ca`
  without close keywords or closeout ledgers; issues #110-#112 stayed open
  until manual recovery.
- The issue skill already says to prefer explicit close keywords in a PR body
  or direct-to-default commit body and use `issue_tool.py close-with-comment`
  only after auto-close is unsupported or fails after remote verification.
- `skills/public/issue/scripts/issue_tool.py` exposes `close-with-comment`,
  `preflight`, `select`, `resolve-target`, `resolve-invocation`, and
  `brief-path`, but no command audits a PR body, commit body, or manual
  fallback ledger before final closeout.
- `skills/public/release/scripts/release_issue_closeout.py` already implements
  a narrower sibling for release helper flows: it adds `Close #...` lines,
  verifies issue state after publication, and records carrier/manual fallback.
- Closed issue #173 is a same-class prior incident for release/direct work
  leaving an issue open; #176 narrows the miss to the remaining prose-only
  issue-resolve closeout path.

## Reproduction

Static reproduction:

1. Read `skills/public/issue/SKILL.md` step 10 and
   `skills/public/issue/references/closeout-discipline.md`.
2. Read `skills/public/issue/scripts/issue_tool.py`.
3. Observe that the prose requires auto-close carrier verification, but the
   `issue_tool.py` command surface has no verifier for commit/PR/manual
   closeout carriers.

## Candidate Causes

- Prose-only enforcement: the issue skill describes the required carrier, but
  no command makes it a finalization gate.
- Partial sibling coverage: the release helper fixed release-linked issue
  closeout, but ordinary issue-resolve direct/PR work kept relying on agent
  memory.
- Too-narrow close helper: `close-with-comment` verifies manual close state but
  does not verify whether manual close was justified by a failed or unsupported
  auto-close carrier.

## Hypothesis

If the missing prevention surface is a repo-owned issue closeout verifier, then
adding an `issue_tool.py verify-closeout` command with tests for direct commit
carriers and manual-fallback ledger requirements should turn the repeated
omission into a deterministic pre-closeout failure.

## Verification

Pending implementation:

- Add focused tests for `verify-closeout` failing when selected issues lack
  `Close #...` lines in the direct commit body.
- Add focused tests for manual fallback requiring an explicit fallback reason
  and closeout summary.
- Run the focused issue tests and the repo slice closeout gate.

## Root Cause

The structural cause is that Charness encoded the desired GitHub auto-close
behavior as public-skill prose but did not provide an executable issue-resolve
finalization verifier outside the release helper path.

## Detection Gap

- `tests/quality_gates/test_issue_closeout_discipline.py` | asserted wording
  in the skill and references, but did not exercise a command that rejects a
  missing carrier | add command-level tests for selected issues and carrier
  sources.
- `skills/public/issue/scripts/issue_tool.py` | can close manually and verify
  final state, but cannot audit whether auto-close was attempted first | add
  a verifier command that classifies `direct_commit`, `pr_body`, and
  `manual_fallback` carriers.
- Release helper tests | prove the release-specific sibling only | keep as
  sibling evidence, but do not treat it as ordinary issue-resolve coverage.

## Sibling Search

- Mental model: once the public skill says "use close keywords", a diligent
  agent will remember to carry the rule into commit/PR closeout.
- Same layer: `skills/public/issue/scripts/issue_tool.py` direct issue-resolve
  finalization | decision: same bug, fix now | proof: static scan plus issue
  body evidence.
- Abstraction up: public-skill closeout rules backed only by wording tests |
  decision: same class, diagnostic-only for this slice | proof: static scan
  of `test_issue_closeout_discipline.py`.
- Specialization down: `skills/public/release/scripts/release_issue_closeout.py`
  release-linked closeout | decision: intentional implemented sibling, do not
  rewrite now | proof: local tests and code inspection.
- Adjacent operation: manual `issue_tool.py close-with-comment` | decision:
  same class, diagnostic-only for this slice because it verifies final state
  but not fallback legitimacy | proof: static scan.
- Keyword-only non-instance: broad `closeout` mentions in quality, critique,
  and retro artifacts | decision: intentional plain-text or non-rendering
  boundary | proof: static scan only.

## Seam Risk

- Interrupt ID: issue-176-closeout-verifier
- Risk Class: operator-visible-recovery, contract-freeze-risk
- Seam: GitHub issue lifecycle after local commit/push/PR work
- Disproving Observation: a pushed commit or PR body without close keywords can
  still leave GitHub issues open even when local tests pass.
- What Local Reasoning Cannot Prove: whether GitHub auto-close actually fired
  until remote issue state is queried.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Add a small executable verifier to `issue_tool.py` and document it in the
issue-resolve closeout path so missing close keywords or manual-fallback
justification fail before the workflow reports success.
