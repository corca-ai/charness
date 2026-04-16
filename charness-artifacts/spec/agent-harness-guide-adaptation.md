# Spec — Agent Harness Guide Adaptation
Date: 2026-04-16

## Problem

`charness` already has many of the separations described in the external
`Agent Harness Guide v1.0`, but several of them remain implicit, scattered, or
chat-only:

- layer ownership is distributed across skill cores, references, repo docs,
  adapters, manifests, scripts, and runtime state, but there is no single
  contract that explains which surface owns which kind of rule
- instruction precedence and context assembly both exist in practice, but the
  repo does not yet distinguish them cleanly as separate concerns
- review-style work often depends on an evidence bundle (diff, logs, touched
  files, prior artifact, current question), yet the repo mostly encodes that as
  habit rather than as an explicit contract
- artifact durability rules exist in `docs/handoff.md` and skill-specific
  adapters, but there is no short cross-repo policy that maps fixed,
  semi-fixed, and variable knowledge to committed docs, rolling artifacts,
  dated records, and hidden runtime state
- when agent operating constraints change, the sync obligations between docs,
  review policy, adapter/state expectations, and closeout discipline are still
  partly social rather than visibly contractual

The useful adaptation is therefore not a vocabulary rewrite. It is a small set
of repo-owned contracts that make these seams inspectable and easier to verify.

## Current Slice

Design the adaptation as four implementation slices that can land
incrementally:

1. `Harness Composition Contract`
   - add one canonical doc that maps layer ownership, instruction precedence,
     and context assembly order using existing `charness` terms
2. `Review Evidence Contract`
   - tighten review-oriented guidance so `quality`, `premortem`, and adjacent
     review flows explicitly ask for the minimum evidence bundle they rely on
3. `Artifact Durability Contract`
   - add one short policy doc that maps fixed / semi-fixed / variable knowledge
     to committed docs, `latest.md`, dated records, and hidden runtime state
4. `Constraint-Change Sync Contract`
   - make it explicit which repo-owned docs or policy surfaces must move when
     agent operating constraints change, and define the smallest proof that the
     new contract is actually being used

## Fixed Decisions

- Keep existing `charness` vocabulary. Do not rename surfaces into `command`,
  `knowledge`, `controls`, and `execution` just to match the article.
- Do not add new user-facing modes. The adaptation must preserve the current
  strong-default stance.
- Treat the new composition doc as an index and boundary map, not as a second
  full architecture narrative. Canonical details should stay in the existing
  owning docs and references, with the composition doc linking outward instead
  of restating all nuance.
- Keep the public skill core lean. Nuanced layer mapping, evidence-bundle
  details, and artifact taxonomy belong in repo docs and references unless they
  clearly change trigger or workflow selection.
- Treat `quality` as the primary audit surface for layer ownership and review
  evidence discipline. Deterministic enforcement still belongs in repo-owned
  scripts and validators, per current `quality` policy.
- Treat instruction precedence and context assembly as distinct contracts.
  Precedence answers "which source wins when guidance conflicts"; assembly
  answers "what context is collected and in what order."
- Keep precedence explicitly `charness`-local. The doc should explain repo and
  harness composition order, not pretend to redefine host runtime
  system/developer/user precedence outside the repo's control.
- Start the artifact taxonomy as a documentation contract, not a new adapter
  schema field. Promote to schema only if repeated ambiguity remains after the
  policy doc lands.
- Keep the first sync-on-constraint-change step lightweight: docs and review
  policy updates first, new validators only where drift has already been costly.
- Require one consumer-visible proof path. At least one reviewed dogfood or
  quality artifact should show that the new contracts affect real review
  behavior rather than staying architecture prose.
- Pull that proof forward. Selecting the proof target is part of the first
  implementation slice, not a late optional follow-up after all docs land.

## Probe Questions

- Should one new canonical composition doc absorb precedence, assembly, and
  layer ownership together, or should precedence live inside an existing doc
  such as `runtime-capability-contract.md`?
  - Recommended answer: one new canonical composition doc; current precedence
    notes are too domain-specific to carry the general contract alone.
