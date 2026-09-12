# Debug Review: issue 813 temporary-output ownership
Date: 2026-09-12

## Problem

Charness has an owned runtime-scratch primitive, but production commands can still
create anonymous system-temp roots that no Charness inspection or GC surface can
attribute after abrupt termination.

## Correct Behavior

Every production temporary-output producer is either under one receipt-bound
Charness root, a colocated atomic file with bounded cleanup, an anonymous
auto-delete handle, or an explicitly durable output. New unclassified producers
are refused before merge.

## Observed Facts

- `scripts/runtime_scratch.py` owns receipts, locks, retention, promotion, and
  terminal states; 61 focused scratch tests and 75 lifecycle/recovery tests pass.
- Inspection is bounded to `<runtime-root>/scratch/<producer>/<run>` and therefore
  cannot account for anonymous roots outside that namespace.
- Static inventory found unresolved directory producers in five root shell checks,
  `scripts/check-secrets.sh`, and the Claude evaluator. Ordinary traps/finally
  remove them, but SIGKILL or host loss leaves no owner receipt.
- Atomic sibling files and anonymous context-managed file handles are bounded and
  are not the reported directory-leak class.

## Reproduction

- `rg -n 'mktemp|mkdtempSync' scripts skills/public` finds production directory
  creators outside `owned_scratch`; compare with `rg -n 'owned_scratch' scripts
  skills/public`. The former includes `scripts/check-shell.sh:39`,
  `scripts/check-python-lint.sh:67`, `scripts/check-links-internal.sh:70`,
  `scripts/check-links-external.sh:42`, `scripts/check-markdown.sh:91`,
  `scripts/check-secrets.sh:125`, and
  `scripts/agent-runtime/run-local-eval-test.mjs:77`.

## Candidate Causes

- Candidate: the scratch primitive is defective. Disconfirmed by focused lifecycle,
  refusal, promotion, and recovery tests.
- Confirmed: adoption is voluntary and no inventory/gate distinguishes safe local
  temporaries from unowned run roots.

## Hypothesis

- If a semantic producer inventory becomes the single registration boundary and
  unresolved directory producers migrate to owned roots, then deleting one entry
  or adding a raw directory producer will fail the gate, while atomic sibling and
  anonymous-file cases remain accepted. Disconfirmer: an unregistered producer or
  stale registration passes the focused negative controls.

## Verification

- Result: confirmed for the current absence claim — AST/text inventory found both
  registered and unresolved producers, while no existing production gate owns that
  classification. Implementation verification remains pending.

## Root Cause

Commands historically chose temp paths locally; cleanup was treated as a caller
detail. The new owner primitive repaired selected carriers but did not replace that
mental model with a mandatory producer registration boundary. Consequently normal
exit tests can be green while cancellation leaves paths the final GC consumer is
structurally unable to see.

## Invariant Proof

- Invariant: when a production command creates a temporary directory, the runtime
  registry must identify its owner and lifecycle before inspect/GC can claim the
  Charness-owned population is accountable.
- Producer Proof: the cited shell and JS sites create system-temp directories with
  only local cleanup.
- Final-Consumer Proof: `runtime_scratch_registry.py` traverses only the declared
  scratch namespace; a live inspect reports only receipt-bound roots.
- Interface-Shape Sibling Scan: shell `mktemp -d`, JS `mkdtempSync(tmpdir())`, Python
  directory constructors, and runtime-root allocations were classified by behavior.
- Non-Claims: existing arbitrary `/tmp` debris is not attributed to Charness; SIGKILL
  acceptance for every external tool is not yet proven.

## Detection Gap

- production quality gates | no gate rejects an unregistered temp-directory producer
  | add a manifest-backed semantic producer inventory with missing/stale controls.
- lifecycle tests | root primitive and critique paths pass without sampling every
  producer class | add representative process/root acceptance for success, failure,
  timeout, and cancellation plus final-consumer receipt readback.

## Sibling Search

- Mental model: a local `finally` proves lifecycle ownership, even when abrupt process
  loss prevents it from running.
- same layer: shell check scripts and Claude evaluator | decision: same bug, fix now
  | proof: static scan only.
- abstraction up: all production temp creators | decision: same bug, fix now | proof:
  static inventory plus executable gate negative control required.
- specialization down: atomic sibling files and anonymous auto-delete handles |
  decision: intentional plain-text or non-rendering boundary | proof: local payload
  proof from context/finally implementation.
- cross-file: `scripts/runtime_scratch_registry.py` is the final consumer and cannot
  infer paths created outside its namespace.

## Seam Risk

- Interrupt ID: issue-813-temp-output-ownership
- Risk Class: repeated-symptom
- Seam: production temp producer to runtime scratch registry/GC
- Disproving Observation: complete producer inventory plus mutation controls and
  process-terminal acceptance leave no unclassified directory producer.
- What Local Reasoning Cannot Prove: host hard-kill behavior for unsampled external
  tools.
- Generalization Pressure: factor-now

## Interrupt Decision

- Resolution: open
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-09-12-issue-813-temp-output-lifecycle.md

## Prevention

Make producer classification executable, migrate directory-producing run roots to
the shared owner, retain narrow local-file exceptions, and test the registry as the
final consumer rather than inferring ownership from producer cleanup.
