# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- For another quality-improvement loop, start with `quality` for gate posture,
  then move to `impl` for one narrow slice. Before mutating, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **v0.56.6 is published and verified.** `origin/main` is `15d0f038`
  (`Record release verification for v0.56.6`); tag `v0.56.6` points at
  `cb815f45`. Public release URL verified HTTP 200:
  `https://github.com/corca-ai/charness/releases/tag/v0.56.6`.
- Installed Charness was refreshed: `charness update` moved `0.56.5 -> 0.56.6`;
  `charness doctor --json` reported installed checkout, Codex cache, Claude plugin,
  and manifests at `0.56.6`. Existing Codex/Claude sessions may still need restart.
- Latest material slice shipped
  [suggest_mutation_coverage_command.py](../scripts/suggest_mutation_coverage_command.py)
  and fixed broad pytest proof scoping for `run_slice_closeout.py --base`.

## Next Session

- **First high-value loop:** improve the new focused coverage producer UX. Candidate
  slices: add clearer `--help`/status guidance for `recommended`, `partial`,
  `missing`, and `noop`; then consider closeout auto-discovery that offers the
  suggested `--mutation-coverage-command` without hiding the explicit proof path.
- **Second high-value loop:** harden release planning evidence scope. The release
  critique caught that clean-worktree planning can miss commit-range real-host
  triggers; test or improve the planner/helper path so release proof is evaluated
  from the intended release delta, not just current dirty paths.
- **When touching coverage speed:** run
  `python3 scripts/suggest_mutation_coverage_command.py --repo-root . --json`
  before broad coverage fallback, but do not overclaim staged-slice timings. Use
  final commit-range producer timing as the release/closeout number.
- **When reviewing broad pytest proof:** compare top-level closeout `changed_paths`
  with `recorded_broad_pytest_proofs.changed_paths`. Any narrower proof record is
  evidence-scope drift, not harmless JSON noise.

## Discuss

- Whether closeout should auto-run the suggested focused producer or only print a
  command remains a design call: automation saves time, but explicit producer
  selection keeps changed-line proof easier to audit.
- `dup-ratchet` may flag boilerplate family-id rotations after helper additions.
  Inspect family members first; classify intentional standalone-script bootstraps
  or CLI wrappers only after confirming they are not extractable behavior.
- External tool advisories remain non-blocking but visible: `agent-browser`,
  `github-gh`, and `nose` had newer upstream releases during v0.56.6 proof.

## References

- [release v0.56.6 proof](../charness-artifacts/release/latest.md)
- [release critique](../charness-artifacts/critique/2026-06-27-release-0.56.6-focused-mutation-coverage.md)
- [broad pytest proof debug](../charness-artifacts/debug/2026-06-27-broad-pytest-proof-base-scope.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
