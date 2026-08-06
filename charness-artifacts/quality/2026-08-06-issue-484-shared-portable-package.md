# Quality Review
Date: 2026-08-06
Title: Issue #484 Shared Portable Package Quality Review

## Scope

Target boundary: the markdown portability checker and the shipped `skills/shared`
package boundary. The issue reports that shared documents were silently outside
the `unmarked-tree`, portable-absolute, and portable-escape rules.

The repair gives `skills/shared` its shallow package root, makes package-relative
resolution use an explicit repo-relative path, and marks the plugin-level RCA
helpers with `<plugin-dir>/scripts/`. This is a local static quality claim; no
consumer runtime or remote CI claim is made.

## Current Gates

`scripts/check_doc_links.py` owns authoring-tree markdown portability and
`scripts/check_plugin_doc_links.py` owns shipped relative-link followability.
`scripts/check_plugin_dir_references.py` owns `<plugin-dir>/` target existence.
The source/plugin export helper and staged mirror-drift hook own parity.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; local profile is the configured x86_64 quality adapter. <!-- reproduction-source -->
- runtime hot spots: this is a focused static gate slice; no new standing-gate timing claim was needed.
- coverage gate: focused portability/link tests, source checks, plugin checks, and strict inventory pass; broad `run-quality.sh` remains the final umbrella boundary.
- evaluator depth: deterministic-gates-only; Cautilus is not applicable to static markdown path ownership.

## Healthy

- `skills/shared/references/**` now resolves as a portable package rooted at `skills/shared`, while cross-package shared links remain allowed only through the existing `skills/` escape rule.
- Package-relative shared helpers resolve under `skills/shared/scripts`; an outside-root `scripts/` reference is refused as `unmarked-tree`.
- The two shared RCA commands now identify installed plugin-level helpers with `<plugin-dir>/scripts/`, and the source/plugin reference mirrors compare byte-for-byte.
- Strict inventory reports 518 references (259 authoring and 259 shipped), zero findings, and zero unreadable files.

## Weak

No target-slice weakness found. The package-root and command-carrier tests discriminate the repaired verdict rather than only asserting a green end-to-end run.

## Missing

- A real consuming-repo package installation and command execution roundtrip is not present in this slice.
- The plugin-tree invocation of the general backtick checker still reports the pre-existing `plugins/charness/presets/python-quality.md:36` `inventory_sloc.py` unique-basename finding; that file is unchanged and is outside this shared-package repair. The official plugin-link and `<plugin-dir>` gates pass.
- Remote CI state is not proven locally.

## Deferred

Typed non-Markdown command-carrier coverage remains in #483. Broader consumer
execution proof remains outside this local static gate slice.

## Advisory

- structural review result: target quality move is existing-gate reuse; inventory: `check_doc_links.py`, `check_plugin_doc_links.py`, and `check_plugin_dir_references.py`; the source package-root owner, final consumers, and mirror boundary were inspected; ambient plugin-tree prose findings were not treated as #484 evidence.
- Maintainer-Local Enforcement disposition: healthy; command: `python3 scripts/validate_maintainer_setup.py --repo-root .` — the checked-in `.githooks/pre-push` invokes `scripts/run-quality.sh --read-only` and the maintainer setup validator confirms that local contract.

## Delegated Review

- Delegated Review: executed — one bounded fresh-eye reviewer inspected the shared package-root branch, package-relative path calculation, cross-package links, RCA placeholders, source/plugin parity, and discriminating tests; it returned clean with no blockers. Boundary fingerprint `issue484-shared-package-r1` verified clean immediately on return.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof): not_applicable — this is a focused static portability slice, not a slow-gate redesign.

## Commands Run

- `pytest -q tests/quality_gates/test_check_doc_links.py tests/quality_gates/test_check_plugin_doc_links.py tests/quality_gates/test_plugin_dir_references.py` — 77 passed.
- `python3 scripts/check_doc_links.py --repo-root . --require-git-file-listing` — passed.
- `python3 scripts/check_plugin_doc_links.py --repo-root . --require-git-file-listing` — passed; skipped none.
- `python3 scripts/check_plugin_dir_references.py --repo-root . --require-git-file-listing` — passed; two templated references skipped.
- `python3 scripts/inventory_skill_script_references.py --repo-root . --strict` — 518 references, zero findings.
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .` — source/plugin mirror synchronized; `cmp` checks passed.

## Recommended Next Quality Moves

- active capability_needed=portable package gates must cover every shipped source package shape; next_center=shared package root plus typed carrier inventory; transformation=keep the shallow-root fixture and separate plugin-level placeholder proof; proof_boundary=source checker, plugin checker, and strict inventory; enforcement_posture=existing-gate-reuse.
- passive capability_needed=consumer command execution confirmation; next_center=typed non-Markdown carrier corpus; transformation=defer to #483's JSON/YAML/template slice because this slice intentionally owns only Markdown portability; proof_boundary=consumer fixture/readback; enforcement_posture=no-gate.

## History

- [Issue #484](https://github.com/corca-ai/charness/issues/484) — live issue read on 2026-08-06; comments were read and no comments were present.
- [Issue #480 authoring path resolver quality review](2026-08-06-issue-480-authoring-path-resolver.md) — preceding portability slice that widened authoring-tree reference coverage.
- [Prior portability quality review](history/2026-07-19-portable-proof-path-learning-review.md) — source-before-remedy and avoid-premise drift guidance.
