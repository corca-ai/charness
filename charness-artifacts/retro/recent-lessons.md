# Recent Retro Lessons

## Current Focus

- Implemented item-5 slice-2 (the boy-scout duplicate ratchet's teeth): pure policy lib + git seams, the adapter-driven gate CLI, a validated `dup_ratchet` adapter block, the green-seeded gate baseline + charness rollout (D6), run-quality + broad pre-push wiring, the reference, and SC1–SC6 tests. (source: `charness-artifacts/retro/2026-06-19-item5-slice2-dup-ratchet.md`)
- Migrated the code-clone path from the removed `nose scan` to `nose query` (commit `15d5df4f`), re-baselined, verified (run-quality 77/0, 104 focused tests, 2-reviewer fresh-eye critique), committed. (source: `charness-artifacts/retro/2026-06-19-nose-migration-and-self-diagnosis-miss.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-19-v0-52-6-release-auto-retro.md`; sources: 49)
- **Inverted the trust hierarchy.** The canonical gate (`run-quality`) had already *skipped* this check non-blocking (stale fingerprint → `--require-fresh-coverage` skip). I then ran a non-canonical bare `--reuse-coverage` (which trusts any coverage file regardless of freshness/format) and treated *its* block as more authoritative than the canonical gate's pass. A forced, off-contract probe should not outrank the standing gate. (source: `charness-artifacts/retro/2026-06-19-nose-migration-and-self-diagnosis-miss.md`)
- **Mirror sync missed a late edit.** The ownership-overlap docstring fix landed after my last `sync_root_plugin_manifests.py`, leaving the plugin mirror stale — a real BLOCKER. The fresh-eye critique caught it (working as designed), but a sync immediately before the critique/commit would have pre-empted it. (source: `charness-artifacts/retro/2026-06-19-nose-migration-and-self-diagnosis-miss.md`)
- **Re-introduced a known footgun by dropping a special-case in a rewrite.** The old `build_command` dropped `--top` on `--write-baseline` so a baseline records EVERY family; my `query` rewrite used the display `--top`, truncating the advisory baseline to 53 instead of 487. Caught at re-seed verification, not at edit time. (source: `charness-artifacts/retro/2026-06-19-nose-migration-and-self-diagnosis-miss.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-19-v0-52-6-release-auto-retro.md`; sources: 49)
- **capability:** `check_changed_line_mutation_coverage --reuse-coverage` should reject a coverage JSON that contains none of the changed files' repo-relative paths (wrong-format/stale) — degrade to "no usable coverage → skip" rather than scoring every changed file 0% and blocking. This removes the entire false-block class. (follow-up; destination: charness gate hardening.) (source: `charness-artifacts/retro/2026-06-19-nose-migration-and-self-diagnosis-miss.md`)
- **follow-up (genuine, separate from this migration):** `check_dup_ratchet.py` has 0% *attributed* coverage because slice-2 tests it via subprocess (the #393 class). Add an in-process coverage test before pushing the unpushed stack. (source: `charness-artifacts/retro/2026-06-19-nose-migration-and-self-diagnosis-miss.md`)
- for content-hash-keyed baselines (this gate; also `nose-baseline.json` / `doc-nose-baseline.json`), seed/re-seed as the LAST pre-commit step once code is frozen. The dup-ratchet adoption doc now orders scope-then-seed; the "seed last" timing is the transferable half. (source: `charness-artifacts/retro/2026-06-19-item5-slice2-dup-ratchet.md`)

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
- `charness-artifacts/retro/2026-06-19-item5-slice2-dup-ratchet.md`
- `charness-artifacts/retro/2026-06-19-nose-migration-and-self-diagnosis-miss.md`
- `charness-artifacts/retro/2026-06-19-v0-52-6-release-auto-retro.md`
