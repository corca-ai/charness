# Issue draft — ceal self-improvement: capabilities over features (CLI + capability surface)

Status: **FILED 2026-06-18 as corca-ai/ceal#395**
(<https://github.com/corca-ai/ceal/issues/395>, labels `capability`+`enhancement`,
OPEN), via the `issue` skill after a bounded fresh-eye critique that read the real
`../ceal` and folded: **corrected the entrypoint facts** (2 specced binaries —
`ceal-ops` internal / `cealctl` public — no `ceal` binary; `ceal:*` are
pass-throughs) and **reframed to within-entrypoint learn-by-use** (the top-level
split is already specced); added the breaking-change **spec + specdown guard**.
Sibling: code-quality corca-ai/ceal#396. Complement: corca-ai/charness#390.
Audience: ceal making valuable, **independent** progress applying the
*capabilities over features* philosophy to **its own** surface — before/without
waiting on the upstream charness north-star overhaul.

---

## Title

Capabilities over features: audit ceal's own CLI + capability surface for orthogonality & learn-by-use, prune the safe redundancy

## Observed problem

The [*capabilities over features*](https://wiki.g15e.com/pages/Capabilities%20over%20features.md)
principle — minimum, **orthogonal**, composable, **learnable-by-use** surface;
"less but better"; features are promises so removal is hard; non-orthogonal
surface forces "which path?" overhead and wrong choices ("one obvious way") —
gives ceal a positive design target it can pursue on its **own** surface, today,
independent of the upstream charness overhaul.

ceal already practices much of this (SessionStart primes `find-skills`; AGENTS.md
favors progressive disclosure — "read the smallest owner doc"; ~30 `lint:*`
surfaces are aggregated behind `npm run lint`/`verify`; there is a
`docs/verification-philosophy.md`). So this is a **sharpening audit, not a
greenfield cleanup** — it must respect existing good structure and avoid redundant
churn. What has **not** been done is applying the capabilities-over-features lens
explicitly to the **ceal-owned capability surface**. ceal has **two** distinct
binary entrypoints — `bin/ceal-ops` (internal/dev operator CLI) and `bin/cealctl`
(source shim for the public `cealctl` customer binary distributed via
`corca-ai/ceal-cli`) — and their **top-level split is already decided and specced**
(`docs/specs/cealctl-distribution-and-operations.spec.md`); the `ceal:*` npm
scripts are pass-throughs to `ceal-ops`, **not** a third entrypoint. So this audit
does **not** re-decide that boundary. It targets the **within-each-entrypoint**
gaps the lens exposes: does invoking each command **teach its own usage**
(learn-by-use), and can an agent **find the right capability** for a task via
progressive disclosure rather than reading everything up front?

## Evidence

- ceal has **two** binary entrypoints with an already-specced split: `bin/ceal-ops`
  (internal operator) and `bin/cealctl` (public-customer source shim →
  `corca-ai/ceal-cli`); `ceal:*` npm scripts pass through to `ceal-ops`. The
  top-level boundary is **settled** — the audit targets *within-entrypoint*
  learn-by-use, not the split.
- ceal already aggregates ~30 `lint:*` surfaces behind `npm run lint`/`verify`,
  primes `find-skills`, and ships a self-guide / owner-doc surface; the audit's
  job is the *remaining* learn-by-use / capability-discovery gaps, not re-doing
  solved structure.
- ceal's code-quality tooling (`.jscpd.json`, `stryker.config.mjs`, `knip.json`,
  `.dependency-cruiser.cjs`, `nose`) measures *code*, not *capability-surface
  orthogonality* — the latter is a design-judgment audit nothing currently runs.
- The principle's warning (non-orthogonal surface → "which path?" overhead +
  wrong choices) is the learnability tax an autonomous runtime pays whenever its
  capability surface is redundant.

## Cost

Every redundant or non-discoverable capability is a standing learnability tax: a
new contributor (human or agent) must learn more, choose among overlapping paths,
and can choose wrong. Because "features are promises," this debt is *harder to
remove the longer it sits* — so an early, deliberate orthogonality pass is worth
more than the same pass later.

