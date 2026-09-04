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

The propose probe (`propose_mutation_testing.py`) emits YAML of shape
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
by the selected test command. Uncovered CHANGED LINES are the blocking signal
(computed over all eligible changed files in range, before selection); changed
files dropped by coverage, mutation-line, selection-budget, or workload-budget
filters surface as named advisory sections rather than blocking — a capacity
drop of a covered file is not a coverage gap, and blocking on it makes every
larger-than-budget push a guaranteed red run.

When a sampler is configured with a base/head range for changed-file priority,
failure to compute that changed-file list is a blocking signal, not an empty
changed set. Fail before publishing sample manifests, workflow outputs, or
tool config rewrites so downstream summary gates cannot mistake missing
discovery for zero changed files.

## Workflow template

`scripts/templates/mutation-tests.yml` is installed at the adapter's
`workflow_path`. Per checkout, the workflow:

1. parses `<repo-root>/.agents/quality-adapter.yaml` via `yq` and exports every slot
   as an env var (`MUTATION_CMD_FULL`, `MUTATION_AUTO_ISSUE_LABEL`, etc.).
2. branches on event:
   - `pull_request`: runs `commands.dry_run` (no sample step).
   - `workflow_dispatch` or scheduled: runs `commands.sample` then
     `commands.full`. Scheduled runs always execute — same-SHA dedup was
     removed because it both masked real
     regressions and defeated the stratified-sampling intent.
3. always runs `commands.summary` and uploads `report_paths.*` as the
   `mutation-report` actions artifact.
4. when `auto_issue.enabled` is true and the run failed, opens or comments on
   an issue labeled `auto_issue.label`, marked
   `<!-- ${{ github.repository }}-${marker_token} -->`. The marker is what
   identifies an issue as this workflow's own, on both the open-or-comment path
   and the recovery path. Both paths list open issues by label and select on the
   marker; neither uses issue *search*, because `in:title` is GitHub full-text
   (so it matches human-filed issues), search results are relevance-truncated,
   and the search index lags issue creation. **Rotating `auto_issue.marker_token`
   orphans every issue filed under the old token**: the next failure cannot see
   them, files a duplicate, and the orphans never receive a recovery candidate.
   Close them by hand when you change the token.
