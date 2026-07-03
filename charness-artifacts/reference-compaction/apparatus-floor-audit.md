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

### Corrected status of all 9 (each token needs a non-triviality capture, not just emission)

| skill / floor | proposed token | verdict now |
|---|---|---|
| gather ×3 (capability-contract, source-priority, browser-mediated) | Access Mode:/Source: | **REFUTED — trivially green; needs `outcome-assertions` redesign or skip** |
| setup greenfield-flow | `Repo mode: GREENFIELD` | unverified — sibling `normalization` used `Repo mode:`; check triviality |
| setup agent-docs-policy | `AGENTS scaffolded` | unverified — can a hollow run emit it? |
| release version-policy | `Bump: <part> — because <effect>` | unverified — rationale more substantive; capture |
| debug debug-memory | `Related Prior Incidents` (cite incident or explicit none) | unverified — capture for non-triviality |
| handoff workflow-trigger | `## Workflow Trigger` section | unverified — section header may be trivial |
| ideation concept-architecture | `Candidate Direction`/`Recommended Current Decision` | unverified — output-shape label may be trivial |

## Honest plan (corrected — the capture-gate killed the naive fix before it shipped)

- The mechanical "RCF→RSF literal-token swap" is the **WRONG default** — it risks
  trivially-green floors (gather proves it). **Do NOT batch-edit specs.**
- The honest fix for deliverable-claim floors is a **substance instrument**
  (`outcome-assertions.json`: artifact-existence + judge), a per-skill REDESIGN — bigger
  than a sweep, and an operator decision (the gather finding already said so).
- Cheap next step PER floor: one capture that tests token NON-TRIVIALITY (a hollow run
  must FAIL it) before any edit. Several will likely fail like gather → route to the
  substance-judge redesign instead of a token.
- **The 28 KEEP stay untouched.** The audit's real value stands: it located the 9
  mis-checks AND — via this reconciliation — killed a naive token-swap fix before it
  shipped a hollow floor. Correct scope of the *smarter+leaner* win is a per-skill
  substance-instrument redesign, not a mechanical sweep.
