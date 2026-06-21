# Achieve Goal: North-star overhaul sweep: per-unit-disposition consolidation + skill-redesign

Status: complete
Created: 2026-06-20
Activation: `/goal @charness-artifacts/goals/2026-06-20-north-star-overhaul-sweep.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: **COMPLETE** (closeout done 2026-06-20). All five slices landed:
  S0 (concept spec locked) + S1 (R2 escape closed) + S2 (R1 grammar collapsed) +
  S3 (WS-B graft + find-skills cure; deeper redesign deferred with cause) + S4
  (bundle proof + retro + dispositions).
- Outcome: WS-A fully delivered (the primary success — a wrong answer's escape
  path closed at issue/PR close, via rung-1/rung-2, no terminal-green gate + the
  rung-1 grammar collapsed to one substrate). WS-B delivered the unit-test-quality
  graft + one lossless body cure; deeper body redesign deferred with cause (the
  cuts are contract-blocked or lossy — forcing them is the north-star failure
  signature). Bundle proof: broad pytest 3428/0.
- Open operator items (do not block completion): live R2 proof **SATISFIED via #395
  (2026-06-21)**; WS-B body-redesign follow-on tracked **file-over-issue** (no GitHub
  issue, per operator) — see `## Operator Decision Queue`.
- Locked spec (gates all impl):
  [per-unit-disposition concept](../spec/2026-06-20-per-unit-disposition-concept.md).
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
  map-behavior/edge-cases; **fixture/DSL *authoring* principles** —
  plain-literals-first, valid/minimal/visible defaults, avoid cause/effect-hiding
  fluent chains) under cap, P3 worked-example-not-do-not-list, routed from the
  Behavior lens *below* `testability-and-selection.md`. Boundary: graft the
  test-DSL *authoring principles* only — the DSL *review* lens is already stronger
  in `testability-and-selection.md:121-170`, and charness still ships no
  stack-specific DSL implementation (consumer repos build their own).
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
| S0 | Concept spec + critique (gating): the shared per-unit-disposition concept (rung-1 shared floor + rung-2 distinct-channel observer) + the Phase-3 instrument set | concept-first decision; gates every impl slice | spec artifact under `charness-artifacts/spec/` + critique PASS folded | **done** (spec locked; critique PASS-WITH-CONDITIONS folded 2026-06-20) |
| S1 (R2) | Wire the #386 distinct-channel observer + AI-provenance marker onto the standalone issue/PR-close path (the open escape) | issue-path rung-2 absent in code today | seeded-issue proof + fresh-eye + tests; no terminal-green gate added | **done** (rung-1 block-the-silent + provenance floors wired; 6 seeded tests; fresh-eye PASS-WITH-CONDITIONS folded; cautilus refused per policy) |
| S2 (R1) | Extract the cloned rung-1 grammar into one shared substrate; operator-queue/blocked-matrix/coordination → thin configs | de-dup; the substrate R2's rung-1b binding reuses | locked floor tests green + net line drop + fresh-eye | **done** (goal_artifact_floor_grammar.py; parser 5→1, section_body 3→1; 380 floor tests green; strict→permissive swap tested; net −28 lines; fresh-eye PASS) |
| S3 (WS-B) | Phase-3 audit + redesign first candidates: impl/debug (floor-extract), quality/find-skills (concept-separate), achieve (headroom) — apply no-op test + length-causes + leading words; **+ graft `quality/references/unit-test-quality.md`** (better-UT patterns 1-6 incl. fixture/DSL authoring principles, P3 worked-examples) | the capped bodies; instruments now defined in S0 | per-body cause-diagnosis + cut + negative-directive count drop + new reference under cap + fresh-eye | **done (scoped)** — graft landed (82 lines, under cap, fresh-eye PASS) + find-skills named-heuristic cure (neg-directive 7→4, lossless); deeper body redesign (impl/debug/quality/achieve) **deferred with cause**: verification showed cuts blocked (quality anchors contract-pinned by 11 tests) or lossy (impl bullets distinct, one CORE-pinned) — forcing them = the line-count failure signature. Operator-corrected mid-slice (no shaving). |
| S4 | Closeout: broad proof, retro, dispositions, honest non-claims | bundle boundary | final verification populated | pending |

## Operator Decision Queue

Operator-only decisions surfaced at closeout (neither blocks safe local progress;
both are external-write boundaries the goal contract scopes out by default).

