# Portable Authoring Contract

This is the canonical authoring contract for new or migrated `charness`
artifacts.

## Artifact Classifier

Choose the target surface before writing files.

| Artifact | Owns | Does not own | Canonical path |
| --- | --- | --- | --- |
| public skill | one user-facing concept | external tool installs, host defaults | `skills/public/<skill-id>/` |
| support skill | harness-owned tool usage guidance and owned runtime helpers | public taxonomy, binary ownership | `skills/support/<skill-id>/` |
| profile | default bundle selection | host-specific secrets or runtime wiring | `profiles/<profile-id>.json` |
| preset | opt-in default values and vocabulary | mandatory hidden behavior | `presets/<preset-id>.md` |
| integration | external ownership, detection, degradation | product philosophy | `integrations/tools/<tool-id>.json` |
| support capability metadata | machine-readable contract for `charness`-owned runtime | true external ownership | `skills/support/<skill-id>/capability.json` |

If the answer is "two of these at once", split the work.

## Portable JSON Artifacts

JSON artifacts under `.charness/` or `charness-artifacts/` are repo state when
committed. Store repo-root-relative paths in those files. Absolute host paths
are acceptable in transient stdout diagnostics, but not in durable artifacts a
different clone or CI job may read later.

## Skill Brief

Write this before editing:

```text
Name: create-skill
Audience: agent
Trigger: create, migrate, or improve a charness skill
External: WebSearch, optional tool manifests
Repo-specific: adapter paths, preset ids, output paths
Accumulates: only when the migrated skill needs durable notes
```

## Scenario Simulation

Simulate these before implementation:

1. cold start
2. warm start
3. error recovery
4. agent failure modes

Agent failure modes must be concrete. Good examples:

- edits `SKILL.md` before proving the boundary is public vs support
- hardcodes host or repo names into a portable skill
- hides an external dependency behind a one-off shell command
- assumes direct `.env` or secret-file access in a runtime that may be isolated
- copies an upstream support skill even though a manifest plus sync strategy
  would be enough
- treats `unset` and `explicitly empty` as the same thing and keeps re-asking
- leaves rationale in the body instead of moving it into `references/`
- forgets to validate example metadata against the schema it just changed

## Bootstrap Ordering

Put checks in dependency order:

1. required repo context
2. required existing source skill or adjacent files
3. external integration contracts when the skill uses a tool
4. profile or preset context when the change affects bundle defaults
5. cross-session notes only if the skill accumulates state

User-blocking setup comes first. Auto-creatable defaults come after the
blocking checks they depend on.

## Option Minimalism

Modes and options are expensive. They often record design indecision rather
than user need.

Before adding one, ask:

1. can the skill infer the right behavior from context, existing artifacts, or
   the request wording?
2. can a stronger default serve most users better than a visible choice?
3. are the behaviors truly distinct enough that collapsing them would harm the
   user?

Prefer the skill designer taking responsibility for good defaults over pushing
that burden onto the user.

Add an explicit mode or option only when:

- the behaviors are meaningfully different
- the difference matters to user value, not only to implementation neatness
- inference would be risky or dishonest

`mode/option` is not the default answer to ambiguity.

## Reasoned Proposal Rule

When proposing a non-blocking default, also state why.

Good:

- `portable-defaults` fits because the repo has no host-specific preset schema
  yet and already uses repo-owned metadata under `profiles/` and
  `integrations/`.

Bad:

- use `portable-defaults`

If the user declines a proposed optional field, record that as an explicit
empty or explicit alternative so later runs do not ask again.

## Named Anchor Rule

Use a real-person name in `SKILL.md` core when it materially improves retrieval
of a useful reasoning frame from pretraining. This is a positive tool, not only
an exception.

Good:

- Daniel Jackson in a concept-shaping skill where boundary honesty, source of
  truth, and one clear user-facing concept are central
- Gary Klein in a premortem-bearing skill where likely failure modes and wrong
  next actions should be surfaced before closeout
- Ward Cunningham in a spec skill where executable acceptance artifacts should
  stay at the boundary instead of becoming a duplicate unit suite

Bad:

- adding a famous name only to signal taste
- adding several names that all retrieve the same mental move
- stripping a strong public-core anchor into references only when the retrieval
  benefit belongs in `SKILL.md`
