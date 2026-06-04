# Disposition Review: Nose duplicate refactoring

## Scope

Fresh-eye disposition review for the completed `nose` duplicate-refactoring goal,
focused on the final `jscpd` decision and whether the goal can close without
adding a hard `jscpd` gate.

## Findings

- No blocker: the evidence supports not adding `jscpd` as a hard gate in this
  goal.
- `jscpd` 4.2.4 source-only default scan remains useful, but the 87-clone report
  is dominated by short bootstrap, preamble, import, and adapter skeleton pairs,
  with a few real candidates mixed in.
- High-floor scans surface real but small follow-up candidates:
  `check_init_repo_rename.py` / `check_premortem_rename.py`,
  `report_usage_episodes.py` / `validate_usage_episodes.py`, and a small
  resolver/bootstrap/dogfood-helper inventory at a slightly lower floor.
- The one docs-only `jscpd` clone is Achieve goal artifact/template mirroring,
  not a replacement for whole-file document near-copy detection.

## Disposition

Proceed with the recorded outcome: `jscpd` is meaningful advisory code-clone
signal, but adoption should start later as a labelled quality support-binary
candidate with command/options, a reviewed baseline or threshold policy, and
portable-bootstrap handling before any no-increase or hard-fail wiring.
