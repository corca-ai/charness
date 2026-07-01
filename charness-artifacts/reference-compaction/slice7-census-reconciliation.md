# Slice 7 census reconciliation — VERDICTS RESOLVED, execution queued

> **STATUS 2026-07-01: RECONCILED.** All 13 contested doc-open floors were
> re-examined census-first with an adversarial analyze→verify workflow (26 agents,
> one analyst + one refuter per floor). Verdicts + the capture-gated queue are in
> **`## Reconciliation RESOLVED`** at the bottom. The method-error diagnosis below
> stands as the *why*; read it first, then the resolution.

**2026-07-01, operator-surfaced.** The Slice 7 sweep decided each skill's floor
from the LIVE CAPTURE ALONE and never cross-referenced `census.json` — the audit
that had ALREADY classified all 196 references. The result: most "keep" decisions
CONTRADICT the census, and two "refuted" findings mis-framed census-INLINE
confirmations as new mysteries. The audit was done; the sweep just didn't align the
fixtures/specs to it.

## The cross-check (census bucket vs the Slice-7 decision)

| skill | Slice-7 decision | ref | census bucket | verdict |
|---|---|---|---|---|
| create-cli | MOVE (drop) | command-conventions.md | INLINE | ✅ aligned (dropped) — but tagged DEPTH, should be INLINE |
| achieve | MOVE (drop) | goal-artifact.md, lifecycle.md | INLINE | ✅ aligned (dropped) — tag should be INLINE |
| hitl | MOVE (drop) | chunk-contract.md | INLINE | ✅ aligned (dropped) — tag should be INLINE |
| handoff | del | document-seams.md | DUP | ✅ aligned (deleted) |
| handoff | keep | chunked-routing.md | DEPTH | ✅ aligned (kept) |
| critique | keep | premortem-decision.md, autonomous-trigger.md | DEPTH | ✅ aligned (kept) |
| **hotl** | **KEEP** | proof-rules.md | **DUP** | ❌ CONTRADICTS — census says redundant |
| **hotl** | **KEEP** | ledger-and-dispositions.md | **INLINE** | ❌ CONTRADICTS |
| **handoff** | **KEEP** | workflow-trigger.md, state-selection.md, spill-targets.md | **INLINE** | ❌ CONTRADICTS |
| **critique** | **KEEP** | counterweight-triage.md | **INLINE** | ❌ CONTRADICTS |
| **gather** | **refuted→#411** | source-priority.md, capability-contract.md | **INLINE** | ❌ mis-framed — INLINE, not a mystery |
| **setup** | **refuted→#413** | normalization-flow.md, agent-docs-policy.md, default-surfaces.md | **INLINE** | ❌ mis-framed — INLINE |

The 3 MOVES align with the census (drop INLINE docs). Everything I "kept" because a
capture OPENED it contradicts the census, which says those docs are INLINE/DUP.

## The method error (do NOT repeat)

I inferred "the run opened the doc → it is load-bearing → keep the doc-open floor."
That inference is invalid: **a run can open an INLINE/DUP doc redundantly.** The
census already judged the content is duplicated in SKILL.md, so the open is wasteful
whether or not a given run does it. Deciding floors from captures alone, ignoring the
existing audit, produced answers that contradict the audit.

## Correct method for the reconciliation pass

For each Slice-7 skill, per RCF ref:

1. **Read the census bucket FIRST** (`census.json` `per_skill[].references[].bucket`
   + `evidence`). The census is the audit of record.
