# Proposal Flow

`quality` is not only a gate-reporting skill. It is also a proposal skill.

## Principle

If a useful gate is missing, propose the smallest concrete setup that would
improve confidence materially.

If the issue is automatable, propose the gate before proposing more prose.

## Good Proposals

Good proposals name:

- the seam the gate would protect
- the command or tool family to use
- where it should run
- why it is the next best improvement
- whether the proposal is `AUTO_CANDIDATE` or `NON_AUTOMATABLE`

Examples:

- add `ruff check` in CI because Python linting is currently absent and the repo
  already uses `pyproject.toml`
- add one focused integration test because the failure path is user-visible and
  unit tests cannot prove it honestly
- add dependency review in CI because supply-chain changes are currently
  invisible in pull requests
- replace repeated documentation guidance with `markdownlint` or a repo-owned
  validator because the rule is deterministic and repeated manually today

## Bad Proposals

Bad proposals sound like:

- improve code quality
- add more tests
- harden security

Those are ambitions, not next steps.
