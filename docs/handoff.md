# Charness Handoff

## Workflow Trigger

- **A goal is SHAPED and pursue-ready** — no activation question, because the
  standing approvals in `AGENTS.md` now cover it. Activate directly:
  `/goal @charness-artifacts/goals/2026-08-04-close-the-unreachable-file-class-and-widen-the-claims-round.md`

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
- **#477 and #478 are CLOSED**; their sites are repaired in both trees. Recount
  with `python3 scripts/inventory_skill_script_references.py --repo-root .`
- **Every retro must now carry `## North Star Alignment`** — validator-enforced,
  scaffold-seeded, grandfathered from 2026-08-03.
- **The accumulation mechanism is the durable finding**, not the count:
  `<repo-root>/` was the link gate's own documented escape, so the escape hatch
  and the typo were the same token. `<authoring-repo>/` now splits them.
- Still open and untouched: the **E-cluster**, D41–D49,
  `parse_created_date`'s uncorroborated consumers.

## Next Session

1. **The waiting goal owns #479 and the claims-round widening.** Read it rather
   than re-deriving its slices here.
2. **#479 is the enclosing class #477/#478 were sub-forms of** — eleven-plus
   confirmed live instances, including broken links in the shipped mirror that
   `check_doc_links` never scans. Every prior pass reported an honest zero with
   a ruler narrower than the class.
3. **#475's behavioural half is still an OPEN operator decision.** Nobody has
   observed an agent ask-and-spawn in a repo that never ran `setup`.

## Discuss

- **Issue creation is STANDING and push is standing CONDITIONAL ON THE GATES**
  (`AGENTS.md` `## External Side Effects`). Do not re-ask either. Issue close,
  PR, release, tag, version bump, and cautilus stay per-goal. Weakening a gate
  to reach a green push revokes the push approval.
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

- [waiting goal](../charness-artifacts/goals/2026-08-04-close-the-unreachable-file-class-and-widen-the-claims-round.md) · [completed goal](../charness-artifacts/goals/2026-08-03-push-the-armed-gate-and-close-477-through-its-carrier.md) · [its retro](../charness-artifacts/retro/2026-08-02-push-the-armed-gate-and-close-477-through-its-carrier.md) · [prior goal](../charness-artifacts/goals/2026-08-03-repair-the-commands-the-skills-tell-agents-to-run.md) · [retro](../charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md) · [the sweep](../charness-artifacts/audit/2026-08-02-can-this-rule-fire-sweep.md)
- [deferred decisions](./deferred-decisions.md) (D45–D49) · [north star](./design-north-star.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md)
