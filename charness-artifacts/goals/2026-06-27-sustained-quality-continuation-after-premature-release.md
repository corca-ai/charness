# Achieve Goal: Sustained quality continuation after premature release

Status: active
Created: 2026-06-27
Activation: `/goal @charness-artifacts/goals/2026-06-27-sustained-quality-continuation-after-premature-release.md`

This goal continues the prior quality timebox after the `v0.56.5` release was
cut too early relative to the user's intent to keep discovering quality slices.

## Active Operating Frame

- Current slice: Release publish fake CLI fixture extraction.
- Current slice intent: continue reducing test helper prompt/template bulk by
  moving release-publish fake `git`, `gh`, and distinct-channel probe bodies
  out of `tests/quality_gates/release_publish_fixtures.py` and into fixture
  script files.
- Next action: commit and push this fixture extraction, then continue discovery
  unless a release-worthy boundary is reached.
- Verification cadence: focused deterministic checks at each small slice;
  broader proof only when code, generated surfaces, or release boundaries move.

## Goal

Continue aggressive Charness quality improvement after the prior goal was
closed early. Keep discovering and implementing additional high-leverage quality
slices across bugs, test speed, script speed, execution speed, token efficiency,
and operator/agent usability. Commit and push useful slices; decide whether a
follow-up release is warranted only after additional release-worthy changes
accumulate.

## Non-Goals

- Do not cut another release merely to compensate for the premature closeout.
- Do not weaken standing quality gates to create speed.
- Do not add a broad blocking floor for every discovered documentation drift.
- Do not run Cautilus unless the repo planner allows a named log-backed lane.

## Boundaries

- The `v0.56.5` release already exists. New changes belong to this continuation
  goal and need a separate release decision later.
- Push is in scope for completed local quality slices.
- Release is not automatic for each slice; route through `release` only if the
  final bundle changes installed/operator behavior enough to warrant it.
- Done-early policy: continue_next_improvement while cheap, local proof remains
  available.

## User Acceptance

- Review the continuation commits pushed after `v0.56.5`.
- Run focused tests or validators named in `## Final Verification`.
- Inspect the updated handoff/quality artifacts for honest non-claims.

## Agent Verification Plan

- `find-skills` recommendation confirms `quality` for the improvement route.
- Quality planner primers and report-first inventories guide slice selection.
- Focused validators cover changed docs/skill surfaces.
- `check_changed_surfaces.py` and sync checks run if generated/plugin surfaces
  are touched.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Re-enter quality discovery and repair stale reference drift | User clarified the timebox should continue; startup found a stale handoff and support-skill helper path | find-skills route, quality planner, focused validators | complete |
| 2 | Repair remaining support helper reference drift | Continue discovery beyond the first cleanup | support package scan and focused proof | complete |
| 3 | Speed up RCA ledger tests without weakening CLI assertions | Standing-test economics pointed at nested CLI fanout; this file had 44 subprocess-heavy tests | focused timing, length headroom, changed-surface validators, standing pytest | complete |
| 4 | Extract HITL report HTML template from Python | Prompt-bulk inventory identified two large HTML/CSS/JS literals in `hitl_report_mode_lib.py` | focused HITL report tests, prompt-bulk delta, packaging sync | complete |
| 5 | Extract Charness CLI fake binary scripts from support helper | Prompt-bulk inventory identified large fake `claude`/`codex` script literals in `tests/charness_cli/support.py` | focused CLI tests, prompt-bulk delta, standing pytest | complete |
| 6 | Extract remaining Charness CLI external-tool fake scripts from support helper | Prompt-bulk inventory still points at `tests/charness_cli/support.py`; the fake npm/cargo/uv bodies are local, deterministic, and expensive to keep inline | focused CLI update/tool lifecycle tests, prompt-bulk delta, standing pytest | complete |
| 7 | Extract Charness CLI Go/specdown/glow fake scripts from test helpers | Prompt-bulk inventory still points at Go installer script literals after slice 6 | focused CLI update/tool lifecycle tests, prompt-bulk delta, standing pytest | complete |
| 8 | Extract release publish fake CLI scripts from test fixture helper | Prompt-bulk inventory next surfaced large fake release CLI bodies in `release_publish_fixtures.py` | focused release publish tests, prompt-bulk delta, standing pytest | complete |
| 9 | Continue discovery/push/release decision | Avoid another premature release | next candidate ledger, final validators, commit/push, release recommendation | pending |

## Operator Decision Queue

none — no operator-only decision is currently queued; follow-up release remains
deferred until enough release-worthy changes accumulate.

## Coordination Cues

Routing: `find-skills` recommended `quality` for this continuation quality
discovery route.
Gather: n/a — no external URLs or source links were introduced as working
context for this continuation slice.
Release: n/a — this slice intentionally does not cut a release.
Issue closeout: n/a — this continuation has not claimed tracked issue closeout.

