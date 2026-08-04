# Gathered source: GitHub issue #496

Source URL: https://github.com/corca-ai/charness/issues/496
Source identity: GitHub issue #496, title and body read through authenticated `gh issue view 496 --repo corca-ai/charness --json ...`.
Access route: direct public fetch attempted first and returned typed `captcha`; authenticated GitHub CLI then returned the structured issue record.
Freshness: issue metadata updated 2026-08-03T13:14:24Z; gathered 2026-08-04.

## Captured facts

- Issue is OPEN: “The #493 recursion reports hollow refills for inert defaults (mutation_testing.commands)”.
- `refilled_policy_subkeys` recurses into partially-written nested policy blocks and names `mutation_testing.commands` leaves `dry_run` and `sample` as refilled even though their defaults are empty strings.
- Reproduction shape:

      mutation_testing:
        commands:
          full: pytest --mutate
          summary: python3 scripts/summarize.py

- Reported leaves are `commands.dry_run` and `commands.sample`, with defaults `''`; the operator supplied real `full` and `summary` commands and nothing was discarded.
- `customization_warning` recommends dropping the whole block and declaring it deliberately absent, which could discard real workflow configuration merely to silence a report about inert defaults.
- The issue classifies this as report readability / intent-loss framing, not correctness: the claim is literally true but over-names and does not mis-name.
- Candidate decision remains open: suppress inert nested defaults in `refilled_policy_subkeys`, decide whether top-level symmetry would alter existing behavior, or repair the warning remedy text instead.
- Destination named by the issue is `quality`, with candidate owners `scripts/quality_policy_merge.py` or `scripts/quality_bootstrap_absence.py`.
- Issue says the behavior arose after #493 recursion and was filed rather than fixed in that slice.

## Acquisition gap and non-claims

The public HTML route was blocked by captcha; no public body was treated as
captured. The authenticated CLI response is the source for the facts above.
This record does not claim the issue is fixed, that the proposed inert-default
predicate is correct, or that changing the warning text alone preserves all
operator intent. Local reproduction and semantic invariant proof remain
required.
