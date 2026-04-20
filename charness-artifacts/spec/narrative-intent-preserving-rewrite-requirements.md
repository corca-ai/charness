# Narrative Intent-Preserving Rewrite Requirements
Date: 2026-04-20

## Goal

Make the `narrative` skill better at producing a good README for interested
users without turning the public skill into a `charness`-shaped template.

The public skill should help an agent recover a repo's real story, preserved
intent, and best first-touch structure. Repo-local adapters should then carry
the repo-specific priorities, warnings, and special cases.

## Problem Statement

Recent README work in `charness` surfaced three related failures:

1. structural cleanup can erase preserved intent
2. internal design language can leak into user-facing README prose
3. the agent can remember source docs but still fail to carry forward explicit
   user intent already clarified in-thread

The fix is not a rigid README template. The fix is stronger intent recovery,
clearer intent-preserving rewrite checks, and cleaner separation between public
skill behavior and repo-local adapter expectations.

## Public Skill Requirements

These belong in the public `narrative` skill because they are portable across
repos.

### 1. Reader-first rewrite

`narrative` should optimize for the repo's interested reader, not for internal
doc inventory alone.

The skill should ask:

- who is the first-touch reader
- what must that reader understand first
- what should stay below the fold or move into owner docs

### 2. Intent inventory before rewrite

Before rewriting a README or other landing doc, `narrative` should inventory:

- current explicit intents in the source docs
- user-confirmed intents from the current thread
- any high-signal distinctions that the rewrite must preserve even if headings
  and section order change

The rewrite should not start from "what is a neat outline?" It should start
from "what meaning must survive?"

### 3. Preserve, move, compress, or delete explicitly

For high-signal prior sections or concepts, `narrative` should classify each as:

- preserved in place
- moved elsewhere
- compressed into another block
- intentionally deleted

If deleted, the skill should say why the old intent is no longer needed instead
of treating deletion as self-justifying simplification.

### 4. Distinguish concept from layout

The public skill must keep structure flexible.

- ordered section titles are suggestions, not the contract
- the contract is preserved intent and honest first-touch guidance
- repos may need different section names or different ordering

### 5. Quick Start must model who acts

When a landing page includes a quick start, `narrative` should ask:

- is the human the primary executor
- or is the right move to hand the install/use contract to an agent

The skill should not assume that "Quick Start" means human CLI steps.

### 6. Internal language filter

`narrative` should challenge internal terms that may be meaningful to
maintainers but unclear to interested readers.

Examples of risky categories:

- internal architecture shorthand
- repo-native jargon that was never defined
- design words that sound precise internally but vague externally

The skill should prefer user value language first, then define any necessary
product-local term at first use.

### 7. Core concepts before feature catalog when appropriate

When the repo's identity depends on a few high-leverage concepts, `narrative`
should be able to surface a compact concept table or concept list near the top
instead of jumping straight into feature or skill inventory.

This is optional and repo-shaped:

- some repos need scenario-first entry
- some repos need quick-start-first entry
- some repos need concept-first entry

The public skill should decide this based on reader need, not habit.

### 8. Skill map should connect back to concepts

If the README includes a skill map, `narrative` should check whether the map is
just a list or whether it helps the reader understand the repo's core concepts.

A good map may:

- group by intent
- group by actor direction
- separate special entrypoints from ordinary flows
- distinguish user-facing concepts from support/tool layers

### 9. Communication is a first-class design question

`narrative` should be able to recognize when a repo's communication layer is
part of the product story.

In those repos, it should ask:

- who is speaking
- who is receiving
- why those communication paths need different artifacts or formats

### 10. Carry-forward check before closeout

Before stopping, `narrative` should run a short explicit check:

- which user-stated intents from the current thread were preserved
- which were intentionally challenged
- which are still unresolved

This should become part of the workflow, not only a chat habit.

## Repo-Local Adapter Requirements For `charness`

These should stay repo-local because they describe what *this* repo wants from
`narrative`, not what every repo should want.

### 1. Core concept emphasis

The adapter should let `charness` declare that README rewrites must protect
high-signal concepts such as:

- less is more / trust capable agents
- human-code-AI symbiosis
- shared logic with repo-local growth
- agents as first-class users
- concepts first, tools second
- quality as the foundation for trusted autonomy
- communication shaped by who speaks to whom
- expert tacit knowledge becoming workflow
- the system getting smarter with use

### 2. Terms to avoid or downgrade

The adapter should be able to record internal language that often sounds worse
than the underlying user value when used too early in a README.

Current candidates:

- `portable`
- `surface`
- `seam`
- `repo-owned agent work`

These are not forbidden everywhere, but they should not dominate the first
touch unless the README already earned them.

### 3. Quick Start execution model

The adapter should let `charness` say that Quick Start usually means:

- tell a human where the canonical install contract lives
- provide an agent-facing prompt when agent execution is the preferred path
- do not assume the human wants the full install procedure inline in README

### 4. Public skill map expectations

The adapter should let `charness` preserve repo-specific grouping choices such
as:

- `init-repo` as a distinct entrypoint, not just one item in a flat list
- `quality` and `retro` as quality-improvement loops, not mere post-impl cleanup
- communication grouped by speaker/receiver direction
- support skills and integrations explained as non-public tool layers

### 5. Owner-doc boundary reminders

The adapter should help `narrative` remember which deeper details belong
outside the README.

For `charness`, the README should not silently absorb:

- full install contract
- full packaging contract
- full operator takeover contract
- deeper validation policy

### 6. README-specific danger checks

The adapter should be able to encode a few current failure patterns worth
checking explicitly during README rewrites:

- over-flattening the public skill map
- making `find-skills` sound like a normal end-user command instead of mostly
  an internal/default routing aid
- placing `cautilus` as a top-level product contrast instead of in the support
  integration layer
- adding low-value inventory sections that do not help first-touch readers

## Suggested Adapter Extensions

Potential new adapter fields for `charness`:

- `primary_reader_profiles`
- `preserve_intents`
- `terms_to_avoid_in_opening`
- `quick_start_execution_model`
- `special_entrypoints`
- `skill_grouping_rules`
- `owner_doc_boundaries`
- `landing_danger_checks`

These are suggestions, not yet the canonical schema.

## Non-Goals

- Do not turn `narrative` into a rigid README template generator.
- Do not encode `charness` section names as global defaults.
- Do not force every repo to use a concept table.
- Do not treat structural elegance as success if preserved meaning was lost.

## Recommended Implementation Order

1. update the repo-local adapter contract for `charness`
2. update `narrative` public workflow to require intent inventory and
   carry-forward checks
3. add or revise reference material for landing-page intent preservation
4. only then build `cautilus` fixtures and GEPA loops against the new contract