## Slice Log

- Re-entry evidence:
  - User clarified that the original three-hour goal meant continued discovery,
    not early release once one slice passed.
  - `find-skills` recommended `quality` as the public skill route.
  - `quality` planner required report-first evidence and current-primer reads.
  - Runtime summary: `run-quality-read-only` remains the main standing cost
    (`38.1s` latest, `65.7s` recent median) but within budget.
  - Handoff candidate check: `route_public_fetch.py` is no longer near-limit
    (`85/360` Python code lines), so the handoff's "split remaining near-limit
    web-fetch helper" instruction is stale.
  - Support-skill reference drift: `skills/support/web-fetch/SKILL.md` and the
    plugin mirror list `<repo-root>/scripts/route_public_fetch.py` and
    `<repo-root>/scripts/classify_fetch_response.py`, but the runnable helpers
    live under the support skill's `scripts/` directory.
  - Slice 1 repair: changed web-fetch references to
    `scripts/route_public_fetch.py`, `scripts/classify_fetch_response.py`, and
    `scripts/acquire_public_url.py`; updated `docs/handoff.md` to remove the
    stale near-limit split instruction and point #392 back to current
    gather/web-fetch behavior evidence.
  - Sync proof: `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
    refreshed `plugins/charness/support/web-fetch/SKILL.md` and marketplace
    surfaces.
  - Focused proof: `check_skill_surface_preflight.py` for web-fetch,
    `check_doc_authoring_preflight.py --path docs/handoff.md`,
    `check_references_link_inventory.py` for web-fetch, `validate_skills.py`,
    `validate_skill_ergonomics.py`, `check_skill_ownership_overlap.py`,
    `check_doc_links.py`, `check_command_docs.py`, `check-markdown.sh`,
    `check-secrets.sh`, `validate_packaging.py`,
    `validate_packaging_committed.py`, `validate_cautilus_proof.py`, and
    `validate_cautilus_diagnostics.py` passed.
- Slice 2 evidence:
  - Follow-up scan found the same support-helper reference drift in
    `gather-notion`, `gather-slack`, and `markdown-preview`: their `## References`
    sections pointed at `<repo-root>/scripts/...` helpers while the shipped
    helpers live inside each support skill package.
  - Repaired root support skill references and provenance references to use
    package-local `scripts/...` paths, then synced plugin mirrors.
  - Drift check: `rg -n '<repo-root>/scripts/' skills/support
    plugins/charness/support` returned no matches after the repair.
  - Focused proof: `check_references_link_inventory.py` over support
    `SKILL.md`/references, `validate_skills.py`, `validate_skill_ergonomics.py`,
    `check_doc_links.py`, `check_command_docs.py`, `check-markdown.sh`,
    `check-secrets.sh`, `validate_packaging.py`,
    `validate_packaging_committed.py`, `validate_cautilus_proof.py`,
    `validate_cautilus_diagnostics.py`, `check_skill_ownership_overlap.py`, and
    support helper `py_compile` passed.
- Slice 3 evidence:
  - `inventory_standing_test_economics.py --repo-root . --json` kept nested CLI
    fanout visible: 346 Python test files, 146 nested CLI files, and 145
    standing/mixed nested CLI files. This slice chose one contained speed target
    instead of moving or weakening standing coverage.
  - Baseline focused timing: `pytest -q tests/test_rca_ledger.py` reported
    `44 passed in 3.96s`.
  - Changed `tests/test_rca_ledger.py` to reuse script `main(argv)` entrypoints
    through `tests/rca_ledger_helpers.py`, preserving subprocess-like
    `CompletedProcess` returncode/stdout/stderr assertions and retaining a
    real subprocess fallback for unknown scripts.
  - Post-change focused timing: `pytest -q tests/test_rca_ledger.py` reported
    `44 passed in 0.61s` to `0.64s`.
  - Length proof after helper extraction:
    `tests/test_rca_ledger.py` is `665/800` code lines (`135` left) and
    `tests/rca_ledger_helpers.py` is `73/800` code lines (`727` left).
  - Focused proof: `py_compile` for both test files, `ruff check`,
    `check_python_lengths.py --require-git-file-listing`,
    `validate_attention_state_visibility.py`, `check_test_repo_copy_invariants.py`,
    `check_boundary_bypass_ratchet.py`, and
    `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only`
    passed; standing pytest reported `3675 passed in 19.98s`.
