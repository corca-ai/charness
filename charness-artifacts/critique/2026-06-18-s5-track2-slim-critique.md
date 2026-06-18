# S5 — Fresh-Eye Critique: Track 2 slim (AGENTS.md PUSH→PULL + retro SRP)

Status: **PASS (no blockers, no folds).** Bound by slice S5 of
`charness-artifacts/goals/2026-06-18-north-star-overhaul.md`. Date: 2026-06-18.

Reviewer provenance: one bounded fresh-eye subagent (read-only, shared parent
worktree; prior versions via `git show HEAD:<path>`, no index/worktree mutation).

## Slice review packet

- **Intent:** shrink the standing prose surface via concept-separation (P2), not
  line-shaving; success metric = learnability, not line count. Two changes:
  - **A — AGENTS.md PUSH→PULL** (the always-on host surface; CLAUDE.md symlinks
    to it; highest blast radius). 70 → 58 lines: the Cautilus bullet compressed
    to a 1-line pointer (detail already in + tooling-enforced by
    `quality/references/cautilus-on-demand.md`); the `## Skill Routing` section
    collapsed (it duplicated Start Here's find-skills/gather/quality routing).
  - **B — retro own-concept SRP-split.** retro SKILL.md core 160 → 144: the
    `## Auto-Retro Trigger` and `## Expert Counterfactual Rule` body sections
    compressed to their load-bearing rule + repo-specific command, delegating the
    taxonomy/examples to the pre-existing references `trigger-and-persistence.md`
    and `expert-lens.md`.
- **The boundary the reviewer guards:** "was any safeguard lost or made unread?"
  (goal Boundaries — AGENTS.md is its own critique boundary).

## Reviewer verdict (summary) — PASS

- **QA1 AGENTS.md Cautilus — PASS, nothing unread.** The 1-line pointer keeps the
  safeguard core (consult the planner; refuse `next_action:none` /
  `must_ask_before_running` without a failing-log; use `run_cautilus_eval.py`,
  never bare `cautilus evaluate`). The dropped detail — supported-surfaces
  enumeration, provenance, and the **disabled-surfaces list** (claim discovery /
  optimize / review-learning / `evaluate live` / Agent orchestration) — is all
  present in `cautilus-on-demand.md`, which pre-existed and is **unchanged by S5**
  (genuine pull, not freshly-created absorption).
- **QA2 Skill Routing collapse — PASS, only duplication removed.** Every removed
  line maps to retained always-on content: find-skills bootstrap (Start Here L8),
  the capability-noun recommendation pattern (retained verbatim in the collapsed
  section), gather routing (L10), quality/HITL-ordering (L15, verbatim). The
  **safeguard sections are untouched** — Subagent Delegation and Phase Rules show
  zero diff lines; the CLAUDE.md→AGENTS.md symlink is intact.
- **QB1 retro SRP — PASS, nothing lost.** The repo-specific `check_auto_trigger.py`
  command + `auto_session_trigger_surfaces`/`path_globs` and the mandate "every
  retro includes ≥1 counterfactual lens" + the `Persisted` rule are retained in
  the compressed body; the trigger taxonomy/examples and expert-lens patterns are
  confirmed present in the (unchanged, pre-existing) references.
- **QB2 concept-separation vs line-shaving — PASS.** Both references pre-existed
  and already owned the concept (already in retro's References list), so detail
  was relocated, not pushed into newly-created overflow. P2-compliant.

Over-worry dismissed: the compressed Cautilus pointer no longer spells the
disabled-surfaces list inline, but the actionable trip-wires are all retained
always-on and the governance list is one reference hop away.

## Post-S5 correction (S6 broad proof)

The reviewer's QA2 PASS on the **Skill-Routing collapse** was **superseded** at
the S6 bundle-boundary broad pytest: `AGENTS.md`'s `## Skill Routing` is a
**setup-generated surface** pinned verbatim by
`setup/scripts/render_skill_routing.py` (`matches_compact_block`). The collapse
flipped `charness doctor`'s `repo_onboarding` status `ready → required`, failing
`test_charness_doctor_reports_managed_surface`. Both the reviewer and the doer
missed that an AGENTS.md section can be skill-owned/generated (the review checked
duplication + safeguards, not generated-surface ownership). **Corrected in S6:**
the canonical Skill-Routing block was restored verbatim; a genuine collapse would
need a lockstep `render_skill_routing.py` change (deferred to the spun-out
Track-2 work). The **Cautilus PUSH→PULL (Change A) stands unaffected** — it
targets a non-generated Start-Here bullet and its safeguard core remains
always-on. The measurable standing-surface shrink is therefore carried by the
retro SRP-split (B) plus the Cautilus always-on text reduction.

## Disposition

PASS on Change A (Cautilus) + Change B (retro SRP); Change A-routing
(Skill-Routing collapse) reverted in S6 as a generated-surface contract
violation. Track 2's standing-surface shrink is demonstrated: the
always-on AGENTS.md is measurably smaller (70 → 58) with no safeguard lost or made
unread, and the retro body was pulled off the cap (160 → 144) by genuine
concept-separation to references that already owned the concepts. The
remaining-13-capped-body SRP sweep is recommended to spin out (S4 sizing).