5. when a **scheduled** `full` run succeeds, comments a recovery *candidate* on
   its marked issues and labels them `mutation-recovered-candidate`; it never
   changes issue state. The sample seed rotates per run, so the green may not
   have mutated the same file population as the run that filed the issue, and it
   does not verify that the reported surviving mutant is dead. Closing on it
   would be the workflow certifying its own green at an irreversible boundary,
   per *P4*/*P5* of the authoring-repo-internal `<authoring-repo>/docs/design-north-star.md`; the
   close is a distinct observer's call, made against the observables in that
   comment. Operational detail: the comment is a point-in-time snapshot posted
   **once** per recovery — the label is the dedupe key, so later greens are
   silent, and if the label write fails after the comment lands the run logs an
   error and a later green may repeat the comment. A fresh failure removes the
   label and re-arms the next candidate, and
   `mutation-recovered-candidate` is a fixed name, not an adapter slot. Routing a
   human to the candidate is the consuming repo's job — the workflow populates
   the record but assigns no observer.

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
runs. Other slots are read at runtime each job.

**The workflow file is written once, at first install, and never re-rendered.**
`propose_mutation_testing.py --execute` acts only when `mutation_testing` is
`missing`, and even then it refuses to overwrite an existing `workflow_path`
(it reports `workflow already present, not overwritten`). So changing
`schedule_cron` — or picking up a newer charness workflow template after an
upgrade — means editing the installed workflow yourself, or deleting it and
re-running install. There is no re-render command; do not expect one.

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

- `<plugin-dir>/scripts/mutation/sample_mutation_files.py` rewrites `cosmic-ray.toml`'s
  `[cosmic-ray].module-path` list, derives the pytest node ids that actually
  covered the selected mutation surface, rewrites `[cosmic-ray].test-command`
  for that sampled surface, applies executable-mutant and pytest-nodeid
  workload budgets, and writes the sample manifest.
  Its coverage probe defaults to `reports/mutation/sample-coverage.json`, which
  is separate from the changed-line producer's
  `reports/mutation/test-coverage.json`.
- `scripts/mutation/run_cosmic_ray_mutation.py --mode dry-run` runs baseline + init,
  then filters known low-signal annotation-only work items from the session.
- `scripts/mutation/run_cosmic_ray_mutation.py --mode full` runs baseline + init +
  filter + exec + dump.
- `<plugin-dir>/scripts/mutation/check_mutation_score.py` consumes `cosmic-ray dump` JSONL and
  writes `report_paths.summary_md`.
- `<plugin-dir>/scripts/mutation/run_js_mutation.py` runs the repo's StrykerJS command-runner slice
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

## Changed-Line Coverage Gate (portable pattern)

Mutation and changed-line coverage are explicit release-final/CI concerns in
Charness. A full mutation run is too slow for routine developer commands, so
ordinary implementation uses focused tests plus the default core lane. The
release-final owner runs the producer once after its other release checks and
passes its payload to the portable consumer. Direct invocation also remains
available for focused diagnostics. The optional
`check_changed_line_coverage.py` capability reproduces the **blocking** signal
of a deeper gate: a changed pool file whose changed lines over `base..head` lack
coverage. It does not run mutants; it **reuses** a coverage.py report produced by
the caller. Consumers should keep it out of ordinary, default, and full lanes
unless they explicitly choose the release-final cost.

Configure it with the `changed_line_mutation_gate` adapter block
(`coverage_json`, `eligible_globs`, `exclude_globs`). It is stack-neutral — the
eligible set is glob-driven, not sourced from a tool config — so a consuming repo
inherits the gate without the mutation-runner wiring. Empty `eligible_globs`
keeps it inert. Base/head come from `--base-sha`/`--head-sha` or
`MUTATION_BASE_SHA`/`MUTATION_HEAD_SHA`.

Pass only the base and leave the head defaulted. An analyzed head that is not the
checked-out `HEAD` cannot be judged — coverage comes from the live worktree while
the change set is diffed against that head — so the gate exits **3** (could not
judge, `ok: true`, not a coverage failure) when the range touched eligible files,
and exits 0 with an `analyzed_head_not_checked_out_head` disclosure plus a stderr
warning when it did not. See the adapter contract's exit-code table. This also
means a stale exported `MUTATION_HEAD_SHA` can no longer silently empty the range
and report `OK` over a tree the gate would otherwise have blocked.

### Freshness guard: content fingerprint, not a commit SHA

Reusing a coverage report is only safe if the report was built for the code being
judged. The producer stamps a sibling `<coverage_json>.fingerprint` marker; the
consumer recomputes it and **skips non-blocking** on a mismatch, so a stale
report can never raise a false "uncovered changed line".

The marker is a **content** hash of the changed eligible files over
**base → working tree**, not a commit SHA, on purpose: a producer and a later
consumer can see the same on-disk content even when a commit boundary lies
between them. A SHA-keyed marker would silently mismatch and skip. A content
hash also survives a no-op recommit/rebase that does not touch the pool, while a
base advance correctly re-invalidates.

If another flow already stamps `<coverage_json>.fingerprint` for the same
report (e.g. a tool-specific producer with a different eligible-file source),
point this gate at a distinct `coverage_json` so the two markers do not clobber
each other — divergent fingerprints make each gate read the other's marker as
stale and skip non-blocking (never a false fail, but also no teeth).

### Producer cost: one instrumented run, no second pass

Coverage for the gate belongs to the final release lane. After release pytest and
the cheaper release checks pass, instrument only the standing tests mapped to the
changed mutation-pool files, once, with plain statement coverage. Ordinary
implementation and pre-commit lanes do not run it. Drop per-test `dynamic_context`
for this report: the gate
only needs executed-vs-missing lines, and per-test context can balloon the
coverage JSON by orders of magnitude. Measured on the authoring repo, same
coverage data with the export flag as the only difference: **8.22 GB vs 12.26 MB
(671x), and 36.5s / 20.44 GiB peak RSS vs 0.13s / 0.06 GiB just to load it.**

Size is the lesser half. **20 GB of peak RSS to read a report is a correctness
risk, not a speed one:** on a host with less headroom that load raises
`MemoryError`, and a gate with no branch for it reports an out-of-memory crash as
a tool failure rather than as the refusal-to-judge it is — which is exactly the
distinction a changed-line gate exists to keep.

Make the collection an **explicit flag**, never a side effect of an adjacent one.
The authoring repo tied it to the flag that stamps the freshness marker, so the
cheap path arrived only for callers who happened to want a marker, and the other
arm paid 671x for a column the verdict never reads. Where a second consumer *does*
read contexts (a mutant sampler resolving per-line test nodeids), give it its own
report path rather than sharing one: whichever tool ran last then decides whether
the other one works.

Run the cheap deterministic doc/lint gates *before* paying for the instrumented
run so a late failure does not force a re-pay.

### Name the cheap refresh first, in the payload

When the final lane cannot use the coverage it produced — absent report, stale
fingerprint, or an unmapped changed file — it exits nonzero and names the missing
scope. Repair the mapping or standing test, then rerun the release lane once. The
scheduled broad mutation workflow remains an independent diagnostic; it is not a
second closeout fallback. The incremental direction is safe for a *fresh* subset producer run: coverage
from a test subset is a subset of full coverage, so it can cost a false stop
but cannot grant a false pass. The freshness marker is **pool-scoped**: it
hashes mutation-pool files only (`scripts/`, `tools/`, skill helpers), not
`tests/`. Deleting or renaming tests that supplied the proof, while pool files
stay put, leaves `--require-fresh-coverage` matching the old JSON. That hole
is declined to widen; do not read a matching marker as "the tests that
produced this coverage still exist."

### The false-green dry-run trap

A diagnostic run with `--head-sha HEAD` is a **false green** when the
mutation-pool change is still uncommitted: HEAD is the parent, so `base..HEAD`
excludes the change and the gate judges nothing. At the release boundary, run
the producer (which stamps the marker over base → worktree) then the consumer,
or analyze a head that includes the worktree. The capability **warns**
(non-blocking) when the analyzed head resolves to `HEAD` while eligible files
have uncommitted changes, so the trap surfaces instead of reading as a clean
pass.

### The unverified-skip trap (an absent gate must not read as a pass)

A cheap consumer that **skips non-blocking** when coverage is absent or stale is
safe against false positives, but it creates a subtler failure: a skip that
happens *while eligible files changed* is indistinguishable from a clean pass. A
release attestation could go green, the uncovered changed lines could land, and
the scheduled run — whose base accumulates everything since its last run — flags
them after merge and auto-files. This is the recurrence engine behind the seam.

The fix is **surfacing, not a new hard gate**: when the gate skips while eligible
pool files changed in the range, emit a loud, non-blocking obligation that names
the unverified files and the producer command to run. The verdict stays unchanged
(still exit 0, still cheap), but `skipped` no longer looks like `verified`. Keep
the structured signal (`coverage_not_verified`) in the report too, so a wrapper or
CI summary can distinguish "nothing to check" from "did not check".

## Fixing a changed-line-coverage regression

When a run FAILs on the **blocking** "changed files with uncovered changed
lines" signal (distinct from a score break — the score can pass while this
fails), two traps waste time and produce false proof:

- **Read the summary as two results, not one overloaded status.** The top-level
  status is the overall gate result. The `Mutation score:` row reports only the
  reachable killed/survived threshold result, and the `Blocking signals:` row
  reports non-score blockers such as changed-line coverage. A run can
  therefore show `Status: FAIL`, `Mutation score: PASS`, and
  `Blocking signals: FAIL` without any survived Python mutants.

- **`UNMEASURED` is a new status token, and it is not a score verdict.** Counting
  it as "the third status" would be wrong: the `Status:` row already emits
  `PASS`, `FAIL`, `PASS-partial`, and `FAIL-incomplete`. `PASS` and
  `FAIL` both claim that mutants ran and were scored. When nothing was scored,
  both statuses would assert a measurement that never happened, so the summary
  says `UNMEASURED` instead and the score row reads
  `(no reachable mutant produced a verdict; no score was computed)` rather than
  a percentage against the threshold. Three routes reach it: the coverage
  baseline aborted before mutation ran, the StrykerJS report is missing, or the
  denominator is zero (`killed + survived == 0` — every mutant skipped or
  ignored, an empty dump, a Stryker config excluding the operator set).
  **`UNMEASURED` is still red**: the exit code and the workflow result are
  unchanged, and the blocking-signal row still names the real cause. What
  changes is only that the run stops claiming a score it never took. Read it as
  "go find out why nothing ran", not as "the score dropped" — for four days in
  2026-08 a baseline abort published as a mutation-score regression, and that
  misreading is what this token exists to prevent.

- **Reproduce with the gate's own coverage, not a naive `coverage run`.** The
  gate collects coverage with `parallel = True` + `COVERAGE_PROCESS_START`
  (`mutation_sampling_lib.run_test_coverage`), so it **captures subprocess-
  invoked CLI scripts run at their real in-repo path with an inherited
  environment** (measured 2026-07-30). A plain `coverage run -m
  pytest` does not, and will report such a script as 0% — a measurement
  artifact, not the gap. Drive `run_test_coverage` scoped to the file's test
  surface, then `classify_changed_line_scope_gap`, to see the real blocking
  verdict. **But a 0% under the gate's own producer is NOT always an
  artifact:** a spawn whose `env=` replaces the environment drops
  `COVERAGE_PROCESS_START`, and a test that runs an out-of-repo COPY of the
  script falls outside the rcfile's `source = <repo-root>` and is dropped with
  the environment fully intact. The gate's `subprocess_coverage_advisory`
  payload names those cases on a BLOCK.
- **`workflow_dispatch` cannot prove a changed-line fix.** Only `schedule`
  events compute `base_sha` (see `mutation-tests.yml`); a dispatch run has zero
  changed files, so the changed-line classifier is inert. A green dispatch
  proves only the **score/survivor** path. This false-proof class recurred
  after its prose-only lesson, so the rule is now gate-shaped: before citing a
  CI mutation run as changed-line proof, run
  `python3 <plugin-dir>/scripts/mutation/check_mutation_run_proof.py --claim changed-line --run-id <id>`
  (or pass explicit `--event`/`--base-sha`/`--sample-manifest` facts); it
  refuses the claim deterministically when the run's trigger cannot evaluate
  it. A changed-line-blocker fix is confirmed by the **next scheduled run**, or
  locally by the sampler with explicit `MUTATION_BASE_SHA`/`MUTATION_HEAD_SHA`.

The signal is per-run `base..head`, so it can recur on any newly-changed file
whose changed lines lack coverage; the durable fix is test coverage of those
lines (not a floor/budget tweak). For a survived *format* mutant (e.g.
`json.dumps(..., indent=2)`), assert on raw output, not a `json.loads`
round-trip, which is indentation-agnostic.

For manual targeted-mutant proof, bind the edit to the gate target before
mutating. Use the changed-line helper or sample manifest's changed-line proof
targets, cite/display the exact `path:line` and source text, mutate that exact
line, record the failing test, and then revert. A file-level blocker alone is
not enough proof when nearby returns or branches look similar.

## See Also

- `adapter-contract.md` — full field list and types.
- `../scripts/propose_mutation_testing.py` — the probe.
- `../scripts/templates/mutation-tests.yml` — the workflow.
