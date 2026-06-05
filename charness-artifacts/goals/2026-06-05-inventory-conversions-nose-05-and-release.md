# Achieve Goal: Finish inventory_* conversions, leverage nose 0.5, and release

Status: draft
Created: 2026-06-05
Activation: `/goal @charness-artifacts/goals/2026-06-05-inventory-conversions-nose-05-and-release.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: before activation (shaped, inert until `/goal`).
- Next action: activate next session with the `Activation:` command above.
- Timebox: 3h
- Closeout reserve: 30m
- Done-early policy: continue_next_improvement
- Activation time: (set at `/goal` activation).
- Discuss before activation: RESOLVED with the user on 2026-06-05. (a) Release
  PUSH is in scope — the release slice pushes to `origin` (outward-facing,
  irreversible); user chose "version bump + push" over no-push and version-only.
  The push executes ONLY at the release slice after all gates are green and the
  packaging validators pass; it is not a mid-run action. (b) nose 0.5 live proof
  is feasible — `nose 0.5.0` is installed at `~/.cargo/bin` (verified 2026-06-05);
  the gate's earlier "nose missing" was a stale pre-install observation. (c) nose
  scope is bounded to "use 0.5 features + refresh baseline" (option B), NOT
  promoting clone findings to a hard gate. No other unresolved consequential
  activation discussion remains.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Continue the 2026-06-05 quality-scaffold/testability goal in three bundled items
ending in a release: (1) leverage the upgraded **nose 0.5** clone-family scanner
(bump `integrations/tools/nose.json` version expectation, adapt the quality
clone-family inventory to nose 0.5's new `--mode` semantics, and refresh the
nose-baseline with a live 0.5 scan); (2) finish the remaining import-safe
`inventory_*` boundary-bypass conversions per `docs/testability-dsl-initiative.md`
Remaining item 1 (the five named convertible tests, regenerating the baseline per
conversion); (3) cut a **release** — version bump `0.20.0 → 0.21.0`, regenerated
install manifests, announcement, and push to `origin`.

## Non-Goals

- Do not execute any slice during the Before phase or before `/goal` activation.
- Do not push to `origin` until the release slice, after all read-only and
  packaging gates are green; push is the final gated step, never mid-run.
- Do not convert the two internally-spawning `inventory_*` tests
  (`inventory_entrypoint_docs_ergonomics`, `inventory_ubiquitous_language`); the
  boundary stays for those.
- Do not promote nose clone-family findings from advisory to a hard standing gate
  in this goal (scope B = use 0.5 features, not gate promotion).
- Do not lower `scripts/boundary-bypass-baseline.json` or the nose-baseline via
  exemptions to fake progress; the boundary drop must reflect real in-process
  conversions and the nose-baseline must reflect a real 0.5 scan.
- Do not hand-edit generated baselines; regenerate them canonically and sync
  plugin mirrors before validators.

## Boundaries

- **nose 0.5**: `integrations/tools/nose.json` currently constrains
  `Prefer nose 0.4.0 or newer` — bump it to prefer 0.5. nose 0.5 changed `--mode`
  to REPLACE the default (`syntax` CPD + `exact` semantic) rather than add to it
  (`nose scan --help`), and `skills/public/quality/scripts/inventory_nose_clones.py`
  passes an explicit `--mode`, so adapt it to 0.5 semantics so the scan does not
  silently under-report. Refresh the nose-baseline
  (`charness-artifacts/goals/2026-06-04-nose-duplicate-refactoring-nose-baseline.json`)
  from a real 0.5 scan. `nose 0.5.0` is installed at `~/.cargo/bin` (verified), so
  live scan proof is feasible.
- **inventory_\* conversions**: follow `docs/testability-dsl-initiative.md`
  Remaining item 1 — convert `inventory_adapter_gate_design`,
  `_brittle_source_guards`, `_cli_side_effect_probes`, `_public_spec_quality`,
  `_skill_ergonomics`; reuse the two documented patterns from the prior goal
  (direct `inventory()` lib call; in-process `main()` with captured stdout). Some
  tests (e.g. `test_quality_bootstrap.py`) only spawn the inventory among many
  other subprocess calls — convert just the inventory call sites. Regenerate the
  boundary-bypass baseline to canonical form per conversion and sync the mirror.
- **release**: bump `plugins/charness` version `0.20.0 → 0.21.0` via the `release`
  skill, regenerate install manifests, draft the announcement, then push. Local is
  ahead of `origin/main` by ≥9 commits (this session's work included).

## User Acceptance

What the user can do to verify completion directly.

- `nose --version` → `0.5.0`; the quality clone-family inventory runs under 0.5
  (not advisory-skip) and the nose-baseline reflects a real 0.5 scan;
  `integrations/tools/nose.json` prefers 0.5.
- The five `inventory_*` tests are converted to in-process; the boundary-bypass
  `candidate_count` dropped by the converted count (not by exemption); the full
  read-only quality gate is green.
- `plugins/charness` is at `0.21.0` with regenerated manifests; the release is
  pushed and `git log origin/main` (or the remote) shows it.

## Agent Verification Plan

### Low-Cost Checks

- Focused `pytest` per converted `inventory_*` test; `ruff` / `py_compile` /
  `check_python_lengths.py` on touched scripts; `check-doc-links` /
  `check-markdown` for doc/manifest edits; `nose --version` + `nose scan --help`.

### High-Confidence Checks

- `./scripts/run-quality.sh --read-only` at slice/bundle boundaries;
  `check_boundary_bypass_ratchet.py` after conversions; a live nose 0.5
  clone-family scan; release validators (`validate-packaging`,
  `validate-packaging-committed`). Bounded fresh-eye critique per substantial
  slice; `check_goal_artifact.py` before completion.

### External Or Live Proof

- Live nose 0.5 clone scan (feasible — installed). The release **push to origin**
  is the outward/live step, gated on green gates + packaging validators. No
  Cautilus run claimed unless explicitly requested.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | nose 0.5 integration: bump `version_expectation`, adapt inventory to 0.5 `--mode` semantics, refresh nose-baseline from a live 0.5 scan | fresh capability the user just upgraded; isolated from the conversions | manifest + inventory edits; live nose 0.5 scan output; refreshed nose-baseline; gate green | pending |
| 2 | Convert the 5 import-safe `inventory_*` boundary-bypass tests to in-process; regen baseline per conversion | continues the prior goal; bounded, two documented patterns | converted tests green; boundary-bypass `candidate_count` drop recorded; ratchet green | pending |
| 3 | Release: version bump `0.20.0 → 0.21.0` + manifests + announcement + push | bundle close; user-requested ship | release commit; packaging validators green; pushed to `origin` | pending |
| 4 | Verify, per-slice fresh-eye critique, retro, goal closeout | closeout | full gate; per-slice critiques; retro; goal check | pending |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns. At completion, recorded
  implementation / debug / quality / issue work needs this `Routing:` evidence
  or a `Routing: n/a — <reason>` opt-out.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — this run touches a release surface (version bump +
  install-manifest edit + push), so a `Release:` line pointing at the release
  proof is REQUIRED at closeout.
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`.

