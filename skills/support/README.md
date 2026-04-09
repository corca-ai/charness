# Support Skills

`skills/support/` is for harness-owned tool-usage guidance, not public workflow
concepts.

## Current Layout

- `generated/`: machine-generated wrapper or reference material created by the
  control plane

## Rules

- do not put public workflow concepts here
- prefer upstream consumption plus manifests when the external repo already
  ships a usable support surface
- generated reference artifacts may live here even when `charness` does not own
  a local `SKILL.md`
- generated wrappers or references should be regenerated through
  `scripts/sync_support.py` instead of edited by hand
