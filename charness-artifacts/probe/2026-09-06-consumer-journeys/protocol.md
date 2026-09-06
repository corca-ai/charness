# Goal 798 consumer journey protocol

Frozen before any baseline execution. This is a bounded, on-demand dogfood
observation using existing task and review carriers, not a new evaluator or
standing semantic gate. The seed-baseline unit test proves only seed usability.

## Identity and execution

- Source inputs: `evals/fixtures/consumer-journeys/`; the freeze manifest records
  every seed and prompt digest plus these independent checks and this protocol.
- Baseline source: actual v8.4.3 tag, `7cea68253f3e208f4263f9efdb4a354ed5709bc0`.
  Canonical Codex export already exists at `/tmp/charness-goal798.qWglDo/baseline-export/plugins/charness`.
- Candidate source is an explicitly captured integrated commit, exported by its
  own canonical exporter. Record source SHA, version manifest, exporter identity,
  and consumed SKILL digests. A SKILL digest is not a full closure digest.
- Both arms use fresh copies of identical seeds committed as clean Git repos;
  exported packages stay outside consumer repos. No copied skill fragment, root
  source-checkout routing, or host-installed Charness may substitute.
- The existing `charness task run` carrier uses `gpt-5.6-luna`, effort `xhigh`,
  Codex exec `workspace-write`, timeout 1800 seconds, and `--skip-prepare` for
  these stdlib-only seeds. Record actual command, CLI version, runner receipt,
  logs, target commit, and any policy-derived execution settings. No model or
  effort differences may support a comparison claim.
- `CHARNESS_FIXTURE_PLUGIN_ROOT` names the selected exported package. The producer
  must report the consumed skill path and manifest version. Parent inspects its
  command trace for actual reads; self-report alone is not installed-layout proof.

## Handoffs and allowed intervention

Journey A runs the spec prompt in one context, then fast-forwards the consumer
repo to that exact produced commit before a fresh impl context receives the impl
prompt. The discoverable constraint is duplicate definitions: list-of-pairs
preserves information that a dict would destroy. It is visible before either
phase, not injected post hoc. Spec scope is `docs/alias-resolution.md`; impl
scope is that document plus `src/catalog.py` and `tests/test_catalog.py`.

Journey B runs the create-cli build prompt once, with README, executable
`repoctl`, scripts, and tests in scope. The prompt asks create-cli to hand off to
impl within the build. If it stops at design-only, the already frozen impl prompt
may be run in one fresh continuation context; that is a counted intervention,
not a silently successful first pass. No continuation is issued if the build
already completed.

No producer sees the independent check scripts or acceptance results before its
first pass ends. Parent does not edit consumer implementations. Maximum one
frozen continuation for B; no rescue prompt for A. Infrastructure retries retain
the same bytes and settings, are reported separately, and never erase failed
attempts. A tool failure is not a semantic failure unless the skill caused it.

## Independent acceptance

Run the frozen scripts with `CHARNESS_CONSUMER_ROOT=<completed repo>` using the
same Python interpreter and `PYTHONDONTWRITEBYTECODE=1`. Preserve stdout, stderr,
exit status, command, tested commit and check digests. First run them against the
seed: canonical and legacy behavior should pass; missing aliases/repoctl should
fail. This proves the oracle distinguishes the requested capability from baseline
tests that were already green. Do not change assertions after seeing an arm's result.

The parent is separate from producer contexts and runs the actual API and CLI.
A configured fresh-eye reviewer then inspects the outputs, command logs, handoff
documents and this protocol, naming its review packet and dispositions.

A acceptance: canonical lookups preserved; successful aliases; canonical-name,
duplicate (same/different target), dangling/alias-chain rejection; unknown lookup
KeyError; first-invalid-pair reporting. Inspect the spec's criterion/check mapping,
fixed/deferred choices, readiness and first slice. Check impl ancestry and any
contract edits: no redesign or hidden relaxation. No exact prose rubric.

B acceptance: executable entrypoint; read-only help, version, meaningful missing
versus ready doctor; dry-run with absent/present cache; JSON mode at declared
positions; only existing cache path written; parser errors refused before writes;
legacy refresh/check compatibility. Read-only comparison includes contents,
modes and mtimes in the copied consumer tree. It does not inspect outside-tree
writes or arbitrary host side effects. No undocumented JSON key or exit-code
convention is imposed on doctor. Review README against observed commands.

## Comparison and repeated work

Report acceptance per predicate, intervention count, redundant operation count,
wall time and reported token use separately. First-pass acceptance means all
required checks and semantic handoff review pass before any intervention.
Baseline success is preservation, not improvement. One sample per arm is a
bounded observation, not causal, statistical or cross-model performance evidence.

A repeated operation is another invocation for the same purpose and unchanged
input/revision after usable evidence or a contract was already available: repeated
adapter/planner discovery, repeated identical full gate, or re-asking an already
resolved API/CLI decision. Count from the producer's actual trace, grouping by
purpose, normalized command, input identity and intervening changes. Exclude
independent review, changed-input tests, phase-required spec→impl reading, and
infrastructure retry from this metric; report the latter separately.

The review-preview friction has a separate paired fixed workload: preview then
live with the same ID, both generated and supplied packets. Before repair, a
renamed live invocation was additionally necessary; after repair, that recovery
invocation is removed. Equal acceptance includes live duplicate refusal,
unchanged preview bytes, fresh generated input and stale supplied-input refusal.
Do not count the retained inspectable preview itself as removed work.

Only demonstrated owner gaps justify skill edits. If an arm fails due to an
ambiguous fixture or oracle bug, disposition the run as invalid and freeze a new
version before restarting both arms; never revise the oracle to turn a candidate
green. Final claims bind accepted source/export bytes to the released carrier by
equivalence or focused rerun. No auto-routing, Claude-host or production claim.
