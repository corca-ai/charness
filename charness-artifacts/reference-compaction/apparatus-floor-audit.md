# Claim-fidelity apparatus — RCF doc-open floor audit (cold/neutral, 2026-07-03)

Serves [intent.md](./intent.md): north = SMARTER agent; test = "그게 정말 최선인가?"
Follows the redundancy [compaction-plan.md](./compaction-plan.md): ref-deletion came
back 0/17, so the lever question moved UPSTREAM to the claim-fidelity apparatus itself
(the machinery that verifies "does a run route to / use its refs as claimed": 22-skill
specs + `claim_fidelity_lib.py` + the 941L observation harness + tests). This audits
its "teeth."

## Phase 1 — teeth inventory (deterministic, no judgment)

40 RCF floor-entries across 27 spec files; **ALL 40 are filename-forces-doc-open**
("the run must OPEN this file"), **0 token-RCF**. Only **6 RSF** (emitted-substance)
floors total. `impl`/`achieve`/`hitl` are already RSF-only (`RCF=[]`) — the proven
migrated shape (impl was keystone move C's proving ground). *Raw fact, not a verdict:
"all doc-open" ≠ "all ritual" — that needs per-floor judgment (Phase 2).*

## Phase 2 — cold per-floor audit (37 distinct floors)

Method: 17 neutral per-skill evaluators, **no preferred answer** (KEEP/MIGRATE/DROP all
on the table) → any MIGRATE/DROP verdict re-challenged by an **independent adversarial
defender** arguing the floor is genuinely load-bearing; a successful defense flips it back
to KEEP. The burden-of-proof was deliberately put on the demote direction (the one this
investigation was inclined toward). **The guard fired: 6 initial demotions flipped back.**

| verdict | count | share |
|---|---|---|
| **KEEP_DOCOPEN** (genuine floor; doc-open honest) | **28** | 76% |
| **MIGRATE_TO_RSF** (check mis-shaped: verify emitted substance, not file-open) | **9** | 24% |
| DROP (pure ritual, nothing to check) | 0 | — |
| UNSURE | 0 | — |

**Correction of an earlier over-reach:** Phase 1's leap — "100% doc-open ⇒ the apparatus
IS the churn disease" — was WRONG. Cold: **76% of floors are well-shaped**; **0 are pure
ritual.** The real defect is a bounded **24% mis-CHECK**, not bloat. The apparatus is
mostly earning its place.

**Pattern (why the split is trustworthy):** MIGRATE = *deliverable-claim* skills — the
produced artifact carries the claim (gather fidelity, setup surfaces/mode, release bump,
debug prior-incidents, ideation candidate direction, handoff trigger); a run can open the
how-to doc and still emit a hollow artifact, or emit a faithful one without opening it, so
the emitted token is the truer check. KEEP = *consult-judgment* skills — unique judgment
consulted at the point of need (spec/critique/create-*/quality/retro/issue), with no
emitted token that faithfully proxies "did you apply this thinking." Independently
corroborated by the specs' own `_comment`s (gather `capability-contract` already tagged
MOVE; setup `normalization` already migrated to a `Repo mode:` token).

**Composes with Phase 0 (not a contradiction):** `debug-memory` / `concept-architecture`
are load-bearing CONTENT (Phase 0 → keep the ref) AND mis-CHECKED (Phase 2 → migrate
RCF→RSF). Keep the ref; change how the claim is verified.

## The 9 mis-checked floors — and why the FIX is NOT a mechanical token swap

Phase 2 says these 9 verify "opened the doc" when the claim is about the emitted
deliverable. That **direction is sound.** But prior capture evidence forces a sharp
correction on the **prescription**: the audit agents proposed literal RSF tokens (mostly
Output-Shape field labels), and a real capture proves those tokens can be
**trivially-green traps.**

### Reconciliation with prior capture (gather slice7, 2026-07-01) — CRITICAL

