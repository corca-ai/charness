# Achieve Goal: Finish inventory_* conversions, leverage nose 0.5, and release

Status: complete
Created: 2026-06-05
Activation: `/goal @charness-artifacts/goals/2026-06-05-inventory-conversions-nose-05-and-release.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: COMPLETE — all four slices done. nose 0.5 (Slice 1), 5
  inventory_* conversions (Slice 2), and the full 0.21.0 publish (Slice 3,
  tag + GitHub release) all landed; closeout (Slice 4) done: 3 fresh-eye
  critiques SHIP, retro persisted, #305 filed, dispositions bound.
- Next action: none — goal met. Residual: real-host proof owed (dev-machine
  only); follow-up #305 (publish-flow resilience) filed.
- Timebox: 3h
- Closeout reserve: 30m
- Done-early policy: continue_next_improvement
- Activation time: 2026-06-05T06:00:00+00:00
- Routing: Slices 1–2 routed via `find-skills` local-first inventory → `achieve`
  operator + `quality` (clone-family inventory + boundary-bypass ratchet) +
  bounded fresh-eye `critique` subagents. Slice 3 release → `release` +
  `announcement`.
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
| 1 | nose 0.5 integration: bump `version_expectation`, adapt inventory to 0.5 `--mode` semantics, refresh nose-baseline from a live 0.5 scan | fresh capability the user just upgraded; isolated from the conversions | manifest + inventory edits; live nose 0.5 scan output; refreshed nose-baseline; gate green | done (commit 7bd7d1ee; nose 0.5.0 live, 20 families; gate 71/0) |
| 2 | Convert the 5 import-safe `inventory_*` boundary-bypass tests to in-process; regen baseline per conversion | continues the prior goal; bounded, two documented patterns | converted tests green; boundary-bypass `candidate_count` drop recorded; ratchet green | done (candidate 94→90, keys 157→152, convertible 55→51; ratchet OK; gate 71/0) |
| 3 | Release: version bump `0.20.0 → 0.21.0` + manifests + announcement + push | bundle close; user-requested ship | release commit; packaging validators green; pushed to `origin` | done (full publish: origin/main + tag v0.21.0 + GitHub release; packaging validators green; user chose full publish) |
| 4 | Verify, per-slice fresh-eye critique, retro, goal closeout | closeout | full gate; per-slice critiques; retro; goal check | done (3 fresh-eye critiques SHIP; retro persisted; #305 filed; goal check passing) |

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

### Closeout evidence

- Routing: `find-skills` local-first inventory routed the impl and quality phase work (nose 0.5 inventory fix + 5 inventory_* conversions + boundary-bypass ratchet) under the `achieve` operator, with bounded `critique` subagents per slice and `release`/`announcement`/`retro`/`issue` at closeout.
- Routing detail: `find-skills` (no adapter; in-repo discovery) → `achieve` goal
  operator; Slices 1–2 quality work → `quality`; each slice → fresh-eye
  `critique`; Slice 3 → `release` + `announcement`; closeout → `retro` + `issue`
  (#305).
- **Gather:** n/a — `## Context Sources` are all in-repo artifacts/docs; no
  external URL/Slack/Notion/Docs/Drive source applied.
- **Release:** full publish verified —
  `https://github.com/corca-ai/charness/releases/tag/v0.21.0` (tag `v0.21.0`,
  `origin/main` at the release commit, `gh release view` confirms published).
  Record: [charness-artifacts/release/latest.md](../release/latest.md);
  critique: [charness-artifacts/critique/2026-06-05-v0-21-0-release.md](../critique/2026-06-05-v0-21-0-release.md).
  Real-host proof remains owed (dev-machine only) — recorded, not claimed.
- **Issue closeout:** n/a — this goal resolved no tracked GitHub issue; it filed
  follow-up #305 (publish-flow resilience) from the retro, which is a new
  finding, not a closeout.

## Slice Log

_Empty until `/goal` activation._

### Slice 1: Slice 1 — nose 0.5 integration

