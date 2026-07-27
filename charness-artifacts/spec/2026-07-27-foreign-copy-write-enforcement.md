# Spec — Foreign-Copy Write Enforcement

Date: 2026-07-27

Status: decided 2026-07-27 — option 3 + option 2 adopted, option 1 rejected;
extended 2026-07-27 with Decision 2 (containment exemption, bug-hunt A1/A2)

Executed in `9356697a`: the misleading validator message is fixed (#462, closed)
and the entrypoint guard landed with its six review defects repaired and its
claim reduced to "fast failure for copies that carry it". Option 1 was rejected
because recompute-and-compare applies only to derived artifacts and a provenance
stamp needs cooperation the stale copy cannot give; the residual it exposed is
tracked separately as #463.

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

## Decision (resolved — see Status)

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

## Decision 2 — the containment exemption (A1/A2)

Decided 2026-07-27. Scope: `inspect_helper_provenance` returned `same-tree` for
any copy merely *contained in* the target root, and this repo's packaging manifest
declares the checked-in `plugins/charness` tree as an install source
(`packaging/charness.json:59-60`). So the copy that is stale during every
`mutate -> sync` window is structurally exempt — bug-hunt
[A1](../audit/2026-07-27-evidence-surface-bug-hunt.md). The decision the fix
needed first was whether removing that exemption refuses legitimate in-repo
mirror invocations.

**It does not.** Measured against the live tree with the containment clause
removed: `own_root` resolves to `plugins/charness` (the mirror carries its own
`scripts/runtime_bootstrap.py`), versions agree, and a tree scan resolves a
counterpart for **all 605** scanned modules with **0 drifted**, measured after
the export sync (`compared_pairs == compared_count == 605`; before the `shared/` remap below, 4 of the 605 were
scanned but never compared). A synced mirror invocation therefore moves from
`same-tree` (passed without comparing anything) to `in-sync` (passed after
comparing everything). Refusal arrives only while the mirror carries older logic
than the repo it is writing, which is the condition the guard exists for.
Consuming repos are unaffected — their target is not a charness source tree, so
they still classify `consuming-repo`. At decision time no test pinned the
containment behavior (the mirror-executing tests target `tmp_path`); the slice
adds four that do.

**And it should refuse there,** with a narrower claim than the first draft of
this section made. The structural constraint above — a guard is absent from
exactly the copies that need it — still applies to the contained copy, because
`runtime_bootstrap.import_repo_module` loads the guard from the *invoked* tree:
a mirror invocation runs the mirror's own `helper_provenance_lib`, so a change to
the guard module itself is unenforced until the next sync. What shrinks is the
horizon, not the constraint — one sync window instead of one host-managed
`charness update` cycle, and one file instead of the whole tree, since a sync
repairs every other module at the instant it repairs the guard. What this repo
fully controls is the *sync*, not the enforcement. That is still worth having:
it is the only copy whose staleness this repo can end with one command.

Two couplings make the A1 fix alone leaky, so they land with it:

- `counterpart_path` has no `shared/` -> `skills/shared/` remap, so the export's
  four `shared/scripts/*.py` modules resolve to no counterpart and are skipped
  silently. Confirmed: they are exactly the 4 no-counterpart files in the scan
  above.
- **A2**: when the invoked entry script has no counterpart, an already-computed
  non-empty `drifted` list is discarded and the write is allowed as
  `consuming-repo`. With the remap missing, the four `shared/` helpers are entry
  points that take that path. A version mismatch is discarded on the same
  branch, and there the anchors scan has compared the entry point not at all —
  so both signals now survive the existence test, and only "versions agree and
  nothing drifted" still classifies `consuming-repo`.
- The anchor sibling glob in `_tracked_files` was keyed on `skills`, so an
  exported `support/`- or `shared/`-rooted entry point compared one lone file
  while its siblings drifted unseen (the second half of open item A9).

Accepted cost, stated at full width: the mirror is refused during **every**
window between editing any `scripts/**` or `skills/**` Python file and running
the export sync — not only the release-bump window. That is most of a working
session, and the release-bump case (version manifests differ with no code drift)
is the subset that killed two `2.11.2` publishes. It stays a refusal rather than
a carve-out; the escape hatch is `CHARNESS_ALLOW_FOREIGN_HELPER=1`, and the
in-repo remedy is to invoke `skills/`/`scripts/` directly, which is what the
operator contract already says.

Residual, unconfirmed: a git worktree created *inside* the repo is also a
contained second source tree and would now be compared. Documented usage puts
worktrees outside the repo (`docs/worktree-prepare.md`), so no live instance was
found — but "no legitimate path regresses" is asserted for that shape, not
proven.

Rejected: keeping the exemption and relying on the commit-time mirror-drift gate
instead. That gate fires at commit, after the bad artifact is already written,
and the failure this class produces is a wrong-schema artifact mid-publish.

Non-goal for this decision: a live test that runs the real mirror against the
real repo root. It would fail during any legitimate `mutate -> sync` window and
duplicates `check_staged_mirror_drift`; a new blocking floor is not warranted
here (Floor-Addition Restraint: advisory-vs-floor call recorded, existing gate
covers it).

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

- **UNMET, tracked as [#463](https://github.com/corca-ai/charness/issues/463).**
  A drifted foreign copy cannot land an artifact in this repo without something
  refusing, **for at least one enforcement path that does not live in the
  drifted copy**. Only option 1 can satisfy this; Decision 2 does not advance it,
  since the new enforcement also lives in the invoked copy.
- **Decision 2 scope only.** A drifted *contained* copy (the checked-in
  `plugins/charness` mirror) is compared rather than exempted, a synced one still
  writes, and a verdict reached with nothing compared refuses as
  `scope-unestablished` instead of passing.
- The refusal names a remediation that terminates.
- No legitimate path regresses: repo-local invocation, CI, `charness update`,
  consuming repos, and the in-repo `plugins/charness` mirror probe.

## Critique

- Interrupt Source: absent-guard-not-dead-guard
- Seam Summary: the installed-copy lifecycle (`charness update` pull cadence), host-managed rather than repo-managed
- Chosen Next Step: impl
- Impl Status: allowed
- Impl Status Reason: Decision 2 needs no host-lifecycle change, which is the
  part the interrupt says local reasoning cannot prove. The contained mirror's
  revision is set by this repo's own sync step, so the enforceable side is
  in-repo and the impl stays inside what local reasoning can establish.
- What Disproving Observation Is Resolved: the guard is no longer absent from
  the copy that runs in this repo's own tree — a stale `plugins/charness` mirror
  is compared (605 modules) and refused instead of exempted as `same-tree`,
  while a synced mirror still writes.

Fresh-eye review (bounded, read-only) returned eight defects against the first
draft of this slice; all were repaired before closeout. Load-bearing ones: the
no-counterpart remediation told the operator to resync and re-run, which does not
terminate when the resync is what deletes the entry point; the A2 fix rescued
`drifted` but still let the coarse existence test absorb a `version_mismatch`;
`compared_count` counted files scanned, not counterparts compared, so both the
test assertion and this document's "605" claimed a scope neither had established;
the four new tests all ran `scan="tree"` while the five guarded write sites run
the default anchors scan; and the module docstring plus
`skills/shared/references/bootstrap-resolution.md` still stated the pre-change
contract. The audit ledger rows for A1/A2/A9 were also left stale.

Held back deliberately: no live test runs the real mirror against the real repo
root. It would fail during every legitimate `mutate -> sync` window and
duplicates `check_staged_mirror_drift`.
