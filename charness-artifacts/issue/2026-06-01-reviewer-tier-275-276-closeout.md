# Reviewer Tier, Issue #275, and Issue #276 Closeout Carrier

Date: 2026-06-01
Repo: corca-ai/charness
Goal: `charness-artifacts/goals/2026-06-01-reviewer-tier-closeout-and-issue-275.md`

## Carrier Scope

Close:

- #275 Handoff chunker issue source silently drops open issues in installed
  plugin layout.
- #276 Achieve should surface consequential discussion points before goal
  activation.

## Close Comment

Resolved by the reviewer-tier closeout carrier.

JTBD: make Charness pickup and activation flows trustworthy in installed
plugin usage: handoff must see the configured live issue source, and achieve
must not present a structurally shaped goal as activation-ready while hiding
operator-significant defaults.

Classification: bug for #275 and #276.

Root cause: two runtime contracts were treated as structural conventions. For
#275, handoff cross-skill imports assumed source-tree public skill paths
(`skills/public/<id>/`) even though installed plugins flatten public skills to
`skills/<id>/`; the fallback swallowed import failures as an empty issue list.
For #276, achieve pursue-readiness treated placeholder removal as sufficient
even when activation decisions about live proof, issue closure, bundled scope,
side effects, or proof non-claims still needed to be visible to the operator.

Debug artifact: n/a — causal review is recorded in the goal and resolution
critique artifacts for this carrier.

Siblings: cross-skill public imports and structural-readiness gates | decision:
bundle the direct handoff-to-issue, handoff-to-achieve, and achieve
Before-phase activation-readiness fixes; defer broader runtime resolver
unification and unrelated support-skill topology risks | proof: fresh-eye
causal reviews plus final code critique in
`charness-artifacts/critique/2026-06-01-reviewer-tier-275-276-resolution.md`.

Prevention: installed-layout fixtures now cover `skills/<id>/` issue and
achieve lookups, issue-source diagnostics expose pre-provider and provider
payload failures through parse-to-propose flow, and
`check_goal_artifact.py --pursue-ready` now blocks consequential activation
decisions unless a non-empty current `Discuss before activation:` summary is
visible before the Slice Log.

Critique: charness-artifacts/critique/2026-06-01-reviewer-tier-275-276-resolution.md
Post-commit critique: charness-artifacts/critique/2026-06-01-reviewer-tier-275-276-postcommit-subagent-critique.md

Close #275.
Close #276.

Evidence:

- Goal artifact:
  `charness-artifacts/goals/2026-06-01-reviewer-tier-closeout-and-issue-275.md`
- Carrier artifact:
  `charness-artifacts/issue/2026-06-01-reviewer-tier-275-276-closeout.md`
- Resolution critique:
  `charness-artifacts/critique/2026-06-01-reviewer-tier-275-276-resolution.md`
- Post-commit subagent critique:
  `charness-artifacts/critique/2026-06-01-reviewer-tier-275-276-postcommit-subagent-critique.md`
- Final broad pytest: `1980 passed, 4 skipped in 271.87s`
- Post-critique focused regression tests:
  `115 passed in 4.07s`
- Final deterministic validators: packaging, docs, skill validation, Cautilus
  proof policy, critique artifacts, lint, length, attention-state visibility,
  public-skill validation, public-skill dogfood, and py_compile all passed.

## Non-Claims

- This carrier has not been pushed.
- GitHub issue state is not claimed closed until push/remote verification.
- No release is part of this carrier.
