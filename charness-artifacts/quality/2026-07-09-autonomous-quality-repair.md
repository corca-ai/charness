# Quality Review
Date: 2026-07-09

## Scope

Target boundary: repo-wide bug, code-quality, and test-speed pass after the
local #427 proof-honesty repair bundle.

Ambient repo findings: broad gate passed, but fresh-eye review found two
runtime bugs and the quality gate exposed stale changed-line coverage proof.

## Current Gates

- Healthy: `./scripts/run-quality.sh --read-only` passed 81 phases in 48.6s.
- Healthy: locked slice closeout with broad pytest and focused mutation coverage
  producer passed for the current base..HEAD plus worktree diff.
- Weak: the changed-line mutation gate initially skipped because the coverage
  fingerprint was stale for
  [score_prompt_mutation_survival_lib.py](../../scripts/score_prompt_mutation_survival_lib.py).
- Deferred: Cautilus remains ask-before-run; no log-backed behavior proof was
  requested for this local quality slice.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`. <!-- reproduction-source -->
- runtime hot spots: `pytest` 26.7s latest / 31.6s median, budget 140.0s; `dead-code-advisory` 7.8s latest / 7.8s median, default-off; `check-coverage` 7.0s latest / 7.3s median, budget 55.0s; `check-markdown` 6.0s latest / 5.9s median, budget 11.0s.
- coverage gate: `run_slice_closeout.py --base --verification-lock --refresh-broad-pytest-proof --produce-mutation-coverage --mutation-coverage-command "python3 -m pytest -q tests/test_score_prompt_mutation_survival.py tests/test_skill_efficiency_ab.py tests/test_markdown_preview_support.py"` passed.
- evaluator depth: deterministic gates only; Cautilus planner reported ask-before-run and no explicit log-backed behavior proof request was present.

## Healthy

- Broad quality gate passed: 81 passed, 0 failed, total 48.6s.
- Focused regression suite passed:
  [test_score_prompt_mutation_survival.py](../../tests/test_score_prompt_mutation_survival.py),
  [test_skill_efficiency_ab.py](../../tests/test_skill_efficiency_ab.py), and
  [test_markdown_preview_support.py](../../tests/test_markdown_preview_support.py)
  returned 91 passed.
- Security/supply-chain local posture passed through `check-secrets`,
  `check-supply-chain`, and `check-github-actions` in the read-only gate.

## Weak

- A/B preserved bundles did not include `stream.jsonl`, so the scorer's new
  stream fallback could not help real A/B outputs; fixed in
  [run_skill_efficiency_ab.py](../../scripts/run_skill_efficiency_ab.py) and
  plugin mirror, with `.gitignore` preventing raw preserved streams from
  becoming committed efficiency artifacts.
- A/B arm names, default config names, empty arms, and non-positive run counts
  could create path escapes or empty evidence; malformed arm entries could also
  leak raw CLI exceptions. Fixed with run-spec and default result-name
  validation.
- Markdown preview accepted absolute files outside the repo but later rendered
  them through repo-relative paths; repo-relative symlinks had the same escape
  class. Both are fixed by rejecting resolved out-of-repo targets during
  selection while keeping safe glob matches.
- Test-speed structure remains mixed: `inventory_standing_test_economics.py`
  found 384 Python test files and 156 standing/mixed nested-CLI files.

## Missing

- Missing: no safe deterministic pruning was proven for `pytest`; the suite is
  under budget and needs duration-attribution before any scope reduction.
- Missing: no current remote proof for unpushed local commits; this review makes
  no claim about GitHub issue closure or remote CI.

## Deferred

- Deferred: remove `check-markdown` from docs-only pre-push was not applied
  because local enforcement docs intentionally include markdown in the subset.
- Deferred: `dead-code-advisory` is unbudgeted but default-off, so the next move
  is runtime-summary labeling or a profile budget, not a blocking gate.
- Deferred: #421 remains machine-owned/watch; this review did not manually
  close it.

## Advisory

- structural review result: evidence: quality planner packet; capability needed is reliable local proof after
  broad code changes; current centers are read-only quality, slice closeout, and
  focused tests; next center was refreshed changed-line coverage proof.
- prose review result: evidence: delegated fresh-eye review plus inventory output; trigger boundaries stayed repo-wide quality; skill
  ergonomics inventory reported heuristic hits, but the actionable fixes were
  runtime bugs and one small test structural-waste cleanup.
- `inventory_structural_waste.py --json` initially found repeated
  [capture-skill-run.sh](../../scripts/agent-runtime/capture-skill-run.sh)
  reads in
  [test_skill_efficiency_ab.py](../../tests/test_skill_efficiency_ab.py); after
  hoisting the stable read, rerun found no findings.
- `inventory_standing_test_economics.py --summary` found nested CLI fanout, but
  no safe prune; next speed work should start with pytest durations over that
  fanout.

## Delegated Review

- Delegated Review: executed — bug/code-quality fresh-eye found A/B stream
  preservation, arm-name escaping, non-positive runs, and markdown-preview
  absolute-path crash; worker patches fixed all four.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof):
  executed — runtime fresh-eye found no budget failure; `pytest` remains under
  budget and check-markdown pruning is deferred for policy review.

## Commands Run

- command: quality planner JSON via quality skill `plan_quality_run.py`.
- command: runtime summary JSON via quality skill `render_runtime_summary.py`.
- command: standing-test economics summary via quality skill inventory.
- command: structural-waste JSON via quality skill inventory.
- command: skill-ergonomics summary via quality skill inventory.
- command: `./scripts/run-quality.sh --read-only`
- command: focused pytest over prompt mutation, A/B harness, and markdown-preview support tests, 91 passed.
- command: `python3 scripts/run_slice_closeout.py --repo-root . --base --verification-lock --refresh-broad-pytest-proof --produce-mutation-coverage`

## Recommended Next Quality Moves

- active next-speed-measurement — capability_needed=predictable fast proof; next_center=nested CLI fanout; transformation=run pytest durations over the standing nested-CLI sample before pruning; proof_boundary=duration report plus unchanged broad gate; enforcement_posture=advisory.
- passive check-markdown-docs-only-prune because local enforcement policy intentionally includes markdown in docs-only pre-push; capability_needed=faster docs-only pushes; next_center=policy review; transformation=decide whether CI mirror is enough before changing `.githooks/pre-push`; proof_boundary=policy diff plus docs-only push timing; enforcement_posture=no-gate.
- passive dead-code-advisory-runtime-label because it is default-off; capability_needed=runtime summary clarity; next_center=runtime summary labeling or budget; transformation=mark default-off labels separately or add a 10s profile budget; proof_boundary=runtime summary output; enforcement_posture=advisory.

## History

- [2026-07-03 pytest suite audit](./history/2026-07-03-pytest-suite-test-value-audit.md)