- Decision: run a **live** GitHub `issue resolve` / PR-close that exercises the new
  R2 rung-1 floors (behavioral-verdict + AI-provenance) on a real issue.
  - Owner: operator
  - Why deferred: the goal contract scopes R2 to local implement + test +
    seeded-instance proof; any live close/comment is operator-approved and
    phase-scoped (approval does not carry forward). Local seeded proof is complete.
  - Unblock action: operator names a target issue and approves one live
    close/comment run.
  - Revisit trigger: the next real `issue resolve` of a bug/feature/deferred-work
    issue once the operator approves the external write.
  - **SATISFIED 2026-06-21:** #395 (bug) was resolved+closed via a live
    `issue resolve` exercising the R2 rung-1 floors — per-issue behavioral verdict
    (distinct channel: a green real-nose characterization test + the dogfooded
    case-2 recovery, not a CLOSED-only green) + AI-provenance marker;
    `verify-closeout --expect-state CLOSED` verified, confirmed via `gh` SoT.
    This is the live proof the goal deferred. Commit `6658acec`.
- Decision: track the **deferred body-redesign follow-on**
  (impl/debug/quality/achieve concept-separation + the pre-cut lossless+contract-safe
  WS-B instrument).
  - Owner: operator
  - **DECISION 2026-06-21 (operator): file-over-issue.** Do NOT file a GitHub
    issue — the deferral already has a documented cause and a file home (this goal's
    S3 slice log + the overhaul-sweep retro `## Next Improvements`/`## Sibling
    Search`), and needs no tracker lifecycle. Promote to a goal when the WS-B
    body-redesign is actually started.
  - Unblock action: start the follow-on goal directly from the retro/S3 record.
  - Revisit trigger: starting the WS-B body-redesign follow-on.
  - **APPROVED + VERIFIED 2026-06-21 (operator): the `quality` anchor-split (the
    first unblock step) is approved AND its lossless+contract-safety is proven.**
    A bounded fresh-eye adversarial verifier (distinct channel; read the actual
    files, told to REFUTE "lossless") returned **`LOSSLESS-ACHIEVABLE` via
    concept-separation** with a bullet-by-bullet orphan hunt = ZERO irreducible
    orphans. Root cause of the prior S3 defer identified: it tried *delete-without-
    merge* of the distinct-routing anchors (`inventory_ci_recoverable_gates.py`,
    dup-ratchet/boundary-bypass routing, the Python/JS lint baselines), which
    orphaned them — concept-separation with *targeted merge* fixes exactly that.
    Refinement on the verifier: the two `"canonical routing lives in SKILL.md"`
    pointers (`quality-lenses.md:20`, `automation-promotion.md:48`) refer to the
    smell-sensor graduation PRINCIPLE (stays in SKILL.md), NOT the inventory
    routing — so they stay green unchanged (no pointer flip needed).
  - **Ready-to-execute plan (the next slice):** (1) MERGE the ~8 distinct-routing
    anchors into `references/inventory-dispatch.md` (Runtime gains
    `inventory_ci_recoverable_gates.py` + ci-recoverable-gate-triage; Source Hygiene
    gains a boundary-bypass/dup-ratchet subsection; Language/Adapter gains the
    ruff/C90/mypy + eslint/tsc/complexity baselines; Skills/CLI/Docs gain the smell-
    list phrases the tests pin). (2) DE-DUP the 3 already-present anchors
    (`recommend_behavior_test.py`, the source-guard rollup, the smaller-surface
    principle already in `quality-lenses.md`). (3) FOLD the ~6 judgment principles
    into SKILL.md `## Workflow`/`## Guardrails` VERBATIM (preserve the pinned strings
    `"Do not treat a passing length, duplicate, or pressure heuristic as the goal"`
    + `"delete, merge, split ownership, extract a helper, or narrow the interface"`).
    (4) Replace `## Load-Bearing Anchors` with a short branch-reliable pointer to
    `references/inventory-dispatch.md` (Workflow step 2 already points there).
    (5) RE-POINT ~38 `assert "X" in skill_text` in
    `tests/quality_gates/test_quality_skill_docs.py` to the new home — **the green
    test suite IS the losslessness oracle** (every must-survive phrase is pinned).
    Caveats: the 4 language-lint asserts (`test ...language_lint_defaults`, L191-196)
    must flip `quality_skill`→dispatch read; do NOT re-point `Standing Test
    Economics` (L168, passes vs Output Shape) or `structural smell sensors` (L166,
    intro) — moving them regresses. (6) sync mirror, verify, fresh-eye critique,
    commit. Then the impl/debug/achieve bodies follow the same recipe.
  - **EXECUTED 2026-06-21 (the `quality` anchor-split landed).** The `## Load-Bearing
    Anchors` catalog was dissolved exactly per the plan: distinct/duplicated routing →
    `references/inventory-dispatch.md` (verbatim phrases), CORE-contract + judgment cues
    folded into `SKILL.md` `## Workflow`/`## Guardrails`, the catalog replaced by a short
    `## Routing` pointer. SKILL.md 200/200 → 191/200 (9 headroom restored). ~40 test pins
    re-pointed across `test_quality_skill_docs.py` + `test_docs_and_misc.py` +
    `test_quality_dual_implementation.py` (the green losslessness oracle). Proof: full
    `tests/quality_gates/` = 2283 passed; `check_skill_contracts` (13 core + 8 package),
    `validate_quality_closeout_contract`, `validate_skills`, ergonomics, markdown,
    doc-links, mirror-drift all green; `--verification-lock` closeout exit 0. Three
    distinct-channel fresh-eye reviewers returned `LOSSLESS-CONFIRMED` /
    `RELOCATION-SOUND` / `SEPARATION-HONEST` (zero orphans; cautilus-refuse safety stays
    in the always-loaded body and gate-enforced). Critique:
    [2026-06-21-quality-anchor-split](../critique/2026-06-21-quality-anchor-split.md).
    Two deferred NITs recorded there. The impl/debug/achieve bodies remain the follow-on
    (same recipe).
  - **EXECUTED 2026-06-21 (the `impl` body redesign landed) — supersedes the S3
    "deferred with cause (lossy: impl bullets distinct, one CORE-pinned)" note.**
    Operator reframed the work: distill to essence + DELETE duplication, not
    relocate (`less but better`, progressive disclosure). The clean cut the prior
    pass thought was blocked is the **unpinned duplication around the pins** — the
    gate pins (CORE/PACKAGE contracts + impl/cautilus test asserts) mark the
    load-bearing essence, so deleting everything unpinned-and-duplicated needs
    **zero** edits to `check_skill_contracts.py` or any test. Guardrails 9→2 via
    `achieve`'s name-the-rule-don't-restate pattern (the in-repo template);
    Workflow step 4 13 sub-bullets→4 by deferring browser/lint/external-API/
    completion-report rules to `references/verification-ladder.md` (which already
    owns them); worktree-doctor bullet consolidated; 194→187 lines. Proof: full
    `tests/quality_gates/` = 2283 passed; `check_skill_contracts` (13 core + 8
    package), `validate_skills`, ergonomics, markdown, doc-links, mirror-drift all
    green; 2 distinct fresh-eye reviewers `ESSENCE-PRESERVED` /
    `CONTRACT-HONEST-AND-FAITHFUL`. dogfood case[12] consumer contract re-frozen
    (scenario review: `impl-adapter-bootstrap` unchanged). Critique:
    [2026-06-21-impl-essence-deletion](../critique/2026-06-21-impl-essence-deletion.md).
    Recipe now proven; `debug` (triple cross-ref, helper-prose) + `quality`
    (relocated-not-deleted, 49 refs) are the next exemplar-rollout targets.
  - **Operator agreed 2026-06-21: OPEN THE PINS for the rollout.** impl stayed at
    unpinned-dup-only (the safe ceiling); the agreed next step deletes gate-pinned
    contracts too, under a disciplined test — a pin earns deletion only when it (a)
    freezes wording rather than proving behavior, or (b) the behavior is owned
    canonically elsewhere (`CLAUDE.md` / a reference / another gate). Deleting a pin
    deletes its test + contract row, so **green `main` is the prerequisite** (the
    green suite is the losslessness oracle): sequence is green-main → `debug`
    (safe) → `quality` as the pin-opening pilot (undo the relocation + fold/kill
    the 49-ref sprawl). Promote the pin-deletion test to a durable convention once
    proven on `debug`/`quality`.

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