- Does the review evidence contract need a validator immediately?
  - Recommended answer: no. First land it in `quality` and adjacent references;
    promote to a script or validator only if a real miss repeats.
- Should the artifact durability contract stay cross-cutting, or should each
  skill continue to own its own policy independently?
  - Recommended answer: keep one short cross-cutting policy plus skill-specific
    adapter details. The repo already has enough shared shape to justify a
    common map.
- Does constraint-change sync belong in `.agents/surfaces.json` now?
  - Recommended answer: not yet as a new dedicated surface. Existing markdown,
    skill, policy, and adapter surfaces already cover most verification. Add a
    dedicated surface only if the first implementation still leaves misses.

## Deferred Decisions

- Whether artifact durability should later become machine-readable metadata such
  as `durability_class` in adapters or manifests
- Whether review evidence should later get a helper script that inventories the
  presence of diff/log/question/proof inputs before a review artifact is
  written
- Whether the composition contract eventually deserves executable acceptance
  coverage in `specdown`
- Whether constraint-change sync should become a new explicit closeout surface
  in `.agents/surfaces.json`
- Whether `debug`, `hitl`, or GitHub plugin workflows should consume a shared
  evidence-bundle helper instead of repeating similar guidance in references

## Non-Goals

- renaming existing repo concepts to mirror the external article
- adding a new top-level public skill
- introducing a planner/reviewer product split or more explicit user mode menus
- creating a mandatory ADR bureaucracy beyond the repo's existing decision and
  handoff surfaces
- rewriting every current doc to use the new framing

## Deliberately Not Doing

- No host-specific behavior in the new contracts. Host/runtime details stay in
  adapters, manifests, and integration docs.
- No attempt to solve all source-of-truth drift with one new validator before
  the repo has proven which drift is actually recurring.
- No new hidden runtime state for review evidence. The first step is visible
  contracts, not more session state.
- No generic "architecture overview" doc that duplicates existing docs without
  naming the concrete ownership and sync questions future maintainers need to
  answer.

## Constraints

- Manually maintained repo docs stay in English.
- `spec` remains adapter-free. The canonical artifact for this design should
  therefore live in a checked-in spec document, not in a new adapter-managed
  state path.
- Any change to public skill text or references must keep the concise-core
  policy intact and pass current skill/package validation.
- Any design that touches checked-in docs must keep markdown, secrets, and
  local link validation green.
- The adaptation must preserve current decisions in
  `docs/deferred-decisions.md`, especially `quality` as proposal/review skill
  and `spec` as heuristic, not mode-heavy.

## Success Criteria

1. Maintainers can open one canonical doc and answer:
   - which layer owns a rule
   - which instruction source wins on conflict
   - how turn context is assembled before execution
2. Review-oriented guidance names the minimum evidence bundle explicitly enough
   that `quality` or adjacent review artifacts no longer rely on unstated local
   habits.
3. The repo has one short artifact-policy doc that maps:
   - fixed knowledge -> committed docs
   - semi-fixed knowledge -> rolling artifacts such as `latest.md`
   - variable knowledge -> dated records or hidden runtime state, depending on
     whether the state must remain operator-visible
4. Constraint changes to agent behavior or review policy visibly name the
   affected sync surfaces instead of relying on chat-only memory.
5. At least one reviewed proof surface shows the new contract in use: either a
   refreshed dogfood case, a quality artifact, or a closeout rule that cites
   the new contract directly.
6. The new docs do not create a second conflicting truth surface. Each one
   explicitly names where detailed owning guidance still lives.

## Acceptance Checks

- `docs/harness-composition.md` exists and covers:
  - layer ownership map
  - instruction precedence order
  - context assembly order
  - examples using existing `charness` surfaces
  - explicit "authoritative detail lives in ..." cross-links so the doc acts as
    a boundary map rather than a duplicate handbook
