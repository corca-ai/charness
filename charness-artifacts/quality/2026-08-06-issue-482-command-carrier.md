# Quality Review
Date: 2026-08-06
Title: Issue #482 Command Carrier Portability Quality Review

## Scope

Target boundary: command carriers in shipped portable skill Markdown. The issue
reports commands that use the authoring-only `skills/<kind>/<skill>/...` layout,
which exists in this checkout but not in a consumer's installed plugin tree.

The repair rejects source-existing kind-bearing command paths, reports the
expected shipped spelling and export omission when applicable, and rewrites the
14 live sites to `$SKILL_DIR/...` or `<plugin-dir>/...`. It makes no installed
consumer runtime or remote CI claim.

## Current Gates

`scripts/check_doc_links.py` owns command target existence and the new
authoring-vs-consumer command boundary. `scripts/check_documented_command_flags.py`
owns argparse flag proof and preserves the special consuming-skill anchor for
shared references. `check_plugin_doc_links.py`, `check_plugin_dir_references.py`,
and staged mirror drift own shipped links, placeholders, and source/plugin parity.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; local profile is the configured x86_64 quality adapter. <!-- reproduction-source -->
- runtime hot spots: this is a focused static command-carrier slice; no new standing-gate timing claim was needed.
- coverage gate: focused command/link/plugin suites and strict inventory pass; broad `run-quality.sh` remains the final umbrella boundary.
- evaluator depth: deterministic-gates-only; Cautilus is not applicable to static path-carrier ownership.

## Healthy

- Source-existing `skills/public/...` and `skills/support/...` command carriers inside shipped skill docs are rejected even when their plugin export is absent; the cohesive `scripts/portable_command_carrier.py` module names the expected `<plugin-dir>/...` spelling and whether export is missing.
- The 14 live command sites no longer use the authoring kind-bearing layout: own-skill commands use `$SKILL_DIR`, and cross-skill commands use `<plugin-dir>/skills/...`.
- Shared `$SKILL_DIR/../../shared/...` semantics remain anchored at the consuming skill rather than the newly portable `skills/shared` package root.
- Focused portability, documented-command, plugin-link, and plugin-dir suites passed 123 tests; source/plugin mirrors are byte-identical.

## Weak

No target-slice weakness remains after the two bounded review rounds. The second
round found a missing-plugin-directory fail-open and the repaired surface now
has a regression fixture for that branch.

## Missing

- A real installed-consumer command execution roundtrip is not present in this slice.
- The documented-command gate intentionally reports 11 flag-bearing invocations as not proven (ambiguous basenames or placeholders); this is a typed coverage disposition, not a claim that those commands were executed.
- Remote CI state is not proven locally.

## Deferred

Typed JSON/YAML/template command carriers remain in #483. Consumer runtime proof
and broader non-Markdown asset discovery remain outside this Markdown slice.

## Advisory

- structural review result: target quality move is existing-gate reuse; inventory: `check_doc_links.py` plus `check_documented_command_flags.py`; source-to-shipped path mapping, final command execution boundary, and shared-anchor ownership were inspected; ambient plugin-tree prose findings were not folded into #482.
- Maintainer-Local Enforcement disposition: healthy; command: `python3 scripts/validate_maintainer_setup.py --repo-root .` — the checked-in `.githooks/pre-push` invokes `scripts/run-quality.sh --read-only` and the maintainer validator confirms the local enforcement contract.

## Delegated Review

- Delegated Review: executed — round 1 reviewer `019fd46c-ecef-74c2-802e-0d48ffbc28b5` found a fail-open when the exported target was absent; the repair removed that condition and added an export-missing test. Round 2 reviewer `019fd46f-4a05-72f1-a687-6bb8ba7d0a69` found a second fail-open when `root/plugins` was absent; the repair now checks source existence independently and adds a no-plugin-directory test. Both boundary fingerprints verified clean immediately on return.
- Round-2 repair disposition: accepted-unreviewed under the two-round cap; no third round was run.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof): not_applicable — this is a focused static command-carrier slice, not a slow-gate redesign.

## Commands Run

- `pytest -q tests/quality_gates/test_check_doc_links.py tests/quality_gates/test_documented_command_flags.py tests/quality_gates/test_check_plugin_doc_links.py tests/quality_gates/test_plugin_dir_references.py` — 123 passed.
- `python3 scripts/check_doc_links.py --repo-root . --require-git-file-listing` — passed; no remaining authoring-layout command sites.
- `python3 scripts/check_documented_command_flags.py --repo-root . --require-git-file-listing` — 254 invocations validated; 11 typed skips reported.
- `python3 scripts/check_plugin_doc_links.py --repo-root . --require-git-file-listing` — passed; skipped none.
- `python3 scripts/check_plugin_dir_references.py --repo-root . --require-git-file-listing` — passed; two templated references skipped.
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .` — source/plugin mirrors synchronized.
- `python3 scripts/check_python_lengths.py --repo-root . --paths scripts/check_doc_links.py scripts/portable_command_carrier.py ...` — passed with the existing advisory warn-band notice for the cohesive checker module.

## Recommended Next Quality Moves

- active capability_needed=command carriers must be validated from the consumer's execution tree; next_center=the source-vs-shipped command detector; transformation=retain source-only, missing-export, and no-plugin-directory fixtures; proof_boundary=portable command gate plus plugin reference checks; enforcement_posture=existing-gate-reuse.
- passive capability_needed=non-Markdown carrier coverage; next_center=typed JSON/YAML/template corpus; transformation=defer to #483 because this slice's denominator is intentionally Markdown-only; proof_boundary=typed carrier inventory and consumer fixture/readback; enforcement_posture=no-gate.

## History

- [Issue #482](https://github.com/corca-ai/charness/issues/482) — live issue read on 2026-08-06; comments were read and no comments were present.
- [Issue #484 shared portable package quality review](2026-08-06-issue-484-shared-portable-package.md) — preceding package-boundary repair and shared-anchor regression.
- [Prior portability quality review](history/2026-07-19-portable-proof-path-learning-review.md) — source-before-remedy and avoid-premise drift guidance.
