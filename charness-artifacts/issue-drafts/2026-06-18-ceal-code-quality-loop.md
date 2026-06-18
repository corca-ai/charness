# Issue draft (B) — ceal code-layer quality pass (less but better)

Status: **FILED 2026-06-18 as corca-ai/ceal#396**
(<https://github.com/corca-ai/ceal/issues/396>, label `enhancement`, OPEN), via
the `issue` skill after a bounded fresh-eye critique (read the real `../ceal`) that
folded: a scorecard **"Behavior value" gate** on the mutation step (no
trivial-silencing of survivors), and **file-only** `defaultMutate` expansion
pending a measured CI-cost proof. Sibling: capability-surface corca-ai/ceal#395.
Complement: corca-ai/charness#390.
Audience: ceal making valuable, **independent** code-quality progress on **its
own** TS code, before/without the upstream charness overhaul.

---

## Title

Code-layer quality pass: act on tolerated duplication / dead-code / mutation survivors + bug-hunt (scorecard-routed, one pass)

## Observed problem

ceal already has strong quality **gates** (jscpd at `threshold: 2.2`, knip,
stryker, dependency-cruiser, ~35 `lint:*` surfaces aggregated behind
`verify`). But a gate enforces a *threshold* — it does not drive the surface
toward [*less but better*](https://wiki.g15e.com/pages/Capabilities%20over%20features.md).
Duplication tolerated **below** 2.2%, knip-flagged dead surface, **surviving
mutants**, and latent logic bugs (which no gate hunts) accumulate quietly. The
capabilities-over-features lens + the operator's quality loop (bug-hunt, nose /
duplicate-refactor, doc↔code consistency) gives ceal a concrete, independent
code-quality pass — distinct from the capability-**surface** design audit
(sibling issue A) and from the upstream charness plugin (#390).

## Evidence

- `.jscpd.json` sets `threshold: 2.2` — duplication up to that bar is *tolerated*,
  not driven down. `lint:duplicates` / `lint:test-duplicates` exist as signals.
- `stryker.config.mjs` `defaultMutate` lists only **5 files**
  (`invocation.ts`, `handle-turn-readiness.ts`, `runtime-config.ts`,
  `slack-format.ts`, `audit-conversation.ts`) — narrow mutation coverage, so
  survivors and untested hot logic elsewhere are invisible to the gate.
- `knip.json` is configured (`lint:knip`) but dead-surface findings still need a
  human/agent to act on them.
- ceal's own AGENTS.md mandates **scorecard-routed** structural cleanup
  (`docs/implementation/quality-signal-scorecard.md`) and treats **tool output as
  quality signals, not sources of truth** — this issue inherits that discipline.

## Cost

Tolerated-below-threshold debt compounds; narrow mutation coverage hides latent
bugs in real logic; dead surface taxes every reader. Because "features are
promises," the longer this sits the harder it is to remove — an early bounded
pass is worth more than the same pass later.

## Useful outcome

One **closeable, scorecard-routed** pass that lands the safe structural
improvements (real duplication reduced, genuinely-dead surface removed, top
mutation survivors killed, latent bugs fixed) **test-first**, and files the rest
— **no metric-chasing**, no upstream-charness edits, no gate-threshold gaming.

---

## Autonomous execution contract (for the runner)

### In scope (ceal-owned code)
- ceal's own TypeScript code (`packages/**`), `scripts/**`, and their tests; the
  quality signals from ceal's own tooling (jscpd, knip, stryker,
  dependency-cruiser, `nose`).

### Out of scope (hard guards)
- **Upstream charness** plugin/skill source — file a `corca-ai/charness` issue or
  repo-local guard (per ceal AGENTS.md); the charness-plugin track is **#390**.
- The capability-**surface** design audit (CLI orthogonality / learn-by-use) —
  that is **sibling issue A**, not this.
- **Gate-threshold re-litigation.** Respect existing config; change a threshold
  only as a deliberate, recorded decision — never to make a check pass.
- No external side effects (push/CI, Slack, apply/restart) beyond ceal's
  documented operator-preauthorized lanes, with the boundary-reason flag.

### The pass (scorecard-routed, one iteration)
1. **Route through `docs/implementation/quality-signal-scorecard.md` first**
   (AGENTS.md). Treat every tool output below as a **signal, not truth**: fix for
   real behavior / ownership value, not to move a number.
2. **Duplication.** Run `lint:duplicates` / jscpd; reduce the top *real* cluster
   toward "less but better" (test-first). **Only merge code that shares a true
   invariant** — never collapse non-orthogonal lookalikes (the capabilities-over-
   features trap). File the rest.
3. **Dead surface.** Run `lint:knip`; remove genuinely-dead exports/files
   (test-first); file the ambiguous ones.
4. **Mutation.** Run stryker; kill the top **surviving mutants** by adding the
   missing behavior test. **Run the scorecard "Behavior value" check before adding
   any assertion** — a new test must state a *named behavior*, not merely observe
   that the mutant dies (no `toBeDefined()`-style trivial silencing). Where a hot
   file with real logic is absent from `defaultMutate`, **file it only** — never
   expand `defaultMutate` in this pass without a *measured* run-time-cost proof
   (an unmeasured expansion can silently blow CI time).
5. **Bug-hunt.** Systematic read of high-risk logic (the mutate-listed hot files
   + connector formatting + turn/invocation paths) for latent bugs **no gate
   finds**; fix with a regression test, or file.
6. **Doc↔code.** Reconcile code-level doc drift by fixing the code, or file when
   the doc is wrong; never edit upstream charness docs.

### Done (closeable — bounded to ONE pass)
Closes when the scorecard is consulted and **one** duplication + **one** knip +
**one** stryker + **one** bug-hunt + **one** doc↔code sweep over the in-scope set
are complete: the safest top items landed (test-first), every finding *surfaced
in this pass* committed or filed as a sub-issue. The runner **stops after one
pass** — not after exhausting all findings. The loop continues via filed
sub-issues.

### Discipline
- Route through ceal `find-skills` + the quality-signal scorecard; **tool output
  is signal, not truth** — no metric-chasing (AGENTS.md).
- **Test-first** for any uncovered code touched; bounded fresh-eye `critique` for
  deletion / assertion-moving / cross-surface changes (AGENTS.md cadence).
- `mutate → sync → verify → publish`; commit each meaningful unit. No unrequested
  push/apply/Slack/publish; `ceal-dev` apply/restart is operator-preauthorized
  only, with `--boundary-reason` (the server runs on another machine).
- Name the highest external-capability proof level reached; readiness ≠ action
  proof.

### Acceptance (operator-verifiable)
The scorecard + filed sub-issues + landed commits show real reductions
(duplication / dead surface / mutation survivors) and fixed latent bugs, the gate
suite green, **no upstream-charness edits**, and **no metric-chasing churn**
(every change ties to behavior/ownership value, not a moved number).