- `docs/artifact-policy.md` exists and maps committed docs, `latest.md`, dated
  records, and hidden runtime state to durability classes with current repo
  examples
  - including explicit exceptions where current skill behavior intentionally
    diverges from the default pattern
- `skills/public/quality/` guidance explicitly asks for:
  - the decision/review question
  - fresh source inventory
  - relevant diff or changed surface
  - command output or logs when the claim depends on runtime behavior
  - prior artifact only as context, not as authoritative truth
- `skills/public/premortem/` or another adjacent review reference explicitly
  calls out document/source-of-truth cascade risk when a rule change should
  propagate across multiple surfaces
- `docs/handoff.md` points the next implementation session at this spec when the
  adaptation is the active workstream
- the first implementation slice names one concrete proof target up front:
  - refreshed `quality` artifact
  - reviewed public-skill dogfood case
  - or one focused closeout rule tied to the new docs
- Validation passes:
  - `./scripts/check-markdown.sh`
  - `./scripts/check-secrets.sh`
  - `python3 scripts/check-doc-links.py --repo-root .`
  - `python3 scripts/validate-skills.py --repo-root .` if public skill
    references change

## Premortem

- A rushed implementer may overreact and create a big new architecture doc that
  duplicates existing policy instead of naming the few missing contracts. The
  slice must stay narrow and practical.
- Another likely failure is turning review evidence into a rigid checklist in
  public skill core. That would bloat `SKILL.md` files and fight the repo's
  concise-core discipline.
- A third risk is defining precedence but not distinguishing it from context
  assembly, which would preserve the original confusion under nicer wording.
- Another failure mode is documenting artifact durability in a way that
  contradicts current `handoff`, `debug`, `gather`, or `retro` behavior. The
  policy doc must describe current shared shape first, then name exceptions.
- The biggest false sense of completion would be landing only docs with no
  proof surface. At least one review-facing artifact or dogfood case must show
  the design changed actual maintenance behavior.
- Another likely miss is writing precedence as if `charness` controls the whole
  host instruction stack. The contract must stay scoped to repo-owned guidance
  composition and explicitly avoid claims about host/runtime layers it does not
  own.
- A more subtle failure is creating a clean boundary map that no current review
  workflow actually consumes. The first slice should therefore choose a proof
  target immediately so the design cannot end as passive documentation alone.

## Canonical Artifact

This document: `charness-artifacts/spec/agent-harness-guide-adaptation.md`

If implementation discovers a better seam or a lighter proof path, update this
spec rather than leaving the change only in chat.

## First Implementation Slice

`Slice 1 — Composition + Durability docs`

Land the lowest-risk, highest-leverage clarification first:

1. Add `docs/harness-composition.md`.
   - map current surfaces:
     - public skill core
     - references
     - repo docs
     - adapters
     - integration manifests
     - validators/scripts
     - hidden runtime state
   - separate instruction precedence from context assembly
   - include one or two concrete examples using current `quality`, `gather`, or
     adapter workflows
   - keep the doc pointer-heavy: link to owning docs instead of duplicating
     detailed policy text already maintained elsewhere
2. Add `docs/artifact-policy.md`.
   - define fixed / semi-fixed / variable knowledge
   - map each class to current repo surfaces
   - record the current exceptions intentionally rather than pretending one rule
     fits every skill
3. Choose the first proof target immediately.
   - default recommendation: refresh one `quality` review or one reviewed
     dogfood case after the docs land so the new contracts affect a real
     maintenance workflow
4. Update `docs/handoff.md` to point future work at this spec when this
   adaptation is active and name the chosen proof target.
5. Run doc validation:
   - `./scripts/check-markdown.sh`
   - `./scripts/check-secrets.sh`
   - `python3 scripts/check-doc-links.py --repo-root .`

`Slice 2` should then tighten `quality` and adjacent review references around
the evidence bundle and ownership audit. `Slice 3` should land the chosen proof
path if it did not already fit into Slice 2. `Slice 4` should revisit whether
any of the new contracts justify a validator or changed-surface rule.
