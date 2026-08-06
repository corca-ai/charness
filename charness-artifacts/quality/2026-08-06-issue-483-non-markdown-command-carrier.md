# Quality Review
Date: 2026-08-06
Title: Issue #483 Non-Markdown Command Carrier Quality Review

## Scope

Target boundary: command-shaped strings in shipped JSON, YAML, and YML plugin assets.
The gate parses typed structured values, maps authoring skills/public or skills/support
targets to their shipped plugin layout, and rejects unreachable carriers. It repairs
the two live source sites in integrations/tools/vulture.json and
skills/public/achieve/adapter.example.yaml. It does not claim arbitrary strings,
consumer runtime execution, or remote CI behavior.

## Current Gates

scripts/check_plugin_asset_command_carriers.py is the new deterministic bundle gate,
queued by scripts/run-quality.sh. It scans tracked plugins/**/*.json|yaml|yml,
recurses through strings, reports parse/layout/source/export failures, and is mirrored
under plugins/charness. Existing plugin-dir, doc-link, documented-command, and
source/plugin parity gates remain separate owners.

## Runtime Signals

- runtime source: .charness/quality/runtime-signals.json; this focused static slice adds no standing timing claim. <!-- reproduction-source -->
- runtime hot spots: not measured for this slice; broad run-quality remains the final bundle boundary.
- coverage gate: focused tests and direct structured-asset scan pass; broad gate and remote CI remain separate proof.
- evaluator depth: deterministic-gates-only; Cautilus is not applicable to typed path ownership.

## Healthy

- 62 tracked shipped structured assets scan with no authoring-layout command carriers.
- Seven focused tests cover JSON/YAML recursion, explicit plugin placeholders, missing export,
  missing source, malformed assets, unsupported package layout, and interpreter options.
- Source and generated plugin copies of the new gate and both repaired assets are byte-identical.
- The run-quality queue has a timing-table verdict: broad-only/stays, because source, export,
  and typed asset corpus form a cross-surface relationship without one safe staged-file trigger.

## Weak

No known target-slice weakness remains after the bounded review repairs. The gate does not
attempt shell parsing or arbitrary non-command strings; that boundary is intentional.

## Missing

- Installed-consumer execution and provider/remote CI proof are absent by contract.
- Commands using interpreter options with arguments, shell composition, or non-Python
  executable forms beyond the supported matcher are not a general shell parser.

## Deferred

Broader command-language normalization and consumer roundtrip proof remain follow-up work;
they are not required to resolve the current typed-asset reachability class.

## Advisory

- structural review result: command: capability_needed=shipped assets must preserve executable command
  reachability; current_centers=typed asset parser plus source/plugin mapper; next_center=
  one bundle-level detector; move=existing-gate-reuse with proof boundary=62-asset scan
  and focused fixtures; enforcement_posture=existing-gate-reuse; command:
  python3 scripts/check_plugin_asset_command_carriers.py --repo-root . --require-git-file-listing.
- Maintainer-Local Enforcement disposition: healthy; command:
  python3 scripts/validate_maintainer_setup.py --repo-root .; the checked-in pre-push
  path invokes scripts/run-quality.sh --read-only.

## Delegated Review

- Delegated Review: executed — round 1 found missing timing classification, source-missing
  fail-open, and package-layout ambiguity; all were repaired. Round 2 confirmed those
  repairs and found interpreter-option bypass; that was repaired with two option fixtures.
- Boundary fingerprints: round 1 issue483-nonmarkdown-r1 verified clean; round 2 was
  parent-attributed only for declared edits, with no undeclared drift. The round-2 repair
  is accepted-unreviewed under the repo's two-round cap; no third round is claimed.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof):
  not_applicable; this is a deterministic static bundle gate.

## Commands Run

- pytest -q tests/quality_gates/test_plugin_asset_command_carriers.py — 7 passed.
- python3 scripts/check_plugin_asset_command_carriers.py --repo-root . --require-git-file-listing — 62 assets passed.
- python3 scripts/check_timing_layer_completeness.py --repo-root . — 89 validators classified.
- python3 scripts/sync_root_plugin_manifests.py --repo-root . — source/plugin mirrors synchronized.
- python3 scripts/check_plugin_dir_references.py --repo-root . — passed in reviewer read-only checks.
- python3 scripts/check_doc_links.py and check_documented_command_flags.py — passed in the focused portability run.

## Recommended Next Quality Moves

- active capability_needed=typed shipped assets must keep commands reachable; next_center=
  structured carrier detector; transformation=retain source-missing/export-missing and
  interpreter-option fixtures; proof_boundary=the bundle gate plus generated parity;
  enforcement_posture=existing-gate-reuse; command:
  python3 scripts/check_plugin_asset_command_carriers.py --repo-root . --require-git-file-listing.
- passive capability_needed=installed-consumer command execution because local source/export
  proof cannot reproduce provider installation; next_center=consumer fixture/readback;
  transformation=defer until a real consumer harness exists; proof_boundary=explicit
  roundtrip evidence; enforcement_posture=no-gate because local scope cannot prove it;
  command: python3 scripts/check_plugin_asset_command_carriers.py --repo-root .

## History

- Issue #483 live read on 2026-08-06; remote state remains a separate closeout readback.
- 2026-08-06-issue-482-command-carrier.md — preceding Markdown command-carrier boundary.
- 2026-08-06-issue-484-shared-portable-package.md — preceding shared package boundary.
- [2026-07-19 portable proof-path learning review](history/2026-07-19-portable-proof-path-learning-review.md) — source-before-remedy lesson.
