# Issue #518 Quality Declaration Reconciliation Contract

Date: 2026-08-07
Source: [Issue #518 debug record](../debug/2026-08-07-issue-518-quality-declaration-reconciliation-debug.md)

## Problem

Quality configuration can preserve a preset, adapter field, canonical document,
skill path, or language-specific gate without proving that the declaration
reaches an executable reader and the final quality artifact. Producer exit 0 or
zero findings can therefore become a false healthy result. The new `awiki`
dependency adds the same obligation: installation and execution must be
declared, read, and folded as a typed final disposition.

## Capability Contract

The quality control plane must reconcile every declared quality surface through:

`declaration → resolved reader → applicability/scope → observed result → final consumer`.

Each row has a typed state: `covered`, `clean`, `unexamined`, `unsupported`,
`inapplicable`, `deferred`, or `failed`. A declaration, producer-only payload,
missing binary, empty scope, or exit-0 helper is never sufficient for `clean`.

`awiki` is an external binary owned through `integrations/tools/awiki.json`.
The manifest owns detection, healthcheck, install/update guidance, version
observation, degradation, and `quality` intent discovery. The quality route owns
the exact repository invocation `awiki lint -root docs -recursive`, its parsed
result, and the final artifact disposition. The synchronized plugin projection
must expose the same manifest and dependency membership.

## Current Slice

Add the manifest/dependency/quality-reader contract and its fixtures, then run
the actual Charness docs graph command through the final quality consumer. This
slice does not claim that the current docs graph is repaired or that #514/#515
are implemented.

## Fixed Decisions

- Use the upstream `corca-ai/awiki` binary as an external integration; do not
  vendor its implementation or hide installation in a casual command example.
- Prefer the host-controlled Rust install route (`cargo install --git
  https://github.com/corca-ai/awiki awiki`) and retain detect/healthcheck and
  version evidence; update through the same provenance-aware route.
- Run Charness with `awiki lint -root docs -recursive` and preserve non-zero
  output as `failed`/advisory according to the final quality policy; never
  silently skip a missing binary or collapse a failed graph into clean.
- Keep existing `check-doc-links`, `markdownlint`, `check-links-internal`, and
  `nose` document-duplicate review until a command-level overlap matrix proves
  that a candidate has the same scope, reader boundary, and verdict semantics.
- Root and plugin manifests/dependency declarations are synchronized before
  validation; no sibling repository is modified by this slice.

## Probe Questions

- Should the awiki result be a blocking gate or a report-first advisory for the
  current Markdown corpus? The final consumer fixture must answer without
  hiding `failed`, and the choice must name the remediation/owner boundary.
- Which awiki counts and paths are stable enough for machine-readable parsing,
  and which remain raw diagnostic text? Pin this against the installed binary
  and a synthetic fixture rather than assuming the current summary format.
- Does any existing linter fully subsume awiki graph connectivity or link-only
  judgment? Compare commands and findings before deleting anything.

## Deferred Decisions

- Repairing the seven current orphan pages and 230 link-only lines is a
  follow-up implementation decision after the final-consumer contract exists.
- Cross-repository docs graph policy for `cmanki` and `craken-agents` is
  comparison evidence, not a consumer-repo change or product claim.
- A general quality-integration manifest schema redesign is outside this slice.

## Non-Goals

- Do not remove a linter because it is named “lint” or because awiki is cheaper.
- Do not copy `craken-agents`'s repository-specific gate list into Charness.
- Do not claim awiki installation on hosts where only this host's binary was
  observed; missing-host behavior remains an explicit disposition.
- Do not close #518, #515, or #514 from this contract alone.

## Deliberately Not Doing

- No `awiki format` rewrite is part of the proof; the current run is read-only.
- No sibling worktree write, remote publish, Cautilus evaluation, or issue close.
- No clean verdict from `documents=40`, `orphans=7`, `islands=0`,
  `link_only_lines=230`, `largest_component_ratio=0.8250`,
  `orphan_rate=0.1750`, `content_coverage=1.0000`, exit 1.

## Constraints

- The final quality artifact must bind tool version, exact args, execution root,
  exit code, parsed counts, result digest/locator, final consumer, and
  unexamined axes.
- The integration validator, plugin parity check, quality route, and focused
  tests must distinguish missing, failed, unsupported, and inapplicable states.
- The #518 contract must compose with #515 routing/disclosure and #514 evidence
  assembly without making any issue depend on another issue's taxonomy.

## Success Criteria

- A fresh checkout can resolve the awiki manifest, report readiness, and expose
  a reproducible install/update path through the quality integration surface.
- Charness executes the exact awiki command and its final artifact retains the
  tool identity, command, exit code, parsed graph counts, and non-clean status.
- A missing binary, command failure, or unsupported/scope-empty result is not
  measured as clean and is visible to the final consumer.
- The overlap matrix proves retention or deletion for every candidate existing
  linter; no duplicate detector is removed without replacement proof.
- Root/plugin projections and focused manifest/reader/final-fold tests agree.

## Acceptance Checks

- `python3 scripts/validate_integrations.py --repo-root .` (unit/integration:
  manifest schema and dependency declaration)
- `python3 scripts/check_staged_mirror_drift.py --repo-root .` (integration:
  root/plugin projection parity)
- `awiki --version` and `awiki lint -root docs -recursive` (integration:
  installed binary and actual Charness reader; preserve the observed failure)
- focused quality-reader/final-artifact tests for missing, failed, and clean
  awiki outcomes (unit/integration: disposition propagation)
- `python3 scripts/validate_quality_artifact.py --repo-root .` and
  `python3 scripts/validate_debug_artifact.py --repo-root .` (integration:
  durable evidence shape)
- `python3 scripts/plan_risk_interrupt.py --repo-root . --changed-paths
  charness-artifacts/spec/2026-08-07-issue-518-quality-declaration-reconciliation-contract.md`
  (integration: interrupt handoff remains explicit)

## Boundary Ownership

- `preserve`: the integration manifest owns external binary readiness and
  install/update policy; it does not own graph meaning.
- `preserve`: awiki owns graph analysis; the quality reader owns invocation and
  parsed receipt; the quality artifact/final fold owns the visible verdict.
- `preserve`: existing link/Markdown/duplicate tools retain their own reader
  boundaries unless the overlap matrix proves replacement.
- `preserve`: Charness owns its docs and quality contract; `cmanki` and
  `craken-agents` remain read-only comparison sources.

## Critique

- Interrupt Source: issue-518-declaration-to-verdict
- Seam Summary: consumer adapter/preset declaration → quality helper/adapter mirror →
- Chosen Next Step: critique
- Impl Status: blocked
- Impl Status Reason: the causal record found producer-side evidence but no final-consumer proof; the current awiki run demonstrates the same visibility requirement.
- What Disproving Observation Is Resolved: the pinned consumer and Charness awiki run both show that an exit-0/installed producer is not equivalent to a clean final verdict.
- Fresh-Eye Review: required before the implementation slice; the parent goal owns the bounded architecture/execution/counterweight review and the second round for repaired verdict logic.

## Canonical Artifact

- `charness-artifacts/spec/2026-08-07-issue-518-quality-declaration-reconciliation-contract.md`

## First Implementation Slice

Add `integrations/tools/awiki.json`, include `awiki` in the quality dependency
installation/discovery list and plugin projection, implement the smallest
reader/final-disposition fixture path, then rerun the exact Charness awiki
command and record the overlap matrix before any linter deletion.
