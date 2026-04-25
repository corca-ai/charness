# Operability Signals

`quality` should treat runtime drift and diagnostic visibility as first-class
operability concerns when the repo has meaningful standing gates or
operator-facing flows.

Missing operator takeover guidance is also an operability signal. When a repo
has a roadmap, install/update surface, or explicit maintainer handoff burden
but no honest `<repo-root>/docs/operator-acceptance.md`, classify that as `missing`
operability posture rather than a doc-nice-to-have.

Workflow runtime drift is also an operability signal. If the repo keeps GitHub
Actions workflows, a cheap repo-owned checker such as
`python3 scripts/check_github_actions.py --repo-root .` should flag outdated
JavaScript action majors before hosted-runner deprecation notices become the
first signal.

## Runtime Timing

If the repo runs lint, test, eval, or quality commands regularly:

- prefer a cheap repo-owned elapsed-time signal for the standing commands
- keep the signal machine-readable so later sessions can compare drift instead
  of guessing from memory
- keep the current summary compact and rotate older samples into archives
- prefer per-command timing over only one aggregate wall-clock number

Good timing artifacts help answer:

- which gate is getting slower
- whether a recent change widened the standing bar accidentally
- whether flaky setup or external calls are inflating runtime

Do not default to removing standing gates just because they are slow. First
make speed regressions visible, then tighten overlap, execution shape, or
runtime behavior.

## Slow Gate Triage

When a standing lint, test, eval, or executable-spec gate is slow:

1. confirm the repo still needs the full gate and is not accidentally running a
   wider surface than intended
2. inspect overlap and duplication before weakening coverage
3. move repeated fine-grained assertions into cheaper lower layers when they do
   not belong at the boundary
4. optimize repeated command bodies, adapters, or orchestration paths before
   reducing contract depth
5. use parallelism or scoped execution where the repo can support it honestly
6. only then consider changing standing gate scope, and name the coverage tradeoff explicitly

Preferred deterministic guards:

- overlap lint for duplicated broad test commands
- timing logs with bounded rotation
- adapter- or runner-level caching for repeated command bodies
- repo-owned scoped smoke plus a separate fuller boundary run when both are
  genuinely needed and clearly labeled
- a scoped or filtered runner mode for debugging and runner-behavior tests when
  the repo can narrow execution without lying about what the standing bar covers
- a local GitHub Actions major drift check when the repo depends on hosted
  workflows and wants runner-runtime changes caught before CI warnings

## Logs And Diagnostics

If the repo depends on logs, traces, or machine-readable diagnostics for normal
operation or debugging:

- check whether the useful signal appears early enough for an agent or operator
  to act on it
- keep the default standing-gate stream compact enough that phase-level signal
  is still visible on green; use `standing-gate-verbosity.md` when the default
  gate is getting noisy
- prefer logs that reveal the failing seam, command, boundary, or recovery path
  without forcing a full repro first
- check whether the format is stable enough that future automation can inspect
  it honestly

## Rotation And Retention

Unbounded logs are an operability quality problem.

Inspect whether:

- logs or timing samples are rotated into bounded archives
- current summaries stay short and useful
- retention is explicit enough that future sessions know what survives
- the repo avoids committing ever-growing machine output by accident

Do not force full observability stacks onto small repos. Apply this lens when
the repo already emits meaningful diagnostics or clearly would benefit from
them.
