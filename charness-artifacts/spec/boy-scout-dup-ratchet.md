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
     **(Superseded by Slice 2 D1: the "accepted code baseline" is the new
     gate-owned `family_id` baseline `dup-ratchet-baseline.json`, NOT
     `nose-baseline.json` — its `key` is not `family_id`-diffable. See
     `### Slice 2`.)**
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
  ever names an extraction target, exclude test-file-only helpers (Obs 5).
  PARTIALLY RESOLVED (slice 1, 2026-06-19): the seed (`seed_dup_review.py` +
  `dup_review_lib.py`) does the *mechanical* half — auto-seed `intentional` only
  when **every** member file is a pure portable copy (`resolve_adapter.py` /
  `init_adapter.py`), else leave `unreviewed`; it NEVER auto-seeds `fixable`. The
  *interactive* structural-field `fixable`-vs-`intentional` proposal UX is
  **deferred to slice 2** with the gate (it needs the structural fields the gate
  already reads), not built blind in slice 1.
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
  **UPDATE (2026-06-19, post-slice-2): nose 0.13.3 REMOVED `nose scan` entirely —
  the migration is no longer optional.** `nose query <path> --format json` is now
  `schema_version: 3` with `top_candidates` (NOT `families`), each keyed by `id`
  (NOT `family_id`), plus `locations`/`members`/`removable`/`shared`; full
  enumeration needs the `all` term, and `top=`/`sort=` are query terms. Slice 2
  shipped on 0.13.0 (`scan`); under 0.13.3 the gate degraded to advisory and never
  false-blocked (FD8 validated). The scan->query migration + re-baseline under
  0.13.3 is its own next-session slice (see `docs/handoff.md` `## Next Session`);
  it also fixes the existing `inventory_nose_clones.py` code-clone advisory, which
  breaks identically on 0.13.3.
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

### Slice 1 DONE (2026-06-19)

- `family_summary()` emits `family_id` (5226ad9f). ✓
- `dup_review_lib.py` (pure: `classify` / `family_records` / `build_review` /
  `validate_review`) + `seed_dup_review.py` (CLI: collects both inventories,
  merges, writes) + `tests/quality_gates/test_dup_review_seed.py`. ✓
- Canonical `charness-artifacts/quality/dup-review.json` seeded
  (`schemaVersion: charness.quality.dup_review.v1`). First seed: 2 auto-`intentional`
  code families, `fixable_ceiling: 0`.
- **Design decisions (reversible; regenerate the artifact to change):**
  - **Classified-only overlay** — stores only `intentional`/`fixable`; an unlisted
    family is implicitly `unreviewed` (keeps it small; newness still computed from
    the baselines per FD4, not from this overlay).
  - **Seed input = the inventories' DEFAULT (baseline-active) behavior**, so the
    seed classifies drift; it does NOT bypass the baseline or import baseline
    identities (avoids the unresolved baseline-`key`-vs-`family_id` reconciliation).
  - **Docs carry no member paths** in the inventory view (only witness spans), so
    doc families never auto-seed `intentional` in slice 1 — operator-driven later.
- **Open for slice 2 — RESOLVED 2026-06-19:** all four open points are settled
  in `### Slice 2 — Resolved Decisions + Plan` below (identity reconciliation,
  `unreviewed`-blocks, proposal UX, adapter wiring).

## Slice 2 — Resolved Decisions + Plan (2026-06-19)

Settles the slice-2 fork the handoff flagged. **Supersedes the literal reading of
FD4** ("diff current `family_id` set vs the accepted code baseline"): the existing
nose code baseline is NOT `family_id`-diffable (see D1), so the gate keys code
newness on a new gate-owned `family_id` baseline instead.

### Evidence (reproduced this session)

- `nose-baseline.json` keys code families by **`key`** (547 entries:
  `{key, note, members}`), written by `nose scan … --write-baseline`. The scan
  report (`nose scan … --format json`) families carry **`family_id`** (stable
  16-hex content hash) and **no `key`** — two different identity schemes, neither
  cross-referenceable. `key` is cluster/membership-sensitive: a copy family
  re-keys when *any* sibling copy changes, so `--baseline` re-flags unchanged
  copies as drift — **17 of 42 current code "drift" families have every member in
  files unchanged since the baseline commit** (all high-multiplicity boilerplate:
  `init_adapter.py` / `resolve_adapter.py` / `scaffold_*_artifact.py`).
  `family_id` stayed stable across the same churn (the 2 seeded intentional
  family_ids reappear unchanged). Filed upstream: **corca-ai/nose#466**.
- Code full scan ≈ 0.6s; doc scan ≈ 18.5s; doc drift currently 0; doc `signature`
  (sorted member `path#heading`) is heading-based and **stable** (no churn).

### Decisions

- **D1 — Code newness via a `family_id` gate baseline (NOT nose `key`).** New
  artifact `charness-artifacts/quality/dup-ratchet-baseline.json`
  (`{schemaVersion: charness.quality.dup_ratchet_baseline.v1, code_family_ids:[…]}`,
  consumer path via adapter). Run a FULL `nose scan` (no `--baseline`) → current
  code `family_id` set; a family_id absent from the gate baseline AND not
  classified `intentional` in the overlay = a new fixable-eligible family → HARD
  block. The churny `key`/nose-`--baseline` path is unused for gating.
- **D2 — Doc newness via existing stable signature drift.** Use the doc inventory
  drift (vs `doc-nose-baseline.json`, signature-based); a doc drift family not
  `intentional` → block. No doc gate baseline (signature is already stable). The
  code/doc asymmetry is justified by the tool: code `key` churns, doc `signature`
  does not — document it in the reference.
- **D3 — `unreviewed` blocks (FD1).** A NEW family (not in the accepted reference:
  gate baseline for code, `doc-nose-baseline` for docs) that is not `intentional`
  hard-blocks regardless of `unreviewed`/`fixable`. Recording it `unreviewed` does
  NOT unblock; only removal, `intentional` reclassification, or a deliberate
  gate-baseline acceptance does. A family already in the accepted reference is
  "known" and never hard-blocks.
- **D4 — Structural-field `fixable` proposal UX deferred.** It is an interactive
  `quality`-skill feature, not a gate dependency; the gate only consumes the
  overlay's classifications. Out of slice-2 gate scope.
