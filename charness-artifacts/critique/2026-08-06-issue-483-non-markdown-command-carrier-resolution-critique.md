# Issue #483 Non-Markdown Command Carrier Resolution Critique
Date: 2026-08-06

## Decision Under Review

Add a typed JSON/YAML/YML shipped-asset gate for authoring-layout command carriers,
repair the two live source assets, mirror the gate, and run it at the broad bundle
boundary. Success is local structured-asset reachability proof, not consumer runtime proof.

## Failure Angles

- Typed parser gaps could miss nested strings, malformed assets, or assets outside a package.
- Source/export checks could fail open when the authoring source or generated export is absent.
- Interpreter options could hide a command target from a simplistic adjacent-token matcher.
- A new run-quality label could bypass the timing classification meta-gate.
- Over-broad shell parsing could report prose or module arguments as executable file carriers.

## Counterweight Pass

Round 1 found the timing-table omission, source-missing fail-open, and package-layout ambiguity;
these were repaired with a timing row, fail-closed findings, and regression tests. Round 2
confirmed those repairs and found the real interpreter-option bypass; the matcher now accepts
option flags and tests cover -u and --isolated. The two-round cap means that final round-2
repair is accepted-unreviewed, not claimed as a third fresh-eye result. Shell-language
generalization and consumer runtime remain valid deferrals.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/check_plugin_asset_command_carriers.py and tests/quality_gates/test_plugin_asset_command_carriers.py | action: fix | note: source-missing, unsupported-layout, malformed-asset, and option-bearing carriers must fail closed; implemented and covered.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/run-quality.sh and docs/conventions/validator-timing-layers.md | action: fix | note: every queued validator needs an explicit timing verdict; implemented and meta-gate passes.
- F3 | bin: bundle-anyway | evidence: strong | ref: integrations/tools/vulture.json and skills/public/achieve/adapter.example.yaml | action: fix | note: both live authoring-layout carriers now use plugin-relative paths and generated mirrors match.
- F4 | bin: valid-but-defer | evidence: moderate | ref: COMMAND_RE and the typed asset scope | action: defer | note: this is not a general shell parser and does not claim arbitrary strings or consumer execution.
- F5 | bin: over-worry | evidence: weak | ref: remote CI and installed plugin behavior | action: defer | note: those channels are explicitly separate proof obligations, not blockers for local static ownership.

## Reviewer Tier Evidence

- Requested tier: gpt-5.6-terra with medium reasoning effort.
- Requested spawn fields: model gpt-5.6-terra, reasoning_effort medium, service_tier priority, fork_context false, unnamed one-shot bounded reviewer.
- Host exposure state: applied
- Application state: host-confirmed: two reviewers returned findings for round 1 and repaired-surface round 2.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated: round 1 reviewer 019fd479-eb03-7d31-936e-c924be5af373 returned
three findings; round 2 reviewer 019fd47d-82c3-79b1-b937-5291cfcd8a58 confirmed the
repairs and found the interpreter-option bypass. Boundary round 1 verified clean.
Round 2 had only declared parent-attributed edits after return and no undeclared drift.
The final round-2 repair is accepted-unreviewed under the two-round cap.

## Reviewed Input Identity

No critique packet was consumed; both reviewers read the changed checker, tests, queue,
timing table, source/plugin assets, and focused checks directly.

## Boundary Ownership

- Producer: scripts/check_plugin_asset_command_carriers.py extracts typed asset strings and maps source to shipped paths.
- Consumer: run-quality's bundle verdict for plugin structured assets and the generated plugin package.
- Owning surface: the new checker, its tests, synchronized plugin mirror, and the two repaired source assets.
- Verdict: owned-correctly