**S2 (R1) impl critique — PASS (2026-06-20), folded.** Bounded fresh-eye reviewer
verified against actual code + ran the tests + ran ruff on canonical AND mirror
(distinct evidence channel). 6 checks confirmed: 3 permissive consumers
behavior-preserving; the strict→permissive swap real + pinned by divergence-input
tests; the ≥7 RULE_DATEs still separate per floor; fail-closed/grandfather intact;
narrow triggers + anti-bypass guards untouched; substrate a pure leaf; no clone
missed; operator-queue/blocked-matrix H2-list `_section_body` correctly kept
separate (level-aware migration deferred — needs the P-e `###`-subsection proof).
De-dup judged **genuine** (single source of truth: parser 5→1, section_body 3→1),
not line-count churn. No conditions. The extraction also surfaced a latent
accidental divergence (two floors parsed `Created:` more strictly than three
others) and turned it into one deliberate, tested decision.

**S3 (WS-B) critique — PASS (2026-06-20), folded.** Bounded fresh-eye reviewer
verified A-E against actual files + ran gates: the unit-test-quality.md graft is
authoring-only (no dup-ratchet with `testability-and-selection.md`'s review lens);
the find-skills named-heuristic collapse is lossless (3 layer-honesty cases
preserved in one principle, neg-directive 7→4, not contract/test-pinned); **no
shave remains** (debug + the quality body byte-identical to HEAD); the graft is
net-new + under cap; all gates green. The reviewer independently judged the
deferral of deeper impl/debug/quality/achieve redesign the **correct north-star
call** (no safe lossless cut missed; the two reverts — a debug in-place shave and
a lossy/contract-blocked quality catalog move — were right). **Operator correction
folded:** compressing a capped body in place is the P2 anti-pattern; the proper
cure is concept-separation / de-dup / named-heuristic, verified lossless +
contract-safe before cutting, measured by concept clarity not line count.

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
  - Routing: find-skills `--recommend-for-task` recommended issue (S1), impl (S2), quality (S3) — every recorded slice was routed via find-skills; per-slice detail below.
  - S0 (concept spec + critique): `find-skills --recommend-for-task` →
    `achieve` (owner) coordinating `spec` (concept-spec authoring) + `critique`
    (gating fresh-eye review). Spec authored inline under achieve; gating critique
    run as a bounded fresh-eye subagent. `Routing: spec + critique`.
  - S1 (R2 impl): `find-skills --recommend-for-task` → `issue` (owns the closeout
    surface; impl-style slice on it) + `critique` (slice fresh-eye). Cautilus
    refused (`plan_cautilus_proof` next_action=none, ask-before-run);
    deterministic gates + fresh-eye own closeout. `Routing: issue + critique`.
  - S2 (R1 impl): `impl` (gate-script refactor on the achieve floor surface) +
    `critique` (slice fresh-eye). Cautilus refused (next_action=none).
    `Routing: impl + critique`.
  - S3 (WS-B): `quality` (skill bloat-audit + the unit-test-quality graft on the
    quality surface) + `create-skill`/`impl` (skill-body redesign) + `critique`
    (slice fresh-eye). Cautilus refused (next_action=none).
    `Routing: quality + critique`.
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

### Slice 1: S0 — Concept spec + critique (gating)

- Objective: Author the shared per-unit-disposition concept spec (rung-1 presence/form floor + rung-2 distinct-channel observer) + the Phase-3 instrument set under charness-artifacts/spec/, and lock it with a bounded fresh-eye critique before any implementation slice.
- Why this approach: Concept-first per the goal: the cluster (operator-queue #381, blocked-matrix #385, coordination-cues, disposition rungs, issue closeout, #386) is one abstraction wearing N masks; a locked shared concept gates all impl. Three parallel read-only Explore passes mapped the R2/R1/WS-B surfaces; load-bearing claims re-verified by direct reads.
- Commits:
- What changed: Created charness-artifacts/spec/2026-06-20-per-unit-disposition-concept.md (Status: locked). Defines: the two-rung abstraction; the no-terminal-green invariant; R2/S1 wire (rung-1 block-the-silent presence floor + AI-provenance marker + rung-2 observer onto issue/PR close); R1/S2 substrate boundary (unify parse_created_date/is_floor_in_scope/placeholder-markers/parametric opt-out; keep RULE_DATEs/triggers/_section_body-divergence separate); the 6 risk-constraints mapped to code anchors; the Phase-3 instrument set + per-body re-measure hypotheses + the unit-test-quality graft scope/placement; Fixed Decisions F1-F7, Probes P-a..P-e, testable Success Criteria, Rejected Alternatives.
- Alternatives rejected: Bulk gate deletion / fewer-gates-as-metric (north-star failure signature); an 8th terminal-green self-classification gate (#386 anti-pattern); keep R2 judgment-only (lets a silent carrier ride CLOSED to done); naive union of opt-out/_section_body variants (carries real anti-bypass intent); full 21-body rewrite (out of scope).
- Targeted verification: Gating bounded fresh-eye critique = PASS-WITH-CONDITIONS; reviewer verified claims against actual code (distinct evidence channel). 4 conditions folded. Counts re-verified directly: grep confirmed >=7 RULE_DATE constants + 5 parse_created_date clones (initial map missed phase_routing). No code mutated this slice (spec-only).
- Test duplication pressure:
- Critique: PASS-WITH-CONDITIONS — folded into ## Plan Critique Findings + the spec's section 10. T1 (rung-1 != terminal-green) adjudicated distinct; T2/T3/T4 resolved; 4 blockers folded as S2 measurement-tightening conditions.
- Off-goal findings:
- Lessons carried forward: S2 must prove behavior-preservation per swap (created-date strict->permissive RELAXES grandfathering; 9 locked tests green on unchanged inputs = form-passed-not-content-correct). Surface maps from subagents can under-count (phase_routing missed) — re-verify load-bearing counts on a distinct channel before locking.
- Metrics:

### Slice 2: S1 (R2) — wire rung-2 distinct-channel observer + AI-provenance onto issue/PR close

- Objective: Close the open escape where the standalone issue/PR-close path treats CLOSED+ledger-form as terminal-green: wire a rung-1 block-the-silent behavioral-verdict presence floor + an AI-provenance presence floor onto issue closeout (verify-closeout / validate-closeout-draft / commit-msg hook), presence/form only, honesty stays rung-2.
- Why this approach: Per the locked S0 spec section 2: the prose mandate existed (closeout-discipline.md:106-138) but was unwired — issue_verify_closeout.py:262-263 greened status:verified on CLOSED+form only. The rung-1/rung-2 split is the third option between judgment-only and terminal-green; it forces the question without declaring completion (status:verified stays necessary-not-sufficient; a typed non-verified disposition satisfies the floor).
- Commits:
- What changed: issue_verify_closeout_body.py: evaluate_behavioral_verdict + evaluate_ai_provenance + _behavior_lines + has_ai_provenance_marker + Behavior #N: line grammar (mirrors Critique #N:). issue_verify_closeout.py: both floors wired into ok/status + result. check_issue_closeout_commit_msg.py: _format_failure surfaces the new floor failures (legibility). closeout-discipline.md: doctrine sync (replaced the stale 'no new gate/script/verdict token' clause with the rung-1/rung-2 split; PRESERVED the render-not-declare/no-aggregate #386 sentence). attention-state-visibility.json: registered issue_verify_closeout_body.py (new skipped_classification term). 5 test files + 6 new seeded tests. Plugin mirror synced. SKILL.md reverted (headroom-gate: detail belongs in the reference, not the capped body).
- Alternatives rejected: Hard-require the marker in close_with_comment (rejected: fires before backend logic, masks backend errors, breaks 7 unrelated tests; provenance enforcement belongs in the floor like ledger fields). Adding a SKILL.md guardrail (reverted: issue SKILL.md at 199 has <4-line headroom buffer; progressive disclosure keeps the rung-1/rung-2 detail in closeout-discipline.md). Gating close on aggregate 'all confirmed' (rejected: the #386 anti-pattern; floor demands rendering per issue, accepts typed dispositions).
- Targeted verification: 88 issue tests pass incl 6 new seeded (silent carrier FAILS before CLOSED greens; typed disposition PASSES; missing marker FAILS; question-class exempt; per-issue-in-bundle; validate-draft blocks-silent pre-mutation). run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review = exit 0 (validate_skills, check_skill_contracts, check_python_lengths, ruff, attention-state-visibility, skill-ergonomics, mirror-drift, doc-links all PASS). Cautilus refused: plan_cautilus_proof next_action=none, ask-before-run; deterministic+fresh-eye own closeout.
- Test duplication pressure: 6 new seeded tests target distinct behaviors (silent-fail, typed-disposition-pass, missing-marker-fail, class-exempt, per-issue-bundle, draft-pre-mutation-block); no duplicate-pressure with existing tests (those cover close-keywords/ledger/state/critique/source-preservation — orthogonal axes).
- Critique: PASS-WITH-CONDITIONS (bounded fresh-eye, verified against actual code+tests). 6 invariants CONFIRMED (presence-only, render-not-declare, classification-gate, necessary-not-sufficient, no-aggregate, doctrine-preserved); bypass holes clean (fence-strip, placeholder, single-issue-shorthand scoping, silent->verified closed). 2 conditions folded: (1) registered issue_verify_closeout_body.py in attention-state-visibility.json; (2) fixed the has_ai_provenance_marker docstring overstatement.
- Off-goal findings:
- Lessons carried forward: #386 trap, self-inflicted then caught: I 'confirmed pre-existing' the attention-state failure by stash-testing with the WRONG gate invocation (missing --scan-root skills --scan-root-map) — both stashed/unstashed runs failed identically for the wrong reason, masking that my change added a REAL new violation. The fresh-eye reviewer caught it by running the gate the enforcement way (distinct channel). Lesson: verify gate failures with the EXACT enforcement invocation, never a hand-rolled approximation. Touching a capped SKILL.md forces the 4-line headroom buffer — prefer pushing detail to references.
- Metrics:

### Slice 3: S2 (R1) — collapse the cloned rung-1 grammar into one shared substrate

- Objective: Extract the rung-1 grammar cloned across the Created-gated goal-artifact closeout floors (parse_created_date x5, is_floor_in_scope x6+, section_span/section_body x3) into one shared substrate; operator-queue/blocked-matrix/coordination/phase-routing/disposition become thin configs over it.
- Why this approach: Per locked spec section 3-4 + F4: this is the genuine duplication the goal names. The created-date parse was inconsistent (strict in operator_queue/blocked_matrix, permissive in 3 others) — an accidental divergence; unification makes it one deliberate, tested decision.
- Commits:
- What changed: NEW skills/public/achieve/scripts/goal_artifact_floor_grammar.py (pure leaf: parse_created_date permissive, is_floor_in_scope fail-closed grandfather, section_span/section_body level-aware). Migrated 6 consumers: operator_queue + blocked_matrix (strict->permissive swap, re-export parse_created_date/is_floor_in_scope), disposition_grammar + phase_routing + coordination_floors (zero-change: already permissive/level-aware), disposition.py (2 inline scope checks -> is_floor_in_scope). Kept separate per spec: the >=7 RULE_DATEs, narrow triggers, verdict fns, first-satisfying-wins, operator_queue/blocked_matrix H2-list _section_body (NOT migrated to level-aware). Plugin mirror synced.
- Alternatives rejected: Migrate operator_queue/blocked_matrix _section_body to the level-aware variant (rejected without a ###-subsection divergence proof, spec P-e). Unify the divergent opt-out matchers (deferred: 3 genuinely divergent forms — none/n-a/Auto-Retro-scoped; the spec allows keeping divergent things separate; the high-value de-dup is the parse grammar).
- Targeted verification: 380 goal/disposition/coordination floor tests pass; 2 NEW divergence-input behavior-preservation tests pin the strict->permissive swap (prefixed/list/lowercase pre-rule Created now grandfathers; plain forms unchanged). ruff clean (canonical + mirror). run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review = exit 0. Net script lines -28 with genuine duplication removed (parser 5->1, section_body 3->1, section_span 2->1).
- Test duplication pressure: 2 new tests target ONLY the strict->permissive divergence inputs (the case the locked plain-form tests cannot see) — no duplicate pressure with the existing floor tests, which cover trigger/verdict/scope behavior the substrate did not touch.
- Critique: PASS (bounded fresh-eye, no conditions). Verified against actual code + ran tests + ruff on canonical AND mirror. 6 checks CONFIRMED: 3 permissive consumers behavior-preserving; strict swap real+tested; >=7 RULE_DATEs still separate; fail-closed/grandfather intact; triggers/anti-bypass guards untouched; substrate a pure leaf; operator_queue/blocked_matrix H2-list _section_body correctly kept separate; no clone missed. De-dup judged GENUINE (single source of truth), not line-count churn.
- Off-goal findings:
- Lessons carried forward: An accidental divergence (2 floors parsed Created more strictly than 3 others) hid behind passing tests because the tests only used plain Created lines — extraction surfaced it and turned it into one deliberate, tested decision. De-dup value is single-source-of-truth + consistency, not line count (north-star metric).
- Metrics:

### Slice 4: S3 (WS-B) — unit-test-quality graft + one demonstrated body cure (find-skills); deeper body redesign deferred with cause

- Objective: Phase-3 skill bloat-audit + redesign per the locked spec section 5, measured by concept clarity not line count (P2/P3, no shaving).
- Why this approach: WS-B instruments: graft the better-UT authoring layer (genuine net gap); apply named-heuristic-over-do-nots / concept-separation to the capped bodies. Operator mid-flight correction (2026-06-20): in-place compression of a capped body is the P2 anti-pattern — do it properly (concept-separation/de-dup/named-heuristic, lossless) or not at all.
- Commits:
- What changed: ADDED skills/public/quality/references/unit-test-quality.md (82 lines, under cap): 6 better-UT patterns (determinism harness, invariants-in-test, observable-contract, real-collaborators-in-process, map-behavior/edge-cases, fixture/DSL authoring), each principle + one worked example, authoring-only, routed from the quality Behavior lens BELOW testability-and-selection.md (which keeps the DSL *review* lens). find-skills/SKILL.md: named-heuristic collapse — 3 layer-honesty do-nots merged into ONE 'Classify the capability layer honestly' principle (neg-directive 7->4, all 3 cases preserved, lossless). docs/handoff.md link fix. Plugin mirror synced.
- Alternatives rejected: REVERTED two non-proper attempts (operator correction): (1) debug in-place compression = a shave (P2 violation) -> reverted to HEAD; (2) quality Load-Bearing Anchors catalog->reference move -> reverted: verification showed it is NOT clean de-dup (orphaned check phrases) AND the anchors are contract-pinned to the body by 11 tests in test_quality_skill_docs.py + the 'consumer prompts use these anchors' contract. DEFERRED deeper body redesign for impl/debug/quality/achieve: careful verification found their cuts blocked (quality contract-pinned) or lossy (impl critique bullets are distinct rules, one CORE-pinned; bodies are concept-dense per the Phase-0 back-test). Forcing cuts to hit a line target is the north-star failure signature.
- Targeted verification: find-skills 7->4 neg-directive (lossless), 200->198 lines; all gates green (validate_skills, check_skill_contracts, ergonomics, headroom, doc-links, test_quality_skill_docs 22 passed). run_slice_closeout --skip-broad-pytest --ack-cautilus-skill-review = exit 0. Cautilus refused (next_action=none). No shave remains: debug + quality body byte-identical to HEAD.
- Test duplication pressure:
- Critique: PASS (bounded fresh-eye, no conditions). Verified A-E against actual files + ran gates: graft authoring-only (no dup-ratchet with testability-and-selection.md); find-skills collapse lossless (3 cases preserved, not contract/test-pinned); no shave remains (debug + quality body = HEAD); graft net-new + under cap; gates green. Independently judged the deferral the CORRECT north-star call (no safe lossless cut missed; the two reverts were right).
- Off-goal findings:
- Lessons carried forward: Operator correction internalized: a capped body at the cap is a signal to concept-separate or delete (no-op), NEVER to compress in place. And 'concept-separation' must be verified lossless (every removed phrase has a reference home) AND contract-safe (check test/CORE-contract pins) BEFORE cutting — quality's catalog failed both. The planning audits (reference-absorption 'flagship bloat'; Agent-3 collapse candidates) OVER-identified cuts; the bodies are concept-dense (Phase-0 back-test was right). Proper WS-B = deliver the clean additive graft + the genuinely-safe lossless cure, defer the rest with cause rather than force line-count wins.
- Metrics:

### Slice 5: S4 — closeout (bundle proof + retro + dispositions)

- Objective: Bundle-boundary broad proof, retro, disposition every surfaced improvement, honest non-claims, flip to complete.
- Why this approach: Achieve closeout: prove the goal at the bundle boundary and reflect honestly, with non-terminal per-unit dispositions (no aggregate green).
- Commits:
- What changed: Authored the retro (charness-artifacts/retro/2026-06-20-north-star-overhaul-sweep.md, validated, registered source #241); ran refresh_recent_lessons (lessons now extracted as candidates after a dash-bullet fix the rung-2 review caught); filled Final Verification (Retro bound; Host log probe skipped: host-log-not-exposed; Disposition review bound) + Auto-Retro dispositions + Structural follow-up + the Coordination Cues Routing line + Operator Decision Queue (2 external-write items).
- Alternatives rejected:
- Targeted verification: Broad pytest = 3428 passed, 0 failed (8m15s) — bundle proof green. check_goal_artifact ok at active; complete-flip gates next. Bounded fresh-eye DISPOSITION REVIEW (rung 2) = PASS WITH ONE CORRECTION: it verified every improvement is disposed + the S1/S2/S3 non-claims are honest against committed code, and caught a real overclaim (the retro's numbered Next Improvements were NOT extracted by recent_lessons_lib's dash-bullet-only parser, so 'captured in the digest' was false) — fixed by reformatting to dash bullets (now 20 candidate hits) + precise disposition wording.
- Test duplication pressure: n/a — closeout slice, no new tests added.
- Critique: Disposition review (rung 2): charness-artifacts/critique/2026-06-20-north-star-overhaul-sweep-disposition-review.md — PASS WITH ONE CORRECTION, correction folded (retro dash-bullet fix + precise wording). The distinct-channel rung-2 audit caught a memory-wiring overclaim a same-proxy re-read would have shipped.
- Off-goal findings:
- Lessons carried forward: Rung-2 distinct-channel review caught a third escape this goal: a disposition claimed 'captured in the wired digest' but the retro's numbered bullets were silently dropped by the dash-bullet-only extractor. Lesson: retro Next Improvements must be dash bullets to enter the recent-lessons candidate pool; verify the memory actually landed, do not assume refresh_recent_lessons captured it.
- Metrics:

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

**S0 concept-spec critique — PASS-WITH-CONDITIONS (2026-06-20), folded.**
Spec: [per-unit-disposition concept](../spec/2026-06-20-per-unit-disposition-concept.md)
(`Status: locked`). A bounded fresh-eye reviewer verified the spec's load-bearing
claims against the **actual code** (distinct evidence channel, not an artifact
re-read — the #386 discipline). Architecture (rung-1/rung-2, R2-first,
no-terminal-green) unchallenged; four conditions tightened the S2 measurement and
are folded into the spec:

1. Created-date unification is a **tested deliberate behavior change** (strict→
   permissive relaxes operator_queue/blocked_matrix grandfathering), not a no-op;
   each swapped consumer needs a divergence-input locked test. "9 locked tests
   pass" alone is rejected as S2 proof (greens on unchanged inputs).
2. **Counts corrected** (verified by `grep` over `skills/public/achieve/scripts/`):
   ≥7 RULE_DATE constants (the initial surface map missed `phase_routing` 6-4 and
   `recurrence_lineage` 6-8 + `disposition_form`/`structural_followup`); 5
   `parse_created_date` clones (incl. phase_routing).
3. `_section_body` unification needs a **divergence-exposing** seeded proof
   (`###`-subsection artifact), or the consumer keeps its own.
4. The `closeout-discipline.md:136-138` rewrite preserves the "render-not-declare /
   no aggregate all-confirmed" #386 sentence; only the stale "no new gate/script/
   verdict token" clause is replaced.

Load-bearing tension T1 (is the rung-1 issue floor a disguised terminal-green?)
adjudicated **distinct** — the achieve path already ships the non-terminal
rung-1b/rung-2 shape in code; the issue floor refuses silence only,
`status: verified` stays necessary-not-sufficient. Gate result: **S0 locked;
S1 may proceed.**

**S1 (R2) impl critique — PASS-WITH-CONDITIONS (2026-06-20), folded.** Bounded
fresh-eye reviewer verified all 6 invariants against the actual code + live tests
(presence-only; render-not-declare; classification-gate; necessary-not-sufficient;
no-aggregate; doctrine #386-sentence preserved) and probed bypass holes (fence
strip, placeholder, single-issue-shorthand scope, silent→verified path — all
closed). Two conditions folded: (1) registered `issue_verify_closeout_body.py` in
`attention-state-visibility.json` (the new `skipped_classification` term); (2)
corrected the `has_ai_provenance_marker` docstring (the write-site guard was
reverted; the floor owns enforcement). The reviewer also caught a **#386 trap I
fell into**: I "confirmed pre-existing" the attention-state failure via a
stash-test using the *wrong* gate invocation (both runs failed identically for the
wrong reason, masking a real S1-caused violation). Running the gate the
enforcement way (distinct channel) showed it was S1-caused — and after the fix +
correct invocation it PASSES (85 files validated). The distinct-channel doctrine
validated itself on this slice.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: charness-artifacts/retro/2026-06-20-north-star-overhaul-sweep.md
Host log probe: skipped: host-log-not-exposed: this session exposes no per-turn token/time/tool-call host log to probe, so the goal-window efficiency metrics block cannot be rendered from a provider-safe source.
Disposition review: charness-artifacts/critique/2026-06-20-north-star-overhaul-sweep-disposition-review.md

## User Verification Instructions

- **S0 (concept):** read `charness-artifacts/spec/2026-06-20-per-unit-disposition-concept.md`
  (`Status: locked`) — confirm the rung-1/rung-2 split is explicit and no
  terminal-green gate is specced (§1 invariant, F2).
- **S1 (R2 escape closed):** `python3 -m pytest tests/quality_gates/test_issue_closeout_verifier.py -q`
  — the 6 seeded tests show a silent bug carrier FAILS before `CLOSED` greens, a
  typed non-`verified` disposition PASSES (render-not-declare), and a missing
  `AI-provenance:` marker fails its check. Read `issue/references/closeout-discipline.md`
  §"Per-Issue Behavioral Verdict" — the rung-1 floor + the preserved
  render-not-declare #386 sentence.
- **S2 (R1 de-dup):** read `skills/public/achieve/scripts/goal_artifact_floor_grammar.py`
  (the one substrate) and confirm operator-queue/blocked-matrix/coordination/
  phase-routing/disposition import it; `python3 -m pytest tests/quality_gates/ -k "goal or disposition or coordination" -q`
  (380 floor tests green, incl. the 2 strict→permissive divergence tests).
- **S3 (WS-B):** read `skills/public/quality/references/unit-test-quality.md`
  (the graft, under cap, authoring-only) and the find-skills "Classify the
  capability layer honestly" named-heuristic; the deferred body redesign is in the
  retro + S3 slice log with cause.
- **Bundle:** broad pytest = 3428 passed / 0 failed (recorded in Final Verification
  + S4 slice log).

## Auto-Retro

Retro dispositions: out-of-scope: the three surfaced lessons are behavioral/process improvements captured as candidates in the wired recent-lessons selection index (`charness-artifacts/retro/2026-06-20-north-star-overhaul-sweep.md` is registered source #241 via `refresh_recent_lessons.py`; its `## Next Improvements` dash-bullets are extracted into the candidate pool — the recency/recurrence policy decides which reach the top-N display digest, so they may not appear in `recent-lessons.md` this cycle); none is a code change for THIS goal — (1) gate-failure-triage-uses-exact-enforcement-invocation and (3) bloat-diagnoses-are-hypotheses-to-verify-per-body are process lessons, and (2) the skill-body pre-cut lossless+contract-safe check belongs to the deferred body-redesign follow-on. Filing tracked GitHub issues is deferred to an operator-approved external write (see `## Operator Decision Queue`).
Structural follow-up: repo-local guard: charness-artifacts/retro/2026-06-20-north-star-overhaul-sweep.md — the transferable waste (the deferred impl/debug/quality/achieve body redesign + the pre-cut lossless+contract-safe instrument) is captured in that retro's `## Next Improvements` + `## Sibling Search` and this goal's S3 slice log for a follow-on goal; a tracked issue is deferred to operator-approved external write (Operator Decision Queue).