- **D5 — Adapter block = validated peer of `changed_line_mutation_gate`** (in
  `quality_policy_defaults.py` + `quality_adapter_lib.py`):
  `dup_ratchet: { enabled (default false → inert), floor_F, escalation_K,
  scope_paths, review_artifact_path, gate_baseline_path }`. Gate reads via
  `load_quality_adapter_strict` (raw unknown keys are stripped by the loader, so
  it must be a validated block, not read ad hoc).
- **D6 — charness rollout = enable green, seeded** (operator-decided): seed the
  gate baseline with today's full code `family_id` set so the hard arm is green,
  enable `dup_ratchet` in `.agents/quality-adapter.yaml`, keep `fixable_ceiling: 0`
  (boy-scout advisory). Wire into `run-quality.sh` + broad pre-push only (NOT the
  docs-only fast subset; C5).

### Inert / degraded ladder

`dup_ratchet` absent or `enabled:false` → inert (exit 0). Enabled but overlay OR
gate baseline missing/unreadable → advisory, never block (FD8). nose missing →
empty families → degraded advisory (the `doc-duplicates --require-nose` phase owns
fail-closed on nose presence, not this gate).

### File plan (next session)

1. `skills/public/quality/scripts/dup_ratchet_lib.py` — pure `evaluate(...)`
   (hard arm + boy-scout/floor/escalation), gate-baseline load/build/validate,
   `intentional_identities`/`fixable_ceiling` from the overlay, and the git seams
   `resolve_anchor` / `anchor_is_ancestor` / `stagnation_commits(repo, anchor, head)`
   (injectable per FD5). `evaluate` takes injected `stagnation` — do not inline git.
2. `skills/public/quality/scripts/check_dup_ratchet.py` — CLI. Loads the adapter,
   reads `dup_ratchet`; code = full `nose scan` (reuse `inventory_nose_clones`
   `build_command`/`resolve_nose_bin` with `baseline=None`, high `--top`, then
   `nose_report.run_nose`); doc = drift (accept `--code-inventory`/`--doc-inventory`
   injected JSON like `seed_dup_review.py`); `--write-baseline` seeds the gate
   baseline. Mirror `check_changed_line_coverage.py` bootstrap/adapter pattern.
3. `scripts/quality_policy_defaults.py` + `scripts/quality_adapter_lib.py` — add
   `DEFAULT_DUP_RATCHET` + `validate_dup_ratchet` + `_apply_dup_ratchet` + key in
   `infer_quality_defaults` (no test snapshots the full default key set, verified).
4. `skills/public/quality/adapter.example.yaml` — inert `dup_ratchet` example.
   `.agents/quality-adapter.yaml` — charness's enabled block.
5. `skills/public/quality/scripts/inventory_doc_duplicates.py` — add `--json-out`
   so `run-quality`'s `doc-duplicates` phase persists drift JSON for the gate to
   reuse (avoids a second 18.5s doc scan).
6. `scripts/run-quality.sh` — `doc-duplicates` writes `--json-out "$TMPDIR/…"`; add
   a `dup-ratchet` phase in a flush batch AFTER `doc-duplicates` (passes
   `--doc-inventory` the reused file; runs its own 0.6s code scan).
7. `charness-artifacts/quality/dup-ratchet-baseline.json` — seed (D6) so green.
8. `skills/public/quality/references/dup-ratchet.md` — reference (mirror
   `boundary-bypass-ratchet.md`); state the code/doc asymmetry + nose#466.
9. `tests/quality_gates/test_dup_ratchet.py` — SC1–SC5 with injected inventories +
   injected `stagnation_commits` + a real `git init`/`--allow-empty` fixture +
   consumer-style fixture (no charness internals).

### Gotchas

- `seed_dup_review.py` runs the inventory with the default `--top 20` (truncates
  to 20 families) — the gate baseline seed MUST enumerate the FULL set (high/no
  `--top`, no nose baseline), or it will miss families and false-block later.
- Plugin mirror flattens `skills/public/quality/` → `plugins/charness/skills/quality/`;
  run `sync_root_plugin_manifests.py` before validators (it rmtree+re-exports).
- `family_summary()` already emits `family_id` (slice 1). `members` is an int
  count in the scan report but a list in the baseline file — read `locations` for
  files in scan output.

### Slice 2 DONE (2026-06-19)

All nine file-plan steps landed; SC1–SC6 green; full `run-quality.sh --read-only`
green (77/0) with the live `dup-ratchet` phase PASS (~1.4s).

- `dup_ratchet_lib.py` (pure `evaluate` two-arm policy + gate-baseline
  build/load/validate + overlay readers + injectable git seams `resolve_anchor` /
  `anchor_is_ancestor` / `stagnation_commits`; `evaluate` takes injected stagnation).
- `check_dup_ratchet.py` CLI (adapter-driven; full code scan reuse of
  `inventory_nose_clones` build_command with `baseline=None` + high `--top`; doc via
  injected `--doc-inventory`; `--write-baseline` seed; `--stagnation` test seam).
- Adapter block validated. **Deviation from file-plan step 3:** the default +
  validator live in a NEW module `scripts/quality_dup_ratchet_policy.py`, not
  `quality_policy_defaults.py` — that file was already at its 480-line cap, so
  piling on would have entered the warn band; `quality_adapter_lib` imports the
  default + validator from the new module. Net behavior identical to the plan.
- `inventory_doc_duplicates.py` `--json-out`; `run-quality.sh` doc-duplicates
  `--json-out` + a broad-only `dup-ratchet` phase reusing it (C5: NOT in the
  pre-push docs-only subset). `dup-ratchet-baseline.json` seeded green (571 ids,
  `fixable_ceiling: 0`); `dup_ratchet` enabled on charness (D6).
- Reference `references/dup-ratchet.md`; tests `tests/quality_gates/test_dup_ratchet.py`.
- Truth-surface follow-ons required by the new phase/surfaces: quality `SKILL.md`
  references entry (traded the redundant "Frequent-path references" line to stay
  under the 200-line cap), the validator-timing-layers table row, the
  attention-state-visibility declaration, and the handoff rewrite.
- **nose#466 anchors stripped from the portable skill package** (skill-anchor
  guard); provenance kept in this spec + the commit, not in the package.

### Slice 2 Critique (2026-06-19)

Bounded fresh-eye code critique via the prepare packet: 4 angle reviewers
(Jackson framing / Weinberg diagnostic / Gawande operational / Minto legibility)
+ 1 separate counterweight pass. Acted before commit:

