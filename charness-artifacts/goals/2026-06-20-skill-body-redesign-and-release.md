# Achieve Goal: Skill-body redesign (all 20 public bodies, diagnosis-first) -> release

Status: draft
Created: 2026-06-20
Activation: `/goal @charness-artifacts/goals/2026-06-20-skill-body-redesign-and-release.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: **S1 (cure the 3 sub-buffer must-fix: issue / impl / debug)** —
  S0 is **complete and committed** (diagnosis spec LOCKED, gating critique
  PASS-WITH-CONDITIONS folded). The full diagnose-and-cure scope (all 20 public
  bodies) and the terminal live-release slice are operator-resolved.
- Current slice intent: apply the S0-diagnosed cures to issue / impl / debug. All
  three are `duplication` (guardrail-cluster collapse + single-source); issue and
  impl carry **pin hazards** (test-literal pins) so the pre-cut check
  (`scripts/check_skill_cut_safety.py`) + a per-body fresh-eye are load-bearing
  here. Use the verbatim-preserve path (do not update a pinned test). Re-sync the
  plugin mirror before validators.
- Next action: cure `issue/SKILL.md` per the S0 disposition row — run the pre-cut
  check, apply the duplication collapse preserving the pinned literals verbatim,
  re-measure, fresh-eye, then impl and debug.
- S0 deliverables (locked): `scripts/check_skill_cut_safety.py` (+ test, docs,
  drift-guard); disposition table for all 20 bodies in
  [2026-06-20-skill-body-diagnosis-disposition.md](../spec/2026-06-20-skill-body-diagnosis-disposition.md)
  (19 cure + 1 defer-with-cause `hotl`); raw verified records in the sibling
  `...-diagnosis-results.json` / `...-measured-input.json`.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`,
  and `## Auto-Retro`.

## Goal

Redesign **all 20 public SKILL.md bodies** for **concept clarity and headroom**,
diagnosis-first, applying the locked Phase-3 instrument set
([per-unit-disposition spec §5](../spec/2026-06-20-per-unit-disposition-concept.md):
no-op deletion test, three length-causes, Leading-Word Rule, named-heuristic-over-
do-nots, load-bearing-anchor split, body-altitude, show-one-instance). For **each**
body: diagnose the length *cause* (**sediment** / **duplication** / **sprawl**)
**before** any cure; apply the cure the diagnosis warrants (prune / single-source
cite / disclose-split to a reference / collapse a negative-bullet cluster to one
named heuristic / anchor roster → reference); and **defer a justified-density body
WITH CAUSE** rather than force a cut. Then cut a **release** whose live publish
exercises the WS-1 rung-1/rung-2 non-terminality floors landed in Phase-4 — the
deferred WS-1 live-floor proof.

**Success = (a)** each body de-pinned by the *right* cure (re-measured, not a
pre-committed mandate): concept clarity raised and headroom restored where the
diagnosis warrants, or an explicit *defer-with-cause* where density is justified;
**(b)** no lost content — every removed phrase has a reference home AND no test or
CORE-contract pins it; **(c)** a live release confirmed via a channel **distinct
from `gh release view`**, exercising the WS-1 floors. **"Fewer lines / lower core
count" is NOT the metric — in either direction** (the
[goodhart retro](../retro/2026-06-20-goodhart-not-line-count.md): line count is
orthogonal to success; lead with the capability/clarity delta, never the diff).

Measured starting state (`core_nonempty`, cap 160, ratchet buffer 4): 3 already
**under-buffer** (issue 159 / impl 158 / debug 157); 8 more **crammed** at 150–156
(create-skill 156, achieve 156, hitl 155, release 155, create-cli 155,
find-skills 152, announcement 152, critique 150); the rest 103–149. This is
context for sequencing, **not** the target — S0 re-measures and the diagnosis
decides each body.

## Non-Goals

- **Not a trim-to-160 sweep / line-count-as-metric** — the north-star failure
  signature ([goodhart retro](../retro/2026-06-20-goodhart-not-line-count.md)). A
  body whose length is justified density is **deferred with cause**, not cut to a
  number.
