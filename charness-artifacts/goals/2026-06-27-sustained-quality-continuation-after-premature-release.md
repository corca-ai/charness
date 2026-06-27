# Achieve Goal: Sustained quality continuation after premature release

Status: active
Created: 2026-06-27
Activation: `/goal @charness-artifacts/goals/2026-06-27-sustained-quality-continuation-after-premature-release.md`

This goal continues the prior quality timebox after the `v0.56.5` release was
cut too early relative to the user's intent to keep discovering quality slices.

## Active Operating Frame

- Current slice: slice 17 complete; re-inventory for slice 18.
- Current slice intent: continue prompt/template bulk reduction after the issue
  closeout-draft stub extraction.
- Next action: commit and push slice 17, then continue discovery unless a
  release-worthy boundary is reached.
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
| 9 | Reuse release fake git fixture for tag-history and real-host tests | Prompt-bulk inventory still surfaced a second fake git body in `test_release_publish_real_host_delta.py` | focused tag-history/real-host tests, prompt-bulk delta, standing pytest | complete |
| 10 | Extract remaining release publish sync/quality fake scripts | `release_publish_fixtures.py` still carried inline sync and quality scripts after fake CLI extraction | focused release publish tests, prompt-bulk delta, standing pytest | complete |
| 11 | Extract handoff auto-draft goal template from Python | Prompt-bulk inventory next surfaced `chunked_routing_auto_draft.py`; the content is a template asset rather than Python logic | focused handoff tests, prompt-bulk delta, plugin sync, standing pytest | complete |
| 12 | Extract handoff ranker prompt template from Python | Prompt-bulk inventory next surfaced `chunked_routing_lib.py`; the ranker prompt is static prompt content, not Python logic | focused handoff ranker tests, prompt-bulk delta, plugin sync, standing pytest | complete |
| 13 | Extract setup host-docs AGENTS fragments from Python | Prompt-bulk inventory next surfaced `setup_host_docs_lib.py`; these Markdown fragments are template assets, not Python logic | focused setup tests, prompt-bulk delta, plugin sync, standing pytest | complete |
| 14 | Extract plugin import smoke script template from Python | Prompt-bulk inventory next surfaced `validate_packaging_install_surface.py`; the subprocess body is script text, not validator logic | focused packaging tests, prompt-bulk delta, plugin sync, standing pytest | complete |
| 15 | Extract achieve closeout stub template from Python | Prompt-bulk inventory next surfaced `describe_goal_closeout_shape.py`; the closeout starter stub is generated content, not Python logic | focused achieve/preflight tests, prompt-bulk delta, plugin sync, standing pytest | complete |
| 16 | Extract critique adapter scaffold template from Python | Prompt-bulk inventory next surfaced `critique/scripts/init_adapter.py`; the adapter skeleton is generated YAML, not Python logic | focused critique/reviewer tests, prompt-bulk delta, plugin sync, standing pytest | complete |
| 17 | Extract issue closeout-draft stub template from Python | Prompt-bulk inventory next surfaced `describe_closeout_draft_shape.py`; the starter closeout body is generated Markdown, not Python logic | focused issue/preflight tests, prompt-bulk delta, plugin sync, standing pytest | complete |
| 18 | Continue discovery/push/release decision | Avoid another premature release | next candidate ledger, final validators, commit/push, release recommendation | pending |

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
- Slice 9 evidence:
  - Prompt-bulk inventory after slice 8 still reported 39 findings and surfaced
    `tests/quality_gates/test_release_publish_real_host_delta.py` as a large
    inline fake git script candidate.
  - Added the real-host/tag-history failure knobs to the shared
    `tests/quality_gates/fixtures/release_publish_fake_git.py` fixture and
    changed the real-host delta helper to copy that fixture with sidecar real-git
    config.
  - Prompt-bulk inventory after the change reported 38 findings; the
    `test_release_publish_real_host_delta.py` fake git body no longer appears in
    the top sample.
  - Fresh-eye review: no blocking issue found; reviewer flagged that
    `FAKE_GIT_LS_REMOTE_TAG_HISTORY_FAIL` had only helper-level coverage. Folded
    response: added a full subprocess `publish-current` test for that shared
    fixture knob.
  - Focused proof: `py_compile`, focused `ruff check`, and the real-host
    delta/tag-history pytest bundle passed; focused pytest reported `17 passed
    in 12.57s`.
  - Changed-surface proof before artifact update: full repo `ruff check`, Python
    length gate, attention-state visibility, test repo copy invariants,
    boundary-bypass ratchet, and the standing pytest runner passed; standing
    pytest reported `3676 passed in 21.02s`.