A representative gather run scored `outcome=FAILED, coverage 0/8` against the current
spec — a textbook-faithful gather that opened ZERO docs (both RCF floors refuted). So
the mis-check is real. BUT the same finding already **rejected the naive fix**:
`Access Mode: public` is emitted by ANY public fetch (appears incidentally 3×), so
`requiredSummaryFragments=[Access Mode:]` would be **trivially green = softening the
matcher** (forbidden). gather's honest floor is a durable-artifact-existence check + a
substance judge (`outcome-assertions.json`) — a floor REDESIGN, "needs an operator
decision," skip the mechanical sweep. **My audit's gather tokens walked straight into
that trap.** The audit tested "is the content load-bearing" but NOT "is the proposed
token NON-TRIVIAL" (would a hollow run FAIL to emit it) — a real gap.

### Sort result — adversarial non-triviality test of the 6 non-gather tokens (0 survived)

Each token was attacked: could a HOLLOW template-only run emit it? **0 of 6 survived as
clean migrations.** Combined with gather's 3 (empirically refuted), **all 9 fail the
mechanical token fix:**

| floor | sort verdict | honest fix |
|---|---|---|
| gather ×3 (capability/source/browser) | REFUTED (live capture) | substance judge (`outcome-assertions.json`) or skip |
| setup greenfield-flow | TRIVIAL — `Repo mode: GREENFIELD` is prompt-dictated + mandated closeout label | greenfield-scenario substance judge |
| setup agent-docs-policy | TRIVIAL — `AGENTS scaffolded` is a mandated per-surface label a boilerplate dump also emits | artifact-substance judge |
| debug debug-memory | TRIVIAL — the `none related` escape-hatch is a free default | **KEEP doc-open** + NEW substance assertion for memory-consumption |
| handoff workflow-trigger | TRIVIAL — mandated Output-Shape section; captured closeouts show 0 occurrences | substance judge naming a concrete installed workflow |
| ideation concept-architecture | TRIVIAL — `Recommended Current Decision` is a mandated Output-Shape label | substance judge on the sharpened direction |
| release version-policy | **KEEP_DOCOPEN** — token trivial AND doc-open is planner-forced/honest | none — Phase 2's MIGRATE was wrong; keep the floor |

## Final conclusion (correcting several of my own earlier claims)

1. **The mechanical RCF→RSF token sweep is DEAD for deliverable-claim skills.** A
   `requiredSummaryFragment` is emitted by the TEMPLATE, and hollow runs follow the
   template too — so a summary token cannot verify output QUALITY/fidelity; only a judge
   reading the produced artifact can. (impl's `ran-pass` worked because it is a binary
   FACT, not a quality claim.) **0/9 clean migrations.**
2. **The apparatus is even more well-shaped than the audit's 76%:** release + debug keep
   their doc-open (Phase 2's MIGRATE was too aggressive). The genuinely mis-shaped set is
   ≈6 floors (gather×3, setup×2, handoff, ideation), and each needs a per-skill
   **substance-judge redesign** (`outcome-assertions.json`) — MORE apparatus, a deliberate
   design investment, NOT a lean quick win.
3. **These floors are a MEASUREMENT-VALIDITY issue, not a runtime tax — this disconfirms
   my own hypothesis.** Captures show faithful runs IGNORE the doc-open floors (gather
   0/8), so they are NOT forcing runtime ritual/churn; they only produce latent
   false-FAILED *capture* verdicts. Fixing them serves honest measurement, NOT a smarter
   LIVE agent.

## What this means for the north star

Against "smarter + efficient + intelligent LIVE skills," the apparatus floor-fix is a
measurement-honesty investment that **does not touch the runtime agent** — worthwhile but
NOT the smarter-agent lever, and not lean. Recommend: record it (optionally file a
substance-judge-redesign follow-up as a deliberate future slice), and put energy on levers
that DO touch the live agent — the churn sweep and the intent's held-open systemic
context-tax question. The apparatus-first detour earned its cost by **disconfirming that
the apparatus is a runtime drain** and by catching three over-eager fixes (Phase-1
over-reach, the naive token swap, the runtime-churn hypothesis) before any shipped.
