# Automation Promotion

`quality` should separate three cases before writing findings:

- `AUTO_EXISTING`
- `AUTO_CANDIDATE`
- `NON_AUTOMATABLE`

## `AUTO_EXISTING`

The concern is already enforced by a meaningful deterministic gate.

Examples:

- a broken markdown link already caught by `check_doc_links.py`
- a backtick-wrapped file reference that would silently rot on rename, already
  caught by the same `check_doc_links.py` rule that rejects path-like
  tokens inside inline code, paired with `check-links-internal.sh` for
  actual file-existence verification
- malformed skill frontmatter already caught by `validate_skills.py`
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

## Interpreting inference-layer advisories

The "unless you are adding repository level interpretation" clause above is not
optional for inference-layer proxies (clone/duplicate %, ergonomics heuristics,
test-economics trends, recommendation rankings, length/pressure smells, runtime
trends). When such an output declares an `interpretation` self-declaration per
[advisory-interpretation-contract.md](../../../shared/references/advisory-interpretation-contract.md),
answer its declared interpretation question for this repo before repeating,
ranking, or escalating the number. The contract is inference-layer only; verified
facts (green gates, counts, AST results) stay trusted, never re-litigated.

Per-surface interpretation questions the consumer must answer first (one line per
inference-layer surface, not a banner repeated per invocation):

- `inventory_nose_clones.py` (clone families): which families are intentional /
  portability boilerplate versus genuinely extractable debt for THIS repo?
- `inventory_skill_ergonomics.py` (ergonomics heuristics / `subcheck_counts`):
  which heuristic hits are real ergonomic/portability debt versus intentional
  structure the lexical heuristic cannot distinguish?
- `inventory_standing_test_economics.py` (test-economics trend): is the
  test-file / nested-CLI growth paying for real isolation and coverage value, or
  is it startup-cost waste THIS repo should consolidate?
- `inventory_lint_ignores.py` (suppression pressure): which suppressions are
  justified, provenance-bearing deferrals versus normalized debt THIS repo should
  structurally fix?
- `check_python_lengths.py` warn band / `--headroom` near-limit (length smell —
  the hard over-limit file gate stays a verified fact, never re-litigated;
  function length is gated separately by ruff PLR0915):
  is a warn-band file an honest cohesive unit near its limit,
  or genuine over-accumulation THIS repo should split now?
- recommendation rankings (`find-skills` `recommendation_interpretation`; this
  artifact's `Recommended Next Gates` ordering — see
  [gate-classification.md](./gate-classification.md)): does the top-ranked item
  genuinely fit THIS repo's current state, or is it a generic default / a
  trigger-phrase coincidence the ranking cannot contextualize?
- `render_runtime_summary.py` (runtime hot-spot trend): is a hot spot a real
  standing cost THIS repo should budget or optimize, or transient machine noise /
  a cost that already buys necessary proof?

## Adding an advisory inventory or interpretation surface

When you add a new advisory inventory (`inventory_*.py`) or a new inference-layer
output, front-load these registrations so the requirement does not surface only
at the slow broad gate. Each is enforced by a deterministic gate; the first three
now run at the **commit boundary** (the cheap structural sweep), so a miss fails
in ~1s, not after a ~4-min broad-pytest run.

- **A 4-field `interpretation` self-declaration?** Register the declaration file +
  paired consumer line in `<repo-root>/.agents/inference-interpretation-surfaces.json`
  per the
  [advisory-interpretation contract](../../../shared/references/advisory-interpretation-contract.md).
  An unregistered 4-field dict is a `LEAK` failure
  (`validate-inference-interpretation`, commit-boundary).
- **A new `inventory_*.py` under `skills/public/quality/scripts/`?** Declare it in
  [`inventory-consumer-fields.json`](./inventory-consumer-fields.json) (≥2
  non-headline fields, or a non-empty `opt_out_reason`)
  (`check-inventory-declaration-coverage`, commit-boundary).
- **An exit-zero / advisory / skipped attention state?** Make it visible in
  [`attention-state-visibility.json`](./attention-state-visibility.json)
  (`validate-attention-state-visibility`, commit-boundary).
- **A public-skill behavior worth dogfooding?** Update the dogfood
  `EVIDENCE_OVERRIDES` scaffold per the authoring-repo-internal
  `docs/public-skill-dogfood.md`.
- **Touching a `SKILL.md`?** Keep it inside the ≤200-line core budget (the
  `check-skill-core-headroom` ratchet) — push depth into `references/`.

If you add a new commit-boundary structural check, record its timing verdict in
the authoring-repo-internal `docs/conventions/validator-timing-layers.md`.
