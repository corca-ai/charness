# Recent Retro Lessons

## Current Focus

- This retro reviews `charness-artifacts/goals/2026-06-28-issue-405-405-add-verification-channel-fitness-guard-propagation-acros.md`: the achieve goal that resolved GitHub issue #405 by adding two named bullets (`verification-channel fitness`, `guard-propagation across seams`) to the `quality` Behavior lens and a `## Distinct Named Lenses` delegation note to the shared `fresh-eye-subagent-review.md`, plus the regenerated `plugins/` mirror. (source: `charness-artifacts/retro/2026-06-28-issue-405-405-quality-lens-guard-propagation-retro.md`)
- Release publish triggered a configured automatic session retro for `v0.56.6`. (source: `charness-artifacts/retro/2026-06-27-v0-56-6-release-auto-retro.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-27-v0-56-9-release-auto-retro.md`; sources: 66)
- The Before-phase consequential-discussion floor fired five triggers when only two (issue-close, proof-non-claim) were genuine; the other three matched my own prose that *describes* those categories as not-applicable. Resolving it cost one extra edit cycle (the floor is presence-only and cannot read negation — an accepted simplicity tradeoff, not a defect). (source: `charness-artifacts/retro/2026-06-28-issue-405-405-quality-lens-guard-propagation-retro.md`)
- The first `Discuss before activation:` summary was placed after `## Slice Log` and worded `none — …`, both of which the parser rejects (summary must precede `## Slice Log` and begin `resolved/confirmed/approved`). The `--pursue-ready` reason named the gap precisely, so it self-corrected in one cycle, but a Before-phase describe-first preflight (the After-phase has one) would have surfaced the shape up front. (source: `charness-artifacts/retro/2026-06-28-issue-405-405-quality-lens-guard-propagation-retro.md`)
- The active worktree also contains unrelated v0.56.7 release WIP. Keeping that boundary explicit was necessary, but it means broad lock-style closeout cannot honestly be claimed for this goal without mixing unrelated release state. (source: `charness-artifacts/retro/2026-06-27-capability-first-skill-redesign-retro.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-27-v0-56-9-release-auto-retro.md`; sources: 66)
- A Before-phase describe-first preflight (sibling to `describe_goal_closeout_shape.py`) could surface the `Discuss before activation:` placement/wording shape before `--pursue-ready` rejects it. Disposition: out-of-scope: a Before-phase preflight is a separate achieve-tooling change larger than this docs goal; `--pursue-ready` already names the exact gap, so the friction is one self-correcting cycle, not a recurrence warranting a new tool here. (source: `charness-artifacts/retro/2026-06-28-issue-405-405-quality-lens-guard-propagation-retro.md`)
- The two new Behavior-lens entries and the delegation note are portable skill doctrine, inherited by every charness-consuming repo through the public `quality` skill and shared reference. Disposition: applied: the doctrine landed in `skills/public/quality/references/quality-lenses.md` and `skills/shared/references/fresh-eye-subagent-review.md` (mirrored to `plugins/`), so adopting repos inherit it, not just charness. (source: `charness-artifacts/retro/2026-06-28-issue-405-405-quality-lens-guard-propagation-retro.md`)
- After writing a quality current-pointer artifact, immediately run `validate_quality_artifact.py`, `validate_inventory_consumption.py`, `check_spec_evidence_durability.py`, and `validate_current_pointer_freshness.py` before starting locked closeout. (source: `charness-artifacts/retro/2026-06-27-sustained-quality-speed-token-release-round-4-goal-retro.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-03-v0-17-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-04-v0-18-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-04-v0-19-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-20-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-21-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-22-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-23-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-06-v0-24-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-06-v0-24-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-06-v0-25-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-07-v0-27-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-28-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-29-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-30-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-30-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-31-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-32-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-32-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-33-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-34-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-35-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-36-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-37-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-38-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-39-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-40-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-11-v0-41-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-12-v0-41-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-12-v0-42-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-12-v0-43-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-12-v0-44-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-13-v0-44-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-13-v0-45-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-13-v0-46-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-14-v0-47-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-14-v0-48-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-14-v0-49-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-14-v0-50-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-15-v0-50-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-16-v0-50-2-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-16-v0-51-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-16-v0-51-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-16-v0-52-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-17-v0-52-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-17-v0-52-2-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-17-v0-52-3-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-18-v0-52-4-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-18-v0-52-5-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-19-v0-52-6-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-20-v0-53-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-23-v0-54-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-23-v0-54-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-23-v0-54-2-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-25-v0-55-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-25-v0-55-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-25-v0-55-2-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-25-v0-56-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-26-v0-56-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-26-v0-56-2-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-26-v0-56-3-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-26-v0-56-4-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-26-v0-56-5-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-27-capability-first-skill-redesign-retro.md`
- `charness-artifacts/retro/2026-06-27-sustained-quality-speed-token-release-round-4-goal-retro.md`
- `charness-artifacts/retro/2026-06-27-v0-56-6-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-27-v0-56-7-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-27-v0-56-8-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-27-v0-56-9-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-28-issue-405-405-quality-lens-guard-propagation-retro.md`
