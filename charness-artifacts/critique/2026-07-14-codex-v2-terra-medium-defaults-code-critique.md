# Codex V2 Terra/Medium Default Critique
Date: 2026-07-14

## Decision Under Review

Make Charness's Codex subagent default explicit and enforceable: request
`gpt-5.6-terra` with `medium` reasoning effort and, in MultiAgent V2, use
`fork_turns: "none"` unless bounded parent history is consciously required.
Preserve the existing standing authorization for agents to choose dynamic
workflows when their benefit justifies their cost.

Packet Consumed:
`charness-artifacts/critique/2026-07-14-104105-packet.md`.
The three angle passes respectively consumed
`2026-07-14-103252-packet.md`, `2026-07-14-103608-packet.md`, and
`2026-07-14-103913-packet.md` from the same directory before the separate
counterweight pass consumed the packet named above.

## Failure Angles

- Spawn-contract correctness: a full-history V2 fork rejects caller-provided
  model and reasoning overrides, and an agent role can still replace accepted
  values.
- Policy propagation: live adapters, scaffolds, public references, root
  instructions, setup normalization, and the generated plugin must agree.
- Setup safety: policy inspection must find genuinely Charness-managed
  repositories without treating a casual mention of Charness as ownership, and
  harmless Markdown formatting must not create a false drift finding.
- Runtime honesty: requested spawn fields, host acceptance, and provider-side
  application are distinct claims.

## Counterweight Pass

- The initial missing setup-adapter drift checks, missing existing-AGENTS
  recommendations, loose Charness-management predicate, and Markdown-sensitive
  policy detector were real blockers. The final diff adds targeted checks and
  regressions for each.
- The shared portable adapter must carry `fork_turns` but must not become a
  Codex-only validator. Codex default enforcement therefore lives in the
  Codex-aware setup inspection path.
- Do not claim provider application from a successful spawn request. The
  public mapping now labels its fields as requests and requires host
  confirmation before recording application.
- Do not add a provider-runtime probe or rewrite arbitrary consumer AGENTS in
  this slice. Those require host-visible evidence or a separate policy change.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: `scripts/setup_agent_docs_lib.py` | action: fix | note: enforce both reviewer tiers' Codex Terra/medium/none defaults and report configuration drift; applied
- F2 | bin: act-before-ship | evidence: strong | ref: `scripts/setup_agent_docs_lib.py` | action: fix | note: inspect existing Charness-managed AGENTS for missing dynamic-workflow and profile policy without rewriting user content; applied
- F3 | bin: act-before-ship | evidence: strong | ref: `scripts/setup_agent_docs_lib.py` | action: fix | note: require complete Skill Routing evidence rather than a bare `charness` substring, and normalize harmless Markdown decoration; applied
- F4 | bin: bundle-anyway | evidence: strong | ref: `skills/public/critique/references/adapter-contract.md` | action: document | note: distinguish requested fields from host/provider application and state the role override caveat; applied
- F5 | bin: over-worry | evidence: moderate | ref: `scripts/critique_adapter_lib.py` | action: defer | note: do not make the portable adapter parser Codex-only by validating V2 enum values globally
- F6 | bin: valid-but-defer | evidence: strong | ref: Codex MultiAgent V2 runtime | action: defer | note: provider-side model/effort application needs an explicit host confirmation surface; request submission is not that proof

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `model=gpt-5.6-terra`,
  `reasoning_effort=medium`, `fork_turns=none` (sent for this review).
- Host exposure state: requested_fields_sent
- Application state: unverified-by-host; the spawned-agent surface did not
  expose resolved provider model or reasoning metadata.

## Fresh-Eye Satisfaction

parent-delegated. Three distinct bounded angle reviews covered spawn-contract
correctness, setup/policy propagation, and package/runtime truthfulness. A
separate counterweight pass triaged their findings, and a final independent
review checked the Markdown-normalization repair. Parent-side
worktree/index-fingerprint verification reported no drift after every accepted
review.

## Boundary Ownership

- Producer: the critique adapter provides requested reviewer-tier fields;
  setup inspection recognizes and reports configuration policy.
- Consumer: Charness skills and generated AGENTS guidance issue the host spawn
  call; Codex MultiAgent V2 validates and applies (or rejects) the request.
- Owning surface: portable field transport stays in the critique adapter;
  Codex-specific defaults and drift reporting stay in Charness's setup policy;
  provider application evidence stays with the host runtime.
- Verdict: owned-correctly
