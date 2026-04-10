# Automation Promotion

`quality` should separate three cases before writing findings:

- `AUTO_EXISTING`
- `AUTO_CANDIDATE`
- `NON_AUTOMATABLE`

## `AUTO_EXISTING`

The concern is already enforced by a meaningful deterministic gate.

Examples:

- a broken markdown link already caught by `check-doc-links.py`
- malformed skill frontmatter already caught by `validate-skills.py`
- Python import hygiene already caught by `ruff`

Do not repeat these as primary manual findings unless you are adding repository
level interpretation.

## `AUTO_CANDIDATE`

The concern should become a deterministic gate.

Examples:

- repeated helper boilerplate that should be surfaced by duplicate checks
- profile references to missing skills that should fail validation
- secret-bearing text that should be checked by `gitleaks`, `secretlint`, or another repo-native secret scanner
- markdown portability rules that should be checked by markdown lint or link
  validation

Preferred outputs:

- a concrete validator or linter rule
- a test or smoke scenario
- a hook or script entrypoint

## `NON_AUTOMATABLE`

The concern still requires judgment, tradeoffs, or human review.

Examples:

- whether one public skill is conceptually overloaded
- whether a proposed gate is worth the maintenance burden
- whether a mode split is honest or design laziness

These belong in prose findings and proposals.

## Rule

If a concern is `AUTO_CANDIDATE`, prefer promoting it into a deterministic gate
before adding more policy text.