- **D (Act):** reordered the Adoption steps in `references/dup-ratchet.md` +
  `adapter.example.yaml` so `scope_paths` is set BEFORE `--write-baseline` (the
  seed reads it; the old order re-introduced the truncation footgun the doc itself
  warns about).
- **B (Bundle):** `check_dup_ratchet.py` degrades when a real (non-injected) code
  scan returns 0 families against a non-empty gate baseline — a broken scan /
  misconfigured `scope_paths` can no longer read as a silent clean pass (new
  empty-real-scan guard test).
- **G (Bundle):** `escalation_K` CLI fallback aligned to the policy default (10).
- **L (Bundle):** dropped the point-in-time "17/42" number from the portable lib
  docstring (would rot per consumer/scan).

Deferred to a Next-Session "enabled-but-misconfigured → degrade / re-seed
discipline" hardening slice: **C** `--write-baseline` delta/confirm guardrail
(FD6 one-way lock-in has no code teeth yet); **I** wire `validate_gate_baseline`
into a run-quality/validate phase (a malformed committed baseline silently
disarms the hard arm); **F** warn when `enabled` but `scope_paths` empty (falls
back to nose `DEFAULT_PATHS` silently).

Counterweighted as Over-Worry (recorded so they are not relitigated): per-surface
vs whole-gate degrade (A — whole-gate advisory is the FD8 conservative posture,
never false-blocks, prints `degraded_reasons`); the "ratchet down" claim while the
boy-scout arm is inert at ceiling 0 (E — built + tested, dormant by honest config,
disclosed in the handoff); degraded-vs-clean summary token (H — `status` and the
ADVISORY body already distinguish them); stale-baseline drift telemetry (J); empty
`fixable` subset at ship (K — D4 deferred by design).

## Slice 3 — nose 0.13.3 scan→query migration DONE (2026-06-19)

Closes the `## Constraints` nose note (0.13.3 removed `nose scan`). The code-clone
path (the doc path already ran `nose query`) migrated to `nose query`, isolated to
the resolver `nose_report_lib.py` as the Constraint required; charness upgraded to
nose 0.13.3 and both id-baselines were re-seeded on it.

- **Resolver (`nose_report_lib.py`)** pins the command + shape: `build_query_command`
  (`all`/`top=`/`sort=` are query TERMS, not flags); `collect_families` runs one
  `nose query` per scope root (query takes one path) and merges, deduped by identity,
  with whole-result `error` if any root errors (FD8: never a silent clean pass) and
  `OSError` degrade for an invalid `NOSE_BIN`; `extract_report` reads `families`
  (sv2 0.13.0 / sv3 0.13.3, under the `all` term) OR `top_candidates` (no-`all`
  dashboard); `family_summary` normalizes `id`→`family_id`, `shared`→`shared_lines`,
  location `start`/`end`→`start_line`/`end_line`, derives `dup_lines` from member
  spans, and stamps `tool_version` from `nose --version` (query JSON omits it).
- **Advisory drift baseline moved off nose-native `--baseline`** (it clobbers across
  single-path query writes and keys on the churn-prone cluster `key`) to a pure
  Python id-set set-diff (`nose_baseline_lib.py`, `nose-baseline.json` reshaped to
  `schemaVersion: charness.quality.nose_baseline.v2` + `code_family_ids`). A legacy
  key-based baseline reads as `None` → all-drift until re-seeded (honest signal).
- **Gate (`check_dup_ratchet._scan_code_family_ids`)** reuses the resolver; both
  `dup-ratchet-baseline.json` (gate) and `nose-baseline.json` (advisory) re-seeded
  to 487 ids under 0.13.3. The advisory write path enumerates the FULL set
  (`WRITE_BASELINE_TOP`), never the display `--top` (a truncation bug caught + fixed
  in verification).
- **Version floor bumped `>=0.13.0`→`>=0.13.3`** in `integrations/tools/nose.json`
  (the gate baseline is version-scoped; running on a different nose risks false
  "new family" blocks). The doc engine's internal floor stays 0.13.0 (the Markdown
  engine landed at 0.13.0 and is unaffected) — an honest layer asymmetry.
- **Accepted query semantics:** a clone family split across two scope roots is no
  longer grouped (query scans one root); documented in the resolver + manifest, with
  re-baseline-per-scanner-version guidance.
- Verified on live 0.13.3: 104 focused tests, `run-quality.sh --read-only` 77/0
  (dup-ratchet + inventory-nose-clones + doc-duplicates phases green), packaging +
  managed-install green. Bounded fresh-eye critique (2 reviewers: correctness +
  portability) ran before lock: a stale plugin-mirror BLOCKER (re-sync), the gate
  baseline `nose scan` provenance note + stale `scan` comments, and an FD8 `OSError`
  hardening were all acted; the version-floor message divergence was counterweighted
  as an honest asymmetry (NIT, left).

## Slice 4 — D30 content-fingerprint re-key (SPEC, 2026-06-27, critique-hardened)

Resolves [`docs/deferred-decisions.md` D30](../../docs/deferred-decisions.md)
("dup-ratchet id-rotation affordance") and the
[2026-06-21 rotation debug](../debug/2026-06-21-dup-ratchet-family-id-rotation.md).
**Supersedes Slice 2 D1 + FD4's literal "diff the current `family_id` set vs the
gate baseline":** the gate stops keying code newness on nose's `family_id` and keys
on a gate-computed, offset/path-independent **content fingerprint** instead. The
two-arm policy, adapter surface, floor/escalation, and git stagnation seams are
unchanged — only the *identity the set-diff runs on* changes. Hardened by the
2026-06-27 bounded fresh-eye spec critique (3 angles + counterweight; see `### Critique`).

### Problem

nose's `family_id = f(normalized span content, line offset, file path)`, and the
family id folds every member's per-span id, so editing ANY scanned member file —
even inserting lines *above* an unchanged duplicated span — rotates the whole
family id with zero new duplication. The hard arm reads that pure rotation as a
brand-new family and blocks; the only honest recovery is a manual `--write-baseline`
re-baseline. This fires on essentially every member-file edit (#395, the v0.56.7
release hit it again → D30 reopen trigger). Slice 3 documented the rotation and the
re-baseline workflow; Slice 4 removes the false block at its root.