## Slice Log

_Empty until `/goal` activation._

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- Just-completed goal:
  [quality-scaffold-and-testability-followups](2026-06-05-quality-scaffold-and-testability-followups.md)
  — the two in-process conversion patterns and the baseline-regen step.
- [docs/testability-dsl-initiative.md](../../docs/testability-dsl-initiative.md)
  Remaining item 1 — the five remaining convertible `inventory_*` tests, the skip
  list, and the per-conversion baseline-regen note.
- Prior nose goal:
  [2026-06-04-nose-duplicate-refactoring](2026-06-04-nose-duplicate-refactoring.md)
  and its `2026-06-04-nose-duplicate-refactoring-nose-baseline.json`.
- [integrations/tools/nose.json](../../integrations/tools/nose.json) (version
  expectation, scan command) and
  [inventory_nose_clones.py](../../skills/public/quality/scripts/inventory_nose_clones.py).
- [plugins/charness plugin.json](../../plugins/charness/.claude-plugin/plugin.json)
  — current version `0.20.0`.
- nose 0.5.0 is installed at `~/.cargo/bin/nose` (verified 2026-06-05); the gate's
  earlier "nose missing" was a stale pre-install observation, not a real gap.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- nose scope: chose B (bump version + use nose 0.5's new features in the
  inventory + refresh baseline). Rejected A (version-only — does not actually
  "leverage" the improvements) and C (promote clone findings to a hard gate —
  too large/risky for this bundle and a separate policy decision).
- nose install / live proof: the user asked why the gate said "nose missing"
  despite installing it. Diagnosed live: `nose 0.5.0` IS installed at
  `~/.cargo/bin`, detected, and runs; the "missing" line was a stale pre-install
  gate observation. Conclusion: live 0.5 scan proof is feasible.
- release: chose B (version bump + push). Rejected no-push (user wants it
  shipped) and version-only (manifests/notes matter for a real release). Push is
  consequential/irreversible → recorded under Discuss-before-activation.
- Execution timing: chose draft-now / execute-next-session (artifact-only now).
- Timebox: chose 3h with `continue_next_improvement` on done-early.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique. (Pre-activation
self-critique; full per-slice fresh-eye critique runs during execution.)

- nose 0.5 `--mode` behavior change: 0.5 makes `--mode` REPLACE the default
  channels instead of adding; the inventory passes an explicit `--mode`, so it
  may under-report under 0.5. Folded into Boundaries — adapt the inventory to 0.5
  semantics and verify the scan still surfaces real findings before refreshing the
  baseline. (The current 0.5 scan reports "0 families" — confirm that is genuine,
  not a mode-replacement artifact.)
- nose-baseline gaming: refreshing under 0.5 could mask clones. Folded into
  Non-Goals — the baseline must reflect a real 0.5 scan, no exemption-faking.
- Push irreversibility: pushing to `origin` is outward-facing and hard to undo.
  Folded into Non-Goals + Discuss-before-activation — push only at the release
  slice after green gates + packaging validators.
- Bundle-scope (over-worry, not folded): three somewhat-disparate items (nose,
  conversions, release) in one goal. The user explicitly chose to bundle them with
  the release last, and they share a quality-tooling/ship theme; recorded, not
  split.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

_Filled in the After phase._

## User Verification Instructions

_Filled in the After phase._

## Auto-Retro

_Filled in the After phase._
