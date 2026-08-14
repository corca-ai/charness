# 6.0.0 Release Scope

Status: in-progress
Date: 2026-08-15
Source: docs/handoff.md `## Next Session`, open issues #527-#632, owner scope
decision recorded in this session (wide scope, all four themes in one release)

## Problem

Shipped is `5.2.0`. `6.0.0` was prepared on 2026-08-14 and never published, and
the 2026-08-15 `--json` removal landed on top of it (`eae80f660`). Three things
follow, and they are the whole problem:

1. **The prepared release notes are false for the tree they would ship.** They
   say *"twelve public skill scripts still declare `--json`, and that is the
   convention"* and *"do not read this as 'the flag is gone repo-wide'"*.
   Measured on `eae80f660`: **zero** scripts declare their own `--json`; the only
   remaining spellings are `gh --json` pass-throughs and one `--json-path`. A
   consumer following these notes under-migrates. The notes were repaired for
   four false claims on 08-14 and were stale again within one day — the same
   false-completeness class the migration retro names, recurring in the notes
   channel.
2. **The publish path cannot satisfy its own contract.** #608:
   `publish_release.py --execute` bumps, syncs, verifies, tags, pushes, and
   creates the GitHub release in one execution, with no seam for the required
   pre-publication claims review.
3. **Ten fixes are stranded behind the publish.** #618-#627 are fixed in-repo
   and still reproduce for their reporters, because nothing installable changed.
   Their closability depends on the publish, not on more repair.

The owner chose the wide scope: the remaining live defect classes ship in the
same release rather than in a follow-up.

## Capability Contract

A maintainer publishes one `6.0.0` whose notes are **derived from the tree being
shipped** rather than hand-maintained, through a publish path that can pause for
the claims review the contract requires. The release carries the live defect
classes still open after the migration: destructive artifact scaffolds, the
non-functional lesson loop, the unheld docs-graph bar, the structural
verification gaps, and two operating-contract rules the session's own incidents
earned. After publish, #618-#627 close against executed proof.

## Current Slice

The whole release, sequenced S1-S7 below. Each S is its own commit and its own
`impl` -> `prove` closeout; the release executes only after S1-S6 are green.

## Sequence

Ordering is by dependency pressure, not by theme grouping.

- **S1 — tooling and release-path correctness.** #599 first: it is the force
  multiplier for every later slice (seven wrong removal proposals in one session,
  each refutable by one grep). Then #608's claims-review pause, `--no-cache` on
  the ruff verification path, and #630 (`npm exec --no`, one line).
- **S2 — destructive defects.** #628: `debug`'s scaffold points its write path at
  an unrelated OPEN investigation. #620 fixed this producer defect for the
  `quality` family only; #628 proves it is a class. Fix the class — one
  current-pointer/date-coherence guard across scaffold families — not the second
  instance.
- **S3 — lesson loop.** Refresh the #617 spec and close its debug interrupt (the
  capability shipped in `eae80f660`; this session's own run produced a bundle).
  Then the score outcome vocabulary, #631, #626, #627.
- **S4 — docs graph.** #629 at the handoff scaffold, then this repo's own
  `link_only_lines` **254** -> 0, then make `check_docs_graph.py` assert the
  count it already parses (`:12-18` still reads only `orphans`/`islands`).
- **S5 — structural umbrellas.** #586 (a check that passes its own direct-call
  test while never firing on the wired path), then #584, #583, #582.
- **S6 — operating contract.** No-mutating-git for write-capable subagents; a
  monitored-phase path for long-running children.
- **S7 — release execution.** Regenerate the notes from the final tree, gate
  them, run the release critique, publish, then close #618-#627.

## Fixed Decisions

- **The release notes are a derived surface, regenerated last and gated.**
  Hand-authoring them at any point before S6 is complete guarantees they go
  stale again; that has now happened twice in two days. The generator's input is
  the shipped tree, and a gate refuses a publish whose notes disagree with it.
  This is the one structural change that makes the recurrence impossible rather
  than unlikely.
- **Notes regeneration is not a rewrite of the prose.** The claim surfaces that
  drifted are enumerable — flag inventories, probe payload shapes, scanned
  surfaces. Those are derived and asserted; the operator-facing narrative around
  them stays authored.
- **#628 is fixed as a class, not as the debug instance.** The second occurrence
  of a producer defect is the evidence that the first fix was scoped wrong.
- **#626/#627 are redefined to their title scope and resolved in this release**
  (owner decision). Their titles promise a fillable resurrection slot and
  rewritten lessons; the release delivers those, so the titles stop outrunning
  the code instead of the issues being narrowed to what already shipped.
- **The bump is major.** `--json` removal breaks invocation expectations. Target
  `6.0.0` is already what `plan_release_run.py --part major` computes from
  `5.2.0`.
