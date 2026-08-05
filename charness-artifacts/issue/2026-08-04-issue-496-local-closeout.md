# Issue #496 — local closeout carrier

Date: 2026-08-04
Status: locally closed; remote issue remains open and out of scope
Issue: https://github.com/corca-ai/charness/issues/496

## Current-state supersession (2026-08-05)

This historical local carrier predates the #507 quality-bootstrap lifecycle
refactor. Its producer/consumer and proof-matrix language below describes the
then-current leaf-warning path, not the current ordinary-bootstrap behavior.
Today `skills/public/quality/scripts/bootstrap_adapter.py` is the
operator-facing entry surface, while `quality_bootstrap_lifecycle.py` owns the
semantic-difference, byte-preserving `conflict` advisory, and explicit
`--migrate` write authorization mechanics. The current #496 closeout uses that
top-level conflict contract as its behavioral proof; it does not claim a
leaf-warning or automatic-rewrite path.

## Closeout scope

This is a local proof carrier for the independent #496 hollow-refill track. It
does not close or modify the remote GitHub issue, and it makes no claim about
remote CI, release, host-specific rendering, or future quality-policy
consumers. It makes no predicate recommendation for, or other claim about,
#503's separate closeout-cost decision. Conversely, #503's local decision
supplies no predicate recommendation to #496; that track remains independently
bounded and locally closed under its own carrier.

## Historical producer, consumer, and owner (pre-#507)

- Producer: `_mark_subkey_refills` in `scripts/quality_bootstrap_lib.py` carries
  the generic nested refill names into the quality bootstrap report. The
  mutation policy boundary owns the exact exception for omitted
  `mutation_testing.commands.dry_run` and `.sample` leaves whose defaults are
  empty strings.
- Consumer: `describe_intent_loss` in `scripts/quality_bootstrap_absence.py`
  renders the JSON/stderr customization warning that a quality maintainer or
  operator reads alongside the rewritten adapter.
- Owner: Charness quality/bootstrap maintainer. The generic recursive helper
  remains reusable and is not assigned the semantic policy exception.

## Historical semantic invariant and axis-varying counterexample (pre-#507)

The report may suppress only the two named omitted mutation command leaves that
are known no-op defaults; it must continue reporting omitted command defaults
outside that allowlist, preserve supplied real commands, and never recommend
discarding a partially configured block to silence a nested finding.

The axis-varying counterexample is a partial `prompt_asset_policy` whose
`exemption_globs` default is `[]`: the shape is empty like the command defaults,
but it defines the scan boundary and must remain reportable. This rules out a
generic empty-value predicate.

## Historical reproduction and repair (pre-#507)

The gathered issue fixture was:

    mutation_testing:
      commands:
        full: pytest --mutate
        summary: python3 scripts/summarize.py

Before repair, the producer reported `commands.dry_run` and
`commands.sample`, and the final warning recommended dropping the whole
`mutation_testing` block. After repair, the exact fixture reports neither
inert leaf, retains `full` and `summary` in the rewritten adapter, and gives
leaf-level review guidance that explicitly preserves configured siblings.

## Historical proof matrix (pre-#507)

- Positive: exact full+summary fixture suppresses only the two omitted inert
  leaves; source and shipped plugin entrypoints produce the same complete JSON
  payload and stderr.
- Negative: a fixture omitting `summary` still reports `commands.summary`;
  `full` is outside the suppression allowlist. Explicit empty `dry_run` and
  `sample` are not reclassified as refills.
- Sibling preservation: partial `report_paths` still reports inherited leaves
  and its warning does not advise whole-block deletion.
- Axis control: partial `prompt_asset_policy` keeps empty `exemption_globs`
  reportable.
- Fresh path: an initially absent adapter produces no customization warning and
  empty stderr.
- Focused standing proof: the quality bootstrap, absence, and policy-merge
  targets passed 85 tests in 1.87 seconds.
- Review proof: the pre-implementation critique and required second repaired-
  surface review both ran through delegated fresh-eye windows. Round 2 found a
  selected-key source/plugin parity gap; after clean boundary verification the
  complete-payload assertion was added and the focused suite reran green. This
  round-2 repair is recorded accepted-unreviewed under the repository's
  two-round cap; no third review is claimed.

## Historical exact changed paths (pre-#507)

- `scripts/quality_bootstrap_lib.py`
- `scripts/quality_bootstrap_absence.py`
- `plugins/charness/scripts/quality_bootstrap_lib.py`
- `plugins/charness/scripts/quality_bootstrap_absence.py`
- `tests/quality_gates/test_quality_bootstrap.py`
- `tests/quality_gates/test_quality_bootstrap_absence.py`
- `charness-artifacts/gather/2026-08-04-issue-496-hollow-refill.md`
- `charness-artifacts/debug/2026-08-04-debug-review-followup-2.md`
- `charness-artifacts/critique/2026-08-04-slice-e-496-hollow-refill-semantic-repair-critique.md`
- `charness-artifacts/critique/2026-08-04-slice-e-496-hollow-refill-packet.json`
- `charness-artifacts/critique/2026-08-04-slice-e-496-hollow-refill-packet.md`
- `charness-artifacts/goals/2026-08-04-make-recurring-closeout-cost-actionable.md`
- `charness-artifacts/issue/2026-08-04-issue-496-local-closeout.md`

## Historical residuals and reopen trigger (pre-#507)

- The generic helper still reports empty values elsewhere; no universal
  semantic-inertness taxonomy is claimed.
- The command allowlist is evidence-backed for the current quality policy and
  should be revisited if a future consumer gives `dry_run` or `sample` a
  non-empty default or different semantics.
- Sub-key deliberate absence remains unsupported; the warning intentionally
  recommends leaf review rather than inventing a new absence contract.
- Reopen #496 if a real adapter or future consumer demonstrates that either
  named command slot carries operator intent, if a warning still recommends
  destructive whole-block removal, or if source/plugin payload parity diverges.

## Historical fresh-observer acceptance (pre-#507)

Accepted by delegated fresh-eye reviewer Helmholtz
(`019fca72-094b-7721-8d21-6fd732d557e9`) after the carrier wording repair. The
reviewer confirmed the carrier explicitly states that #503 supplies no
predicate recommendation to #496, remains independently bounded/closed, and
that remote closure, CI/release, and future consumers are non-claims. The
reviewer found no remaining blocker. Boundary verification for the final
reread window is recorded by
`.charness/reviewer-boundary/issue-496-local-closeout-final-before.json` with
`verdict: clean` and `drift: []`.

Remote issue closure is not claimed or requested by this carrier.
