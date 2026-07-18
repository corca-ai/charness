# Public Skill YAML Detail Output Critique
Date: 2026-07-18

## Decision Under Review

Align public skill copyable planner commands with the root CLI's YAML vocabulary:
full structured output is YAML by default or behind `--detail`, while hidden
legacy `--json` remains real JSON for parser compatibility.

## Failure Angles

- Portability/compatibility: source and plugin layouts must both resolve the
  shared YAML renderer, and the missing-PyYAML fallback must remain valid YAML.
- Operator/agent UX: progressive-disclosure references must not re-teach
  `--json` after the top-level skill changes.
- Scope: Charness-style agent-first output policy must not overwrite
  human-first or third-party native CLI contracts.

## Counterweight Pass

- Act before ship: fix the release index and create-cli reference drift; keep
  legacy `--json` as actual JSON rather than a silently format-changing alias;
  state the agent-first versus human-first/third-party branch explicitly.
- Bundle anyway: add targeted owned-command documentation checks, YAML fallback
  coverage, and default/detail versus hidden-JSON compatibility tests.
- Over-worry: do not convert persisted `.json` artifacts, provider-native flags,
  or always-full planners to inert `--detail` options.
- Valid but defer: none — all concrete findings fit this slice.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/release/references/index.md | action: fix | note: replace the stale copyable --json planner command
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/create-cli/references | action: fix | note: align progressive disclosure and state the agent-first versus native-contract branch
- F3 | bin: act-before-ship | evidence: strong | ref: affected planner parsers | action: fix | note: preserve real JSON output for the hidden legacy compatibility flag
- F4 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_public_skill_yaml_output_contract.py | action: fix | note: test targeted docs, compatibility modes, hidden help, and YAML fallback
- F5 | bin: over-worry | evidence: strong | ref: charness-artifacts/debug/2026-07-18-residual-json-flags-after-yaml-migration.md | action: document | note: exclude persisted artifacts and third-party native JSON contracts
- F6 | bin: act-before-ship | evidence: strong | ref: AGENTS.md | action: fix | note: migrate the governing Cautilus planner call and its live operator references to YAML detail output
- F7 | bin: over-worry | evidence: strong | ref: tests/test_cautilus_proof_artifact.py | action: defer | note: final bounded review found the focused YAML/detail, hidden-JSON, help, follow-up, and live-instruction coverage sufficient; do not add more Cautilus-specific output tests
- F8 | bin: act-before-ship | evidence: strong | ref: docs/handoff.md | action: fix | note: bind the next-release decision to both unreleased post-v2.0.0 changes so the YAML correction cannot silently displace the update/init self-heal
- F9 | bin: bundle-anyway | evidence: strong | ref: docs/handoff.md | action: fix | note: label the correction uncommitted and separate restart evidence for installed v2.0.0 from the uninstalled local change
- F10 | bin: act-before-ship | evidence: strong | ref: scripts/inventory_boundary_bypass_lib.py | action: fix | note: recognize yaml.safe_load(stdout) as structured behavior proof alongside json.loads(stdout), preventing a false keep-boundary increase after the format migration
- F11 | bin: act-before-ship | evidence: strong | ref: scripts/check_skill_contracts.py | action: fix | note: replace the old required risk-interrupt --json snippet with --detail so representative skill scenarios enforce the migrated live contract

## Reviewer Tier Evidence

- Requested tier: high-leverage for a public-skill/workflow/export change.
- Requested spawn fields: model gpt-5.6-terra, reasoning_effort medium,
  service_tier priority, fork_turns none.
- Host exposure state: requested_fields_sent
- Application state: host accepted the requested fields; provider application metadata was not exposed.

## Fresh-Eye Satisfaction

parent-delegated — two distinct angle reviewers and a separate counterweight
reviewer completed read-only passes. Parent-side fingerprints verified cleanly
after both angle reviews, the counterweight review, the final Cautilus-scope
review, and the handoff refresh review.

## Boundary Ownership

- Producer: public skill copyable commands and their planner output parsers.
- Consumer: agents executing bootstrap/closeout commands from installed skills.
- Owning surface: public skill command contracts plus source/plugin helper
  implementations and focused compatibility tests.
- Verdict: owned-correctly
