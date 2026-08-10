# deletable surfaces sweep
Date: 2026-08-11

## Decision Under Review

After six proposed deletions were refuted six times, the operator asked whether there is
genuinely nothing deletable in this repo — looking both at the items already selected and
at surfaces never considered. The pending change is
`charness-artifacts/spec/2026-08-10-umbrella-class-disposition-plan.md`
(`# Deletable-surfaces sweep — 2026-08-11`), which records what survives for execution in
a later session. Nothing has been executed.

## Failure Angles

- **Zero-consumer hunt.** Every candidate had to carry the grep proving its consumer set,
  because the missing reader-search is what produced all six wrong deletions. Returned
  three proven candidates and, more usefully, a refuted list — including
  `evals/cautilus/contract-effectiveness.fixture.json`, which looks orphaned and is
  consumed by a directory glob at `scripts/cautilus_scenarios_lib.py:46`, the same shape as
  the `listed_skill_ids` trap from the previous slice.
- **Duplicate-surface hunt.** Held to the north star's `## Taste` precondition: prove the
  capability is EQUAL, do not assume it. Returned one moderate candidate and refuted the
  two most obvious pairs, in both cases by finding the readers.
- **Teeth without a cliff.** Found the repo's own
  `charness-artifacts/audit/2026-07-04-gate-reclassification.md`, which already classified
  every wired gate — and found that two of its `review-needed` rows have sat unaddressed
  for five weeks. Also volunteered the denominator: a list of gates whose teeth are earned.
- **Re-examine the refutations.** The sharpest angle. Six-for-six is suspicious in the
  other direction too — a reviewer rewarded for refuting will refute — so this angle
  attacked the refutations themselves. It found two overreaches and one refutation that is
  simply wrong.

## Counterweight Pass

**Not run this round.** Four angles ran; no separate skeptical triage pass was spawned, so
the classification in the plan is the parent's own and has not been triangulated. This is
recorded rather than smoothed: the four-bin triage the critique contract expects is
therefore absent, and the next session should treat the candidate list as un-triaged.

What the parent DID do instead, in the channels the read-only reviewers lacked: verified
the pickup spec `engage-always`/`classTag` sets directly, read
`scripts/claim_fidelity_lib.py:151` to confirm the substance judge resolves per directory,
confirmed `recursive_variant` has no `refused_citation_count` key, and ran
`git show v4.0.0` to settle the `check_title_slug_drift` shim question. Three of those
four moved a verdict.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/test_inventory_marker_rule_measurement.py:190 | action: fix | note: the refused_citation_count branch is DEAD (no such key in recursive_variant), so a documented count-only comparison never runs and a full-list deep-equality runs instead — the opposite of what the shallow test does to the same field
- F2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/spec/2026-08-10-umbrella-class-disposition-plan.md:1 | action: document | note: my refutation of pickup.spec.json was itself wrong — the substance judge resolves per directory (claim_fidelity_lib.py:151) and pickup-ambiguous is also a pickup-intent scenario, so the surface is not load-bearing for the gate
- F3 | bin: bundle-anyway | evidence: strong | ref: scripts/boundary_bypass_ratchet_lib.py:17 | action: fix | note: candidate_key_count cannot fire without new_keys firing first, so it is a strictly subsumed verdict input
- F4 | bin: bundle-anyway | evidence: strong | ref: tests/test_inventory_marker_rule_measurement.py:189 | action: fix | note: the recursive pin deep-compares rows/pre_contract_citations_skipped/corpus/recursive, none of which D47 publishes, so narrowing it does not touch the open operator decision and does not wait on the pin ruling
- F5 | bin: bundle-anyway | evidence: moderate | ref: skills/public/quality/scripts/run_dead_code_advisory.py:100 | action: fix | note: _dataclass_field_locations is a pass-through whose only consumer is its own test; production reaches the same data via source_role_locations
- F6 | bin: valid-but-defer | evidence: strong | ref: skills/public/quality/scripts/inventory_ubiquitous_language.py:431 | action: file-issue | note: blocks unconditionally on a word-preference finding while every sibling inventory gate is advisory or opt-in, and the repo's own 2026-07-04 audit flagged it review-needed five weeks ago | follow-up: deferred charness-artifacts/spec/2026-08-10-umbrella-class-disposition-plan.md
- F7 | bin: valid-but-defer | evidence: moderate | ref: scripts/check_references_link_inventory.py:143 | action: file-issue | note: enforces bullet SHAPE inside a section nothing consumes, can block a push alone from the docs-only subset, and has a recorded firing on a wrapped bullet | follow-up: deferred charness-artifacts/spec/2026-08-10-umbrella-class-disposition-plan.md
- F8 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_adapter_key_warn_tier.py:292 | action: document | note: two more exact-count pins of the #561 shape; the invariant wanted is per-family non-emptiness, since a prior threshold was refuted for surviving a whole-glob deletion
- F9 | bin: over-worry | evidence: contested | ref: skills/shared/scripts/check_title_slug_drift.py:13 | action: defer | note: two angles independently proposed the retirement shim, and git show v4.0.0 settled it — the shim ships in a released install, so the compat argument transfers
- F10 | bin: over-worry | evidence: weak | ref: scripts/check_python_filenames.py:44 | action: defer | note: the reviewer proposed and then declined it itself, because ruff's N rules are not enabled here so "the linter already does it" is false and the capability is not equal

## Reviewer Tier Evidence

- Requested tier: high-leverage per `.agents/critique-adapter.yaml`, with the adapter's `model` field deliberately not forwarded — it names a model id this host does not expose.
- Requested spawn fields: subagent type `bounded-reviewer` (Read/Grep/Glob only), one angle per spawn, unnamed one-shot spawns, session model inherited.
- Host exposure state: host-defaulted
- Application state: the host exposed `subagent_type` and accepted it; no `service_tier`, `reasoning_effort`, or `fork_turns` control was exposed, so those adapter fields were not applied.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated` — four distinct bounded subagent contexts. Reviewer boundary
fingerprint snapshot/verify around the window returned `clean` with zero drift. No
counterweight pass ran; see `## Counterweight Pass`.

## Reviewed Input Identity

<!-- No packet was consumed. This sweep reviewed the repo tree itself rather than a
prepared change surface, so there is no reviewed-input binding to declare and the binding
floor is intentionally not claimed. The previous critique in this sequence
(2026-08-11-umbrella-class-disposition-plan.md) records why a stale binding is not
re-declared to make a floor pass. -->

## Boundary Ownership

- Producer: the four bounded reviewers, each producing candidate deletions with a proven consumer set.
- Consumer: the next session's execution slice, and the gate-reclassification decision for the teeth-without-a-cliff findings.
- Owning surface: `charness-artifacts/spec/2026-08-10-umbrella-class-disposition-plan.md` for the candidates; `charness-artifacts/audit/2026-07-04-gate-reclassification.md` already owns the gate-teeth question and its rows should be updated rather than duplicated.
- Verdict: owned-correctly