- **Not a lossy cut.** No phrase leaves a body without a reference home AND a
  verified absence of any test/CORE-contract pin (the WS-B pre-cut instrument gap
  from recent-lessons).
- **Not a references/scripts re-audit.** Sprawl-split moves prose *to* references,
  but this goal does not separately re-audit reference bodies beyond guarding the
  reference sprawl/sediment a body cure itself creates.
- **Not the unit-test-quality graft** — already landed (overhaul-sweep S3,
  `f496812b`).
- **Not the ceal #417 doctrine propagation** — separate repo/track; unblocked by
  Phase-4 but out of this goal's scope.
- **Not the secondary gate demotions** (`check_doc_links` backtick→advisory;
  `--reuse-coverage` skip) — separate follow-ups.
- **Not #391 / #392 / #371 / #394 (mutation regression) / #395** — orthogonal
  open tracks.

## Boundaries

- **Diagnosis-first is gating.** S0 produces a per-body length-cause + a
  cure/defer-with-cause disposition table for all 20 bodies, **locked by a bounded
  fresh-eye critique** before any cure slice. **Bloat diagnoses are hypotheses to
  verify per body, not mandates to cut** (recent-lessons; the overhaul-sweep
  caution carried forward).
- **Pre-cut lossless + contract-safe check (binding, every cure).** Before
  removing any phrase: (a) it has a reference home, and (b) no test or
  CORE-contract pins it — verified *before* the cut, not after a gate rejects it.
  Build/confirm a cheap **deterministic** helper for this in S0 (turn the WS-B
  instrument gap into a declarative check, not a manual ritual).
- **Headroom-measure-first.** Measure the core buffer *before* adding any line;
  mechanism detail belongs in a reference from the start, not after a
  `long_core`/`core-headroom` rejection (recent-lessons WS-1 churn: 3 edit cycles
  on one bullet).
- **Per-body fresh-eye before commit.** Each body cure is a governing
  skill-surface edit → bounded fresh-eye critique before commit. Reviewers run in
  the **shared parent worktree**: inspect prior versions read-only
  (`git show <ref>:<path>`), never run index/worktree-mutating git ops
  ([fresh-eye-subagent-review](../../skills/shared/references/fresh-eye-subagent-review.md)).
