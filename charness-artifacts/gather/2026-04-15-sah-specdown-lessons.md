# Gather: `sah-cli` and `specdown` Lessons

## Source

- Local source: `../sah-cli`
- Local source: `../specdown`
- Source identity: adjacent Corca repositories reviewed as reference
  implementations for improving `charness`.
- Accessed: 2026-04-15 UTC

## Freshness

Both sources were read from the local workspace. This pass inspected repository
documents, command surfaces, tests, worker/spec contracts, and standing gates.

Verification commands run during this gather:

- `go test ./...` in `../sah-cli`: passed.
- `go test ./...` in `../specdown`: passed.
- `specdown run -dry-run -quiet` in `../specdown`: passed.
- `python3 scripts/validate-integrations.py --repo-root .` in `charness`:
  passed.

## Requested Facts

### `sah-cli`

The strongest reusable pattern is a narrow, explicit worker contract:

- One assignment is claimed, solved, and submitted at a time.
- The local agent is launched without the SCIENCE@home credential.
- The agent runs in a fresh empty temporary workdir.
- Codex is invoked with JSON event output, read-only sandboxing,
  no session persistence, and an explicit `--cd` into the temp workdir.
- Claude/Qwen/Gemini are also invoked in headless structured-output modes with
  plan/read-only style permissions where available.
- The prompt demands exactly one JSON object, or `ABORT: <reason>`.
- Output parsing accepts the intended JSON object, recognizes aborts, and
  rejects empty or unreadable output.
- Local failure, abort, protocol mismatch, or submit failure releases the
  assignment so work is not pinned until expiry.
- Compatibility is explicit: task protocol and client capability headers are
  advertised only on worker routes, and old response shapes keep tests while
  they remain deployed.
- User-facing discovery is state-aware: the CLI computes local auth, installed
  agent, daemon, and release state, then merges that with server-provided
  navigation and local fallbacks.

What matters for `charness` is not the SCIENCE@home API shape. The transferable
invariant is: agent work that affects a durable contract should run through a
small task envelope with isolation, a strict output schema, explicit abort
semantics, and cleanup/release behavior.

### `specdown`

The strongest reusable pattern is Markdown that is both readable contract and
runnable acceptance surface:

- Specs mix prose, executable blocks, doctest-style command/output examples,
  check tables, variables, hooks, and frontmatter.
- Specs stay at acceptance-boundary level; unit tests keep detailed edge cases.
- Built-in shell execution is enough for simple flows, but repeated shell
  parsing should become an adapter.
- Adapter protocol is NDJSON over stdin/stdout with request IDs, structured
  success/failure responses, expected/actual diffs, labels, timeouts, and
  stdout reserved for protocol messages.
- Traceability is document-level, typed by frontmatter, and enforced through
  named markdown links plus cardinality, acyclicity, and transitive closure
  constraints.
- `specdown run -dry-run` gives parse/validation confidence without executing
  cases.
- The repo dogfoods its own specs and example project in the pre-commit hook.

What matters for `charness` is not adopting specdown everywhere. The
transferable invariant is: durable behavioral claims should have a readable
contract artifact and a runnable, acceptance-level check, with traceability when
documents start forming a graph.

## Candidate Charness Adaptations

### 1. Add a strict agent-task envelope for evaluator or HITL probes

Classification: `AUTO_CANDIDATE`, active.

Shape:

- repo-owned helper such as `scripts/run-agent-task.py`
- input: JSON task file with `task_id`, `task_type`, `payload`,
  `instructions`, `submission_schema`, `timeout`, and optional agent selector
- execution: empty temp dir, no session persistence where the agent supports
  it, read-only or plan-mode permissions, no repo mutation
- output: exactly one JSON object on stdout, or one JSON object containing
  `status: "aborted"` and `reason`
- stderr: diagnostics only
- persisted state: optional `.charness/agent-task/<run-id>.json` with command,
  duration, exit class, output parse status, and cleanup status

Why:

`charness` already has smoke evals and Cautilus scenario wiring, but it does not
yet have a repo-owned generic task envelope for agent-executed probes. The
`sah-cli` contract would make future evaluator-required skill checks less
dependent on ad hoc prompt discipline.

### 2. Promote selected durable docs into executable specs instead of more prose

Classification: `AUTO_CANDIDATE`, active after the next spec target is chosen.

Best first targets:

- `docs/control-plane.md`: manifest lifecycle commands, lock sections, support
  materialization, and doctor exit semantics.
- `docs/public-skill-validation.md`: tier assignments and adapter requirements
  already have JSON policy plus validators, so spec blocks could demonstrate
  the acceptance contract without duplicating unit tests.

Keep the initial spec small:

- a `specdown.json`
- one index file
- one focused spec using `run:shell` doctest blocks against existing validators
- no custom adapter until at least three shell blocks repeat the same parsing
  pattern

Why:

`charness` has many validators and good docs, but the reader still has to infer
which doc claims are executable. A small specdown layer would make selected
contracts discoverable as runnable acceptance specs.

### 3. Add document traceability only where the graph is real

Classification: `AUTO_CANDIDATE`, passive until the first specdown document
  exists.

Candidate graph:

- `control` docs depend on integration manifests and lock schema.
- public-skill validation docs depend on JSON policy and scenario registry.
- operator acceptance docs depend on roadmap or handoff items when those
  documents are intentionally maintained.

Why:

`specdown` traceability is strongest when documents form typed layers with
cardinality expectations. It would be wasteful as a repo-wide markdown link
replacement, but useful for the control-plane and validation-policy surfaces.

### 4. Add release/cleanup semantics to long-running review workflows

Classification: `AUTO_CANDIDATE`, active for HITL/evaluator runtime state.

Shape:

- when a HITL or evaluator session claims a review chunk, record whether it was
  completed, aborted, or released
- if a chunk fails locally or is aborted, persist a structured reason and make
  the next pickup explicit
- validators should detect stuck claimed state only if the repo introduces such
  claims

Why:

`sah-cli` releases assignments aggressively on abort and local failure. The same
concept maps to `charness` review/eval state: avoid leaving future agents to
guess whether a partially processed chunk is still owned.

## What Not To Copy

- Do not make `charness` public skill bodies host-specific by embedding Codex,
  Claude, Gemini, or Qwen invocation details there. Agent-specific execution
  belongs in scripts, adapters, or integration manifests.
- Do not turn every design doc into a specdown spec. Use executable specs only
  for contracts that are stable enough and important enough to run repeatedly.
- Do not use specdown shell blocks as broad unit-test wrappers. Keep acceptance
  examples small; leave coverage and branch detail to pytest and validators.
- Do not add a daemon model just because `sah-cli` has one. The reusable idea is
  local state discovery, structured output, and cleanup behavior, not background
  work.

## Open Gaps

- This pass did not build a `charness` agent-task helper yet.
- This pass did not add a `specdown.json` or any `*.spec.md` files to
  `charness`.
- The next implementation should decide whether agent-task execution belongs
  under evaluator/Cautilus support, HITL, or a more general control-plane
  helper before creating a new command surface.
