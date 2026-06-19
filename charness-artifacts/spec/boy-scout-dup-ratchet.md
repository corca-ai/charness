# Spec — Boy-scout duplicate ratchet + advisory-review capability (item 5)

Refines [the item-5 design note](../audit/2026-06-19-boy-scout-dup-ratchet-design.md).
Builds on item 4 (nose required >=0.13.0; `inventory_doc_duplicates.py` advisory +
`doc-nose-baseline.json`; `inventory_nose_clones.py` advisory + `nose-baseline.json`).
Hardened by the 2026-06-19 fresh-eye spec critique (recorded in `## Critique`).

## Problem

Quality only improves when the `quality` skill is run; nothing ratchets
duplication *down* over time. And the existing nose advisories report raw family
counts that include **intentional portable boilerplate** (nose's own blind-spot
note: `resolve_adapter.py` copied per skill inflates the count). So any ratchet on
the raw count is dishonest — there is no reviewed "genuinely-fixable" subset to
ratchet against. Two coupled pieces, one capability.

## Current Slice

Add the reviewed-fixable classification layer (piece 1) and the soft
escalation-ladder ratchet on the fixable subset (piece 2). The portable
deliverable is a **standalone adapter-driven gate script + a payload artifact
contract** (mirroring `references/boundary-bypass-ratchet.md`), NOT new logic
baked into charness's internal runner. charness wires the script into its own
`run-quality.sh` + broad pre-push; a consumer wires the same script into their own
runner/hook or gets the verdict via the `quality` skill. First impl slice = piece 1
(the ratchet is meaningless without the reviewed subset).

## Fixed Decisions

1. **Soft-floor policy = escalation ladder** (operator-decided 2026-06-19):
   - **Hard block, always:** introducing a *new* fixable-eligible family blocks.
     Never oscillates — you simply do not add new fixable duplication.
   - **Boy-scout removal of existing fixable dup = escalating nudge:** normally an
     advisory message. If the fixable ceiling has not decreased for **K** commits
     since the review artifact last changed, it escalates to a **one-time block**,
     which resets on the next reduction.
   - **Healthy floor F:** when fixable count `<= F`, the boy-scout
     nudge/escalation fully softens to advisory. The hard "no new dup" block still
     applies.
2. **Tuning surface = `.agents/quality-adapter.yaml`** (operator-decided):
   `dup_ratchet: { enabled, floor_F, escalation_K, scope_paths,
   review_artifact_path }`. **Default when the block is absent: `enabled: false`
   (fully inert — no block, no charness-path read, no crash)**, matching this
   repo's stack-neutral opt-in pattern (`changed_line_mutation_gate`,
   `command_timing_log`, `standing_doc_provenance` are all inert-when-absent).
   Consumers point `review_artifact_path` + `scope_paths` at their own repo.
3. **Reviewed classification = a separate artifact**
   `charness-artifacts/quality/dup-review.json` (consumer path via adapter), keyed
   by family identity: **`family_signature` for docs, `family_id` for code**
   (nose 0.13.0 emits `family_id`, a stable 16-hex content hash — there is NO
   `key` field; slice 1 must extend `nose_report_lib.family_summary()` to
   propagate `family_id`, which it does not today). Each entry
   `{ id, surface: code|doc, class: fixable|intentional|unreviewed, note,
   reviewed_at }`. The two existing baselines keep owning drift detection
   unchanged; the review artifact references their identities.
4. **New-family detection = our own set-diff over the enumerated `families[]`,
   per surface — NOT nose's native `--fail-on`.** Driven by corca-ai/nose#463
   Obs 4 ([gather asset](../gather/2026-06-19-nose-463-v013-output-observations.md)):
   on a real repo nose's `--fail-on any` count (1163) diverges from
   `summary.families`/`families[]` (1068) by ~95, so the gate count and the
   fixable count would be inconsistent if mixed. **One enumeration feeds both the
   count and the newness check.**
   - **code:** diff the current `family_id` set vs the accepted code baseline.
   - **docs:** diff the current `family_signature` set vs `doc-nose-baseline.json`
     (already how `inventory_doc_duplicates.py` works).
   A "new fixable-eligible family" = a family present now, absent from the
   baseline, whose identity is not classified `intentional`.
