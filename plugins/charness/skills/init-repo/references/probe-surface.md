# Probe Surface

When a repo ships an installable CLI, plugin, package, or local agent-facing
integration surface, `init-repo` should bootstrap one small explicit probe
surface instead of leaving wrappers or operators to infer it later.

This is not a demand for giant command taxonomies or mandatory bootstrap docs
files. It is a normalization move for repos whose install and probe semantics
would otherwise drift.

## Minimum Shape

Name these only when the repo really exposes them:

- canonical install or update path
- canonical binary healthcheck
- machine-readable command discovery, if the repo actually has one
- repo or install readiness command
- local discoverability or materialization step for plugins, skills, or cached
  host-visible surfaces

## Placement

- keep the repo story and high-level pointer in [`README.md`](../../../../README.md)
- put the fuller install and probe semantics in a repo-local bootstrap doc when
  the repo genuinely needs one
- keep [`docs/operator-acceptance.md`](../../../../docs/operator-acceptance.md) focused on takeover and acceptance, not as
  the primary install manual

## Avoid

- saying "`doctor` checks everything" when health, readiness, and local
  discoverability are different seams
- duplicating conflicting install or probe guidance across [`README.md`](../../../../README.md) and
  the repo's deeper bootstrap guidance
- inventing a discovery command that the repo does not really ship
