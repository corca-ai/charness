# Agent Production Runtime

Use this lens when a repo is building or operating a user-facing LLM or agent
runtime. The goal is not to enforce one provider's architecture. The goal is to
make production risk visible, classify what can be proven deterministically,
and recommend behavior proof only when deterministic gates cannot answer the
risk honestly.

## Boundary

Charness owns quality review, evidence classification, recommendation wording,
and durable artifact honesty.

Consumer repos own the product policy, provider SDK integration, runtime
implementation, telemetry, and provider-specific pricing or limit references.

Cautilus owns evaluator-backed behavior proof when the risk lives in agent
behavior, model routing judgment, or recovery quality rather than static code
shape.

Do not build an Anthropic-specific wrapper, retry library, streaming runtime, or
behavior-test runner in Charness. Provider-specific numbers can appear only as
source-bound examples. Ask the consumer repo to cite current provider docs when
it relies on pricing, cache multipliers, rate-limit semantics, or model names.

## Trigger Evidence

Apply this lens when repo evidence shows a production LLM or agent runtime, such
as:

- a model/API client in a serving path
- model routing, fallback, or provider configuration
- streaming response endpoints or event processors
- tool/action queues driven by model output
- runtime telemetry for model calls, tokens, retries, costs, or fallbacks
- user-facing agent product docs or operator runbooks only when paired with
  serving-path code, runtime configuration, telemetry, or concrete
  incident/runtime evidence

Do not trigger it from eval fixtures, skill docs, prompt examples, docs-only
agent product descriptions, harness-only agent orchestration, or offline
benchmark scaffolding by themselves. Those may need behavior-testing,
prompt-asset review, or concept/docs synchronization review, but they are not
production runtime evidence until paired with a concrete runtime seam.
Docs or runbooks that merely name a serving path, provider, or conceptual
procedure do not trigger this lens without corroborating runtime evidence.

## Review Questions

Treat these as review prompts, not mandatory architecture. A good answer may be
implemented proof, an explicit non-applicability note, or a deliberately
accepted product tradeoff.

### Cache And Cost Economics

- Does the repo claim cost or latency savings from prompt caching, batching, or
  context reuse?
- Are cache write and cache read tokens measured separately from ordinary input
  and output tokens?
- Is there a break-even argument for reuse count, cache key/version policy, and
  invalidation, or is caching treated as automatically cheaper?
- Are model prices, cache multipliers, and provider-specific token fields
  source-bound instead of hard-coded into Charness guidance?

Deterministic proof can include unit tests for cache key/version behavior,
structured telemetry fields, cost calculators with provider-doc citations, and
artifact examples that show read/write token counters.

### Overload And Fallback Policy

- Does transient provider overload, capacity failure, or rate limiting have an
  ordered degradation policy instead of unbounded same-model retry?
- Does the chain distinguish retry, older or cheaper model fallback, cached
  response, partial/degraded answer, and clean failure?
- Are fallback reasons and selected tiers recorded so cost and quality changes
  can be audited later?

Deterministic proof can cover retry limits, ordered fallback selection, and log
fields. Behavior proof may be needed when the concern is whether the degraded
answer is acceptable for a real user task.

### Retry And Idempotency

- Can a timeout followed by retry duplicate a provider call, charge, tool
  action, or user-visible side effect?
- Does the runtime use a request fingerprint, idempotency key, ledger, or dedupe
  store for non-idempotent paths?
- Do tests cover timeout-after-submit, worker restart, and replay cases where
  the original provider response is unknown?

Deterministic proof can usually own this. Escalate to behavior proof only when
the dedupe decision depends on agent interpretation of task state.

### Streaming Stall Recovery

- Does the stream handler model states such as started, token-received,
  silence-threshold-exceeded, stop-received, partial-returned, and failed?
- Is there a silence timeout or watchdog for streams that never deliver a final
  stop event?
- Can the product return, store, or discard partial output according to an
  explicit policy?

Deterministic proof can include fake stream fixtures and state-machine tests.
Behavior proof may be appropriate when partial-output usefulness or recovery
wording changes the agent experience.

### Model Routing Economics

- Are simple classification, extraction, moderation, or routing tasks defaulting
  to an expensive model without a confidence or difficulty signal?
- Is there a cheap-first path with escalation only for low confidence, ambiguous
  labels, high-risk actions, or known hard cases?
- Are escalation reasons, final model choice, and quality/cost outcomes logged?

Deterministic proof can pin routing thresholds and telemetry. Cautilus-backed
`fixture` or `observation` proof may be needed when the claim is that a
cheap-first route preserves task quality. Use `skill-experiment` only when the
runtime under review is itself a Charness skill or prompt variant.

## Recommendation Shape

When this lens finds a gap, record:

- runtime seam under review
- trigger evidence that made the lens applicable
- deterministic proof already present
- missing proof or missing explicit non-applicability decision
- behavior risk, if any, and likely Cautilus mode (`fixture` or `observation`;
  `skill-experiment` only for Charness skill or prompt variants)
- external/provider proof level using the shared external capability proof
  ladder
- current state: `healthy`, `weak`, `missing`, `deferred`, or
  `recommend_only`

Do not call a healthcheck, configuration surface, or queued worker a production
provider roundtrip. For external/runtime capability slices, use the proof ladder
from `../../../shared/references/external-capability-proof-ladder.md`; routine
quality review may recommend stronger proof without running a live provider
test.

## Enforcement Triage

- `AUTO_EXISTING`: the repo already has tests, logs, artifacts, or validators
  proving the relevant branch.
- `AUTO_CANDIDATE`: a low-noise check could verify config shape, telemetry
  fields, retry limits, or fake-stream state transitions.
- `NON_AUTOMATABLE`: product policy decides the acceptable fallback, partial
  answer, cost/quality tradeoff, or user-facing degradation.

Start with review and recommendation. Promote a static inventory or adapter
field only after repeated dogfood runs show a low-noise shape.
