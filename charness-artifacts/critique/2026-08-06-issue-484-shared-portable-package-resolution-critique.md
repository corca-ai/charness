# Issue #484 Shared Portable Package Resolution Critique
Date: 2026-08-06

## Decision Under Review

Treat `skills/shared/**` as a shallow portable package for the markdown
portability checker, calculate its package-relative paths from the explicit
repo-relative package root, and mark plugin-level RCA helpers with
`<plugin-dir>/scripts/`.

Success means the shared package gets the same structural verdicts as other
shipped skill packages without breaking cross-package links or shared helper
resolution. This slice does not claim installed-consumer execution or remote
CI behavior.

## Failure Angles

- **Shallow-root arithmetic**: reusing the three-level `parents[2]` derivation
  could prepend the wrong path for `skills/shared`, making valid shared helpers
  fail or missing helpers pass.
- **Cross-package link semantics**: enabling the package root could turn the
  existing intentional `skills/` cross-package reference allowance into false
  positives or incorrectly allow links that escape the source tree.
- **Shared script ambiguity**: the shared RCA prose could continue to name
  plugin-level scripts as bare `scripts/...`, leaving the new gate either noisy
  or silently exempt.
- **Mirror/verdict drift**: source and plugin copies could disagree, or tests
  could assert only a green run without distinguishing package-relative and
  outside-root cases.

## Counterweight Pass

The implementation is bounded and the concerns are answered by direct
evidence. The production caller passes `portable_package_root.relative_to(root)`
so the shallow shared root is explicit; focused tests cover a valid shared
helper and an outside-root unmarked path; the existing plugin-link and
`<plugin-dir>` gates pass; and source/plugin copies compare byte-for-byte.
The plugin-tree invocation of the general backtick checker still reports an
unchanged ambient `inventory_sloc.py` unique-basename finding, but that is not
the official shared package gate and is not caused by this slice.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: `scripts/check_doc_links.py:portable_skill_package_root`, `tests/quality_gates/test_check_doc_links.py::test_shared_is_a_portable_package_for_package_relative_paths` | action: fix | note: shared needs an explicit shallow package root and a repo-relative package path; implemented with discriminating regression coverage.
- F2 | bin: bundle-anyway | evidence: strong | ref: `skills/shared/references/rca-ledger-append.md` and `tests/quality_gates/test_plugin_dir_references.py` | action: fix | note: plugin-level helpers are now named with `<plugin-dir>/scripts/`, and the shipped target gate confirms them.
- F3 | bin: over-worry | evidence: weak | ref: plugin-tree general checker finding at `plugins/charness/presets/python-quality.md:36` | action: defer | note: the file is unchanged, the official plugin-link and plugin-dir gates pass, and broad prose-checker cleanup is outside #484.
- F4 | bin: valid-but-defer | evidence: moderate | ref: `charness-artifacts/quality/2026-08-06-issue-484-shared-portable-package.md` | action: defer | note: installed-consumer execution and typed JSON/YAML/template carrier coverage remain separate non-claims owned by #483 or a later proof slice.

## Reviewer Tier Evidence

- Requested tier: `gpt-5.6-terra` with `medium` reasoning effort.
- Requested spawn fields: model `gpt-5.6-terra`, reasoning effort `medium`, service tier `priority`, `fork_context: false`, unnamed one-shot bounded reviewer.
- Host exposure state: applied
- Application state: host-confirmed: unnamed reviewer `019fd465-cf3c-76d2-95b7-aaf9125f7c72` returned a clean verdict.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated: round 1 reviewer `019fd465-cf3c-76d2-95b7-aaf9125f7c72`
read the changed checker, shared docs, mirrors, tests, and focused commands;
it found no blockers and confirmed the shallow-root arithmetic. Boundary
fingerprint window `issue484-shared-package-r1` verified clean immediately
after return. Because round 1 produced no repairs, the proof-surface
second-round obligation is discharged.

## Reviewed Input Identity

No critique packet was consumed; the reviewer read the changed source, tests,
shared reference, mirrors, and command results directly.

## Boundary Ownership

- Producer: `scripts/check_doc_links.py` determines package root, package-relative reachability, and portability verdicts.
- Consumer: the source markdown gate, shipped relative-link gate, and `<plugin-dir>` reference gate render the final local verdict.
- Owning surface: `scripts/check_doc_links.py`, with focused tests and synchronized shared/plugin references.
- Verdict: owned-correctly
