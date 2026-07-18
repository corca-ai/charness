# Quality Review
Date: 2026-07-18
Title: Close quality-infrastructure false greens and ownership seams

## Scope

Target boundary: mutation coverage production through final changed-line consumption, Nose executable transport ownership, and quality-runner fixture economics.

Ambient repo findings: D18 remains ignored per operator direction. The duplicate ratchet found two extractable same-owner families and two intentional portable bootstrap families; the former were removed and the latter were reviewed explicitly.

## Current Gates

- Existing changed-line consumer, closeout focused/broad proof, source/plugin sync, packaging validation, duplicate ratchet, ruff, focused pytest, and the 81-phase read-only quality gate.
- No new blocking floor was added. The slice wires an existing authoritative consumer, adds visible non-claims, and reuses existing pre-push teeth.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; local-linux-x86_64-36cpu profile. <!-- reproduction-source -->
- runtime hot spots: final read-only quality 56.5s versus 56.0s recent median and 90s budget; pytest 36.1s versus 36.1s median and 140s budget.
- coverage gate: 81 passed, 0 failed; focused integration proof passed 207 tests in 29.65s.
- evaluator depth: deterministic-gates-only because range identity, JSON verdict shape, subprocess failures, clone isolation, and mirror bytes are directly observable. Cautilus is ask-before-run and was not executed.

## Healthy

- A successful coverage producer now invokes the existing changed-line consumer; only `ok=true`, an empty `blocking` list, and the exact generated base/head range produce a pass.
- Dirty tracked and untracked eligible files remain nonblocking before commit but render a conspicuous `NOT CHECKED` reason, file list, and exact follow-up command.
- Nose binary resolution, version normalization, and raw JSON subprocess facts have one owner; Markdown and code-report policy remain in their domain consumers.
- `inventory_doc_duplicates.py` moved from 334 to 313 code lines and `nose_report_lib.py` from 331 to 310; the shared transport is 85 lines and synchronized byte-for-byte into the plugin.
- Quality-runner seeds are built once per test module while every test mutates a private clone; a contamination regression test protects the invariant.
- Consumer-execution tests were split from the near-limit producer module behind a 23-line mechanical fixture: producer tests now have 252 lines of headroom and the new consumer module 634.

## Weak

- The prior closeout treated producer exit zero as terminal success and deferred authoritative consumption until the release helper; cumulative proof could therefore fail only at the irreversible boundary.
- The first repair still missed untracked eligible files, accepted any JSON object, and hid the structured non-claim in text mode. Fresh-eye review found all three before closeout.
- The first committed-range consumer then blocked three files on 10 uncovered changed lines. Focused branch tests for malformed commands, range mismatch, idempotent consumption, non-verification, and version normalization closed those exact gaps before release.
- Structural fixture work removes repeated seed construction, but end-to-end pytest timing did not improve beyond noise: the final 36.1s equals the recent median and is slower than the session-opening 34.6s sample. No runtime-win claim is made.

## Missing

- Before this slice, no integration test proved producer-to-consumer blocker propagation, malformed clean-verdict rejection, dirty untracked non-claims, or operator-visible `NOT CHECKED` output.
- Before this slice, no test proved a module-scoped quality seed remained unchanged after a sibling clone mutation.

## Deferred

- A new mandatory post-commit attestation is rejected for now: the existing pre-push gate already consumes the committed range, and another gate would duplicate teeth on reversible work.
- Unifying direct and path-based loading of the stateless Nose helper has no observed identity or state defect.
- Broader nested-CLI cleanup remains a separate testability program; this slice changes only the repeated fixture construction with an explicit isolation proof.

## Advisory

- structural review result: capability_needed=honest final-consumer proof plus single-owner transport; current_centers=producer metadata, changed-line consumer, Nose callers, repeated seed builders; next_center=authoritative consumer execution, `nose_tool_lib`, module seed; transformation=connect, extract, reuse; proof_boundary=range-matched JSON, text non-claim, source/plugin bytes, clone isolation; enforcement_posture=existing-gate reuse under the north star.
- prose review result: quality trigger boundaries and progressive disclosure are unchanged; operator text gained one concise non-claim block. Skill ergonomics reported 22 checked skills and 16 host-reference heuristic hits; none found by inventory were attributable to this helper-only slice.
- command: `inventory_standing_test_economics.py --summary` reports 399 test files and 169 standing-or-mixed nested-CLI files; the fixture optimization does not claim to resolve that broader boundary cost.
- command: duplicate ratchet initially named three families, then two after extraction. Review removed the same-owner loader/result duplication and classified only two small direct-execution bootstrap spans intentional; the final ratchet passed at `fixable_ceiling=0`.
- dogfood/scenario review: keep the maintained `quality` consumer case unchanged. This slice changes helper ownership and closeout proof plumbing, not quality routing, planner primers, artifact expectations, slow-gate lenses, or the public prompt contract; deterministic focused tests and the existing dogfood validator own the changed behavior.

## Delegated Review

- Delegated Review: executed — root-cause/ownership and operability/test-economics angles plus a separate counterweight found four act-before-ship concerns; all were fixed, and a bounded fix-verification pass returned ship-ready.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof): re-delegated. Seed construction falls from per-test to per-module, copytree remains per test for isolation, and no critical-path speedup is claimed without a stable measured delta.
- Reviewer boundary fingerprints verified no worktree/index drift after each review stage; details: `../critique/2026-07-18-quality-infrastructure-correctness-and-v2-1-1-release.md`.

## Commands Run

- quality planner, runtime summary, skill ergonomics, standing-test economics, Python headroom, and changed-surface inventory.
- focused worker proofs: 44 fixture tests, 46 mutation producer/closeout tests, and 86 Nose consumer tests; integrated focused proof: 207 passed.
- `ruff check`, source/plugin sync, packaging validation, duplicate ratchet, artifact preflights, and critique validators.
- `./scripts/run-quality.sh --read-only` — first integrated attempt 80/81 exposed duplicate pressure; final 81/81 in 56.5s with pytest 36.1s.
- first postcommit producer→consumer run — focused and broad pytest passed, then the authoritative consumer blocked three files; branch-focused tests were added and the exact committed range was regenerated rather than waived.

## Recommended Next Quality Moves

- active publish v2.1.1 after committed-range coverage proof — capability_needed=installed honest quality infrastructure; next_center=release helper; transformation=patch bump, clean-checkout proof, public publish/readback, installed refresh; proof_boundary=distinct public HTTPS plus installed-version channel; enforcement_posture=irreversible-boundary helper.
- passive revisit broader nested-CLI consolidation only after per-family profiling because capability_needed=lower standing-suite cost without losing delivery-boundary proof; next_center=the highest repeated subprocess family, not raw file count; transformation=move repeated behavior in-process and retain thin binary smokes; proof_boundary=selected-vs-broad parity and repeated timing; enforcement_posture=no-gate because current timings remain within budget and causality is not yet measured.

## History

- [Prior durable quality review](history/2026-07-14-open-issue-resolution-proof.md)
