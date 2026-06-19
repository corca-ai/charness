# Boy-scout duplicate ratchet + advisory-review capability — design note (item 5)

Deferred to a future session (operator: "item 5는 다음 세션에서"). This captures
the decided intent so the next session designs/builds without re-deriving it.
Builds on item 4 (nose required >=0.13.0 + `inventory_doc_duplicates.py` advisory
+ `doc-nose-baseline.json` drift baseline).

## Goal

Make quality improve continuously (boy-scout: leave it better than you found it),
not only when the `quality` skill is run. Concretely, ratchet duplication *down*
over time. Duplication is the first instance; the pattern should generalize to
other advisory inventories.

## Two coupled pieces (this is one capability, not two)

1. **Review advisories → reviewed-fixable-candidate list.** Today the quality
   nose advisories (`inventory_nose_clones`, `inventory_doc_duplicates`) report
   families with a drift baseline, but there is NO structured "review the
   advisory → classify intentional-boilerplate vs genuinely-fixable → durable
   candidate list" step. Add it. This is the precondition for any ratchet:
   `inventory_nose_clones.py` explicitly forbids treating raw `total_dup_lines`
   as a reduction target (intentional boilerplate inflates it), so the ratchet
   must run on the **reviewed-fixable subset**, never the raw count.
2. **Ratchet on the reviewed subset.** A checked-in baseline + gate so the
   candidate count cannot increase, and boy-scout decrement via deliberate
   re-baseline lock-in (one-way).

## Operator design input (2026-06-19)

- **Use nose's commit-comparison.** nose supports `--baseline <FILE>` and a
  `since=<ref>`/`--fail-on new` temporal lens. Use "compare against last
  origin/main" to separate **newly-introduced** duplication from **pre-existing**.
- **Pre-push ratchet shape:** in pre-push, require (a) reduce **newly-introduced**
  dup (vs origin/main) by >= 1, AND (b) reduce **existing** dup by >= 1
  (boy-scout — any push nudges the backlog down, related or not).
- **NOT an absolute rule (critical).** Once quality is high, a strict
  "always -1" ratchet **oscillates** and creates friction (forces churn / blocks
  unrelated work when there is nothing meaningful left to remove). The design
  MUST account for diminishing returns: e.g. a healthy floor below which the
  requirement softens to advisory, a per-push opt-out with a reason, an escalation
  ladder (advisory -> nudge -> block) rather than a hard floor, or a budget that
  decays. Do not ship a hard absolute gate.

## Pre-push integration tension (flagged at item 4)

- A ratchet in pre-push must **fail closed on increase** but **not block unrelated
  work**, and stay **fast** — `doc-duplicates`' full-tree nose scan is ~18s, too
  slow for the ~13s docs-only fast subset, which is why item 4 kept it broad-only.
  The commit-comparison (`since=origin/main`) likely scopes the work to the diff
  and may be fast enough for pre-push; verify timing before wiring.
- Decide which loop owns it: a new pre-push phase vs an extension of the broad
  `doc-duplicates`/`inventory-nose-clones` phases.

## Portability (charness + consumer repos)

- The reviewed-candidate list + ratchet baseline are repo-local artifacts (like
  `nose-baseline.json` / `doc-nose-baseline.json`): charness uses
  `charness-artifacts/quality/`; consumers point an adapter at their own path.
- nose required (>=0.13.0, landed in item 4) is the enabler — both charness and
  consumers run the same engine. Keep the gate adapter-driven (scope + baseline
  path + soft-floor policy), not hardcoded.

## Related open idea (operator point #3)

`quality` could PROPOSE a multi-slice "surgery" campaign from its inventories
(scoped + sequenced + ratcheted), not just point at debt. The gate buy-vs-build
track itself was operator-initiated; a `quality` "propose a surgery" output mode
is the gap. Consider folding into item 5 or tracking separately.

## Routing

`find-skills` -> `quality` (capability lives in the quality skill) -> likely
`spec` to fix the soft-ratchet policy before `impl`. The soft/non-absolute
behavior is the hard design problem; spec it before building.
