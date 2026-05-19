# Issue 175 Advisory Recurrence Debug
Date: 2026-05-19

## Problem

Issue #175 looked like a recurrence of earlier script-silence and empty-policy
fixes: a green or exit-zero helper state still let required quality attention
disappear from normal closeout.

## Correct Behavior

Given a validator intentionally exits 0 for an opt-in integration that is absent
or disabled, when quality runs it, then the operator-visible output and JSON
payload should still expose a warning with the next action.

Given a quality inventory reports that prose review is still required, when a
quality artifact cites that inventory, then the artifact body should record the
prose-review result separately from copied script fields.

## Observed Facts

- Related prior incident `charness-artifacts/debug/2026-05-11-issue-145-script-silence-closeout.md`
  found that helper silence was being treated as prose-level closeout.
- Related current-pointer incident `charness-artifacts/debug/latest.md`
  documented the 2026-05-17 empty-policy silent-pass pattern: empty enforcement
  policy plus quiet pass-time output hid disabled gates.
- Commit `5bef8bc` fixed pass-time attention replay for `WARNING`, `WARN`,
  `WEAK`, and `ADVISORY` lines and added warnings for empty skill ergonomics
  rule policy.
- Commit `8e3001f` routed usage episodes through setup and quality only when
  `.agents/usage-episodes-adapter.yaml` exists; it explicitly left `no_adapter`
  and `disabled` as skipped states but did not make absent opt-in visible.
- Commit `662fe81` split `scope_status`, `finding_status`, and
  `prose_review_status`, but did not emit an `ADVISORY` line for required prose
  review and did not require an artifact-level `prose review result:`.
- Commit `c324fed` enabled default skill ergonomics gate rules, reducing one
  empty-policy path, but not the advisory inventory closeout path.
- Issue #175 evidence came from a consumer repo: `validate_usage_episodes.py`
  returned `status: no_adapter`, `valid: true`, and no warning payload; the
  skill ergonomics inventory returned `prose_review_status: required` while a
  quality workflow could still summarize the script as complete review.

## Reproduction

Before `0c35cb4`, these paths could pass quietly:

```bash
python3 scripts/validate_usage_episodes.py --repo-root . --json
CHARNESS_QUALITY_LABELS=validate-usage-episodes ./scripts/run-quality.sh
python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --json
python3 scripts/validate_inventory_consumption.py --repo-root .
```

The first command reported `no_adapter` without `warnings`, the quality runner
did not queue `validate-usage-episodes`, the ergonomics inventory did not print
an `ADVISORY` line for `prose_review_status`, and the consumption validator did
not require a separate prose-review result.

## Candidate Causes

- The previous fix was scoped to empty configured rule lists, not every new
  exit-zero skipped state.
- Usage episodes were introduced after the earlier script-silence RCA and
  treated opt-in absence as a benign skip rather than an attention state.
- The quality inventory consumption contract required non-headline field
  engagement, but had no special rule for fields that explicitly say human or
  model judgment remains required.
- The quality runner could only replay attention text that a queued phase
  actually emitted.

## Hypothesis

If skipped opt-in validators emit structured warnings and normal `WARNING`
output, if `run-quality` queues the validator unconditionally, and if cited
skill ergonomics inventories require both `prose_review_status` and an explicit
`prose review result:`, then the #175 recurrence is blocked without turning
opt-in absence into a hard failure.

## Verification

- `gh issue view 175` plus `git show` on `5bef8bc`, `8e3001f`, `662fe81`,
  `c324fed`, and `0c35cb4` confirmed the reported symptoms and fix boundary.
- `rg` over `scripts`, `skills/public`, and `skills/support` for skipped-state
  and attention-output terms found the live #175 siblings plus already-visible
  release, markdown-preview, and control-plane states.
- `./scripts/run-quality.sh` passed after the fix with `61 passed, 0 failed`.

## Root Cause

The recurrence happened because earlier fixes addressed symptoms inside
specific helpers rather than establishing a generalized promotion rule for new
exit-zero attention states. `validate_usage_episodes.py` had no warnings and
was not always queued, while `inventory_skill_ergonomics.py` exposed
`prose_review_status` only as data. Tests proved those local outputs but did
not include sibling fixtures for "new optional validator absent" or "inventory
says prose still required, artifact omits prose review result."

## Detection Gap

- usage episodes validator | `no_adapter` and `disabled` returned exit 0 with
  no warning payload | add `warnings` and normal `WARNING:` output for both
  states.
- quality runner queue | usage episodes validation ran only when an adapter was
  present | queue `validate-usage-episodes` unconditionally; keep missing and
  disabled states non-failing.
- skill ergonomics inventory | `prose_review_status` existed only as JSON data
  | add `advisories` and plain `ADVISORY:` output for `required` and
  `still_required`.
- quality artifact consumer | inventory field engagement could still be
  satisfied without the separate prose judgment | require
  `prose_review_status` plus `prose review result:` outside `## Commands Run`
  when `inventory_skill_ergonomics.py` is cited.
- sibling scan discipline | previous RCA memory did not automatically trigger
  on a newly introduced validator | carry "exit-zero attention state" as a
  reusable scan lens in issue/debug closeout.

## Sibling Search

- Mental model: exit-zero skipped states were treated as harmless unless the
  exact helper had already been patched.
- same state axis: `validate_usage_episodes.py` was the live unpatched
  `no_adapter`/`disabled` validator; fixed by `0c35cb4`.
- same consumer axis: `inventory_skill_ergonomics.py` was the live unpatched
  prose-review-required inventory; fixed by `0c35cb4`.
- same runner axis: `run-quality.sh` already replayed attention output after
  `5bef8bc`, but could not replay an unqueued phase; fixed by unconditional
  queueing.
- adjacent release axis: `check_requested_review_gate.py` reports
  `configuration_status: not_configured` and prints `WARNING`; no code patch
  needed for this incident.
- adjacent axes: release fresh-checkout probes, markdown-preview disabled
  state, and Cautilus disabled state are already visible in artifacts,
  warnings, or planner payloads; no patch needed here.
- out-of-scope runtime axis: `t_events_emit_lib.py` returns local no-op reasons
  for runtime emission, not a standing quality closeout signal; no patch needed
  unless a consumer begins treating it as quality proof.

## Seam Risk

- Interrupt ID: issue-175-advisory-recurrence
- Risk Class: contract-freeze-risk
- Seam: helper exit-zero states versus quality closeout meaning
- Disproving Observation: focused tests now fail if usage episode warnings
  disappear, if the phase is not queued, or if a quality artifact cites skill
  ergonomics inventory without a prose-review result.
- What Local Reasoning Cannot Prove: whether every future opt-in integration
  helper will be written under the same attention-state rule without a template
  or generator enforcing it.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Treat any new exit-zero skipped, disabled, missing-adapter, or not-configured
state as an attention-state design question before closeout. If it is part of a
standing quality or release path, it needs one of: structured warnings plus
pass-time attention output, artifact-visible status, or an explicit waiver.
Inventories that say prose or judgment remains required must force the consuming
artifact to record that judgment separately from script output.

Related prior incidents:

- `charness-artifacts/debug/2026-05-11-issue-145-script-silence-closeout.md`:
  helper silence treated as prose closeout.
- `charness-artifacts/debug/latest.md`: 2026-05-17 empty-policy silent pass.