- Slice 10 evidence:
  - Moved the remaining fake release sync command and fake quality command from
    `tests/quality_gates/release_publish_fixtures.py` to
    `tests/quality_gates/fixtures/release_publish_sync_root_plugin_manifests.py`
    and `tests/quality_gates/fixtures/release_publish_run_quality.sh`.
  - Kept `_write_exec` in `release_publish_fixtures.py` because downstream
    release tests import it for small one-off executable fixtures.
  - Prompt-bulk inventory after the change reported 37 findings and no longer
    sampled `release_publish_fixtures.py`.
  - Length proof: `tests/quality_gates/release_publish_fixtures.py` moved to
    `154/800` code lines; the new Python sync fixture is `23/800` code lines.
  - Focused proof: `py_compile`, focused `ruff check`, `bash -n` for the shell
    fixture, and the release publish focused pytest bundle passed; focused
    pytest reported `78 passed in 53.31s`.
  - Changed-surface proof: full repo `ruff check`, Python length gate,
    attention-state visibility, test repo copy invariants, boundary-bypass
    ratchet, and the standing pytest runner passed; standing pytest reported
    `3677 passed in 21.15s`.
  - Fresh-eye review: no blocking issue found; reviewer flagged only that the
    two new fixture files must be committed with the helper change. Folded
    response: stage both new fixture files in the slice commit.
- Slice 11 evidence:
  - Prompt-bulk inventory after slice 10 reported 37 findings and surfaced
    `skills/public/handoff/scripts/chunked_routing_auto_draft.py` as the next
    large inline template candidate.
  - Moved the auto-draft goal artifact shell to
    `skills/public/handoff/scripts/templates/auto_draft_goal.md`; the Python
    renderer now reads that template file and keeps the existing `.format(...)`
    contract.
  - Synced plugin export, adding
    `plugins/charness/skills/handoff/scripts/templates/auto_draft_goal.md` and
    updating the plugin mirror of `chunked_routing_auto_draft.py`.
  - Prompt-bulk inventory after the change reported 36 findings; the handoff
    auto-draft template no longer appears in the top sample.
  - Length proof: `skills/public/handoff/scripts/chunked_routing_auto_draft.py`
    moved to `162/360` code lines.
  - Fresh-eye review: blocking closeout risk was staging hygiene for the new
    source and plugin template files; non-blocking gap was the lack of a full
    rendered-output golden after template extraction. Folded response: stage
    both template files and add `tests/fixtures/handoff-auto-draft-rendered.txt`
    plus a full-render comparison test.
  - Dup-ratchet closeout: classified the 3 new doc duplicate families
    (`13741926e48b3ac1`, `b56c1479ef7c3d0e`, `c4b45fc90f69c007`) as intentional
    because the handoff auto-draft template must preserve the achieve goal
    artifact activation/header, section skeleton, and decision-queue shape;
    `check_dup_ratchet.py --json` then reported `status: clean`.
  - Public-skill scenario review: `suggest_public_skill_dogfood.py --skill-id
    handoff` returned the existing handoff consumer case, and
    `evals/cautilus/scenarios.json` still maps `handoff` to
    `handoff-adapter-bootstrap`; recorded the no-registry-change decision in
    `docs/public-skill-dogfood.json` because this slice changes implementation
    shape, not routing or adapter bootstrap behavior. Cautilus planner
    `next_action: none`, so no evaluator run was performed.
  - Focused proof: `py_compile`, focused `ruff check`, and the handoff
    auto-draft/end-to-end/producer pytest bundle passed; focused pytest reported
    `18 passed in 1.02s`.
  - Changed-surface proof: packaging validators, markdown/doc/secret checks,
    skill validators, public-skill validation and dogfood validators,
    gitignore-scan hygiene, and the standing pytest runner passed; standing
    pytest reported `3678 passed in 20.94s`.
