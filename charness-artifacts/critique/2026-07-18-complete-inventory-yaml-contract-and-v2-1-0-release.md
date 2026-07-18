# Complete inventory YAML contract and v2.1.0 release
Date: 2026-07-18

## Execution

- Two independent angle reviewers and a separate counterweight reviewer ran read-only in the shared worktree.
- Parent fingerprints verified no worktree, index, or HEAD drift after every review and fix-verification pass.
- After the first release attempt stopped on cumulative coverage, a new bounded reviewer checked the repair. One review was quarantined because the parent changed retro artifacts during it; the repeated final review ran against a frozen tree and its parent fingerprint verified no drift.

## Fresh-Eye Satisfaction

parent-delegated

## Packet Consumed

- `charness-artifacts/critique/2026-07-18-074508-packet.md`
- Fix verification: `charness-artifacts/critique/2026-07-18-075354-packet.md`

## Target

`release-critique.md`: code/interface correctness plus release lock-in for v2.1.0.

## Decision Under Review

Ship one coherent v2.1.0 bundle in which every quality inventory and every inventory-dispatch command exposes compact summary YAML, full detail YAML, and hidden JSON compatibility, then publish through the repo release helper.

## Release Scope

- Version/tag: `2.1.0` / `v2.1.0`.
- Consumer change: quality review no longer mixes legacy text/JSON-first inventories with YAML-first commands; programmatic JSON compatibility remains hidden.

## Capability at Stake

Agents need bounded first-read evidence without losing full attribution, programmatic compatibility, failure status, or explicit mutation boundaries.

## Surface-Lock Inventory

- Shared output selector and bounded-list helper under `skills/public/quality/scripts/summary_output_lib.py`.
- Twenty `inventory_*.py` commands and seven additional dispatch commands, including runtime, duplicate-ratchet, dogfood, and behavior-recommendation surfaces.
- `references/inventory-dispatch.md`, quality catalog brief, and `.agents/surfaces.json` verifier command.
- Source/plugin generated mirrors and marketplace/version manifests produced by the release helper.
- Focused CLI tests, all-inventory semantic contract test, release notes, public tag/release, and installed plugin cache.

## Failure Angles

- Interface semantics: incompatible output flags, changing exit codes, unsafe write/probe defaults, unbounded summaries, or omitted error diagnostics.
- Structural ownership: dispatch-only coverage that misses undispatched inventories, prose-regex drift, source/plugin divergence, and duplicated subprocess cost.
- Release operations: a green local helper without public tag/release visibility, fresh-checkout proof, real-host proof, or installed-version readback.
- Proof composition: green slice-local coverage that does not cover the complete range from the last public tag, or a claimed cumulative result whose retained coverage report belongs to another head.

## Counterweight Pass

- Act before ship: reject Markdown plus structured modes; bound diagnostic arrays with counts/samples/truncation; execute semantic YAML/JSON parity for every source inventory; make plugin proof exact-copy rather than duplicated execution; isolate the mutable pytest-temp signal. All were fixed and independently rechecked PASS.
- Bundle anyway: replace the remaining agent-facing `.agents/surfaces.json` inventory verifier `--json` call with `--detail`; done.
- Over-worry: hidden JSON compatibility itself is not a defect because programmatic consumers require it and help/agent docs do not teach it.
- Valid but defer: a structured dispatch registry could replace the canonical backtick syntax if that syntax actually starts drifting; no second registry or new gate is justified now.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/recommend_behavior_test.py | action: fix | note: conflicting Markdown and structured modes now fail at parse time and all three conflicts are tested.
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/summary_output_lib.py | action: fix | note: unbounded high-variance arrays now emit count, bounded sample, and truncation signals with oversized fixtures.
- F3 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_public_skill_yaml_output_contract.py | action: fix | note: all source inventories receive semantic parity probes, plugin commands are byte-matched, and mutable temp-footprint input is isolated.
- F4 | bin: valid-but-defer | evidence: moderate | ref: skills/public/quality/references/inventory-dispatch.md | action: defer | note: keep the documented canonical command syntax until observed drift earns a structured registry.
- F5 | bin: act-before-ship | evidence: strong | ref: scripts/check_spec_evidence_durability.py | action: fix | note: CommonMark ordered-list continuation markers were declared by the regex but excluded by a later unordered-only condition; root/plugin code and positive/negative regression tests now agree.
- F6 | bin: act-before-ship | evidence: strong | ref: reports/mutation/test-coverage.json | action: fix | note: the first release attempt correctly stopped before commit/tag/push on nine cumulative coverage blockers. Behavior-focused in-process tests were added, but the retained report inspected by the final reviewer belonged to an older head. Commit the repair, regenerate coverage for exact `v2.0.0..HEAD`, and require the same consumer to return clean before publishing.

## Operator Action Required

- Run release prep/dry-run and the release-only gate after the implementation commit.
- Before release execution, run a verification-locked cumulative coverage producer and consumer for the committed `v2.0.0..HEAD` range; do not cite a prior report or slice-local green as this proof.
- Publish only through `publish_release.py --part minor --execute --critique-artifact ...`.
- Treat helper success as provisional until distinct public release/tag readback, fresh checkout/real-host proof, and installed v2.1.0 readback all pass.

## Upgrade Path

- Upgrade: run the release helper's post-publish `charness update`, then verify doctor and installed plugin version.
- Rollback: reinstall the prior `v2.0.0` tag if an external consumer finds a regression; no stored adapter migration is required because JSON compatibility remains available.

## Deliberately Not Doing

- No Cautilus evaluation: the change is deterministically observable and Cautilus remains ask-before-run.
- No new standalone quality gate: the existing YAML contract test owns the structural invariant.
- No removal of hidden JSON or persisted JSON artifact seams used by programmatic consumers.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `fork_turns=none`, `model=gpt-5.6-terra`, `reasoning_effort=medium`, `service_tier=priority`.
- Host exposure state: requested_fields_sent
- Application state: host accepted the requested spawn fields; provider-side application metadata was not exposed.

## Boundary Ownership

- Producer: each quality inventory builds its full evidence payload; `summary_output_lib.py` owns encoding selection and bounded list projection.
- Consumer: agent quality runs, programmatic compatibility consumers, and packaged plugin users.
- Owning surface: public quality skill source with generated plugin mirrors.
- Verdict: owned-correctly

## Next Move

Commit the cumulative-coverage repair and this disposition, regenerate and consume exact `v2.0.0..HEAD` coverage on that commit, then execute the v2.1.0 release helper and verify it from a distinct public channel.
