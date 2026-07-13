# Find-Skills Legacy Removal And v1.0.0 Release Critique
Date: 2026-07-13

## Decision Under Review

Remove every active `find-skills` compatibility seam, retain only canonical
`session_routing` and `capability-catalog` surfaces, then publish Charness
v1.0.0. Historical dated audit records remain immutable evidence.

## Failure Angles

- First-reader / rename cascade: active hook filenames, module APIs, adapter
  keys, tests, and operator docs still teach `find-skills` ownership even though
  the public skill is gone.
- Operational release: removing old adapter inputs and hook paths is a breaking
  migration; v1.0.0 notes must state the canonical replacements, cleanup step,
  rollback target, update command, and restart expectation.
- Implementation integrity: registry wiring, schema, catalog sources, CLI
  status, current-pointer validator aliases, evaluator fixtures, and checked-in
  plugin mirrors must move together.

## Counterweight Pass

- Act before ship: remove legacy adapter inputs and paths; rename the active
  hook module/script/APIs/tests; update registry, schema, CLI status, active
  evaluator fixtures and docs; sync exports; bump and verify v1.0.0.
- Bundle anyway: preserve old marker removal only as one-way deletion of owned
  host state, under canonical cleanup names. It must not accept or advertise an
  old configuration shape.
- Over-worry: do not rewrite dated artifacts or explicit historical fixtures.
- Valid but defer: broad concept-history prose may remain when it is plainly
  historical and not consumed by an active workflow or operator path.

## Rename Scope

- `host_hook_find_skills.py` -> `host_hook_session_routing.py`
- `session_start_find_skills.py` -> `session_start_routing.py`
- `find_skills_routing` -> removed; canonical `session_routing` only
- `find-skills-adapter.yaml` candidates -> removed; canonical
  `capability-catalog-adapter.yaml` only
- `find_skills` function/constant/test names -> canonical session-routing or
  capability-catalog names

## Allowlist Inventory

- Allowed: dated `charness-artifacts/**` audit records, explicit historical
  fixtures/transcripts, and v1.0.0 release/retro text that says the surface was
  removed.
- Rejected: active `scripts/`, `plugins/charness/scripts/`, integration schemas,
  generated exports, current operator docs, active evaluators, and tests that
  assert old inputs still work.
- One-way deletion of old host hook markers is allowed only when owned and
  named as cleanup, never as compatibility.

## First-Reader Probe Result

Pre-change FAIL. A reader who knows only session routing and capability catalog
still encounters active `find-skills` module/script names, schema aliases,
adapter paths, CLI output, and operator docs. Post-change release review must
repeat the probe against the canonical names only.

## Slug Drift Result

The rename reviewer ran the advisory title/slug checker. It reported only
unrelated existing drift in quality and retro references; no routing/catalog
slug issue was reported. This does not waive the active cite cascade above.

## Release Scope

- Current public version: v0.66.4
- Target: v1.0.0 (major because invocation/configuration compatibility is
  removed and operators must migrate)
- Consumer change: ordinary workflow routing uses installed skill metadata and
  model judgment; hidden availability uses `charness catalog`; session context
  uses only the canonical session-routing hook.

## Surface-Lock Inventory

- Versioned packaging and checked-in plugin exports.
- SessionStart hook module, script, registry, state/status, settings scan, and
  host adapter schema.
- Capability catalog source discovery and current-pointer validation.
- CLI help/status and generated CLI reference.
- Active routing/evaluator fixtures, setup output, README/operator docs, and
  release notes.
- Fresh-checkout probes, public GitHub release visibility, and maintainer
  install refresh/readback.

## Upgrade Path

- Rename adapter key `find_skills_routing` to `session_routing`.
- Rename any `find-skills-adapter.yaml` file to
  `capability-catalog-adapter.yaml`.
- Remove old owned SessionStart hook entries before installing the canonical
  hook, then run `charness update` and restart Claude Code/Codex.
- Roll back to v0.66.4 if migration must be reversed.

## Operator Action Required

- Publish notes must carry the breaking migration and rollback instructions.
- The release helper must run sync, release quality, fresh-checkout probes,
  distinct-channel public readback, and maintainer install refresh.

## Scenario Review

The deterministic Cautilus planner reported `required: false`,
`scenario_registry_review_required: false`, and `next_action: none`. The active
agent-runtime routing fixture was updated from a mandatory discovery bootstrap
to canonical direct routing, while no maintained Cautilus scenario needed to be
added or removed. No live Cautilus evaluation was run under the repo's
ask-before-run policy.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/host_hook_find_skills.py:52 | action: fix | note: remove legacy runtime and schema adapter key
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/host_hook_registry.py:49 | action: fix | note: rename active hook module script APIs constants and tests
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/capability_catalog_sources.py:34 | action: fix | note: remove legacy adapter path lookup and warning behavior
- F4 | bin: act-before-ship | evidence: strong | ref: packaging/charness.json:5 | action: fix | note: bump sync verify and publish v1.0.0 through the release helper
- F5 | bin: act-before-ship | evidence: moderate | ref: tests/agent-runtime/native.test.mjs:66 | action: fix | note: remove active evaluator assumptions about mandatory find-skills bootstrap
- F6 | bin: bundle-anyway | evidence: strong | ref: docs/support-skill-policy.md:97 | action: fix | note: update active owner documentation while the surface is open
- F7 | bin: bundle-anyway | evidence: strong | ref: scripts/host_hook_find_skills.py:42 | action: fix | note: retain old marker deletion only as canonical one-way cleanup
- F8 | bin: over-worry | evidence: moderate | ref: charness-artifacts | action: document | note: preserve historical dated audit records
- F9 | bin: valid-but-defer | evidence: weak | ref: docs/retro-self-improvement-spec.md:119 | action: defer | note: historical concept prose is not a runtime compatibility seam

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority
- Host exposure state: requested_fields_sent
- Application state: host accepted the requested fields but did not expose provider-side application confirmation

## Fresh-Eye Satisfaction

parent-delegated. Three distinct angle reviewers and one separate counterweight
reviewer completed read-only passes; every parent boundary fingerprint verify
returned `ok: true` with no drift.

Post-change, a separate bounded reviewer consumed
`charness-artifacts/critique/2026-07-13-033046-packet.md`. It rendered PASS for
the compatibility-removal slice and first-reader probe, and correctly held the
release boundary until the v1.0.0 bump plus release-helper verification,
publication readback, and install refresh. Its boundary fingerprint also
returned `ok: true` with no drift. Retired JSON hook entries are cleanup-on-
reconcile rather than pre-reconcile status-visible; that optional observability
extension is deliberately not another compatibility surface or release blocker.

## Boundary Ownership

- Producer: session-routing hook and capability-catalog source owners
- Consumer: host settings reconciliation, CLI operators, installed agents, and release users
- Owning surface: integrations-and-control-plane plus checked-in-plugin-export
- Verdict: moved-to-owner

## Packet Consumed

`charness-artifacts/critique/2026-07-13-031004-packet.md`
