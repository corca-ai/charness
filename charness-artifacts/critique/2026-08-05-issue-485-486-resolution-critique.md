# Issue 485 and 486 resolution critique
Date: 2026-08-05

## Decision Under Review

Whether [#485](https://github.com/corca-ai/charness/issues/485) (a declared-absent
field still resolves to a preset default naming phantom paths) and
[#486](https://github.com/corca-ai/charness/issues/486) (the customization warning
silences itself once an adapter has no comments left) are genuinely resolved.

Both directions were chosen by the operator: for #485, *path-bearing fields only
consult the declaration* — do not change what fields mean at resolution time; for
#486, *split the two claims*.

## Failure Angles

- The #485 audit was scoped to `coverage_floor_policy` and generalized to five
  fields; a consumer premising on a path from any of the other four would make the
  chosen direction under-scoped.
- The hand-maintained path map could disagree with its own stated ruler, so the
  warning could enumerate part of a set while reading as exhaustive — the class this
  field exists to close, re-created inside the fix for it.
- The split refill claim could either still be silenced, or never converge into noise.
- Two existing tests were CHANGED; one could have been weakened to fit the code.
- The generated `plugins/` mirror could lag the repo copy, shipping the defect.

## Counterweight Pass

**Round 1 refused #485 and was right.** The audit had been widened only in prose:
`scripts/check_mutation_score.py:145` and `check_js_mutation_score.py:44` build
`repo_root / summary_rel` from `mutation_testing.report_paths.summary_md`, a live
filesystem premise on a field the map covered at a key it omitted. So the warning
named one phantom path of four while reading as complete. Confirmed by reproduction,
then repaired.

**Round 2 refused the repairs, and found the sharper defect.** The guard built to
stop "a partial enumeration presented as complete" was itself a partial rule
presented as complete: the ruler was stated three times and the code statement was a
closed 10-extension allowlist while both prose statements said "a file extension".
A `coverage.xml` default would have derived nothing, passed the completeness test,
and shipped a short enumeration. Repaired by moving the rule rather than widening it
— `names_a_filesystem_location` and `path_bearing_entries` now live once and the test
imports them, which also dissolved the list-of-dicts blindness and the unrepresentable
shapes instead of patching them.

**Round 2 also caught a barrier I skipped rather than a subtlety.** The `plugins/`
mirror was never synced after the round-1 repairs, so the copy an installed machine
runs still carried the original defect while the completeness test was green — it
imports the repo module and nothing reads the mirror.

**Not over-worry, worth naming:** round 1 verified the audit independently rather
than accepting it, checked all five fields, and correctly REJECTED two apparent
counterexamples (`check_dup_ratchet.py`, `changed_line_coverage_gate_lib.py`) whose
path use sits behind inertness defaults, and one more
(`coverage_floor_inventory.py`) that hard-codes its own policy and never reads the
adapter. That precision is why F1 is trustworthy.

**Genuine over-worry, not folded:** the `written` line-prefix parser in
`describe_intent_loss`, and the docstring of `test_a_converged_adapter_still_says_nothing`
claiming more than the test proves — the mechanism is real, the docstring overreaches.

