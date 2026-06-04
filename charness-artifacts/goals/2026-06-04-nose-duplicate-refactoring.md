# Achieve Goal: Nose duplicate refactoring

Status: complete
Created: 2026-06-04
Activation: `/goal @charness-artifacts/goals/2026-06-04-nose-duplicate-refactoring.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: complete.
- Next action: no goal work remains; future `jscpd`/`nose` support-binary work
  should start as a new scoped goal or issue.
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
| 1 | Lock baseline and scope | Avoid optimizing against stale `nose 0.2.0` or raw `jscpd` output | `nose 0.4.0` version, top-family inventory, docs updated to defer `jscpd` | done |
| 2 | Remove portable bootstrap duplication where a shared path is provably safe | Largest `nose` family is skill runtime bootstrap across public skill scripts | shared helper or generator path, source/plugin execution tests, reduced `nose` family | done |
| 3 | Consolidate adapter resolver/validator skeletons | Adapter families are the next largest actionable duplication | common adapter validation helpers or templates, focused resolver tests, reduced `nose` family | done |
| 4 | Preserve or narrow `check_duplicates.py` to document near-copy ownership | Do this only after code-clone cleanup clarifies what Python near-file coverage would be lost | tests proving Markdown near-copy behavior; explicit non-claim or retained coverage for helper-script near-file checks | done |
| 5 | Reassess post-cleanup `jscpd` signal | Only after actual cleanup can raw token clone signal be judged fairly | before/after `jscpd` summary, recommendation to defer/add wrapper/skip | done |

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

### Slice 1: Baseline and bootstrap loader contraction

- Objective: Lock the nose 0.4.0 duplicate baseline and remove the largest portable per-script bootstrap duplication that is safe before tackling adapter resolver families.
- Why this approach: The baseline prevents optimizing against stale jscpd or nose output. The per-script ancestor bootstrap preamble was a real high-cardinality code clone, but direct source/plugin execution still requires a tiny local preamble because arbitrary skill scripts cannot import repo modules until the bootstrap has located the repo root.
- Commits: same closeout commit as this slice log.
- What changed: Recorded raw nose baseline JSON beside the goal artifact; changed public skill and plugin mirror scripts from importlib.util module loading to runpy + SimpleNamespace bootstrap loading; further contracted the repeated loader body; added goal JSON surface coverage; fixed handoff issue reference parsing for #285-#289 and issue_tool.py --number arguments exposed by the broad test run.
- Alternatives rejected: Did not introduce jscpd in this slice. Did not claim that all skill_runtime_bootstrap loaders changed: root shims still use importlib.util. Did not remove the final 5-line per-script bootstrap clone because that is the portability boundary for independent script execution.
- Targeted verification: nose 0.4.0 baseline: /home/hwidong/codes/nose/target/release/nose scan scripts skills/public skills/support --mode syntax,semantic,near --threshold 0.70 --min-lines 18 --min-tokens 24 --sort extractability --top 0 --format json > charness-artifacts/goals/2026-06-04-nose-duplicate-refactoring-nose-baseline.json; baseline 230 families, top bootstrap family 86 members / 1020 dup_lines. After slice: same scan > /tmp/charness-nose-after-slice.json; 225 families, top remaining bootstrap family 81 members / 400 dup_lines. ruff check passed; representative source/plugin env -u PYTHONPATH -u CHARNESS_REPO_ROOT direct executions passed; packaging, skill, surface, markdown, secrets, duplicate, policy, integration, py_compile, plugin import smoke, focused pytest passed. Broad pytest initially found handoff range/--number parsing gap; fixed and focused tests passed.
- Test duplication pressure: check_duplicates.py remains the document near-copy gate and passed with --fail-on-match. nose remains advisory evidence; this slice reduces its top bootstrap signal but leaves adapter resolver families as the next target. Cautilus planner reported next_action none and must_ask_before_running true; no evaluator was run because this slice changed runtime bootstrap mechanics, not prompt behavior or skill semantics.
- Critique: Medium fresh-eye runtime reviewer found no runtime/portability regression and independently ran source/plugin direct execution checks. Medium evidence reviewer found blockers in stale goal logging and unmatched baseline JSON; fixed by adding goal-evidence-json surface coverage and writing this slice log. Evidence reviewer also noted success-semantics coverage gap; parent added source/plugin direct execution and plugin import smoke evidence.
- Off-goal findings: The broad repo-python test exposed a pre-existing live handoff parser blind spot for issue ranges and issue_tool.py --number references; fixed because it blocked the changed-surface gate and improves handoff structure.
- Lessons carried forward: For future nose-driven refactors, record raw baseline evidence before editing and update surfaces when the evidence format is not already covered. Keep claims narrow: per-script bootstrap loader contraction is not the same as replacing every root bootstrap shim.
- Metrics: nose families 230 -> 225; bootstrap duplicate lines 1020 -> 400; changed-surface unmatched paths 1 -> 0 after goal-evidence-json surface.

### Slice 3: Adapter resolver envelope consolidation

- Objective: Remove the repeated adapter discovery, fallback-warning, artifact-path, and JSON envelope code from the next actionable `nose` families while keeping per-skill validation semantics local.
- Why this approach: The high-value duplication was not each skill's field policy. It was the repeated adapter search/envelope contract across public skill resolver scripts. Centralizing that contract in `scripts/simple_skill_adapter_lib.py` preserves plugin/source portability because every public resolver still keeps the tiny runtime bootstrap and local validation function.
- Commits: same closeout commit as this slice log.
- What changed: Added `adapter_candidates`, `searched_adapter_paths`, `find_adapter`, `artifact_path`, `record_artifact_pattern`, and `load_adapter_contract` to the shared adapter helper. Refactored `debug`, `gather`, `hitl`, `impl`, `retro`, and `release` public resolver scripts to call the shared contract, then synced the `plugins/charness` mirrors.
- Alternatives rejected: Did not force `achieve`, `critique`, `find-skills`, `issue`, `quality`, `create-skill`, `announcement`, or `narrative` through the generic helper in this slice because their resolver shapes either have lower duplicate pressure or more bespoke semantics. Did not move per-skill validation into a generic schema layer because that would hide adapter intent only to improve a duplicate score.
- Targeted verification: `ruff check` and `py_compile` passed for the shared helper plus the six touched public resolvers. Focused pytest passed for gather provider, release backend/publish, and retro memory coverage. Direct source and `plugins/charness` resolver JSON smoke tests passed for all six skills, including `env -u PYTHONPATH -u CHARNESS_REPO_ROOT` plugin execution. `check_export_safe_imports.py`, `check_plugin_import_smoke.py`, `validate_packaging.py`, `validate_packaging_committed.py`, `validate_skills.py`, `check_skill_ownership_overlap.py`, `validate_public_skill_validation.py`, `validate_public_skill_dogfood.py`, `validate_adapters.py`, `validate_integrations.py`, `sync_support.py --json`, and `update_tools.py --json` passed. `check_duplicates.py --fail-on-match --require-git-file-listing --json` returned no matches.
- Nose evidence: Before this slice, the advisory `nose 0.4.0` scan over `scripts skills/public skills/support` reported 225 families. After the slice it reported 222 families. The raw count moved only slightly because the remaining resolver import/main skeletons still cluster, but the large `load_adapter` families disappeared from the top reported families: the `find_adapter` family dropped from 10 members / 54 duplicate lines to 4 members / 18 duplicate lines, and the debug/gather/hitl/release plus impl/retro adapter-load families no longer appeared in the top 16 inspected results.
- Critique: Medium fresh-eye reviewer found no behavior or regression blockers, checked the shared resolver contract and plugin mirror, confirmed gather/release/HITL/impl/retro special payloads still land in the intended top-level or `data` fields, and smoke-ran all six source and plugin resolver paths. The reviewer also tested missing-adapter and fallback-adapter cases in a temp repo.
- Test duplication pressure: `check_duplicates.py` remains the whole-file/document near-copy gate. `nose` remains advisory for refactoring inventory. This slice reduces meaningful adapter contract duplication but makes no zero-clone claim; remaining import/bootstrap/main skeleton families are still candidates only if a later slice can keep independent plugin execution clear.
- Lessons carried forward: Prefer extracting the shared envelope around adapter resolution before extracting field validation. Count-based `nose` deltas need interpretation: a smaller number of higher-cardinality skeleton families can mask removal of more semantically important duplicated bodies.
- Metrics: nose families 225 -> 222; adapter `find_adapter` duplicate lines 54 -> 18; changed files 14; net source/plugin mirror diff 456 insertions / 888 deletions before goal-log closeout.

### Slice 4: Document near-copy gate naming and scope

- Objective: Make the hard duplicate gate match the user's intended role: catch near-identical checked-in Markdown, skill, reference, and README surfaces, while leaving code clone inventory to `nose` and later `jscpd` reassessment.
- Why this approach: The prior `scripts/check_duplicates.py` name and `DEFAULT_PATTERNS` implied a broad duplicate detector, but the algorithm is whole-file Ratcliff/Obershelp-style text similarity at threshold 0.98. That is the right shape for near-copy documents, not for Python block clones. The canonical command is now `scripts/check_doc_near_duplicates.py`; `scripts/check_duplicates.py` remains as a compatibility wrapper.
- Commits: same closeout commit as this slice log.
- What changed: Renamed the canonical checker to `check_doc_near_duplicates.py`, narrowed its patterns to `docs/*.md`, skill/support/shared reference Markdown, public/support `SKILL.md`, and `README.md`, and changed the `run-quality.sh` phase plus docs-only pre-push label to `check-doc-near-duplicates`. Synced plugin mirrors, renamed runtime budget keys in `.agents/quality-adapter.yaml`, updated strategy/operating docs, and replaced the boundary-bypass baseline key for the renamed script.
- Coverage tradeoff: Before narrowing, the checker scanned 627 substantive tracked files: 400 Python and 227 Markdown. The old broad scope and the new document scope both reported 0 duplicate pairs at threshold 0.98 in the current tree. The removed future coverage is only whole-file near-copy Python/helper-script blocking; this goal intentionally assigns Python clone cleanup to advisory `nose` refactoring inventory and the later `jscpd` decision, not to the document near-copy hard gate.
- Targeted verification: `python3 scripts/check_doc_near_duplicates.py --repo-root . --fail-on-match --require-git-file-listing --json`, legacy `scripts/check_duplicates.py`, and the plugin mirror equivalents all returned `[]`. Focused tests passed for document near-copy rejection, gitignored docs, helper-script exclusion, and legacy wrapper scope. `CHARNESS_QUALITY_LABELS=check-doc-near-duplicates ./scripts/run-quality.sh --read-only` passed. `pytest` focused quality-runner/docs/mutation/runtime-budget/bootstrap set passed with 137 tests. `check_boundary_bypass_ratchet.py` passed after the rename baseline update with 95 candidates, one fewer than the prior baseline. Packaging, docs, markdown, secrets, Cautilus proof validation, adapter validation, mutation workflow test/GitHub Actions check, maintainer hook validation, integrations, support/tool dry-runs, ruff, Python length, and attention-state visibility checks passed. Scenario review: the prompt-affecting adapter paths changed only runtime-budget/phase label strings; Cautilus planner reported `next_action: none`, so deterministic validation owned closeout and no live evaluator run was made.
- Nose evidence: Maintainer-local `nose 0.4.0` still reports 222 families after this slice, matching the post-adapter slice count. This slice does not claim code-clone reduction; it removes the misleading code-scan responsibility from the whole-file document gate.
- Critique: Medium fresh-eye reviewer found no behavior or regression blockers. The reviewer checked root/plugin run-quality labels, docs-only pre-push label, runtime budgets, canonical document scope, legacy wrapper dispatch, boundary-bypass rename legitimacy, and source/plugin command output. Reviewer recommended adding a wrapper compatibility test; parent added it.
- Test duplication pressure: This slice improves duplicate-test pressure by making the deterministic gate's scope explicit instead of pretending a whole-file document matcher is the code-clone gate. The next slice can compare `jscpd` against the cleaned code baseline without conflating it with Markdown near-copy behavior.
- Lessons carried forward: Rename-induced boundary-bypass changes should be treated as key migration, not new behavior, and proved with the ratchet. Keep compatibility wrappers when operator muscle memory or older local commands may still call the previous script name.
- Metrics: scanned substantive files 627 -> 227 for the hard near-copy gate; current hard-gate duplicate pairs remained 0 -> 0; boundary-bypass candidates 96 -> 95 after the rename/scope change; `nose` families remained 222.

### Slice 5: Post-cleanup jscpd signal reassessment

- Objective: Reassess whether `jscpd` should be introduced after the `nose`-driven cleanup and document near-copy narrowing.
- Why this approach: The user explicitly changed the plan to avoid adding `jscpd` until after `nose` cleanup. This slice compares post-cleanup `jscpd` signal against the cleaned baseline without changing the standing gate.
- Tooling: `npx --yes jscpd --version` reported 4.2.4. This is maintainer-local analysis evidence, not a Charness support-binary install/update proof.
- Evidence: `npx --yes jscpd scripts skills/public skills/support --format python --min-lines 18 --min-tokens 50 --reporters json --output /tmp/charness-jscpd-code --exitCode 0 --noTips --silent` found 87 exact clones / 2110 duplicated lines across 409 Python sources (3.05%). Classification: 58 skill-runtime bootstrap preamble clones / 1361 lines, 9 adapter resolver skeleton clones / 225 lines, 6 repo runtime bootstrap/import preamble clones / 163 lines, plus smaller CLI/helper shapes and 9 other exact blocks / 276 lines. This report is not pure false-positive noise: it is dominated by short bootstrap/preamble/import/adapter skeleton pairs, with a few real refactoring candidates mixed in.
- Document comparison: `npx --yes jscpd docs skills/public skills/support README.md --format markdown --min-lines 18 --min-tokens 50 --reporters json --output /tmp/charness-jscpd-docs --exitCode 0 --noTips --silent` found 1 exact Markdown clone / 23 duplicated lines between `skills/public/achieve/references/goal-artifact.md:43-66` and `skills/public/achieve/scripts/goal_artifact_template.md:27-50`. This is template/reference mirroring and does not replace whole-file near-copy detection.
- Mixed comparison: `npx --yes jscpd scripts skills/public skills/support docs README.md --format python,markdown --min-lines 18 --min-tokens 50 --reporters json --output /tmp/charness-jscpd-mixed --exitCode 0 --noTips --silent` found 88 clones / 2133 duplicated lines, which is the source-only result plus the one template/reference Markdown clone.
- Higher-floor comparisons: `npx --yes jscpd scripts skills/public skills/support --format python --min-lines 40 --min-tokens 80 --reporters json --output /tmp/charness-jscpd-code-40 --exitCode 0 --noTips --silent` found 3 exact Python clones / 188 duplicated lines: two blocks shared by `scripts/check_init_repo_rename.py` and `scripts/check_premortem_rename.py`, plus one shared by `scripts/report_usage_episodes.py` and `scripts/validate_usage_episodes.py`. `--min-lines 30 --min-tokens 100` found 9 clones / 398 duplicated lines, adding a small set of resolver/bootstrap and dogfood helper candidates. These are real follow-up candidates, but they are a small inventory rather than a repo-wide hard-gate-ready result.
- Strict-mode comparison: `npx --yes jscpd scripts skills/public skills/support --format python --min-lines 18 --min-tokens 50 --mode strict --reporters json --output /tmp/charness-jscpd-code-strict --exitCode 0 --noTips --silent` found 92 clones / 2209 duplicated lines, slightly increasing bootstrap/preamble noise rather than improving gate fitness.
- Recommendation: `jscpd` has meaningful code signal, but do not add it as an unbaselined hard gate in this goal. The default/lower-floor scan is still dominated by portable bootstrap and remaining adapter/import skeleton pairs, while stricter floors surface real but small follow-up candidates. If adopted later, it should enter through the external-tool/support-binary path as a labelled code-only advisory or baseline/no-increase wrapper with recorded command/options and a reviewed threshold/ignore policy before any hard-gate promotion.
- Nose cross-check: Maintainer-local `nose 0.4.0` final scan still reports 222 families after Slice 4. Top families remain bootstrap/import skeletons and smaller helper shapes; the large adapter-load families removed in Slice 3 remain gone.
- Critique: Medium fresh-eye reviewer found no blockers. The reviewer verified the `jscpd 4.2.4` report counts, confirmed the default code-only report is dominated by short bootstrap/preamble/import/adapter skeleton pairs but not pure false-positive noise, confirmed the high-floor reports are small real follow-up inventories, and confirmed the docs-only clone is Achieve template/reference mirroring.
- Metrics: `jscpd` source-only default floor 87 clones / 2110 duplicated lines; source high floor 3 clones / 188 duplicated lines; docs-only 1 clone / 23 duplicated lines; mixed code+docs 88 clones / 2133 duplicated lines.

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

Status: complete.

Retro: charness-artifacts/retro/2026-06-04-nose-duplicate-refactoring.md
Host log probe: charness-artifacts/probe/2026-06-04-nose-duplicate-refactoring.json
Disposition review: charness-artifacts/critique/2026-06-04-nose-duplicate-refactoring-disposition-review.md

- `nose 0.4.0` was verified from `/home/hwidong/codes/nose/target/release/nose --version`.
- Baseline `nose` scan: 230 families, top bootstrap family 86 members / 1020 duplicate lines.
- After bootstrap slice: 225 families, top remaining bootstrap family 81 members / 400 duplicate lines.
- After adapter slice and document-gate slice: 222 families. Large duplicated adapter `load_adapter` bodies disappeared from the inspected top families; remaining top families are portable bootstrap/import skeletons, smaller adapter resolver skeletons, and helper shapes.
- `check_doc_near_duplicates.py` is the hard document near-copy gate; legacy `check_duplicates.py` delegates to it. Source and plugin canonical/legacy commands returned `[]`.
- `jscpd` 4.2.4 was reassessed post-cleanup. It remains meaningful as advisory code-clone signal, especially at a high floor, but is not added as a hard gate in this goal.
- Final standing proof: `./scripts/run-quality.sh --read-only` passed with 70 phases, 0 failures, total 53.4s.
- Fresh-eye review ran for the adapter resolver slice, document near-copy gate slice, and final `jscpd` disposition; no blockers remained.
- Arbitrary-machine `nose` install/update proof was not run; support-binary manifest work remains an explicit future integration step.
- Non-claims: no `jscpd` support manifest, `nose` support manifest, consumer-repo install proof, or zero-clone proof was produced in this goal.

## User Verification Instructions

Review this artifact and, if desired, rerun:

- `python3 scripts/check_doc_near_duplicates.py --repo-root . --fail-on-match --require-git-file-listing --json`
- `/home/hwidong/codes/nose/target/release/nose scan scripts skills/public skills/support --mode syntax,semantic,near --threshold 0.70 --min-lines 18 --min-tokens 24 --sort extractability --top 0 --format json`
- `npx --yes jscpd scripts skills/public skills/support --format python --min-lines 40 --min-tokens 80 --reporters json --output /tmp/charness-jscpd-code-40 --exitCode 0 --noTips --silent`

## Auto-Retro

Persisted: [`charness-artifacts/retro/2026-06-04-nose-duplicate-refactoring.md`](../retro/2026-06-04-nose-duplicate-refactoring.md)

- Context: completed the `nose` duplicate-refactoring goal, narrowed the hard
  near-copy gate to document surfaces, and reassessed `jscpd` after cleanup.
- Waste: raw clone counts were easy to overstate as either noise or proof; final
  evidence needed command/options beside the report counts.
- Critical decisions: kept whole-file document near-copy separate from token
  clone detection, used `nose 0.4.0` for refactoring, and deferred `jscpd` hard
  gating until support-binary/baseline policy exists.
- Counterfactuals: Gary Klein would have asked which clone families would block
  a push today; Daniel Kahneman would have resisted a binary "noise or gate"
  framing and asked for threshold/base-rate evidence.
- Disposition decisions: applied — exact `jscpd` commands/options and version are
  recorded in this goal and `docs/duplicate-detection-strategy.md`; applied —
  duplicate-detector responsibilities are now named by algorithm shape.
