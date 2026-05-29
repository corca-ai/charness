# Mutation Testing — Detect, Propose, Install

`quality` adopts mutation testing through a single `mutation_testing` block
in `<repo-root>/.agents/quality-adapter.yaml`. The public quality skill
contract is stack-neutral and does not require Stryker, Cosmic Ray, or any
other specific runner. The block declares four command slots and a GitHub
Actions workflow template that calls those slots at runtime.

## States

- **installed**: `commands.full` is a non-empty string.
- **missing**: top-level `mutation_testing` key is absent, or `commands.full`
  is empty, and `declined` is not `true`.
- **declined**: `declined: true`. The propose probe stops re-asking. Remove
  the flag to reopen.

The propose probe (`propose_mutation_testing.py`) emits JSON of shape
`{status, recommendation, install_actions}` with `status` in
`{installed, missing, declined, blocked}`. `blocked` is reserved for the case
where adapter validator errors are non-empty; the propose stage runs only
after `validate_quality_adapter_data` returns zero errors. The quality skill
must not call the probe when validation failed.

## commands.summary contract

The consumer-owned summary command is the single integration seam:

1. Write `report_paths.summary_md` as GitHub-issue-renderable markdown. The
   auto-issue step embeds it verbatim into the issue body, so HTML tags or
   tool-specific renderers should be normalized to plain markdown before the
   write.
2. Exit non-zero when the mutation score breaks `score_break`. Use the
   reachable-mutant denominator by default: `killed / (killed + survived)`.
   Runner-native no-test/no-mutation-possible outcomes and consumer-detected
   test-scope gaps should surface in `summary.md` as separate blocking line
   items, not folded into the score. Do not assume a runner's `no-test` label
   proves coverage absence unless that runner explicitly defines it that way.

charness does not enforce a score-extraction schema. Every reasonable mutation
runner can wrap its own report behind a thin script that meets both clauses.

Mutation testing is also a testability review trigger. Before tuning sampling,
timeouts, or runner parallelism, inspect whether the repo has a fast structural
test layer that can exercise the mutated behavior without repeatedly paying a
delivery boundary. See `testability-and-selection.md`: observation-based test
selection can accelerate mutation work, but it should surface hidden broad-test
dependencies instead of making them look like a healthy design.

## Runner prerequisites

Tool-specific knobs that enumerate mutation targets, copy files, or choose
how tests run belong in the tool's own config (`cosmic-ray.toml`,
`stryker.conf.json`, etc.) rather than the `mutation_testing` adapter block.
The adapter block stays stack-neutral by design: `commands.*` describes how
to invoke the tool and the tool decides how to source files. If the next
consumer needs to copy test fixtures or generated assets into a runner-owned
sandbox, that enumeration lives beside the tool's config, not in the adapter.

## commands.sample contract

The sample step exists so scheduled/full runs can limit the mutation set to
changed files plus deterministic fill. It is optional. When set:

1. Write deterministic file selections to stdout.
2. Also emit `sample_files=<space-separated list>` to `$GITHUB_OUTPUT`.

The workflow template captures the output into `MUTATION_SAMPLE_FILES` env
and exposes it to `commands.full`. The shape (CLI flag, env file, session
DB) is up to the consumer — charness only mandates the env var name.

When `commands.sample` is empty, the workflow runs the full mutation set.

Consumers that make scope gaps fatal should make the sampling contract at
least as strict as the summary contract. If the summary fails on uncovered
mutants, the sample step should prefer targets whose mutable lines are covered
by the selected test command, and should surface changed files filtered out by
coverage, mutation-line, or selection-budget filters as a blocking signal rather
than silently replacing them with fill samples.

When a sampler is configured with a base/head range for changed-file priority,
failure to compute that changed-file list is a blocking signal, not an empty
changed set. Fail before publishing sample manifests, workflow outputs, or
tool config rewrites so downstream summary gates cannot mistake missing
discovery for zero changed files.

## Workflow template

`scripts/templates/mutation-tests.yml` is installed at the adapter's
`workflow_path`. Per checkout, the workflow:

1. parses `.agents/quality-adapter.yaml` via `yq` and exports every slot
   as an env var (`MUTATION_CMD_FULL`, `MUTATION_AUTO_ISSUE_LABEL`, etc.).