- Slice 4 evidence:
  - Prompt-bulk inventory before the change reported 53 findings, with two top
    findings in `scripts/hitl_report_mode_lib.py` from the inline HTML/CSS/JS
    shell (`1349` and `873` chars).
  - Moved the HITL report HTML/CSS/JS shell to
    `scripts/templates/hitl_report.html` and changed
    `scripts/hitl_report_mode_lib.py` to render it via `string.Template`.
  - Synced the plugin export, adding
    `plugins/charness/scripts/templates/hitl_report.html` and updating
    `plugins/charness/scripts/hitl_report_mode_lib.py`.
  - Prompt-bulk inventory after the change reported 51 findings; the two
    `hitl_report_mode_lib.py` HTML findings no longer appear in the sample.
  - Length proof: `scripts/hitl_report_mode_lib.py` moved from `340/480` to
    `314/480` code lines.
  - Focused proof: `pytest -q tests/quality_gates/test_hitl_report_mode.py`,
    `python3 -m py_compile scripts/hitl_report_mode_lib.py`,
    `ruff check scripts/hitl_report_mode_lib.py`, and
    `python3 scripts/sync_root_plugin_manifests.py --repo-root .` passed.
  - Push-gate repair: `dup-ratchet` initially flagged three rotated existing
    helper families after the template extraction shifted `hitl_report_mode_lib.py`;
    reviewed and classified them as intentional in
    `charness-artifacts/quality/dup-review.json`, then
    `check_dup_ratchet.py --repo-root . --json` passed clean.
  - Mutation proof repair: `run_slice_closeout.py --repo-root . --base
    origin/main --produce-mutation-coverage --verification-lock --skip-sync`
    completed and refreshed `reports/mutation/test-coverage.json.fingerprint`.
    The pre-push-shaped check with the concrete `origin/main` SHA passed with
    no blocking targets for `scripts/hitl_report_mode_lib.py`.
- Slice 5 evidence:
  - Prompt-bulk inventory before the change reported 51 findings, with two large
    `tests/charness_cli/support.py` fixture-script literals in the top sample
    (`4211` and `3464` chars).
  - Moved the fake `claude` and fake `codex` executable bodies to
    `tests/charness_cli/fixtures/fake_claude.py` and
    `tests/charness_cli/fixtures/fake_codex.py`; `support.py` now copies those
    files into the temp `bin/` directory and keeps the `fail_plugin_install`
    seam via a sidecar marker.
  - Prompt-bulk inventory after the change reported 49 findings; the two large
    fake binary bodies no longer appear in the top sample.
  - Length proof: `tests/charness_cli/support.py` moved from `641/800` to
    `462/800` code lines.
  - Focused proof: `py_compile`, `ruff check` for the touched test helper and
    fixtures, `pytest -q tests/charness_cli/test_codex_managed_install.py
    tests/charness_cli/test_codex_cache_refresh.py
    tests/charness_cli/test_doctor_cache_selection.py`,
    `check_python_lengths.py --require-git-file-listing`,
    `validate_attention_state_visibility.py`, `check_test_repo_copy_invariants.py`,
    `check_boundary_bypass_ratchet.py`, and
    `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only`
    passed; standing pytest reported `3675 passed in 20.61s`.
- Slice 6 evidence:
  - Prompt-bulk inventory before this change reported 49 findings and still
    sampled `tests/charness_cli/support.py` fake toolchain literals in the top
    results.
  - Moved fake `agent-browser`, `npm`/`defuddle`, `cargo`/`tokei`, and
    `uv`/`ruff`/`vulture` executable bodies to
    `tests/charness_cli/fixtures/`; `support.py` now copies fixture executables
    and writes small sidecar JSON files for temp paths.
  - Prompt-bulk inventory after the change reported 46 findings; the extracted
    npm/cargo/uv bodies no longer appear in the top sample, leaving the larger
    Go/specdown and tool-lifecycle fake bodies as later candidates.
  - Length proof: `tests/charness_cli/support.py` moved from `462/800` to
    `340/800` code lines; new fixture files are each at most `26/800` code
    lines.
  - Focused proof: `py_compile` for the touched helper and fixture files,
    focused `ruff check`, and the release-only CLI update/tool lifecycle subset
    passed; the focused pytest run reported `9 passed, 13 deselected in
    35.10s`.
  - Changed-surface proof: full repo `ruff check`, Python length gate,
    attention-state visibility, test repo copy invariants, boundary-bypass
    ratchet, and the standing pytest runner passed; standing pytest reported
    `3675 passed in 22.35s`.
  - Slice critique: the main risk is sidecar JSON lookup drift between copied
    fake binaries and generated fake tools. Folded response: every copied
    installer script resolves its own `<script>.json` config, and the focused
    update/tool lifecycle tests exercised the npm, cargo, uv, agent-browser,
    specdown, and glow update/install paths.
