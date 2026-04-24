# Session Retro: Delegation Policy Phrasing

## Context

The user challenged my final phrasing that cited a "host-level delegation
policy" after a quality review that should have respected this repo's
checked-in subagent delegation contract.

## Evidence Summary

- `AGENTS.md` explicitly says repo-mandated bounded fresh-eye, premortem,
  `init-repo`, and `quality` reviews are already delegated and must not wait
  for a second user message.
- `docs/handoff.md` records the same current-state rule for mandatory
  fresh-eye loops.
- The final response described the skipped delegated review as a host-policy
  limitation, which made the repo contract sound weaker than intended.

## Waste

Trust was lost because the final explanation blurred two distinct facts:
the repo has already opted into required bounded subagent review, while the
runtime/tooling instruction surface can still constrain what the assistant is
allowed to call in a given host. The useful answer should have named that
boundary directly instead of implying that the repo wording had not solved the
authorization problem it was designed to solve.

## Critical Decisions

- The repo contract is still the correct local policy: do not ask the user
  whether subagents are allowed for repo-mandated bounded reviews.
- When the host instruction stack prevents tool use despite that repo policy,
  report it as an instruction-stack/tool-contract conflict, not as a generic
  "host policy" that weakens the repo rule.

## Expert Counterfactuals

- Jef Raskin-style discoverability would have named the exact next action and
  blocker: "repo policy says spawn; current tool contract does not permit this
  call without explicit user delegation wording."
- Gerald Weinberg-style systems thinking would have separated the local system
  rule from the host runtime rule before closing, instead of compressing both
  into one vague cause.

## Next Improvements

- workflow: In final closeout, distinguish `repo_contract_requires_subagent`
  from `host_tool_contract_blocks_spawn` when both are true.
- memory: Treat future user corrections about subagent authorization as a sign
  to inspect the exact wording of both AGENTS and the active tool contract
  before explaining the blocker.
- capability: Consider a validator or canned quality closeout phrase that
  rejects vague "host policy" wording when the repo's bounded subagent rule is
  the relevant local contract.

## Persisted

yes: `charness-artifacts/retro/2026-04-24-delegation-policy-phrasing.md`
