# Cautilus Dogfood
Date: 2026-04-23

## Trigger

- slice: make the `premortem` subagent capability check reject shell-only
  runners, routing-only proof, and model self-report as evidence that the
  canonical bounded subagent path actually ran
- claim: improve

## Validation Goal

- goal: improve
- reason: the slice changes prompt-affecting `premortem` reference behavior so
  agents should attempt the bounded subagent path or report a concrete host
  spawn restriction instead of claiming a prose-only premortem succeeded

## Change Intent

- `prompt_affecting_change`
- `skill_reference_change`
- `dogfood_behavior_probe`

## Prompt Surfaces

- `skills/public/premortem/references/subagent-capability-check.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id premortem --json`
- custom probe: `node ./scripts/agent-runtime/run-local-instruction-surface-test.mjs ... --cases-file .artifacts/cautilus-experiments/premortem-spawn-probe-cases.json`

## Regression Proof

- instruction-surface summary: `3 passed / 0 failed / 0 blocked`
- run artifact: `.cautilus/runs/20260423T083229670Z-run/`
- maintained startup routing still bootstrapped through `find-skills`, then
  selected the expected durable work skills for the default instruction-surface
  cases

## Scenario Review

- before the reference change, the custom premortem probe reported
  `observationStatus: observed` and claimed bounded subagents were used while
  the actual runner trace only showed shell `exec`
- after the reference change and proof-only `charness update --repo-root .
  --no-pull --skip-cli-install`, the same probe reported
  `observationStatus: blocked`, `blockerKind: subagent-spawn-host-contract`,
  and the concrete host error `collab spawn failed: Fatal error: parent thread
  rollout unavailable for fork`
- this proves the intended behavior improvement for the current Codex runner:
  do not accept self-reported subagent use when the runtime cannot actually
  fork a bounded subagent

## A/B Compare

- baseline_ref: `HEAD`
- `cautilus workspace prepare-compare --repo-root . --baseline-ref HEAD --output-dir .artifacts/cautilus-experiments/premortem-ab-compare`
- `cautilus mode evaluate --repo-root . --mode held_out --intent 'Premortem subagent capability checks should block on missing spawn tooling instead of accepting shell-only self-report.' --baseline-ref HEAD --output-dir .artifacts/cautilus-experiments/premortem-mode-evaluate`
- report artifact: `.artifacts/cautilus-experiments/premortem-mode-evaluate/report.json`
- mode evaluate status: `defer`; held-out eval scenarios passed

## Outcome

- recommendation: `accept-now`
- routing notes: the default instruction-surface regression still passes, and
  the targeted premortem dogfood probe now blocks honestly on the host spawn
  contract instead of inventing a same-agent or self-reported premortem

## Follow-ups

- promote the custom premortem spawn probe into a maintained cautilus case once
  the instruction-surface runner can assert actual tool events or expected
  blocked host signals directly