5. **Stagnation measured from git, no stored SHA, no mutable counter.** Anchor =
   `git log -1 --format=%H -- <review_artifact_path>` (the commit that last touched
   the review artifact). Stagnation = `git rev-list --count <anchor>..HEAD`. This
   avoids BOTH circularities (a hook cannot commit a counter into the push it
   gates, and a commit cannot store its own SHA). Lowering the ceiling = editing
   the review artifact = a commit touching it = resets the clock; any reclassify is
   also legitimate review work that resets it. Edge rules the gate MUST implement:
   - **anchor not an ancestor of HEAD** (rebase/squash/force-push orphaned it):
     advisory only, surface "re-baseline needed", never hard-block on a phantom.
   - **interval consistency:** at pre-push, count over `<anchor>..HEAD` scoped to
     what is being pushed; on a long feature branch this counts branch commits —
     accepted as the "push proxy" and documented in the gate's help, not silently
     surprising.
   - expose stagnation as a function seam `stagnation_commits(anchor, head, repo)`
     so acceptance can inject a distance; do not inline `git rev-list` at the call
     site.
6. **One-way lock-in.** `fixable_ceiling` (the count) only decreases, via a
   deliberate re-review. An increase is exactly the "new fixable dup" the hard
   block rejects.
7. **Loop ownership + C5.** charness wires the gate script into `run-quality.sh`
   (`inventory-nose-clones` ~0.6s + `doc-duplicates` ~19s phases already run there)
   and the **broad pre-push path**, not the ~13s docs-only fast subset. Critique
   **C5 is acknowledged and accepted, not "absorbed"**: the docs-only fast subset
   intentionally keeps no doc-dup teeth (timing); the broad path carries the
   ratchet. (C5 is charness-internal — `.githooks/pre-push` DOCS_ONLY_LABELS — with
   no consumer relevance.)
8. **Inert when the review artifact is absent.** If `dup-review.json` is missing or
   unreadable (consumer never ran the piece-1 seed step), the gate emits no verdict
   and is advisory — never a hard block or crash.

## Probe Questions

- **Family-identity stability across nose versions.** RESOLVED (2026-06-19): the
  code gate runs `nose scan --format json` (see `inventory_nose_clones.build_command`),
  whose top-level `families[]` each carry `family_id` (16-hex content hash, present
  on all families, deterministic across runs). NB the `nose query` dashboard uses a
  different `id` field — anchor on the gate's `nose scan` output only. Re-review
  trigger when nose changes the fingerprint: same as the doc gate's per-scanner
  re-baseline. Still TODO in slice 1: propagate `family_id` through
  `nose_report_lib.family_summary()` (absent today).
- **How `quality` seeds classifications.** Default new families to `unreviewed`;
  `quality` proposes `fixable` vs `intentional` (auto-seed `intentional` for
  portable-copy patterns like `*/scripts/resolve_adapter.py`, `init_adapter.py`);
  operator confirms. **Key proposals on structural fields (`shared`/`removable`,
  members, files, same-vs-cross-language), NOT the dashboard `proven`/
  extractability labels** — corca-ai/nose#463 Obs 1+2 show those labels overclaim
  behavioral equivalence and rank a cross-language ~0-removable family #1, so a
  cross-language 0-removable family must not auto-seed `fixable`. If a proposal
  ever names an extraction target, exclude test-file-only helpers (Obs 5). Exact
  proposal UX resolved in slice 1.
- **Do `unreviewed` families block?** This is a *gating* (slice 2) decision and
  cannot be exercised in the no-gate slice 1. Slice 1 only records new families as
  `unreviewed`. Slice 2 decides + tests block (hard arm) vs advisory (boy-scout
  arm) for `unreviewed`.
- **Broad pre-push timing.** Measure the ~19s doc scan on a real broad push; if
  intolerable, gate code-clone in pre-push and defer the doc-dup ratchet to the
  broad gate. (slice 2)

## Deferred Decisions