- Slice 12 evidence:
  - Prompt-bulk inventory after slice 11 reported 36 findings and surfaced
    `skills/public/handoff/scripts/chunked_routing_lib.py` as the next static
    prompt candidate.
  - Moved `RANKER_PROMPT` to
    `skills/public/handoff/scripts/templates/ranker_prompt.txt`; the Python
    module now reads that template asset and strips only trailing newlines so
    packet output remains stable.
  - Synced plugin export, adding
    `plugins/charness/skills/handoff/scripts/templates/ranker_prompt.txt` and
    updating the plugin mirror of `chunked_routing_lib.py`.
  - Prompt-bulk inventory after the change reported 35 findings; the handoff
    ranker prompt no longer appears in the sample.
  - Length proof: `skills/public/handoff/scripts/chunked_routing_lib.py` and
    its plugin mirror report `217` Python code lines.
  - Focused proof: `py_compile`, focused `ruff check`, and the handoff
    ranker/end-to-end pytest bundle passed; focused pytest reported `17 passed
    in 0.60s`.
  - Changed-surface proof: packaging validators, markdown/doc/secret checks,
    skill validators, public-skill validation and dogfood validators, staged
    mirror drift, the focused handoff/goal pytest bundle, and the standing
    pytest runner passed; standing pytest reported `3679 passed in 20.83s`.
  - Fresh-eye review: blocking closeout risk was staging hygiene for the new
    source and plugin template files; non-blocking gap was direct plugin parity
    coverage. Folded response: stage both template files and rely on
    `sync_root_plugin_manifests.py`, staged mirror drift, packaging validators,
    and byte-for-byte source/plugin template diff for plugin parity.
  - Closeout producer proof:
    `run_slice_closeout.py --skip-sync --allow-unmatched
    --ack-cautilus-skill-review --produce-mutation-coverage
    --verification-lock` completed, including coverage-instrumented standing
    pytest, gitignore-scan hygiene, and agent browser runtime guard. Cautilus
    planner reported `next_action: none`; recorded the no-registry-change
    decision in `docs/public-skill-dogfood.json` because this slice changes
    implementation shape, not handoff routing or adapter bootstrap behavior.
- Slice 13 evidence:
  - Prompt-bulk inventory after slice 12 reported 35 findings and surfaced
    `scripts/setup_host_docs_lib.py` as the next generated-doc template
    candidate.
  - Moved the AGENTS.md commit-discipline and compact subagent-delegation
    fragments to `scripts/templates/agents_commit_discipline.txt` and
    `scripts/templates/agents_subagent_delegation.txt`; `setup_host_docs_lib.py`
    now reads those template assets.
  - Synced plugin export, adding the matching
    `plugins/charness/scripts/templates/agents_commit_discipline.txt` and
    `plugins/charness/scripts/templates/agents_subagent_delegation.txt` files.
  - Prompt-bulk inventory after the change reported 33 findings; the two
    `setup_host_docs_lib.py` template fragments no longer appear.
  - Focused proof: `py_compile`, focused `ruff check`, and setup
    commit-discipline/normalize-host-docs pytest passed; focused pytest
    reported `13 passed in 0.46s`.
  - Markdown closeout correction: first broad markdown pass failed because the
    fragment files used `.md` while intentionally starting at `##`; renamed them
    to `.txt` template assets so generated output stays unchanged and standalone
    Markdown document rules do not apply.
  - Changed-surface proof: packaging validators, plugin import smoke, staged
    mirror drift, markdown/doc/secret checks, focused setup/preflight pytest,
    and the standing pytest runner passed; standing pytest reported `3680
    passed in 23.03s`.
  - Fresh-eye review: blocking closeout risk was the same staging hygiene after
    the `.txt` correction; folded response: stage the `.md` removals and `.txt`
    additions together with `git add -A`, then re-run staged mirror drift.
  - Closeout producer proof:
    `run_slice_closeout.py --skip-sync --allow-unmatched
    --produce-mutation-coverage --verification-lock` completed, including
    coverage-instrumented standing pytest, integration/support/tool update
    checks, gitignore-scan hygiene, and agent browser runtime guard.
- Slice 14 evidence:
  - Prompt-bulk inventory after slice 13 reported 33 findings and surfaced
    `scripts/validate_packaging_install_surface.py` as the next inline script
    candidate.
  - Moved the plugin import-smoke subprocess body to
    `scripts/templates/plugin_import_smoke.py.txt`; the validator now reads that
    template asset and passes it to `python3 -c`.
  - Synced plugin export, adding
    `plugins/charness/scripts/templates/plugin_import_smoke.py.txt` and updating
    the plugin mirror of `validate_packaging_install_surface.py`.
  - Prompt-bulk inventory after the change reported 32 findings; the packaging
    import-smoke body no longer appears.
  - Focused proof: `py_compile`, focused `ruff check`, two packaging tests, and
    `check_plugin_import_smoke.py --repo-root .` passed.
  - Changed-surface proof: packaging validators, plugin import smoke,
    markdown/doc/secret checks, focused packaging pytest, and the standing
    pytest runner passed; standing pytest reported `3681 passed in 20.52s`.
  - Fresh-eye review: no blocking finding. Reviewer verified staged scope,
    source/plugin template parity, import-time template paths, the `python3 -c`
    call contract, and that the template body matched prior behavior except for
    a harmless leading newline removal.
  - Closeout producer proof:
    `run_slice_closeout.py --skip-sync --allow-unmatched
    --produce-mutation-coverage --verification-lock` completed, including
    coverage-instrumented standing pytest, integration/support/tool update
    checks, gitignore-scan hygiene, and agent browser runtime guard.
