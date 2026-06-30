# Reference Compaction — Keystone Policy + Slice Plan (2026-07-01)

Operator-approved; execution deferred to the next session, slice by slice.
Full per-ref classification + evidence: `census.json`. Full per-skill execution
contracts + adversarial risk verdicts: `plan.json` (`per_skill_plans`, `execution`).

## Origin

Census of all 24 skills / 196 references (judge panel + adversarial verify of every
delete-candidate): **DEPTH 109 (56%) · INLINE 58 (30%) · DUP 26 (13%) · DEAD 3**.
The earlier manual "impl 5/8 DUP" read was over-aggressive — the adversarial verifier
reclassified 4 of those to DEPTH (they carry conditional load-bearing judgment, not pure
redundancy). The real lever is **INLINE** (stranded emittable tokens), NOT deletion.

## Keystone (diagnosis CORRECTED by the plan)

`coverage` NEVER gates a run: `build-skill-execution-observation.mjs:666` —
`outcome = findings.length>0 ? 'failed':'passed'`, and `findings` come ONLY from
`requiredCommandFragments` (RCF) + `requiredSummaryFragments` (RSF). Coverage is advisory
by construction. The real re-read **teeth** is RCF pinned to a doc *filename*
(impl `RCF=['verification-ladder.md']`), which the command-log matcher satisfies only when
the doc is literally opened — forcing a wasteful re-read of intent the run already has.
Fix THAT; the "headroom vs coverage" contradiction dissolves.

Three coordinated moves:

- **A — token home:** SKILL.md gets a headroom-exempt H2 `## Closeout Vocabulary` holding
  only **emittable-verbatim** tokens (a validator substring-matches it, OR a closeout line
  is malformed without the literal string). `create-skill` rule amended: only prose / why /
  examples exile to `references/`; **never** literal tokens a closeout must emit.
- **B — headroom:** add `'Closeout Vocabulary'` to `PRESSURE_EXEMPT_H2_SECTIONS`
  (`check_skill_surface_preflight.py:30`) so the block is invisible to the core-nonempty
  density gate (like `Load-Bearing Anchors`/`References`). `MAX_SKILL_MD_LINES=200` STILL
  counts real bytes (file-size guard). Anti-abuse: the vocab block must be token-shaped
  (≤~12 lines, label+one-clause, no multi-sentence prose).
- **C — floor:** drop the ref *filename* from RCF and assert the emitted **token** via RSF
  (the actual claim, not the open-the-doc proxy); relax `claim_fidelity_lib` guard from
  "RCF non-empty" to "RCF-or-RSF non-empty"; add advisory per-ref `classTag` DUP/INLINE/
  DEPTH; compute the reported coverage denominator over DEPTH refs (+ `coverage.declaredAll`
  backward-compat). **KEEP** the judge `honest-categorized-closeout` for substance — the
  deterministic token floor (form) + judge (substance) split is the mature issue-closeout
  pattern and covers the hollow-RSF risk below.

## Slices (DAG order; ~70–95 files total; each its own commit; mutate→sync→verify→critique)

1. **KEYSTONE MECHANISM** (no per-skill content): the gate exemption, the RCF-or-RSF guard,
   the `classTag` infra (`claim_fidelity_lib` + `build-observation.mjs` + both tests), and
   the `create-skill` token-home rule. MUST be first — empty-RCF fails closed and `classTag`
   has zero consumers until this lands.
2. **DEAD deletes:** web-fetch/gather-slack/gather-notion provenance+lineage memos
   (rm file + drop SKILL.md `## References` bullet together + mirror + find-skills inventory).
3. **spec 8 pure-DUP deletes** (RCF untouched; re-baseline spec coverage 16→8).
4. **advisory `classTag` only** (retro/achieve/create-skill/find-skills/announcement/
   narrative/debug) — cosmetic, no token movement.
5. **★ PROVING: impl** — `## Closeout Vocabulary` lift (Lint-Gate enum + 5 completion-report
   categories from verification-ladder.md, which becomes a pointer-to-core) + RCF→RSF.
   Validator-enforced, HIGHEST single risk (200-line knife-edge ~199; needs Slice 1's guard).
   **Needs a FRESH ask-before-run cautilus capture** to pick the honest RSF token (don't assume).
6. **spec acceptance-checks enum lift** (no RCF rewrite → no capture; lower risk).
7. **DEFERRED SWEEP — file ONE tracking issue:** per-skill RCF→RSF for critique/hitl/gather/
   hotl/handoff/setup/create-cli/achieve. Each needs a fresh ask-before-run capture.

## Self-flagged risks (from the plan — read before executing)

- **200-line TOTAL ceiling knife-edge:** impl ~190+9≈199, zero margin → may force an honest
  prose trim of true redundancy elsewhere in impl core (correct signal, not a workaround).
- **empty-RCF fails closed:** any RCF drop before Slice 1's RCF-or-RSF guard lands is rejected.
- **hollow RSF token:** a run could emit the RSF token from always-loaded core without doing
  the categorization work → mitigated by KEEPING the judge `honest-categorized-closeout`.
- **plan_input `validator_enforced` was WRONG** for critique/hitl/find-skills/debug — their
  artifact/routing validators DO substring-match enums in reference files; treat as
  validator-enforced in slices 4/7 (the plan's risk stage already corrected this).

## Full-circle

Slices 5/7 RSF tokens re-baseline from fresh **live captures** — possible now BECAUSE #409
(the capture→grade harness) was fixed this session. This work also implements the
operator-flagged "impl closeout-vocabulary fork" as **Option A (internalize)** and fixes the
floor measurement for the whole correctness sweep.
