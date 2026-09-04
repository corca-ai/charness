# Deferred-decisions archive

Date: 2026-09-04
Status: archived; `docs/deferred-decisions.md` was deleted

There is no live register and no how-to-defer page. Closed choices live in
their owning mechanisms and docs. Resolved, declined, and "not now" entries
live here so a reopener can quote the trigger without a second operating
manual in `docs/`.

The pasted body below was copied from `docs/` and is **historical**. Its
`Status: current` header and relative links are frozen as of that tree; do not
treat a heading that still says "Defer" as a live open item. The disposition
table above is the 2026-09-04 stamp. Paths in the table are repo-root relative.

## 2026-09-04 dispositions (operator: empty the register)

Do not implement. The current mechanism, or an explicit decline, is the answer.

| ID | Disposition | Where the choice now lives |
| --- | --- | --- |
| D1, D3, D4 | already the packaging contract | `packaging/charness.json`, `docs/host-packaging.md` |
| D5, D8 | already metadata-only `extends` | `profiles/profile.schema.json` |
| D6 | already metadata, no secret orchestration | `integrations/tools/manifest.schema.json` |
| D7 | already `trusted` | discovery/catalog copy |
| D9–D17 | already the skill/preset shapes | owning SKILL.md / presets |
| D19 | decline taint analysis | helper-adoption + string-literal scanner |
| D27 | decline rewriting the filter | keep `sed '/^Finding: /d'` until upstream ships quiet |
| D28 remainder | decline fill-guards and `--write` | until n-fold rework evidence; polarity already resolved |
| D29 | decline scorecard helper/guard | until a consumer skip or metric-only closeout is observed |
| D30, D36, D38, D50 | already resolved | named mechanisms in the archived entries |
| D34, D35, D44 | already declined | archived entries |
| D39 | decline widening the fingerprint to `tests/` | `skills/public/quality/references/mutation-testing.md` freshness section (pool-scoped; `tests/` edits do not invalidate) |
| D40 | decline a second pre-landing producer | release-final lane already owns the block |
| D41 | decline mapper widening | dotted imports; fix call sites |
| D42 | decline exit 3 | operator 2026-07-30: exit 0 + hedge |
| D43 | decline per-label slack | operator 2026-07-30: global factor |
| D45 | decline arming `--require-evaluated-scope` | flag exists; wiring it reds this repo's exempt workflows |
| D47 | decline arming the marker | measured, not armed; distinctiveness withdrawn |
| D48 | decline deriving absence from sync | declared-only in release adapter-contract; resume now re-reads the surface before publish |
| D51 | decline waiting on GitHub Actions before tag | `skills/public/release/SKILL.md` and `references/publication-boundary.md`: local `--release`, then tag/push, then distinct-channel readback. Distinct-channel is post-publication, not a different-observer CI wait before tag. |
| D54 | decline a CPU-time SLO | wall-clock stays advisory telemetry |

Reopen from the trigger on the archived entry, then decide in the owning
mechanism or docs page. Do not recreate a register.

---

# Deferred Decisions (historical copy)

> Status: archived
> Source of truth: the 2026-09-04 disposition table above, then owning mechanisms
> Last verified: 2026-09-04

This document is the canonical closure surface for deferred product-boundary
decisions that were previously carried in session state.

## Scope

- Decision window: pre-integration cleanup closure
- Closed date: 2026-04-10
- Owner: current `charness` maintainer session

## Record Shape

Use this shape when a closed decision needs to be reopened:

```text
Decision ID:
Question:
Current choice:
Why now:
Alternatives considered:
Impact surfaces:
Reopen trigger:
```

## Named Remedy Premise Contract

A remedy recorded in a deferred decision is a hypothesis, not an implementation
plan. Before shaping work around a named remedy, the next resolver must inspect
the current owner and first reader of the channel the remedy assumes, then run
or read the smallest evidence that can establish whether that channel exists
and behaves as described. A historical sentence is not a current capability.

Record the result in the decision entry before implementation begins:

```text
Named remedy premise:
- Remedy: <the proposed repair, quoted or named>
- Premise: <the current fact the repair depends on>
- Evidence channel: <file read, command, fixture, or live readback>
- Observation: <what the current channel actually establishes>
- Downstream decision delta: <the later remedy, scope, order, or stop decision changed by this result>
- Status: verified | falsified | narrowed | withdrawn | not-run
```

`Downstream decision delta` is the acceptance boundary: if the observation
does not change or falsify a later remedy decision, the premise check has not
yet earned a slice. `not-run` is an explicit non-claim, not permission to
implement the named remedy. This is a review convention, not a new mechanical
blocking floor; the owning issue, reviewer, and closeout record decide whether
the evidence is sufficient for the boundary at hand.

## Closed Decisions (2026-04-10)

### D1. Shared Packaging Canonical Source