### Empirical anchor (reproduced this session on live nose 0.15.0, schema v6)

Two-file fixture sharing a 12-line function; raw nose-query member `locations` are
repo-relative `file` + 1-based-inclusive `start`/`end` (confirmed, not assumed):

- **Pure line-shift** (prepend 5 comment lines to one member): nose family id
  `f1e6823f50846bb3 → 806e4b5664258151` (ROTATES), content fingerprint
  `4032933ec3cfec51 → 4032933ec3cfec51` (**STABLE**) → the false hard-block is gone.
- **Genuine span-content change** (`total = 0 → total = 1` inside the span):
  fingerprint `4032933ec3cfec51 → a58724bff95adc18` (ROTATES) → genuine new/changed
  duplication is still caught. **This is the false-negative D30 blocked on** — a
  path-set `(file, name)` fingerprint would have masked it; the content fingerprint
  does not.

Fingerprints are computed against the SAME working tree the producing nose scan ran
on (the gate scans, then immediately fingerprints the same tree), so member line
numbers and file content are always consistent — no staleness window.

### Decisions

- **S4-D1 — Key code newness on a content fingerprint, not nose's `family_id`.**
  Per family the gate computes one fingerprint from member span CONTENT only;
  `evaluate` diffs the fingerprint set vs a fingerprint baseline (identical set-diff
  shape, different identity). nose's `family_id` is no longer stored or diffed.
- **S4-D2 — Fingerprint algorithm v1, PINNED VERBATIM** (an under-specified hash
  produces a self-consistent-but-cross-incompatible baseline that passes its own
  tests yet silently mis-gates — implementer/adversary F3/F2). Compute from the RAW
  `nose query` family's `locations` list (keys `file`/`start`/`end`), NOT
  `family_summary`/`sample_locations`/`start_line` (those truncate to 6 members).
  Member `file` is repo-relative because nose runs with `cwd=repo_root`, so the
  reader opens `repo_root / member["file"]`:

  ```python
  lines = (repo_root / member["file"]).read_text(encoding="utf-8").splitlines()
  member_hash = sha256("\n".join(l.rstrip() for l in lines[start-1:end]).encode()).hexdigest()[:16]
  # member_hashes is a duplicate-PRESERVING list — do NOT set()-dedup before sorting,
  # or {A,A,B} collapses to {A,B} and collides with a real 2-member {A,B} (adversary F2).
  family_fp = sha256("\n".join(sorted(member_hashes)).encode()).hexdigest()[:16]   # 16 hex = 64-bit
  ```

  Invariant to member order, line offset, and file path; sensitive to member content,
  membership, and member-multiplicity. (`sorted` over per-member hashes makes it
  order/path-independent; reading span bytes by `[start-1:end]` makes it
  offset-independent; duplicate-preserving keeps multiplicity.)
- **S4-D3 — Resolves D30's blocking false-negative.** D30 deferred because a sorted
  member `(file, name)` fingerprint masks a new clone reusing the same files. The
  CONTENT fingerprint distinguishes content, so it strictly dominates that approach
  (proven by the content-change anchor above).
- **S4-D4 — Migrate gate AND advisory baselines in lockstep.** Both
  `dup-ratchet-baseline.json` (gate) and `nose-baseline.json` (advisory) currently
  store `code_family_ids` (nose ids), re-baselined in lockstep to identical 538-id
  sets. Both move to a NEW key `code_family_fingerprints` under bumped schema versions
  (`dup_ratchet_baseline.v2`, `nose_baseline.v3`). The loader reads ONLY the new key;
  a pre-migration baseline (old key) loads as `None` → degraded advisory (FD8) — NO
  dual-read legacy fallback (a stale checkout misreading nose ids as fingerprints is
  exactly the mis-gating the new-key choice prevents; that choice is load-bearing,
  not cosmetic). Keep the loader's function NAME (`load_gate_baseline_ids`) — it is
  identity-agnostic ("the accepted identity set"), only the key it reads changes.
  Re-baseline in the SAME commit so no SHIPPED commit has a toothless window (S4-D7).
  Stamp `fingerprint_algo_version` beside the existing nose `tool_version`.
- **S4-D5 — Stamp the fingerprint at the report layer; one shared helper.** New
  `skills/public/quality/scripts/nose_fingerprint_lib.py` owns the pure normalization +
  `family_content_fingerprint(family, repo_root) -> str | None`.
  `nose_report_lib.collect_families` (which holds the RAW full `locations`) calls it
  once per family and stamps `family["family_fingerprint"]`, the same way it already
  stamps `family_id` (`keyed.setdefault`). EVERY consumer then reads that one stamped
  field: the gate (`check_dup_ratchet`), the advisory (`inventory_nose_clones`), AND
  the overlay seed (`dup_review_lib.family_records`, today reading `family_id`). One
  computation, no per-consumer truncation, no three-way divergence — and it respects
  the cohesion/length-cap split pattern (slice 1 split `nose_report_lib` out for the
  same reason).
- **S4-D6 — FD8 preserved: an uncomputable fingerprint degrades the WHOLE gate, never
  blocks, never drops the family.** A missing/unreadable member file or an
  out-of-range line span returns `None`; the scan path then appends a
  `degraded_reasons` entry (whole-gate advisory, the existing FD8 ladder) — it must
  NOT silently drop the family from the diff set (a dropped family reads as a false
  "removed family"). Inherit the Slice-2 whole-gate posture; do not add per-family
  degrade or richer telemetry (counterweighted Over-Worry A in Slice 2).
- **S4-D7 — "No live window" holds only for SHIPPED commits; lockstep is one commit.**
  Safety = (old-key baseline on disk) + (new code reading the new key) → `None` →
  degraded advisory (FD8, never false-block). This is airtight for any shipped commit
  ONLY because the lib, both baselines, the overlay, and the mirror all land in ONE
  commit (Phase Rules treat baselines as repo state committed with their code). An
  intermediate WORKING-TREE state (lib edited, baseline not yet re-written) degrades
  to advisory — never false-blocks — so the implementer's own pre-push is safe too.
  Acceptance gate: a fresh checkout AT the migration commit shows the dup-ratchet
  phase PASS or ADVISORY, never hard-block.
