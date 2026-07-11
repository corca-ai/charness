# Quality Review
Date: 2026-07-11

## Scope

Target boundary: the three operator-facing `web-fetch` route, acquire, and
classify CLIs; exactly 18 `argparse_missing_help` findings.

Ambient repo findings: none repaired; the remaining repo-wide argparse-help
inventory stays separate. `update_tools.py --json` reports Cautilus 0.18.0
behind 0.19.1 with a manual update path.

## Current Gates

- `inventory_skill_ergonomics.py` reports missing `help=` strings advisory-first.
- Focused subprocess `--help` tests, Ruff, py_compile, and existing web-fetch
  behavior tests own this package's deterministic proof.

## Runtime Signals

- runtime source: timing capture is missing for this focused help-only slice;
  no standing-runtime claim is made.
- runtime hot spots: none investigated; closeout timings were not promoted to a
  structured runtime artifact.
- coverage gate: verification-lock standing pytest and focused mutation
  coverage producer passed.
- evaluator depth: deterministic gates only because no agent behavior or prompt
  claim changed.

## Healthy

- All 18 descriptions stay with the existing parser owner; defaults, choices,
  actions, required flags, JSON output, routing, and acquisition behavior are
  unchanged.
- Option-scoped tests bind each long option to a distinctive help fragment and
  tolerate argparse wrapping without snapshotting whole output.

## Weak

- Repo-wide argparse missing-help debt remains 62 findings after this package;
  the advisory count is a selection prompt, not a mandate to sweep every site.

## Missing

- none for this target — the three direct entrypoints now expose meaningful
  help and have focused executable readback.

## Deferred

- Other skill packages wait for their own cohesive ownership slice; `quality`
  has the largest count but is spread across ten files.
- Cautilus update is deferred because this slice neither evaluates behavior nor
  authorizes a machine-tool installation change.

## Advisory

- structural review result: command: `inventory_skill_ergonomics.py --summary`;
  capability_needed=agents/operators can understand
  route, acquisition, and proof controls from `--help`; sequencing applies as
  inventory -> one package -> focused proof; current centers are the parsers and
  advisory inventory; next center is another cohesive package only after this
  commit; transformation=help strings plus option-scoped readback;
  proof_boundary=18 mappings and focused behavior suite;
  enforcement_posture=no-gate.
- prose review result: artifact:
  `charness-artifacts/critique/2026-07-11-web-fetch-argparse-help-critique.md`;
  the three commands form one route -> acquire -> classify operator workflow;
  fresh-eye rejected repo-wide sweeping and caught ambiguous browser/collect
  wording before closeout.
- command: `inventory_skill_ergonomics.py --summary` measured 80 findings before
  and 62 after, with `web-fetch` moving 18 -> 0.

## Delegated Review

- Delegated Review: executed — selection review approved the three-command
  package; semantic and test-fidelity angles required clearer browser/collect
  wording and option-bound assertions; a separate final counterweight found no
  remaining blocker.
- Slow-gate lenses: fixture-economics, parallel-critical-path, and
  duplicated-proof were not re-delegated because runtime and broad-gate
  economics are outside this help-only slice.

## Commands Run

- Skill-ergonomics summary/JSON; all three `--help` commands; 40 focused
  web-fetch tests; Ruff; py_compile; `git diff --check`; verification-lock
  standing pytest plus focused mutation coverage.

## Recommended Next Quality Moves

- active argparse-help-next-package — capability_needed=another cohesive CLI package explains its inputs; next_center=retro's three-script 11-finding cluster; transformation=repeat this bounded help/readback slice; proof_boundary=package inventory plus focused help tests; enforcement_posture=no-gate.
- passive scattered-quality-help debt until one owner-level cluster ranks above the retro package because its 23 findings span ten files; capability_needed=discoverable quality helper CLIs; next_center=deferred; transformation=none; proof_boundary=current inventory only; enforcement_posture=advisory.

## History

- [Prior quality review](history/2026-06-16-quality-review.md)
