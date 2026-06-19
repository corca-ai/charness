# Recent Retro Lessons

## Current Focus

- Implemented item-5 slice-2 (the boy-scout duplicate ratchet's teeth): pure policy lib + git seams, the adapter-driven gate CLI, a validated `dup_ratchet` adapter block, the green-seeded gate baseline + charness rollout (D6), run-quality + broad pre-push wiring, the reference, and SC1–SC6 tests. (source: `charness-artifacts/retro/2026-06-19-item5-slice2-dup-ratchet.md`)
- One autonomous run executed the whole north-star overhaul goal: Track 1a (generalize the #386 per-unit behavioral-verdict framing to every irreversible boundary) + Track 2 (slim the standing prose surface). (source: `charness-artifacts/retro/2026-06-18-north-star-overhaul-retro.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-18-v0-52-5-release-auto-retro.md`; sources: 48)
- **Re-seeded the gate baseline 3×** (mid-implementation, after the module extraction, after the critique fixes). The baseline is a content-hash (`family_id`) snapshot of the scanned `.py` tree, so every code edit shifts it and invalidates a prematurely-seeded baseline. Each re-seed cost a scan + a re-verify. Root cause: seeding a content-hash baseline before code was frozen. (source: `charness-artifacts/retro/2026-06-19-item5-slice2-dup-ratchet.md`)
- **Two length-cap collisions discovered at the gate, not before the edit:** `quality_policy_defaults.py` was already at its cap (adding the validator pushed 490 > 480), and `quality/SKILL.md` was pinned at exactly 200 lines (adding a required reference entry pushed it to 201). Both forced rework (extract a module; trade a redundant convenience line) that a pre-write headroom check would have surfaced up front. (source: `charness-artifacts/retro/2026-06-19-item5-slice2-dup-ratchet.md`)
- **AGENTS.md `## Skill Routing` is a GENERATED surface (S5 → reverted in S6).** The S5 collapse treated it as free prose, but `setup/scripts/render_skill_routing.py` pins the canonical compact block verbatim (`matches_compact_block`), and `charness doctor`'s `repo_onboarding` status flips `ready → required` when AGENTS.md diverges — failing `test_charness_doctor_reports_managed_surface` in the broad suite. The S5 fresh-eye reviewer AND I both missed that an AGENTS.md section can be skill-owned/generated. Reverted to the canonical block; a real collapse needs a lockstep `render_skill_routing.py` edit. **Lesson: before editing an AGENTS.md section, check whether a `setup`/`render_*` script generates or pins it.** (source: `charness-artifacts/retro/2026-06-18-north-star-overhaul-retro.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-18-v0-52-5-release-auto-retro.md`; sources: 48)
- for content-hash-keyed baselines (this gate; also `nose-baseline.json` / `doc-nose-baseline.json`), seed/re-seed as the LAST pre-commit step once code is frozen. The dup-ratchet adoption doc now orders scope-then-seed; the "seed last" timing is the transferable half. (source: `charness-artifacts/retro/2026-06-19-item5-slice2-dup-ratchet.md`)
- run `check_python_lengths --repo-root . --headroom <file>` before adding code to a near-cap module, rather than learning the cap at the gate. (source: `charness-artifacts/retro/2026-06-19-item5-slice2-dup-ratchet.md`)
- this artifact + the recent-lessons digest carry the "seed content-hash baselines after freeze" + "check length headroom before editing near-cap files" lessons. (source: `charness-artifacts/retro/2026-06-19-item5-slice2-dup-ratchet.md`)

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
- `charness-artifacts/retro/2026-06-19-item5-slice2-dup-ratchet.md`
