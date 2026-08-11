# Charness Handoff

## Workflow Trigger

- **Invoke `charness:handoff`**, which routes a pickup here. Read
  [recent lessons](../charness-artifacts/retro/recent-lessons.md) BEFORE acting, then
  `## Next Session`, then route the chosen item through its owning skill — `impl` for code,
  `quality` for gate or floor changes, `issue` before any close.
- The digest is measurably lossy AND partly discharged — its `>= 35` ratchet-floor item is
  done. Correction filed in the
  [thesis](../charness-artifacts/spec/2026-08-11-harness-improvement-thesis.md).
- No goal is running. Run `git log --oneline origin/main..HEAD | wc -l` and state that number
  in your first reply. A push grant has been declined every session for several sessions — do
  not ask for one.

## Continuation Capability

- **Run the REPO's script, never `~/.agents/src/charness`.** That path is a full second
  checkout with its own git, adapters, and artifacts. Reading it as the source cost a wrong
  claim to the operator and two ~4-minute failed publishes.
- **On a proof surface, the round that reads the REPAIRS is the one that catches you.** Cap is
  two rounds, round-2 repairs are recorded accepted-unreviewed, and a round 1 that produced no
  repairs discharges it — full rule in
  [operating contract](./conventions/operating-contract.md) Critique Discipline.
- **A count pin standing in for a derivable fact: derive it, do not bump it** — but a coverage
  floor is a deliberate bar, not a derivable fact, and two derivations sharing one parser move
  together and stay green.
- **A ratchet baseline is regenerated, never hand-edited** — but only after confirming the
  delta is intended, or regeneration launders a real violation green. Its guard cross-checks
  one pair of fields, so a hand-edit left two ENFORCED counts stale.
- **A removal's consumer grep must cover every consumer AND every spelling.** Two misses this
  session: a second reader of the same baseline file, and shipped prose naming the capability
  in English where the identifier grep saw nothing.
- **"Replaces" needs its limits stated where the claim is made** — a repo-level gate cannot
  replace what shipped inside a portable skill package.
- **Before writing a list, a pin, or a key: does a surface here already know the answer?**
  [Declared Where Derivable](./conventions/implementation-discipline.md#declared-where-derivable).

## Current State

- Re-take gate and open-issue counts, do not inherit them:
  [quality posture](../charness-artifacts/quality/latest.md), `gh issue list --state open`.
  `check-changed-line-mutation-coverage` UNPROVEN on a dirty tree is expected; the block below is frozen.
- **Ruling 1 (`#598`) is EXECUTED, both halves**; the rulings artifact now carries a status
  line per ruling. **`#598` is not closable yet** — it needs the `issue` closeout floor, and it
  still sits inside the `#593`-`#599` range in `## Next Session` item 6. Ruling 4's deletion
  half also predates its ruling; only its release-note line is owed.
- **Two release-note lines are owed at the next bump, a MAJOR**: `check_title_slug_drift`, and
  the `domain_language_contract` removal. That second one has THREE parts a note must carry —
  see the "limits on the word replaces" block in
  [the gate](../scripts/check_documented_subcommands.py). Verified on a synthetic consumer, not
  an observed one: such an adapter resolves valid with the field dropped.
- **New: [#604](https://github.com/corca-ai/charness/issues/604)** (shipped parity defaults miss
  the bare `<repo-root>/scripts/run-quality.sh` form charness scaffolds; fails red→green) and
  **[#605](https://github.com/corca-ai/charness/issues/605)** (a trim-back loop whose guardian
  tests no longer reach it; unproven, deliberately not deleted).
- **`#582`-`#585` CARRY their own status. CLASS REMAINS, 4/4.** Do not close them.
- **D53's reopen trigger has three clauses and only the middle one — this repo's quality
  catalog gaining `validate_adapters`— is in-repo observable, with nothing watching for it**
  ([deferred](./deferred-decisions.md)).

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

1. **Rulings 2, 3, 5, 6** — [six-operator-rulings](../charness-artifacts/spec/2026-08-11-six-operator-rulings.md),
   status per section. Do not re-litigate; four overturned the framing handed up. Ruling 1's
   execution corrected its own sizing, so treat the others' measurements as estimates too.
2. **Ruling 6 is the largest** and the only schema change:
   [inventory_boundary_bypass_lib](../scripts/inventory_boundary_bypass_lib.py) records no
   call-site line info, so the payload, its public validator, and both baselines move together.
3. **Redesign the recent-lessons SELECTION policy — operator has the design**
   ([thesis](../charness-artifacts/spec/2026-08-11-harness-improvement-thesis.md)). Do not add a
   filter; that stacks a heuristic on a heuristic. The top `next_improvement` candidates by weight
   are content-free bookkeeping — every retro emits that line and recurrence boost rewards it.
4. **`#587` — edit, do not close.** Mapper is `tests_referencing_paths` in
   [suggest_mutation_coverage_command.py](../scripts/suggest_mutation_coverage_command.py). Read
   the issue body first; the only in-repo mention of `#587` describes different work.
5. **`#546` phase 2 — the adapter `conditional:` marker.**
6. **Waves 2-3.** `#539` `#581` `#588` `#528` `#589` `#542`, then `#586` `#590` `#593`-`#597`
   `#599` `#550` `#527`. Umbrellas wait on their own work.

## Discuss

- **Does a pattern-match decide what someone MEANT?** `--intent` replaced
  `should_fire_chunker`; the same shape survives in `setup_skill_routing_lib`'s
  semantic-completeness regex (ships to consumers), `chunked_routing_parser`,
  `classify_push_diff_lib`. Form validators are NOT in this class.
- **Should a consumer-facing capability be deletable without a portable replacement?** Ruling 1
  removed one that shipped in the quality package; the replacement is repo-only by
  construction, since it derives from charness's own CLI. Is a release note the standing answer?

## References

- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — read before changing operating contracts, prompt or skill surfaces, exports, or artifacts.
- [Design north star](./design-north-star.md)
- [Deferred decisions](./deferred-decisions.md)
- [Umbrella class disposition plan](../charness-artifacts/spec/2026-08-10-umbrella-class-disposition-plan.md) — per-section execution status, the sweep with its consumer greps, and the pickup-deletion ruling.
- [Harness-improvement thesis](../charness-artifacts/spec/2026-08-11-harness-improvement-thesis.md) — the digest slot-policy finding and the autonomy precondition.
- [Six operator rulings](../charness-artifacts/spec/2026-08-11-six-operator-rulings.md) — status per ruling, the evidence behind each, and the two feasibility measurements.
- [Rulings retro](../charness-artifacts/retro/2026-08-11-six-rulings-and-the-declared-where-derivable-class.md) — the record behind most Continuation Capability bullets.
- [Validator timing layers](./conventions/validator-timing-layers.md) — the live registry and what its gate cannot check.
- [Open-issue opinion](../charness-artifacts/audit/2026-08-08-open-issue-opinion.md)