- **Nothing is closed before the publish.** #618-#627's closability is gated on
  an installable artifact, and the issue closeout floor refuses a close whose fix
  exists only in unpushed local commits.
- **The classification ledger is written before any close.** The 8-fixed /
  3-broken / 4-partly-valid split for #618-#632 currently exists only as a
  sentence in `docs/handoff.md`; no checked-in ledger artifact carries it, and
  the closeout floor requires one.

## Probe Questions

- **What is the smallest honest slice of #582/#583/#584?** All three are
  umbrellas whose members are CLOSED and whose class is declared LIVE. That shape
  has no natural stopping point. Probe: land one executable guard per umbrella,
  measure what it catches on the current tree, and defer the rest with the
  measurement attached. Answer this in S5 before expanding scope.
- **Is `link_only_lines` 0 reachable without damaging the docs?** 254 lines is a
  large rewrite, and the linter's rationale (a lone link gives no local context)
  is a readability claim, not a formatting one. Probe on the twenty worst lines
  first; if the rewrite reads worse, the honest outcome is a declared bar above 0
  that the gate holds, not 0.
- **Does lifecycle promotion still belong to `quality`?** The 2026-08-12 ledger
  spec assigns it there and it was never wired. Confirm the assignment still
  holds against the current skill boundaries before wiring #626 into `quality`.
- **Does #612 survive this commit?** Its cited survived mutants are
  `print(json.dumps(...))` lines the migration deleted. Re-measure rather than
  assume stale.

## Deferred Decisions

- **#527** (per-skill human-readable docs, maturity buckets, invocation locks) —
  a product-shape change, not a defect. It does not belong in a release already
  carrying four themes.
- **#528** (a repo cannot declare a `coverage_floor_policy` sub-key absent) and
  **#546** (a budgeted label with no sample WARNs forever) — both are real
  adapter/gate-honesty defects and both are cheap, but they are the first things
  to cut if S1-S6 runs long.
- **#550** (near-identical adapter resolver bodies) and the ledger write
  transaction shared by four writers ([dup-review](../quality/dup-review.json)
  family `d3fea2dbc2463d22`) — refactors with no user-visible defect behind them.
- **#601** (CLI test-harness pathology detection in `quality`) and **#605**
  (unreachable trim-back loop, honest state UNPROVEN).

## Non-Goals

- No new host support, no Cautilus evaluation, no PR/tag/push outside S7's
  explicit grant.
- No migration shim, compatibility parser, or `--json` deprecation window. That
  decision was made and executed in `eae80f660`.
- Not closing #628/#629/#631 in this release unless S2/S4/S3 actually deliver
  them; a close asserts the behavior, not the intent.

## Deliberately Not Doing

- **Not repairing the 6.0.0 notes by hand now.** That is the move that failed
  twice. Notes come last, derived, in S7.
- **Not shipping the release before S6.** The owner chose wide scope with the
  stranded-fix cost stated and accepted.
- **Not adding a second per-family date-coherence check for `debug`.** That
  repeats #620's scoping error one family over.

## Constraints

- `mutate -> sync -> verify -> publish`. Every slice touching exported source
  runs `sync_root_plugin_manifests.py` before validators and stages the mirror.
- Verification claims use cache-free commands. Measured today: `ruff check .` was
  green while `ruff check --no-cache .` reported 180 `I001` — a false green that
  reached a checked-in retro as "Ruff clean".
- The full suite costs **~22 minutes** (9331 tests). Budget it per slice; do not
  claim a green that predates the edit being claimed.
- Slices touching verdict logic on a proof surface owe the two-round bounded
  review. S1 (#608), S2, S3 (#631 continuity logic), S4 (the docs-graph
  assertion), and S5 are all proof surfaces.
- Bounded reviewers run read-only in the shared worktree and never run
  index- or worktree-mutating git ops.
- Push, tag, version bump, and publish each require an explicit phase-scoped
  grant at S7. A green gate is not one.

## Success Criteria

1. The published 6.0.0 notes contain no claim contradicted by the shipped tree,
   and a gate — not a reviewer — is what establishes that.
2. `publish_release.py` can stop between release-record creation and
   tag/push/publish, and the claims review happens in that gap.
3. `debug`'s scaffold cannot target an unrelated open investigation, and the
   guard that establishes this covers every scaffold family rather than two.
4. A session that reads a lesson which then works can record that outcome
   without declaring a recurrence, and a session scoring lessons from two origin
   retros can satisfy `check_lesson_evaluation_continuity.py`.
5. The archive/resurrection/graduation slot has a production caller.
6. `check_docs_graph.py` fails when `link_only_lines` exceeds the declared bar,
   and this repo is at or under that bar.
