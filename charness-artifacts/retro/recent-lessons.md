# Recent Retro Lessons

## Current Focus

- One autonomous run executed the whole north-star overhaul goal: Track 1a (generalize the #386 per-unit behavioral-verdict framing to every irreversible boundary) + Track 2 (slim the standing prose surface). (source: `charness-artifacts/retro/2026-06-18-north-star-overhaul-retro.md`)
- Release publish triggered a configured automatic session retro for `v0.52.4`. (source: `charness-artifacts/retro/2026-06-18-v0-52-4-release-auto-retro.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-18-v0-52-5-release-auto-retro.md`; sources: 48)
- **AGENTS.md `## Skill Routing` is a GENERATED surface (S5 → reverted in S6).** The S5 collapse treated it as free prose, but `setup/scripts/render_skill_routing.py` pins the canonical compact block verbatim (`matches_compact_block`), and `charness doctor`'s `repo_onboarding` status flips `ready → required` when AGENTS.md diverges — failing `test_charness_doctor_reports_managed_surface` in the broad suite. The S5 fresh-eye reviewer AND I both missed that an AGENTS.md section can be skill-owned/generated. Reverted to the canonical block; a real collapse needs a lockstep `render_skill_routing.py` edit. **Lesson: before editing an AGENTS.md section, check whether a `setup`/`render_*` script generates or pins it.** (source: `charness-artifacts/retro/2026-06-18-north-star-overhaul-retro.md`)
- **Release cap fight (S3, ~4 wasted edit-cycles).** I tried to land the G3 per-surface-verdict framing inside the capped `release/SKILL.md` body several times before recognizing the `check-skill-core-headroom` ratchet (a ≥4-line core-headroom buffer that blocks a *regressing* change) required relocating the detail to a reference. Checking the binding constraint *first* would have routed it to `install-surface.md` immediately. (source: `charness-artifacts/retro/2026-06-18-north-star-overhaul-retro.md`)
- **Skill-prose slim broke 3 deterministic tests the per-slice gates missed (caught only at the S6 bundle-boundary broad pytest).** (a) `retro/SKILL.md` reworded a trigger sentence `check_skill_contracts.py` pins (caught at the S5 commit by `run_evals`); (b) the S3 release consolidation dropped the exact phrase "tag push alone as publish completion" that `test_release_real_host.py` pins (NOT in the `run_evals` subset, so it survived to S6); (c) the S5 `retro/SKILL.md` slim dropped "fresh-eye reader misread an invariant" that `test_retro_skill.py` pins. The fresh-eye critiques checked safeguard *content*, not the verbatim pinned-phrase tests — so the broad suite, not the reviewer or the per-slice subset, was the catch. **Lesson: the bundle-boundary broad pytest is load-bearing for skill-prose slims; the per-slice `run_evals` subset does not cover every pinned-phrase test.** (source: `charness-artifacts/retro/2026-06-18-north-star-overhaul-retro.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-18-v0-52-5-release-auto-retro.md`; sources: 48)
- **capability:** a small pre-edit affordance that, given a SKILL.md path, prints its core-headroom margin + its pinned contract snippets would collapse both traps to one read. Candidate follow-up issue (not filed this run — see Auto-Retro disposition). (source: `charness-artifacts/retro/2026-06-18-north-star-overhaul-retro.md`)
- **memory:** the staged-blob-headroom-ratchet and contract-snippet-slim traps are captured durably in this retro's Waste + Sibling Search (the canonical memory home the `recent-lessons.md` digest selects from on its next persist cycle) so the spun-out 13-body SRP sweep can pre-check them. (source: `charness-artifacts/retro/2026-06-18-north-star-overhaul-retro.md`)
- **workflow:** before editing a near-cap SKILL.md, in one shot check `check_skill_surface_preflight.py` core-headroom AND grep `check_skill_contracts.py` for that skill's pinned snippets — the two traps above are both pre-checkable. Re-stage before re-reading any staged-boundary gate. (source: `charness-artifacts/retro/2026-06-18-north-star-overhaul-retro.md`)

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
- `charness-artifacts/retro/2026-06-18-north-star-overhaul-retro.md`
- `charness-artifacts/retro/2026-06-18-v0-52-4-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-18-v0-52-5-release-auto-retro.md`
