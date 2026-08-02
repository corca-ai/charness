# Charness Handoff

## Workflow Trigger

- **No goal is waiting.** The last one completed: pushed, #477 closed, all seven
  #478 sites dispositioned. Pick from `## Next Session`, or shape one with
  `/achieve <outcome>`.

## Continuation Capability

- **The round that reads the REPAIRS is where the class comes back — four times
  measured, and the last is the sharpest.** The fix for "a documented command
  that cannot run" shipped three NEW documented commands that cannot run: bare
  paths to shims that ship mode 100644. A whole session on that class, and it
  still recurred inside its own repair.
- **A claims reviewer finds a different class than a code reviewer — now a
  standing contract step, and it proved itself on its first outing.** It found
  five record blockers four code rounds had not: an evidence line bound to its
  own record, a section saying NOT APPLIED after the edits shipped, CI
  attribution naming no SHA, every slice row still `pending`, and a
  "all reviewers clean" sentence written before the last reviewer returned.
- **A test can assert a proxy instead of the thing.** `assert "--strict" not in
  source` matched the docstring explaining that flag's absence. Read the real
  parser. Same family as "build fixtures from the source constant".
- **The dup ratchet re-fires after a refactor** — running it at the first edit
  is necessary, not sufficient; restructuring rotates the fingerprints.

## Current State

- `main` is at `727cbf40`, pushed, CI green on every pushed SHA. The path check
  is an ARMED blocking gate (`--strict` in run-quality), `<authoring-repo>/` is
  split out of `<repo-root>/`, and the closeout-claims review is a standing
  contract step. Re-check with `gh run list --limit 3`.
- The combined-status API reports `pending` / `total_count: 0` for every commit
  here because this repo publishes check-runs, not legacy statuses. Not a real
  pending; do not read it as one.
- **The 13 broken shipped commands are repaired and pinned**, in BOTH the
  authoring tree and the shipped mirror — different trees, and the inherited
  measurement had only seen one. Recount with
  `python3 scripts/inventory_skill_script_references.py --repo-root .`
- **The accumulation mechanism is the durable finding**, not the count:
  `<repo-root>/` was the link gate's own documented escape, so the escape hatch
  and the typo were the same token. `<authoring-repo>/` now splits them.
- Still open and untouched: the **E-cluster**, D41–D49,
  `parse_created_date`'s uncorroborated consumers.

## Next Session

1. **#478 is closable and not closed.** All seven sites are dispositioned and
   applied; the grant covered conversions, never the close. It needs its own
   carrier and ledger, exactly as #477 got.
2. **The `parents[3]` family is correct by coincidence.** Ten occurrences resolve
   in both layouts only because the exporter's flattening cancels the
   `plugins/<pkg>` prefix, and an eleventh (`skill_runtime_bootstrap.py:103`,
   `parents[4]`) is already wrong but unreachable. Revisit trigger: **any change
   to `export_plugin.py`'s skill-tier layout** turns all of them into #477 at
   once.
3. **#475's behavioural half is still an OPEN operator decision.** Nobody has
   observed an agent ask-and-spawn in a repo that never ran `setup`.

## Discuss

- **External side-effect approval expired with the completed goal.** Push,
  issue-filing, and issue-closing each need a fresh grant.
- **The path check is now a BLOCKING gate.** Its own two review rounds shipped
  four false-positive/false-negative classes before it was safe, and the
  "false positives are structurally impossible" argument was wrong and is
  retracted. If CI refuses on it, read the refusal; do not disarm it.
- **Open: which spelling of the delegation contract wins for EXISTING
  consumers.** Widening the markers flips every already-set-up repo at once,
  against a population this tree cannot count — what D49 forbids.
- **A read-only check and an irreversible boundary deserve different teeth** —
  D48 left `drift` alone and refused at publish; still open for other gates.

## References

- [completed goal](../charness-artifacts/goals/2026-08-03-push-the-armed-gate-and-close-477-through-its-carrier.md) · [its retro](../charness-artifacts/retro/2026-08-02-push-the-armed-gate-and-close-477-through-its-carrier.md) · [prior goal](../charness-artifacts/goals/2026-08-03-repair-the-commands-the-skills-tell-agents-to-run.md) · [retro](../charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md) · [the sweep](../charness-artifacts/audit/2026-08-02-can-this-rule-fire-sweep.md)
- [deferred decisions](./deferred-decisions.md) (D45–D49) · [north star](./design-north-star.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md)
