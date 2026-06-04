# Achieve Goal: Nose duplicate refactoring

Status: draft
Created: 2026-06-04
Activation: `/goal @charness-artifacts/goals/2026-06-04-nose-duplicate-refactoring.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: before activation.
- Next action: activate with `/goal @charness-artifacts/goals/2026-06-04-nose-duplicate-refactoring.md`.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Use `nose 0.4.0` to drive a real code-duplicate refactoring pass in Charness
before deciding whether `jscpd` still adds useful hard-gate signal.

The desired end state is:

- `check_duplicates.py` is retained through the `nose` cleanup and narrowed to
  the Markdown/skill/reference whole-file near-copy guard only after the
  coverage tradeoff is explicit.
- Existing high-value Python duplicate families reported by `nose` are reduced
  through shared helpers or clearer entrypoint contracts.
- `nose` is treated as a support binary candidate for advisory `quality`
  refactoring inventory, with install/update/doctor work planned before relying
  on it outside maintainer-local checkouts.
- `jscpd` is not added during this goal. It is reassessed only after the
  `nose`-driven cleanup changes the baseline.

## Non-Goals

- Do not add `jscpd` as a hard gate or support binary in this goal.
- Do not replace the Markdown near-copy behavior with a token/block detector.
- Do not hide test intent or behavior assertions in helpers only to reduce a
  duplicate score.
- Do not claim arbitrary-machine `nose` support until the tool manifest,
  dependency staging, update, and doctor path are actually implemented.
- Do not perform release or publish work unless the implementation touches a
  release surface unexpectedly.

## Boundaries

- Work in the dedicated worktree
  `/home/hwidong/codes/charness-duplicate-detection`.
- The sibling `/home/hwidong/codes/nose` checkout is allowed only as a
  maintainer-local analysis source until Charness owns a `nose` support-binary
  manifest.
- Prefer production/helper extraction that preserves portable plugin execution;
  plugin/export independence must be proven by existing validators or focused
  tests before removing bootstrap duplication.
- Treat bootstrap and adapter duplicate families as accepted debt only until a
  slice proves a shared path can remove them without breaking source-tree or
  installed-plugin execution.
- Keep generated/plugin surfaces synced before validation when touched.

## User Acceptance

The user can verify completion by inspecting:

- the final `nose 0.4.0` report summary recorded in this artifact
- focused diffs showing removed or consolidated bootstrap/adapter duplicate
  families
- passing focused tests for source-tree and plugin-like execution paths
- a final statement that either `jscpd` still has meaningful post-cleanup signal
  or is deferred with evidence

## Agent Verification Plan

### Low-Cost Checks

- Resolved maintainer-local `NOSE_BIN` or
  `/home/hwidong/codes/nose/target/release/nose --version` reports
  `nose 0.4.0`; plain `nose --version` is reserved for the future support
  manifest/install path.
- Focused `nose scan` commands are run before and after each refactoring slice
  against the touched scope.
- Targeted pytest is run for each extracted helper or entrypoint family.
- Markdown/doc checks are run for changed docs and goal artifacts.
- `scripts/check_duplicates.py` remains green for the Markdown/reference scope
  it is intended to protect.

### High-Confidence Checks

- `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest`
  after meaningful multi-file refactoring slices.
- `./scripts/run-quality.sh --read-only` or the documented focused substitute at
  final closeout, depending on the changed surface and cost.
- Fresh-eye critique for substantial bootstrap, adapter, validator, or gate
  design changes.

### External Or Live Proof

- No external live proof is planned.
- Arbitrary-machine `nose` install/update proof is explicitly out of scope until
  a Charness support-binary manifest slice is accepted.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Lock baseline and scope | Avoid optimizing against stale `nose 0.2.0` or raw `jscpd` output | `nose 0.4.0` version, top-family inventory, docs updated to defer `jscpd` | pending |
| 2 | Remove portable bootstrap duplication where a shared path is provably safe | Largest `nose` family is skill runtime bootstrap across public skill scripts | shared helper or generator path, source/plugin execution tests, reduced `nose` family | pending |
| 3 | Consolidate adapter resolver/validator skeletons | Adapter families are the next largest actionable duplication | common adapter validation helpers or templates, focused resolver tests, reduced `nose` family | pending |
| 4 | Preserve or narrow `check_duplicates.py` to document near-copy ownership | Do this only after code-clone cleanup clarifies what Python near-file coverage would be lost | tests proving Markdown near-copy behavior; explicit non-claim or retained coverage for helper-script near-file checks | pending |
| 5 | Reassess post-cleanup `jscpd` signal | Only after actual cleanup can raw token clone signal be judged fairly | before/after `jscpd` summary, recommendation to defer/add wrapper/skip | pending |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`.

