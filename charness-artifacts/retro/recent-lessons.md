# Recent Retro Lessons

## Current Focus

- This session picked up the handoff item to remove mutmut from the Charness mutation-testing workflow and migrate the repo dogfood path to Cosmic Ray. (source: `charness-artifacts/retro/2026-05-15-mutation-cosmic-ray-migration.md`)
- Issue 146/148 work found the immediate worktree readiness and cleanup gaps, but the first sibling search stayed too close to the `worktree` noun and nearby CLI surfaces. (source: `charness-artifacts/retro/2026-05-12-worktree-search-generalization.md`)

## Repeat Traps

- A local `.artifacts/cosmic-ray-venv` created for proof leaked into repo-wide Python filename scans until it was removed. The verification environment was useful, but it should have been outside the repo or cleaned before broad gates. (source: `charness-artifacts/retro/2026-05-15-mutation-cosmic-ray-migration.md`)
- `run_slice_closeout.py` initially blocked because the workflow, Cosmic Ray config, and critique packet had no declared surface. The fix was useful but should have been obvious when adding a new workflow/config family. (source: `charness-artifacts/retro/2026-05-15-mutation-cosmic-ray-migration.md`)
- The first pass treated Cosmic Ray dry-run as if the normal summary step could still run. Fresh-eye review caught that dry-run creates no dump, so PR mode would have failed after a successful baseline/init. (source: `charness-artifacts/retro/2026-05-15-mutation-cosmic-ray-migration.md`)
- **Acceptance Checks 미분리**. 첫 draft가 spec-slice (본 파일 land + critique fold) 와 impl-slice (validators + grep + dogfood)를 한 block에 섞어둠. 본 슬라이스가 spec 단독인데 validator가 acceptance에 listed → category error. Hidden Sequencing critique A3.5 catch. (source: `charness-artifacts/retro/2026-05-09-debug-issue-substrate-vs-target-spec.md`)

## Next-Time Checklist

- For workflow migrations with mode branches, add one test that pins each mode's artifact assumptions before running closeout. (source: `charness-artifacts/retro/2026-05-15-mutation-cosmic-ray-migration.md`)
- Keep new workflow/config families in `.agents/surfaces.json` in the same slice that introduces them. (source: `charness-artifacts/retro/2026-05-15-mutation-cosmic-ray-migration.md`)
- Preserve the mutmut structural limit as historical dogfood evidence, but make new handoff state point to first-run Cosmic Ray observation rather than re-debating the pivot. (source: `charness-artifacts/retro/2026-05-15-mutation-cosmic-ray-migration.md`)
- before closing issue-class work, run one structural sibling pass in addition to keyword sibling search. (source: `charness-artifacts/retro/2026-05-12-worktree-search-generalization.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-09-debug-issue-substrate-vs-target-spec.md`
- `charness-artifacts/retro/2026-05-12-worktree-search-generalization.md`
- `charness-artifacts/retro/2026-05-15-mutation-cosmic-ray-migration.md`