- Question: Which shared packaging manifest is canonical for Claude/Codex dual support?
- Current choice: [`packaging/charness.json`](../packaging/charness.json). Detail: [host-packaging](./host-packaging.md).
- Reopen trigger: If host-specific metadata can no longer be represented as generated output from one shared manifest.

### D3. Packaging Version Ownership

- Question: Should the shared packaging manifest carry release version directly or rely on export-time override?
- Current choice: Shared manifest is canonical for default version; export-time override is allowed. Detail: [host-packaging](./host-packaging.md).
- Reopen trigger: If release tooling requires immutable manifest-only versioning with no override path.

### D4. Generated Export Tree Storage

- Question: Store generated Claude/Codex export trees as fixtures or keep script+temp smoke canonical?
- Current choice: Script-driven temporary materialization; do not commit generated export trees. Detail: [host-packaging](./host-packaging.md).
- Reopen trigger: If a downstream installer requires committed generated trees as contract artifacts.

### D5. `profile.extends` Depth

- Question: Promote `extends` into merged-bundle runtime behavior now?
- Current choice: Keep `extends` as constrained metadata seam; no broad merged-bundle runtime expansion in this phase.
- Reopen trigger: If real profile composition demand appears in downstream consumer repos.

### D6. Integration Capability Depth

- Question: How deep should capability grants/authenticated binary/env fallback go beyond metadata?
- Current choice: Metadata + validation only; no secretful runtime orchestration. Schema: [manifest.schema.json](../integrations/tools/manifest.schema.json).
- Reopen trigger: If multiple consumers need standardized executable orchestration beyond current manifest metadata.

### D7. `official` Terminology in Discovery Policy

- Question: Replace `official` with broader wording (`trusted`/`declared`) now?
- Current choice: Replace `official` with `trusted` now.
- Reopen trigger: If the trust policy later needs a more precise distinction than one `trusted` bucket.

### D8. Profile Inheritance Policy

- Question: Allow richer inheritance vs flattened bundles?
- Current choice: Favor flattened effective bundles for execution, with minimal inheritance metadata retained for authoring convenience only.
- Reopen trigger: If flattening causes repeated maintenance burden across real consumer profiles.

### D9. Preset Contract Format

- Question: Move presets to JSON schema now or keep markdown-first catalog?
- Current choice: Keep markdown-first preset contract with required frontmatter until first downstream organization preset matures.
- Reopen trigger: If org-install preset scale needs stronger machine-only schema guarantees.

### D10. `ideation` Core Boundary

- Question: How much entity/stage thinking belongs in public core vs references?
- Current choice: Keep lightweight entity/stage framing in public core; push detailed playbooks, examples, and edge handling into references.
- Reopen trigger: If repeated user confusion shows core guidance is too thin.

### D11. `spec` Weight Control

- Question: How to keep `spec` strong without procedural bloat?
- Current choice: Keep heuristic core (`Fixed Decisions` / `Probe Questions` / `Deferred Decisions`) and keep procedural detail, examples, and edge handling in references.
- Reopen trigger: If implementation handoff quality repeatedly fails due to underspecified core guidance.

### D12. `quality` Skill Identity

- Question: Is `quality` a proposal skill, gate skill, or both?
- Current choice: `quality` remains a strong public proposal/review skill; deterministic enforcement stays in repo-owned quality gates/scripts.
- Reopen trigger: If users need one unified interface that both proposes and enforces without ambiguity.

### D13. Sample Preset Scope

- Question: Keep sample presets repo-agnostic vs move to host/profile seams?
- Current choice: Keep `charness`-shipped presets repo-agnostic maintainer examples; make those examples realistic and varied, but keep consumer-specific install surfaces in downstream repos.
- Reopen trigger: If cross-host install UX requires shipping host-specific presets in-core.

### D14. Quality Dogfood Proposal Promotion

- Question: Where should Session 10+ gate proposals be implemented?
- Current choice: Implement only deterministic, repo-owned gates in `charness`; keep evaluator/HITL-heavy checks in an explicit consumer-owned workflow.
- Reopen trigger: If current repo-owned gates prove insufficient for regression containment.

### D15. `spec` Mode Strategy

- Question: Keep explicit mode menu or heuristic branch?
- Current choice: Stay with heuristic branch strategy; explicit mode menu remains retired.
- Reopen trigger: If operators repeatedly request explicit mode selection for predictability.

### D16. `announcement` Delivery Kinds

- Question: How much delivery taxonomy belongs in `announcement` public core?
- Current choice: `announcement` is human-to-human communication. Public core covers draft shape, audience, and explicit human-facing delivery confirmation; actual delivery backends stay adapter-defined, and `command` is not a public core kind.
- Reopen trigger: If multiple consumers need the same additional human-facing delivery concept beyond draft style plus adapter-defined backend.

### D17. `hitl` Runtime State Depth