2. branches on event:
   - `pull_request`: runs `commands.dry_run` (no sample step).
   - `workflow_dispatch` or scheduled: runs `commands.sample` then
     `commands.full`. Scheduled runs always execute — same-SHA dedup was
     removed (see corca-ai/craken-agents#127) because it both masked real
     regressions and defeated the stratified-sampling intent.
3. always runs `commands.summary` and uploads `report_paths.*` as the
   `mutation-report` actions artifact.
4. when `auto_issue.enabled` is true and the run failed, opens or comments on
   an issue labeled `auto_issue.label`, marked
   `<!-- ${{ github.repository }}-${marker_token} -->` so repos sharing a
   tracker do not collide. When the run succeeds, the same marker closes the
   issue.

`yq` is pre-installed on `ubuntu-latest`. macOS/Windows/self-hosted host
support is a deferred Probe Question; the initial install target is Ubuntu.

### Slot quoting

`commands.*` values are spliced into workflow `run:` lines via
`${{ steps.adapter.outputs.cmd_* }}`. The string GitHub Actions substitutes
into the bash `run` block is the raw adapter value. Keep slot values as
plain commands (e.g., `"npm run test:mutation"`) and use a helper script when
the command needs setup, redirects, or multi-step orchestration.

### Schedule cron is install-time, not runtime

`mutation_testing.schedule_cron` is rendered into the workflow file's
`schedule.cron` field when `propose_mutation_testing.py --execute` writes the
template, because GitHub Actions parses `on.schedule` before any job step
runs. Other slots are read at runtime each job. To change the cron, edit the
adapter and re-run `propose_mutation_testing.py --execute` so the workflow is
re-rendered.

## Detect / Propose Stage

`quality` calls `propose_mutation_testing.py` after the read-only review
phase when the adapter is valid:

- `installed` → no message.
- `missing` → one-line propose with `install_actions`:
  (a) scaffold `mutation_testing:` block into the adapter under a fenced
      `# >>> mutation_testing (charness propose) >>>` marker, and
  (b) write the workflow template to `workflow_path`.
- `declined` → one-line note "declined; remove `mutation_testing.declined`
  to reopen". No further action.
- `blocked` → never called when validation fails; the quality stage just
  surfaces the validator errors.

Adapter mutation is fenced-marker append for the initial slice: it only fires
on operator confirmation and only when no existing `mutation_testing` block is
present. Re-running propose on an already-installed repo is a no-op. A round-
trip mutation strategy (e.g., ruamel.yaml) is a deferred follow-up.

## Charness Dogfood Runner

The Charness repo itself uses Cosmic Ray 8.4.6, verified from PyPI's latest
release metadata on 2026-05-15. These helpers are dogfood support for this
repo's own mutation workflow, not a portable requirement for consumers:

- `scripts/sample_mutation_files.py` rewrites `cosmic-ray.toml`'s
  `[cosmic-ray].module-path` list, derives the pytest node ids that actually
  covered the selected mutation surface, rewrites `[cosmic-ray].test-command`
  for that sampled surface, applies executable-mutant and pytest-nodeid
  workload budgets, and writes the sample manifest.
- `scripts/run_cosmic_ray_mutation.py --mode dry-run` runs baseline + init,
  then filters known low-signal annotation-only work items from the session.
- `scripts/run_cosmic_ray_mutation.py --mode full` runs baseline + init +
  filter + exec + dump.
- `scripts/check_mutation_score.py` consumes `cosmic-ray dump` JSONL and
  writes `report_paths.summary_md`.
- `scripts/run_js_mutation.py` runs the repo's StrykerJS command-runner slice
  for `scripts/agent-runtime/*.mjs`. It is intentionally separate from the
  Python coverage-derived sampler: command-runner mode reruns the JS-native
  `npm run test:agent-runtime` command per mutant, so Charness budgets it by
  deterministic target sampling, mutant-count weights, concurrency, and a hard
  timeout instead of claiming affected-test precision. The runner deletes stale
  StrykerJS JSON before each launch, and the summary checker fails full mode
  when the fresh JSON report is missing.

## Defaults Source

All non-empty defaults trace to
`craken-agents/.github/workflows/mutation-tests.yml` (2026-05-14). Stryker-
literal paths (`stryker.log`) are renamed to neutral equivalents (`run.log`)
and stack-coupled values (`commands.*`) ship empty so the portable-defaults
preset stays stack-neutral.

## Fixing a changed-line-coverage regression

When a run FAILs on the **blocking** "changed files with uncovered changed
lines" signal (distinct from a score break — the score can pass while this
fails), two traps waste time and produce false proof (learned from #251):

- **Reproduce with the gate's own coverage, not a naive `coverage run`.** The
  gate collects coverage with `parallel = True` + `COVERAGE_PROCESS_START`
  (`mutation_sampling_lib.run_test_coverage`), so it **captures subprocess-
  invoked CLI scripts**. A plain `coverage run -m pytest` does not, and will
  report a subprocess-only script as 0% — a measurement artifact, not the gap.
  Drive `run_test_coverage` scoped to the file's test surface, then
  `classify_changed_line_scope_gap`, to see the real blocking verdict.
- **`workflow_dispatch` cannot prove a changed-line fix.** Only `schedule`
  events compute `base_sha` (see `mutation-tests.yml`); a dispatch run has zero
  changed files, so the changed-line classifier is inert. A green dispatch
  proves only the **score/survivor** path. The blocking-trio fix is confirmed
  by the **next scheduled run**, or locally by the sampler with explicit
  `MUTATION_BASE_SHA`/`MUTATION_HEAD_SHA`.

The signal is per-run `base..head`, so it can recur on any newly-changed file
whose changed lines lack coverage; the durable fix is test coverage of those
lines (not a floor/budget tweak). For a survived *format* mutant (e.g.
`json.dumps(..., indent=2)`), assert on raw output, not a `json.loads`
round-trip, which is indentation-agnostic.

## See Also

- `adapter-contract.md` — full field list and types.
- `../scripts/propose_mutation_testing.py` — the probe.
- `../scripts/templates/mutation-tests.yml` — the workflow.
