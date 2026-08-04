# Resolution Critique — Issues #497, #500, and #501
Date: 2026-08-04

## Decision Under Review

Close the three bug issues after the Slice D repairs: shared goal-value
validation for both goal producers (#500), supported literal helper-call
detection in the export-safe-import proof surface (#501), and source/flattened
layout-aware adapter loading and discovery in the exported validator (#497).

Success means each reporter JTBD has a current root cause, a checked-in
prevention move, a distinct behavior channel, and a carrier that remains honest
about the supported boundary. Arbitrary dynamic imports, arbitrary future
packaging layouts, and direct-library API hardening are out of scope.

## Causal Context Consumed

The bounded causal review classified all three as bugs. It distinguished the
causes rather than collapsing them into one slogan: #500 was producer-parity
ownership, #501 was static-analysis scope, and #497 was an exported-layout
assumption. It found the implementation evidence adequate after the debug
record was reconciled. The current debug record is
`charness-artifacts/debug/2026-08-04-debug-review-followup.md`.

## Angles

- **Michael Jackson — problem framing:** each JTBD is met by a concrete
  consumer-facing proof: hostile no-artifact refusal for #500, supported
  literal-call refusal plus negative controls for #501, and an isolated
  generated-export subprocess for #497.
- **Gerald Weinberg — diagnostic and ownership:** the repairs are at the causal
  boundaries. `goal_artifact_lib.py` owns shared value facts, the import gate
  owns its supported literal-call predicate, and `validate_adapters.py` owns
  source/flattened runtime resolution. The three causes remain distinct.
- **Atul Gawande — operational proof:** source and generated mirrors are synced;
  handoff refusal occurs before `mkdir`/`write_text`; the exported validator is
  run with `CHARNESS_REPO_ROOT` removed; and dynamic forms remain explicit
  non-claims rather than silent false greens.

## Counterweight Pass

- **Act Before Ship — strong:** bind the carrier to this checked-in critique,
  use the exact JSON packet hash below, and name all three distinct behavior
  channels before any close call.
- **Bundle Anyway — strong:** retain concrete test paths and the per-issue
  `Boundary` lines in the carrier instead of saying only “focused tests passed.”
- **Over-Worry — strong:** do not infer arbitrary dynamic-import dataflow,
  redesign the package loader, or add a second generic gate without a recorded
  consumer. The negative controls pin the deliberate static boundary.
- **Valid but Defer — moderate:** hardening a direct call to
  `goal_artifact_lib.upsert_goal` would be future-proofing, but there is no
  alternate production caller and it is not required by #500's recorded JTBD.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/references/closeout-discipline.md:206 | action: document | note: bind the three-issue carrier to this checked-in resolution critique and exact packet identity
- F2 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_profile_and_preset_validation.py:515 | action: document | note: name separate behavior channels for #500, #501, and #497
- F3 | bin: over-worry | evidence: strong | ref: tests/quality_gates/test_export_safe_asset_paths.py:392 | action: defer | note: arbitrary dynamic-import inference and package-loader redesign are unsupported scope
- F4 | bin: valid-but-defer | evidence: moderate | ref: skills/public/achieve/scripts/goal_artifact_lib.py:269 | action: defer | note: direct-library API hardening has no current alternate production caller

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority, fork_context=false.
- Host exposure state: requested_fields_sent
- Application state: unverified — the host returned findings but exposed no provider-application confirmation.
- Delivery state: findings-received.

## Fresh-Eye Satisfaction

parent-delegated — three named angle reviewers and one separate counterweight
returned findings; the boundary fingerprint for `slice-e-resolution-critique`
verified clean before this artifact was written.

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/2026-08-04-issue-497-500-501-resolution-packet.json`
- Packet path: `charness-artifacts/critique/2026-08-04-issue-497-500-501-resolution-packet.json`
- Packet SHA256: `7befe176cd54ec23fba7f8b397b8a1166fd01358a479e6b45283a05c62cc6f8c`
- Packet Markdown SHA256: `c2d9de94983f1e6a7c1e01507274903a1633c61a4aaa4e0dfa7c88b5b4dc730f`
- Identity SHA256: `650e78712ee861c4efd1ffe9fab82a7076cabda4666e61d8aacbb1135a221e74`

## Boundary Ownership

- Producer: `goal_artifact_lib.py` produces canonical goal-value verdicts;
  `check_export_safe_imports.py` produces the supported static export verdict;
  `validate_adapters.py` produces the source/flattened resolver validation.
- Consumer: goal artifact readers, the export-safe-import gate's caller, and the
  installed/exported `scripts/validate_adapters.py` entrypoint.
- Owning surface: shared goal-value library plus the export-aware import gate
  and layout-aware adapter validator.
- Verdict: moved-to-owner.

## Per-Issue Verdicts

### #500 — producer parity

JTBD: both goal-artifact creators must apply the same value guards and refuse
unsafe rendered values before writing an artifact.

Root cause: value predicates were private to `upsert_goal.py`, so the handoff
producer bypassed them. Prevention is the shared library contract applied to the
exact rendered title/body and supplied slug before filesystem mutation.

Behavior verdict: confirmed locally through the hostile handoff producer tests,
including no-artifact refusal, canonical newline handling, explicit supplied
slug refusal, and auto-draft fallback; the achieve input-channel tests cover
the sibling producer. Evidence: `tests/test_handoff_chunker_auto_draft.py:569`
and `tests/quality_gates/test_upsert_goal_input_channel.py:85`.

Sibling decision: achieve and handoff are same-class producers — fix now at the
shared value owner; proof level is local payload/behavior tests, not a provider
roundtrip.

### #501 — helper-path export detection

JTBD: the export-safe-import proof surface must catch the recorded module path
when it is passed as a supported literal argument to `import_repo_module`.

Root cause: the gate modeled import-statement AST nodes, not the helper's literal
module-path contract. Prevention is the narrow unqualified literal-call
predicate, with positional/keyword and `Path(__file__)` coverage.

Behavior verdict: confirmed locally through direct gate execution and controls
for variables, aliases, f-strings, concatenation, qualified calls, near misses,
and unrelated strings. Evidence: `tests/quality_gates/test_export_safe_asset_paths.py:361`.

Sibling decision: dynamic-loader and arbitrary dataflow forms are diagnostic
non-claims for this slice; proof level is static gate behavior plus in-process
tests.

### #497 — exported adapter validator

JTBD: an installed/exported plugin must import `validate_adapters.py` and
validate the resolvers that exist in its flattened layout instead of failing on
an authoring-only `skills.public` path or silently scanning an empty scope.

Root cause: runtime loading and glob discovery assumed the source-tree layout.
Prevention is layout-aware source/flattened resolver selection and generated
export execution.

Behavior verdict: confirmed locally through a freshly generated exported-plugin
subprocess with `CHARNESS_REPO_ROOT` removed; source validation reports 16
resolvers/18 YAML files and exported validation reports 16 resolvers. Evidence:
`tests/quality_gates/test_profile_and_preset_validation.py:515`.

Sibling decision: source and flattened resolver layouts are real interface-shape
siblings — fix now with the exported consumer proof; proof level is isolated
subprocess plus source/export validator output.

## Deliberately Not Doing

No claim is made for arbitrary dynamic import construction, aliases, f-strings,
concatenation, qualified loader calls, every possible host packaging layout, or
a direct-library API hardening pass. These are either explicitly negative-tested
non-claims or valid-but-defer concerns with no current recorded consumer.

## Next Move

Use this artifact and the exact packet identity in the multi-issue carrier;
validate the carrier draft before any tracker mutation, then obtain final GitHub
state through a separate issue-tool readback. The carrier must render
`Behavior #500`, `Behavior #501`, and `Behavior #497` from the channels above.
