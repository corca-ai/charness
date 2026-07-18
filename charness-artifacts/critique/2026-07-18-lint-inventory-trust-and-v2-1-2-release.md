# Lint inventory trust and v2.1.2 release critique
Date: 2026-07-18

## Execution

- Two bounded read-only angles reviewed parsing compatibility and
  boundary/operability; a separate counterweight triaged their disagreement.
- The prepared packet was consumed before broad sampling, and parent fingerprint
  verification found no worktree, index, or HEAD drift.

## Packet Consumed

`charness-artifacts/critique/2026-07-18-110224-packet.md`

## Target

Code critique plus patch-release lock-in.

## Decision Under Review

Split suppression parsing by syntax family, repair malformed-Python fallback,
reuse stable test fixtures, and publish the compatible behavior repair as
v2.1.2.

## Diff Scope

One shared inventory producer and its generated plugin mirror, four focused
test modules, repo-Markdown closeout routing, and the
quality/critique/retro/release truth surfaces.

## Capability at Stake

A quality judge must receive exact, compact lint-rule facts and must not lose
the entire inventory when one tracked Python file is temporarily malformed.

## Failure Angles

- Parsing compatibility: prose must not become codes, while ESLint/Pylint
  hyphenated names and normal Python rule identifiers remain intact.
- Boundary ownership: repair the producer rather than hiding junk in the YAML
  renderer; source remains canonical and plugin output derived.
- Operability/economics: malformed input must degrade to one honest fallback;
  stable-file reuse must not imply a measured speedup.

## Findings

- The initial patch caught `TokenError` only around generator construction,
  although Python raises it during token iteration. Materializing tokens inside
  the exception boundary fixes the cause and prevents partial-result duplication.
- Invalid/mixed directives need an explicit parse-status contract before they
  can be distinguished from blanket directives; no repo instance justifies that
  expansion now.
- Module constants read immutable repo fixtures and are safe for these tests.
- The first locked closeout exposed an existing durability validator missing
  from repo-Markdown surface routing; moving that existing check before broad
  pytest closes the recurrence without adding a new floor.

## Counterweight Pass

- Act before ship: repair atomic tokenizer fallback, add malformed-source proof,
  and route the existing evidence-durability check before broad pytest; completed.
- Bundle anyway: retain source/plugin byte verification and ordinary sync gates.
- Over-worry: cache invalidation for root fixtures that no test mutates.
- Valid but defer: invalid-directive schema work without an observed consumer.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/lint_ignore_inventory_lib.py | action: fix | note: token iteration escaped the fallback boundary; materialize atomically and test malformed EOF
- F2 | bin: valid-but-defer | evidence: moderate | ref: scripts/lint_ignore_inventory_lib.py | action: defer | note: invalid-directive classification needs an output-contract decision and has no observed instance
- F3 | bin: over-worry | evidence: strong | ref: tests/charness_cli/test_version_surface.py | action: document | note: stable root fixtures are not mutated during their module lifecycle
- F4 | bin: bundle-anyway | evidence: strong | ref: plugins/charness/scripts/lint_ignore_inventory_lib.py | action: document | note: retain byte sync and packaging proof without a speedup claim
- F5 | bin: act-before-ship | evidence: strong | ref: .agents/surfaces.json | action: fix | note: route existing Markdown evidence durability before broad pytest after the first locked run exposed the missing obligation

## Deliberately Not Doing

- No new gate: existing behavior, sync, packaging, ruff, durability, and
  changed-line gates own the deterministic contract; only routing changed.
- No lint-site count reduction target and no wall-clock speed claim.
- No Cautilus evaluation; its planner returned `not-required`.

## Boundary Ownership

- Producer: `scripts/lint_ignore_inventory_lib.py` produces parsed suppression facts.
- Consumer: quality agents/operators reading the YAML inventory.
- Owning surface: canonical root producer with generated plugin mirror.
- Verdict: owned-correctly

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `fork_turns=none`, `model=gpt-5.6-terra`,
  `reasoning_effort=medium`, `service_tier=priority`.
- Host exposure state: requested_fields_sent
- Application state: host accepted fields; provider application metadata hidden.

## Fresh-Eye Satisfaction

parent-delegated

## Release Scope

Patch v2.1.2: accurate lint-ignore rule payloads, resilient malformed-source
inventory, and test-only stable-file reuse.

## Surface-Lock Inventory

- Generated artifacts: plugin manifests/version metadata and the synchronized
  plugin copy of the inventory producer.
- Consumer behavior: compact/full YAML inventory `codes` fields and fallback
  completion on malformed Python.
- Documentation: release record, quality review, critique, retro, and handoff.
- Adapters/integrations: no contract change; existing release adapter drives sync.

## Operator Action Required

- Use the repo release helper for bump, quality, fresh-checkout probes, tag,
  publish, distinct-channel readback, and installed refresh.

## Upgrade Path

Run `charness update`; the change is backward compatible and needs no migration.

## Defect Class Cross-Link

`charness-artifacts/retro/recent-lessons.md`: executable final-consumer proof and
producer/consumer ownership must remain distinct.

## Next Move

Run fix verification, locked closeout, patch release planning, then publish only
after every release observable is populated.