- Question: Keep portable minimum runtime state vs add richer queue/context tooling now?
- Current choice: Keep portable minimum runtime state model in public core for agent-to-human bounded review; consider richer queue and context tooling as future support-layer work.
- Reopen trigger: If current state model cannot sustain real review-loop throughput.

## Open Deferrals (2026-05-07)

### D19. Current-Pointer Write Scanner Generalization

- Question: Should [check_current_pointer_writes.py](../tools/check_current_pointer_writes.py) detect adapter-resolved current-pointer writes via taint analysis, or rely on per-writer helper adoption?
- Current choice: Defer scanner generalization; rely on helper-adoption convention for adapter-resolved writers. The static scanner continues to catch string-literal `latest.md` / `latest.json` writes only.
- Why now: Only one adapter-resolved sibling ([hitl sync_review_artifact.py](../skills/public/hitl/scripts/sync_review_artifact.py)) was discovered, and it was closed in commit `0364886` by migrating to `write_current_pointer_text`. Adding taint analysis on a single sample is premature; the fixture matrix and false-positive surface are larger than the leak surface.
- Impact surfaces: [tools/check_current_pointer_writes.py](../tools/check_current_pointer_writes.py), [scripts/artifacts/current_pointer_writer_lib.py](../scripts/artifacts/current_pointer_writer_lib.py), future skill writers that resolve their durable artifact path through an adapter dictionary.
- Reopen trigger: When a second adapter-resolved current-pointer sibling that bypasses the string-literal scanner appears, or when more than one new skill adds a `latest.md` / `latest.json` writer through adapter-resolved paths without the helper.

### D27. markdownlint-cli2 Verbose Banner Filter

- Question: Should [`check-markdown.sh`](../scripts/check-markdown.sh) keep the local `sed` `Finding:` filter forever, or replace it once markdownlint-cli2 adds a `--quiet` flag or equivalent upstream knob?
- Current choice: Defer. v0.21.0 has no quiet flag; the banner line listing every linted path is the only source of the per-commit stdout flood. The filter is anchored, load-bearing-space, and verified against a known-failing fixture.
- Why now: Local one-line fix is correct today; rewriting it under a future upstream flag would just be ceremony until the upgrade actually lands.
- Impact surfaces: [scripts/check-markdown.sh](../scripts/check-markdown.sh)
- Reopen trigger: markdownlint-cli2 ships a documented quiet/verbosity flag, OR the per-error line format changes such that legitimate errors now begin with the same prefix the filter drops (caught by slice 6 stop condition on every fixture run).

### D28. Template-First Fill Guards And Report-All For Sibling Artifact Validators — POLARITY RESOLVED, FILL GUARDS STILL DEFERRED (2026-07-27)

- Question: Should the fill-time guard comments added to the quality scaffold be generalized to the other scaffold families (debug, critique, retro, handoff, ideation), should the sibling artifact validators share ONE one-pass control instead of per-family flag polarity, and should `emit_payload_main` in [scaffold_artifact_lib.py](../scripts/core/scaffold_artifact_lib.py) grow a `--write` mode so scaffold-first becomes the path of least resistance?
- Current choice: one-pass is resolved — `--fail-fast` is the family's only control, declared once in `add_one_pass_args`, and the critique/debug/retro/ideation validators route `main()` through `run_changed_artifact_validator` in [artifact_validator.py](../scripts/artifacts/artifact_validator.py). Fill guards and `emit_payload_main --write` stay deferred.
- Impact surfaces: [scripts/artifacts/artifact_validator.py](../scripts/artifacts/artifact_validator.py), the debug/critique/retro/ideation/handoff/quality validators, [scripts/run-quality.sh](../scripts/run-quality.sh), [scripts/core/scaffold_artifact_lib.py](../scripts/core/scaffold_artifact_lib.py) and the five sibling scaffolds.
- Reopen trigger: `emit_payload_main --write`; fill guards for any family that accumulates observed n-fold rework evidence; or a new artifact validator that needs a hook `run_changed_artifact_validator` cannot express, since forking `main()` again is what re-opens the polarity risk.

### D29. Quality-Signal Scorecard Helper Script And Metric-Only Closeout Guard

