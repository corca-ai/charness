# Achieve Goal: North-star overhaul sweep: per-unit-disposition consolidation + skill-redesign

Status: draft
Created: 2026-06-20
Activation: `/goal @charness-artifacts/goals/2026-06-20-north-star-overhaul-sweep.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: **ready to activate** (Discuss-before-activation resolved
  2026-06-20) — `/goal @charness-artifacts/goals/2026-06-20-north-star-overhaul-sweep.md`.
  First slice on activation = S0 (concept spec + critique).
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

Make charness's public skills **and** the closeout gate-script layer embody the
validated north-star doctrine (equip a judge; teeth only where a wrong answer
escapes; **non-terminal per-unit disposition over terminal-green**; at
irreversible boundaries confirm via a **distinct observer AND a distinct evidence
channel**). Two workstreams, concept-first:

- **WS-A (Phase 2) — per-unit-disposition consolidation.** The cluster
  (operator-queue #381, blocked-matrix #385, coordination-cues, the disposition
  rungs, issue closeout, the #386 disposition-review) is one abstraction wearing
  N masks. Collapse to **one shared concept**: a rung-1 presence/form floor (shared
  grammar) + a single rung-2 distinct-channel observer mandate. Sequence inside:
  - **R2 first (the real open escape):** the #386 per-issue distinct-channel
    behavioral verdict exists in code only on the achieve-bundle path; the
    standalone `issue resolve`/PR-close path has **no coded rung-2** — `CLOSED`
    state is the terminal-green proxy. Wire the distinct-channel observer mandate
    + an **AI-provenance marker** onto that boundary.
  - **R1 then:** extract the rung-1 grammar that is cloned ~4x
    (`mask_fences`/`_section_body`/`created_gate`/opt-out/placeholder) into one
    shared substrate; operator-queue / blocked-matrix / coordination become thin
    configs.
- **WS-B (Phase 3) — skill bloat-audit + concept-separation + principle-over-rulebook**
  on the capped SKILL.md bodies, using the absorbed instruments (no-op deletion
  test, three length-causes diagnosis, Leading Word Rule, body-altitude,
  named-heuristic-over-do-nots, load-bearing-anchor split, show-one-instance).

**Success = a wrong answer's escape path closed (R2) AND concepts got clearer /
genuine duplication removed (R1 + WS-B).** "Fewer lines / fewer gates" is NOT the
metric (it is a north-star failure signature).

## Non-Goals

- **Not bulk gate deletion.** Per-surface migration discipline only: name the
  failure-mode → land the replacement → prove it catches a *seeded* instance →
  only then delete the old surface + record a rollback ref.
- **Not an 8th terminal-green gate** (the #386 anti-pattern). Rung-1 stays
  presence/form-only; per-unit *honesty* stays a rung-2 human-audited observer.
  A deterministic gate that greens on self-classification re-grants the exact
  terminal trust the cluster abused.
- **Not "fewer lines" as success.** Measure concept clarity + closed escapes.
- **Not the full 21-body rewrite this goal** — scope is the named first
  candidates; the rest defers (see Discuss item 2).
- **Not the separate tracks:** #388 mutation regression, #371 chromium cleanup,
  #392 gather-X — orthogonal, out of scope.

## Boundaries

- **Concept-first (gating).** S0 specs the shared per-unit-disposition concept
  (rung-1 + rung-2) + the Phase-3 instrument set, and it is **locked by critique**
  before any implementation slice.
- **Six consolidation risk-constraints are binding** (from the cluster-survey,
  `wf_f03ba5fe-62d`): (1) carry transition *direction* + a no-runnable-contradiction
  predicate so #385's wrong-**block** mirror-image is not inverted; (2) preserve
  each floor's narrow trigger as a per-unit predicate (no false-fire from a
  unioned enumerator); (3) preserve per-concept `RULE_DATE` grandfathering +
  fail-closed on undatable goals; (4) rung-1 stays presence/form (no rung-1→rung-2
  collapse); (5) carry forward every anti-bypass guard (fence-masking,
  Auto-Retro-scoped opt-out, first-satisfying-wins, placeholder-as-blank);
  (6) the issue-path rung-2 must be **actually wired**, not assumed-present.
- **Phase-3 framing (operator, 2026-06-20):** progressive disclosure is
  *endorsed* (push reference behind a branch-reliable pointer); the guard is
  reference **sprawl/sediment**, not disclosure — apply the no-op test +
  three-length-causes to references too, and watch reference count/size. WS-B also
  grafts one `quality/references/unit-test-quality.md` (better-UT patterns:
  determinism harness; properties/invariants in the test; observable-contract +
  one-reason-to-fail; in-process real-collaborators-by-default;
  map-behavior/edge-cases) under cap, P3 worked-example-not-do-not-list, routed
  from the Behavior lens *below* `testability-and-selection.md`.
- **Governing-surface edits** (design-north-star.md, AGENTS.md,
  portable-authoring.md, skill bodies, gate scripts) each get a **bounded
  fresh-eye critique before commit**.
- External side-effect scope: R2 touches the GitHub issue/PR-close path. Default
  = implement + test + seeded-instance proof **locally**; any **live** GitHub
  close/comment is operator-approved and phase-scoped, and that approval does not
  carry forward.

## User Acceptance

What the user can do to verify completion directly.

- Read the S0 spec + the Phase-3 instrument set and confirm they embody the
  doctrine (no terminal-green gate added; rung-1/rung-2 split explicit).
- R2: on a *seeded* closed issue, confirm the standalone issue/PR-close path now
  records a per-issue distinct-channel behavioral verdict (or a typed
  non-verified disposition) + an AI-provenance marker — not a `CLOSED`-only green.
- R1: confirm the rung-1 grammar lives in one shared module and
  operator-queue/blocked-matrix/coordination are thin configs; the locked floor
  tests still pass; net script lines fell *without* losing a guard.
- WS-B: confirm the named first-candidate bodies were de-pinned by the *right*
  cure (impl/debug = floor-extract de-dup; quality/find-skills = concept-separate),
  negative-directive counts fell, the no-op test was applied, and concept clarity
  rose (not just line count).
- Gate suite green at the bundle boundary.

## Agent Verification Plan

### Low-Cost Checks

- Commit boundary: `validate_skills`, `check_skill_contracts`, `check_doc_links`,
  `check-markdown`, `ruff`, `check_python_lengths`, the locked floor tests for any
  touched gate, plugin-mirror sync + `staged-plugin-mirror-drift`.

### High-Confidence Checks

- Slice boundary: bounded fresh-eye critique per slice; **seeded-instance proof**
  for each migrated floor (the replacement catches the seeded failure *before* the
  old surface is deleted); `run_slice_closeout.py`.

### External Or Live Proof

- Bundle boundary: broad pytest (record the verification lock).
- R2 live GitHub close proof: only if the operator approves; otherwise record
  `skipped:` and name the un-run proof level honestly.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| S0 | Concept spec + critique (gating): the shared per-unit-disposition concept (rung-1 shared floor + rung-2 distinct-channel observer) + the Phase-3 instrument set | concept-first decision; gates every impl slice | spec artifact under `charness-artifacts/spec/` + critique PASS folded | pending |
| S1 (R2) | Wire the #386 distinct-channel observer + AI-provenance marker onto the standalone issue/PR-close path (the open escape) | issue-path rung-2 absent in code today | seeded-issue proof + fresh-eye + tests; no terminal-green gate added | pending |
| S2 (R1) | Extract the cloned rung-1 grammar into one shared substrate; operator-queue/blocked-matrix/coordination → thin configs | de-dup; the substrate R2's rung-1b binding reuses | locked floor tests green + net line drop + fresh-eye | pending |
| S3 (WS-B) | Phase-3 audit + redesign first candidates: impl/debug (floor-extract), quality/find-skills (concept-separate), achieve (headroom) — apply no-op test + length-causes + leading words; **+ graft `quality/references/unit-test-quality.md`** (better-UT patterns 1-5, P3 worked-examples) | the capped bodies; instruments now defined in S0 | per-body cause-diagnosis + cut + negative-directive count drop + new reference under cap + fresh-eye | pending |
| S4 | Closeout: broad proof, retro, dispositions, honest non-claims | bundle boundary | final verification populated | pending |

## Operator Decision Queue

Record decisions, confirmations, credential actions, manual proof steps, and
external-boundary approvals discovered during the run when they do not block
safe local progress. Use `none — <reason>` when the queue is empty at closeout.

Queue item form:

- Decision: operator-only decision or confirmation needed
- Owner: operator or named human owner
- Why deferred: why the run did not stop immediately
- Unblock action: exact action or answer needed
- Revisit trigger: event, date, or proof boundary that reopens this

## Discuss before activation

Resolved — all consequential defaults confirmed with the proposed values
(operator, 2026-06-20: "나머지 동의"). No open activation discussion remains.

1. **R2 / GitHub external writes** — RESOLVED: implement + test + seeded-instance
   proof **locally**; any **live** GitHub close/comment is operator-approved and
   phase-scoped (approval does not carry forward).
2. **Phase-3 breadth** — RESOLVED: named first candidates only (impl, debug,
   quality, find-skills, achieve); the remaining ~16 capped bodies defer to a
   follow-on goal.
3. **Phase-3 deletion aggressiveness** (roadmap open question) — RESOLVED:
   migration-discipline-cautious (land replacement + seeded proof, *then* cut +
   rollback ref) while applying the no-op deletion test rigorously *within* that.
4. **Structure** — RESOLVED: one achieve goal (operator choice). The
   bundle-closeout #386 risk is mitigated by per-slice critique + this goal's own
   non-terminal, per-unit closeout (no aggregate green).

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns. At completion, recorded
  implementation / debug / quality / issue work needs this `Routing:` evidence
  or a `Routing: n/a — <reason>` opt-out.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`.

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- [Phase-0 diagnosis back-test](../audit/2026-06-20-north-star-phase0-diagnosis-backtest.md) — the validated diagnosis + the distinct-channel + mirror-image corrections.
- [Reference-absorption note](../audit/2026-06-20-reference-absorption-overhaul-inputs.md) — matt-skills + craken net-new adoptions + Phase-3 instruments.
- [north-star overhaul roadmap](../../docs/north-star-overhaul-roadmap.md) and [design north star](../../docs/design-north-star.md) — the plan of record + the governing doctrine.
- [closeout-floor audit](../audit/closeout-floors.md) — the floor stack (stale: predates #381/#385/#386).
- [the complete Track-1a pilot](2026-06-18-north-star-overhaul.md) — the #386 seed this goal continues.
- cluster-survey workflow `wf_f03ba5fe-62d` (per-unit-disposition family map, the rung-1/rung-2 shape, the 6 risk-constraints) — not a checked-in file; folded into the S0 spec.

## Interview Decisions

- **Sequencing:** concept-first + staged migration (chosen) vs safety-first-R2
  vs dedup-first-R1. Chosen because the operator wants the concept locked +
  critiqued before any impl; R2→R1 ordering lives *inside* the staged migration.
- **Structure:** one achieve goal (chosen) vs independent issues per workstream.
  Operator chose the goal lifecycle; the bundle-closeout risk it carries (#386) is
  mitigated by per-slice critique + this goal's non-terminal per-unit closeout.
- **Reference inputs:** matt-skills + craken folded (operator-directed), under
  baseline discipline — only genuine net gaps counted; convergent doctrine is a
  citation, not an adoption.
- **External skills evaluated (2026-06-20, the craken "pending share" arrivals):**
  `bug-hunt` = MOSTLY-CONVERGENT (charness `debug` ≥; no absorption). `better-UT`
  = MOSTLY-CONVERGENT + one narrow gap → the WS-B `unit-test-quality.md` graft.
  Per-surface evals recorded in the
  [reference-absorption addendum](../audit/2026-06-20-reference-absorption-overhaul-inputs.md).

## Plan Critique Findings

_S0 folds the concept-spec critique here before implementation begins._

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

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
