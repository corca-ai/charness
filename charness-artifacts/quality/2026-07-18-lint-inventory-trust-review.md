# Quality Review
Date: 2026-07-18
Title: Trustworthy lint-ignore inventory and cheaper stable-file tests

## Scope

Target boundary: lint-suppression source text through the structured inventory
that briefs a quality judge, plus two stable-file reads found by the structural
waste inventory.

Ambient repo findings: D18 remains ignored. Cautilus 0.20.0 is available while
0.19.3 is installed, but evaluator proof is not required for this deterministic
parser slice and no update was authorized or performed.

## Current Gates

- Existing inventory behavior tests, YAML output-contract tests, source/plugin
  sync, packaging validation, inference-interpretation validation, ruff,
  changed-line coverage, and the read-only quality gate own this slice. The
  repo-Markdown surface now routes the existing evidence-durability check before
  broad pytest.
- No new blocking floor was added; the change repairs a producer and reuses
  existing gates.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile
  `local-linux-x86_64-36cpu`. <!-- reproduction-source -->
- runtime hot spots: release quality 87.5s latest / 82.5s median; read-only
  quality 59.4s / 56.2s against a 90s budget; pytest 38.5s / 36.4s against a
  140s budget.
- coverage gate: final locked closeout is recorded in this artifact's commands.
- evaluator depth: deterministic-gates-only because exact parsed codes,
  malformed-source fallback, mirror bytes, and repeated reads are directly
  observable. The Cautilus planner returned `not-required`; no evaluation ran.

## Healthy

- `noqa` and Ruff rule identifiers now use a Python-rule parser, while Pylint
  and ESLint named rules use a separate parser that removes official `--`
  rationale text without rejecting hyphenated rule names.
- Raw snippets remain in findings, so removing rationale tokens from `codes`
  does not remove operator context.
- Tokenization is materialized inside the `TokenError` boundary; malformed
  Python falls back once instead of aborting or duplicating partial findings.
- Root and plugin inventory producers are byte-identical after the owning sync.
- Stable packaging-version and inventory-dispatch fixtures are read once per
  module; tests retain isolated command execution and do not mutate those files.

## Weak

- The previous shared permissive parser treated human explanation words as
  rule codes, producing misleading and longer YAML such as `BLE001`, `--`,
  `a`, `missing`.
- The previous malformed-Python fallback caught generator construction only;
  `TokenError` occurs during iteration, so the advertised fallback could abort.
- The first locked closeout spent 36.4s on 4,801 tests before the real-repo
  durability test found a misplaced reproduction marker. The repo-Markdown
  surface had not routed its existing cheap validator before broad pytest.
- Inventory samples include generated plugin mirrors as separate suppression
  sites. That is honest shipped-surface visibility, but consumers must not read
  the raw count as independent source debt.

## Missing

- Before this slice no test covered rationale-bearing Ruff, noqa, Pylint, and
  ESLint directives together or proved non-duplicating fallback on malformed
  Python.
- No wall-clock experiment isolates the two removed stable-file reads from
  normal test noise, so no speedup is claimed.

## Deferred

- Invalid mixed Python rule text remains leading-valid-prefix parsing. A distinct
  invalid-directive state would change the output contract and has no observed
  repo instance; revisit only with a real consumer need.
- Broader nested-CLI consolidation remains profiling-led: 400 test files and
  169 standing-or-mixed nested-CLI files are structure counts, not waste proof.

## Advisory

- structural review result: artifact: quality planner packet;
  capability_needed=accurate compact suppression
  facts; current_centers=tokenizer, syntax regexes, YAML inventory, mirror sync;
  next_center=syntax-specific parsing and atomic fallback; transformation=split
  parser ownership and hoist immutable fixtures; proof_boundary=exact emitted
  codes plus malformed-source execution; enforcement_posture=existing-gate reuse.
- prose review result: command: `inventory_skill_ergonomics.py --summary`;
  public skill triggers and progressive disclosure did not change. It scanned
  22 skills and found 16 host-reference
  heuristic hits; those are ambient portability prompts outside this
  producer/test-only slice.
- command: `inventory_structural_waste.py --summary` moved its conservative
  intra-test reread candidates from 2 to 0 while duplicate-discovery and broad-
  scanner candidates remained 0; this is code-shape evidence, not timing proof.
- command: `inventory_lint_ignores.py --summary` still reports 253 sites across
  118 files, all inline and rule-specific; the repaired priority sample now
  emits only real rule codes while retaining snippets and recommendations.

## Delegated Review

- Delegated Review: executed — parsing-compatibility and ownership/operability
  angles plus a separate counterweight found the tokenizer fallback defect;
  it was fixed before closeout. Invalid-directive schema expansion was deferred.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof):
  re-delegated; two stable reads were removed, but no critical-path or runtime
  improvement is claimed.
- Parent fingerprint verification found no worktree/index/HEAD drift after all
  read-only reviewers; details are in the linked critique.

## Commands Run

- quality planner; runtime, skill-ergonomics, lint-ignore, structural-waste,
  standing-test-economics, verbosity, clone, dual-implementation, and source-
  guard inventories.
- focused proof: 40 tests across lint inventory, version surface, and YAML
  output contract; focused ruff; source/plugin byte comparison.
- packaging, integration, support/update dry-runs, boundary escalation, and
  Cautilus proof planner.
- first locked closeout: 4,800 passed / 1 durability failure; the existing
  durability gate was then added to repo-Markdown closeout routing and rerun.
- final read-only quality and locked changed-line proof recorded at closeout.

## Recommended Next Quality Moves

- active publish v2.1.2 — capability_needed=installed trustworthy quality
  briefing; next_center=release helper; transformation=patch bump, fresh-checkout
  proof, public publish/readback, installed refresh; proof_boundary=distinct
  public HTTPS plus installed version; enforcement_posture=existing-gate reuse.
- passive profile the highest repeated nested-CLI family before consolidation because
  capability_needed=lower standing cost without losing delivery proof;
  next_center=measured family, not file count; transformation=in-process core plus
  thin binary smoke; proof_boundary=parity and repeated timing;
  enforcement_posture=no-gate because causality is not measured.

## History

- [Prior durable quality review](history/2026-07-14-open-issue-resolution-proof.md)
