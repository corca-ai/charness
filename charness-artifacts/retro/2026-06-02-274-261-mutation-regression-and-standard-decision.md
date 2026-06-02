# #274 + #261 Mutation Regression And Standard Decision Retro

Date: 2026-06-02

## Context

Session retro for
`charness-artifacts/goals/2026-06-02-274-261-mutation-regression-and-standard-decision.md`.
The goal fixed #274's current scheduled mutation workflow failure and made a
bounded #261 disposition without turning it into a fresh survivor-hardening
campaign.

## Evidence Summary

- Goal artifact:
  `charness-artifacts/goals/2026-06-02-274-261-mutation-regression-and-standard-decision.md`
- Debug artifact:
  `charness-artifacts/debug/2026-06-02-274-mutation-workflow-tokei-dependency.md`
- Issue carrier:
  `charness-artifacts/issue/2026-06-02-274-261-mutation-workflow-recovery.md`
- Resolution critique:
  `charness-artifacts/critique/2026-06-02-274-261-mutation-workflow-recovery-resolution.md`
- Host probe:
  `charness-artifacts/probe/2026-06-02-274-261-mutation-regression-and-standard-decision.json`
- Final local proof:
  `python3 scripts/run_slice_closeout.py --repo-root . --verification-lock`
  completed successfully.

## Waste

- The first final broad gate failed because debug artifacts cited gitignored
  reproduction paths without same-line `<!-- reproduction-source -->` markers.
  This cost one broad rerun and was preventable by running the durability check
  before the first verification-lock attempt.
- The goal was marked `complete` before its after-phase evidence lines were
  bound. The deterministic gate caught it, but the closeout sequence should bind
  retro, host-probe, and disposition-review evidence before flipping status.
- The issue symptom named StrykerJS JSON, but the earliest failing workflow step
  was Python sample selection. The debug slice avoided a wrong code change, but
  the distinction still needed repeated narration in the carrier and critique.

## Critical Decisions

- Treated GitHub workflow logs as the source of truth for #274, not the issue
  summary's downstream missing-report text.
- Fixed the runner dependency setup by installing `tokei` before sampling
  instead of changing StrykerJS config, mutation thresholds, or selection policy.
- Left #261 open because the #274 evidence did not change the coordination-cues
  survivor policy boundary.
- Ran final `verification-lock` after the slice was stable, and reran it after
  the artifact durability fix so the broad gate result is clean.

## Expert Counterfactuals

- Gary Klein lens: start with the earliest disconfirming event in the workflow
  timeline. That would have made the missing `tokei` dependency the primary
  hypothesis immediately and prevented over-reading the JS report symptom.
- W. Edwards Deming lens: closeout evidence is part of the system, not
  paperwork after the system. Bind after-phase evidence before changing the goal
  status so the process cannot outrun its proof.

## Next Improvements

- applied: When debug artifacts cite local or gitignored reproduction files,
  run `check_spec_evidence_durability.py` before final verification-lock and
  mark reproduction paths on the same line as the cited path.
- applied: Bind `Retro:`, `Host log probe:`, and `Disposition review:` evidence
  before marking active achieve goals `complete`.
- applied: For mutation workflow failures, inspect job-step ordering and skipped
  steps before changing reporter configuration or mutation gate thresholds.
- deferred: Consider a separate diagnostic-reporting follow-up if post-fix
  mutation runs still summarize upstream sample failures as missing JS reports.

## Sibling Search

- same layer: debug artifacts that cite generated reports | decision: same
  waste, fix now | proof: current debug artifact and `latest.md` carry same-line
  reproduction-source markers.
- abstraction up: achieve closeout sequencing | decision: same waste, fix now |
  proof: this goal now binds retro, host-probe, and disposition-review evidence
  before final commit.
- specialization down: mutation summary wording | decision: valid but defer |
  proof: carrier and goal record it as a follow-up only if the dependency fix
  does not recover #274.
- mental-model sibling: downstream symptoms in GitHub issue comments | decision:
  same waste, fix now | proof: debug artifact records the earliest failing
  component and carrier avoids claiming StrykerJS misconfiguration.

## Persisted

Persisted: yes
`charness-artifacts/retro/2026-06-02-274-261-mutation-regression-and-standard-decision.md`