- **Success = concept clarity + headroom-where-warranted, never count.** For equal
  capability: less prose, more declarative, more open (the operator's ordering).
  A roomy-core body with a real clarity problem (e.g. an anchor catalog exempt
  from the core count) still gets the right cure; a dense body with no clarity
  problem is left alone with cause.
- **Release terminal slice.** The live publish is **operator-approved +
  phase-scoped at run** (approval does not carry forward); rung-2 confirms the
  published release via a channel **distinct from `gh release view`** (the WS-1
  floor). Release-tracked issues close through the non-terminal closeout floors,
  never a terminal-green.
- **Sync barriers (mutate → sync → verify → publish).** Re-sync the `plugins/`
  mirror (`sync_root_plugin_manifests.py`) before validators — the
  `staged-plugin-mirror-drift` gate fails an unsynced SKILL.md edit. Generated /
  export surfaces sync before the gate suite.
- **Public-skill validation discipline.** Each cured public body routes through
  the public-skill validation path (Cautilus eval-only / ask-before-run; recorded
  fresh-eye review; dogfood-case refresh) per the repo contract — 20 bodies means
  20 such passes, batched at slice boundaries.

## Discuss before activation

Discuss before activation: RESOLVED — the two consequential, scope-shaping
defaults were settled with the operator in this shaping conversation (2026-06-20);
recorded so a fresh session inherits the resolution rather than re-litigating it.

- **Scope = all 20 public bodies — RESOLVED.** Operator chose the full
  diagnose-and-cure pass over the entire public surface (over "3 sub-buffer only"
  and "11 crammed only"). Diagnosis runs on all 20; cures commit where the
  length-cause warrants; justified-density bodies are deferred with cause. `axis:
  surface-coverage`.
- **Live release at the terminal slice — RESOLVED.** Operator chose: the release
  is this goal's terminal slice, and the **live publish** is operator-approved +
  phase-scoped *at that point* (Phase-4 ODQ pattern; approval does not carry
  forward). It serves as the deferred WS-1 live-floor proof, confirmed via a
  channel distinct from `gh release view`. `axis: external-write boundary`.

## User Acceptance

What the user can do to verify completion directly.

- Read the S0 diagnosis table and confirm every body carries a **named
  length-cause** + a **cure-or-defer-with-cause** disposition; no body is marked
  "cut" without the cause and the pre-cut lossless+contract-safe check.
- For a sample of cured bodies, confirm every removed phrase has a reference home
  and no test/CORE-contract regressed; `validate_skills`, `check_skill_contracts`,
  `check_skill_surface_preflight` (core-headroom), `staged-plugin-mirror-drift`
  all green.
- Confirm at least one body was **deferred with cause** where density is justified
  — i.e. the goal did **not** force every body down (proof that count was not the
  metric).
- Confirm concept clarity rose: spot-read a cured body and confirm it reads
  clearer / the judge is still equipped, not merely shorter.
- **Release:** on the live cut, confirm the publish path recorded a per-surface
  behavioral verdict + a rung-2 distinct-channel confirmation **before**
  issue-closeout — not a `gh release view` returncode-only green.
- Gate suite green at the bundle boundary (broad pytest).

## Agent Verification Plan

### Low-Cost Checks

- Commit boundary: `validate_skills`, `check_skill_contracts`,
  `check_skill_surface_preflight` (core-headroom ratchet), `check_doc_links`,
  `check-markdown`, `ruff`, `check_python_lengths`; the **pre-cut
  lossless+contract-safe check** per cured body; the skill-ergonomics,
  attention-state-visibility, and prose-pin gates; plugin-mirror sync +
  `staged-plugin-mirror-drift`.

### High-Confidence Checks

- Slice boundary: bounded fresh-eye critique per cure slice; per-body
  **re-measurement proving the cure addressed the *diagnosed* cause** (not just the
  count); `run_slice_closeout.py`; the public-skill validation path (Cautilus
  eval-only + recorded fresh-eye + dogfood refresh) per cured public skill.

### External Or Live Proof

- Bundle boundary: broad pytest (record the verification lock).
- Terminal slice: the **live release** (operator-approved + phase-scoped)
  exercising the WS-1 rung-1/rung-2 floors, confirmed via a channel distinct from
  `gh release view`. If the operator does not approve the live cut, record
  `skipped:` and name the un-run proof level honestly (the WS-1 live-floor proof
  stays deferred — Honest Proof Discipline).

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| S0 | Diagnosis spec + gating critique: measure all 20 cores; apply the §5 instrument set diagnostically per body; produce a per-body length-cause + cure/defer-with-cause disposition table; build/confirm the pre-cut lossless+contract-safe check (declarative, not manual); lock with a bounded fresh-eye critique | concept-first; the diagnosis IS the contract that gates every cure | diagnosis artifact under `charness-artifacts/spec/` (or `audit/`) + the pre-cut check + critique PASS folded | **complete** (2026-06-20): disposition spec LOCKED (19 cure + 1 defer `hotl`); `check_skill_cut_safety.py` + test + docs + drift-guard landed; gating critique PASS-WITH-CONDITIONS folded |
| S1 | Cure the 3 sub-buffer must-fix (issue 159 / impl 158 / debug 157): apply the S0-diagnosed cures; pre-cut check; re-measure; fresh-eye; public-skill validation | they already violate the 4-line ratchet buffer — highest value, land first | each body de-pinned by the right cure (or deferred with cause); lossless+contract-safe; mirror synced; fresh-eye PASS | pending |
| S2 | Cure crammed batch B (create-skill / achieve / hitl / release): per-body diagnosed cure or defer-with-cause; pre-cut check; re-measure; fresh-eye; validation | the next-tightest cluster (155–156) | same evidence shape as S1 | pending |
| S3 | Cure crammed batch C (create-cli / find-skills / announcement / critique): same discipline | the remaining ≥150 crammed set | same | pending |
| S4 | Diagnose-and-cure-or-defer the headroom tier (gather / spec / ideation / retro / narrative / setup / handoff / hotl / quality): expect mostly defer-with-cause; cure only where the diagnosis genuinely warrants (e.g. quality's anchor-catalog sprawl — a §5 anchor-split *hypothesis* to confirm against the actual catalog, not a pre-committed cut) | completes the all-20 scope without forcing cuts on already-roomy bodies | per-body disposition: cured-with-cause or deferred-with-cause; no count-driven cut | pending |
| S5 | Release terminal slice: bump version + sync install manifests + announcement; **live publish operator-approved + phase-scoped**; rung-2 distinct-channel confirmation; close any release-tracked issues through the non-terminal floors | the body redesign is the release payload; the live cut is the deferred WS-1 live-floor proof | release proof; distinct-channel verification recorded; mirror synced; WS-1 floors exercised | pending |
| S6 | Closeout: broad proof (verification lock), retro, disposition every surfaced improvement, honest non-claims, flip to complete | bundle boundary | Final Verification populated; disposition review (rung 2); gate suite green | pending |

S0's diagnosis may re-batch S1–S4; the plan table is up-front intent, the Slice
Log is execution truth. **Prior-cure note:** `find-skills` (S3) already took a
partial named-heuristic cure in `f496812b` (negative-directive 7→4, lossless) yet
is still 152 core — S0 diagnoses its *residual* cause and does not re-litigate the
landed collapse.

## Operator Decision Queue

Operator-only decisions surfaced at shaping; none blocks safe local progress
through S0–S4.

- Decision: approve the **live GitHub release** at the terminal slice (S5) that
  exercises the WS-1 rung-1/rung-2 floors.
  - Owner: operator
  - Why deferred: the goal scopes S0–S4 to local diagnose + cure + seeded/gate
    proof; the live publish is operator-approved + phase-scoped (approval does not
    carry forward), and is the deferred WS-1 live-floor proof.
  - Unblock action: operator names a target version (bump level) and approves one
    live release run at S5.
  - Revisit trigger: reaching S5 with all body cures landed and the gate suite
    green.
- Decision: any body the S0 diagnosis flags as needing a **contract change** (a
  CORE-contract pin or a pinned test that should move) beyond a prose cure.
  - Owner: operator
  - Why deferred: a contract/test move is a wider blast radius than a body-prose
    cure; surface it rather than silently re-home a pinned obligation.
  - Unblock action: operator confirms the contract/test relocation, or the body is
    deferred-with-cause.
  - Revisit trigger: S0 diagnosis flags a CORE-contract-pinned phrase.

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns. At completion, recorded
  implementation / debug / quality / issue work needs this `Routing:` evidence
  or a `Routing: n/a — <reason>` opt-out. (Expected: S0 → `spec`/`quality` +
  `critique` (gating); cure slices → `create-skill`/`quality` (skill-surface
  authoring) + `critique`; S5 → `release` + `announcement` + `critique`; S6 →
  `retro` + `critique`.)
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>`. (Expected `Gather: n/a` —
  shaped from in-repo doctrine only.)
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`. (Expected: S5 cuts a real release →
  a bound `Release:` proof line.)
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`.

## Slice Log

### S0 — diagnosis spec + gating critique (complete, 2026-06-20)

- **Built the pre-cut lossless+contract-safe check** (`scripts/check_skill_cut_safety.py`):
  composes `check_skill_contracts` CORE/PACKAGE after-state pins + `check_prose_pin`
  test-literal scan (BLOCK, deterministic) and adds the lossless reference-home half
  (REVIEW, surfaced not blocked — a hard "every removed line must reappear" rule
  would forbid the §5 no-op prune cure). Locked by
  `tests/quality_gates/test_check_skill_cut_safety.py` (7 cases), documented in
  `docs/conventions/authoring-preflight.md`, drift-guarded in
  `tests/test_authoring_preflight_reference.py`.
- **Diagnosed all 20 bodies** via a background Workflow (40 agents: 20 diagnose +
  20 adversarial verify): 15 `duplication`, 3 `mixed`, 1 `sprawl`, 1
  `justified-density`. **19 cure + 1 defer-with-cause (`hotl`)** — proves count was
  not the metric. Dominant signature: `## Guardrails` clusters that negate the
  Workflow/references → §5.5 named-heuristic collapse + §5.2 single-source.
- **Key finding:** the adversarial verify caught 4 of 20 proposed cures (issue,
  impl, find-skills, retro) would break a pin the diagnosing agent missed (dedicated
  test-literal files + a paraphrased package pin). Diagnosis is a hypothesis; the
  pre-cut check + per-body fresh-eye are mandatory before each cure. All 4 have a
  verbatim-preserve path → no contract change required.
- **Gating critique:** bounded fresh-eye PASS-WITH-CONDITIONS (distinct channel:
  re-measured 6 cores, grepped 4 test files, ran the check). Two precision
  conditions folded; spec LOCKED.
- Routing: `find-skills` → S0 = `spec`/`quality` validation + `critique` (gating);
  Cautilus `next_action: none` (ask-before-run, disabled this run).
- Gates green: ruff, check_python_lengths, validate_skills, check_doc_links,
  check-markdown, attention-state-visibility, affected pytest.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order. (No external
URL/Slack/Notion/Docs/Drive source — `Gather: n/a` expected.)

- [per-unit-disposition concept spec §5](../spec/2026-06-20-per-unit-disposition-concept.md)
  — the **locked Phase-3 instrument set** (7 instruments) + per-body redesign
  hypotheses for debug/quality/impl/find-skills/achieve to re-measure. (Note: that
  spec's `§9` "Full **21**-body rewrite" line is stale — it predates a
  since-removed body; the current public surface is **20**, re-measured
  2026-06-20. S0 works the live 20, not the spec's 21.)
- [goodhart retro](../retro/2026-06-20-goodhart-not-line-count.md) — count is not
  the metric, in either direction; lead with the capability/clarity delta.
- [Phase-4 goal](2026-06-20-north-star-phase4-boundary-non-terminality.md) — the
  **structural template** for this goal + the WS-1 rung-1/rung-2 release-publish
  floors the terminal live release exercises.
- [overhaul-sweep goal](2026-06-20-north-star-overhaul-sweep.md) +
  [its retro](../retro/2026-06-20-north-star-overhaul-sweep.md) — the deferred
  WS-B body redesign; bloat-diagnoses-are-hypotheses; the pre-cut
  lossless+contract-safe instrument gap this goal closes.
- [recent-lessons](../retro/recent-lessons.md) — the pre-cut lossless+contract-safe
  check and headroom-measure-first traps.
- [design north star](../../docs/design-north-star.md) — the governing doctrine
  (equip a capable judge; teeth only where a wrong answer escapes).
- `scripts/check_skill_surface_preflight.py` — the `core_nonempty` metric (strip
  frontmatter + the pressure-exempt `Load-Bearing Anchors`/`References` sections),
  cap `MAX_CORE_NONEMPTY_LINES = 160`, buffer 4, total-file `MAX_SKILL_MD_LINES =
  200`/`NEAR_CAP_WARN_LINES = 195`. The measurement source of truth.
- **Measured-state snapshot (folded inline, 2026-06-20):** ≥150 core (11): issue
  159, impl 158, debug 157, create-skill 156, achieve 156, hitl 155, release 155,
  create-cli 155, find-skills 152, announcement 152, critique 150. 140–149 (5):
  gather 149, spec 148, ideation 147, retro 146, narrative 144. <140 (4): setup
  137, handoff 125, hotl 114, quality 103 (bulk in pressure-exempt
  Load-Bearing-Anchors → its core is roomy but the anchor catalog is the §5
  anchor-split candidate).

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- **Body scope.** Family: (A) 3 sub-buffer only / (B) 11 crammed (≥150) / (C) all
  20. **Chosen: C (all 20)** (operator, 2026-06-20). `axis: surface-coverage`.
  Rejected: A leaves 8 crammed-but-legal bodies as future debt; B skips the
  diagnostic value of confirming the roomy bodies are roomy *with cause* (and
  catches non-core clarity issues like quality's anchor catalog).
- **Release end-state.** Family: (A) terminal live slice / (B) prepare-only +
  stop / (C) separate follow-on goal. **Chosen: A (terminal live slice,
  operator-approved + phase-scoped)** (operator, 2026-06-20). `axis: external-write
  boundary`. Rejected: B defers the WS-1 live-floor proof yet again; C fragments
  the body-redesign → release payload.
- **Run mode.** Family: artifact-only (shape + stop) vs implementation-
  continuation. **Chosen: artifact-only** ("설계 시작" = design the goal; `/goal`
  activation is the operator's separate action — this draft does not execute
  slices).
- **Diagnosis vs mandate.** Family: pre-commit cures from the prior audit vs
  diagnosis-first re-measure. **Chosen: diagnosis-first** (locked doctrine + the
  retro that bloat diagnoses are hypotheses, not mandates to cut).
- **Anti-anchoring axis records:** body scope = `axis: surface-coverage` (cure
  where diagnosed, not where the count is highest); release = `axis: external-write
  boundary` (operator-approved + phase-scoped); the metric = `axis: clarity`, never
  `axis: line-count`.

## Plan Critique Findings

**Bounded fresh-eye DRAFT critique — PASS-WITH-CONDITIONS (2026-06-20), folded.**
A different agent context, read-only (Read/Grep/`git show`, no worktree mutation),
verified the draft against the locked doctrine and **independently re-measured all
20 core counts** (a distinct evidence channel) — every number matched. It
confirmed: next action correct (artifact-only; `/goal` is the operator's separate
act); scope (all 20, diagnosis-first) carries **no** trim-to-160 mandate; the §5
instruments + the `core_nonempty` constants (cap 160 / buffer 4 / total 200 /
warn 195 / pressure-exempt `{Load-Bearing Anchors, References}`) are accurately
quoted; no Slice-Plan cell over-commits to a cut before S0 re-measures; the release
boundary is correctly operator-approved + phase-scoped + distinct-channel; the
Non-Goals (unit-test graft already landed `f496812b`; ceal #417 out of scope) are
right.

**Three clarity conditions folded (none a blocker):**

- **Spec §9 "21-body" vs the live 20-body surface** — the
  per-unit-disposition spec's `§9` says "Full 21-body rewrite" but the live public
  surface is 20 (a body was removed since). Folded: a staleness note on the spec
  link in `## Context Sources` so the S0 reviewer does not flag a false
  scope-mismatch.
- **`find-skills` prior partial cure** — `f496812b` already landed a
  named-heuristic collapse on `find-skills` (7→4 negative directives), yet it is
  still 152 core. Folded: a prior-cure note under the Slice Plan so S0 diagnoses
  the *residual* cause, not the settled collapse.
- **`quality` anchor-catalog framed as hypothesis** — tightened the S4 row so the
  anchor-split reads as a §5 *hypothesis to confirm against the actual catalog*,
  not a pre-committed cut (symmetry with diagnosis-first).

**Over-worries raised but deliberately NOT folded** (recorded so a fresh session
does not re-add rigor): the S1–S4 tier-ordered batching could *look* like
count-as-metric, but the draft pre-empts it ("context for sequencing, **not** the
target") and every cure cell defers to the diagnosis — tier-ordering is legitimate
triage, not a Goodhart target. Reviewer agreed; no change.

**Reviewer provenance:** bounded fresh-eye subagent (distinct `general-purpose`
context), read-only inspection, re-ran the core-count measurement script. The
deeper **gating** critique still runs at S0 during activation, against the **actual
body text**, before any cure lands.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

Concrete commands a maintainer can run to verify completion directly (filled at
closeout). Expected shape:

- **Diagnosis (S0):** read the diagnosis artifact under `charness-artifacts/` —
  confirm each of the 20 bodies has a named length-cause + cure/defer disposition.
- **Cures (S1–S4):** `python3 scripts/check_skill_surface_preflight.py` headroom
  on the cured paths; the pre-cut lossless+contract-safe check; `validate_skills`;
  `staged-plugin-mirror-drift`.
- **Release (S5):** the release proof + the distinct-channel verification record
  (a channel other than `gh release view`).
- **Bundle:** `python3 -m pytest -q tests/` green at the verification lock.

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
