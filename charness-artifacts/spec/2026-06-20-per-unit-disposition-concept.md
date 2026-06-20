# Concept Spec — The Per-Unit-Disposition Abstraction + Phase-3 Instrument Set

Status: **locked** (S0 gating artifact — fresh-eye critique PASS-WITH-CONDITIONS
folded 2026-06-20; implementation may proceed)
Created: 2026-06-20
Goal: `charness-artifacts/goals/2026-06-20-north-star-overhaul-sweep.md`
Provenance: surface maps from three read-only Explore passes + direct reads of
`issue_verify_closeout.py`, `issue/references/closeout-discipline.md`,
`goal_artifact_operator_queue.py`, `goal_artifact_markdown.py`,
`goal_artifact_disposition_grammar.py`. Doctrine: `docs/design-north-star.md`
(P1–P5). Diagnosis: `charness-artifacts/audit/2026-06-20-north-star-phase0-diagnosis-backtest.md`.
Instruments: `charness-artifacts/audit/2026-06-20-reference-absorption-overhaul-inputs.md`.

This spec is concept-first. It fixes the shared abstraction and the instrument
definitions; per-slice implementation detail (exact diffs, test bodies) is the
job of S1/S2/S3 and is left as named probes here, not pre-written.

---

## 1. The one concept (the abstraction wearing N masks)

A **per-unit disposition** is the record a lifecycle transition leaves for each
unit it touches, structured as two rungs:

- **Rung-1 — presence/form floor (deterministic, P5-legitimate).** A gate that
  *forces a question* by refusing a transition whose record is **silent or
  malformed** on the per-unit obligation. It checks that the record *contains*
  the required shape (a disposition line, a verdict line, a bound path, an
  opt-out with a reason) — **never** whether the content is honest. It may force
  the question; it may not declare completion. There is no terminal green.

