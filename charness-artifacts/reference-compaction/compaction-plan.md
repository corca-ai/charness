# Reference redundancy-compaction — plan + Phase 0 result (2026-07-03)

Serves [intent.md](./intent.md): north = SMARTER agent; *능력이 같다면 적을수록 좋음.*
Operator re-opened the redundancy track (delete/compress refs the body/scaffold/
validator already covers) as a **peer of the churn sweep, not a replacement** — both
matter. This is the review+plan; **execution is deferred behind the concurrent
test-necessity audit** (some refs are validator/test-coupled).

## Two tracks (keep separate)

- **churn** (runtime waste): effectively closed — the only two churn-positive skills
  (quality, debug) are FIXED+PROVEN; spec/retro/ideation verified clean. See
  [anti-churn-patterns.md](./anti-churn-patterns.md).
- **redundancy compaction** (surface leanness): this doc. Sequenced FIRST because a
  leaner surface makes any residual churn unambiguous (no "maybe it needed the ref").

## Phase 0 — re-verify surviving delete-candidates against the LIVE tree

`census.json` is a plan-time snapshot and is **stale + ~50% unreliable on
delete-candidates** (its own history: the adversarial verifier reclassified 4 impl
"DUP" → DEPTH). Re-baselining the 26 DUP + 3 DEAD against the current tree:

- **~12 already deleted** by earlier slices (spec's 8 pure-DUP, 2 provenance DEAD,
  handoff/spec document-seams copies). Earlier disk-existence checks false-positived
  on same-named copies in other skills — **same name ≠ same ref** (`document-seams.md`,
  `runtime-contract.md` are skill-specific, all different hashes; no cheap dedup).
- **17 survivors** (16 DUP + 1 DEAD) fanned out to 17 keep-biased adversarial
  verifiers (workflow `wf_07b43c52-431`), `concept-architecture.md` left in blind as a
  calibration probe.

### Result: 0 / 17 DELETE_SAFE (calibration passed)

`concept-architecture.md` → correctly `KEEP_LOAD_BEARING` (it is ideation's sole RCF
floor; census tagged it DUP). Every survivor kept, most on **grep-confirmed unique
content** ("this string lives only in the ref"), not bias.

| ref | keep reason (one clause) |
|---|---|
| debug/debug-memory.md | **RCF floor** (sole RCF); Artifact Rule not inlined |
| debug/document-seams.md | planner emits as required read; 4th surface type + dated pattern stranded |
| create-cli/code-shape.md | "rule of three", giant-handler anti-pattern, cwd warning unique |
| create-cli/case-studies.md | named case studies (agent-browser/specdown/cautilus) absent from body |
| setup/greenfield-flow.md | **RCF floor** (greenfield.spec); 4 Minimum Questions stranded |
| retro/mode-guide.md | ⚠ **largely DUP**; only adapter default_mode tie-break rung stranded → LIFT candidate |
| ideation/concept-architecture.md | **RCF floor**; 6-step Main Loop + Document Discipline (calibration) |
| ideation/agent-human-lens.md | ~10 probing questions not inlined |
| ideation/effectuation.md | "Do Not Overclaim" guardrail unique |
| ideation/sequence-discipline.md | ordering Core Move (opposes body's "not ceremony") |
| impl/contract-consumption.md | read-first qualifier + route-back rule grep-only-here |
| hotl/proof-rules.md | **RCF floor**; Proof-levels ladder enum + per-rule guidance absent from body |
| web-fetch/runtime-contract.md | 10-step Route Ladder, Response Classes, durable field list |
| web-fetch/routing-table.md | **RCF floor** + test-asserted; domain tactics unique |
| gather-slack/runtime-contract.md | URL schema + degradation ladder; planner emits path + test asserts |
| gather-notion/runtime-contract.md | fidelity-loss enum + block conversion pipeline |
| release/install-surface.md | ⚠ **DEAD tag false**; legacy redirect (index.md + historical artifacts) — coupling-kept |

## Honest reading (do not overclaim either way)

1. **"Review before execution" was vindicated hard.** Executing census-as-written
   would have deleted RCF floors (debug-memory, concept-architecture, greenfield-flow,
   proof-rules, routing-table). The real safe deletes were already harvested; the
   census's 42.9%-redundant headline was inflated by (a) done deletes + (b) stale tags
   later calibrations flipped.
2. **"0 DELETE_SAFE" is a keep-biased LOWER bound, not "nothing to do."** This pass
   under-surfaced INLINE-lift opportunities (0 LIFT is not trustworthy). The one clear
   residual is `retro/mode-guide.md` (lift the single tie-break rung); the rest are
   1–3-token marginal. **True remaining trimmable surface ≈ nil.**
3. **The real upstream lever (north-star relevant).** Nearly every KEEP also cited:
   *"deleting breaks `claim_fidelity_lib.py:192-195` (declared refs must exist) +
   `test_claim_fidelity_specs.py`."* The claim-fidelity `declaredReferences` apparatus
   **actively resists ref deletion.** So *"fewer refs"* collides with the claim-fidelity
   test suite — exactly what the concurrent agent is auditing ("are these tests
   necessary?"). **Compaction's ceiling is set by that verdict**, which is why execution
   waits for it.

## Plan (updated by Phase 0)

- **Deletion track: CLOSED.** 0 safe; residue is load-bearing. Forcing it would delete
  DEPTH — a north-star violation. Do not.
- **Lift track: LOW priority.** ~1 real case (mode-guide). Weigh against "don't
  manufacture marginal fixes"; recommend skipping unless a lift-focused (non-keep-biased)
  pass is explicitly wanted.
- **Next real lever (higher than ref count):** after the test-necessity verdict lands,
  reassess whether the `declaredReferences`/RCF/claim-fidelity apparatus itself is
  over-heavy. If that coupling is trimmed, both deletion friction AND the apparatus's
  own overhead drop — a bigger *적을수록 좋음* win than any single ref.