- Objective: Bump nose version expectation to prefer 0.5, adapt the quality clone-family inventory to nose 0.5 (mode-replace + new JSON object schema), and refresh the nose-baseline from a live 0.5 scan.
- Why this approach: nose 0.5's --format json changed from a top-level array (0.4) to a top-level object with a families key + tool_version. The inventory read the object as a list and silently reported 0 families. Parse both shapes (backward-compatible), thread tool_version, keep the inventory advisory.
- Commits: feat(quality): adapt nose clone inventory to nose 0.5 + refresh baseline (this slice)
- What changed: skills/public/quality/scripts/inventory_nose_clones.py (+ plugin mirror): new _extract_families helper handles 0.5 object and 0.4 array; tool_version threaded into payload + human label; DEFAULT_MODE comment documents 0.5 mode-replace (syntax,semantic,near is a superset of the 0.5 default). integrations/tools/nose.json (+ mirror): version_expectation constraint 0.4.0 -> 0.5.0. charness-artifacts/goals/2026-06-04-nose-duplicate-refactoring-nose-baseline.json: refreshed from live 0.5 scan (raw output, tool_version 0.5.0, 236 families vs prior 230). tests/quality_gates/test_quality_nose_advisory.py: added test_nose_advisory_parses_v05_object_schema; kept the 0.4-array test.
- Alternatives rejected: Slicing baseline to just .families (a hand-edit/transform of canonical output) — rejected for raw canonical 0.5 output that self-certifies tool_version. Promoting nose findings to a hard gate — explicitly out of scope (scope B).
- Targeted verification: 3 focused tests pass (missing/0.4-array/0.5-object); py_compile + ruff clean; ./scripts/run-quality.sh --read-only = 71 passed / 0 failed; live inventory prints 'nose clone advisory (nose 0.5.0): findings; 20 families'; plugin mirror byte-identical to canonical.
- Test duplication pressure: Added one 0.5-schema regression test mirroring the existing 0.4 test shape; no broad new duplication — the two tests intentionally share structure to contrast the two nose JSON schemas.
- Critique: Bounded fresh-eye subagent review (general-purpose): SHIP, no blockers. 14-shape adversarial sweep of _extract_families confirmed it never raises and always degrades to advisory; mirror byte-identical; baseline has no code consumer (array->object shape change safe); family count rose 230->236 (not masked). One cosmetic non-blocker (timeout path missing tool_version) applied.
- Off-goal findings:
- Lessons carried forward: nose 0.5 mode-replace semantics: list every wanted channel explicitly. Tool JSON schema changes are a silent under-report risk for parsers expecting the old top-level shape; a regression test on the exact new schema is the durable guard.
- Metrics:

### Slice 2: Slice 2 — convert 5 inventory_* boundary-bypass tests

