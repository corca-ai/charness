# Integration Seams

Public and support skills must describe external dependencies honestly.

## Use An Integration Manifest When

- the skill depends on an external binary
- an upstream repo owns the support skill
- the host needs detect, healthcheck, update, or degradation rules

The canonical contract is [manifest.schema.json](/home/ubuntu/charness/integrations/tools/manifest.schema.json).

## Ownership Rules

- `charness` owns when the tool should be used and how workflows degrade
- upstream owns the binary and deep tool-specific behavior
- a thin local wrapper is acceptable only when the upstream skill is missing,
  incompatible, or too broad for the harness

## Authoring Rules

- do not vendor an external binary into `charness`
- do not imply a required tool with a casual shell snippet
- declare `support_skill_source` when an upstream skill exists
- define degradation behavior when the tool is missing or stale
- prefer `reference`, `copy`, `symlink`, or `generated_wrapper` explicitly;
  never make sync strategy implicit

## Review Questions

- can this dependency be represented as a manifest instead of a copied skill?
- if a wrapper exists, is it thin and clearly justified?
- does the skill still produce value when the dependency is absent?
