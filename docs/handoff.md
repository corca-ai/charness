# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <date-slug>`
  BEFORE any brief or reviewer spawn. `--session-id` and `--seed` are both required and
  take the SAME value, so the selection is reproducible and citable. The command now
  prints the frozen bundle path on stderr; cite it in this session's durable artifact.
- Then run `## Next Session` item 1.

## Continuation Capability

- The [release record](../charness-artifacts/release/latest.md) holds the published
  version, its verification state, and the distinct-channel readback.
- The [claims review](../charness-artifacts/release-review/2026-08-17-v6.0.1-prepared-claims-review.md)
  holds the bump rationale, the non-claims, and the three items it generated.
- The digest a session reads before work is [recent lessons](../charness-artifacts/retro/recent-lessons.md).

## Current State

- **A release published this session; the record could not carry its own bump rationale.**
  The [claims review](../charness-artifacts/release-review/2026-08-17-v6.0.1-prepared-claims-review.md)
  holds it, and names the two template defects that forced that.
- **The claims round found a FALSE CLAIM four code rounds missed** — see the corrected
  [release critique](../charness-artifacts/critique/2026-08-17-release-v6-0-1.md), which
  had asserted a rationale lived in a record that has no field for it.
- **`validate_retro_artifact.py` keys its candidate filter and owned prefix on a hardcoded
  prefix while its planner path is adapter-declared.** Not reachable today: the scoping
  that would expose it was reversed before the tag. Reproduce with
  `python3 scripts/validate_retro_artifact.py --repo-root <repo-with-custom-output_dir> --paths <its retro>`.
- **Three verdict-surface edits shipped with one bounded round, not two** — recorded
  `accepted-unreviewed` in the [claims review](../charness-artifacts/release-review/2026-08-17-v6.0.1-prepared-claims-review.md),
  against the two-round floor in [operating contract](./conventions/operating-contract.md).
- **[quality/latest.md](../charness-artifacts/quality/latest.md) is stale** — it asserts as
  open two issues since closed. Deliberately not hand-edited; regenerate, do not patch.
- **The [#548 single-owner pointer resolver](../scripts/scaffold_artifact_lib.py) raises on a
  looping symlink.** Guarded at one call site only; it has five callers.
- Re-prove with `python3 scripts/run_standing_pytest.py` after
  `python3 scripts/sync_root_plugin_manifests.py`, then
  `python3 -m ruff check --no-cache scripts skills tests`, then `-m release_only`.
- **COMMIT the slice, THEN run the changed-line proof** —
  `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --refuse-unestablished`
  reads `base..HEAD`, so a dirty pool proves nothing. Run it BEFORE the broad lane.

## Next Session

1. **Give the release record a bump-rationale field.** Its writer
   [publish_release_artifact.py](../skills/public/release/scripts/publish_release_artifact.py) neither
   takes nor writes one, so the policy's say-why requirement cannot land in the artifact
   an outside reader gets.
2. **Bind two lines in [publish_release_artifact.py](../skills/public/release/scripts/publish_release_artifact.py)
   to their dispositions** — the no-version-drift sentence is an unconditional literal, and
   the adapter focused preflight prints `required` with no executed state.
3. **Give [validate_retro_artifact.py](../scripts/validate_retro_artifact.py) the
   adapter-derived prefix its debug sibling has**, then re-scope the retro shape packet in
   [plan_retro_run.py](../skills/public/retro/scripts/plan_retro_run.py). Its test asserts
   the ABSENCE of `--paths` today and must flip with it.
4. **Regenerate the [quality record](../charness-artifacts/quality/latest.md)** by running
   `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root .` and following
   its plan; do not hand-edit a dated measurement snapshot.
5. **[#636](https://github.com/corca-ai/charness/issues/636) residual** — the scoping half
   shipped; the case-sensitive authoring markers that fail one at a time did not.
6. **Verify-and-close sweep for [#633](https://github.com/corca-ai/charness/issues/633),
   [#631](https://github.com/corca-ai/charness/issues/631),
   [#632](https://github.com/corca-ai/charness/issues/632),
   [#630](https://github.com/corca-ai/charness/issues/630).** Run each issue's own
   reproduction first; do NOT close on code that merely looks right.

## Discuss

- **Consumers owe an upgrade step no shipped surface names.** A symlinked debug
  `latest.md` needs its seam-risk index regenerated after upgrade or `--check` fails.
  Should the release adapter carry per-release update instructions?
- **The boundary-bypass gate has no scoped rotation accept.** Four rotations this session
  each rewrote the whole baseline; the dup ratchet's `--accept-rotation` is the better shape.
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
