# Session Retro: Evidence Panel Adaptation

## Context

This session adapted the gathered expert-panel prompt lessons into `charness`
skill guidance. The important surface was not runtime behavior; it was keeping
the public skill core portable while making review outputs more evidence-aware.

## Evidence Summary

- `charness-artifacts/gather/latest.md`
- `python3 scripts/check_auto_trigger.py --repo-root .`
- `python3 scripts/run-slice-closeout.py --repo-root .`
- Current diff across source skill references and checked-in plugin export

## Waste

- `quality/SKILL.md` initially took the authority-only guidance directly in the
  public core. `validate-skills` caught that the core had grown too long, so the
  detail moved into `quality/references/quality-lenses.md`.
- I used a broad `find ..` to locate the auto-retro helper and hit unrelated
  permission-denied paths. The repo-local script path was already knowable from
  `skills/public/retro/scripts/`.

## Critical Decisions

- Kept evidence-strength guidance in references rather than creating a new
  public mode or heavier panel workflow.
- Preserved generated export sync by running `sync_root_plugin_manifests.py`
  and then `run-slice-closeout.py`.
- Used the EBP/PBE lesson as a small falsifiability improvement: non-automatable
  quality recommendations now ask for a minimum experiment or review loop.

## Expert Counterfactuals

- John Ousterhout would have pushed the authority-only rule out of
  `quality/SKILL.md` immediately: the core should select and sequence, while
  reference files carry nuance.
- Gary Klein would have asked earlier what the next maintainer is likely to do
  wrong under pressure. The answer was "copy reference implementations too
  literally," so the Core Practice / Peripheral Practice distinction belongs in
  provenance and integration guidance.

## Next Improvements

- workflow: when adapting external prompts into skills, start by naming which
  parts are core practice versus peripheral practice before editing.
- capability: consider a small validator or inventory for overlong public
  `SKILL.md` files before edits, not only after.
- memory: keep the export-sync and concise-core trap visible in recent retro
  lessons.

## Persisted

yes: `charness-artifacts/retro/2026-04-15-evidence-panel-adaptation.md`