- Question: Should the quality-signal scorecard ([quality-signal-scorecard.md](../skills/public/quality/references/quality-signal-scorecard.md), the #356 resolution) gain a helper script that renders a candidate scorecard skeleton from known adapter gates, and a closeout guard validator that refuses metric-only rationale for structural cleanup?
- Current choice: Defer both; ship the reference plus mandatory wiring from the inventory-dispatch structural-signals path, the testability/duplicate-pressure path, and the quality SKILL anchor. The issue's Desired Outcome requires the scorecard judgment itself; the helper and guard are its "Possible Direction" items.
- Why now: The scorecard rows are repo-judgment fields (behavior value, ownership, stop condition) that a renderer cannot fill, so a skeleton helper saves little until the prose contract has consumer mileage; a rationale-classifying guard is a content classifier, which the repo's deterministic-floor philosophy avoids until an observed gaming instance shapes a narrow checkable form.
- Impact surfaces: [skills/public/quality/references/quality-signal-scorecard.md](../skills/public/quality/references/quality-signal-scorecard.md), [skills/public/quality/references/inventory-dispatch.md](../skills/public/quality/references/inventory-dispatch.md), quality closeout validators.
- Reopen trigger: A consumer-repo run skips the scorecard despite the wiring (discovery failure), or a quality closeout ships metric-only rationale past review (guard-shaped failure), or an operator asks for the rendered skeleton.

### D30. dup-ratchet id-rotation — RESOLVED

Newness is keyed on a content fingerprint ([`nose_fingerprint_lib`](../skills/public/quality/scripts/nose_fingerprint_lib.py), algo v2; baseline schema v3), so a pure line-shift produces no "new" family; a membership reduction is an advisory naming `--accept-rotation`, a grow still hard-blocks. Residuals S4-Defer-1..3 and their status: [spec Slice 4](../charness-artifacts/spec/boy-scout-dup-ratchet.md); gate behavior: [dup-ratchet.md](../skills/public/quality/references/dup-ratchet.md).

### D34. Same-observer `confirmed` on announcement delivery — DECLINED

[`record_announcement.py`](../skills/public/announcement/scripts/record_announcement.py) enforces the presence of a typed verification record, not its independence (operator, 2026-07-04; [pr419 closeout](../charness-artifacts/critique/2026-07-04-pr419-adversarial-fix-closeout.md)). Reopen: a self-attested `confirmed` later proves wrong, or the delivery-verification seam is touched.

### D35. Release distinct-channel probe shape-match — DECLINED

`_probe_matches_release_view_shape` in [`publish_release_post_create.py`](../skills/public/release/scripts/publish_release_post_create.py) matches leading tokens only; the default HTTPS-fetch channel is already distinct (operator, 2026-07-04; [pr419 closeout](../charness-artifacts/critique/2026-07-04-pr419-adversarial-fix-closeout.md)). Reopen: a same-proxy probe is recorded as a distinct-channel confirmation, or the matcher is touched.

### D36. Exemption advisory on the commit-msg close carrier — RESOLVED

`review_advisory_for_classification` has one carrier-neutral owner, [issue_closeout_rung1_floors.py](../skills/public/issue/scripts/issue_closeout_rung1_floors.py); [`check_issue_closeout_commit_msg.py`](../scripts/gates/check_issue_closeout_commit_msg.py) surfaces it as a non-blocking `review_advisory` ([critique](../charness-artifacts/critique/2026-07-04-d36-close-exemption-advisory-single-source.md)). Reopen: a commit-message close self-classifies `question`/`decision-needed` and skips the floors unnoticed, or the shared advisory is touched.

### D38. Promotion gate for decaying retro lessons

- Question: should a correct retro lesson that never reaches a durable contract be
  detectable, rather than depending on the same rolling digest that let it decay?
- The single instance was fixed first: the reviewer result-delivery rule lives in [fresh-eye-subagent-review.md](../skills/shared/references/fresh-eye-subagent-review.md) `## Result Delivery`, pinned by [test_reviewer_result_delivery.py](../tests/quality_gates/test_reviewer_result_delivery.py) and enforced by the `Delivery state` floor in [validate_critique_artifacts.py](../scripts/review/validate_critique_artifacts.py).
- Resolved 2026-09-03: the promotion contract is [lesson-graduation.md](../skills/shared/references/lesson-graduation.md); the first joint review is [781-lesson-dispositions.md](../charness-artifacts/goal-runs/775/781-lesson-dispositions.md). Residual: a Next Improvement nobody tags is invisible to the ledger; [`check_lesson_ledger.py`](../scripts/lessons/check_lesson_ledger.py) names unseeded classes.

### D39. Changed-line proof freshness fingerprint is blind to `tests/`

- Question: Should the coverage freshness marker the release-final changed-line gate trusts digest the test files whose presence the coverage actually depends on, or stay scoped to mutation-pool files only?
- Current choice: Defer. The marker stays pool-scoped; the risk is recorded rather than repaired inside an issue-resolution slice.
- Why now: [changed_pool_fingerprint](../scripts/mutation/mutation_changed_files_lib.py) digests only `changed_pool_files_vs_base(...)`, and the mutation pool globs in [sample_mutation_files.py](../scripts/mutation/sample_mutation_files.py) do not include `tests/`. A tests-only slice therefore moves the fingerprint by zero bits, so a `reports/mutation/test-coverage.json` produced BEFORE the new tests existed still satisfies `--require-fresh-coverage` and is accepted as fresh. Surfaced as finding C6 of [the #464 resolution critique](../charness-artifacts/critique/2026-07-28-issue-464-changed-line-coverage-recurrence.md). <!-- reproduction-source -->
- Why deferral is right at the time: for a change that ADDS tests the failure direction is self-announcing — stale coverage shows the changed lines still uncovered, so the consumer raises a loud false FAIL, not a false pass. The dangerous direction is a change that DELETES or renames tests while the marker still matches, which is a gate design question (what content the freshness claim is actually about) rather than a one-line widening, and widening the digest to all of `tests/` would invalidate the marker on every unrelated test edit and make the release-final producer pay again.
- Impact surfaces: [mutation_changed_files_lib.py](../scripts/mutation/mutation_changed_files_lib.py), [check_changed_line_mutation_coverage.py](../scripts/mutation/check_changed_line_mutation_coverage.py), [run-quality.sh](../scripts/run-quality.sh) (the `--require-fresh-coverage` consumer), [mutation_coverage_producer.py](../scripts/mutation/mutation_coverage_producer.py).
- Reopen trigger: a changed-line gate verdict that passes against coverage produced before the tests it credits, or any slice that removes tests from a mutation-pool file's proof set.

### D40. Changed-line proof has one release-final owner

- Question: Should a lane that runs before a landing refuse a push whose changed lines were never proven — and if so, which one pays: a mandatory ~10-minute local coverage producer, or branch protection forcing the PR path?
- Current choice: the release-final lane owns the blocking proof — `run-quality.sh --release` runs [release_changed_line_coverage.py](../scripts/mutation/release_changed_line_coverage.py) once with `--refuse-unestablished`, so a partial or unestablished result fails the release ([pushing](./development.md#pushing)); default/full lanes do not claim to have run it.
- Still open: whether any pre-landing lane should BLOCK an unproven changed line; the operator chose the non-blocking option on 2026-08-06 ([goal record](../charness-artifacts/goals/2026-08-06-make-a-verdict-state-the-scope-it-measured.md)).
- Non-claim: this repairs the SIGNAL, not the coverage. A changed pool file that maps to no standing test is still unanalyzed before the push, and remote CI is still the thing that catches it.
- Impact surfaces: [run-quality.sh](../scripts/run-quality.sh) (the `--skip-if-no-coverage` flag set), [check_changed_line_mutation_coverage.py](../scripts/mutation/check_changed_line_mutation_coverage.py), [quality-core.yml](../.github/workflows/quality-core.yml), [mutation-tests.yml](../.github/workflows/mutation-tests.yml), repository branch-protection settings (not in tree).
- Reopen trigger: a ninth instance of the class, or an operator decision to pay one of the tolls.

### D41. The coverage mapper cannot see a bare top-level import of a repo script

- Question: Should `tests_referencing_paths` resolve a changed script from a bare `import <stem>` / `from <stem> import ...`, or should the repo require the dotted `from scripts import <stem>` form in tests?
- Current choice: Defer the mapper change; fix the call sites. The two tests found this way now use the dotted form, and the convention is the cheaper half.
- Why now: [suggest_mutation_coverage_command.py](../scripts/mutation/suggest_mutation_coverage_command.py) maps tests by dotted module name, so a bare `import <stem>` (which works at runtime because a conftest puts `scripts/` on `sys.path`) matches none of its patterns and the gate reports covered lines as uncovered.
- Why deferral is right at the time: the obvious widening (match `import <stem>` for every pool file's stem) is a mapper change on a surface that now feeds a BLOCKING gate, so it owes its own two-round review — and it over-matches in a way the existing patterns do not, since a bare stem can collide with a real top-level package name. The direction is safe (an extra test only adds measured coverage) but the cost lands on every push, and the same effect is available for free by writing the import the way the rest of the repo does.
- Impact surfaces: [suggest_mutation_coverage_command.py](../scripts/mutation/suggest_mutation_coverage_command.py), [release_changed_line_coverage.py](../scripts/mutation/release_changed_line_coverage.py), any test importing a `scripts/` module by bare name.
- Reopen trigger: a third changed file reported uncovered while a test demonstrably covers it, or a slice where converting the call sites is not available (a vendored or generated test).

### D42. Should a claim-time proof gate that established nothing exit 3 rather than 0?

- Question: `check_mutation_run_proof.py --claim changed-line --base-sha <sha>` with no sample manifest establishes that the run's TRIGGER could evaluate the claim, never that it evaluated any file. Should that exit 3 (`UNPROVEN`, non-blocking) instead of 0 with a stderr warning?
- Current choice: exit 0; the verdict carries `range_established` and the hedge prints to stderr on both range and conclusion. Operator-confirmed 2026-07-30 ([goal record](../charness-artifacts/goals/2026-07-29-close-the-armed-changed-line-pre-push-lane-s-known-holes-pin.md)).
- Impact surfaces: [check_mutation_run_proof.py](../scripts/mutation/check_mutation_run_proof.py), [mutation-testing.md](../skills/public/quality/references/mutation-testing.md), [run-quality.sh](../scripts/run-quality.sh) `UNESTABLISHED_CAPABLE_LABELS` if it ever becomes a queued label.
- Reopen trigger: a citation of a `range_established: false` or `conclusion_established: false` run as changed-line proof in any closeout, issue, or release note; or this gate becoming a queued `run-quality.sh` label.

### D43. Should the loose-bar advisory be per-label rather than one global factor?

- Question: `BUDGET_SLACK_FACTOR = 3.0` in [runtime_budget_lib.py](../skills/public/quality/scripts/runtime_budget_lib.py) is a single module constant applied to every label on every profile. Should it become per-label or per-profile so a bar that cannot fail is reported?
- Current choice: `BUDGET_SLACK_FACTOR` stays global; the advisory divides by `max_recent_elapsed_ms`, so a bar sized from a documented range cost rather than an observed worst run is invisible to it — the one such bar (`run-quality-read-only`) is a recorded decision in [quality-adapter.yaml](../.agents/quality-adapter.yaml), not a blind spot. Operator-confirmed 2026-07-30 ([goal record](../charness-artifacts/goals/2026-07-29-close-the-armed-changed-line-pre-push-lane-s-known-holes-pin.md)).
- Impact surfaces: [runtime_budget_lib.py](../skills/public/quality/scripts/runtime_budget_lib.py), [quality-adapter.yaml](../.agents/quality-adapter.yaml), [check_runtime_budget.py](../skills/public/quality/scripts/check_runtime_budget.py).
- Reopen trigger: a bar that was NOT a recorded decision goes unreported by the advisory and is later found to be unfailable; OR a bar goes stale in the TIGHT direction and hard-fails with nothing regressed. The second clause exists because this session's actual discovery was tight, not loose (`run-quality-read-only` at 58500 against a post-lane latest of 90618), and the original trigger would not have caught it.

### D44. Per-line subprocess-only path in `blocking_targets` — DECLINED (2026-08-01)

- Question: Should the changed-line gate's `blocking_targets` payload report, per blocked line, that the file's existing tests reach it only via `subprocess`/`run_script`?
- Current choice: declined; the premise ("reached only via subprocess explains a BLOCK") was falsified by measurement, and the honest residue is [subprocess_only_coverage_advisory.py](../scripts/mutation/subprocess_only_coverage_advisory.py), whose docstring owns the mechanism, the control measurement, and its `silence_means`. No test→line map exists, so a per-line claim is not establishable.
- Open residual: per blocked file, WHICH tests reference it and how (remedy information) is computed by `_advisory` and reduced to a count; a path reaching the advisory via `blocking` alone gets `blocked_lines: []`, and the single-key entrypoints take no `blocking` argument.
- Impact surfaces: [check_changed_line_mutation_coverage.py](../scripts/mutation/check_changed_line_mutation_coverage.py), [subprocess_only_coverage_advisory.py](../scripts/mutation/subprocess_only_coverage_advisory.py) and their plugin mirrors.
- Reopen trigger: a measured case where a blocked line's only exercise is an environment-inheriting, in-repo spawn and coverage still misses it (a THIRD mechanism, not a re-argument of the two known ones); or a BLOCK the advisory stayed silent on that is later diagnosed as an unattributed-child artifact; or a test→line map that makes the per-line claim establishable; or the candidate-NAME residual above is wanted by a session that has just spent a cycle re-deriving it by hand.

### D45. Should `run-quality.sh` arm `--require-evaluated-scope` on the CI/local parity gate?

- Question: charness's own two workflows BOTH carry a `# charness:gate-policy` exemption marker, so [inventory_ci_local_gate_parity.py](../skills/public/quality/scripts/inventory_ci_local_gate_parity.py) evaluates **zero jobs** in this repo while [run-quality.sh](../scripts/run-quality.sh) asserts `--require-empty-parity-issues` and reports PASS. Should the runner also pass the new `--require-evaluated-scope`, turning that green into a refusal?
- Current choice: **Defer — the flag ships, unwired.** The S26/S30 slice made the zero-denominator legible (`workflows_not_exempt`, `jobs_evaluated`, a NOTE line, and the flag), and pinned the posture in `test_real_repo_workflows_or_zero_parity_issues` so a third workflow fires a test. It did not arm the refusal.
- Why now: found while closing sweep rows S26/S30 on 2026-08-01, verified by running the gate against this repo (`--detail`: two workflows, both `exempt: true`, `jobs: []`). This is S31's consequence rather than S31 itself — S31 is that a comment INSIDE the audited file grants the exemption, which stays open.
- Why deferral is right at the time: arming it makes this repo's broad quality lane permanently red with no honest remediation short of deleting a legitimate `scheduled-deeper-check` exemption, and the alternative repair — moving the exemption declaration out of the audited file into the adapter, which is the north-star "different channel" answer — is a contract change for every consumer repo and deserves its own slice, not a ride-along on a defect repair. Choosing which toll to pay is the same class of call as [D40](#d40-changed-line-proof-has-one-release-final-owner), and it is the owner's.
- Non-claims: the NOTE line is legibility, not teeth — it is one line in an ~82-gate run, and the slice does not claim anyone will read it. Nothing here narrows S31's self-declaration defect. A second new flag, `--require-established-gate-match`, is NOT part of this deferral: round 2 established it is a no-op on this repo today (every workflow is exempt, so the bucket is empty), so it was armed at the commit boundary in [staged_commit_gate_plan.py](../scripts/staged_commit_gate_plan.py) rather than deferred. `run-quality.sh` still does not pass it, for the same reason it does not pass `--require-evaluated-scope`: the broad lane runs in consumer repos too, and a composite-action CI is an honest shape there.
- Impact surfaces: [run-quality.sh](../scripts/run-quality.sh), [inventory_ci_local_gate_parity.py](../skills/public/quality/scripts/inventory_ci_local_gate_parity.py), [ci_local_gate_parity_lib.py](../skills/public/quality/scripts/ci_local_gate_parity_lib.py), [maintainer-local-enforcement.md](../skills/public/quality/references/maintainer-local-enforcement.md), `.github/workflows/*.yml`.
- Named remedy premise:
  - Remedy: move the exemption declaration from the workflow into the adapter.
  - Premise: an adapter-declared exemption channel already exists for this reader.
  - Evidence channel: read [`ci_local_gate_parity_lib.py`](../skills/public/quality/scripts/ci_local_gate_parity_lib.py) and the quality adapter contract.
  - Observation: the reader accepts workflow text only; the adapter has related fields but no exemption input.
  - Downstream decision delta: keep the deferral, but reshape the remedy from a rewire into a new adapter seam with precedence rules.
  - Status: falsified
- Reopen trigger: a CI/local parity escape that this repo's own green did not catch; or S31 being worked, since moving the exemption to the adapter changes what "evaluated" can mean; or a third charness workflow landing.

### D47. Should inventory-field engagement require a value marker?

- Question: Should `_engages` in [validate_inventory_consumption.py](../scripts/gates/validate_inventory_consumption.py) also require a value marker so ordinary-English field names are not engaged by incidental prose?
- Current choice: **Defer — measure recorded, refusal not armed.** Named remedy (per-field distinctiveness in the inventory declaration) **withdrawn** as unbuildable: declaring names non-distinctive spares the reviews; declaring them distinctive makes the rule a measured-zero no-op.
- Measurement: [2026-08-12 snapshot](../charness-artifacts/probe/2026-08-12-inventory-marker-rule-snapshot.json) (`sha256: ac63f8a54a558217cebde320f02d4915d10e6bab538c3df22ff6e1397083f62d`), pinned by [test_inventory_marker_rule_measurement.py](../tests/test_inventory_marker_rule_measurement.py). Counts live in that payload. The snapshot does not license arming or consumer claims; unmodelled cases live in [measure_inventory_marker_rule.py](../scripts/gates/measure_inventory_marker_rule.py).
- Reopen trigger: a quality artifact passing the floor on incidental prose and later found not to have consumed the inventory; or per-field distinctiveness landing in the declaration; or the currently-refused artifacts being rewritten. A new decision must run `python3 scripts/gates/measure_inventory_marker_rule.py --repo-root . --json` on its then-current corpus and record a **new** dated snapshot with its own SHA-256; do not overwrite this one.

### D48. Should an absent release surface be drift without a self-authored declaration?

- Question: [current_release.py](../skills/public/release/scripts/current_release.py) turns
  an ABSENT generated release surface into drift only for surfaces the repo's own
  `required_release_surfaces` names, and that field defaults to empty. Should absence be
  drift by default, or derived from a channel the audited repo does not author?
- Current choice: declared-only, default empty (operator, 2026-08-01). [`current_release.py`](../skills/public/release/scripts/current_release.py) reports `absence_corroboration` and `undeclared_absent_surfaces`; `publish_release_preflight.release_surface_blocker` refuses a publish while it reads `uncorroborated` (`drift` unchanged, so read-only status reddens no unshipped lane). A PRESENT surface that is `unreadable`/`no-version` is drift without any declaration and is exemptable via the second adapter field `unpublished_release_surfaces` (`required_release_surfaces` means "must exist" and cannot be the remedy for not publishing). Pinned by [test_absent_input_is_not_a_matching_input.py](../tests/quality_gates/test_absent_input_is_not_a_matching_input.py).
- **Not warned earlier, and it cannot be:** `plan_release_run` runs BEFORE the sync command, so the gate sits immediately after sync, where an absent surface means the sync did not write it; the refusal lands after the version bump has already rewritten the worktree.
- **Known gap, not closed:** [`publish_release_resume.py`](../skills/public/release/scripts/publish_release_resume.py) reaches `create_release` without
  the release-surface check, so a surface deleted or corrupted between a failed attempt
  and the resume still reaches publish unchecked. Pre-existing for `drift` too. Adding
  the gate there was attempted and reverted: every resume fixture exercises a repo with
  no generated tree, so it is a contract change with its own blast radius rather than a
  line this slice was entitled to add.
- Named remedy premise:
  - Remedy: derive the expected release-surface set from sync command output.
  - Premise: the sync output names every generated surface in the vocabulary consumed by [`current_release.py`](../skills/public/release/scripts/current_release.py).
  - Evidence channel: read [`sync_root_plugin_manifests.py`](../scripts/plugin_export/sync_root_plugin_manifests.py) output fields and [`current_release.py`](../skills/public/release/scripts/current_release.py) surface vocabulary.
  - Observation: sync reports the plugin root as a directory, omits two surfaces, and uses no path-to-key mapping for the release vocabulary.
  - Downstream decision delta: withdraw the derivation repair; retain declared-only status with explicit uncorroborated publish refusal.
  - Status: withdrawn
- Non-claims: the declaration is unverified against reality; nothing checks that a
  declared surface is one the sync command actually produces. This entry does not narrow
  S31.
- Impact surfaces: [current_release.py](../skills/public/release/scripts/current_release.py),
  [release resolve_adapter.py](../skills/public/release/scripts/resolve_adapter.py),
  [adapter-contract.md](../skills/public/release/references/adapter-contract.md),
  [release-adapter.yaml](../.agents/release-adapter.yaml).
- Reopen trigger: a release published with a surface missing that the declaration did not
  cover; or the sync command gaining a machine-readable list of what it writes; or S31
  being worked, since moving a declaration out of the audited surface is the same question.

### D50. `<plugin-dir>/` — RESOLVED (2026-08-04)

Adopted for the trigger the deferral named ([#479](https://github.com/corca-ai/charness/issues/479)'s `<repo-root>/skills/public/...` family needs the installed layout). `<plugin-dir>/` is the only spelling meaning the installed plugin's own tree; [`native_gate_lib.py`](../scripts/native_gate_lib.py) `... plugin-refs` resolves every such reference against the generated `plugins/<pkg>/` package and refuses a dangling one, and `$PLUGIN_DIR` is documented in the shared bootstrap reference for the shell case. No host substitutes the placeholder textually; it stays agent-resolved ([live probe](../charness-artifacts/probe/2026-09-03-plugin-dir-placeholder-live-probe.md)).

### D51. Release branch/CI barrier and quality-gate runtime

- Question: How should the release helper preserve the branch-push → different
  observer CI barrier before tag/public publication, while making the measured
  quality-gate runtime actionable without weakening proof floors?
- Current choice: Defer the helper state-machine repair and runtime treatment
  as one explicit follow-up. The v3.2.0 closeout was run as a manually split
  branch-push → CI readback → tag → independent readback sequence; its measured
  gate runtimes are in the [2026-08-04 session retro](../charness-artifacts/retro/2026-08-04-session-retro.md)
  and are quality-debt signals, not permission to narrow proof.
- Why now: The release helper's natural ordering would otherwise allow tag
  publication before the remote branch's CI result, and the recurring runtime
  signal needs an owner that can optimize structure rather than ask operators
  to accept a terminal green.
- Impact surfaces: [publish_release_execute.py](../skills/public/release/scripts/publish_release_execute.py),
  [run-quality.sh](../scripts/run-quality.sh), [design-north-star.md](./design-north-star.md),
  and release closeout artifacts.
- Reopen trigger: the next release-helper change, or a measured quality-gate
  runtime regression that supplies a concrete optimization candidate.

### D54. Should a per-gate runtime budget measure the gate's own work rather than contended wall clock?

- Question: the budget grades recorded wall-clock (`elapsed_ms`, verdict on `median_recent_elapsed_ms`) of a concurrently queued command, so it measures contention, not gate work. Should it measure the gate's own work?
- Current choice: wall-clock stays telemetry; [`run-quality.sh`](../scripts/run-quality.sh) passes `--advisory` to [`check_runtime_budget.py`](../skills/public/quality/scripts/check_runtime_budget.py), which is blocking only on an explicit owner invocation; adapter/profile/label-universe errors remain blocking.
- Non-claims: the mismatch is not fixed; no CPU-time or contention-normalized metric exists; 4-core and aarch64 profile values were not re-derived.
- Impact surfaces: [quality-adapter.yaml](../.agents/quality-adapter.yaml) (four
  `runtime_budgets` blocks), [record_quality_runtime.py](../scripts/gates_support/record_quality_runtime.py),
  [runtime_budget_lib.py](../skills/public/quality/scripts/runtime_budget_lib.py),
  and [run-quality.sh](../scripts/run-quality.sh)'s concurrent queue.
- Reopen trigger: a real correctness or safety decision becomes dependent on latency;
  a machine-independent timing metric becomes available; or an owner explicitly
  chooses to introduce a separately scoped performance SLO.
