# Quality Review
Date: 2026-08-06
Title: Issue #480 Authoring Path Resolver Quality Review

## Scope

Target boundary: the portability inventory's `<authoring-repo>/<path>` resolver
and its source/plugin mirror behavior. The issue reports docs and
`charness-artifacts/` targets escaping the resolver's scripts-only pattern.

Ambient repo findings: no broad quality claim is made; live consumer and remote
CI behavior remain outside this local quality slice.

## Current Gates

The existing `inventory_skill_script_references.py --strict` gate owns this
reference class. Source/plugin synchronization is enforced by
`sync_root_plugin_manifests.py` and the staged mirror-drift hook. The focused
test suites own positive, negative, source-layout, shipped-layout, and
`<plugin-dir>` behavior.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; local profile is the configured x86_64 quality adapter. <!-- reproduction-source -->
- runtime hot spots: this slice uses the focused inventory/test channel; no new
  standing-gate timing claim was needed.
- coverage gate: focused tests and strict inventory pass; broad `run-quality.sh`
  is reserved for the final umbrella boundary.
- evaluator depth: deterministic-gates-only; Cautilus is not applicable to a
  static path resolver.

## Healthy

- `<authoring-repo>/<path>` now resolves against the authoring source root in
  both authoring and shipped mirror scans, while `<plugin-dir>/scripts/...`
  retains its generated-plugin root.
- The strict inventory reports 514 references scanned (257 authoring and 257
  shipped), zero findings, and zero unreadable docs.
- The focused portability/link/command suites passed 132 tests, and source and
  plugin copies are byte-identical.
- A missing docs/artifact target remains actionable in the new fixture, so the
  widened resolver is not a blind green.

## Weak

No target-slice weakness found. Local proof does not establish that a real
consumer follows every shipped command; that is a boundary non-claim, not a
resolver verdict weakness.

## Missing

- A real consuming-repo execution roundtrip is not present in this slice.
- Remote CI and installed-cache behavior are not proven locally.

## Deferred

Defer consumer-repo execution proof and a broader non-Markdown carrier corpus to
#483's separate typed-carrier slice; do not fold those populations into this
Markdown inventory denominator.

## Advisory

- structural review result: target quality move is existing-gate reuse; inventory:
  `inventory_skill_script_references.py`; the
  source/plugin reader position and authoring-root ownership were inspected,
  while ambient skill-ergonomics findings were not treated as #480 evidence;
  command: `python3 scripts/inventory_skill_script_references.py --strict`.
- prose review result: corrected two stale authoring references; artifact:
  `charness-artifacts/quality/2026-08-06-issue-480-authoring-path-resolver.md`;
  discovered by
  widening the scan (`north-star-overhaul-roadmap.md` and explicit external
  `<cautilus-repo>` ownership); no new public mode or ritual was introduced;
  artifact: `charness-artifacts/quality/2026-08-06-issue-480-authoring-path-resolver.md`.
- Maintainer-Local Enforcement disposition: healthy; command:
  `python3 scripts/validate_maintainer_setup.py --repo-root .` — the checked-in
  `.githooks/pre-push` invokes `scripts/run-quality.sh --read-only`, and the
  maintainer setup validator is part of the existing local gate contract;
  command: `python3 scripts/validate_maintainer_setup.py --repo-root .`.

## Delegated Review

- Delegated Review: executed — one bounded fresh-eye reviewer inspected the
  source/plugin resolver, docs/artifact fixture, stale-reference repairs, and
  strict inventory; it returned clean with no blocker. The boundary fingerprint
  was verified clean immediately on return.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof): not_applicable — this is a focused static resolver slice, not a slow-gate redesign.

## Commands Run

- `pytest -q tests/test_skill_script_references.py tests/quality_gates/test_check_doc_links.py tests/quality_gates/test_plugin_dir_references.py tests/quality_gates/test_documented_command_flags.py` — 132 passed.
- `python3 scripts/inventory_skill_script_references.py --repo-root . --strict` — 514 references, zero findings.
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .` — source/plugin mirror synchronized.
- `cmp` source/plugin checks and bounded reviewer fingerprint verify — passed.

## Recommended Next Quality Moves

- active capability_needed=portable reference checks must cover every supported authoring placeholder; next_center=existing inventory gate; transformation=retain the widened path matcher plus source-root field and paired missing-target fixture; proof_boundary=strict inventory and focused source/plugin tests; enforcement_posture=existing-gate-reuse.
- passive capability_needed=consumer execution confirmation; next_center=typed non-Markdown carrier coverage; transformation=defer until #483's JSON/YAML/template corpus is shaped because this slice's Markdown denominator is now explicit; proof_boundary=consumer fixture/readback; enforcement_posture=no-gate.

## History

- [Issue #480](https://github.com/corca-ai/charness/issues/480) — live issue
  read on 2026-08-06; comments were read and no comments were present.
- [Prior portability quality review](history/2026-07-19-portable-proof-path-learning-review.md) — source-before-remedy and
  avoid-premise drift guidance.
