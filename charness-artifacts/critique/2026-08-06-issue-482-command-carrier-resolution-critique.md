# Issue #482 Command Carrier Resolution Critique
Date: 2026-08-06

## Decision Under Review

Make command carriers in shipped portable skill Markdown consumer-relative: reject
source-existing `skills/public/...` or `skills/support/...` command paths,
require `$SKILL_DIR/...` for the current skill or `<plugin-dir>/...` for another
shipped package, and make missing export state explicit.

Success means all known kind-bearing command sites are repaired and future
authoring-layout commands fail in source trees, including partial trees without
`plugins/`. This slice does not claim installed-consumer execution.

## Failure Angles

- **Consumer path ownership**: resolving only against the authoring checkout can
  make a command appear runnable while its kind-bearing path is absent in a
  consumer.
- **Export fail-open**: requiring a mapped target to exist in the plugin mirror,
  or requiring `root/plugins` to exist, can silently waive the command in a
  partial/export-drift tree.
- **Placeholder semantics**: `$SKILL_DIR` must remain the consuming skill's
  anchor for shared references; `<plugin-dir>` must remain an accepted explicit
  shipped-package form.
- **Scope/false positives**: path mentions in prose must not be treated as
  commands, and the command flag gate must retain its separate argparse role.

## Counterweight Pass

Round 1 found a real export-omission fail-open, and round 2 found the related
missing-plugin-directory fail-open. Both were repaired with focused fixtures;
the final suite passes and the source/plugin mirrors are synchronized. The
two-round cap is the repo contract's stopping rule, so the round-2 repair is
recorded as accepted-unreviewed rather than claiming a third review. Consumer
execution and non-Markdown carriers remain explicit follow-ups.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: `scripts/check_doc_links.py::iter_unportable_command_targets` and `tests/quality_gates/test_check_doc_links.py::test_a_shipped_skill_command_cannot_use_the_authoring_kind_layout` | action: fix | note: authoring kind-bearing commands must be judged from the consumer path, not only the source checkout; implemented and covered.
- F2 | bin: act-before-ship | evidence: strong | ref: `tests/quality_gates/test_check_doc_links.py::test_an_authoring_skill_command_is_rejected_when_export_omits_target` and `::test_an_authoring_skill_command_is_rejected_without_plugin_directory` | action: fix | note: source existence now forces rejection and the message distinguishes exported versus missing export state.
- F3 | bin: bundle-anyway | evidence: strong | ref: 14 repaired Markdown command sites under `skills/public/**/references/` | action: fix | note: own-skill commands use `$SKILL_DIR`; cross-skill commands use `<plugin-dir>/skills/...`, preserving consumer-readable ownership.
- F4 | bin: valid-but-defer | evidence: moderate | ref: `charness-artifacts/quality/2026-08-06-issue-482-command-carrier.md` | action: defer | note: typed JSON/YAML/template carrier coverage and real consumer execution remain #483/future proof scope.
- F5 | bin: over-worry | evidence: weak | ref: prose-only `skills/public/quality/references/automation-promotion.md` kind-bearing path mention | action: defer | note: it is not a command carrier and remains outside the detector by design.

## Reviewer Tier Evidence

- Requested tier: `gpt-5.6-terra` with `medium` reasoning effort.
- Requested spawn fields: model `gpt-5.6-terra`, reasoning effort `medium`, service tier `priority`, `fork_context: false`, unnamed one-shot bounded reviewer for each round.
- Host exposure state: applied
- Application state: host-confirmed: round 1 reviewer `019fd46c-ecef-74c2-802e-0d48ffbc28b5` and round 2 reviewer `019fd46f-4a05-72f1-a687-6bb8ba7d0a69` returned findings.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated: round 1 found the missing-export fail-open and round 2, after
the repair, found the no-plugin-directory fail-open. Boundary fingerprints
`issue482-command-carrier-r1` and `issue482-command-carrier-r2` both verified
clean immediately after their respective returns. Round 2's repair is
accepted-unreviewed under the two-round cap; no third round is claimed.

## Reviewed Input Identity

No critique packet was consumed; both reviewers read the changed checker,
tests, command docs, mirrors, and focused command results directly.

## Boundary Ownership

- Producer: `scripts/check_doc_links.py` extracts command targets and maps authoring layout to shipped layout.
- Consumer: the source Markdown quality gate and downstream plugin/flag gates render path and invocation verdicts.
- Owning surface: `scripts/check_doc_links.py` plus its cohesive `scripts/portable_command_carrier.py` module, with command-carrier tests and synchronized plugin mirrors; `check_documented_command_flags.py` retains argparse ownership.
- Verdict: owned-correctly
