# Integration Seams

Public and support skills must describe external dependencies honestly.

They should also describe runtime access honestly: isolated hosts may provide a
grant or authenticated binary, while ordinary local hosts may need env
fallback.

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
- public skills own the capability requirement, not the secret plumbing

## Authoring Rules

- do not vendor an external binary into `charness`
- do not imply a required tool with a casual shell snippet
- declare `support_skill_source` when an upstream skill exists
- prefer grant-first, then authenticated binary, then env fallback
- keep manifest metadata rich enough for discovery surfaces to expose what kind
  of capability exists and which access modes it supports
- declare readiness probes in the manifest when setup prerequisites should fail
  closed before runtime use
- define degradation behavior when the tool is missing or stale
- prefer `reference`, `copy`, `symlink`, or `generated_wrapper` explicitly;
  never make sync strategy implicit
- do not use adapters or presets as secret transport

## Review Questions

- can this dependency be represented as a manifest instead of a copied skill?
- if a wrapper exists, is it thin and clearly justified?
- does the skill still produce value when the dependency is absent?
