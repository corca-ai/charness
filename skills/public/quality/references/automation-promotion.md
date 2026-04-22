# Automation Promotion

`quality` should separate three cases before writing findings:

- `AUTO_EXISTING`
- `AUTO_CANDIDATE`
- `NON_AUTOMATABLE`

## `AUTO_EXISTING`

The concern is already enforced by a meaningful deterministic gate.

Examples:

- a broken markdown link already caught by [`check_doc_links.py`](../../../../scripts/check_doc_links.py)
- a backtick-wrapped file reference that would silently rot on rename, already
  caught by the same [`check_doc_links.py`](../../../../scripts/check_doc_links.py) rule that rejects path-like
  tokens inside inline code, paired with [`check-links-internal.sh`](../../../../scripts/check-links-internal.sh) for
  actual file-existence verification
- malformed skill frontmatter already caught by [`validate_skills.py`](../../../../scripts/validate_skills.py)
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
- stable CLI command docs that should be checked against no-side-effect
  `--help` output and a repo-local command-docs contract

Preferred outputs:

- a concrete validator or linter rule
- a test or smoke scenario
- a hook or script entrypoint

Promotion checklist:

- follow the canonical routing in `SKILL.md` first: length, duplicate, and
  pressure findings stay advisory until the repo can name one explicit
  low-noise invariant and a clear structural response
- the invariant is clear enough to explain in one sentence
- false positives are low enough that maintainers will trust the gate
- the expected structural response is obvious: delete, merge, split ownership,
  extract a helper, narrow an interface, or add one missing proof seam
- the gate protects a real concept, behavior, security, or operability claim,
  not a cosmetic score target

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

Treat length, duplicate, and pressure heuristics as smell sensors first. That
default is a tie-breaker, not a veto: if the repo has an honest invariant and
the failure implies a clear structural action, promote it. If not, keep it
advisory or `NON_AUTOMATABLE` instead of forcing it into a hard gate.

When the same confidence gap can be closed either by shrinking production
surface or by adding more tests, prefer the smaller production surface first if
behavior and signal both improve. Test growth is not the default answer when
design simplification removes the risk more directly.