- Slice 7 evidence:
  - Prompt-bulk inventory before this change reported 46 findings and still
    sampled `tests/charness_cli/support.py` Go installer literals plus
    `tests/charness_cli/test_tool_lifecycle.py` glow installer literals.
  - Moved fake Go/specdown/gitleaks/glow executable bodies to
    `tests/charness_cli/fixtures/`; the helper functions now copy fixture
    executables and write small sidecar JSON files for temp `GOPATH`, `GOBIN`,
    bin-dir, fixture-root, and per-test glow version behavior.
  - Prompt-bulk inventory after the change reported 42 findings; the
    `support.py` and `test_tool_lifecycle.py` fake Go literals no longer appear
    in the top sample.
  - Length proof: `tests/charness_cli/support.py` moved from `340/800` to
    `269/800` code lines; `tests/charness_cli/test_tool_lifecycle.py` moved to
    `550/800`; new Go fixture files are each at most `38/800` code lines.
  - Fresh-eye review flagged an uncovered `GOBIN` branch in the fake Go
    installers. Added a narrow helper-level test and fixed the extracted glow
    fake to create `GOPATH/bin` before writing the target binary when `GOBIN`
    redirects the install root.
  - Focused proof: `py_compile`, focused `ruff check`, the new `GOBIN` helper
    test, and the release-only CLI update/tool lifecycle subset for update-all,
    specdown, and glow passed; the focused pytest run reported `6 passed,
    17 deselected in 28.09s`.
  - Changed-surface proof: full repo `ruff check`, Python length gate,
    attention-state visibility, test repo copy invariants, boundary-bypass
    ratchet, and the standing pytest runner passed; standing pytest reported
    `3675 passed in 21.22s`.
  - Slice critique: the main risks were preserving the old installer distinction
    between support's glow version (`glow version 2.1.2`) and the lifecycle
    test's glow version (`glow 2.1.1-test`), plus `GOBIN` path behavior. Folded
    response: the shared `fake_glow.py` reads optional sidecar config, focused
    glow/specdown tests exercised the configured behavior, and the new helper
    test covers `GOBIN`.
- Slice 8 evidence:
  - Prompt-bulk inventory before this change reported 42 findings and surfaced
    `tests/quality_gates/release_publish_fixtures.py` fake release CLI literals
    in the top sample.
  - Moved fake `git`, fake `gh`, and distinct-channel probe executable bodies
    to `tests/quality_gates/fixtures/`; `release_publish_fixtures.py` now copies
    those fixture scripts and writes a tiny sidecar JSON file for the real git
    binary path.
  - Prompt-bulk inventory after the change reported 39 findings; only the
    smaller inline sync script remains sampled from `release_publish_fixtures.py`.
  - Length proof: `tests/quality_gates/release_publish_fixtures.py` moved to
    `194/800` code lines; new release fixture files are each at most `49/800`
    code lines.
  - Focused proof: `py_compile`, focused `ruff check`, and the release publish
    focused pytest bundle passed; focused pytest reported `77 passed in 52.17s`.
  - Changed-surface proof: full repo `ruff check`, Python length gate,
    attention-state visibility, test repo copy invariants, boundary-bypass
    ratchet, and the standing pytest runner passed; standing pytest reported
    `3676 passed in 20.23s`.
  - Fresh-eye review: no blocking correctness issue found; reviewer flagged only
    that the three new fixture scripts must be committed with the helper change.
    Folded response: stage all new fixture scripts in the slice commit.

## Context Sources

- User clarification in chat: "계속 발굴하라는 거 맞음".
- Prior completed goal:
  `charness-artifacts/goals/2026-06-27-sustained-quality-speed-token-release-round-4.md`
- `docs/handoff.md`
- `charness-artifacts/retro/recent-lessons.md`
- `charness-artifacts/quality/latest.md`

## Interview Decisions

- Continue rather than only acknowledge because the user corrected the intended
  operating shape.
- Treat `v0.56.5` as already published and keep additional slices local until a
  new release decision is justified.
- Prefer measured current candidates over stale handoff text when they conflict.

## Plan Critique Findings

- Same-agent critique: another immediate release would compound the premature
  release mistake. Folded response: release is deferred until the continuation
  bundle warrants it.
- Same-agent critique: broad `<repo-root>/scripts/...` reference existence
  enforcement would currently flag many historical path conventions. Folded
  response: fix the concrete support-skill drift first and leave broader cleanup
  as a later candidate.

## Off-Goal Findings

- Broader `<repo-root>/scripts/...` reference cleanup may be useful, but it needs
  a separate source-of-truth decision because many public skill references use
  that convention today.

## Final Verification

Retro: skipped: not-closeout-yet: continuation goal is still active.
Host log probe: skipped: not-closeout-yet: continuation goal is still active.
Disposition review: skipped: not-closeout-yet: continuation goal is still active.

## User Verification Instructions

- Inspect changed support-skill references and handoff text after slice 1.
- Run focused validators named in the slice log.

## Auto-Retro

Retro dispositions: pending until closeout.