## Useful outcome

One **closeable audit-then-prune pass** that (1) maps ceal's own CLI + capability
surface for orthogonality and learn-by-use, (2) lands the safe consolidations /
learn-by-use improvements, and (3) files the rest — with **zero edits to upstream
charness** and no silent breaking of an existing CLI contract.

---

## Autonomous execution contract (for the runner)

### In scope (ceal-owned surface only)
- ceal's own CLI entrypoints — `bin/ceal-ops` (internal operator) and
  `bin/cealctl` (→ public `corca-ai/ceal-cli`) — and ceal-owned skills /
  capabilities / owner docs. (No `ceal` binary exists; `ceal:*` scripts are
  `ceal-ops` pass-throughs.)

### Out of scope (hard guards)
- **Upstream charness plugin/skill source** — per ceal's own AGENTS.md rule, do
  **not** edit charness; file a `corca-ai/charness` issue or a repo-local guard
  instead. The charness-plugin code-quality track is **corca-ai/charness#390**.
- No external side effects (apply/restart, Slack write, push/CI, issue/PR/release
  publish) beyond ceal's documented operator-preauthorized lanes, and only with
  the repo-owned boundary-reason flag.

### The pass (one closeable iteration)
1. **Orthogonality audit (capabilities over features).** The top-level
   `ceal-ops`/`cealctl` split is specced — do **not** re-litigate it. Look
   *within* each entrypoint (and across ceal-owned skills/capabilities) for ≥2
   overlapping ways to do one task (the "folder vs tag vs link" smell); rank by
   "which path?" overhead. Land the **safe** consolidations toward "one obvious
   way" — test-first for any touched code. A breaking CLI-contract change must be
   **intentional and recorded in
   `docs/specs/cealctl-distribution-and-operations.spec.md` (or a filed
   sub-issue)** before the pass closes; the specdown tests
   (`packages/ceal-runtime/test/ceal-cli.test.ts`, `bin/ceal.test.mjs`) are the
   failure signal for an unintentional break (features are promises). File the rest.
2. **Learn-by-use audit.** For each entrypoint: does invoking it teach its usage
   (discoverable subcommands, honest `--help`, error → next-step)? Improve the
   cheap, safe gaps so an agent can learn the capability **by calling it** rather
   than by reading everything up front. File the larger ones.
3. **Capability-discovery check.** Confirm `find-skills` / owner docs let an agent
   find the **right** capability for a task via progressive disclosure (smallest
   owner doc first), not by loading the whole surface. File concrete gaps.

### Done (closeable — bounded to ONE pass)
Closes when one orthogonality audit + one learn-by-use audit + one
capability-discovery check over the ceal-owned surface are complete: the safest
consolidations landed (test-first / breaking-changes recorded), and every finding
*surfaced in this pass* is committed or filed as a sub-issue. The runner **stops
after one pass** (not after exhausting all conceivable findings — that never
closes). Sibling tracks — code-layer refactor via jscpd/stryker/knip/nose,
bug-hunt, doc↔code consistency — are filed as their **own** issues, not absorbed
here.

### Discipline (route through ceal's own conventions)
- `find-skills` first; prefer the matching installed skill over an ad-hoc
  workflow. Use ceal's quality tooling as **signals, not truth** (AGENTS.md).
- **Test-first** for any touched code; bounded fresh-eye `critique` premortem for
  cross-surface/deletion/contract changes (AGENTS.md cadence).
- `mutate → sync → verify → publish`; commit each meaningful unit; treat
  `charness-artifacts/` as repo state.
- Name the highest external-capability proof level reached; readiness ≠ action
  proof. No unrequested push/apply/Slack/publish.

### Acceptance (operator-verifiable)
Read the audit + filed sub-issues + landed commits: ceal's CLI/capability surface
is measurably more orthogonal and learn-by-use (fewer redundant paths, better
self-teaching invocation), no existing contract broke unintentionally, and **no
upstream charness edits** were made.
