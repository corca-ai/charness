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
  holds the published release's bump rationale and non-claims; its three code items ship here.
- The digest a session reads before work is [recent lessons](../charness-artifacts/retro/recent-lessons.md).

## Current State

- **Both critique rounds ran; round-2 repairs are `accepted-unreviewed`.** The floor in
  [operating contract](./conventions/operating-contract.md) caps at two rounds, so the
  fixes in the final commit were read by nobody. Round 1 returned eight blockers.
- **The resume lane deliberately runs NO surface gate and NO focused preflight.** One was
  added there and reverted; see the comment in
  [publish_release_resume_publish.py](../skills/public/release/scripts/publish_release_resume_publish.py).
  Its record says "NOT recorded by this helper invocation", which is true of that lane.
- **The release record carries a bump rationale, quoted verbatim.**
  `--bump-rationale` reaches a `## Bump Rationale` section; `version_drift_check` is set
  on the execute lane only, and renders as unrecorded everywhere else.
- **`validate_retro_artifact.py` resolves its prefix from the adapter**, and the retro
  planner's shape packet is scoped again. Reproduce the old defect with
  `python3 -m pytest tests/quality_gates/test_retro_artifact_validation.py -k custom_output_dir`.
- **[quality/latest.md](../charness-artifacts/quality/latest.md) is still stale** — it
  asserts as open two issues since closed. Regenerate, do not patch; see item 1.
- **The [#548 single-owner pointer resolver](../scripts/scaffold_artifact_lib.py) raises on a
  looping symlink.** Guarded at one call site only; it has five callers.
- Re-prove with `python3 scripts/run_standing_pytest.py` after
  `python3 scripts/sync_root_plugin_manifests.py`, then
  `python3 -m ruff check --no-cache scripts skills tests`, then `-m release_only`.
- **COMMIT the slice, THEN run the changed-line proof** —
  `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --refuse-unestablished`
  reads `base..HEAD`, so a dirty pool proves nothing. Run it BEFORE the broad lane.

## Next Session

1. **Regenerate the [quality record](../charness-artifacts/quality/latest.md)** by running
   `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root .` and following
   its plan. It is a full `quality` workflow, not a rerun: six required reads, a structural
   review packet, and a maintainer-local enforcement disposition. Do not hand-edit it.
2. **[#636](https://github.com/corca-ai/charness/issues/636) residual** — the scoping half
   shipped (both halves now); the case-sensitive authoring markers that fail one at a time
   did not.
3. **Verify-and-close sweep for [#633](https://github.com/corca-ai/charness/issues/633),
   [#631](https://github.com/corca-ai/charness/issues/631),
   [#632](https://github.com/corca-ai/charness/issues/632),
   [#630](https://github.com/corca-ai/charness/issues/630).** Run each issue's own
   reproduction first; do NOT close on code that merely looks right.
4. **Prove `--bump-rationale` survives a real resume.** It is rebuilt from arguments, so a
   dropped flag publishes a record saying none was recorded. Only the planner's
   [repeat_original_arguments](../skills/public/release/scripts/plan_release_run_packets.py)
   names it; nothing refuses the omission.
5. **Round-2 residuals, all disclosed and none fixed.** `run_release_adapter_preflight`
   shells out to a bare test-runner binary, so a venv-only install gives a traceback
   where a refusal belongs
   ([publish_release_adapter_preflight.py](../skills/public/release/scripts/publish_release_adapter_preflight.py)).
   ~20 lesson-lifecycle scripts still hold the literal `charness-artifacts/retro/`; find
   them with `grep -rln "charness-artifacts/retro" scripts/`. `seed_retro_memory.py` is
   the one that reports a state contradicting the retro validator.

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