- leaving the name in a reference when the public trigger contract is where the
  retrieval benefit actually matters

Keep the anchor sparse, factual, and attached to a concrete move. Put the
source-faithful essence, nuance, and reference contents in `references/`.

If the same philosophy should shape several adjacent skills, encode the
behavioral translation in each public core and keep only the anchors that
materially improve retrieval there.

If the name is optional color rather than a meaningful retrieval anchor, leave
it out of the public core.

## Expert Reference Hygiene

When you add a named anchor or expert reference:

- keep the public-core claim close to what the source actually supports
- compress to the few moves the skill really needs, not a mini-biography
- verify fuzzy or non-obvious paraphrases before shipping them
- prefer one strong anchor plus a behavior rule over a pile of overlapping names

## Progressive Disclosure Rule

Let `SKILL.md` own selection and sequencing.

- put "when this matters" and "which reference to read" in the skill core
- keep references focused on the payload: core moves, nuance, edge cases,
  examples, and anti-overclaim
- do not let a reference become a second workflow that re-decides when to act

## Runtime Capability Rule

Assume the skill may run in both:

- isolated runtimes that can provide capability grants
- ordinary local coding environments that rely on authenticated binaries or env
  fallback

Prefer designing the public skill and integration surface so:

1. grant-first works cleanly
2. authenticated-binary reuse works next
3. env fallback remains possible without becoming the canonical mental model

Do not put raw secret-handling rituals in the public skill body.

## Adapter Fallback Rule

Every adapter-using public skill should declare one fallback posture:

1. `allow`: missing adapter may stay implicit because the work is local,
   reversible, and not repo-truth-defining
2. `visible`: missing adapter may continue only when the skill says it is
   using inferred defaults and does not pretend those defaults are repo-owned
3. `block`: missing adapter must stop the skill before it rewrites
   high-leverage truth, review, or release surfaces

Use `block` when the skill would otherwise invent repo truth, delivery policy,
human-review state, or release boundaries. Use `visible` when inference is
acceptable only if the repo-contract gap stays explicit. Use `allow` only when
the work is narrow enough that hiding the bootstrap step is not misleading.

## WebSearch Rule

If a step requires outside examples, standards, or upstream tool behavior, call
WebSearch explicitly instead of vaguely asking the agent to "research more".

- search with the exact tool, runtime, or error text
- prefer primary sources such as upstream repos or official docs
- store the conclusion in the changed reference or migration notes instead of
  leaving it as transient chat context

## File Layout

Keep packages minimal:

```text
skills/public/<skill-id>/
  SKILL.md
  references/
  scripts/
skills/support/<skill-id>/
  SKILL.md
  capability.json
profiles/<profile-id>.json
presets/<preset-id>.md
integrations/tools/<tool-id>.json
```

`SKILL.md` is the trigger contract and decision skeleton. Long explanations,
schemas, anti-patterns, and examples belong in `references/`.

## Helper Script Rule

If a skill repeatedly depends on deterministic steps such as:

- adapter resolution
- adapter initialization
- durable artifact upsert or naming
- validation of repeated fields
- bootstrap checks with stable output

then ship a helper script instead of leaving the process as prose-only
instructions.

Good scripts reduce cold-start variance and make error recovery real. A future
session should not have to reinterpret the same ritual from scratch.

## Cross-Skill Propagation Rule

When a high-leverage reasoning pattern lands in one public skill, inspect
adjacent public skills before stopping.

Check for:

- obvious missing symmetry in the same cluster
- new named anchors that belong in more than one public core
- review or closeout steps that now look inconsistent across neighboring skills

Do not force perfect uniformity. Propagate only when the same user-facing
concept pressure is genuinely present.

## Reuse Rule

Default to porting before inventing:

1. inspect the upstream or prior-repo skill
2. keep the useful workflow spine
3. delete host-specific assumptions
4. move variable details into adapters, presets, or integration manifests
5. only then add new material

`create-skill` should preserve good existing structure, not reward rewriting
from zero.

## Verification

Before stopping:

- check trigger overlap with nearby skills
- verify every mentioned path exists
- validate changed JSON examples against repo schemas
- run scripts with `--help` or dry-run paths when present
- reread the body once for hidden host assumptions
