# Auto Retro Missing Surfaces Closeout
Date: 2026-04-23

## Context

Auto-retro closeout triggered because issue #63 changed the checked-in plugin export surface via the retro public skill helper.

## Evidence Summary

- Issue #63 reported a consumer repo closeout crash when `.agents/retro-adapter.yaml` existed without `.agents/surfaces.json`.
- Focused regression tests now cover both no-trigger missing-manifest fallback and configured missing-manifest remediation.
- `run_slice_closeout.py --ack-cautilus-skill-review` and `./scripts/run-quality.sh` passed after plugin export and debug seam index sync.

## Waste

The helper had safe adapter defaults but evaluated surfaces before checking whether the defaults made surfaces unnecessary. The extra dogfood-review stop was useful, but it required an explicit recorded decision that the prompt-routing dogfood contract did not change.

## Critical Decisions

- Return `triggered: false` before git diff or surfaces loading when both auto-trigger lists are empty.
- Keep configured missing-manifest repos failing nonzero, but with JSON remediation instead of a traceback.
- Record the dogfood decision in the debug artifact instead of changing `docs/public-skill-dogfood.json`, because the public prompt-routing contract stayed stable.

## Expert Counterfactuals

- Gary Klein: test the consumer-repo precondition first as a recognition-primed cue; a no-config adapter should make surfaces loading suspect immediately.
- Daniel Kahneman: separate the salient traceback from the base-rate path. Most consumer repos without auto triggers should not pay the manifest requirement just because mature charness repos have one.

## Next Improvements

- workflow: when a helper has optional adapter fields, check the no-op branch before loading required repo manifests.
- capability: keep `check_auto_trigger.py` regression tests anchored on consumer repos, not only this repo.
- memory: preserve this as an operator-visible recovery seam in the debug artifact and recent lessons.

## Persisted

Persisted: yes via `skills/public/retro/scripts/persist_retro_artifact.py`.
