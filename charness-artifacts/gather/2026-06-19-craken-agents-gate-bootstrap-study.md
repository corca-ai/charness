# craken-agents as a design reference for charness A/B (2026-06-19)

Captured to answer the handoff Discuss item "What `../craken-agents` is / how to
use it." Source: `/home/hwidong/codes/craken-agents` (local sibling repo, read
only). **Not** an external source and **not** a charness consumer — a full-repo
grep for `charness` returns zero matches. It is a sibling-repo *pattern*
reference only, not a dependency or integration.

## What it is

A single Cloudflare Workers TypeScript/Node app ("general-purpose agent that
learns and improves on its own", `AGENTS.md:1`) — a modular monolith over
Durable Objects + D1/Drizzle, ~40 product domains under `src/`, deployed via
`wrangler` (not GitHub Actions). It has its own internal "skills" concept
(`src/skills/builtin/*/SKILL.md`) unrelated to charness skill *packages*.

## Why it is the reference for B (gate reduction) — buy vs build

craken-agents covers 9 quality-gate concerns with **~761 lines of off-the-shelf
tool config and zero custom gate logic**, plus ~1,200 lines of bespoke code that
each guards a genuinely repo-unique invariant no tool can express:

| Concern | Tool | Custom code |
|---|---|---|
| format/lint/import-org | biome (`biome.json`, 110 lines) | 0 |
| arch boundaries | dependency-cruiser (`.dependency-cruiser.cjs`, 508 lines, ~40 declarative forbidden rules) | 0 |
| dead code | knip (6 lines) | 0 |
| duplication | jscpd (`.jscpd.json`, 9 lines) | 0 |
| mutation testing | stryker (103 lines, scheduled) | 0 |
| secrets | gitleaks (25 lines) | 0 |
| file-length + complexity caps | **biome rules** `noExcessiveLinesPerFile`, `noExcessiveCognitiveComplexity` (maxAllowedComplexity 12 src / 8 test) | 0 |

The only bespoke gates (`bin/*.mjs` ≈ 1,200 lines) are a live-Chrome design-system
check, a Zod content-data schema, and a D1 migration-squash-window check — all
irreducibly repo-unique.

**Contrast:** charness enforces a comparable scope with ~16.4K lines of *named*
bespoke Python gates (≈34.7K counting libs + closeout orchestration + nested
quality scripts) — roughly 20–30× the gate code for a smaller surface.

**Transferable lesson:** the length/complexity cap is a *configured rule in a
tool already run*, not a 400-line bespoke script. "Less but better" on gates =
triage each bespoke gate by "does this re-implement biome/knip/jscpd/dep-cruiser,
or is it genuinely repo-unique?" — delete the re-implementations, keep the unique.

### jscpd: threshold + audited ignore list, NOT a baseline ledger

`.jscpd.json` uses `threshold: 0` + `mode: weak` + a 3-entry `ignore` list — no
accepted-clones baseline. Their governance (`docs/quality-exceptions.md`): every
ignore is justified as "low-signal for this surface," carries a last-audited
date, and is **audited by removing each ignore in isolation and counting
reappearing clones** — then the missing shared owner is extracted instead of
re-accepting the clone (2026-06-03 audit re-enabled 3 surfaces totalling 344
clones, fixed by writing helpers).

**Relevance to charness:** the `nose-baseline.json` that #390 just created is the
permanent-ledger pattern craken-agents deliberately rejected. Steal the
discipline, not necessarily the threshold-0: a baseline should be a *temporary
ratchet with a last-audited date and a scheduled removal audit*, not a permanent
accepted-clones file. (Connects to handoff item D's baseline `tool_version`
stamp — extend it to a `last_audited` stamp + audit cadence.)

## Why it is a WEAK / cautionary reference for A (bootstrap consolidation)

craken-agents is aggressively DRY: one shared core (`src/core/`, `src/workspace-kernel/`),
zero per-package copies, and dependency-cruiser *enforces* the shared-core
boundary (no-circular, no-facade/barrel, single-owner-import rules). But it is a
**single bundled deployable** — a shared core is imported at build time with zero
distribution cost. charness skill packages must ship **standalone as portable
plugins** with no guaranteed shared runtime at the destination, which is exactly
the constraint that motivates the copy. So craken-agents proves shared-core is
the norm *for a single app*, but says little about charness's *distribution*
problem. The A lesson is narrow: consolidate any bootstrap/gate code that runs
**only inside the charness repo's own tooling** (use dependency-cruiser-style
boundary enforcement); leave the *distribution-motivated* per-package copy alone.

## What does NOT transfer

Cloudflare/Durable-Object/Worker-bundle architecture, the real-browser design
gate, mutation-testing scope, and the anti-barrel stance are all properties of a
single Node app with a unified build. None address charness's core constraint:
portable Python skill packages that ship standalone.
