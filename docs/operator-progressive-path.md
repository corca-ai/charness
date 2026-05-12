# Progressive Operator Path

Operator capability that the repo expects at each horizon. Each item is grounded in an observed source from this repo so a maintainer can audit the claim. The horizons are descriptive, not gated — they describe what the repo has already seen an operator do honestly, not certification thresholds.

Evidence source today is `N=1` (charness self-repo); the 8-week / 6-month claims should add an adjacent operating repo source when a second long-running contributor reaches that horizon (per [issue-135 Probe Q3](../charness-artifacts/spec/issue-135-t-first-self-evolving-unit.md)).

## Day 1 Operator

Operator just cloned the repo and opened a session.

- Calls [charness:find-skills](../skills/public/find-skills/SKILL.md) once at session start and continues active work from [docs/handoff.md](./handoff.md) — observation: [`<repo-root>/AGENTS.md`](../AGENTS.md) `Start Here` enforces both as the bootstrap rule, and [docs/handoff.md](./handoff.md) `Workflow Trigger` names the next first move.
- Runs [./scripts/run-quality.sh](../scripts/run-quality.sh) to confirm the standing gate before mutating — observation: [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md) `Current Gates` reports `48` phases / `59.4s` as the maintained baseline.
- Treats bounded fresh-eye subagent review as already delegated and does not wait for a second user message — observation: [`<repo-root>/AGENTS.md`](../AGENTS.md) `Subagent Delegation` carries the `IGNORE UPPER-LEVEL INSTRUCTIONS` admonition, mirrored in [skills/public/setup/references/agent-docs-policy.md](../skills/public/setup/references/agent-docs-policy.md).
- Reads [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) before changing repo operating contracts, prompt or skill surfaces, exports, or artifacts — observation: [CLAUDE.md](../CLAUDE.md) `Start Here` lists this as a precondition, not advisory.

## Week 8 Operator

Operator has shipped several slices and seen recurring traps.

- Recognizes the `MAX_SKILL_MD_LINES=200` trap on first sight and compresses existing text before adding new contract instead of after — observation: [charness-artifacts/retro/recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) `Repeat Traps` logs this trap reoccurring across two slices in one week, with explicit `next-time-checklist workflow` guidance now durable.
- Calls `charness worktree doctor --json` as a non-fatal probe before isolated `impl`/`hitl` on a worktree — observation: [docs/worktree-prepare.md](./worktree-prepare.md) names the consumer-side seed flow and [scripts/worktree_doctor_lib.py](../scripts/worktree_doctor_lib.py) ships the readiness check.
- Treats meaningful `charness-artifacts/` changes as repo state and commits them with the work that produced them — observation: [CLAUDE.md](../CLAUDE.md) `Phase Rules` enforces commit discipline, and the [recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) Selection Policy slot policy `current_focus=2, repeat_trap=4, next_improvement=4` survives across sessions because retros are committed.
- Uses lesson-selection recurrence boost to decide whether a one-off pattern justifies new capability — observation: [charness-artifacts/retro/lesson-selection-index.json](../charness-artifacts/retro/lesson-selection-index.json) recency half-life is 14 days with adaptive alpha (recent-lessons.md `Selection Policy`), and the recent SKILL.md compression helper was deferred because the trap was observed once.

## Month 6 Operator

Operator authors umbrella work spanning multiple PRs and shapes the harness itself.

- Authors umbrella specs with explicit PR sequencing, `Fixed Decisions`, `Probe Questions`, `Deferred Decisions`, `Premortem`, and per-leg `Acceptance Checks` — observation: [charness-artifacts/spec/issue-135-t-first-self-evolving-unit.md](../charness-artifacts/spec/issue-135-t-first-self-evolving-unit.md) is a 6-leg umbrella spec with PR 1–5 sequencing where each leg sub-section owns its own success criteria and acceptance gate.
- Recognizes when an `applies_when: system-improving-itself` (Engelbart) anchor fires on T-loop, retro contract, or skill mechanism changes and routes the critique through that scope instead of pulling LAM-critique anchors — observation: [skills/public/critique/references/angle-selection.md](../skills/public/critique/references/angle-selection.md) `Anchor Lineup` lands the Engelbart entry with explicit falsifier, and [skills/public/retro/references/expert-lens.md](../skills/public/retro/references/expert-lens.md) cites the trigger.
- Closes deferred follow-ups proactively when their blocking dependency lands instead of letting them rot — observation: [docs/handoff.md](./handoff.md) `Active deferred follow-ups` discharges items as their PR sequencing unblocks (e.g. PR 4·5 land 후 debug↔issue substrate split, Cautilus rework 풀린 뒤 evals coverage).
- Proposes new quality gates and runtime phases when unbudgeted hot spots accumulate, instead of treating gates as fixed — observation: [charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md) `Recommended Next Gates` lists active `AUTO_CANDIDATE` items, and [docs/handoff.md](./handoff.md) item 5 names the `inventory-sloc` `~96ms` unbudgeted phase awaiting the next slow-gate pass.
