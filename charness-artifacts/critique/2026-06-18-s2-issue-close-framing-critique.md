# S2 — Fresh-Eye Critique: issue/PR-close per-unit behavioral-verdict framing

Status: **PASS (no blockers, no folds).** Bound by slice S2 of
`charness-artifacts/goals/2026-06-18-north-star-overhaul.md`. Date: 2026-06-18.

Reviewer provenance: one bounded fresh-eye subagent (read-only, shared parent
worktree; prior versions via `git show HEAD:<path>`, no index/worktree mutation),
per the CLAUDE.md subagent-delegation contract and
`skills/shared/references/fresh-eye-subagent-review.md`.

## Slice review packet (provided to the reviewer)

- **Intent:** generalize the #386 per-unit behavioral-verdict framing
  (`achieve/references/lifecycle.md` Rung-2 seed) to the GitHub issue/PR-close
  boundary *outside* the achieve seed — the standalone `issue resolve` close path
  (direct-to-default commit and PR-merge carriers; gaps G1+G2 from the S1 audit).
- **Changed surfaces:**
  - `skills/public/issue/references/closeout-discipline.md` — new section
    "## Per-Issue Behavioral Verdict At Close (the irreversible-boundary
    mandate)" (the full mandate home).
  - `skills/public/issue/SKILL.md` — guardrail rewritten in place
    (`carrier_verified` / `CLOSED` now "necessary-not-sufficient"); no net lines
    added (held at 199/200 cap).
  - `skills/public/issue/references/resolve-flow.md` — one salient pointer
    sentence at the close step.
  - `plugins/charness/skills/issue/...` — generated mirror (synced, byte-matches
    sources).
  - `docs/public-skill-dogfood.json` — scenario-review freeze record for `issue`.
- **Expected invariants:** framing only; no new gate/script/verdict token (P5);
  distinct channel + distinct observer (P4); same-proxy re-read forbidden; both
  carriers covered; `question`/`decision-needed` carve-out.
- **Non-claims:** not behaviorally re-run (validated by reasoning against
  north-star P4/P5 + the Step-0 per-unit-verdict finding + this critique).
- **Out of scope:** release publish (G3), release-linked close (G4), deletions
  (G5) — those are S3.

## The mandatory per-boundary check (B2 blocker from the plan critique)

> Does the sharpened prose **DECLARE a completion condition** (BLOCKER —
> "all units confirmed = close" re-creates the exact #386 terminal-green) or only
> **MANDATE the per-unit question** (PASS)?

**Verdict per surface: MANDATES (pass), all three.** The dispositive evidence the
reviewer cited:

- closeout-discipline.md explicitly *forbids* the relapse in prose: "a per-issue
  **question to render, never a completion condition to declare** … the
  obligation is to render the verdict-or-disposition per issue, not to gate the
  close on an aggregate 'all confirmed'." The **verdict-OR-disposition** shape is
  the tell — a non-verified disposition is a legitimate non-blocking outcome, so
  "all confirmed" is never the close trigger.
- SKILL.md guardrail demands the verdict be *rendered* ("a per-issue behavioral
  verdict … is required"), not "close when the verdict is positive".
- resolve-flow.md gates the *report* ("required before reporting the issue
  resolved"), not the close mechanism.

## Reviewer verdict (verbatim summary)

**Overall: PASS.** Per-question:

- **Q1 declares-vs-mandates — PASS.** All three surfaces mandate the per-unit
  question; none re-creates the terminal-green equivalence.
- **Q2 smuggled gate / new token — PASS.** No new deterministic surface;
  `verify-closeout` stays a *state* check and is explicitly named as the
  same-proxy re-read to avoid.
- **Q3 safeguard preserved — PASS (strengthened).** The `carrier_verified`-is-
  not-closeout prohibition is retained verbatim and *extended* to reject a bare
  `CLOSED`. No stale duplicate guardrail survived. carrier_verified is made *less*
  acceptable, not more.
- **Q4 distinct channel + observer (P4) — PASS.** Concrete distinct channels
  named (behavior test / provider roundtrip / fetch-readback / artifact); the
  fresh-eye resolution critique named as the distinct observer; same-proxy
  re-read forbidden; P4 citation faithful to `design-north-star.md` L42–48.
- **Q5 scope / coherence — PASS.** Both carriers (direct-commit + PR
  merge-to-shared-history) covered; `question`/`decision-needed` carve-out
  coherent with the existing skip-the-critique rule; no internal contradiction;
  HOTL ledger reference resolves.

Counterweight (over-worries raised and discharged by the reviewer): "before
reporting … is also required" gates the *report* not the *close* (close still via
auto-close keywords + unchanged state check); "necessary-not-sufficient" does not
weaken `status: verified` (state requirement unchanged); no stale duplicate
guardrail.

## Disposition

PASS with no folds. S2's in-place pattern is validated: the per-unit behavioral
verdict framing generalizes cleanly to the issue/PR-close boundary as prose at
the decision point, with no gate, token, or lost safeguard. The validated pattern
carries to S3 (release publish G3, release-linked close G4, deletions G5).
