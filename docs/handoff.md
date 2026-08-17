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

- **Five critique rounds ran; the last round's repairs are `accepted-unreviewed`.** The
  record is the [session critique](../charness-artifacts/critique/2026-08-17-session-release-record-retro-prefix.md),
  whose Fresh-Eye section labels its own unfalsifiable parts. Every round found the
  previous round's repair carrying the class it repaired.
- **The resume lane deliberately runs NO surface gate and NO focused preflight**; the three
  reasons are at the call site in
  [publish_release_resume_publish.py](../skills/public/release/scripts/publish_release_resume_publish.py).
- **The release record carries a bump rationale**, quoted verbatim and emitted LAST so
  no construct in it can hide the record; see
  [version-policy.md](../skills/public/release/references/version-policy.md).
- **`validate_retro_artifact.py` resolves its prefix from the adapter**, and the retro
  planner's shape packet is scoped again. Reproduce the old defect with
  `python3 -m pytest tests/quality_gates/test_retro_artifact_validation.py -k custom_output_dir`.
- **[quality/latest.md](../charness-artifacts/quality/latest.md) is still stale** — it
  asserts as open two issues since closed. Regenerate, do not patch; see item 1.
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

1. **This session owes a retro and did not write one.** Confirm with
   `python3 skills/public/retro/scripts/check_auto_trigger.py --repo-root . --base-ref da6913245`.
   A lesson session was declared at open, so the disposition floor applies. Write it FIRST.
2. **Regenerate the [quality record](../charness-artifacts/quality/latest.md)** by running
   `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root .` and following
   its plan. It is a full `quality` workflow, not a rerun: six required reads, a structural
   review packet, and a maintainer-local enforcement disposition. Do not hand-edit it.
3. **[#636](https://github.com/corca-ai/charness/issues/636) residual** — its scoping half
   shipped. The case-sensitive authoring markers that fail one at a time did not; read the
   issue for what remains, because no artifact in this repo records it.
4. **Verify-and-close sweep for [#633](https://github.com/corca-ai/charness/issues/633),
   [#631](https://github.com/corca-ai/charness/issues/631),
   [#632](https://github.com/corca-ai/charness/issues/632),
   [#630](https://github.com/corca-ai/charness/issues/630).** Run each issue's own
   reproduction first; do NOT close on code that merely looks right.
5. **Prove `--bump-rationale` survives a real resume.** It is rebuilt from arguments and
   nothing refuses the omission; only the planner's
   [repeat_original_arguments](../skills/public/release/scripts/plan_release_run_packets.py)
   names it. The warning is unconditional in three places but only the non-claims lane
   can actually lose it — the claims lane skips the artifact write.
6. **Migrate the lesson-ledger directory in ONE slice, or not at all.** Scope it with
   `grep -rln "charness-artifacts/retro" scripts/ skills/ tests/ .agents/ plugins/`; a
   `scripts/`-only sweep misses
   [seed_retro_memory.py](../skills/public/setup/scripts/seed_retro_memory.py). Moving one
   site was tried twice and reverted twice — `canonical_retro_citation` and
   `collect_retro_candidates` are what make the literal load-bearing.
7. **`run_release_adapter_preflight` shells out to a bare test-runner binary**, so a
   venv-only install gives a traceback where a refusal belongs
   ([publish_release_adapter_preflight.py](../skills/public/release/scripts/publish_release_adapter_preflight.py)).
8. **The critique validator refuses the value its own skill teaches** —
   [critique_enforcement_scope.py](../scripts/critique_enforcement_scope.py)'s
   `PACKET_ABSENT_VALUES` omits `blocked`, so an honestly skipped packet declared the way
   `charness:critique` prescribes demands SHAs for a packet just declared absent.

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
