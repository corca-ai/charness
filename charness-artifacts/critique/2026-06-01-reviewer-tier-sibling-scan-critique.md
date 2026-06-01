# Fresh-Eye Critique: Reviewer Tier Sibling Scan

Target: direct fresh-eye reviewer sibling fixes after the critique adapter
reviewer-tier default change.

## Change

Direct high-leverage reviewer spawns in `quality`, issue causal review, and
`setup` now name the portable `high-leverage` tier and tell agents to apply
host-exposed `reviewer_tiers.high-leverage` fields. Setup adapter scaffolding
now carries review-policy evidence fields consumed by setup inspection while
leaving delegated-review recommendations disabled by default.

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated.

Reviewer:

- Cicero (`019e82e1-8c01-7c62-babc-07beffff7387`) — host-plural policy,
  sibling coverage, scaffold safety, and test scope

## Act Before Ship

Fixed before closeout:

- Removed default `agents.delegated_review_policy` recommendation/enablement
  from the setup adapter scaffold. The scaffold remains evidence-driven: it
  declares where to look for review-policy terms but does not push Charness
  delegated-review policy into every new consumer repo without evidence or
  explicit adapter opt-in.
- Added a consumer-effect regression proving a scaffolded setup adapter plus a
  plain `AGENTS.md` does not emit `agents.delegated_review_policy`.

## Counterweight Triage

No remaining ship blocker after the setup scaffold correction.

Bundle anyway:

- Keep the direct reviewer prompt edits, setup scaffold safety fix, tests,
  debug artifact, and plugin mirror in one commit because they close one
  sibling class.
- Keep concrete provider values only in adapter surfaces; portable skill prose
  names only the tier and field path.

Over-worry:

- Provider model names in adapter examples/contracts remain acceptable because
  those are host-specific adapter documentation, not portable skill instructions.

Valid but defer:

- The known direct-reviewer test uses a maintained tuple. A future stronger gate
  could scan newly added direct fresh-eye spawn language and require nearby
  `high-leverage` plus `reviewer_tiers.high-leverage`.

## Verification Cited

- targeted reviewer-tier and setup scaffold tests
- skill, adapter, packaging, markdown, debug-artifact, and changed-surface gates
- broad pytest after blocker fix