- Slice 15 evidence:
  - Prompt-bulk inventory after slice 14 reported 32 findings and surfaced
    `skills/public/achieve/scripts/describe_goal_closeout_shape.py` as the next
    generated-content candidate.
  - Moved the goal-closeout starter stub to
    `skills/public/achieve/scripts/templates/closeout_stub.txt`; the
    `stub()` helper now reads that template asset.
  - Synced plugin export, adding
    `plugins/charness/skills/achieve/scripts/templates/closeout_stub.txt` and
    updating the plugin mirror of `describe_goal_closeout_shape.py`.
  - Prompt-bulk inventory after the change reported 31 findings; the achieve
    closeout stub no longer appears.
  - Focused proof: `py_compile`, focused `ruff check`, and the achieve
    closeout/preflight pytest bundle passed; focused pytest reported `61 passed
    in 1.77s`.
  - Attention-state correction: first standing pytest pass surfaced that
    `validate_attention_state_visibility.py` expects the declared evidence term
    `skipped: <allowed-reason>` to remain visible from the source file. Added a
    short source marker pointing at the extracted stub's skip form, then
    `validate_attention_state_visibility.py` and focused preflight tests passed.
  - Changed-surface proof: skill/public-skill/packaging validators, markdown/doc
    checks, plugin import smoke, staged mirror drift, focused achieve/preflight
    pytest, and the standing pytest runner passed; standing pytest reported
    `3682 passed in 20.47s`.
  - Public-skill scenario review: `suggest_public_skill_dogfood.py --skill-id
    achieve` confirmed `achieve` remains `hitl-recommended`; Cautilus planner
    reported `next_action: none`. Recorded the unchanged consumer-contract
    decision in `docs/public-skill-dogfood.json` because this slice changes
    implementation shape, not routing, activation, draft creation, adapter
    bootstrap, or maintained evaluator behavior.
  - Fresh-eye review: no blocking finding. Reviewer verified `stub()` behavior,
    source/plugin template parity, plugin import-time path parity, and that this
    is implementation-shape extraction rather than dogfood/scenario behavior
    change.
  - Closeout producer proof:
    `run_slice_closeout.py --skip-sync --allow-unmatched
    --ack-cautilus-skill-review --produce-mutation-coverage
    --verification-lock` completed, including skill/public-skill/dogfood
    validators, docs/markdown/secrets checks, focused structural sweeps,
    coverage-instrumented standing pytest, gitignore-scan hygiene, and agent
    browser runtime guard. Usage episode:
    `slice-closeout-2dc738253c624e9eae79706a33631549`.
  - Pre-push repair: first push attempt passed 78/79 full quality gates but
    `dup-ratchet` blocked one new code family
    (`182c64eeb9a8ccb7`) between `achieve` and `issue` closeout-shape helper
    output tails. Reworked the `achieve` `main()` output branch to remove the
    family instead of classifying it; `check_dup_ratchet.py` then reported no
    new code/doc families and the focused achieve/preflight pytest bundle
    reported `61 passed in 1.63s`.
