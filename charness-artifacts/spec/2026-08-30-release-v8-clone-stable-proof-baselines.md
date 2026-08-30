# Clone-Stable Proof Baselines for v8 Release

Date: 2026-08-30

## Problem

Release pytest exposed two forms of local state being mistaken for durable
proof. Artifact commit citations pass in a long-lived authoring object database
but fail in a clean provider clone. Separately, a dated inventory measurement is
treated as an exact mirror of today's growing quality-artifact corpus, forcing
historical snapshot rewrites when safety behavior did not change.

## Capability Contract

Charness's repo-owned release gate must give the same commit-referent verdict
for identical tracked `HEAD` bytes in a clean clone and a long-lived authoring
clone. Intentional local-only historical context must be representable through
one exact, reasoned, stale-checked declaration. The inventory-consumption gate
must evaluate current safety invariants live without rewriting a dated
measurement merely because valid corpus members were added.

## Current Slice

- Replace object-existence authority with reachability from the reviewed `HEAD`
  for artifact commit referents.
- Add one repo-owned declaration surface keyed by artifact path, line, token,
  full-line SHA-256, and nonempty reason for the Goal Draft's intentional
  local-only context; bind its bytes to the Git index candidate.
- Keep declared findings visible; refuse malformed, unmatched, or stale entries.
- Replace full live-payload equality against the dated inventory probe with
  live invariant checks over the current corpus.
- Preserve the dated probe unchanged as historical measurement evidence.

## Fixed Decisions

- Published `HEAD` reachability, not arbitrary object-database presence, is the
  durability authority.
- No prose regex such as "local commit" grants an exemption.
- The declaration is exact and repo-owned; consumer repositories do not inherit
  Charness's local-history declaration.
- Historical measurement records are not rolling mirrors. Current gates derive
  current facts and enforce behavior rather than exact corpus volume.
- A complete HEAD ancestry snapshot is the single reachability owner; a shallow
  repository is unestablished, not evidence that historical commits are absent.

## Probe Questions

- Whether future declaration owners need more policy fields than the exact,
  visible, candidate-bound surface proven in this repo; no generic consumer
  contract is introduced in this slice.

## Deferred Decisions

- A generic consumer-facing local-history declaration format.
- Machine-distinct hosted Mutation Tests execution and mutation score.
- Automatic migration of older grandfathered artifact references.

## Non-Goals

- Editing the frozen Goal Draft to make a gate green.
- Publishing the excluded local commit or merging unrelated local history.
- Treating line counts, corpus counts, or test ratios as consumer value.
- Changing consumer Git, submodule, worktree, or topology policy.

## Deliberately Not Doing

- Do not add a broad token allowlist or date exception.
- Do not refresh the dated inventory probe from 156 to 158.
- Do not skip the release pytest lane or represent Mutation Tests as successful.

## Constraints

- Existing grandfathered findings remain reported and nonblocking.
- Exact declarations remain findings in output and cannot silently disappear.
- A stale declaration blocks so a one-time exception cannot become permanent
  invisible policy.
- Generated plugin mirrors are refreshed only through the canonical sync owner.
- Release publication remains behind claims review, public readback, and
  post-publication install observation.

## Success Criteria

- Identical tracked bytes at one `HEAD` produce the same referent verdict in a
  clean clone and in a repository holding an unrelated side-branch object.
- The two Goal Draft local-context sites are accepted only by exact declaration;
  wrong path, line, token, line content, blank reason, untracked/unstaged bytes,
  or no-longer-failing entry refuses.
- Adding a valid quality artifact does not require rewriting the dated probe
  when current floor safety remains intact.
- Lowered required citations, below-floor label values, refused exemptions, or
  an empty corpus remain blocking current observations.
- The original release-focused failures pass before the release lane is retried.

## Acceptance Checks

- Verification type: unit — a temporary Git repository holds a side-branch-only
  commit; HEAD reachability rejects it despite `cat-file` success.
- Verification type: unit — exact local-context declaration accepts and reports
  the finding; malformed, changed-line, unbound, and stale declarations refuse.
- Verification type: integration — the checked-in artifact-referent corpus test
  passes in the clean release clone without importing the local commit object.
- Verification type: unit — current inventory invariants pass after additional
  valid corpus records while deliberate below-floor and lowered-citation
  controls fail.
- Verification type: integration — the two release pytest nodes pass together,
  then `./scripts/run-quality.sh --release` owns broad confirmation.
- Verification type: performance regression — the full referent corpus uses one
  HEAD ancestry read rather than one Git process per SHA; observed wall time is
  about 2.73 seconds versus about 60.5 seconds for the first implementation.

## Boundary Ownership

- Producer: Git `HEAD`, artifact text, and the current inventory scanner.
- Consumer: the repo-owned artifact-referent and inventory release gates.
- Owner: repo-only gate configuration owns Charness local-history context;
  portable libraries own reachability and live measurement semantics.
- Verdict: owned-correctly.

## Critique

- Interrupt Source: release-v8-artifact-corpus-drift-2026-08-30
- Seam Summary: published HEAD reachability versus authoring-object visibility, and dated measurement versus live corpus.
- Chosen Next Step: factor-first
- Impl Status: allowed
- Impl Status Reason: clean/shared-object differential and live corpus payload
  establish both failure identities; product scope and acceptance are fixed.
- What Disproving Observation Is Resolved: parent tracked bytes pass referents
  only when an unrelated local object is visible, while inventory drift is
  identical at parent and candidate and changes no rule-sensitive invariant.

## Canonical Artifact

This file is the current implementation contract. The debug record owns the
causal evidence; release critique owns the publish decision.

## First Implementation Slice

Implemented HEAD reachability plus candidate-bound exact declarations and
negative fixtures, then replaced mutable full-payload equality with live
invariant assertions. Focused verification is green; Luna counterweight review
and broad release quality remain before publication.