- Objective: Convert the 5 remaining import-safe inventory_* boundary-bypass tests from subprocess spawns to in-process calls; regenerate the boundary-bypass baseline canonically to record the real drop.
- Why this approach: The captured-main() pattern (load entrypoint by file, patch sys.argv, capture stdout/stderr, treat main()'s return as exit code) preserves the exact CLI surface (flags, exit codes, adapter-wrapped JSON) the subprocess tests asserted on — faithful for the several tests that assert exit codes and stderr. Two scripts lacked the sibling-lib __file__ sys.path bootstrap their peers had, so they got it (raising real in-process testability, goal A) rather than a test-side path hack.
- Commits: test(quality): convert 5 inventory_* gate tests to in-process (this slice)
- What changed: TEST conversions (run_script -> in-process _run): test_quality_brittle_source_guards (6), _cli_side_effect_probes (8), _public_spec_quality (15), _skill_ergonomics (21); test_quality_bootstrap (2 adapter_gate_design sites -> _run_adapter_gate_design, OTHER spawns kept at boundary). PRODUCTION testability: inventory_public_spec_quality.py + inventory_cli_side_effect_probes.py (+ mirrors) gained the __file__ sys.path bootstrap (+ noqa E402) their siblings already carried. BASELINE: scripts/boundary-bypass-baseline.json (+ mirror) regenerated canonically: candidate 94->90, keys 157->152, convertible 55->51 (internal 38, keep 23 unchanged); exactly 5 keys removed, 0 added, no exemption change. DOC: docs/testability-dsl-initiative.md Remaining item 1 marked done.
- Alternatives rejected: Test-side sys.path hack to import siblings — rejected (commit a7449e8a removed test path-bootstraps; production bootstrap is the parity fix and raises real testability). Direct inventory() lib calls — rejected for the captured-main() pattern because several tests assert exit codes / main()-wrapped fields. Adding exemptions to fake the drop — explicitly a non-goal.
- Targeted verification: 57 focused converted tests pass in-process; ./scripts/run-quality.sh --read-only 71 passed / 0 failed (broad pytest, ratchet OK 90/51/38/23, test-completeness, test-production-ratio, doc-links, markdown); baseline diff minimal (5 keys + 3 numbers); plugin mirrors byte-identical; subprocess gate path still runs.
- Test duplication pressure: No new tests added; existing tests converted in place (call mechanism only, assertions byte-preserved). Net test count unchanged; duplication unchanged — the per-file ~25-line in-process loader mirrors the two documented reference loaders (intentional, matches the established pattern).
- Critique: Bounded fresh-eye subagent review (general-purpose): SHIP, no blockers. Verified all 6 invariants: byte-level assertion preservation (spot-checked public_spec 15 sites vs HEAD), exactly 5 keys removed (bootstrap's other 3 kept), exemptions unchanged, canonical regen matches committed baseline byte-for-byte, subprocess path + mirrors intact, internally-spawning tests untouched. Cleared a 91-vs-90 scare (pre-existing export_plugin exemption, ratchet ok:true). Independently ran tests/quality_gates: 1428 passed.
- Off-goal findings:
- Lessons carried forward: A script is 'import-safe' to the boundary probe (has main()+__main__) yet still not cleanly in-process loadable if it bare-imports siblings without a __file__ sys.path bootstrap; converting its test surfaces that gap, and the fix belongs in the production script (parity with peers), not a test path-hack.
- Metrics:

### Slice 3: Slice 3 — release 0.21.0 (full publish)

- Objective: Bump charness 0.20.0 -> 0.21.0, regenerate install manifests, draft the announcement, and full-publish (push origin/main + tag v0.21.0 + GitHub release) per the user's explicit choice.
- Why this approach: User chose full publish (tag + GitHub release) over branch-push-only when asked, matching the repo's prior v0.20.0 release pattern. Minor bump is the lightest honest level (additive nose 0.5 capability + raised testability; no compatibility break).
- Commits: b9d2b342 (bump + announcement + critique), 17110205 (Release charness 0.21.0: latest.md + auto-retro), ac3f7f8a (verified-release finalize)
- What changed: packaging/charness.json + .claude-plugin/marketplace.json + plugins/charness/.claude-plugin/plugin.json + .codex-plugin/plugin.json -> 0.21.0 (bump_version.py + sync). charness-artifacts/announcement/latest.md (draft, delivery_kind none). charness-artifacts/critique/2026-06-05-v0-21-0-release.md (release critique). charness-artifacts/release/latest.md (verified record). Helper-generated auto-retro + lesson index in 17110205.
- Alternatives rejected: Branch-push-only and stop-before-push were offered to the user; user chose full publish. publish_release.py from the installed plugin cache fails its runtime bootstrap (cannot resolve skills.public); the repo-root copy works.
- Targeted verification: current_release.py drift []; validate_packaging + validate_packaging_install_surface pass; bounded fresh-eye release critique SHIP (no blockers, announcement accurate, minor bump justified). Helper --release gate passed; push landed clean (pre-push gate 71/0) after one #194 usage-episodes flake; gh release view confirms published v0.21.0; origin/main fully synced (0 ahead).
- Test duplication pressure: n/a — release slice adds no tests.
- Critique: Bounded fresh-eye subagent (general-purpose): SHIP 0.21.0, no blockers. Verified minor-bump honesty, zero version drift, packaging green, announcement accuracy (flagged the ratchet figure as conservatively under-claimed, confirmed live nose scan = 20 families), release readiness. Artifact: charness-artifacts/critique/2026-06-05-v0-21-0-release.md.
- Off-goal findings: Adapter .agents/release-adapter.yaml update_instructions still describe 0.20.0, so the helper-generated latest.md inherited stale User Update Steps (hand-corrected for this release). A proper adapter update_instructions refresh for 0.21.0 is deferred (separate hygiene task). Also: installed-cache publish_release.py runtime-bootstrap failure (skills.public unresolved) is a portability gap worth a follow-up.
- Lessons carried forward: publish_release.py must be run from the repo-root copy, not the installed plugin cache (cache can't resolve skills.public). The full --release/pre-push gate flakes on the #194 usage-episodes race (live gitignored tree written during the parallel gate); it passes on retry and the test passes in isolation — not a release blocker. Release: full publish (push + tag v0.21.0 + GitHub release) verified at https://github.com/corca-ai/charness/releases/tag/v0.21.0; real-host proof remains owed (dev-machine only).
- Metrics:

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

- **Publish-flow resilience (→ issue #305):** `publish_release.py` is not
  resumable across a mid-publish failure (it commits+tags before the pre-push
  gate can fail, leaving a partial state); it cannot run from the installed
  plugin cache (`ModuleNotFoundError: skills.public`); and the adapter
  `update_instructions` go stale undetected (focused preflight only fires when
  the adapter file changes). Filed as a single consolidated issue.
- **#194 usage-episodes gate flake (already tracked):** the parallel full gate
  intermittently fails `test_session_capture_cli_install_and_uninstall_round_trip`
  because a gate phase appends to the gitignored live `usage_episode.jsonl` while
  that test asserts the tree immutable. Passes in isolation; referenced from
  #305, not re-filed.

## Final Verification

- No safe next slice: all four planned slices (nose 0.5, the five inventory_*
  conversions, the full 0.21.0 publish, and closeout) are complete and verified;
  the release was the terminal deliverable, so there is no remaining in-scope
  slice. The done-early policy's "next improvement" (publish-flow resilience) was
  surfaced by the retro and routed to follow-up #305 — new-goal scope, not an
  in-bundle slice. Closing inside the timebox reserve because the bundled scope
  is genuinely exhausted, not to avoid remaining work.
Early close rationale: all four planned slices (nose 0.5, the five inventory_* conversions, the full 0.21.0 publish, and closeout) completed and verified within the timebox; the release was the terminal deliverable so no in-scope slice remains, and the surfaced follow-up (publish-flow resilience) is out-of-scope, separately tracked as #305.

Retro: charness-artifacts/retro/2026-06-05-inventory-conversions-nose-05-and-release.md

Host log probe: skipped: host-log-not-exposed: no host session-log surface is configured for this repo/run, so there is no transcript to probe; closeout proof is the committed deterministic gate evidence, the live nose 0.5 scan, and the verified GitHub release below.

Disposition review: charness-artifacts/critique/2026-06-05-disposition-review-inventory-conversions-nose-05-and-release.md

Early close report: charness-artifacts/goals/2026-06-05-inventory-conversions-nose-05-and-release-early-close-report.md

- **nose 0.5 (Slice 1):** `nose --version` → `0.5.0`; `integrations/tools/nose.json`
  prefers nose 0.5.0+. The `inventory-nose-clones` gate runs under 0.5
  (`nose clone advisory (nose 0.5.0): findings; 20 families`), not advisory-skip;
  the nose-baseline was refreshed from a live 0.5 scan (`tool_version: 0.5.0`,
  236 families). A regression test pins the 0.5 object schema. Bounded fresh-eye
  critique: SHIP.
- **inventory_\* conversions (Slice 2):** the five named tests are in-process;
  the boundary-bypass `candidate_count` dropped 94→90 and `candidate_key_count`
  157→152 (exactly the 5 converted keys, `convertible` 55→51) by real
  conversion, not exemption (`scripts/boundary-bypass-exemptions.txt` unchanged);
  `check-boundary-bypass-ratchet` OK. `./scripts/run-quality.sh --read-only` =
  71 passed / 0 failed. Bounded fresh-eye critique: SHIP (byte-level assertion
  preservation + canonical baseline regen verified).
- **release (Slice 3):** `plugins/charness` at `0.21.0` with regenerated
  manifests (no drift); packaging validators pass. Full publish verified:
  `origin/main` at the release commit, tag `v0.21.0` pushed, GitHub release
  published — `https://github.com/corca-ai/charness/releases/tag/v0.21.0`
  (`gh release view`: draft false, prerelease false). Bounded fresh-eye release
  critique: SHIP.
- **Proof levels run:** focused pytest + ruff/py_compile; full read-only gate
  (71/0) at both code-slice boundaries; the helper `--release` gate; live nose
  0.5 scan; packaging validators; `gh release view` (live GitHub verification).
- **Non-claims / residual risk:** Real-host proof (second-machine / clean
  temp-home install smoke) is **owed, not run** — I worked on the dev machine;
  the checklist is recorded in `charness-artifacts/release/latest.md`. No
  Cautilus run (not requested). The publish needed manual recovery after the
  #194 pre-push flake (the test passes in isolation; the authoritative
  `--release` gate had already passed); no quality gate was bypassed.

## User Verification Instructions

- `nose --version` → `0.5.0`; run `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json`
  and confirm `tool_version: "0.5.0"` and a non-zero `family_count` (advisory).
- `python3 scripts/check_boundary_bypass_ratchet.py` → OK at 90/51/38/23; the
  five `test_quality_{brittle_source_guards,cli_side_effect_probes,public_spec_quality,skill_ergonomics}.py`
  and `test_quality_bootstrap.py::*adapter_gate_design*` tests pass in-process
  (`python3 -m pytest tests/quality_gates/test_quality_skill_ergonomics.py -q`).
- `git log origin/main -1` shows the release; `gh release view v0.21.0` shows the
  published release; `https://github.com/corca-ai/charness/releases/tag/v0.21.0`.
- `charness update` pulls 0.21.0 (operator steps in `charness-artifacts/release/latest.md`).

## Auto-Retro

Session retro persisted: `charness-artifacts/retro/2026-06-05-inventory-conversions-nose-05-and-release.md`
(recent-lessons + lesson-selection-index refreshed). Substantive findings:

- **Waste:** the publish flaked mid-way (#194 pre-push race) and left a partial
  state the non-resumable helper could not continue, forcing hand recovery; the
  installed-cache `publish_release.py` bootstrap failure cost one dead-end
  attempt; two inventory scripts hid a sibling-import testability gap until
  conversion exercised them.
- **Critical decisions:** diagnosed nose "0 families" as a 0.5 JSON-schema parse
  bug (not a clean scan) before refreshing the baseline; asked the user about the
  publish boundary instead of defaulting; fixed the sibling-import gap in the
  production scripts (not a test path-hack), honoring `a7449e8a`.
- **Expert counterfactuals:** Gary Klein (pre-mortem) — a "what blocks the push?"
  pre-mortem would have surfaced the flaky pre-push gate before the irreversible
  publish. Michael Feathers — "has main()+__main__" is a weak import-safe proxy;
  a cheap in-process import-smoke would flag the sibling-bootstrap gap earlier.
- **Sibling search:** external-tool top-level JSON-schema-change → silent-zero
  parser pattern; the nose inventory was the only unguarded external-schema
  parser (ratchet/boundary libs parse versioned, drift-checked repo payloads).

Dispositions (each surfaced improvement applied or filed):
- Pre-flight the flaky/expensive pre-push gate before an irreversible publish →
  **issue #305**.
- `publish_release.py` installed-cache bootstrap failure → **issue #305**.
- Adapter `update_instructions` staleness — immediate refresh to 0.21.0 →
  **applied** (`.agents/release-adapter.yaml`); systemic detection gap →
  **issue #305**.
- nose 0.5 schema-parse regression risk → **applied** (regression test
  `test_nose_advisory_parses_v05_object_schema`).
- Memory/lesson capture → **applied** (persisted retro + recent-lessons digest).

Disposition review: complete — every surfaced improvement is bound to
`applied: <commit this run>` or `issue #305`; no prose-only memory remains.