**Real but filed rather than blocking:** sub-key refills. A partially-deleted block is
still refilled and reported `preserved`. Filed as
[#489](https://github.com/corca-ai/charness/issues/489).

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/check_mutation_score.py:145 | action: fix | note: a live consumer builds a filesystem path from `mutation_testing.report_paths.summary_md`, falsifying the zero-consumers audit once widened past `coverage_floor_policy`
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/quality_adapter_lib.py:339 | action: fix | note: the map omitted the three `report_paths` keys while the warning presented its list as exhaustive — one of four
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/quality_adapter_lib.py:369 | action: fix | note: `unasserted_paths` read only top-level keys, so adding a nested key would have been silently inert
- F4 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_quality_bootstrap_absence.py:496 | action: fix | note: the map's only guard checked that named keys exist, never that every path-bearing key is named, so F2's class had no biting test
- B1 | bin: act-before-ship | evidence: strong | ref: plugins/charness/scripts/quality_adapter_lib.py | action: fix | note: the generated mirror was never synced after the round-1 repairs, so the shipped copy carried the original defect while the completeness test stayed green
- B2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_quality_bootstrap_absence.py:500 | action: fix | note: the ruler was a closed 10-extension allowlist while its two prose statements said "a file extension" — the guard against partial-presented-as-complete was itself partial
- B3 | bin: act-before-ship | evidence: strong | ref: scripts/quality_adapter_lib.py:397 | action: fix | note: a list of mappings was invisible to both the derivation and the marking, silently in both directions
- B4 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_quality_bootstrap_absence.py:529 | action: fix | note: `_PATH_BEARING_EXCLUSIONS` was unenforced, so one bogus entry silenced the completeness guard for a whole field
- B5 | bin: bundle-anyway | evidence: strong | ref: scripts/quality_adapter_lib.py:377 | action: fix | note: top-level scalar and nested-list shapes had no representation, and their only green path was B4's hatch
- B6 | bin: bundle-anyway | evidence: moderate | ref: scripts/quality_adapter_lib.py:448 | action: fix | note: `unasserted_paths` did not filter structural fields while the warning did, so the data key could be populated with no prose naming it
- B7 | bin: bundle-anyway | evidence: moderate | ref: skills/public/quality/references/bootstrap-posture.md:77 | action: document | note: the reference documented one key shape while the code emits `<field>.<key>` and `<field>[<index>]`, and did not state the ruler at all
- F5 | bin: bundle-anyway | evidence: strong | ref: skills/public/quality/references/catalog.yaml:47 | action: document | note: `is_deliberately_absent` has zero production callers and its rule sits behind an on-demand trigger, so the consumer contract ships stated but unenforced — the close must say so
- F6 | bin: bundle-anyway | evidence: strong | ref: scripts/quality_bootstrap_lib.py:157 | action: file-issue | note: a partially-deleted block is refilled and reported `preserved`, which is the reported class one sub-key down | follow-up: https://github.com/corca-ai/charness/issues/489
- F7 | bin: valid-but-defer | evidence: moderate | ref: skills/public/quality/scripts/propose_mutation_testing.py:161 | action: document | note: `--execute` writes a workflow at a path the resolver simultaneously reports as unasserted, because `classify()` reads a declared-absent block as missing
- F8 | bin: valid-but-defer | evidence: moderate | ref: skills/public/quality/scripts/plan_quality_run.py | action: defer | note: the planner carries no adapter warnings, so the signal survives only as raw resolve JSON rather than planner-carried state
- F9 | bin: over-worry | evidence: contested | ref: tests/quality_gates/test_quality_bootstrap_absence.py:579 | action: document | note: the converged-adapter test proves the outer status gate, not the explicit-field convergence its docstring also claims — docstring drift, not a behaviour gap
- F10 | bin: over-worry | evidence: strong | ref: skills/public/quality/references/coverage_floor_inventory.py:29 | action: document | note: considered and rejected as a blocker — it hard-codes its own policy and never reads the adapter, so a declaration genuinely does nothing to it and the close should say so

## Reviewer Tier Evidence

- Requested tier: n/a — Claude Code host. Per `AGENTS.md` `## Subagent Delegation`
  the per-host split says to use the host's own controls here (typed
  `bounded-reviewer`, session-model inheritance) and NOT to request the Codex
  model/effort pair.
- Requested spawn fields: `subagent_type: bounded-reviewer` (read-only
  Read/Grep/Glob), no host addressing or team `name`, `run_in_background: false`.
- Host exposure state: applied
- Application state: host-confirmed: both rounds returned full findings reports
  inline, each refusing the close it was asked to bless, and each independently
  reported the tools it did NOT have rather than asserting evidence it could not
  fetch — round 1 named four unfetchable items, round 2 named two.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — satisfied before the close call. Two bounded read-only rounds ran
against this resolution, and each REFUSED what it was handed: round 1 refused #485's
close over an under-scoped audit, round 2 refused the round-1 repairs over a guard
that carried the class it guarded.

**Boundary-fence honesty:** `reviewer_boundary_fingerprint.py verify` returned
`clean` around round 1. Around round 2 it returned `boundary-drift`, and the drift is
the parent's own — repairs were edited and committed inside that window, so the fence
cannot certify it and is not claimed to. The read-only property for round 2 rests on
the typed `bounded-reviewer` envelope, which the reviewer itself reported as bound
(Read/Grep/Glob only, no Bash), not on the fingerprint. Recorded rather than rounded
up to `clean`.

## Reviewed Input Identity

<!-- No prepared packet was consumed: each round received an inline bounded packet
     (intent, changed files, invariants, proof, non-claims, reviewer questions). -->

## Boundary Ownership

- Producer: `scripts/quality_adapter_lib.py` resolution, which decides what a resolved
  adapter asserts about the filesystem.
- Consumer: quality gates that build paths from resolved values
  (`check_mutation_score.py`, `check_js_mutation_score.py`,
  `propose_mutation_testing.py`), and any agent reading `resolve_adapter.py` output.
- Owning surface: the resolver, since it is the single place the declaration and the
  default meet.
- Verdict: owned-correctly
- Basis: the producer/consumer brief put the marking in the resolver rather than in
  each consumer, because the alternative — every path-premising gate learning the
  declaration independently — is the rule-duplication that produced B2 and the round-1
  D-findings. Consumers get one call (`is_deliberately_absent`) instead of a rule to
  re-derive. The residual is that no consumer calls it yet, which the close states
  rather than hides.
