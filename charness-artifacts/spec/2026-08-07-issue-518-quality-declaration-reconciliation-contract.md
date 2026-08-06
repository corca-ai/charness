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

Do not compress the lifecycle into one enum. Each row carries separate typed
fields: `coverage` (`covered` or `unexamined`), `declaration_resolution`
(`resolved` or `unresolved`), `applicability`
(`applicable`, `inapplicable`, `unsupported`, or `empty-scope`), `execution`
(`not-run`, `missing`, `tool-error`, `completed`, or `malformed`),
`observed_result` (`graph-clean`, `graph-findings`, `unknown`, or `absent`),
and `aggregate_verdict` (`clean`, `advisory-non-clean`, `failed`,
`inapplicable`, `unsupported`, `deferred`, or `unexamined`). A declaration,
producer-only payload, missing binary, empty scope, or exit-0 helper is never
sufficient for `clean`.

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
- Pin the host-controlled Rust install route to upstream tag `v0.5.0` at
  verified commit `f65f8c43dbf0300609bdfdf823c09cba370222c6`:
  `cargo install --git https://github.com/corca-ai/awiki --tag v0.5.0
  --locked awiki`. The manifest must carry the tag, commit, version, and
  provenance-aware update command; a moving default branch is not reproducible.
- Add the `awiki-docs-graph` phase to `run-quality.sh` and the docs-only
  pre-push selection. In full, read-only, and explicit-label modes it invokes
  `scripts/run_awiki_quality.py --repo-root . --receipt
  charness-artifacts/quality/receipts/awiki-latest.json`, which persists a
  parsed receipt and raw-result digests. Use report-first policy for a valid
  graph finding: preserve the tool exit code `1`, emit aggregate verdict
  `advisory-non-clean`, and let the wrapper return success so a known docs
  finding is visible without masquerading as a tool failure. Missing binary,
  startup/tool error, malformed output, or no receipt returns failure and
  aggregate verdict `failed`; no route may silently skip or collapse a graph
  finding into clean.
- Keep existing `check-doc-links`, `markdownlint`, `check-links-internal`, and
  `nose` document-duplicate review until a command-level overlap matrix proves
  that a candidate has the same scope, reader boundary, and verdict semantics.
- Root and plugin manifests/dependency declarations are synchronized before
  validation; no sibling repository is modified by this slice.

## Verdict Algebra

The #518 final consumer must apply this table after parsing the persisted
receipt. It asserts both the displayed disposition and the aggregate verdict:

| Preconditions | Displayed disposition | Aggregate verdict |
| --- | --- | --- |
| declaration unresolved | declaration gap | `unexamined` |
| declaration resolved, unsupported language | unsupported | `unsupported` |
| declaration resolved, inapplicable or empty scope | scope inapplicable | `inapplicable` |
| applicable, execution not run | not run | `unexamined` |
| applicable, binary missing or startup/tool error | tool failure | `failed` |
| applicable, malformed/no receipt/unknown result | invalid evidence | `failed` |
| applicable, completed, valid graph findings, tool exit 1 | graph findings (report-first) | `advisory-non-clean` |
| applicable, completed, valid graph-clean result, tool exit 0 | graph clean | `clean` |
| explicit owner-approved deferral | deferred | `deferred` |

The healthy rule is exhaustive: only the final row for a valid completed
applicable graph-clean result may be `clean`. `covered` is a coverage field,
not permission to render a non-clean aggregate as clean. The current Charness
run therefore maps to `execution=completed`, `observed_result=graph-findings`,
`aggregate_verdict=advisory-non-clean`, with tool exit code `1` preserved.

## Probe Questions

- The policy is fixed for this goal: valid graph findings are report-first
  `advisory-non-clean`; missing, malformed, and tool-error states block as
  `failed`. The docs owner decides whether to remediate the seven orphans and
  230 link-only lines in a later slice; that remediation is not hidden by the
  advisory policy.
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
- Charness executes the exact awiki command through the `awiki-docs-graph`
  phase in full, read-only, explicit-label, and docs-only pre-push modes. The
  phase persists the canonical receipt, and the final artifact renderer reads
  that exact receipt, retaining tool identity, command, execution root, exit
  code, parsed graph counts, raw-result digest/locator, and non-clean status.
- The final-consumer fixtures cover unresolved declaration, unsupported
  language, inapplicable/empty scope, missing binary, tool error, malformed
  output/no receipt, exit-1 valid graph findings, and genuinely clean
  applicable execution; none of the non-clean cases can render as `clean`.
- The overlap matrix proves retention or deletion for every candidate existing
  linter; no duplicate detector is removed without replacement proof.
- Root/plugin projections and focused manifest/reader/final-fold tests agree.

## Acceptance Checks

- `python3 scripts/validate_integrations.py --repo-root .` (unit/integration:
  manifest schema and dependency declaration)
- `python3 scripts/check_staged_mirror_drift.py --repo-root .` (integration:
  root/plugin projection parity)
- `awiki --version` and `awiki lint -root docs -recursive` (baseline tool
  evidence only; preserve the observed failure)
- `CHARNESS_QUALITY_LABELS=awiki-docs-graph ./scripts/run-quality.sh
  --read-only --receipt-json=charness-artifacts/quality/receipts/quality-latest.json`
  (integration: actual Charness quality route and final-reader input)
- focused quality-reader/final-artifact tests for all algebra rows, including
  missing, malformed, exit-1 valid findings, and clean awiki outcomes
  (unit/integration: disposition propagation)
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
installation/discovery list and plugin projection, implement
`scripts/run_awiki_quality.py` plus its parser and persisted receipt at
`charness-artifacts/quality/receipts/awiki-latest.json`, wire the
`awiki-docs-graph` phase into `scripts/run-quality.sh` and the docs-only
`.githooks/pre-push` selection, and make the final quality artifact consume
that receipt. Then rerun the exact Charness awiki command in this repository
and record the overlap matrix before any linter deletion.