- Slice 16 evidence:
  - Prompt-bulk inventory after slice 15 reported 31 findings and surfaced
    `skills/public/critique/scripts/init_adapter.py` as the next public-skill
    generated-content candidate.
  - Moved the critique adapter skeleton to
    `skills/public/critique/scripts/templates/critique_adapter.yaml`; the
    `init_adapter.py` scaffold now reads that template asset.
  - Synced plugin export, adding
    `plugins/charness/skills/critique/scripts/templates/critique_adapter.yaml`
    and updating the plugin mirror of `init_adapter.py`.
  - Added deterministic coverage that the scaffolded
    `.agents/critique-adapter.yaml` exactly equals the source template asset.
  - Prompt-bulk inventory after the change reported 30 findings; the critique
    adapter skeleton no longer appears.
  - Focused proof: `py_compile`, focused `ruff check`, and the critique
    reviewer/prepare-packet pytest bundle passed; focused pytest reported
    `56 passed in 2.26s`.
  - Public-skill scenario review: `suggest_public_skill_dogfood.py --skill-id
    critique` confirmed `critique` remains `hitl-recommended`; Cautilus planner
    reported `next_action: none`. Recorded the unchanged consumer-contract
    decision in `docs/public-skill-dogfood.json` because this slice changes
    implementation shape, not routing, artifact home, packet/reviewer-tier
    evidence, counterweight triage, output shape, or maintained evaluator
    behavior.
  - Changed-surface proof: skill/public-skill/dogfood validators, packaging
    validators, plugin import smoke, doc/markdown checks, dup-ratchet,
    attention-state visibility, and the standing pytest runner passed; standing
    pytest reported `3683 passed in 20.67s`.
  - Fresh-eye review: no blocking finding. Reviewer verified source/plugin
    mirror parity, byte-identical template extraction from the old inline
    skeleton, template-asset test coverage, dogfood/Cautilus `next_action: none`
    honesty, and packaging surface coverage; only closeout note was to include
    both new template files in the final commit.
  - Closeout producer proof:
    `run_slice_closeout.py --skip-sync --allow-unmatched
    --ack-cautilus-skill-review --produce-mutation-coverage
    --verification-lock` completed, including skill/public-skill/dogfood
    validators, docs/markdown/secrets checks, focused structural sweeps,
    coverage-instrumented standing pytest, gitignore-scan hygiene, and agent
    browser runtime guard. Usage episode:
    `slice-closeout-0c48db7271864f42bda0b3a62f5ecde2`.
- Slice 17 evidence:
  - Prompt-bulk inventory after slice 16 reported 30 findings and surfaced
    `skills/public/issue/scripts/describe_closeout_draft_shape.py` as the next
    public-skill generated-content candidate.
  - Moved the issue closeout-draft starter body to
    `skills/public/issue/scripts/templates/closeout_draft_stub.txt`; the
    `stub()` helper now reads that template asset.
  - Synced plugin export, adding
    `plugins/charness/skills/issue/scripts/templates/closeout_draft_stub.txt`
    and updating the plugin mirror of `describe_closeout_draft_shape.py`.
  - Added deterministic coverage that the emitted closeout-draft stub exactly
    equals the source template asset.
  - Prompt-bulk inventory after the change reported 29 findings; the issue
    closeout-draft stub no longer appears.
  - Focused proof: `py_compile`, focused `ruff check`, and the issue
    closeout/preflight pytest bundle passed; focused pytest reported
    `69 passed in 2.71s`.
  - Public-skill scenario review: `suggest_public_skill_dogfood.py --skill-id
    issue` confirmed `issue` remains `evaluator-required`; Cautilus planner
    reported `next_action: none` but required maintained scenario review.
    Inspected `evals/cautilus/scenarios.json`: `issue` remains mapped to
    `issue-sibling-search-concept-fixtures` and
    `representative-skill-contracts`; recorded no scenario-registry change in
    `docs/public-skill-dogfood.json` because this slice changes implementation
    shape, not issue routing, GitHub source-of-truth behavior, causal review,
    feature-brief behavior, or the enforced `validate-closeout-draft` grammar.
  - Changed-surface proof: skill/public-skill/dogfood/scenario validators,
    packaging validators, plugin import smoke, doc/markdown checks,
    dup-ratchet, attention-state visibility, and the standing pytest runner
    passed; standing pytest reported `3683 passed in 22.89s`.
  - Fresh-eye review: no blocking finding. Reviewer verified source/plugin
    mirror parity, exact old `--stub` body including final newline, template
    asset coverage, honest evaluator-required scenario review, and packaging
    export coverage.
  - Closeout producer repair: first closeout producer attempt failed
    `check-markdown.sh` because the template was named `.md`, so placeholder
    forms such as `<the job...>` were linted as Markdown/HTML. Renamed the
    template to `closeout_draft_stub.txt`, resynced the plugin export, updated
    references/tests, and reran focused issue/preflight tests (`69 passed in
    2.49s`) plus markdown/mirror checks successfully.
  - Closeout producer proof:
    `run_slice_closeout.py --skip-sync --allow-unmatched
    --ack-cautilus-skill-review --produce-mutation-coverage
    --verification-lock` completed after the `.txt` repair, including
    skill/public-skill/dogfood validators, docs/markdown/secrets checks,
    focused structural sweeps, coverage-instrumented standing pytest,
    gitignore-scan hygiene, and agent browser runtime guard. Usage episode:
    `slice-closeout-19fa63a158684405b2f6a1fb258cd712`.

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
