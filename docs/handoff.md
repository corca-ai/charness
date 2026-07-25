# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. An explicit user task keeps its own authority. The next operator picks
  the smallest coherent backlog slice and closes it end-to-end: mutate canonical
  source, sync generated/plugin mirrors before validators, then prove with the
  mandated bounded fresh-eye critique before commit.

## Continuation Capability

The only open issue is #453; every move below names an owning artifact.

## Current State

- Standing operator direction: bug fixes, friction/rework, test/code speed.
  Release state: [release state](../charness-artifacts/release/latest.md).
- **The seed-budget gate no longer passes a scan that measured nothing.** A
  failed `du` scan used to exit 0. The discriminator is `du`'s output, not its
  exit status; capability gaps stay advisory, everything else blocks.
  [fail-open critique](../charness-artifacts/critique/2026-07-26-seed-fixture-budget-fail-open.md)
- **A gate's escape hatch must be reachable from where the gate fires.**
  `CHARNESS_QUALITY_LABELS` is an allowlist, so a flag the runner does not pass
  leaves only `--no-verify`. Found by release review, after the remediation text
  already promised the flag. [release critique](../charness-artifacts/critique/2026-07-26-v2-9-0-release-critique.md)
- **The handoff may not transcribe a fact a command regenerates** (versions, shas,
  as-of counts); a commit-time gate enforces it. A quoted value is an address,
  not a claim — that carve-out is load-bearing and must not be closed.
- **A gate's measured time is co-scheduled**, so per-gate wall budgets partly
  measure contention; nine `(contended)` bars must be re-derived on any
  parallelism or core-count change. [runner critique](../charness-artifacts/critique/2026-07-26-quality-runner-barrier-removal.md)
- **#453 stays deliberately OPEN** for a human close; its fixes are pushed.

## Next Session

1. **Close #453** once the next **scheduled** mutation run is verified with
   `check_mutation_run_proof.py --claim changed-line --run-id <id>`. A dispatch
   re-run cannot prove it (no `base_sha`).
2. **Re-measure `local-linux-aarch64-4cpu`.** Four bars are `(contended,
   derived)` — raised by this box's contention factor, not measured.
3. **`du_timeout` blocks and is not a capability gap.** Only direct invocation is
   exposed (this repo's runner keys the temp root per repo). Also unprobed: the
   BusyBox/BSD `du` usage-error tokens, backed by no real Alpine or macOS run.
4. **Add a `--restamp-tool-version` path to `check_dup_ratchet.py`.** `run()`
   reaches the restamping `_scoped_rebaseline` only when an id is named, so the
   nose skew warning has no fix that does not absorb the parked #448 items.
5. **The flag gate cannot see argument ORDER** — F7/F8 of its critique; both need
   per-token positions threaded through `split_arguments`. Pinned, not fixed:
   `REPO_ROOT.resolve() / "skills" / "public"` escapes the export-safety
   predicate ([decision point](../tests/quality_gates/test_export_safe_asset_paths.py)).
6. Unowned (sweep signed off): critique packet tier mismatch, specdown preset
   duplication, `recommended_commands` in `plan_cautilus_proof.py`. Still
   deferred: inline `.rglob`/`ls-files` pathspec discovery, D18, D38,
   `CODE_LANGUAGE_FAMILIES` expansion, zero/near-zero test-surface advisory,
   stale basetemps, #451's two unacted siblings.

## Discuss

- Write the violation before writing the guard; reproduce a reviewer's finding
  before fixing it. A gate blocking mid-slice is a design signal, not an obstacle.
- Ask where the operator is standing when the gate fires. Twice now a correct
  remediation was unreachable from the path that produced it.
- Do not re-litigate the two refuted audit findings (removing the dup-ratchet
  hard arm or the boundary-bypass ratchet). #448 items wait for the next slice.

## References

- [fail-open critique](../charness-artifacts/critique/2026-07-26-seed-fixture-budget-fail-open.md) · [release critique](../charness-artifacts/critique/2026-07-26-v2-9-0-release-critique.md) · [flag-gate critique](../charness-artifacts/critique/2026-07-26-documented-command-flag-gate.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