- **S4-D8 — Migrate the `dup-review.json` overlay identity in lockstep (the surface
  both this File plan AND D30's impact list originally missed — operational F1, the
  most dangerous gap).** `evaluate` computes
  `new_code = fingerprints − baseline_fingerprints − intentional_code_ids`, where
  `intentional_code_ids` come verbatim from the overlay's code `id` fields. The live
  overlay stores **33 code `intentional` entries keyed by nose `family_id`, 27 of them
  live in the current baseline; only 2 are auto-seeded, 31 are HAND-classified** with
  irreplaceable review notes. If left nose-id-keyed after the swap, the subtraction
  becomes a no-op and all 27 accepted boilerplate families re-enter the hard arm as
  "new" → the fix would itself introduce a false-block on every accepted family.
  Therefore: (a) migrate the seed identity — `dup_review_lib.family_records` reads the
  stamped `family_fingerprint` instead of `family_id` (so future auto-seeds are
  fingerprint-keyed); (b) one-time DATA migration of `dup-review.json` is a
  **member-preserving REMAP, never a seed re-run**: build a `nose_id → fingerprint`
  map from the live scan, rewrite each code entry's `id` in place while PRESERVING its
  `class`/`note`/`reviewed_at`; entries whose nose_id is not in the live scan
  (already-orphaned classifications, the 33−27) are dropped with a logged note. The
  add-only `build_review` merge must NOT be used here (it would keep stale nose-id
  cruft and silently drop the 31 manual entries). Acceptance: after migration every
  `intentional` code `id` ∈ the migrated fingerprint baseline (no orphaned intentional
  id) and all 31 manual notes survive verbatim.
- **S4-D9 — `evaluate`'s param/key names stay (identity-agnostic); membership change
  still rotates the identity = expected re-baseline.** Keep `evaluate`'s parameters
  and verdict keys (`code_family_ids`, `gate_baseline_ids`, `new_code_families`) — the
  values are now fingerprints but the logic is a pure opaque-string set-diff; do NOT
  rename (a rename ripples through `check_dup_ratchet` + ~15 policy tests for zero
  behavior change). Consequence to document (adversary F1, sharpest attack): because
  the fingerprint folds membership, removing one of N copies (a legitimate reduction)
  rotates the family fingerprint → the reduced family reads "new" → hard-block. This
  is NOT a regression — nose's `family_id` already rotates on membership change today
  (the family id is a function of all member ids) — so the recovery is the SAME
  re-baseline. The reference and SC must state it so operators are not surprised;
  Slice 4 fixes the OFFSET rotation (the D30 bug), not membership rotation.

### Probe Questions (resolve in the first impl slice, against the live corpus)

- **PQ1 — Fingerprint uniqueness.** Confirm `len(distinct fingerprints) ==
  len(distinct nose families)` across the full charness scan. Under nose's GLOBAL
  clustering, identical exact-member-text sets would already have merged (and
  `collect_families` dedups by nose id before fingerprinting), so a NATURAL collision
  is precluded; the residual is only a 64-bit sha256[:16] birthday collision (~8e-15
  over 538 families) — negligible. The check guards an IMPLEMENTATION-induced collision
  (e.g. an accidental `set()`-dedup, S4-D2) more than a natural one. One-shot probe →
  SC3, not a permanent runtime gate.
- **PQ2 — In-place comment/whitespace-edit residual.** v1 rstrip-only normalization is
  STRICTER than nose's tokenizer: an in-place comment or internal-whitespace edit
  inside a duplicated span (no line-count change) rotates the fingerprint where nose's
  normalized id would NOT — a *different* (in-place, non-shifting) edit class, not a
  subset of today's offset triggers. It is low-frequency and falls back to the SAME
  re-baseline recovery, but the honest framing is "trades a high-frequency offset
  trigger for a low-frequency semantically-spurious one nose itself would not
  produce," NOT "strictly rarer." Measure materiality on the corpus before shipping;
  token/comment-aware normalization is S4-Defer-1.
- **PQ3 — Performance.** Stamping a fingerprint for ~538 families adds file I/O to the
  ~0.6s code scan; cache reads per file and confirm the `dup-ratchet` phase stays
  within its ~1.4s budget.

### Deferred Decisions

- **S4-Defer-1 — Token/comment-aware normalization** matching nose's tokenizer
  (eliminates the PQ2 in-place-edit residual). Deferred unless PQ2 shows it material;
  v1 ships rstrip-only. Reopen: in-place-comment false-rotation observed in practice.
  (Its arrival is itself an algo change → bump `fingerprint_algo_version` so stored
  fingerprints surface as algo-skew re-baseline, not a corpus-wide false-block — this
  is exactly why the algo-version stamp is load-bearing, not gold-plating.)
- **S4-Defer-2 — content-fingerprint's own narrow false-negative (vanish/shrink then
  recur).** A baseline family fully vanishes (or SHRINKS, freeing its original
  member-hash set) AND a byte-identical clone with the exact same member set recurs
  elsewhere → fingerprint re-matches → re-accepted as "known." This re-accepts
  already-accepted duplication CONTENT (not new content), needs the original member
  set to recur exactly, and is far narrower than the path-set false-negative D30
  rejected. Accepted as residual; revisit only if observed.
- **S4-Defer-3 — subset-aware reduction diff.** Treat a live fingerprint whose
  member-hash set is a strict subset of a vanished baseline family as a REDUCTION
  (not new dup), so removing a copy does not hard-block (the S4-D9 case). A genuine
  enhancement beyond D30's offset scope; deferred to keep the slice focused (and per
  the counterweight's "don't over-build"). Reopen: operators hit membership-shrink
  re-baseline friction often.

### Non-Goals

- Doc-side change. The doc gate already keys on the position-independent `signature`
  (`path#heading`, Slice 2 D2) and never rotated on offset. Slice 4 is CODE-side
  only; both surfaces are now position-independent (different mechanisms because the
  inputs differ).
- Changing nose, or waiting for nose to ship a content id (D30's other reopen
  trigger) — the gate computes the identity itself.
- Changing the two-arm policy, adapter block, floor/escalation, or git seams.

### Deliberately Not Doing

- **Gate-only migration** (advisory left on nose ids). Rejected: the two baselines
  must stay schema-compatible for the lockstep re-baseline discipline, and the shared
  helper kills the advisory's cosmetic false-rotation noise at the same cost
  (counterweight: skipping it is the MORE expensive path — two incompatible schemas).
