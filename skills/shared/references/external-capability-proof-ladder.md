# External Capability Proof Ladder

Use this when a slice depends on an external or runtime capability — a
host-mediated CLI, a third-party API, a runtime grant, or a host-bridge
operation that must cross the worker → host → provider seam.

This ladder is about **what was actually proven**, not about which tool to
prefer. For tool selection, see `impl/references/verification-ladder.md`.

## The Five Levels

Each level is strictly stronger than the one above it. A slice should declare
the highest level it actually executed and any level it intentionally left
unproven.

1. `surface` — the command, skill section, help text, setup checklist, or
   manifest entry exists. Operators can find it.
2. `worker_queued` — the user-shaped action reaches the host or capability
   bridge from the worker side. Argument parsing, target resolution, and
   permission scoping all complete; the request is shaped correctly enough to
   hand off.
3. `host_decision` — the host (or capability layer) inspects credentials,
   target, installation, and policy and returns a structured accept or reject.
   This is where missing-setup and not-authorized states become real.
4. `provider_roundtrip` — the third-party provider accepts the request and
   returns a parsed response or observable side effect. The worker → host →
   provider seam produced a real outcome.
5. `agent_choice` — given the user's natural-language request, an evaluator,
   a fresh agent, or a Cautilus-style scenario chooses the intended skill or
   command. This level proves that the surface is reachable through prompt
   routing, not only through the documented invocation.

`provider_roundtrip` proves the seam works. `agent_choice` proves the surface
is selectable. Both can be required for a closeout to be honest.

## Readiness Is Not Action Proof

`surface`, `worker_queued`, and a healthcheck-style `host_decision` together
still describe a ready system. They do not prove that the user-shaped action
crosses the seam and reaches the provider.

Common false-pass shapes:

- the help text and setup checklist render, so the slice claims the capability
  works
- a list/inventory call succeeds, so the create/comment/close path is assumed
  to work too
- a fresh-agent dogfood picks the right command, but no executed
  request → response was observed
- a host-side credential resolves, but the request shape was never accepted by
  the provider

Treat readiness as `host_decision` at best. The action-shaped proof must rise
to `provider_roundtrip` before the action surface can be called proven.

## Closeout Discipline

When the slice changes anything that crosses the worker → host → provider
seam, the closeout names:

- the highest proof level executed for each affected action
- the level intentionally not proven and the concrete reason (missing
  credentials, host blocks subagent, no test target, deferred to the next
  slice)
- whether `agent_choice` ran or not, distinguished from
  `provider_roundtrip`; passing one does not imply the other

Closeout phrasing example:

```text
External capability: github.issue
- surface: yes (skill, help, integration manifest)
- worker_queued: yes (preflight returns selected_backend)
- host_decision: yes (gh auth status, ceal capability resolved)
- provider_roundtrip: not run (no test target repo configured)
- agent_choice: not run (deferred to fresh-agent dogfood)
```

A slice that only proves through `host_decision` is not closable as
`capability action works end to end`. It is closable as `capability is ready`.

## Mapping To Existing Concepts

- `impl` strongest-honest verification → choose the level you can credibly
  reach for this slice; do not skip an executable level when credentials or
  a test target exist.
- `quality` enforcement triage → readiness-only proofs for action-shaped
  surfaces are `Weak` until at least one `provider_roundtrip` exists.
- `create-skill` portability seam → a skill that depends on an external
  capability declares which proof levels apply and which the host must
  satisfy.
- `create-cli` action-shaped self-tests → mutating subcommands should have at
  least one `provider_roundtrip` fixture or a recorded reason it cannot run
  in CI.
- `issue` resolution critique → recurrence prevention should name the proof
  level that, if monitored, would catch the regression earliest.

## Common Anti-Patterns

- collapsing `host_decision` into `provider_roundtrip` because the host
  returned a structured ok response without ever calling the provider
- inferring `provider_roundtrip` from a mocked unit test
- claiming `agent_choice` because the documented command exists, without ever
  observing a fresh agent or evaluator pick it from a natural-language prompt
- treating a single level as the whole capability when several action shapes
  exist (create vs read vs delete may each need their own ladder pass)

## Source Bindings

- `impl/references/verification-ladder.md` — strongest-honest tool selection
- `impl/references/external-api-contract.md` — recurring traps mocked tests
  miss
- `create-cli/references/external-capability-clis.md` — worker → host
  boundary, audit-safe output
- `create-skill/references/runtime-capabilities.md` — preferred access order
- `quality` — readiness-versus-action enforcement triage
