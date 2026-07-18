# Quality Review
Date: 2026-07-18
Title: Dynamic entrypoint evidence and structural dead-code quality

## Scope

Target boundary: eliminate the two recurring dead-code review-candidate false positives without hiding stale dynamic exports, weakening plugin portability, or creating a broad allowlist.

Ambient repo findings: D18 remains ignored. Existing near-limit files, test/production ratio, doc-clone advisories, and stale timing samples are reported but not attributed to this slice.

## Structural Packet

- capability_needed: maintainers need a zero-noise dynamic-entrypoint inventory whose exemptions are backed by producer-to-consumer evidence.
- sequencing_applicability: mutation, mirror sync, adversarial review, and broad verification must stay ordered; general dynamic analysis is not a prerequisite.
- current_centers: Vulture findings, git-visible scan scope, source-role AST evidence, and human deletion judgment.
- next_center: conservative bidirectional evidence at the existing advisory classifier.
- quality_move_card: recognize only exact caller-sibling runpy and registry-to-import-to-dispatch flows; prove positive and lookalike-negative fixtures; keep enforcement advisory.
- enforcement_posture: existing-gate-reuse for packaging, tests, and duplication; no new blocking floor.
- authoring_form_relevance: helper ownership matters because the original classifier was near its length band; split AST evidence into cohesive source-role and dynamic-entrypoint modules.

## Current Gates

- Focused advisory and quality-runner tests own classification behavior, fail-closed helper branches, and human-output compatibility.
- Dup ratchet owns new copy-pattern pressure; it initially rejected two families, which were structurally removed rather than baselined.
- Packaging, plugin import smoke, and committed-mirror checks own portable export parity.
- Broad read-only quality and locked slice closeout own final repository confidence; the advisory itself never blocks or authorizes deletion.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` rendered by `render_runtime_summary.py`; `local-linux-x86_64-36cpu`. <!-- reproduction-source -->
- runtime hot spots: read-only quality latest/median 64.0/57.6s against 90s; pytest latest/median 43.9/39.8s against 140s.
- coverage gate: focused 58-test proof passed; the first committed-range consumer exposed 14 uncovered fail-closed lines, which now have direct fixtures. Final refreshed consumer proof remains a closeout action.
- evaluator depth: deterministic-gates-only; exact AST fixtures, live advisory output, mirror bytes, duplication scan, broad pytest, and release readback directly observe this slice. Cautilus remained ask-before-run and was not executed.

## Healthy

- Live sweep stays at 21 total findings but moves the final two from `review_candidate` to `registered_dynamic_entrypoint`; the review-candidate sample is empty.
- A matching string alone, wrong absolute or nested path, unrelated loader/receiver, and loop disconnected from the declared registry all remain review candidates.
- The main advisory module moved from 317 to 274 code lines, leaving 86 lines of headroom; evidence helpers have more than 170 lines each.
- Advisory wall time remained around 8.9-9.1s versus the 8.92s baseline; no material regression was observed.
- Source/plugin copies are synchronized and focused pytest, ruff, compile, packaging, and gitignore-aware scan checks pass.

## Weak

- The evidence recognizer intentionally supports only two exact local dynamic idioms; a new legitimate syntax will initially reappear as review noise.
- Static syntax evidence cannot prove runtime branch reachability or semantic correctness of the dispatcher.

## Missing

- No blocking gap is missing for this bounded capability. Final locked changed-line proof remains a closeout action, not a claimed result in this review.

## Deferred

- Add another bounded syntax witness only after a real recurring candidate demonstrates demand.
- Do not add generic points-to analysis, replace portable dynamic calls, or cache scans without a measured correctness or runtime need.

## Advisory

- structural review result: artifact: `charness-artifacts/critique/2026-07-18-dynamic-entrypoint-evidence.md`; strengthen the existing advisory center and leave ambiguous work to judgment.
- prose review result: command: `inventory_skill_ergonomics.py --summary`; all 16 skill findings are host-surface references. Core overfill, mode pressure, prose ritual, path ambiguity, issue/date anchors, reference discoverability, and missing argparse help are zero. Trigger boundaries and progressive disclosure remain healthy; named host/adaptor seams are intentional ambient portability structure.
- runtime review result: command: `render_runtime_summary.py --summary`; no runtime-visibility or missing-sample findings. Six stale hotspot labels remain ambient maintenance evidence.
- command: `./scripts/run-quality.sh --read-only`; the first 80/81 run failed only on two new duplicate families; the focused duplicate scan is now clean with no baseline acceptance.

## Delegated Review

- Delegated Review: executed — correctness and architecture angles plus a separate counterweight repeatedly reviewed the conservative evidence syntax; final verdicts were SHIP.
- Parent fingerprints verified zero worktree, index, or HEAD drift after each final reviewer. The initial packet/fingerprint race was quarantined and not counted as approval.
- Slow-gate lenses: fixture-economics is bounded to cheap synthetic repos; parallel-critical-path is unchanged; duplicated-proof review found focused classification, broad pytest, duplication, and changed-line checks cover distinct seams rather than repeat one assertion.

## Commands Run

- `pytest` focused advisory plus quality runner: 58 passed; broad quality pytest passed in 43-48s across locked runs.
- Exact-line proof: changing `dynamic_entrypoint_evidence.py:14` from recursive caller-path validation to `False` made the new fail-closed branch test fail; restoring it passed.
- Live dead-code summary: primary clean; sweep 21 findings; 2 registered dynamic entrypoints; 0 review candidates.
- Dup ratchet after refactor: zero new code/doc families; ruff, compile, packaging, skill validation, plugin sync, and artifact validators passed.
- Final locked closeout and irreversible release verification remain downstream phase barriers.

## Recommended Next Quality Moves

- active keep dynamic exemptions evidence-paired — capability_needed=credible attention; next_center=existing classifier; transformation=exact producer-consumer witness; proof_boundary=positive and negative AST fixtures plus live inventory; enforcement_posture=advisory.
- passive broaden syntax only after recurring real noise because speculative reachability machinery would cost more than the two proven consumers — capability_needed=lower triage cost; next_center=observed missed consumer; transformation=bounded witness; proof_boundary=reproduction fixture; enforcement_posture=no-gate.
- passive revisit stale timing labels during dedicated gate-economics work because this slice did not change their commands or budgets — capability_needed=current cost evidence; next_center=runtime signals; transformation=refresh measurements; proof_boundary=structured samples; enforcement_posture=no-gate.

## History

- [Prior durable quality review](history/2026-07-14-open-issue-resolution-proof.md)
