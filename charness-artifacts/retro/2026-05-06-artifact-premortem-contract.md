# Artifact And Premortem Contract Retro

Mode: session
Date: 2026-05-06

## Context

This slice changed the checked-in plugin export, artifact write-target helpers,
and premortem validation for downstream repos. It was triggered by repeated
consumer-repo confusion around hand-editing `latest.md` and blocked automatic
subagent premortems.

## Evidence Summary

- `python3 scripts/run_slice_closeout.py --repo-root . --ack-cautilus-skill-review`
- `./scripts/run-quality.sh --read-only`
- parent-delegated fresh-eye reviews for artifact pointers, premortem
  delegation, and over-tightening
- dogfood probes against `../ceal` for changed premortem validation and
  exported artifact resolver commands

## Waste

- The first implementation treated a repo-local helper path as if exported
  plugin skills could invoke it with the same `$SKILL_DIR` depth.
- The first premortem validator used global text matching, so domain words like
  `blocked` inside a parent-delegated artifact could be mistaken for blocked
  fresh-eye state.
- The helper initially defaulted to dated records, which could create stale
  current pointers for the common quality/debug update path.

## Critical Decisions

- Use `write_artifact_path` as the machine-readable contract instead of asking
  agents to remember when `latest.md` is a pointer or symlink.
- Treat repo `Subagent Delegation` as the explicit delegation request for named
  bounded review scopes, then require concrete `host signal:` or `tool signal:`
  only when fresh-eye satisfaction is actually blocked.
- Keep historical premortem cleanup separate from the default changed-artifact
  gate so old downstream records do not block unrelated work.

## Expert Counterfactuals

- Gary Klein would have asked which first-use path fails in a consumer repo
  before accepting a source-repo pass; that would have caught the exported
  plugin helper path earlier.
- Daniel Kahneman would have challenged the broad `blocked` text heuristic as
  an availability bias from the current bug report; parsing the specific
  Fresh-Eye Satisfaction status avoided that noisy rule.

## Next Improvements

- `workflow`: for exported plugin changes, run at least one command from
  `plugins/charness/...` against a consumer repo before closeout.
- `capability`: later add a current-pointer refresh helper for record writes so
  `update_current_pointer_after_write` becomes directly actionable.
- `memory`: keep this lesson in recent retro selection because export-path
  assumptions and broad text validators are recurring traps.

## Persisted

Persisted: yes `charness-artifacts/retro/2026-05-06-artifact-premortem-contract.md`
