# Charness Handoff

## Workflow Trigger

- **No goal is waiting.** Pick from `## Next Session`, or shape one with
  `/achieve <outcome>`.

## Continuation Capability

- **The round that reads the REPAIRS is where the class comes back — third
  measured instance.** Last run's round-1 repair wired a new advisory into
  `run-quality.sh` and satisfied neither of that surface's two registration
  contracts, shipping a gate failure of the class it was fixing.
- **A claims reviewer finds a different class than a code reviewer.** Three
  code-reading rounds passed over a promised verification step that had never
  run, a Slice Log contradicting its own retro in the flattering direction, and
  an unreconciled headline number. A distinct observer auditing what the
  artifact ASSERTS found all three in one pass.
- **A test can assert a proxy instead of the thing.** `assert "--strict" not in
  source` matched the docstring explaining that flag's absence. Read the real
  parser. Same family as "build fixtures from the source constant".
- **The dup ratchet re-fires after a refactor** — running it at the first edit
  is necessary, not sufficient; restructuring rotates the fingerprints.

## Current State

- `main` is at `ac39c9f5`, remote CI green. Re-check: `gh run list --limit 3`.
  The combined-status API reports `pending`/`total_count: 0` for every commit
  here — this repo publishes check-runs, not legacy statuses. Not a real pending.
- **The 13 broken shipped commands are repaired and pinned.** Recount any time
  with `python3 scripts/inventory_skill_script_references.py --repo-root .`; the
  teeth are [test_skill_script_references.py](../tests/test_skill_script_references.py).
  It resolves against BOTH
  the authoring tree and the shipped `plugins/` mirror, because those are
  different trees and the inherited measurement had only seen one.
- **The accumulation mechanism is the durable finding**, not the count:
  `<repo-root>/` is `check_doc_links.py`'s own documented portable placeholder,
  so the escape hatch and the typo are the same token. Argue any future gate
  promotion from that, not from "13".
- Still open and untouched: the **E-cluster**, D41–D49,
  `parse_created_date`'s uncorroborated consumers.

## Next Session

1. **#477 — an operator decision one character wide.**
   `$SKILL_DIR/../../../scripts/plan_risk_interrupt.py` in `impl`/`spec` reaches
   the repo root in the authoring tree and overshoots the plugin root in the
   shipped one, silently, behind `2>/dev/null || true` — so it has never run in
   any installed plugin. Repointing would make a never-running command start
   running. Decide: repoint, or delete the call.
2. **#478 — skill prose telling a consumer to run charness authoring-repo
   scripts.** They ARE exported to the plugin, so `<plugin-dir>/` would resolve;
   whether public skill prose may invoke plugin-level scripts is the call. One
   site is a `.sh` no `.py`-only measurement ever counted.
3. **The highest-leverage item surfaced and NOT taken**: give the consumer-only
   escape its own distinguishable spelling, so a checker can tell a deliberate
   escape from a typo. See the retro's `## Portable Candidate`.
4. **#475's behavioural half is still an OPEN operator decision.** Nobody has
   observed an agent ask-and-spawn in a repo that never ran `setup`.

## Discuss

- **The external-side-effect approval was scoped to the completed goal and does
  NOT carry forward.** Push, issue-filing, and issue-closing need a fresh grant.
- **Open: which spelling of the delegation contract wins for EXISTING
  consumers.** Widening the markers flips every already-set-up repo at once,
  against a population this tree cannot count — what D49 forbids.
- **A read-only check and an irreversible boundary deserve different teeth** —
  D48 left `drift` alone and refused at publish; still open for other gates.
- **Advisory-vs-gate for the new path check.** It ships advisory by the
  operator's Floor-Addition Restraint call; the recurrence evidence a promotion
  needs is now recorded, so the next occurrence is the trigger, not a fresh count.

## References

- [completed goal](../charness-artifacts/goals/2026-08-03-repair-the-commands-the-skills-tell-agents-to-run.md) · [retro](../charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md) · [prior goal](../charness-artifacts/goals/2026-08-03-fix-the-rule-that-cannot-fire-where-it-was-written-to-then-count-the-rest.md) · [the sweep](../charness-artifacts/audit/2026-08-02-can-this-rule-fire-sweep.md)
- [deferred decisions](./deferred-decisions.md) (D45–D49) · [north star](./design-north-star.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md)
