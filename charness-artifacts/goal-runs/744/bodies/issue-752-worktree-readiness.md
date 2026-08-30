## Situation

Charness 8.0.0 lets a repository declare one or more `prepare.commands` and defaults the example adapter to `skip_if_doctor_passes: true`. `worktree prepare` skips every declared command whenever the pre-prepare doctor reports `PASS`.

Ceal has two independently locked dependency roots (`package-lock.json` and `agent/package-lock.json`), so its adapter declares a separate `npm ci` command for each root.

## Observed experience

In a fresh isolated Ceal worktree, both dependency trees were absent, but `charness worktree doctor` reported `PASS`. With `skip_if_doctor_passes: true`, `charness worktree prepare` then returned success with no executed commands and the reason `doctor already reports pass; pass --force to run prepare anyway.`

The worktree was isolated and its canonical hook checks were healthy, but it was not ready for repository commands that require either dependency tree. The consumer workaround is now `skip_if_doctor_passes: false`, which always runs both declared installs.

## Evidence

- Installed Charness version: `8.0.0`.
- The shipped worktree adapter example sets `skip_if_doctor_passes: true`.
- `run_prepare()` skips all declared commands solely from `pre_doctor["status"] == PASS`; it does not establish that each declared prepare responsibility is already satisfied.
- The adapter contract allows optional doctor checks, but there is no required or typed relationship between a prepare command and a readiness check. A repository with multiple lockfile roots can therefore accidentally prove only isolation/hooks and still skip all dependency preparation.
- Consumer evidence: `charness-artifacts/ideation/2026-08-28-stage-3-release-inventory.md` in `corca-ai/ceal`, under “Charness 7 friction inventory”.

## Minimal reproduction

1. Configure a worktree adapter with dependency-install commands under `prepare.commands` and `skip_if_doctor_passes: true`, without custom doctor probes for every dependency root.
2. Create a linked worktree whose canonical isolation and hook checks pass, while its dependency directories are absent.
3. Run `charness worktree doctor`; observe `status: pass`.
4. Run `charness worktree prepare`; observe `executed: []` and the skip reason.
5. Run a repository command requiring the absent dependency tree; it fails even though prepare returned pass.

## Impact

The current contract makes a doctor pass look like terminal worktree readiness even when it only proves the checks that happen to be declared. The default skip behavior can silently omit repository-owned setup, especially in repositories with multiple lockfiles or generated/materialized prerequisites.

## Possible direction (non-binding)

Distinguish canonical worktree health from declared preparation readiness, or require an explicit readiness predicate for each skippable prepare responsibility. Making skip opt-in rather than the example/default would also remove the false-ready footgun.

This does not imply that doctor should install dependencies, or that every prepare command must always run.

AI provenance: reproduced and drafted by an OpenAI Codex agent; the operator requested the upstream filing.

---

<!-- charness-work-item-key: issue-752-worktree-readiness -->
# Work Item #752 — Bind prepare readiness to proved responsibilities

## Purpose and premise

Make worktree prepare/doctor report ready only for setup responsibilities the selected doctor actually established.

## Acceptance and proof

Prepared responsibilities pass, omitted responsibilities remain unready, and a false-ready fixture fails. The issue owns its focused behavior verdict and resolution critique.

## Non-claims

No global setup redesign or inference that one healthy dependency proves every setup responsibility.
