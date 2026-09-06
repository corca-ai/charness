# Long-delegation four-arm pilot

Goal: [#805](https://github.com/corca-ai/charness/issues/805), protocol work item
[#809](https://github.com/corca-ai/charness/issues/809).

## Decision and non-claims

Test whether the candidate helps a delegated task survive a cooperative context
boundary and changed requirements. This is a bounded two-context proxy for
long-term delegation, not a microtask mode or proof of arbitrary crash recovery.
One run per cell cannot establish statistical superiority, general reliability,
or a model ranking. An honest result can be no demonstrated benefit.

The controlled task channel is a local durable `.task/current.md` file. The
observer replaces it at the scheduled boundary. This is the same capability in
all cells; it does not demonstrate live GitHub/provider Goal recovery.

## Frozen inputs and arms

Before any cell starts, preserve a SHA256 manifest of this protocol, all prompt
files, oracle, launcher, `control-observations.json`,
`launcher-control-observations.json` and these four seed files from
`evals/fixtures/consumer-journeys/spec-impl-alias/seed/`: `README.md`,
`src/__init__.py`, `src/catalog.py`, `tests/test_catalog.py`. Do not copy its
`AGENTS.md`. The manifest is immutable once a cell starts. Candidate package
revision and complete export digest are a separate frozen input, recorded before
any candidate cell; baseline may start after protocol acceptance. No pilot output
may inform the candidate before its initial package is frozen.

Order, chosen before results: low baseline, high candidate, high baseline, low
candidate. Execute sequentially to avoid load contention. Candidate availability
therefore gates the second cell. Requested models are `gpt-5.6-luna` (low) and
`gpt-6-astra` (high), both `medium` effort. Record requested identity and actual
process observations; request success does not independently attest backend
model identity. Never substitute a model or alter effort inside the pilot.

Each cell gets the same initial task bytes and seed, phase-one prompt, revised
task bytes and phase-two prompt. Candidate alone also receives `treatment.md`
and a read-only installed-layout candidate package at `/tmp/package`. No host
Charness discovery, Charness seed instructions, or Charness task runner is shared
with baseline. The extra treatment text and package are counted treatment cost.
Both cells may write ordinary notes/docs/tests, use git, and run local commands.
Neither may contact external services, install packages, modify the observer's
task file, or read paths outside `/tmp/work`, `/tmp/package` (candidate only), and tools
needed to execute the task. No external repository or message is created.

## Neutral launch and isolation

Use raw fresh `codex exec`, never `resume` or Charness task-run. The disposable
launcher only copies frozen inputs, launches, injects the scheduled update,
captures raw output/timing, and snapshots files. It does not choose a plan,
repair a contract, summarize a prior turn, write checkpoint notes, or retry.

Use bubblewrap to mask the authoring checkout and host temporary roots; mount
only the current arm at `/tmp/work`, and candidate package only for treatment.
The oracle and all other arm roots remain unmounted. Disable network in the
task's shell sandbox if supported without breaking the model transport; at
minimum audit shell/tool traces for prohibited external calls and invalidate
on a violation. This pilot is cooperative, not a malicious-agent security test.
The launcher must demonstrate oracle/other-arm path invisibility before launch.

Host flags: `--ignore-user-config --ignore-rules --disable plugins --disable
remote_plugin --disable hooks --enable skip_host_skill_discovery --sandbox
workspace-write --ephemeral --skip-git-repo-check --json`, with working directory
`/tmp/work` and common reasoning setting. Never repurpose `HOME` or `CODEX_HOME`.
System skills can remain equally exposed. `skip_host_skill_discovery` is an
under-development flag, so absence needs observed preflight and trace checks,
not merely a flag assertion. Raw preflight must run inside the final isolation
layout for each treatment shape before its first cell. A contaminated baseline
is invalid, not a failed baseline task.

## Scheduled boundary and budgets

Phase one receives `initial-task.md` as `.task/current.md`. Ask for a durable
design and checkpoint, but no source/test implementation. Allow 900 seconds.
When the process exits, preserve its transcript and full workspace snapshot.
An exit without a checkpoint is a phase-one failure; do not rescue it. Timeout
terminates that phase and records timeout. The scheduled phase two still starts
from whatever durable workspace was actually left.

Replace only `.task/current.md` with `revised-task.md`, preserving every other
byte. Start a new process with `resume.md` and no phase-one transcript or injected
summary. Allow 1800 seconds. No context resume, extra answer, hidden hint or
semantic intervention. The replacement is scheduled stimulus, not intervention.
The prompt points to the task channel in both phases; it does not restate the
delta. This is deliberate cold-context continuation, not a surprise interruption.

No token ceiling is claimed: this CLI exposes a reliable wall-clock timeout,
not an enforced per-run token budget. Capture reported input, cached-input,
output and reasoning tokens when available, each phase's wall time, process
status, tool-call count, observer overhead, treatment overhead, and intervention
count. Missing usage is unknown, never zero. Report tokens/time, not dollars.
Keep preflight and evaluator costs separate from producer costs.

Infrastructure failure before the first model event may be retried once with
identical inputs, preserving both attempts. A semantic failure, timeout after
model activity or oracle rejection gets no initial-pilot retry. After all four
cells, at most one separately labelled candidate repair-validation round is
allowed, with original outcomes retained. Oracle/task changes invalidate this
comparison and require a separately named experiment; never rewrite failures.

## Acceptance and observer

The hidden oracle imports the final producer module in a fresh subprocess. It
checks canonical and unknown behavior, direct aliases, forward chains,
canonical-key lookup, collision/duplicate precedence, cycle/dangling diagnosis,
and preservation of caller inputs. It also compares the original baseline test
bytes, task-channel bytes and immutable initial source bytes at phase one.
Additional producer tests are allowed only in phase two. Compare the complete
phase-one `src/` and `tests/` inventory, file kinds, modes and bytes, including
additions/deletions; ignore interpreter `__pycache__`/`.pyc` runtime writes.
Human trace/snapshot review also rejects phase-one implementation placed outside
those directories. Any boundary violation remains substantive failure even when
final behavior passes. Missing protected files record failed checks, not a
launcher exception; persist each phase before advancing. A corrupted task channel
that cannot be safely replaced records substantive failure and phase two not run.
Reject escaping snapshot symlinks before evaluation; links are recorded as links,
never silently hashed through an outside referent.

Oracle controls must accept correct single-file and package-relative-import
implementations and reject each named broken mutation before any arm starts.
Check unknown names with and without aliases, and deep-snapshot caller values
on both successful and rejected construction. Run final oracle and producer test
commands with a 20-second subprocess limit each; timeout is non-accepting subject
failure. Capture status/output separately from the continuation judgment.

The parent independently reads the transcript and durable documents to judge
three ordered observations: phase one leaves an actionable initial contract;
phase two reads current task/durable truth before source mutation; phase two
reconciles the no-chains rule and new `canonical_key` requirement in durable
docs before claiming completion. Record exact trace events/document paths, or
`unproven` if trace evidence is insufficient. Merely passing final tests does
not establish correct continuation. Original tests and hidden behavior must both
pass; a green test command is not a substitute for this contract.

For each cell report completion (behavior + continuation + mutation checks),
failure class, costs and interventions separately. Compare candidate/baseline
within model first; report cross-model observations without causal tier claims.
Do not trade broken acceptance for lower cost. A candidate preserves acceptance
only when all required checks pass. Improvement is an observed cost reduction
or a passed acceptance dimension its paired baseline failed, with tradeoffs
visible. This pilot cannot prove a win if all cells pass and candidate costs more.

## Verification Scope Decision

Claim: this frozen pilot fairly observes a narrow changed-contract continuation.
Consumer closure: launch isolation, actual model traces, final files and hidden
behavior verdict. Minimum proof: exact input hashes, isolation/discovery
preflight, positive/negative oracle controls and two independent protocol lenses.
Omitted: live provider recovery, malicious isolation attacks, statistical
significance, arbitrary abrupt crash recovery and dollar accounting. Verifier
contract: controls, immutable snapshots and explicit human trace disposition.
Failure classification: contamination/infrastructure invalidates a cell;
implementation/continuation/budget failure remains a substantive observed result.
