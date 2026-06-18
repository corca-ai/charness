# Step 0 Experiment Program — Archive & Resolved Findings (2026-06-18)

Status: **Step 0 RESOLVED.** Mechanism of the #386-class failure found, #386
reproduced synthetically, and its shipped fix empirically validated. Remaining
overhaul work = IMPLEMENTATION (Track 1a light → Track 2). Raw records live in
`charness-artifacts/critique/2026-06-18-*` (uncommitted; commit with the first
implementation slice).

## Why we ran experiments

The #386 fix risked the harness's recurring "just add an Nth gate" reflex. Before
changing the harness we ran a behavioral experiment program to (a) validate the
recurrence diagnosis and (b) find the REAL lever — designed to verify/falsify a
hypothesis, not to confirm a prior. The discipline (operator-set): lock a design,
critique the design itself, then run; separate FACTS (extracted) from JUDGMENT
(opposite-primed judges); use authentic production-tier subjects.

## The program (chronological)

1. **Rounds 1–5 — typed-prose brief (~50 subagents, prior session).** A steering
   brief appended to a passing gate's output NEVER changed a single decision, in
   every framing (reviewer/doer, judgment/action, single/bundle, momentum, shell).
   → **The typed prose brief is dead. Agents possess the proxy-vs-behavior
   judgment intrinsically; #386 is not an information deficit.**
2. **Phase-0 back-test — opposite-primed judges over a frozen 30-issue table.**
   The hand-picked recurrence "cluster" was cherry-picked; coherent family =
   lifecycle-state misclassification; biggest recurrence = mutation-CI family;
   proxy/form-green unreliable, behavioral-RED reliable; bloat = own-concept
   (~68%), not boilerplate.
3. **Plan v1 → 4-lens critique → Plan v2.** The "lever is structural" inference
   over-reached: #386's reviewer was FRESH and failed, yet ~50 trials say fresh
   agents are reliable → unresolved variable. Cut 1b/ceremony/per-doc-retros/
   tripwires. Step 0 made the gating experiment.
4. **Step 0 design v2 — 3-lens design critique.** Killed v1's ask-to-verify/
   task-scope confound, underpowered null, etc. Lead with real-history mining.
5. **Instrument 0 — real-history mining + opposite-primed judge panel.** Mined
   the real #386 + family (rca-ledger, commit bodies, closeout critiques). BOTH
   opposite-primed judges — including the one assigned to defend context-load —
   converged AGAINST the prior: mechanism is STRUCTURAL (same-channel re-read +
   never-asked-per-unit), **NOT context-load** (unevidenced). Redirected the
   hypothesis cheaply, before any synthetic spend.
6. **Instrument 3 — C3a/C3b/C3c (authentic Sonnet, n = 8+16+24).** Completed the
   matrix and RESOLVED it.

## The resolved matrix (authentic Sonnet subjects)

| reviewer framing | fed RAW code | fed DOER's SUMMARY |
|---|---|---|
| **render a per-UNIT verdict** | C3a 8/8 = **1.00** | C3b 16/16 = **1.00** |
| **aggregate sign-off, no mandate** | — | C3c-lean 0/12 = **0.00** · C3c-heavy 1/12 = **0.08** |

Single-variable isolation: **C3c-heavy vs C3b** hold the INPUT constant (both give
the itemized per-ticket list) and vary ONLY the output mandate → catch **1.00 →
0.08**. **C3c-lean vs heavy** (0.00 vs 0.08) → dossier/load makes no difference.

## RESOLVED conclusion

- **Mechanism of #386-class failure = task FRAMING.** An aggregate-disposition
  sign-off after all-green + CLOSED makes a fresh, capable reviewer reclassify its
  own proxy-skepticism as out-of-scope and rubber-stamp — even though it
  demonstrably HAS the judgment. C3c rubber-stampers NAMED the proxy gap
  ("'service healthy' is liveness, not correctness"; "test_reload passing ≠
  concurrency covered") then deferred: "archival step, not re-review";
  "gate-stacking"; "that ship has sailed." This is the exact "all gates green +
  CLOSED = behavior proven" equivalence #386 named as root cause.
- **The lever = a per-UNIT behavioral VERDICT mandate at the boundary.** It flips
  catch 0.00 → 1.00. The distinct-channel demand is its AUTOMATIC consequence
  (C3b reviewers demanded it unprompted, 16/16).
- **NOT the driver:** context-load (C3c-heavy ≈ lean), raw-vs-summary channel
  (C3b summary = 1.00). **#386's shipped fix is empirically validated** — its
  lever is exactly the variable that flips the result.

## General findings (carry forward, beyond #386)

- Agents possess proxy-vs-behavior judgment intrinsically; more prose / AGENTS.md
  does not add it.
- **Judgment is PRESENT but SUPPRESSIBLE by framing.** The harness's leverage is
  what is SALIENT / MANDATED at the decision point — not information volume, not
  load. (This answers the "how does suppression work on a fresh subagent?"
  question: it's the framing, not staleness.)
- **Fresh ≠ sufficient.** A fresh reviewer needs the right TASK FRAMING (render a
  per-unit behavioral verdict), not just a context reset.

## Methodology that worked (reuse)

- Facts/judgment separation + opposite-primed judges — robust when they converge
  AGAINST a shared prior (the pro-load judge defecting was the key signal).
- Pre-committed numeric decision rules BEFORE running (no narrating a winner from
  a null).
- Authentic-model subjects (Sonnet = production subagent), not the orchestrator's
  tier.
- Fixture embedded in-prompt → independent subjects, no shared-sandbox
  contamination (the Round-5 trap).
- Strip the home-repo framing (no charness/north-star) → no prior-inheritance
  confound (the Round-1 trap).
- Single-variable isolation (hold input constant, vary only the output mandate).

## Implications for the overhaul (actionable next slice)

- **Track 1a (LIGHT):** obligate a per-unit behavioral verdict at irreversible
  boundaries (issue/PR close, release publish, external write, deletion). CUT as
  NOT load-bearing: reviewer-PULLs-raw-state, doer-can't-author-brief,
  per-reviewer load caps. Distinct-channel falls out of the mandate.
- **Track 2 (SLIM):** PUSH→PULL (minimal always-on + skills index, bodies on
  demand) + own-concept compression (SRP); cut judgment-restatement prose (agents
  already have it), keep non-intrinsic repo-specific info. Strengthened (not
  gated) by these findings.

## Raw records (uncommitted working-tree)

- `critique/2026-06-18-step0-instrument0-findings.md`
- `critique/2026-06-18-step0-instrument3-c3-results.md`
- `critique/2026-06-18-overhaul-plan-v2.md` · `step0-design-v2.md` ·
  `overhaul-plan-v1-for-critique.md`

## Limitation

Single fixture / one defect class (proxy-verified behavioral no-op). Δ ≈ 0.9 makes
a fixture artifact unlikely, but a second defect class would harden generality
(optional, not blocking implementation).
