# Critique: T2 rewrite operator and sentinel scoring

Date: 2026-07-09
Scope: T2 of `charness-artifacts/goals/2026-07-09-prompt-mutation-step7-slim.md`
Fresh-eye satisfaction: parent-delegated

## Review Packet

- Intent: add a replace-unit prompt mutant operator and an all-arm sentinel witness mechanism so the T3 handoff step-7 slim experiment can be scored without hand-edited manifests.
- Changed surfaces: `scripts/generate_prompt_mutants.py`, `scripts/prompt_mutant_lib.py`, `scripts/prompt_mutant_rewrite_lib.py`, `scripts/score_prompt_mutation_survival.py`, `scripts/score_prompt_mutation_survival_lib.py`, `scripts/score_prompt_mutation_sentinel_lib.py`, focused tests, and synced `plugins/charness/scripts/*` exports.
- Invariants: generated capture refs stay raw parentless snapshot SHAs; no `refs/prompt-mutants/*` refs are created; removal remains supported; rewrite records `operator_kind` and applied replacement hash; sentinels are deterministic all-arm canaries, distinct from causal witness-map entries.
- Non-claims: no T3 captures yet; no policy-doc rewrite-class update yet; no broad pytest lock yet; no live #426 close verification until operator push.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.4-mini, reasoning_effort=medium for lower-power reviewers where host allowed it; one replacement reviewer used inherited parent settings after model capacity rejection.
- Host exposure state: requested_fields_sent
- Application state: host returned reviewer agent ids and completion payloads for the replacement reviewer and two original reviewers; one requested lower-power reviewer errored with model capacity and was replaced.

## Fresh-Eye Findings

Reviewer coverage was parent-delegated and read-only. One lower-power reviewer spawn hit model capacity and was replaced with an inherited-model reviewer.

- Blocker: sentinel scoring raised a hard `SurvivalScorerError` when a configured sentinel hit a missing `observed.v1.json`, even though baseline invalidity is supposed to return an inspectable `EXPERIMENT-INVALID` report. Fixed by making sentinel evaluation convert bundle read failures into in-band sentinel failures, with a regression test.
- Blocker: sentinels were not reachable from the normal manifest producer; the scorer accepted `manifest["sentinels"]`, but `generate_prompt_mutants.py` emitted no such field. Fixed with repeatable `generate --sentinel` support for `CHANNEL=VALUE` and JSON-object forms, plus CLI manifest tests and a real handoff manifest probe.
- Correctness risk: sentinel `all_fired` was vacuously true for a configured zero-run arm. Fixed by reporting zero-run sentinel failures and testing the invalid-for-verdict mutant-arm case.
- Correctness risk: trace-marker sentinels dropped the existing no-`stream.jsonl` truncation caveat. Fixed by carrying sentinel caveats into JSON/markdown.
- Correctness risk: rewrite replacement text without a trailing newline could glue onto the following markdown heading. Fixed by applying a boundary newline when needed and hashing the applied replacement bytes.
- Correctness risk: public sibling mutation used first-substring replacement and could mutate the wrong duplicated section. Fixed by mutating only a uniquely matching parsed public unit; ambiguous public duplicates stay untouched.
- Compatibility risk: sentinel failure originally left CLI exit status green. Fixed by returning nonzero when `sentinels.all_fired` is false.

## Counterweight

- The policy doc being stale for rewrite/sentinel semantics is real but not a T2 Act Before Ship blocker: T4 already requires updating `docs/prompt-mutation-policy.md` when a rewrite is conditionally applied. Pulling that into T2 would document an operator class before the experiment has produced an applied/not-applied outcome.
- Manifest record expansion with `operator_kind` and `replacement_content_sha256` is acceptable for this local advisory tool surface: existing scorer code ignores unknown keys, and the focused tests preserve removal shape while asserting no legacy `mutant_ref`.
- Plugin mirror drift was checked through `sync_root_plugin_manifests.py`, `validate_packaging_committed.py`, and the slice closeout helper.

## Boundary Ownership

- Producer: `generate_prompt_mutants.py` owns mutation manifest facts: snapshot SHAs, operator kind, applied replacement hash, and sentinel definitions.
- Consumer: `score_prompt_mutation_survival.py` / `score_prompt_mutation_survival_lib.py` consume the manifest to render deterministic verdict and sentinel reports.
- Owning surface: prompt-mutation tooling producer/consumer boundary.
- Verdict: owned-correctly

## Closeout Verdict

No remaining Act Before Ship finding for T2. Remaining advisory: `scripts/prompt_mutant_lib.py` is in the length warning band at 465/480 code lines after the cohesive rewrite-helper split; avoid adding more behavior there before another split.