- **Reusing the `code_family_ids` key with changed meaning.** Rejected: a stale
  checkout would misread nose ids as fingerprints; a new key + schema bump degrades
  safely (→ advisory) instead of mis-gating. (Load-bearing per S4-D7's safety proof.)
- **Subset-aware reduction diff or collision-proofing in v1** (S4-Defer-3 / PQ1).
  Rejected for v1: membership-shrink is non-regressive (S4-D9) and natural collisions
  are precluded (PQ1); both are over-build for an operator-approved D30 offset fix.

### Success Criteria

1. A pure member-file line-shift (no duplication added/removed) yields NO new code
   family (no hard-block) — the D30 bug is fixed, locked by a real-nose test.
2. A genuine new/changed duplicated span yields a new fingerprint and hard-blocks
   (no false-negative; D30's blocking concern resolved).
3. Distinct nose families ↔ distinct fingerprints on the live corpus (PQ1 measured),
   AND a golden-value unit test pins a known-good fingerprint for a fixed
   `(file,start,end)` span (an offset-consistent off-by-one read passes SC1/SC2 but
   fails the golden value — adversary F3), AND `fp({A,A,B}) != fp({A,B})` (no
   `set()`-collapse — adversary F2).
4. An uncomputable fingerprint degrades the whole gate to advisory with a
   `degraded_reasons` entry, never blocks, never drops the family (FD8 / S4-D6).
5. Gate + advisory baselines AND the `dup-review.json` overlay migrated to fingerprints
   in lockstep in ONE commit; every `intentional` code id ∈ the migrated baseline (no
   orphaned-intentional disarm, S4-D8); a fresh checkout at the migration commit shows
   the dup-ratchet phase PASS/ADVISORY, never hard-block (S4-D7); full `quality_gates`
   suite green; `run-quality.sh --read-only` green with the live `dup-ratchet` phase
   PASS within budget.
6. Plugin mirror in lockstep; the real-nose characterization test reshaped — the
   nose-id-rotates assertion STAYS (documents the behavior we route around) and a NEW
   gate-fingerprint-stable test asserts the fix; `docs/deferred-decisions.md` D30
   marked RESOLVED.
7. The reference documents the S4-D9 membership-change-rotates-identity behavior as
   expected re-baseline maintenance (not a surprise), and the PQ2 in-place-edit
   limitation honestly (v1 rotates where nose would not).

### Acceptance Checks

- `tests/quality_gates/test_dup_ratchet.py`:
  - KEEP `test_real_nose_family_id_rotates_on_member_line_shift` (nose still rotates
    — the "why we route around nose" anchor) and ADD
    `test_gate_content_fingerprint_stable_on_member_line_shift` (same fixture; assert
    the gate fingerprint is unchanged across the shift) [SC1].
  - ADD `test_content_fingerprint_changes_on_span_content_change` [SC2].
  - ADD a uniqueness assertion on a synthetic multi-family fixture, a golden-value
    assertion for a fixed span, and `fp({A,A,B}) != fp({A,B})` [SC3].
  - ADD a missing-member-file → whole-gate-degrade test (asserts `degraded_reasons`,
    not a dropped family) [SC4].
  - ADD an orphaned-intentional guard: with a migrated overlay, every `intentional`
    code id is present in the migrated fingerprint baseline [SC5].
  - `nose_fingerprint_lib` units: offset-invariance, path-invariance,
    member-order-invariance, multiplicity-sensitivity, content-sensitivity,
    read-failure → `None`.
  - migrate existing policy-test fixtures from injecting `family_id` to injecting
    `family_fingerprint` (else they pass for the wrong reason — empty new set);
    decide whether the `family_id` read path is removed or kept as a no-op (no dead
    seam) [operational F7].
- `validate_gate_baseline` accepts the bumped schemaVersion + `code_family_fingerprints`
  + string `fingerprint_algo_version`; rejects the stale combination (no dual-read).
- Plugin mirror-drift gate + `pytest tests/quality_gates/ -q` green.

### File plan

1. `skills/public/quality/scripts/nose_fingerprint_lib.py` — NEW. `FINGERPRINT_ALGO_VERSION`,
   `normalize_span`, `member_fingerprint`, `family_content_fingerprint(family,
   repo_root) -> str | None` (PINNED algorithm S4-D2; reads RAW `locations`,
   duplicate-preserving, `None` on read/range failure).
2. `nose_report_lib.py` — `collect_families` stamps `family["family_fingerprint"]`
   from full `locations` (S4-D5); rewrite the `tool_version_skew` message text so it
   no longer says "family_ids are scanner-version-scoped" — the family SET (which
   spans nose groups) is nose-version-scoped, the IDENTITY is a content fingerprint
   (adversary F7).
3. `dup_ratchet_lib.py` — baseline build/load/validate `code_family_ids` →
   `code_family_fingerprints` (loader reads ONLY the new key, no dual-read); bump
   `GATE_BASELINE_SCHEMA_VERSION` → `...v2`; add `fingerprint_algo_version` stamp + an
   `algo_version_skew` helper (sibling of `tool_version_skew`); rewrite
   `GATE_BASELINE_NOTE` CHURN CAVEAT (now offset/path-independent; re-baseline on
   genuine content/membership/nose-version/algo change). `evaluate` UNCHANGED — keep
   its `*_ids` param/verdict names (S4-D9).
4. `check_dup_ratchet.py` — `_scan_code_family_ids` reads the stamped
   `family_fingerprint` (degrade-whole-gate on `None` per S4-D6); `--code-inventory`
   reads injected `family_fingerprint` else computes from `locations`; update docstring
   CHURN CAVEAT + the skew note. The one-time migration write is NOT delta-guarded —
   `_write_baseline` reads the old key as `None` → the guard is skipped → it writes
   plainly (no `--confirm-baseline-delta` needed; operational F2); the guard resumes
   for all post-migration re-baselines.
5. `nose_baseline_lib.py` + `inventory_nose_clones.py` — advisory migrates in lockstep
   via the stamped field; bump `BASELINE_SCHEMA_VERSION` → `nose_baseline.v3`; update
   notes. (The advisory has no delta guard at all — its migration is a plain
   `--write-baseline`.)
6. `dup_review_lib.py` (+ `seed_dup_review.py`) — `family_records` code identity
   `family_id` → stamped `family_fingerprint` (S4-D8a); the seed thereafter writes
   fingerprint-keyed entries.
7. `charness-artifacts/quality/dup-review.json` — one-time member-preserving REMAP of
   the 33 code entries' `id`s (nose → fingerprint), preserving the 31 manual notes,
   dropping orphaned ids (S4-D8b). A throwaway migration helper builds the
   `nose_id → fingerprint` map from one live scan; NOT the add-only seed.
8. `charness-artifacts/quality/dup-ratchet-baseline.json` + `nose-baseline.json` —
   one-time lockstep migration re-baseline to fingerprint sets under the new schema,
   in the SAME commit as steps 1–7 and 10.
9. `skills/public/quality/references/dup-ratchet.md` — replace the offset-rotation
   CHURN CAVEAT + "Re-Baseline Triggers" with fingerprint semantics; ADD the S4-D9
   membership-change-still-rebaselines note and the PQ2 in-place-edit v1 limitation
   (SC7).
10. `integrations/tools/nose.json` — reconcile the pre-existing drift the seed depends
    on: floor + "0.14.0 / schema v4 / 0.14.0-seeded" wording → the 0.15.0 / schema-v6
    reality the fingerprint baseline is seeded on (the gate baseline is version-scoped,
    so a 0.14.0 binary vs a 0.15.0 fingerprint baseline is the false-block the manifest
    warns about — operational F4). Bump the floor to `>=0.15.0` or justify keeping it.
11. `tests/quality_gates/test_dup_ratchet.py` — the reshape + new tests (Acceptance).
12. `sync_root_plugin_manifests.py` before validators (rmtree+re-export mirror).
13. `docs/deferred-decisions.md` D30 → RESOLVED (Slice 4), pointer to this spec; add
    `dup-review.json` to the impact-surface list it originally omitted.

### Critique

Execution: completed via bounded fresh-eye subagents (3 angles + 1 counterweight)
through the host Agent tool, 2026-06-27.
Fresh-Eye Satisfaction: parent-delegated.
Packet Consumed: `charness-artifacts/critique/2026-06-27-093537-packet.md`.
Target: `references/spec-critique.md`.
Reviewer Tier Evidence — Requested tier: high-leverage; Requested spawn fields:
model=gpt-5.5, reasoning_effort=medium, service_tier=priority; Host exposure state:
metadata-hidden (the host Agent tool does not expose model/effort/tier spawn fields;
reviewers ran on the parent's available high-leverage model). Application state:
parent spawned three angle reviewers (implementer-misread, adversarial-correctness,
operational-migration) and one counterweight; host accepted the agents but did not
confirm tier metadata application.

Angles: implementer-misread (Weinberg), adversarial-correctness (try-to-break),
operational-migration (Gawande); separate counterweight pass.

Structured Findings (acted before lock unless noted):

- F1 | bin: Act Before Ship | evidence: strong | ref: dup-review.json overlay /
  evaluate:239 | note: 33 nose-id-keyed `intentional` code entries (27 live, 31 manual)
  would silently disarm after the swap → false-block on every accepted family. FIXED:
  S4-D8 (member-preserving overlay+seed identity migration) + SC5 orphaned-intentional
  guard + File-plan steps 6–7,13.
- F2 | bin: Act Before Ship | evidence: strong | ref: S4-D2 | note: algorithm
  under-specified (RAW locations vs truncated sample_locations; repo_root join; "tuple"
  ambiguity; set()-collapse collision; line-base). FIXED: S4-D2 pinned verbatim with
  the code block + dup-preserving rule; SC3 golden value + `fp({A,A,B})!=fp({A,B})`.
- F3 | bin: Act Before Ship | evidence: strong | ref: File plan §5 / _write_baseline |
  note: the "delta guard fires, use --confirm-baseline-delta" claim is wrong (old key →
  None → guard skipped). FIXED: File-plan step 4 — migration write is plainly not
  delta-guarded, guard resumes post-migration.
- F4 | bin: Act Before Ship | evidence: strong | ref: S4-D9 / SC1 | note:
  membership-shrink (removing one of N copies) hard-blocks a legitimate reduction; the
  spec presented membership-sensitivity only as a feature. FIXED: S4-D9 documents it as
  non-regressive expected re-baseline; SC7 + reference note; S4-Defer-3 for the
  subset-aware option.
- F5 | bin: Act Before Ship | evidence: strong | ref: load/validate | note: schema
  migration must be single-new-key, loader reads only it, no dual-read, names kept.
  FIXED: S4-D4 + S4-D9.
- F6 | bin: Bundle Anyway | evidence: moderate | ref: S4-D5/S4-D6 | note: stamp the
  fingerprint centrally (no per-consumer truncation), `None` → whole-gate degrade with
  a reason (never drop a family). FIXED: S4-D5 report-layer stamping + S4-D6.
- F7 | bin: Bundle Anyway | evidence: moderate | ref: S4-D4 / skew | note: two skew
  axes (nose tool_version + fingerprint algo_version) must each name its axis and
  neither degrade; rewrite the stale "family_ids scanner-scoped" message. FIXED:
  File-plan steps 2–3.
- F8 | bin: Bundle Anyway | evidence: moderate | ref: nose.json | note: pre-existing
  0.14.0/schema-v4 drift vs the 0.15.0 seed; reconcile here (version-scoped baseline).
  FIXED: File-plan step 10.
- F9 | bin: Over-Worry | evidence: strong | ref: PQ1 / S4-Defer-2 | note: natural
  fingerprint collisions precluded by global clustering (only a negligible 64-bit
  birthday residual); the vanish/shrink-then-recur false-negative is honest and
  narrow. No change beyond wording; recorded so not relitigated (PQ1 reframed as an
  implementation-collision guard; S4-Defer-2 widened to include shrink-then-recur).
- F10 | bin: Valid but Defer | evidence: moderate | ref: PQ2 / S4-Defer-1 | note:
  rstrip-only is a *different* (in-place) false-positive class, not "strictly rarer."
  FIXED wording: PQ2 reframed; SC7; S4-Defer-1 retained.

Counterweight Triage: bundle verdict PROCEED (cut list: nothing). The new module,
the lockstep advisory migration, and the `fingerprint_algo_version` stamp each trace
to an existing same-file pattern (nose_report_lib split; tool_version skew; FD8
ladder) and are cheaper to include than the divergence they'd otherwise create —
kept. S4-Defer-1 (token-aware normalization) and S4-Defer-2/3 held DEFERRED against
any push for v1 token-normalization, collision-proofing, or subset-aware diffs:
membership-shrink is non-regressive and natural collisions are precluded, so those
are over-build for an operator-approved offset fix. The deferral steelman (D30 was
right to defer a path-set re-key that carried a real false-negative) is overcome
because the content fingerprint is gate-side and content-derived, proven by the
empirical anchor to rotate on a real span edit.

### Canonical Artifact

This spec (Slice 4 of `charness-artifacts/spec/boy-scout-dup-ratchet.md`) is canonical
during implementation.

### First Implementation Slice

1. Build `nose_fingerprint_lib.py` + its unit tests (offset/path/order invariance,
   multiplicity, content-sensitivity, read-failure, golden value, `fp({A,A,B})`) and
   run the live-corpus PQ1 uniqueness + PQ2 in-place-edit + PQ3 perf probes FIRST —
   de-risk the algorithm before touching the gate.
2. Stamp `family_fingerprint` in `collect_families` (S4-D5).
3. Migrate the gate (`dup_ratchet_lib` + `check_dup_ratchet`), the advisory, the seed
   (`dup_review_lib`), and the overlay+both baselines (member-preserving remap) — all
   in ONE lockstep commit with the mirror sync (S4-D7/D8).
4. Reference + nose.json reconcile + D30 resolution.

### Slice 4 DONE (2026-06-27)

All 13 file-plan steps landed in one lockstep commit. Verified on live nose 0.15.0:
SC1 (`test_gate_content_fingerprint_stable_on_member_line_shift`) + SC2
(`..._changes_on_span_content_change`) green alongside the retained nose-rotation
characterization; the live corpus probe confirmed PQ1 (541 families → 541 distinct
fingerprints, no collision), PQ3 (+0.10s, total scan 0.64s — within budget), and zero
degrades; the live `check_dup_ratchet` runs CLEAN against the migrated v2 baseline; the
old v1 baseline + new code degrades-to-advisory (S4-D7 safety proven). Full
`quality_gates` + `tests/` suites green.

Deviations / notes for the next reader:

- **Family count 538 → 541.** The implementation's deliberate axis-symmetry helpers
  (`algo_version_skew` mirroring `tool_version_skew`; `load_gate_baseline_algo_version`
  mirroring the tool-version loader; `build_baseline`≈`build_gate_baseline` with the new
  `algo_version` stamp) formed near-clone families. The two in-file loaders were deduped
  via `_baseline_string_field`; the cross-module skew pair and the advisory/gate builder
  parallel were left as intentional symmetry (a shared abstraction would add cross-module
  coupling for 2-line helpers — consistent with the overlay's existing "small parallel
  helper, keep local" intentional class) and accepted into the re-baseline like the rest.
- **Overlay remap (S4-D8): 27 code remapped + 5 doc kept, 6 already-stale orphans
  dropped** (5 carried manual notes). The 6 referenced nose ids absent from the live scan
  — i.e. families that vanished/rotated in PRIOR work — so they suppressed nothing even
  before the migration (their notes describe families no longer scanned; preserved in git
  history). Orphaned-intentional guard (SC5) passes: every surviving code overlay id ∈ the
  migrated baseline.
- **nose.json floor bumped `>=0.14.0` → `>=0.15.0`** to match the 0.15.0-seeded fingerprint
  baselines (the prior 0.14.0 wording was pre-existing drift from the v0.56.7 0.15.0
  re-baseline; operational-critique F4). The family SET stays nose-version-scoped, so the
  tool_version skew warning still applies.
- **S4-D5 central stamping confirmed necessary:** the overlay seed consumes the truncated
  `family_summary` (`sample_locations`, capped at 6), so it cannot compute its own
  fingerprint — `collect_families` stamps `family_fingerprint` once and `family_summary`
  propagates it to every consumer.
- PQ2 (in-place comment-edit residual) and S4-Defer-2/3 remain deferred as specified; the
  reference documents the v1 limitation and the membership-shrink re-baseline honestly.

### Slice 4 Impl Critique (2026-06-27)

Bounded fresh-eye CODE critique via the prepare packet
(`charness-artifacts/critique/2026-06-27-103255-packet.md`): 2 angle reviewers
(code-correctness / migration-integrity) + 1 separate counterweight, all parent-delegated.
Fresh-Eye Satisfaction: parent-delegated. Verdicts: code-correctness CORRECT (no
mis-gating bug — independently verified the pinned algorithm, central stamping, degrade
ladder, no-dual-read, both skew axes, injected seam); migration-integrity SOUND on the
data (lockstep-identical 541-fp sets, SC5 orphaned-intentional guard passes, all 27
survivor notes preserved verbatim, byte-identical mirror parity, nose.json history
preserved) with one honesty defect; counterweight SHIP.

Acted before commit:

- **Migration F1 (Bundle):** the member-preserving overlay remap rewrote `dup-review.json`
  entry `id`s but left the stored top-level `note` as the stale "code: nose family_id"
  text (the sibling `DEFAULT_NOTE` + both baseline notes were already corrected). Synced
  the overlay note to the canonical `DEFAULT_NOTE` — the gate never parses it, but it was
  exactly the identity-honesty drift this slice removes.
- **Correctness F1 (Over-Worry, doc-fidelity):** the S4-D2 pinned pseudocode wrote
  `sha256(...)[:16]` (missing `.hexdigest()`); the code was already correct
  (`.hexdigest()[:16]`). Corrected the pseudocode so a future copy-paste does not regress.
- **Correctness F2 (Over-Worry, test-hygiene):** `test_inproc_no_version_skew_on_legacy_unstamped_baseline`
  passed its `clean` assertion via an empty injected set; switched it to inject
  `family_fingerprint` so it asserts "known1 ∈ baseline" + added a `new_code_families == []`
  check.

Counterweighted Over-Worry (recorded, not relitigated): the two cross-module
parallel-helper near-clones left local (pre-existed slice 4; a shared abstraction for
axis-specific ~12-line helpers adds coupling for negative gain); the nose.json floor bump
(reconciles genuinely stale 0.14.0 provenance the 0.15.0 seed depends on); the 6 dropped
orphaned overlay entries (absent from the live scan, suppressed nothing, notes in git
history); the membership-shrink case (non-regressive, documented, subset-aware diff
deferred to S4-Defer-3). The overlay keeping `dup_review.v1` is correct (member-preserving
remap, shape unchanged).
