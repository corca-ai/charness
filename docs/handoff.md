# Charness Handoff

## Workflow Trigger

- **A goal is SHAPED but deliberately NOT pursue-ready.** Its one open item is
  an operator grant: settle `## Discuss Before Activation` in
  [the waiting goal](../charness-artifacts/goals/2026-08-03-push-the-armed-gate-and-close-477-through-its-carrier.md)
  — push to `main`, close #477 via the commit carrier, comment on #478 — mark it
  resolved, then activate. `/goal` refuses until then; that refusal is the
  phase-scoped-approval contract working, not a bug.

## Continuation Capability

- **The round that reads the REPAIRS is where the class comes back.** Measured
  three times now. Last run a round-1 repair armed a gate whose own round 2 then
  found it had re-opened a false negative in the class it was fixing.
- **A claims reviewer finds a different class than a code reviewer.** Three
  code rounds missed a promised verification step that never ran, a Slice Log
  contradicting its own retro, and an unreconciled headline count. One distinct
  observer auditing what the artifact ASSERTS caught all three. Now a standing
  contract step.
- **A test can assert a proxy instead of the thing.** `assert "--strict" not in
  source` matched the docstring explaining that flag's absence. Read the real
  parser. Same family as "build fixtures from the source constant".
- **The dup ratchet re-fires after a refactor** — running it at the first edit
  is necessary, not sufficient; restructuring rotates the fingerprints.

## Current State

- `main` is at `ac39c9f5` remotely, and **one proven commit is UNPUSHED**
  (`58960639`). It arms the path check as a blocking gate, repairs #477, splits
  `<authoring-repo>/` out of `<repo-root>/`, and makes the closeout-claims
  review standing. Locally proven — broad suite green, two review rounds — so
  only the boundary crossing is missing. Re-check with `gh run list --limit 3`.
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

1. **The waiting goal owns the work** — push, close #477 through the commit
   carrier with its full ledger, decide the 7 #478 sites. Read it rather than
   re-deriving its slices here.
2. **#475's behavioural half is still an OPEN operator decision.** Nobody has
   observed an agent ask-and-spawn in a repo that never ran `setup`.

## Discuss

- **External side-effect approval expired with the last goal.** Push,
  issue-filing, and issue-closing each need a fresh grant. That grant is exactly
  what blocks the waiting goal.
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

- [waiting goal](../charness-artifacts/goals/2026-08-03-push-the-armed-gate-and-close-477-through-its-carrier.md) · [completed goal](../charness-artifacts/goals/2026-08-03-repair-the-commands-the-skills-tell-agents-to-run.md) · [retro](../charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md) · [the sweep](../charness-artifacts/audit/2026-08-02-can-this-rule-fire-sweep.md)
- [deferred decisions](./deferred-decisions.md) (D45–D49) · [north star](./design-north-star.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md)
