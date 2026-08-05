# Issue #511 Nose Inventory Scope Debug
Date: 2026-08-05

## Problem

`inventory_nose_clones.py` sends Charness-only default roots to `nose` for a
consumer repository that has `src/scripts/worker` but no `skills/` tree. The
wrapper reports an error with zero families and exits successfully, so the
quality runner can record a completed-looking inventory.

## Correct Behavior

The inventory must distinguish requested, scanned, and missing roots. Missing
optional defaults must not be passed to `nose`; a repository with no valid
default root must be explicitly inapplicable or blocked. A failed query must
remain machine-distinguishable from `clean` and must not be represented as a
completed scan by the quality receipt.

## Observed Facts

- Issue #511 is OPEN with no comments; it names `scripts`, `skills/public`, and
  `skills/support` as defaults and provides a successful explicit-path example.
- `inventory_nose_clones.py:32,86` unconditionally selects those defaults.
- `nose_report_lib.py:177-189` preserves the supplied roots as the query scope;
  it has no missing-root classification before invocation.
- `run-quality.sh:849-854` queues the wrapper, while the wrapper's `main` returns
  zero for advisory statuses; a zero exit is therefore not proof of a scan.

## Reproduction

- In a temporary repository containing `src/scripts/worker` and no `skills/`
  directories, run `python3 skills/public/quality/scripts/inventory_nose_clones.py
  --repo-root <tmp> --summary` with nose 0.20.0 available.
- Result: `rc=0`, `status: error`, `family_count: 0`, default paths retained,
  `exit_code: 1`, and stderr `nose emitted no output; the scan produced nothing
  to read`.
- The same binary with explicit `--path src --path scripts --path worker`
  reaches `status: findings`, so the failure is scope selection, not nose
  availability or a universal query failure.

## Candidate Causes

- Default roots are encoded as producer assumptions rather than a consumer
  scope contract.
- The collector correctly degrades a failed query to `error`, but the wrapper
  does not expose missing/scanned root state and the runner sees only exit 0.
- Quality inventory declaration and dispatch prose do not require consumers to
  engage with the scope/error fields.

## Hypothesis

- If root validity is classified before query construction, then the fixture
  will scan only existing defaults and disclose missing roots; with no valid
  root it will return an explicit non-scan status. If the final receipt consumes
  that status, it cannot label the result as a completed scan. Disconfirmer: an
  existing-root-only fixture still reproduces the error after filtering.

## Verification

- confirmed — the minimal fixture reproduced the error and zero exit; explicit
  paths reached a real findings result.
- confirmed — delegated causal review independently identified the same missing
  scope-validity contract and the receipt propagation gap.
- unresolved implementation questions are transferred to the #511 spec; no
  consumer-repository or installed-plugin roundtrip is claimed.

## Root Cause

The producer assumes its own three-root layout is universal. It invokes one
query over nonexistent roots instead of classifying the requested scope first;
the resulting `error` payload is advisory and the wrapper's successful process
exit allows `run-quality.sh` to record it without a scan-validity verdict.

## Invariant Proof

- Invariant: a non-scan status must never be represented as a completed clone
  inventory in the final quality result.
- Producer Proof: `inventory_nose_clones.py:86,135-152` emits the unconditional
  scope and error payload; the temporary fixture observes it directly.
- Final-Consumer Proof: `run-quality.sh:849-854` queues the wrapper and
  `run-quality.sh:286-305,535-550` treats successful queued execution as a
  measured receipt; this is local source proof, not a consumer-repo roundtrip.
- Interface-Shape Sibling Scan: `dup_ratchet_scan.py:197-205` already degrades
  an error; `inventory_doc_duplicates.py:340-371` fails closed for a required
  tool. Both are comparison evidence, not extra failure claims.
- Non-Claims: no private consumer checkout, installed plugin, provider, or
  remote CI behavior has been verified for #511.

## Detection Gap

- `tests/quality_gates/test_quality_nose_advisory.py` covers missing nose and
  successful fake scans but not an existing-code-root fixture without skill
  roots; add that regression and assert requested/scanned/missing scope.
- The quality receipt path has no assertion that `error` or `inapplicable` is
  non-completed; add a focused runner/consumer assertion without making this
  advisory duplication count a hard threshold.

## Sibling Search

- Mental model: a quality producer's default scope silently mismatches the
  consuming repository's source layout.
- same interface: `run-quality.sh:849-854` | decision: bundle status propagation
  and receipt semantics | proof: local source inspection.
- adjacent contract: `dup_ratchet_scan.py:45-50,197-205` | decision: defer its
  broader changes because configured `scope_paths` already guards it | proof:
  static inspection.
- cross-file: `docs/duplicate-detection-strategy.md:101-115` and
  `integrations/tools/nose.json:92` document the stale fixed scope | decision:
  update the affected scope contract/configuration | proof: source inspection.

## Seam Risk

- Interrupt ID: quality-511-default-scope
- Risk Class: external-seam
- Seam: default-root resolver -> `nose query` -> advisory payload -> quality
  runner receipt
- Disproving Observation: an existing-root-only fixture must produce a valid
  scan or an explicit inapplicable result; the current fixture instead errors.
- What Local Reasoning Cannot Prove: behavior in private consumer repositories
  and installed plugin caches; local fixtures and source/plugin parity are the
  available evidence ladder.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-08-05-issue-511-nose-inventory-contract.md

## Prevention

Resolve scope validity before invoking external scanners; carry requested,
scanned, and missing paths plus a machine-readable scan status into both JSON
and summary output; make final consumers reject non-scan statuses as completed
measurements; and keep alternate source roots adapter-owned and documented.
