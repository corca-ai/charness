# Quality Review
Date: 2026-07-18
Title: Autonomous Quality and Efficiency Review

## Scope

Target boundary: repo-wide autonomous improvement across agent-facing token
cost, CLI correctness, coupling, code hygiene, and standing-test setup cost;
D18 excluded.

Ambient repo findings: no duplicate-discovery, broad-scanner, dual-implementation,
or brittle-source-guard candidates; dead-code advisory findings were manually triaged.

## Current Gates

- Focused catalog, SessionStart, CLI, runtime-aggregate, issue, release, and tool
  recommendation tests passed 76 tests; locked full closeout passed below.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: release 81.0s latest / 82.2s median; read-only quality
  55.9s / 55.7s; pytest 35.4s / 35.9s.
- coverage gate: locked-diff full closeout and changed-line mutation coverage passed.
- evaluator depth: deterministic-gates-only; Cautilus is ask-before-run and this
  local CLI/projection seam has direct executable proof.

## Healthy

- Full catalog output remains available; compact YAML output retains adapter
  warnings, layer counts, and hidden support/integration identity and paths.
- Root/plugin mirrors are synchronized and the generated CLI reference exposes
  the new opt-in flag.
- Evidence annotations now follow semantic wrapped bullets, and the CLI reference
  generator no longer owns a private duplicate command-path list.

## Weak

- SessionStart previously prescribed `charness catalog list ... --json`, an
  unsupported public CLI command, so the fallback failed instead of returning inventory.
- Hidden-inventory routing loaded 57,413 bytes / 1,094 lines even though public
  skill detail was not part of the consumer question.
- Evidence durability was coupled to physical line wrapping, and CLI path/order
  was manually repeated across parser, YAML, registry, and renderer surfaces.

## Missing

- No missing standing gate remains for the corrected branch: direct backend,
  public CLI, hook directive, omission, projection, and flag-conflict tests exist.

## Deferred

- Compact-schema versioning or a byte budget waits for a real compatibility
  consumer; the view is currently an opt-in routing projection.

## Advisory

- structural review result: artifact: `2026-07-18-critique-review.md` records that
  the catalog owns source facts and compact projection;
  SessionStart only selects the view, so boundary verdict is `owned-correctly`.
- prose review result: artifact: `2026-07-18-045813-packet.md` shows trigger scope
  stays limited to unclear hidden availability;
  generic and historical full-catalog references remain intentionally unchanged.
- command: `inventory_standing_test_economics.py --summary-yaml` found 155 standing test
  files with nested CLIs; bounded inspection proved seven redundant interpreter
  discovery subprocesses, now replaced with `sys.executable` without losing proof.
- command: `run_dead_code_advisory.py --confidence 60` produced review candidates; history
  and call-site inspection separated four true orphans from intentional/dynamic code.
- artifact: `../debug/2026-07-18-debug-review.md` records the reproduced
  physical-line and duplicated-command-list coupling plus ownership dispositions.

## Delegated Review

- Delegated Review: executed — two high-leverage critique rounds each used two
  angle reviewers and a separate counterweight; all were parent-delegated and
  fingerprint verification reported no drift.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof):
  re-delegated to a bounded speed scout; only the proven interpreter subprocess
  seam was changed, with no gate or assertion removed.

## Commands Run

- quality inventories for structural waste, dual implementation, brittle guards,
  lint ignores, dead code, standing-test economics, and runtime summary.
- focused pytest selection — 76 passed; catalog/SessionStart follow-up — 41 passed.
- `ruff check` on changed Python surfaces — passed.
- real catalog measurement — 57,413B/1,094 lines to 5,308B/120 lines (90.8%).
- public-skill dogfood/scenario review — setup compact-routing evidence updated;
  issue/release public contracts and maintained scenario IDs remain unchanged.
- coupling proof — 27 focused tests passed, all 316 durability-scoped docs passed,
  and CLI reference regeneration was byte-identical.
- locked `run_slice_closeout.py --verification-lock --produce-mutation-coverage`
  and the detected pre-commit lint gate — passed.

## Recommended Next Quality Moves

- passive compact-schema versioning because no external compatibility consumer
  exists yet; capability_needed=stable cross-version compact consumers;
  next_center=capability catalog; transformation=version only when a consumer
  requires it; proof_boundary=consumer compatibility fixture;
  enforcement_posture=no-gate because a standing budget would be premature.

## History

- [Prior durable quality review](history/2026-07-14-open-issue-resolution-proof.md)
