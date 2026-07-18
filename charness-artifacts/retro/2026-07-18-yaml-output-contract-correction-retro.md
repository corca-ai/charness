# YAML Output Contract Correction Retro
Date: 2026-07-18

## Mode

session

## Context

The root `charness` CLI had already migrated its public structured output to
YAML, but public skill commands and the governing Cautilus preflight still
taught `--json`. The operator noticed the contradiction while this autonomous
improvement was in progress, so the slice expanded to repair the full live
instruction-to-helper boundary.

## Evidence Summary

- `AGENTS.md` and `skills/public/quality/references/cautilus-on-demand.md`
  prescribed `plan_cautilus_proof.py --repo-root . --json` before the fix.
- The focused contract suite compares YAML default/detail payloads with hidden
  legacy JSON payloads and checks that live owned documentation no longer
  teaches `--json`.
- Packet consumed:
  `charness-artifacts/retro/2026-07-18-yaml-output-contract-retro-packet.md`.

## Waste

The first implementation boundary followed the source family named by the
debug hypothesis—public skills—and missed a governing repo instruction that
was already visible in the session context. That required a second search,
implementation pass, mirror sync, and test pass after the operator correction.

## Critical Decisions

- Treat agent-facing repo instructions, public skill copyable commands, helper
  help, and plugin exports as one output-contract boundary.
- Keep hidden `--json` behavior temporarily as real JSON for existing parsers;
  migrate live instructions and help to YAML/`--detail` without rewriting
  historical evidence or provider-native JSON contracts.
- Do not run Cautilus merely because its planner instruction changed; the repo
  remains ask-before-run and no live evaluator proof was requested.

## Expert Counterfactuals

- Engelbart system-improving lens: model the operator language, agent method,
  and renderer/tool as one `(H + LAM + T)` unit. Starting with a live
  instruction scan across `AGENTS.md`, skills, references, and helper help
  would have exposed the Cautilus call before implementation began.

## Sibling Search

- same layer: live repo and public-skill copyable planner calls | decision: same bug, fix now | proof: the owned-command test covers AGENTS, active references, and source/plugin skill bodies
- abstraction up: CLI-authoring guidance in create-cli | decision: same bug, fix now | proof: the guidance now distinguishes agent-first YAML from native third-party contracts
- specialization down: hidden compatibility flags and persisted JSON artifacts | decision: intentional boundary | proof: compatibility tests require real JSON while live help hides the flag
- mental-model siblings: historical goal, critique, and Cautilus evidence quoting old commands | decision: diagnostic-only | proof: those records describe immutable past runs and are excluded from live-instruction enforcement

## Next Improvements

- workflow: begin output-format migrations with a live consumer-language scan
  spanning governing instructions, skills, references, help, and exports.
- capability: retain the focused owned-command and YAML-vs-hidden-JSON contract
  test so a future live `--json` instruction fails at authoring time.
- memory: persist this operator correction and its intentional historical/native
  exclusions so later scans do not confuse evidence preservation with drift.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-18-yaml-output-contract-correction-retro.md
