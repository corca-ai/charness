# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. An explicit user task keeps its own authority. The next operator picks
  the smallest coherent backlog slice and closes it end-to-end: mutate canonical
  source, sync generated/plugin mirrors before validators, then prove with the
  mandated bounded fresh-eye critique before commit.

## Continuation Capability

No open issues; every move below names an owning artifact.

## Current State

- Standing operator direction: bug fixes, friction/rework, test/code speed.
  Release state: [release state](../charness-artifacts/release/latest.md).
- **The seed-budget gate no longer passes a scan that measured nothing.** A
  failed `du` scan used to exit 0. The discriminator is `du`'s output, not its
  exit status; capability gaps stay advisory, everything else blocks.
  [fail-open critique](../charness-artifacts/critique/2026-07-26-seed-fixture-budget-fail-open.md)
- **A gate's escape hatch must be reachable from where the gate fires.**
  `CHARNESS_QUALITY_LABELS` is an allowlist, so a flag the runner does not pass
  leaves only `--no-verify`. [release critique](../charness-artifacts/critique/2026-07-26-v2-9-0-release-critique.md)
- **The handoff may not transcribe a fact a command regenerates**; a commit-time
  gate enforces it. A quoted value is an address, not a claim.
- **A runtime profile keys on affinity, not `os.cpu_count()`.** A `taskset` run
  used to file its slow samples into the unrestricted profile and drag that
  profile's median toward its bar. Measure under a CPU limit and check which
  profile the samples land in. [five-item critique](../charness-artifacts/critique/2026-07-26-handoff-backlog-five-items.md)
- **A direct push to main now gets the changed-line signal.** The CI mirror was
  PR-only while pre-push defuses itself off the coverage-producer path, so seven
  auto-filed issues came from one gap. [#453 critique](../charness-artifacts/critique/2026-07-26-issue-453-resolution.md)

## Next Session

1. **Sweep the ~14 named same-class siblings** of #453: unasserted rejection and
   renderer lines in `quality_policy_defaults.py` (`:442`, `:447`, `:483`, `:488`,
   `:438`, `:479`, `:503`, `:319`, `:307`, `:328`, `:335`) and
   `runtime_budget_lib.py` (`_render_hotspot`, the `format_human` WARN suffix).
   Start with `:442`/`:447` vs `:483`/`:488` — two near-identical blocks whose
   eventual consolidation reproduces #453's exact seam.
2. **`local-linux-aarch64-4cpu` bars are FLOORS, not measurements.** The
   core-count term is measured; the architecture term is an explicit assumption.
   A run on the real box replaces them. That block also has no aggregate bar.
3. **The BSD/macOS `du` `illegal option` wording is unprobed.** BusyBox and GNU
   are now measured against real binaries; that third wording is not.
4. **The flag gate cannot see argument ORDER** — F7/F8 of its critique. Pinned,
   not fixed: `REPO_ROOT.resolve() / "skills" / "public"` escapes the
   export-safety predicate ([decision point](../tests/quality_gates/test_export_safe_asset_paths.py)).
5. Unowned (sweep signed off): critique packet tier mismatch, specdown preset
   duplication, `recommended_commands` in `plan_cautilus_proof.py`. Still
   deferred: inline `.rglob`/`ls-files` pathspec discovery, D18, D38,
   `CODE_LANGUAGE_FAMILIES` expansion, zero/near-zero test-surface advisory,
   stale basetemps, #451's two unacted siblings.

## Discuss

- Write the violation before writing the guard; reproduce a reviewer's finding
  before fixing it. A gate blocking mid-slice is a design signal, not an obstacle.
- Check the payload shape before citing a green run: "not in blocking_targets" was
  an ABSENCE OF ANALYSIS, not a verdict. Ask what the measurement measured.
- Do not re-litigate the two refuted audit findings (removing the dup-ratchet
  hard arm or the boundary-bypass ratchet). #448 items wait for the next slice.

## References

- [fail-open critique](../charness-artifacts/critique/2026-07-26-seed-fixture-budget-fail-open.md) · [release critique](../charness-artifacts/critique/2026-07-26-v2-9-0-release-critique.md) · [flag-gate critique](../charness-artifacts/critique/2026-07-26-documented-command-flag-gate.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
