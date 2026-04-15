# Gather Review: `insane-search` vs `charness` `gather` and `web-fetch`

## Source

- External upstream repo: `https://github.com/fivetaku/insane-search`
- External upstream skill: `https://github.com/fivetaku/insane-search/blob/main/skills/insane-search/SKILL.md`
- External upstream references:
  - `https://github.com/fivetaku/insane-search/blob/main/skills/insane-search/references/jina.md`
  - `https://github.com/fivetaku/insane-search/blob/main/skills/insane-search/references/fallback.md`
  - `https://github.com/fivetaku/insane-search/blob/main/skills/insane-search/references/public-api.md`
  - `https://github.com/fivetaku/insane-search/blob/main/skills/insane-search/references/json-api.md`
- Local `charness` sources:
  - `skills/public/gather/SKILL.md`
  - `skills/public/gather/references/capability-contract.md`
  - `docs/support-skill-policy.md`
  - `docs/external-integrations.md`
  - `docs/control-plane.md`
  - `docs/gather-provider-ownership.md`
  - `profiles/profile.schema.json`

## Canonical Asset

- `charness-artifacts/gather/gather.md`

## Freshness

- Inspected on 2026-04-13 UTC.
- External repo state inspected from GitHub `main` plus a fresh shallow clone.

## Requested Facts

### 1. What `insane-search` actually is

`insane-search` is primarily a documentation-heavy support skill and plugin
surface, not a deep local runtime implementation. Its value is:

- a domain-to-strategy routing table
- a concrete fallback order after `WebFetch` failure
- platform-specific recipes for blocked sites
- lightweight response-validation heuristics

It does not appear to ship a broad reusable execution framework beyond those
checked-in instructions and examples.

### 2. Current `charness` position

`charness` already has a strong public contract for `gather`:

- durable artifact first
- source priority and provenance
- clear capability/access-mode ordering
- provider/runtime ownership boundaries

But `web-fetch` is currently only visible as a policy/schema concept:

- listed in `docs/support-skill-policy.md`
- allowed in `profiles/profile.schema.json`
- not present as a checked-in `skills/support/web-fetch/` support skill
- not present as an `integrations/tools/web-fetch*.json` manifest

So today there is a real product seam for `web-fetch`, but not yet a shipped
implementation surface.

## Analysis

### High-confidence improvement opportunities

1. Create a real `web-fetch` support surface.

`insane-search` validates the need for a dedicated tool-usage layer below
`gather`. The public `gather` skill should stay durable-asset-oriented. The
platform-routing and fetch-recovery knowledge belongs in a support skill or
external-skill integration named `web-fetch`, not in `gather` core.

2. Add a fetch strategy ladder with explicit escalation order.

`insane-search` has a useful operational sequence:

- direct fetch
- domain-specific public API or URL transform
- Jina Reader or equivalent public reader
- metadata-only recovery
- archive/cache fallback
- clean stop with reason

`gather` currently specifies source priority and capability order well, but it
does not encode this public-web fallback ladder with the same operational
clarity.

3. Add response validation rules for public-web paths.

The strongest reusable idea in `insane-search` is not any one provider. It is
the explicit distinction between:

- real content
- partial content
- login wall
- CAPTCHA/bot block
- empty SPA shell
- hard fetch failure

That classification would improve both `web-fetch` and `gather` because
`gather` could record whether a source was fully gathered, partially recovered,
or only metadata-backed.

4. Separate domain routing tables from public skill prose.

`insane-search` works because the operational data is concrete. `charness`
should not paste that table into `gather/SKILL.md`, but should consider a
machine-readable or reference-oriented routing surface for `web-fetch`, for
example:

- supported domains/patterns
- preferred access path
- optional binary dependencies
- degradation behavior
- output confidence class

5. Use `insane-search` as upstream reference or sync target, not as owned
runtime.

Per current `charness` policy, this upstream repo fits best as either:

- an `external_skill` manifest with `support_skill_source` and `reference`
  sync, or
- a thin local `web-fetch` wrapper that cites `insane-search` as provenance

It should not be modeled as `charness`-owned runtime unless `charness` starts
shipping and maintaining its own equivalent recipes and helper scripts.

### Medium-confidence opportunities

1. Teach `gather` when to delegate to `web-fetch`.

For public-web sources, `gather` could explicitly route through `web-fetch`
when:

- the user names a blocked or JS-heavy site
- direct URL fetch fails
- the domain matches a known special-case provider

Then `gather` stays focused on durable output shape while `web-fetch` owns
retrieval tactics.

2. Record recovery provenance in gathered artifacts.

When public fetch is indirect, gathered artifacts should say not just the URL
but also the path used, for example:

- `direct`
- `api`
- `jina-reader`
- `mobile-url-transform`
- `archive`
- `metadata-only`

This would make later refresh and trust decisions materially easier.

3. Add optional dependency declarations per fetch tactic.

`insane-search` mixes zero-config strategies with optional tools such as
`yt-dlp` and `gh`. `charness` should keep those as explicit capability or
integration edges rather than silent assumptions.

## What Not To Copy

- Do not collapse `gather` into a giant domain cookbook.
- Do not hardwire Jina, `yt-dlp`, `gh`, or curl recipes into the public
  `gather` contract.
- Do not claim automatic bypass capability if the shipped `charness` surface is
  still only documentation or reference sync.
- Do not treat provenance from `insane-search` as proof that `charness` owns
  the runtime.

## Recommended Direction

### Best near-term move

Add a first real `web-fetch` seam in one of these two shapes:

1. `integrations/tools/insane-search.json` as `external_skill` with reference
   sync to the upstream `skills/insane-search/SKILL.md`
2. local `skills/support/web-fetch/` plus capability metadata, using
   `insane-search` as a reference implementation and copying only the parts
   `charness` is willing to maintain

Given current control-plane policy, option 1 is the lower-risk first step.

### Best longer-term move

Once the seam proves useful, grow a `web-fetch` support capability that
contains:

- public-web response classification
- domain routing metadata
- provider-specific helper scripts only where `charness` truly intends runtime
  ownership
- integration references for external binaries such as `gh`, `yt-dlp`, and any
  browser runner

## Open Gaps

- No live host-level experiment was run to verify how well `insane-search`
  plugs into current Codex/Claude support-sync consumption.
- No success-rate benchmark was run across target sites; this is a design
  comparison, not a reliability bakeoff.
- `web-fetch` is currently a visible policy term in `charness`, but no shipped
  local support skill or manifest was found during this inspection.