- **Rung-2 — distinct-channel observer (human-audited, P4).** A fresh-eye
  observer that judges the *honesty* of each unit's disposition by consulting an
  evidence channel **distinct from** the proxy the transition rode in on (a
  `CLOSED` state, a deterministic gate's green, a readback). Re-reading the same
  proxy is not confirmation. The observer renders a per-unit verdict a human
  audits; its sign-off (not the gate's green) is the stop condition.

The cluster — operator-queue (#381), blocked-matrix (#385), coordination-cues,
the achieve disposition rungs, issue closeout, the #386 disposition-review — is
**this one shape instantiated N times**. Today the rung-1 grammar is cloned per
mask, and the rung-2 observer is wired on the achieve-bundle path but **absent in
code on the standalone issue/PR-close path**. The overhaul collapses the rung-1
clones to one substrate (R1/S2) and wires the missing rung-2 (R2/S1).

### The invariant that makes it non-terminal (binding, never relaxed)

> A rung-1 floor that **greens on self-classification** re-grants the exact
> terminal trust the cluster abused. Rung-1 refuses *silence/malformation* and
> nothing more; *honesty* is always rung-2's job. "All units present ⇒ done" is
> the #386 anti-pattern and is forbidden — the obligation is to render the
> verdict-or-disposition per unit, never to gate the transition on an aggregate
> "all confirmed."

This is why the success metric is **a closed escape + a clearer concept**, never
"fewer lines / fewer gates" (a north-star failure signature).

---

## 2. WS-A / R2 (Slice S1) — wire the missing rung-2 onto issue/PR close

### The open escape (verified in code)

- `skills/public/issue/scripts/issue_verify_closeout.py:262-263` computes
  `status = "verified"` purely from `CLOSED` state + ledger form + close-keyword
  + source-preservation + resolution-critique presence. **No per-issue
  behavioral verdict from a distinct channel is required; no AI-provenance is
  checked.** `CLOSED` is the terminal-green proxy — exactly the #359/#363/#386
  failure shape at an irreversible boundary (issue/PR close).
- `skills/public/issue/scripts/issue_close.py` `close_with_comment()` posts the
  carrier comment **verbatim with no AI-provenance marker**, so the distinct
  observer P4 needs cannot tell an agent authored it.
- The doctrine *already exists in prose*: `issue/references/closeout-discipline.md:106-138`
  ("Per-Issue Behavioral Verdict At Close") + `issue/SKILL.md:148-149` name the
  mandate. **It is unwired** — risk-constraint (6): "actually wired, not
  assumed-present."

### The central tension (S0 critique must adjudicate this)

`closeout-discipline.md:136-138` *deliberately* says **"No new gate, script, or
verdict token is added"** — because the only two options it imagined were
(a) judgment-only prose, or (b) a terminal-green gate that declares "all
confirmed ⇒ done" (which re-creates the equivalence it exists to remove).

The shared concept introduces a **third option** that dissolves the dichotomy:
a rung-1 **block-the-silent** presence floor (force the question) + a rung-2
observer (judge honesty). This is the same architecture the achieve path already
ships (rung-1b binds `Disposition review: <path>`; rung-2 is the fresh-eye
reviewer). It does **not** declare completion: `status: verified` stays
necessary-but-not-sufficient; rung-1 only refuses a closeout that is *silent* on
per-issue behavior.

**Because this reverses a deliberate prior line, S1 revises `closeout-discipline.md:136-138`
and that edit is a governing-surface change requiring a bounded fresh-eye
critique. The S0 critique is asked to confirm the third-option reading is sound
and not a disguised terminal-green gate.** (See `## Open Tensions For Critique`.)

### The wire (what S1 lands)

1. **Rung-1 presence floor on the issue path.** Extend the verify/draft path so a
   `bug`/`feature`/`deferred-work` carrier (the classes with behavior to confirm)
   must *contain*, per closed issue, either a behavioral-verdict line naming a
   distinct channel **or** a typed non-`verified` disposition (HOTL status, or
   `local-only-by-contract`). Presence/form only — it does **not** parse whether
   the channel is genuinely distinct. `question`/`decision-needed` are exempt
   (nothing to confirm), matching the existing classification split. A silent
   carrier fails *before* the `CLOSED`-state green can stand alone.
2. **AI-provenance marker.** `close_with_comment()` (and any agent-posted
   issue/comment body) carries an AI-provenance marker so the distinct observer
   can see it was agent-authored. Presence/form (rung-1 grammar).
3. **Rung-2 binding.** The fresh-eye resolution critique (already the natural
   distinct observer, `closeout-discipline.md:128`) is where the per-issue
   honesty verdict is rendered/audited; S1 makes the rung-1 floor *demand the
   line exists* so the rung-2 observer has something to audit. No aggregate
   "all-confirmed" completion token is created.
4. **Doctrine sync.** Rewrite `closeout-discipline.md:136-138` to describe the
   rung-1/rung-2 split, replacing **only** the now-stale "No new gate, script, or
   verdict token is added" clause (which predates the rung-1/rung-2 split and only
   imagined judgment-only vs terminal-green). **The actual #386 decision —
   "a per-issue question to render, never a completion condition to declare," with
   no aggregate "all-confirmed" gate (`:132-136`) — survives verbatim-in-spirit**
   (S0 critique blocker 4); the new rung-1 floor refuses silence, it does not gate
   the close on aggregate confirmation. Align `issue/SKILL.md:148-149`.

### Proof (S1 acceptance, local-only by goal contract)

- Seeded-instance: a closed-issue carrier that is **silent** on the behavioral
  verdict must FAIL the new rung-1 floor (the replacement catches the seeded
  failure *before* `CLOSED` greens); a carrier that names a distinct channel or a
  typed non-`verified` disposition PASSES rung-1. A carrier without the
  provenance marker fails the provenance presence check.
- New locked tests under `tests/quality_gates/` for the rung-1 presence floor +
  provenance marker; the existing issue-closeout tests stay green.
- No live GitHub close/comment unless operator-approved + phase-scoped
  (Operator Decision Queue).

---

## 3. WS-A / R1 (Slice S2) — collapse the cloned rung-1 grammar to one substrate

### Duplication map (verified)

`mask_fences` is **already** a single shared source (`goal_artifact_markdown.py`,
7 importers) — the **extraction model** to replicate, not a clone to fix.

The genuine clones, all under `skills/public/achieve/scripts/`:

| Primitive | Clones (**5**, count corrected by S0 critique) | Form | De-dup verdict |
| --- | --- | --- | --- |
| `parse_created_date` | operator_queue:37-44, blocked_matrix:62-69, coordination:97-109, disposition_grammar:69-81, **phase_routing:~72 (Agent-2 map missed this)** | divergent: **strict** `^Created:\s*…$` (operator_queue, blocked_matrix) vs **permissive** `^[\s>*-]*Created\s*:\s*…\b` + IGNORECASE (coordination, disposition_grammar, phase_routing) | unify to the permissive parser **as a tested, deliberate behavior change** — see boundary note below (NOT a no-op extraction) |
| `is_floor_in_scope(created, rule_date)` (`created is None or created >= rule_date`) | operator_queue:47-49, blocked_matrix:72-80, coordination:112-126, disposition_grammar:84-91, disposition.py:158 & 207 | identical logic | **unify** (preserves grandfather + fail-closed) |
| placeholder markers (`TODO`/`TBD`/`<…>`/`FIXME` ⇒ blank) | disposition_grammar:58-61, section_placeholders:26-39, closeout_evidence | overlapping markers, context-specific use | **unify the marker set**; keep per-floor use-site |
| `_section_body` | operator_queue:52-63 (H2-list), blocked_matrix:83-96 (H2-list), coordination:90-94 (level-aware, wraps `_section_span`:69-87), disposition_grammar:94-113 (level-aware) | 2 H2-list + 2 level-aware variants — **diverge on any goal with `###` subsections inside the scoped section** | **unify to the level-aware variant ONLY with a per-consumer DIVERGENCE-EXPOSING seeded proof** (a goal carrying `###` subsections); else keep separate |
| opt-out matcher | operator_queue:29 (min 20, `none —`), coordination:40 (min 30, `n/a —`), disposition_grammar:44-47 (min 30, Auto-Retro-scoped `Retro dispositions: none —`) | divergent (length, prefix, scope) | **provide a parametric matcher** (prefix, min-len, scope-section); do NOT collapse to one hardcoded form |

**Created-date unification is a behavior change, not a no-op (S0 critique blocker 1).**
"Most-permissive = fail-closed" was imprecise: the fail-closed property
(`None ⇒ in-scope`) is preserved by the `applies`/`is_floor_in_scope` wrapper
regardless of parser. But swapping operator_queue/blocked_matrix from the strict
to the permissive parser **relaxes** those two floors — a `> Created:` /
`- Created:` / lowercase `created:` line that the strict parser ignored (so the
floor fired) now parses, grandfathering more pre-rule goals (the floor fires
*less*). Defensible (fewer false refusals), but it is a deliberate change at
floors guarding goal-state transitions. The 9 currently-locked tests only
exercise plain `Created: YYYY-MM-DD` lines, where strict and permissive are
byte-identical — so "all 9 locked tests pass" greens **without proving behavior
was preserved** (the form-passed-not-content-correct trap). S2 must add a new
locked test per swapped consumer pinning behavior on a prefixed/blockquoted/
lowercase `Created:` line.

### Substrate boundary (what to unify vs keep separate)

- **Unify into one substrate** (placement probe: a new
  `skills/public/achieve/scripts/goal_artifact_floor_grammar.py` beside
  `goal_artifact_markdown.py`, or extend the markdown module): `parse_created_date`,
  `is_floor_in_scope`, the placeholder-marker set, and a **parametric** opt-out
  matcher. operator-queue / blocked-matrix / coordination / disposition become
  thin configs over these primitives.
- **Keep separate** (false-unification risk): the 5 distinct `RULE_DATE`
  constants, each floor's narrow trigger predicate, the floor verdict/orchestration
  functions, `coordination`'s first-satisfying-wins, and the `_section_body`
  level-aware vs H2-list divergence unless a per-consumer seeded proof shows the
  level-aware variant is behavior-identical for that consumer.

### Locked floor tests (must stay green after extraction)

`tests/quality_gates/`: `test_goal_artifact_operator_queue.py`,
`test_goal_artifact_blocked_matrix.py`, `test_goal_coordination_floors.py`,
`test_goal_disposition_gate.py`, `test_disposition_form_floor.py`,
`test_goal_early_close_report.py`, `test_goal_artifact_lib.py`,
`test_goal_artifact_timebox.py`, `test_goal_artifact_closeout_delegation.py`.

---

## 4. The six binding risk-constraints (mapped to code anchors)

From the cluster-survey (`wf_f03ba5fe-62d`); each is a hard constraint on S1/S2.

1. **Transition direction + no-runnable-contradiction.** Preserve
   `goal_artifact_blocked_matrix.py:155-186` (`flip_refusal`: already-`blocked`
   bypass + runnable-lane detection) so #385's wrong-**block** mirror-image is
   not inverted. The floor guards **both** wrong-completion and wrong-block.
2. **Narrow per-unit triggers.** Preserve each floor's narrow predicate
   (`coordination_floors.py:129-165` gather/release/issue triggers are
   non-overlapping by design); a unioned enumerator must not false-fire.
3. **Per-concept RULE_DATE grandfather + fail-closed.** There are **≥7** distinct
   concept-keyed RULE_DATE constants (S0 critique count, verified):
   operator_queue 6-17, blocked_matrix 6-18, coordination 5-31, issue-closeout 6-2,
   phase_routing 6-4, recurrence_lineage 6-8, disposition 5-30, plus
   `DISPOSITION_FORM_RULE_DATE` and `STRUCTURAL_FOLLOWUP_RULE_DATE` in
   `goal_artifact_disposition*.py`. Keep **all** of them separate; `is_floor_in_scope`
   keeps `created is None ⇒ in-scope` (a goal cannot dodge by corrupting `Created:`).
   The extraction must cover every floor sharing the clone (including phase_routing,
   which the initial surface map omitted) or it is a partial de-dup claiming
   completeness.
4. **Rung-1 stays presence/form.** No rung-1→rung-2 collapse anywhere; rung-1 is
   structure/existence only (`disposition_grammar.py` probes are emptiness, never
   substance).
5. **Carry every anti-bypass guard.** Fence-masking
   (`goal_artifact_markdown.py:5-22`, fail-open on unbalanced fence),
   Auto-Retro-scoped opt-out (`disposition_grammar.py:144-159`),
   first-satisfying-wins (`coordination_floors.py:180-199`), placeholder-as-blank
   (`disposition_grammar.py:116-128`).
6. **Issue-path rung-2 actually wired** (R2/S1 above), not assumed-present.

---

## 5. WS-B (Slice S3) — Phase-3 instrument set + per-body redesign

### The instrument set (locked definitions)

1. **No-op deletion test** (P2). Model-relative, sentence-by-sentence: does this
   line change behaviour vs a capable agent's default? If not, delete the whole
   sentence (do not reword). Settle by running the skill, not debating.
2. **Three length-causes** (P2). Diagnose before cure: **sediment** (prune),
   **duplication** (single source of truth via cite), **sprawl** (disclose-split
   to a reference). Applies to references too (operator framing: guard reference
   sprawl/sediment, not disclosure itself).
3. **Leading Word Rule** (P3). One repeated pretrained token (tracer-bullet,
   tight, red) over a restated phrase or a do-not list; person-name is one
   species. Primary P3 compression + do-not-list reducer.
4. **Body altitude** (P2). 200 is a ceiling, not a target; 195–200 is a bloat
   signal to audit. Ask "smallest body that equips the judge."
5. **Named heuristic over enumerated do-nots** (P3). Collapse 3+ negative bullets
   that restate one principle into one named heuristic; success = negative-
   directive count falling.
6. **Load-bearing-anchor split** (P2). An anchor needing commas for >3 nouns is a
   catalog → one-sentence move in body + roster in a reference.
7. **Show one instance** (P3). Spend reclaimed budget on one sharp worked example
   over another guardrail.

### Per-body redesign hypotheses (RE-MEASURE in S3 — not locked here)

Surface-map measurements diverged from the prior audit on floor share; S3
re-measures each body before cutting. Hypotheses to confirm/correct:

- **debug** — DUPLICATION (bootstrap/floor restatement) → floor-extract de-dup to
  one-line cites. (Both audits agree.)
- **quality** — SPRAWL: the Load-Bearing Anchors section fuses routing with a
  10+-script comma-list → load-bearing-anchor split (roster → reference). (The
  flagship bloat case.)
- **impl** — prior audit said ~32% floor (floor-extract); fresh map said ~19%
  (concept-dense). **S3 re-measures and lets the diagnosis pick the cure**;
  do not pre-commit to floor-extract.
- **find-skills** — concept-separate (decision-frame-vs-discovery split) vs
  sediment-collapse — **S3 diagnoses by the three length-causes.**
- **achieve** — TIGHT (~183L, headroom); apply named-heuristic collapse to its
  14 negative bullets, no forced cut.

Each redesign: per-body cause-diagnosis (three length-causes) → no-op test →
Leading-Word/named-heuristic collapse → negative-directive count drop → fresh-eye.

### Unit-test-quality graft (S3, under cap, P3 worked-examples)

New `skills/public/quality/references/unit-test-quality.md`, routed **from** the
Behavior lens in `quality/quality-lenses.md` (the lens that already cites
`testability-and-selection.md`), sitting **below** `testability-and-selection.md`
(whose lines 121-170 own the test-DSL **review** lens and are *stronger* there —
keep convergent/SKIP). Graft only the six better-UT patterns as principle + one
worked example each: (1) determinism harness; (2) properties/invariants in the
test; (3) observable-contract + one-reason-to-fail; (4) real-collaborators-by-
default for in-process code; (5) map-behavior + edge-case menu; (6) fixture/DSL
**authoring** principles (plain-literals-first; valid/minimal/visible defaults;
avoid cause/effect-hiding fluent chains; small named helpers). **Boundary:** graft
the DSL *authoring* principles only — the DSL *review* lens stays in
`testability-and-selection.md`; charness ships no stack-specific DSL impl.
Guard reference sprawl: apply the no-op test + three-length-causes to this
reference too and watch reference count/size.

---

## 6. Fixed Decisions (locked at S0)

- F1. The shared abstraction is **two rungs**: rung-1 presence/form (deterministic,
  forces the question, no terminal green) + rung-2 distinct-channel observer
  (human-audited honesty). This is the single concept all masks instantiate.
- F2. **No terminal-green gate is added** anywhere; the §1 invariant is binding.
- F3. R2 sequence **first** (open escape), R1 **second** (de-dup the substrate R2
  reuses), WS-B third. Migration discipline: name failure-mode → land replacement
  → seeded-instance proof → only then delete old surface + rollback ref.
- F4. R1 unifies `parse_created_date` (5 clones incl. phase_routing; the
  strict→permissive swap is a **tested deliberate behavior change**, not a no-op),
  `is_floor_in_scope`, placeholder-markers, and a **parametric** opt-out matcher;
  keeps the ≥7 RULE_DATEs, triggers, verdict fns, first-satisfying-wins, and the
  `_section_body` divergence separate (unify the latter only on a
  divergence-exposing per-consumer seeded proof). "9 locked tests pass" is **not**
  sufficient S2 proof — each behavior-changing swap adds a divergence-input test.
- F5. The six risk-constraints (§4) are binding on S1/S2.
- F6. WS-B grafts `unit-test-quality.md` (six patterns, authoring-only, below
  `testability-and-selection.md`, from the Behavior lens).
- F7. Success = closed escape (R2) + clearer concept / genuine de-dup (R1 + WS-B);
  **never** line/gate count.

## 7. Probes (decided during impl, not pre-wired here)

- P-a. Substrate file placement (new `goal_artifact_floor_grammar.py` vs extend
  `goal_artifact_markdown.py`) — decide in S2 by import-graph minimality.
- P-b. Exact rung-1 issue-floor surface (new subcommand vs additive check inside
  `verify_closeout`/`validate-closeout-draft`) — decide in S1 by the
  additive-before-the-ledger-checks pattern already used for the critique header.
- P-c. AI-provenance marker exact token/wording — decide in S1 (must exceed a
  trivial-bypass length, mirror existing marker discipline).
- P-d. Per-body WS-B cures — decided in S3 by fresh measurement (§5).
- P-e. Whether `_section_body` level-aware unification is safe per consumer —
  decided in S2 by a **divergence-exposing** seeded proof: the seed must be a
  goal artifact carrying `###` subsections inside the scoped section (the input
  where H2-list and level-aware variants differ). A flat-section seed proves
  nothing; absent such proof, the consumer keeps its own `_section_body`
  (S0 critique blocker 3).

## 8. Success Criteria (testable)

- S0: this spec exists, the rung-1/rung-2 split is explicit, no terminal-green
  gate is specced, and a bounded fresh-eye critique returns PASS folded here.
- S1: on a *seeded* closed issue, a carrier silent on the behavioral verdict
  FAILS the rung-1 floor before `CLOSED` greens; a carrier with a distinct-channel
  verdict or typed non-`verified` disposition PASSES; provenance-marker absence
  fails its presence check; existing issue-closeout tests stay green.
- S2: the rung-1 grammar lives in one substrate; operator-queue/blocked-matrix/
  coordination are thin configs; all 9 locked floor tests pass **AND** each
  behavior-changing swap (created-date strict→permissive; any `_section_body`
  unification) is pinned by a NEW divergence-input test proving behavior was
  preserved or the relaxation is deliberate; net script lines fall *without*
  losing a guard (each §4 constraint still has a live test). "9 locked tests
  green" alone is rejected as S2 proof (it greens on unchanged inputs).
- S3: named bodies de-pinned by the *right* cure (re-measured), negative-directive
  counts fall, no-op test applied, `unit-test-quality.md` lands under cap from the
  Behavior lens; concept clarity rises (not just line count).
- Bundle: gate suite green; honest non-claims; live-proof levels named.

## 9. Rejected Alternatives

- **Bulk gate deletion / "fewer gates" as the metric** — north-star failure
  signature; rejected (Non-Goals).
- **An 8th terminal-green gate that greens on self-classification** — the #386
  anti-pattern; rejected (F2, §1 invariant).
- **Keep R2 judgment-only (the current `closeout-discipline.md:136-138` line)** —
  rejected: the back-test shows judgment-only with no rung-1 floor lets a *silent*
  carrier ride `CLOSED` to "done" (the open escape). The rung-1 block-the-silent
  floor forces the question without declaring completion.
- **Naively union the opt-out matchers / `_section_body` variants** — rejected:
  divergent length/prefix/scope and level-awareness carry real anti-bypass intent
  (risk-constraints 2/5); parametric-or-separate instead.
- **Full 21-body rewrite this goal** — out of scope (named first candidates only).

## 10. S0 Critique — Folded (PASS-WITH-CONDITIONS, 2026-06-20)

A bounded fresh-eye reviewer (a distinct agent context) verified the spec's
load-bearing claims against the **actual code** (a distinct evidence channel, per
the #386 lesson — not a re-read of this artifact). Verdict:
**PASS-WITH-CONDITIONS**. The locked architecture (rung-1/rung-2, R2-first,
no-terminal-green) was not challenged; four conditions tightened the S2
*measurement* so the de-dup cannot silently change behavior. All four are folded
above. Tension adjudications:

- **T1 (load-bearing) — rung-1 block-the-silent ≠ terminal-green: CONFIRMED
  distinct.** The achieve path already ships this shape in code
  (`describe_goal_closeout_shape.py:163-166` labels the `Disposition review:` line
  "rung 1b" — binds presence; the fresh-eye reviewer is rung-2 and signs honesty).
  The issue floor refuses *silence only*; `status: verified` stays
  necessary-not-sufficient. Matches P5 ("force a question, not declare
  completion"). The #386 trap is avoided **iff** the floor is never wired to gate
  on aggregate "all confirmed" — which F2/§1 forbid and S1 acceptance tests.
- **T2 — `closeout-discipline.md` rewrite is a doctrine-sync, not a regression**,
  needing no operator sign-off beyond the already-mandated per-edit critique —
  **on condition** the "render-not-declare / no aggregate all-confirmed" sentence
  survives (folded into §2.4 step 4 + blocker 4).
- **T3 — defer impl's cure to S3 re-measurement: CORRECT** (locking floor-extract
  on a contested ~32%/~19% diagnosis would be the line-count failure signature).
- **T4 — per-consumer seeded proof INSUFFICIENT as first written** (the real
  blocker): a flat-section seed exposes nothing, and the created-date swap is a
  behavior change the 9 locked tests do not pin. Folded into blockers 1+3.

### Conditions folded (the four blockers)

1. **Created-date unification is a tested deliberate behavior change**, not a
   no-op; the strict→permissive swap relaxes operator_queue/blocked_matrix; each
   swapped consumer gets a new divergence-input locked test (§3 boundary note,
   F4, S2 criterion).
2. **Counts corrected:** ≥7 RULE_DATE constants (incl. phase_routing 6-4,
   recurrence_lineage 6-8, disposition_form, structural_followup); 5
   `parse_created_date` clones (incl. phase_routing) — §3 table, §4 constraint 3,
   F4. Verified directly: `grep` over `skills/public/achieve/scripts/*.py`.
3. **`_section_body` seeded proof must be divergence-exposing** (`###`-subsection
   artifact) — P-e, §3 table.
4. **`closeout-discipline.md` rewrite preserves the render-not-declare sentence**
   — §2.4 step 4.

### Over-worries dismissed by the counterweight pass

The rung-1 floor re-creating terminal-green (T1, dismissed — architecture proven
non-terminal in code); the doctrine rewrite needing fresh operator sign-off
(dismissed — pre-authorized via per-edit critique); a negative-bullet count
nuance and a minor line-cite typo (non-load-bearing); `unit-test-quality.md`
overlapping `testability-and-selection.md` (dismissed — authoring-vs-review
boundary verified sound).

**Gate result: S0 spec LOCKED. Implementation (S1) may proceed.**