- Fast diff-scoped pre-push doc-dup variant (the design note's open perf idea).
- `quality` "propose a multi-slice surgery campaign" output mode (design note
  operator point #3) — track separately, not in this capability.

## Non-Goals

- Ratcheting raw `total_dup_lines` / raw family count (intentional boilerplate
  inflates it — explicitly forbidden by `inventory_nose_clones.py`).
- Forcing reduction of `intentional`-classified families.
- A hard absolute "-1 every push" gate (operator: do not ship).
- Pre-push enforcement *in consumer repos* via charness's hooks — consumers wire
  the portable script themselves or use the `quality` verdict; charness does not
  install hooks into consumer repos.

## Deliberately Not Doing

- No mutable checked-in push counter and no self-SHA anchor (Fixed Decision 5).
- Not baking the ratchet into charness's internal `run-quality.sh` as the only
  home; the portable script is the unit, charness wiring is one consumer.
- Not restructuring the two existing baselines; the review artifact sits beside
  them rather than merging their differing shapes.

## Constraints

- Portable: the gate is a standalone script with adapter-driven paths and an
  honest disabled default; zero hardcoded charness paths; runs in a consumer repo
  pointing the adapter at its own artifact + scope. nose engine ships in the
  plugin, so consumers have the detector.
- nose >=0.13.0 required (item 4 enabler) — same engine in both repos.
- **Pin the nose command + JSON shape behind one resolver.** Gates today run the
  *deprecated* `nose scan --format json` (which carries `families[]` + `family_id`
  — confirmed). The recommended `nose query` has a different shape
  (`top_candidates` vs `families`, needs the `all` term) and takes only one path
  root per call (corca-ai/nose#463 Obs 3+6). Treat a scan->query migration as a
  known future change isolated to the resolver, not an ambient assumption; revisit
  before slice 2 in case nose reconciles Obs 3/4 upstream (which would simplify it).
- Root `scripts/` and `plugins/charness/` mirrors stay in lockstep.
- Advisory findings never block (item 4 posture preserved); only the ratchet
  verdict gates.

## Success Criteria

1. A new fixable-eligible family fails the ratchet (exit 1) via the gate script,
   per surface (code via `family_id` set-diff, doc via signature diff) — counts
   derived from the same `families[]` enumeration, not nose's `--fail-on`.
2. A family classified `intentional` does not count toward the fixable ceiling
   and never triggers the ratchet.
3. When fixable count `<= F`, the boy-scout arm is advisory; the hard
   no-new-dup block still fires.
4. With fixable count `> F`, `>= K` commits since the anchor, and no reduction,
   the boy-scout arm escalates to a block; a reduction (artifact edit advancing
   the anchor) resets it. Anchor-not-ancestor degrades to advisory.
5. **Portability proven, not asserted:** a consumer-style fixture repo with NO
   charness internals, a `dup_ratchet` block pointing at its own
   `review_artifact_path` + `scope_paths`, invoking the standalone gate script,
   gets a real new-dup block — and an absent `dup_ratchet` block leaves the gate
   fully inert.
6. Mirrors identical; full `quality_gates` suite green.

## Acceptance Checks

- `tests/quality_gates/test_dup_ratchet.py`: new-fixable-family blocks per surface
  (SC1); intentional family ignored (SC2); below-floor advisory (SC3); escalation
  fires after K stagnant commits via an injected `stagnation_commits` seam +
  real `git init`/`--allow-empty` fixture, and resets on artifact-anchor advance,
  and anchor-not-ancestor → advisory (SC4); adapter-driven F/K/path honored AND a
  consumer-style fixture repo (no charness internals) blocks on new dup while an
  absent block stays inert (SC5).
- `family_summary()` emits `family_id`; mirror-drift gate + `pytest
  tests/quality_gates/ -q` green (SC6).
- Negative: a new family is recorded `unreviewed` (slice 1) and, in slice 2, is
  not silently ignored by the hard arm.

## Critique

Bounded fresh-eye spec critique ran 2026-06-19: 2 delegated angle reviewers
(Weinberg/Jackson mechanism; Gawande/portability), counterweight triage inline
(the hard policy fork was already operator-decided + counterweighted on
2026-06-19, so not reopened). Findings folded into Fixed Decisions above:
identity field `key`->`family_id` + emit it (was Act); self-SHA anchor circularity
-> git-log-derived anchor (was Act); portability hole (gate wired only into
charness-internal runner) -> standalone adapter-driven script + consumer
acceptance (was Act, the operator's both-repos requirement); per-surface newness,
orphaned-anchor/branch semantics, inert defaults (Bundle); unreviewed-blocks
moved to slice 2 (sequencing); `since=` design-note ghost killed (over-worry).
Fresh-Eye Satisfaction: parent-delegated.

## Canonical Artifact

This spec (`charness-artifacts/spec/boy-scout-dup-ratchet.md`) is canonical during
implementation; the design note is historical intent.

## First Implementation Slice

Piece 1: extend `nose_report_lib.family_summary()` to emit `family_id`; define the
`dup-review.json` schema; add a `quality` review step that reads the two nose
inventories, seeds classifications (`intentional` for portable-copy patterns, else
`unreviewed`), and writes the reviewed artifact with `fixable_ceiling`. No gating
yet — just the reviewed subset + its tests (artifact shape + seed classification +
`family_id` emission). Slice 2 adds the standalone escalation-ladder gate script,
its adapter wiring, and the portability + escalation acceptance tests.
