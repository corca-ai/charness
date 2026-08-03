# Slice D Producer and Export Boundary Critique
Date: 2026-08-04

## Decision Under Review

Move goal-value invariants into `goal_artifact_lib.py`, apply them to the exact
values the handoff drafter renders before any filesystem write, extend export
safe-import detection only for the supported literal `import_repo_module` call,
and make adapter validation run in both source and flattened plugin layouts.

Diff scope is limited to the two goal producers, the export-safe import gate,
the adapter validator and its generated mirror, plus behavioral tests. The
capability at stake is consistent artifact safety and a runnable exported
validator. Template consolidation, general package-loader redesign, arbitrary
dynamic-import inference, and release actions are out of scope.

## Failure Angles

- Jackson / problem framing: the repairs match the three confirmed failures —
  the drafter's unsafe heading, the AST gate's missed helper string, and the
  exported validator's `skills.public` import/layout assumptions. The drafter
  validates the canonical title/body pair and renders those same normalized
  values.
- Weinberg / diagnostic ownership: value-owned normalization, prose shape, and
  total-loss supplied-slug rejection moved to `goal_artifact_lib.py`; caller
  transport and status policy stayed in `upsert_goal.py`. Adapter loading uses
  an explicit source/flattened path rather than changing generic module-root
  resolution.
- Gawande / operational path: hostile draft refusals happen before `mkdir` or
  `write_text`, existing post-write `check_goal` rollback remains, and the
  exported entrypoint is exercised through a fresh export subprocess.
- Raskin / operator surface: refusal messages retain the existing actionable
  shape, while the export scanner's deliberate non-claims are pinned by
  negative tests instead of promising arbitrary dynamic import analysis.

## Counterweight Pass

- Act Before Ship: validate and write the same canonicalized draft values;
  prove a real flattened exported validator invocation; select the matching
  resolver glob instead of scanning the wrong layout. These were strong findings
  from source and reproductions and are implemented.
- Bundle Anyway: add exact literal-call detection and controls for variables,
  aliases, f-strings, concatenation, near-miss prefixes, and unrelated strings;
  add explicit-slug refusal and auto-draft fallback tests. These are cheap
  additions in the touched test surfaces and are implemented.
- Over-Worry: infer assignments, aliases, or arbitrary `importlib`/dynamic
  imports; redesign `runtime_bootstrap`; reject every `skills.public` string.
  No reported consumer or reproduction supports that broader contract.
- Valid but Defer: consolidate the copied handoff goal template or build a
  general package-loader abstraction. The current shared value API and explicit
  two-layout resolver are sufficient for the confirmed incidents; revisit after
  an independent drift signal.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/scripts/draft_goal_from_chunk.py:168-181 | action: fix | note: validate the canonical values that are actually rendered before mkdir/write
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/validate_adapters.py:21-100 | action: fix | note: load and discover resolvers in the source or flattened export layout
- F3 | bin: bundle-anyway | evidence: strong | ref: scripts/check_export_safe_imports.py:183-215 | action: fix | note: detect only the exact literal import_repo_module helper call and pin controls
- F4 | bin: over-worry | evidence: weak | ref: n/a | action: defer | note: broad dynamic-import dataflow and package-loader redesign are unsupported scope
- F5 | bin: valid-but-defer | evidence: moderate | ref: skills/public/handoff/scripts/chunked_routing_auto_draft.py:57-60 | action: defer | note: template consolidation is real duplication but not this incident's owner

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority; fork context disabled.
- Host exposure state: requested_fields_sent
- Application state: n/a — the host returned completed findings but exposed no provider-application confirmation.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — three distinct angle reviewers and one separate counterweight
completed; boundary fingerprints before/after the review were clean.

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/2026-08-04-slice-d-final-packet.json`
- Packet path: `charness-artifacts/critique/2026-08-04-slice-d-final-packet.json`
- Packet SHA256: `00b0eb24dfa1a07b07c996baa3b4efe7f8b1039be6356509ee3382b64533dc32`
- Packet Markdown SHA256: `33443f3c60611d7d4bb4e08dae0ca37c193dcb85f86255001d764150725538d9`
- Identity SHA256: `9dec3758126056e616ea68a6834827a2d89eae22ef2181862ed8bdf997fcc853`

## Boundary Ownership

- Producer: `goal_artifact_lib.py` produces the canonical goal-value verdict;
  `draft_goal_from_chunk.py` and `upsert_goal.py` supply values; packaging
  produces source or flattened resolver paths.
- Consumer: the goal artifact reader/checker and the installed/exported
  `scripts/validate_adapters.py` entrypoint.
- Owning surface: shared goal artifact library plus the export-aware adapter
  validator entrypoint.
- Verdict: moved-to-owner — caller-specific transport/status policy remains in
  each producer, while the shared invariant and export layout decision live at
  the boundary that both consumers use.

## Pre-Merge Action

The implementation and focused tests satisfy the three act-before-ship actions.
Run the broad quality/proof gates after source-to-plugin synchronization; do not
claim export safety from mirror equality alone.

## Defect Class Cross-Link

The recurring lesson is recorded in
`charness-artifacts/retro/recent-lessons.md`: absent or local guards do not
constrain sibling producers or flattened consumers. This critique moves the
guard to the shared value owner and proves the final exported consumer.

## Repair-Read Round

- Final bounded fresh-eye review read the repaired producer, export gate, and
  flattened-validator proof after implementation. It found no blocker or medium
  finding.
- An earlier exploratory read identified two concrete proof repairs before the
  final review: clear `CHARNESS_REPO_ROOT` from the exported subprocess
  environment, and recognize the supported literal helper-call variants
  (`script_file=__file__`, `module_name=...`, and `Path(__file__)`) while keeping
  variables, aliases, f-strings, concatenation, and qualified calls outside the
  matcher. Focused tests and the final reviewer re-read cover those repairs.
- Final review delivery: findings-received; requested model/reasoning/service
  fields were sent; provider application was not exposed by the host.
- Final boundary fingerprint: `slice-d-repair-read-final` verified clean with
  no worktree or index drift.
