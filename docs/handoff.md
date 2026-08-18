# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <date-slug>`
  BEFORE any brief or reviewer spawn — the REPO'S OWN copy, never the installed one:
  the installed-copy declare wrote a receipt without a ledger event this session, the
  half-written state the continuity gate then refuses (`unknown session` on every score).
- Then run `## Next Session` item 1.

## Continuation Capability

- The [release record](../charness-artifacts/release/latest.md) holds the published
  version, its verification state, and the distinct-channel readback.
- The [#640 critique](../charness-artifacts/critique/2026-08-18-issue-640-resolution.md)
  holds this run's window: the artifact line budget became a consuming repo's adapter
  setting, over six bounded reviewer spawns across four rounds.
- The [quality record](../charness-artifacts/quality/2026-08-18-quality-review.md) holds
  the current posture: gates, runtime signals, the pytest budget breach, and the
  recommended next quality moves.
- The [digest](../charness-artifacts/retro/recent-lessons.md) holds what a session reads
  before work. Main and the released tag are pushed; remote and local are in sync.

## Current State

- **#640 is CLOSED**: `max_artifact_lines` (debug, quality) and `max_content_lines`
  (handoff) are adapter fields; seven surfaces resolve them through
  [resolve_adapter_line_budget](../scripts/artifact_validator.py). Inventory:
  `gh issue list --repo corca-ai/charness --state open`.
- **The pytest budget bar is RED and this session pushed past it with `--no-verify`**,
  on an explicitly re-authorized grant. Not a regression: isolated A/B on one machine
  read base 87.4s vs head 85.8s, ~40s under the in-gate figure, so most of the gap is
  contention. Do NOT relevel — the adapter's REVISIT TRIGGER fired and is filed as
  [#668](https://github.com/corca-ai/charness/issues/668), which owes profiling or a
  smaller standing set. The next push should not repeat the bypass.
- **The resume lane deliberately runs NO surface gate and NO focused preflight**; the
  three reasons sit at the [publish_release_resume_publish.py](../skills/public/release/scripts/publish_release_resume_publish.py) call site.
- **The [#548 single-owner pointer resolver](../scripts/scaffold_artifact_lib.py) raises on a
  looping symlink.** Guarded at one call site only; it has five callers.
- Re-prove with `python3 scripts/run_standing_pytest.py` after
  `python3 scripts/sync_root_plugin_manifests.py`, then
  `python3 -m ruff check --no-cache scripts skills tests`, then
  `python3 -m pytest -q -m release_only`.
- **COMMIT the slice, THEN run the changed-line proof** —
  `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --refuse-unestablished`
  reads `base..HEAD`, so a dirty pool proves nothing. Run it BEFORE the broad lane.

## Next Session

1. **#640's two stated non-claims owe small slices.** No test drives
   `plugins/charness/` against a synthetic consumer, so the installed half rests on a
   byte-identical mirror plus a static import trace. And a handoff adapter with an
   UNSUPPORTED `version` drops `max_content_lines` via the early return in
   [simple_skill_adapter_lib](../scripts/simple_skill_adapter_lib.py), while debug does
   not — a real divergence, left alone because that return binds nine skills.
2. **Migrate the lesson-ledger directory in ONE slice, or not at all.** Scope it with
   `grep -rln "charness-artifacts/retro" scripts/ skills/ tests/ .agents/ plugins/`; a
   `scripts/`-only sweep misses
   [seed_retro_memory.py](../skills/public/setup/scripts/seed_retro_memory.py). Moving one
   site was tried twice and reverted twice — `canonical_retro_citation` and
   `collect_retro_candidates` are what make the literal load-bearing.
3. **`run_release_adapter_preflight` shells out to a bare test-runner binary**, so a
   venv-only install gives a traceback where a refusal belongs; the shell-out lives in
   [publish_release_adapter_preflight.py](../skills/public/release/scripts/publish_release_adapter_preflight.py) itself.
4. **[#639](https://github.com/corca-ai/charness/issues/639) carries the lesson-session
   START-surfacing work**, now with two more anchors from this run: the installed-copy
   declare that half-writes, and the atomicity gap the retro's capability improvement
   names. [#638](https://github.com/corca-ai/charness/issues/638) holds the per-round
   critique findings artifact.
5. **Two recorded review residuals await their small slices** — the wrapped-line
   `blocked` asymmetry in [critique_enforcement_scope.py](../scripts/critique_enforcement_scope.py),
   and the retro planner/scaffold disagreeing on the second-dated-retro path; both are
   in the [session retro](../charness-artifacts/retro/2026-08-18-session-retro-second.md)
   Sibling Search.

## Discuss

- **Consumers owe an upgrade step no shipped surface names.** A symlinked debug
  `latest.md` needs its seam-risk index regenerated after upgrade or `--check` fails.
  Should the release adapter carry per-release update instructions?
- **The boundary-bypass gate has no scoped rotation accept.** Four rotations in the last
  release session each rewrote the whole baseline; the dup ratchet's `--accept-rotation`
  is the better shape.
- **This bullet IS an SC14 anchor — do not tidy it away.** The
  [dominance test](../tests/quality_gates/test_command_dominance.py) substitutes into the
  real handoff and needs the bare backticked `python3 scripts/run_standing_pytest.py`, with no flags inside
  the backticks, present here.

## References

- The [design north star](./design-north-star.md) holds the different-observer rule and
  the proof-surface reading of the irreversible boundary.
- The [operating contract](./conventions/operating-contract.md) holds the two-round
  critique floor and the write-capable isolation rule.
- [Implementation discipline](./conventions/implementation-discipline.md) holds the
  `mutate -> sync -> verify -> publish` order and the generated-surface rule.
