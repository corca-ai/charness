# Recent Retro Lessons

## Current Focus

- Achieve goal `charness-artifacts/goals/2026-06-14-367-quality-ci-recoverability-and-timing-ingest.md`, resolving GitHub issue #367 end-to-end (operator chose push + close + release). (source: `charness-artifacts/retro/2026-06-14-367-quality-ci-recoverability-and-timing-ingest.md`)
- Closeout retro for goal `charness-artifacts/goals/2026-06-14-workflow-host-state-hardening-bundle.md`: three non-blocking workflow/host-state guards landed and released as 0.48.0 — S1 agent-browser orphan scoping (bug-class #365), S2 #363 close-keyword-leakage advisory, S3 #364 decaying-habit advisory — each reusing an existing surface (no new blocking floor, per Floor-Addition Restraint), through push + release. (source: `charness-artifacts/retro/2026-06-14-workflow-host-state-hardening-bundle.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-14-v0-50-0-release-auto-retro.md`; sources: 38)
- `advisory-only` attention-state undeclared → blocked the slice-2 commit; fixed by declaring it. One round. (source: `charness-artifacts/retro/2026-06-14-367-quality-ci-recoverability-and-timing-ingest.md`)
- **First no-drift tests blocked by `check-boundary-bypass-ratchet`.** I wrote the gate cross-checks as `subprocess.run(["python3", "scripts/check_doc_links.py", ...])`; the ratchet flagged them as in-process-convertible candidates. Converted to in-process `main()` calls. The gate caught it; one round. (source: `charness-artifacts/retro/2026-06-14-general-doc-authoring-preflight.md`)
- **First S1 commit blocked by `staged-plugin-mirror-drift`.** I committed before running `sync_root_plugin_manifests.py`; `scripts/*.py` is part of the plugin install surface, so the new script needed mirroring into `plugins/charness/scripts/`. One blocked commit → sync → re-commit. The gate caught it; cost was one round, no escaped drift. (source: `charness-artifacts/retro/2026-06-14-general-doc-authoring-preflight.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-14-v0-50-0-release-auto-retro.md`; sources: 38)
- a pre-push/pre-commit advisory that flags a close keyword (`closes/fixes/resolves #N`) in a commit whose changed paths are not a plausible fix for #N (e.g. an artifact-only goal-shaping commit) — surfaced as a non-blocking advisory, per Floor-Addition Restraint. Filed as https://github.com/corca-ai/charness/issues/363 (one recorded instance; advisory before any blocking floor). (source: `charness-artifacts/retro/2026-06-14-general-doc-authoring-preflight.md`)
- **memory/capability:** a short "adding an advisory inventory/surface" checklist (the 3 registries + the SKILL.md ≤200 budget) in the quality references, so the next author front-loads the registrations. → file as issue (same structural cluster as the first; keep one tracked thread). (source: `charness-artifacts/retro/2026-06-14-367-quality-ci-recoverability-and-timing-ingest.md`)
- **memory — repo-root `scripts/*.py` mirror into `plugins/charness/scripts/`**, not just skill surfaces; sync before the commit gate, not after a rejection. (The staged-mirror-drift gate already enforces this deterministically; the lesson is to sync proactively.) (source: `charness-artifacts/retro/2026-06-14-achieve-efficiency-internal-followups.md`)

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
- `charness-artifacts/retro/2026-06-14-367-quality-ci-recoverability-and-timing-ingest.md`
- `charness-artifacts/retro/2026-06-14-achieve-efficiency-internal-followups.md`
- `charness-artifacts/retro/2026-06-14-general-doc-authoring-preflight.md`
- `charness-artifacts/retro/2026-06-14-v0-47-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-14-v0-48-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-14-v0-49-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-14-v0-50-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-14-workflow-host-state-hardening-bundle.md`