2. **INLINE / DUP** → the compaction move applies: verify the gist is actually in
   SKILL.md (INLINE it if the census says "inline X" and it isn't yet — that is the
   compaction), then RETIRE the doc-open floor. Floor on an emitted token (if
   distinctive, create-cli pattern) or output/substance (setup/gather have no clean
   token → artifact/substance, the honest core of #411/#413). Do NOT keep a doc-open
   floor for an INLINE/DUP doc because a capture happened to open it.
3. **DEPTH** → the doc-open CAN be a floor; verify the fixture exercises the DEPTH.
4. **Census ⟷ capture DISAGREE** (census INLINE, but the capture opened it — e.g.
   hotl proof-rules.md opened for the proof-LEVEL ladder that is NOT in SKILL.md's
   `## Proof Rules` preview): the doc is MIXED (INLINE part + DEPTH part). The census
   flattened it to one bucket and may have UNDER-counted the DEPTH. DIG: split the
   compactable part (inline it) from the genuine DEPTH (keep on-demand), and set the
   floor to the DEPTH signal or the output. This reconciliation is the ACTUAL work
   the sweep skipped.

## What this means for the committed Slice-7 slices

- **MOVES (create-cli/achieve/hitl) + document-seams delete + the DEPTH keeps
  (chunked-routing/premortem-decision/autonomous-trigger): census-aligned, stand.**
  (Minor: the classTag on dropped INLINE docs should be INLINE, not DEPTH.)
- **The INLINE/DUP "keeps" (hotl both, handoff workflow-trigger/state-selection/
  spill-targets, critique counterweight-triage.md): re-examine — they likely should
  be compaction moves, not keeps.** My captures showed opens; the census says
  INLINE/DUP; reconcile per step 4 before trusting the keep.
- **gather #411 / setup #413: re-frame from "harness redesign for a refuted mystery"
  to "census says INLINE → inline the gist + retire the doc-open; floor on output
  because there is no clean single emitted token."** The artifact/substance floor is
  the right REPLACEMENT floor, but the driver is the census INLINE verdict, not a
  surprise.

Bottom line: **census bucket first, capture to verify, reconcile on disagreement** —
never decide a floor from a capture while ignoring the audit.

## Reconciliation RESOLVED (2026-07-01, adversarial analyze→verify workflow)

Method run exactly as prescribed above: for each of the 13 RCF-pinned doc-open
floors whose census bucket is INLINE/DUP, one analyst produced a census-anchored
verdict (MOVE / MIXED / KEEP) from primary sources (SKILL.md vs the ref vs the
committed capture), then an independent adversarial verifier tried to refute it.
Result: **12 MOVE, 1 MIXED, 0 genuine KEEP.** Every prior "keep because the capture
opened it" was the flagged method error. One analyst/verifier disagreement
(critique/counterweight-triage.md: analyst MIXED → verifier MOVE) resolved to MOVE.

| skill | ref | census | verdict | why (census-aligned) |
|---|---|---|---|---|
| hotl | proof-rules.md | DUP | **MOVE** | 6 rules inlined verbatim (SKILL.md 106-113); the "proof-LEVEL ladder" is only a POINTER to the shared `external-capability-proof-ladder.md` (SKILL.md line 146 lists it directly) — the open was redundant, not depth |
| hotl | ledger-and-dispositions.md | INLINE | **MIXED** | INLINE tokens (`verified_against.source_commit/.proof_artifact/.proving_surface_refs` + the Operator-Decision-Queue 5-field template) → inline; but the completion-audit **anti-proxy / P4 re-examination-failure** judgment rule (ref L96-105) is genuine on-demand DEPTH absent from SKILL.md → keeps the doc-open floor |
| handoff | workflow-trigger.md | INLINE | **MOVE** | trigger-first gist inlined (SKILL.md step 5); floor → RSF on the emitted explicit trigger |
| handoff | continuation-sequence.md | INLINE | **MOVE** | not opened by the pickup run; also the #412 planner over-requirement — INLINE gist inlined |
| handoff | state-selection.md | INLINE | **MOVE** | Compression Rule inlined (SKILL.md 54/64/111); one stranded keep-list token (task-state envelope) → inline into step 4, not a floor |
| handoff | spill-targets.md | INLINE | **MOVE** | owning-path routing gist inlined; floor → inline the routing tokens, drop the RCF pin (state-selection stays as the refresh RCF until its own move) |
| critique | counterweight-triage.md | INLINE | **MOVE** | four-bin triage DUP-inlined (SKILL.md:37); the `## Structured Findings` schema is genuinely absent BUT opt-in + validator-gated + no run opened it for the schema → census INLINE ("inline the schema/template") wins over MIXED; doc stays DECLARED for on-demand authoring, RCF floor retires; decision-scenario RCF passes only on matcher theater (see follow-up) |
| gather | source-priority.md | INLINE | **MOVE** | run opened ZERO docs (0/8) → INLINE confirmed; primary-source discipline inlined (SKILL.md steps 1-3) |
| gather | capability-contract.md | INLINE | **MOVE** | Access-Modes enum is a stranded token to inline (NOT DEPTH — corrects #411's reclassify proposal); 0/8 confirms |
| setup | greenfield-flow.md | DUP | **MOVE** | ideation+scaffold gist inlined; DUP |
| setup | agent-docs-policy.md | INLINE | **MOVE** | run opened ZERO docs (0/9) → INLINE confirmed |
| setup | default-surfaces.md | INLINE | **MOVE** | 0/9 confirmed; the "multi-surface proxy" doc-open was never forced |
| setup | normalization-flow.md | INLINE | **MOVE** | 0/9 confirmed; normalization is driven by SKILL.md + real surfaces |

### Why the classTags/RCF are NOT flipped in the specs this session

`claim_fidelity_lib.py` enforces that **a ref in `requiredCommandFragments` must not
be classTag DUP/INLINE** (a re-read floor must be load-bearing/DEPTH) AND that
RCF-or-RSF must stay non-empty. So flipping a live floor's tag to INLINE/DUP is
**coupled to removing it from RCF**, which needs a proven replacement floor — and
that proof is **capture-gated** (see queue). Flipping the tag while the ref stays
in RCF would break the validator; dropping the RCF with no proven replacement fails
closed. Therefore this session corrects the **record only** (spec `_comment` notes
+ this doc + issue reframes); the classTag/RCF flips ride with the capture-gated MOVE.

### Capture-gated queue (execute in an ask-before-run Cautilus session)

Systemic finding: **none of these skills has a substance judge**
(`outcome-assertions.json` absent for all), and the Slice-7 capture bundles retain
**no `stream.jsonl`**, so no MOVE can be closed by a spec-only edit or an offline
re-grade — each needs a fresh authorized capture. Two replacement-floor shapes:

- **Script/SKILL-driven skills that open ZERO docs (gather ×2, setup ×4):** the
  honest replacement is an **artifact/substance judge** (`outcome-assertions.json`),
  not an RSF token — exactly the redesign already scoped in **#411 (gather)** and
  **#413 (setup)**. The census INLINE verdict is the *driver*; the 0-coverage
  capture merely confirms it (re-framed below — not a "surprise refutation").
- **Doc-opening skills (hotl/proof-rules, handoff ×4, critique):** the replacement
  is an emitted-token **RSF** proven by a fresh capture, but with **no substance
  judge an RSF is a FORM floor that can over-relax** (a run could echo the token
  from always-loaded core without doing the work). So each MOVE also wants the
  four-bin/schema/routing gist inlined into SKILL.md first, and — for critique —
  respects the **194/200-line SKILL.md ceiling**. Re-pin to a stronger phrase or
  add a judge if a later capture shows a hollow pass; never soften.

**hotl/ledger-and-dispositions.md (MIXED)** is the one partial no-capture step: the
INLINE-token lift (dotted `verified_against.*` + ODQ template) into SKILL.md is a
plain edit (prompt-affecting → still wants a confirming capture), and the anti-proxy
DEPTH keeps its doc-open floor as-is (already capture-proven load-bearing).

### Two follow-ups (the "then" items)

- **#412 (handoff planner):** reconciliation sharpens it — `continuation-sequence.md`
  is INLINE (gist inlined) AND the pickup run correctly skips it, so the fix is both
  the planner making it conditional AND retiring the pickup doc-open floor to RSF.
- **Matcher honesty nuance:** `build-skill-execution-observation.mjs` `collectCommandLog`
  (line 129) pushes every string in each tool-use *input* — including a spawned
  subagent's **prompt** — into the command log the RCF matcher substring-searches. So
  naming a ref filename in an Agent-tool prompt satisfies a doc-open floor with **no
  genuine Read** (critique's decision scenario is a live example: coverage 1/12,
  counterweight-triage.md "engaged" via a name-mention). Recorded as its own issue;
  fixing it changes matcher semantics + needs a re-grade, so it is filed, not rushed.
