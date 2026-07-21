# v2.4.2 Real-Host Proof
Date: 2026-07-22

## Scope

Post-publication maintainer-machine proof for the v2.4.2 release-time
`external-tool-control-plane` trigger.

## Installed Charness Readback

- `charness version` reported `2.4.2`.
- `charness doctor` reported checkout and Codex cache version `2.4.2`, no source
  cache drift, and ready repository onboarding.
- The release helper's `charness update` refresh completed successfully before
  this readback; active Codex and Claude sessions still require restart to load
  their refreshed plugin state.

## Nose Checklist

- `charness tool doctor nose --no-write-locks`: ready, observed `0.19.0`.
- `charness tool install nose --dry-run`: successful script-route dry run; no
  global install was needed because `nose 0.19.0` was already available.
- `nose --version`: `nose 0.19.0`.
- `charness tool sync-support nose`: skipped, confirming that Nose is an
  integration-only binary with no materialized support-skill requirement.
- `inventory_nose_clones.py --summary`: two advisory clone families, 344
  reported duplicate lines; this is refactoring triage, not a quality failure.

## Disposition

The requested real-host checklist is evidenced on this maintainer machine.
This proves the recorded local installation and tool routes only; it does not
claim that every external host or package-manager environment behaves the same.
