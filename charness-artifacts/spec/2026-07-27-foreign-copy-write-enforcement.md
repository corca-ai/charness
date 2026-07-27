# Spec — Foreign-Copy Write Enforcement

Date: 2026-07-27

Status: draft — operator decision pending

## Problem

A charness helper invoked from one tree can be pointed at a different charness
source tree with `--repo-root`. When the invoked copy's libraries lag the target
repo, it writes artifacts in a schema the target repo's own gates reject. Six
release publishes have now died to this shape: four named in
`scripts/helper_provenance_lib.py:5-8`, plus two on 2026-07-27.

`require_repo_local_helper` was added to stop it, and it works — the guard
correctly classifies a drifted copy as `drifted` when it runs. It did not run on
2026-07-27 for a reason no amount of hardening the guard can fix:

**the installed copy predated the commit that introduced the guard.**

Full RCA:
[2026-07-27-absent-guard-not-dead-guard.md](../debug/2026-07-27-absent-guard-not-dead-guard.md).

## The structural constraint

Enforcement placed in the invoked copy is absent from exactly the population
that needs it. A copy stale enough to write a bad artifact is, by the same
staleness, capable of being stale enough to lack the check. Every guard we add
producer-side closes the class only for copies updated *after* the guard ships —
one `charness update` later, and never for the copy that skipped that update.

This is not an argument against the producer-side guard. It is an argument that
the producer-side guard cannot be the *only* answer, and must not be described
as closing the class.

What actually contained the 2026-07-27 incident was the **consumer** side: the
target repo's `validate-retro-lesson-index` rejected the foreign artifact and
the publish rolled back. Target-side detection worked and failed closed.

## Decision needed

Three candidate directions, not mutually exclusive:

1. **Target-side provenance record.** Artifact writers stamp which tree wrote
   them; a target-repo gate rejects a write whose provenance does not match the
   repo. Enforceable regardless of the caller's age, because the check lives in
   the repo being written. Cost: a provenance field on written artifacts and a
   gate to read it.
2. **Caller-side entrypoint guard (drafted, staged, uncommitted).** Refuse at
   `publish_release.py` / `issue_tool.py close-with-comment` before any mutation,
   using a whole-tree scan so a lazily-imported drifted module is caught. Buys a
   fast, well-worded failure with a runnable remediation — but only for copies
   new enough to contain it. Six defects found in bounded review must be fixed
   first (see Non-Goals).
3. **Improve the consumer-side message only.** The gate that fires already
   contains the truth; its remediation just points the wrong way
   ([#462](https://github.com/corca-ai/charness/issues/462)). Cheapest, and it
   shortens every future occurrence of this class regardless of caller age.

Recommendation: (3) unconditionally, (1) as the real closure, (2) as defense in
depth with its claim reduced to "faster failure once installed".

## Non-Goals

- Not closing this class with a producer-side guard alone; the RCA shows that is
  structurally impossible.
- Not landing the staged entrypoint guard as-is. Bounded review found: the
  repo's own release planner (`plan_release_run_packets.py:157`) emits the
  `$SKILL_DIR` command the guard now refuses; `format_refusal`'s remediation is
  not runnable at an entrypoint with required arguments; `_TREE_SCAN_ROOTS`
  misses the exported `support/` and `shared/` layouts; `counterpart_path` drops
  the identity candidate for `skills/shared/**`; the hand-rolled `--repo-root`
  parser is bypassed by argparse abbreviation (`--repo`); and `--help` plus the
  read-only `--prep-update-instructions` are refused.
- Not changing `charness update` cadence; the installed-copy lifecycle is
  host-managed and out of this repo's control.

## Success Criteria

- A drifted foreign copy cannot land an artifact in this repo without something
  refusing, **for at least one enforcement path that does not live in the
  drifted copy**.
- The refusal names a remediation that terminates.
- No legitimate path regresses: repo-local invocation, CI, `charness update`,
  consuming repos, and the in-repo `plugins/charness` mirror probe.
