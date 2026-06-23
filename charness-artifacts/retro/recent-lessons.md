# Recent Retro Lessons

## Current Focus

- Release publish triggered a configured automatic session retro for `v0.54.0`. (source: `charness-artifacts/retro/2026-06-23-v0-54-0-release-auto-retro.md`)
- Release publish triggered a configured automatic session retro for `v0.54.1`. (source: `charness-artifacts/retro/2026-06-23-v0-54-1-release-auto-retro.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-23-v0-54-2-release-auto-retro.md`; sources: 53)
- **API 529 overload thrash (S6).** Three sonnet capture attempts failed or partially failed on `529 Overloaded` (one read 6/7 refs but the closing turn errored) before switching to haiku, which captured cleanly first try. ~15 min + tokens lost retrying the same overloaded tier. (source: `charness-artifacts/retro/2026-06-22-cautilus-skill-usage-validation-harness-retro.md`)
- **Capture-design iteration (S6/S7).** The first capture prompt NAMED the concept refs, so a capable agent reached them by filename in BOTH arms (zero delta). The v2 "follow pointers only" prompt over-corrected into runaway broad exploration (16 refs, no clean result). Two wasted capture passes before settling on the honest v1 result. (source: `charness-artifacts/retro/2026-06-22-cautilus-skill-usage-validation-harness-retro.md`)
- **Lock-schema strictness misread (one debug cycle).** A quick `additionalProperties` probe reported the lock `doctor` block as permissive; it is actually `additionalProperties: False` with a required list. I designed `update_advisory` persistence assuming permissive -> doctor.py raised a jsonschema ValidationError under `--write-locks` -> CLI exit 1, caught by the CLI lifecycle tests. Root: a one-shot probe of the schema instead of reading the actual schema node / running the validator before persisting a new field into a schema-validated artifact. (source: `charness-artifacts/retro/2026-06-22-cautilus-update-advisory-retro.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-23-v0-54-2-release-auto-retro.md`; sources: 53)
- **capability:** behind-latest advisory now exists for every advisory-policy tool via the shared `attach_release_metadata` chokepoint + doctor. (applied, committed.) (source: `charness-artifacts/retro/2026-06-22-cautilus-update-advisory-retro.md`)
- **capability:** the claim-fidelity harness now exists and is reusable; the next-session work is execution-shape (gate triage so the judgment phase is reached), NOT a ref disposition redo. (source: `charness-artifacts/retro/2026-06-22-quality-claim-fidelity-retro.md`)
- **capability/workflow:** new files under a surfaces-managed dir need a `.agents/surfaces.json` entry; the gap is that pre-commit doesn't check surface coverage, only the slice closeout does — a candidate pre-commit guard. (source: `charness-artifacts/retro/2026-06-22-cautilus-skill-usage-validation-harness-retro.md`)

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
- `charness-artifacts/retro/2026-06-22-cautilus-skill-usage-validation-harness-retro.md`
- `charness-artifacts/retro/2026-06-22-cautilus-update-advisory-retro.md`
- `charness-artifacts/retro/2026-06-22-quality-claim-fidelity-retro.md`
- `charness-artifacts/retro/2026-06-23-v0-54-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-23-v0-54-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-23-v0-54-2-release-auto-retro.md`
