# Session Retro
Date: 2026-07-09

## Mode

session

## Context

This retro covers the prompt-mutation step-7 slim follow-up goal. T1 and T2
landed the parentless snapshot and rewrite/sentinel tooling; T3 ran the
step-7 slim refresh experiment; T4 ended as no-apply because the transcript
sweep tainted every refreshed capture for the blinding claim.

## Evidence Summary

- Goal scratchpad:
  `charness-artifacts/goals/2026-07-09-prompt-mutation-step7-slim.md`
- Experiment report:
  `charness-artifacts/prompt-mutation/2026-07-09-step7-slim-experiment.md`
- Survival score:
  `charness-artifacts/prompt-mutation/2026-07-09-step7-slim-survival.json`
- Unblinding sweep:
  `charness-artifacts/prompt-mutation/2026-07-09-step7-slim-unblinding-sweep.json`
- Verification: `run_slice_closeout.py --verification-lock` passed for the
  T3/T4 artifact closeout. The duplicate ratchet initially hard-blocked on 8
  accumulated code families, then the final closeout slice resolved it with one
  extraction plus seven reviewed intentional classifications.

## Waste

The main waste was spending the full capture headroom before the blinding
observer model was enforced strongly enough. Parentless snapshots removed the
parent-diff channel, but the refresh task still performed legitimate git
history/ref probes, and the sweep only made that visible after all captures
were spent.

A smaller waste was artifact-surface drift: prompt-mutation JSON artifacts were
not covered by `.agents/surfaces.json`, so closeout initially blocked on
unmatched durable evidence files instead of validating them directly.

## Critical Decisions

- Treat the sweep as a real gate, not a caveat. This prevented a prose edit from
  shipping on tainted evidence even though sentinels passed and judges split.
- Keep the policy update despite no T4 prose edit. The policy now reflects T1/T2
  behavior that is already implemented: parentless snapshots, rewrite byte
  identity, and sentinel-vs-invalid outcomes.
- Add a prompt-mutation artifact surface instead of using `--allow-unmatched`;
  experiment evidence should parse at closeout like other durable artifacts.

## Expert Counterfactuals

- Engelbart system-improving lens: design the method and tool together before
  spending live captures. A stronger T-loop would have turned the pre-registered
  "captured agents can run git probes" concern into a pre-capture sandbox or
  denylist proof, not a post-hoc discovery.
- Direct decision-quality counterfactual: freeze the ship/no-ship rule and the
  disqualifying sweep probes in executable form before the run starts. The
  human rule existed, but the expensive evidence path still had to discover the
  blocking condition after the fact.

## Sibling Search

- same layer: `scripts/run_skill_efficiency_ab.py` capture harness | decision: valid follow-up outside the slice | proof: refreshed traces show every run can execute identity-relevant git history/ref probes | follow-up: deferred prompt-mutation blind-workspace guard
- abstraction up: `docs/prompt-mutation-policy.md` experiment-integrity floors | decision: same waste, fix now | proof: policy now names parentless capture snapshots, rewrite byte identity, and sentinel-vs-invalid outcomes
- specialization down: `charness-artifacts/prompt-mutation/*` evidence files | decision: same waste, fix now | proof: `.agents/surfaces.json` now declares `prompt-mutation-artifacts` with JSON parse verification
- mental-model siblings: future prompt-surface live experiments | decision: valid follow-up outside the slice | proof: this run shows sentinel/judge green can coexist with tainted observer behavior | follow-up: deferred prompt-mutation clean-proof preflight

## Next Improvements

- workflow: repo-local guard: prompt-mutation blind-workspace guard — before spending live prompt-mutation captures, require a preflight that either prevents identity-relevant git history/ref probes or declares the experiment tainted in advance.
- capability: repo-local guard: prompt-mutation clean-proof preflight — make the post-hoc sweep rules executable earlier so "sentinels green but observer tainted" is caught before capture headroom is exhausted.
- memory: applied: this retro plus the T3/T4 experiment report record that the sweep is a first-class ship gate, not an advisory footnote.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-09-session-retro.md