7. A write-capable subagent cannot run a worktree-mutating git op, enforced
   rather than documented.
8. #618-#627 are `CLOSED` per `verify-closeout --expect-state CLOSED`, each with
   a `Behavior #N:` verdict on a channel distinct from its fix.

## Acceptance Checks

- Verification type: unit — the notes generator, given a tree with a flag/probe
  surface the notes do not mention, produces a diff; given the shipped tree,
  produces none.
- Verification type: integration — the notes gate fails a publish plan whose
  notes disagree with the tree, and the failure names the disagreeing surface.
- Verification type: integration — `publish_release.py` with the pause requested
  writes the release record and stops before tag/push, and the resumed run
  publishes without redoing the bump.
- Verification type: unit — every scaffold family refuses a `write_artifact_path`
  whose target is an existing artifact of a different date or an open
  investigation; the debug family is one parametrized case among them, not a
  special case.
- Verification type: unit — a lesson outcome of `worked` is recordable with no
  `recurrence-class` tag present, and the four-value vocabulary round-trips
  through the ledger.
- Verification type: integration — a session with score events citing two origin
  retros passes `check_lesson_evaluation_continuity.py`, and a genuinely foreign
  score still fails it (negative case).
- Verification type: unit — the resurrection slot draws an archived lesson from a
  ledger that has one, and reports honestly when it has none.
- Verification type: unit — `check_docs_graph.py` exits nonzero when
  `link_only_lines` exceeds the declared bar; the bar is a required value in the
  gate, not a comment (`bar-recorded-as-prose`).
- Verification type: unit — the `what-reads-this` command, given a symbol, path,
  and config key, reports every reference outside the target's own tests and the
  `plugins/charness/**` mirror, and reports zero honestly.
- Verification type: integration — a write-capable subagent attempting
  `git stash`/`checkout`/`reset` in the shared worktree is refused, with the
  refusal naming the rule.
- Verification type: manual — `verify-closeout --expect-state CLOSED` reads back
  each of #618-#627 from the provider after the publish.

## Boundary Ownership

The release helper owns bump/sync/verify/tag/publish and now the claims-review
pause. The notes generator owns derived claim surfaces; the operator owns the
narrative around them. Scaffold libraries own refusing a destructive write
target. `lesson_evaluation_continuity_lib.py` owns score-source agreement;
`quality` owns lifecycle promotion per the 2026-08-12 spec. `check_docs_graph.py`
owns the `link_only_lines` bar. The repo operating contract owns the
subagent git rule; enforcement owns proving it.

## Critique

- Interrupt Source: `lesson-presentation-compaction-2026-08-14`
- Seam Summary: lesson-session rendered output to repo-owned retro verdict
- Chosen Next Step: impl (S3, first item)
- Impl Status: allowed
- Impl Status Reason: the #617 capability shipped in `eae80f660` —
  `open_lesson_session.py:33` resolves `bundle_path`, and this session's own
  `2026-08-15-release-design` open wrote its bundle. What remains is the spec
  refresh and the debug artifact's `Resolution: open`, which is what holds
  `plan_risk_interrupt.py` at `status: blocked`.
- What Disproving Observation Is Resolved: the observation that lesson
  presentation survives only in active context is disproved by a checked-in
  bundle written by the current code path; the interrupt closes on that artifact,
  not on a claim.
- Contract critique: **not run.** The repo mandates a bounded fresh-eye review
  for a task-completing contract on a proof surface. This session's host
  prohibits subagent spawning, so no different-observer review read this
  contract. It is unproven, not approved. Rerun before S7.

Known weaknesses of this contract, stated rather than hidden:

- S5 is the least bounded slice in the release. Its probe question exists
  because "the class remains" umbrellas do not terminate on their own.
- The `link_only_lines` -> 0 target may be the wrong bar; the criterion is
  written as "at or under the declared bar" so that a measured 0 and a measured
  honest non-zero are both acceptable outcomes, and neither is silent.
- Wide scope means the eight stranded fixes stay stranded for the length of
  S1-S6. That cost was stated to the owner and accepted.

## Canonical Artifact

This file is the living contract for the 6.0.0 release scope. Per-issue
contracts stay in their own artifacts — the
[#617 durable lesson-session bundle](./2026-08-14-issue-617-durable-lesson-session-bundle.md)
and the [lesson score outcome vocabulary](./2026-08-14-lesson-score-outcome-vocabulary.md)
are canonical for their slices and are referenced, not restated, here.

## First Implementation Slice

S1: build the `what-reads-this` command (#599) and prove it on the three input
kinds, because every later slice in this release either deletes or rewires
something. Then #608's pause seam, `--no-cache` on the ruff verification path,
and #630. Commit, then S2.
