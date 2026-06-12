# Quality Signal Scorecard

Before any structural quality cleanup edit, build a candidate scorecard from
the available signals. Every quality tool output — clone-family advisories,
duplicate reports, coverage, runtime timing, linters, evals, review findings —
is a **signal**, not a source of truth: each carries the inference-layer
self-declaration contract from
[advisory-interpretation-contract](../../../shared/references/advisory-interpretation-contract.md),
and acting on a bare number without the repo-level judgment row below is the
failure this scorecard exists to block.

A cleanup rationale that cites only a metric ("the dup-line total went down",
"the score improved") is **not acceptable**; the scorecard forces the
behavior-value judgment that the metric cannot make.

## When To Fill It

Fill the scorecard once per structural-cleanup intent, before the first code
edit — not per finding and not after the fact. If mid-work the candidate set
keeps splitting into tiny moves, the set was not structurally settled; stop
editing and re-score (see
[meaningful-slice-cadence](../../../shared/references/meaningful-slice-cadence.md)).

## Per-Candidate Rows

Score each cleanup candidate with these rows; one line each is enough:

- **Behavior value** — what observable behavior, operator workflow, or
  failure class improves if this lands. "The number improves" does not
  qualify.
- **Intent overlap** — which current goal, issue, or contract this serves;
  orphan cleanups default to deferred.
- **Structural signal class** — which structural response the signal maps to
  (machine-owned consistency, owned extraction, generated-surface ownership,
  or design review) per the clone-family taxonomy in
  [inventory-dispatch](./inventory-dispatch.md).
- **Tool signals** — which tools point here, with each treated as a signal
  plus its known blind spots; two weak signals do not sum to one strong one.
- **Ownership** — the owning module/surface the cleanup would live in; if no
  owner is nameable, the candidate is a design question, not an edit.
- **Gate blast radius** — which gate families and generated surfaces the edit
  will touch, and what re-proof that implies.
- **Cost** — rough size of the edit plus its proof, including any
  generated-surface or mirror sync and any coverage-producing rerun.
- **Disposition** — do-now, defer (with trigger), or keep-with-fence; record
  it so the next scan consumes decisions instead of re-discovering findings.
- **Stop condition** — what observation ends this cleanup intent, so the
  loop cannot quietly continue past its value.

## Artifact Discipline

- Learn the owning template/validator contract before drafting any quality
  record; template-first, never post-hoc reshaping.
- Keep current-pointer refreshes separate from record-artifact drafting;
  pointer updates ride the work they describe.
- Behavior proof and ownership clarity come before code edits; broad standing
  gates stay bundle/final-boundary proof per the meaningful-slice cadence.
