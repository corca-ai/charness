# Recent Retro Lessons

## Current Focus

- Activated the shaped achieve goal `2026-06-07-330-metavalidator-gate-hardening` and ran it end to end: built the #330 meta-validator (enumerate inference-layer surfaces; assert the 4-field `interpretation` declaration + paired consumer-must-answer line; fail closed on any unregistered declaration), bundled the #331-deferred surface-idiom lint, wired both as standing + slice-closeout gates, and staged `Closes #330`. (source: `charness-artifacts/retro/2026-06-07-issue-330-metavalidator-gate-hardening.md`)
- Closed #331 (the fnmatch closeout-coverage gap filed during the #328 session), prompted by the operator's "retrospect waste + design the next chunk" request. (source: `charness-artifacts/retro/2026-06-07-issue-331-closeout-fnmatch-idiom.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-07-v0-27-0-release-auto-retro.md`; sources: 11)
- **A deterministic-gate blind spot.** `run_slice_closeout --skip-broad-pytest` (run first, green) does NOT run `check_spec_evidence_durability` (it is a broad-pytest test), so the spec-citation miss only surfaced at minute 6 of run1. (source: `charness-artifacts/retro/2026-06-07-producer-rerun-waste.md`)
- **A misleading false-green pre-commit dry-run.** The pre-commit consumer dry-run used `--head-sha HEAD` while HEAD was the *parent* (changes uncommitted), so `base..HEAD` EXCLUDED my changes → "blocking: []" looked safe, but the gate only judged my changes after commit (drove run3→run4). The dry-run gave false confidence. (source: `charness-artifacts/retro/2026-06-07-producer-rerun-waste.md`)
- **Authoring-preflight skip for new skill-package files.** I authored new `skills/public/quality/scripts/*.py` + `references/*.md` without first running `check_skill_surface_preflight.py` / skimming `authoring-preflight.md`, so the issue-anchor / dated-incident / author-cite / attention-state-declaration constraints bit after the fact — the #308-class trap already in recent-lessons. (source: `charness-artifacts/retro/2026-06-07-325-h3-provenance-gate-capability.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-07-v0-27-0-release-auto-retro.md`; sources: 11)
- a `validate_surfaces` lint that flags any `<dir>/**/*.X` source pattern lacking a `<dir>/*.X` sibling, so the idiom footgun cannot return. Disposition: deferred -> handoff Next Session candidate (anchor surface-idiom-lint), not filed, to avoid issue sprawl for a small hardening. (source: `charness-artifacts/retro/2026-06-07-issue-331-closeout-fnmatch-idiom.md`)
- At task start, verify the target issue's real state (open/closed + last close event) before trusting the goal/handoff "open" framing. Disposition: memory -> recorded in this retro + recent-lessons digest refresh this session. (source: `charness-artifacts/retro/2026-06-07-issue-328-preflight-gate-phase-coverage.md`)
- broaden slice-closeout coverage to top-level scripts (the repo-python fnmatch gap). Disposition: issue -> filed as #331 with the decision framing (source-path widening vs recursive `**`, needs a closeout-cost critique). (source: `charness-artifacts/retro/2026-06-07-issue-328-preflight-gate-phase-coverage.md`)

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
- `charness-artifacts/retro/2026-06-07-325-h3-provenance-gate-capability.md`
- `charness-artifacts/retro/2026-06-07-issue-328-preflight-gate-phase-coverage.md`
- `charness-artifacts/retro/2026-06-07-issue-330-metavalidator-gate-hardening.md`
- `charness-artifacts/retro/2026-06-07-issue-331-closeout-fnmatch-idiom.md`
- `charness-artifacts/retro/2026-06-07-producer-rerun-waste.md`
- `charness-artifacts/retro/2026-06-07-v0-27-0-release-auto-retro.md`
