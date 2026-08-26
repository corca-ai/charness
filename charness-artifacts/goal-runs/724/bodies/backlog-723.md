<!-- charness-work-item-key: backlog-723 -->
# Existing Work Item #723 — Quality planning ownership

## Purpose and premise

Make quality planning discover adapter-declared skill paths and name one
package-verification owner. Re-read the current adapter and planner before
editing; this is a bounded consumer-scope contract, not an umbrella cleanup.

## Owned change and acceptance

Pin the Ceal-shaped adapter fixture, exact planner output, first catalog/quality
consumer, and advisory-only boundary. The result must expose the selected paths,
owner, and advisory disposition deterministically and refuse an unstructured
existence-only claim.

## Verification and evidence boundary

Run `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_quality_run_planner.py`, then changed-line proof. This child claims only local source behavior; installed, hosted, release, and issue-closure behavior need separate proof.

## 2026-08-27 addendum — route planner scope through the declared owner

The follow-up comment was re-read before implementation. It supplies a concrete
Ceal-shaped failure: `packages/official-skills/ceal-native/skills` contains
checked-in `SKILL.md` files and the direct inventory can scan them, while the
planner's hard-coded roots previously reported `skills_in_scope: false` and an
unreachable declared surface. The comment also names the adjacent catalog
equivalent-owner and heuristic-disposition concerns; those broader umbrella
changes remain explicitly excluded from this bounded child by the readiness
contract and are retained as goal follow-up rather than silently claimed here.

The ownership cutover is now at the actual producer boundary:

- `quality_skill_scope.py` resolves adapter-declared skill roots into concrete
  `SKILL.md` paths, and `quality_declaration_lifecycle.py` keeps that result as
  the source of truth. A declared directory accepts its root `SKILL.md` and
  one-level package children; repo-relative and configured external-support
  paths stay canonical and deterministic.
- `plan_quality_run.py::build_plan` is the first quality consumer and the
  package-verification owner for the selection decision. It derives
  `skills_in_scope`, `sample_skill_paths`, target resolution, and the structural
  review packet from the lifecycle's selected list rather than rediscovering a
  different tree. The source and plugin copies are byte-identical.
- The structural packet's `quality_move_card` remains advisory: its default
  enforcement posture is `advisory-or-no-gate`, so heuristic inventory hits do
  not become action-required repairs, fake mirrors, fake commands, or receipts.
  The planner remains a plan and does not execute a package verification command.
- If an explicit declaration resolves no readable `SKILL.md`, the lifecycle
  records `target_state: unreachable`, leaves the selected skill list empty,
  and the planner says `adapter-declared skill paths resolved to no SKILL.md
  files`; path existence alone is not converted into scope or ownership.

## Executed verification

- The issue-specified target alone reports `39 passed`.
- The combined planner, adapter-scope, and declaration-path target reports
  `69 passed`.
- The Ceal-shaped fixture proves the selected path is in scope, the lifecycle
  source is `adapter-declared`, the declared row is `resolved`, and the
  structural packet is required. The refusal and adjacent-loader failure paths
  are also asserted.
- Isolated proof commit `b116e9f3e` ran the target pre-commit checks and a clean
  changed-line proof against base `3f16d6b42`: all 3 changed mutation-pool files
  (`plan_quality_run.py`, `quality_declaration_lifecycle.py`, and
  `quality_skill_scope.py`) were analyzed, `consumer_returncode: 0`,
  `blocking: []`, and `unmapped_changed_pool_files: []`. The proof worktree was
  clean after the run.

## Boundary and non-claims

This is local deterministic quality-planner behavior only. It does not claim
that the consumer's package scripts were executed, that catalog-equivalent
owners were adopted, that heuristic findings were dispositioned in the
consumer, or that installed, hosted, release, tag, push, or issue-closure
behavior changed. The user-authorized implementation path omits forced
fresh-eye, handoff, and micro-slice rituals; no such evidence is claimed.
Issue `#723` remains open.
