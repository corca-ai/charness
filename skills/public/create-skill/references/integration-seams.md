# Integration Seams

Public and support skills must describe external dependencies honestly.

They should also describe runtime access honestly: isolated hosts may provide a
grant or authenticated binary, while ordinary local hosts may need env
fallback.

## Use An Integration Manifest When

- the skill depends on an external binary
- an upstream repo owns the support skill
- the host needs detect, healthcheck, update, or degradation rules

The canonical contract is `<repo-root>/integrations/tools/manifest.schema.json`.

When `charness` owns the runtime itself, the canonical metadata contract is
[capability.schema.json](../../../support/capability.schema.json)
and the file should live next to the support skill as
`skills/support/<skill-id>/capability.json`.

## Ownership Rules

- `charness` owns when the tool should be used and how workflows degrade
- upstream owns the binary and deep tool-specific behavior
- another repo can be a useful reference implementation without becoming the
  runtime owner; model external ownership only when the consumer really needs
  that external runtime installed or synced
- when learning from a reference implementation, preserve the `Core Practice`
  that creates the value and adapt only the `Peripheral Practice` that reflects
  host, packaging, credential, or adapter details
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
- keep support capability metadata equally rich when `charness` owns the
  runtime and no true external integration boundary exists
- declare readiness probes in the manifest when setup prerequisites should fail
  closed before runtime use
- define degradation behavior when the tool is missing or stale
- prefer `reference`, `copy`, `symlink`, or `generated_wrapper` explicitly;
  never make sync strategy implicit
- do not use adapters or presets as secret transport

## GitHub-Hosted Release Metadata

When an integration manifest points at a GitHub-hosted upstream repo and
operator guidance benefits from current release metadata, model that probe as
part of the integration seam instead of hiding a best-effort web call in prose.

Preferred behavior:

- use authenticated `gh api` first when an already authenticated GitHub CLI is
  available
- fall back to HTTP with `GH_TOKEN` or `GITHUB_TOKEN` before public
  unauthenticated HTTP
- keep `gh` optional unless the integration truly requires private GitHub
  access
- persist `status`, `reason`, and `error` in lock or state output so
  `no-release`, `github-forbidden`, invalid JSON, and network failure are
  operationally distinct
- do not turn release probing into silent install or update mutation

## Review Questions

- can this dependency be represented as a manifest instead of a copied skill?
- if a wrapper exists, is it thin and clearly justified?
- does the skill still produce value when the dependency is absent?