Gather: n/a — no external URL or source asset was used to shape this goal.
Release: n/a — no release surface is planned.
Issue closeout: n/a — no tracked GitHub issue is being closed by this goal as
shaped.
Discuss before activation: resolved in transcript on 2026-06-04. The user
changed the plan to defer `jscpd`, keep document near-copy detection, update
`nose` to 0.4.0, and run refactoring before reassessing `jscpd`.

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- User decision in this session: defer `jscpd`; keep document near-copy
  detection; use `nose 0.4.0` to complete refactoring first.
- [`docs/duplicate-detection-strategy.md`](../../docs/duplicate-detection-strategy.md)
- [`docs/conventions/implementation-discipline.md`](../../docs/conventions/implementation-discipline.md)
- [`docs/conventions/operating-contract.md`](../../docs/conventions/operating-contract.md)
- [`charness-artifacts/retro/recent-lessons.md`](../retro/recent-lessons.md)
- Maintainer-local `nose` checkout at `/home/hwidong/codes/nose`, updated to
  `nose 0.4.0` before shaping this artifact.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Detection architecture: considered immediate `jscpd` hard gate, `jscpd`
  baseline/no-increase wrapper, or no `jscpd` until cleanup. Chosen: no `jscpd`
  during this goal. Rejected alternatives because current raw token findings
  are dominated by bootstrap/adapter debt and would make a noisy gate.
- Markdown duplicate guard: considered replacing `check_duplicates.py` with a
  token detector, keeping it broad, or narrowing it to document near-copy.
  Chosen: keep/narrow it for Markdown, skill, reference, and README
  near-similarity. Rejected alternatives because whole-file near-copy is the
  user-intended behavior and `jscpd`/`nose` do not replace it cleanly.
- Refactoring driver: considered `jscpd`, old `nose 0.2.0`, and updated
  `nose 0.4.0`. Chosen: `nose 0.4.0` advisory inventory. Rejected alternatives
  because `nose 0.4.0` has newer clone-family reporting and is better aligned
  with refactoring decisions than raw pair output.
- Portability axis: `nose` use is maintainer-local for analysis until a support
  binary manifest exists. This is an environment/tool-distribution axis, not a
  global assumption about arbitrary machines.
- Activation mode: implementation-continuation goal once explicitly activated
  with `/goal`; this Before-phase only shapes and saves the artifact.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Folded blocker: `nose` must not remain a sibling-checkout assumption for
  consumer repos. The goal allows sibling `nose` only for maintainer-local
  analysis and keeps support-binary manifest work explicit.
- Folded blocker: removing bootstrap duplication can break plugin/source-tree
  independent execution. Slices must prove both execution paths before removing
  copied bootstrap code.
- Folded blocker: `jscpd` raw findings can become a noisy gate. It is deferred
  until after `nose` cleanup and then reassessed from evidence.
- Folded blocker from medium fresh-eye review: the first draft put
  `check_duplicates.py` narrowing before `nose` refactoring and overstated the
  current checker as document-only. The slice plan now performs `nose` cleanup
  first and records the current helper-script scope as a coverage tradeoff.
- Folded blocker from medium counterweight review: `nose --version` is not a
  valid arbitrary-machine check yet. The plan now uses the maintainer-local
  resolved binary until support-manifest/install work exists.
- Over-worry not folded: achieving zero code clones is not required. The goal is
  to remove high-value actionable families and leave justified non-claims.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

N/A — none yet.

## Final Verification

Pending activation and execution.

## User Verification Instructions

After activation and completion, review the final verification section, run the
listed focused tests if desired, and compare the before/after `nose 0.4.0`
summary for the cleaned families.

## Auto-Retro

Pending completion.
