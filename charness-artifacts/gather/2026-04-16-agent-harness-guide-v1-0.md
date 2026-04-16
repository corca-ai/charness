# Gather: Agent Harness Guide v1.0

## Source

- URL: <https://www.linkedin.com/pulse/agent-harness-guide-v10-jooyeong-oh-63znc>
- Title: `Agent Harness Guide v1.0`
- Author: Jooyeong Oh
- Published: 2026-04-15
- Accessed: 2026-04-16 UTC

## Freshness

The article was reviewed directly from the public LinkedIn page on
2026-04-16 UTC. No repository-local copy of the source existed before this
gather pass.

## Requested Facts

There is material worth learning from, but mostly as framing and audit
language, not as a new architecture for `charness`.

Most reusable ideas:

- Responsibility planes are named cleanly. The article separates harness
  concerns into command, knowledge, controls, and execution planes. `charness`
  already has similar separation across skills, adapters, manifests, scripts,
  and runtime state, but this four-plane framing is a clearer review lens than
  many current repo docs.
- Precedence order versus assembly order is called out explicitly. The article
  distinguishes "which instruction wins" from "how context is assembled for the
  model." That distinction is useful for `charness` because public skill
  contracts, host adapters, profiles, and runtime state often interact, and
  unclear ordering is a common source of drift.
- Planning and review are treated as policy-bearing layers, not as hidden model
  behavior. That matches `charness` well. The article reinforces that these
  should be made inspectable and, where possible, testable.
- Fixed, semi-fixed, and variable knowledge is a useful durability taxonomy.
  It provides a simple way to reason about what belongs in committed docs,
  generated artifacts, and session/runtime state.
- The evidence bundle idea is strong. The article suggests carrying prior plan,
  diff, logs, and touched-file context into review instead of relying on vague
  "look at the code" prompts. This maps directly to `quality`, `debug`, and
  GitHub review workflows.
- The article treats architecture decision records and harness docs as coupled.
  That is a good reminder for `charness`: if a repo changes how agents are
  constrained or composed, the operator-facing contract should move with it.

What looks genuinely new for `charness` is not the high-level shape, but the
auditability of the shape. The article is strongest when it turns familiar
concepts into checkable questions:

- Which layer owns what?
- Which layer is durable versus session-scoped?
- Which instruction source overrides which?
- Which evidence package is required before review?

What not to copy directly:

- Do not rename existing `charness` surfaces just to match the article's
  vocabulary. The repo already has working terms such as skills, adapters,
  manifests, artifacts, and runtime state.
- Do not add more user-facing modes because a conceptual model permits them.
  `charness` explicitly prefers strong defaults over exposing many modes.
- Do not leave these ideas as prose-only architecture. In this repo, the right
  adoption path is validators, helper scripts, adapter contracts, and artifact
  policy, not a larger conceptual doc alone.

## Candidate Charness Adaptations

1. Add a lightweight "plane ownership" check to `quality` or `premortem` when a
   repo introduces a new policy/rule surface. The check should ask whether the
   concern belongs in public skill text, adapter logic, integration manifest,
   runtime state, or validator code.
2. Where `charness` documents instruction composition, state precedence order
   separately from context assembly order. This would reduce confusion when a
   host policy, profile, and skill all touch the same turn.
3. Reuse the article's fixed / semi-fixed / variable framing in artifact-policy
   docs or references when deciding whether something belongs in committed docs,
   `latest.md`, dated records, or hidden runtime state.
4. Strengthen review-oriented workflows with an explicit evidence bundle
   contract so "review" means input package plus checks, not only a role prompt.
5. Keep ADR and harness-doc synchronization explicit when agent operating
   constraints change; the article is right that these drift separately unless
   the workflow makes the coupling visible.

## Open Gaps

- This gather pass reviewed the public LinkedIn article only. It did not inspect
  any companion repository, slides, or implementation examples.
- The article appears conceptual rather than normative. It does not provide a
  full operational contract for validators, adapters, or install/update flows.
- Any real `charness` adoption should be justified against current repo
  surfaces, not only against the article's terminology.
