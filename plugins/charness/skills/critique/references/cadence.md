# Critique Cadence

Critique cadence is scoped by risk boundary, not by commit count. The
slice-unit definition itself — what makes a unit meaningful enough to review —
is owned by
[meaningful-slice-cadence](../../../shared/references/meaningful-slice-cadence.md).

## Escalation Ladder

Use the lightest rung that still protects the next irreversible decision:

1. **No repo-change turn** — inspect-only, status-only, and routing-only work may
   record `Critique: not-applicable <reason>`.
2. **Small local-risk slice** — a same-agent scoped critique is enough when the
   change is narrow, reversible, and does not alter workflow, prompt,
   public-skill, validator, export, release, issue-closeout, compatibility,
   host-proof, install/update, rename, deletion, design-lock, or migration
   behavior. Record the decision, likely misread, counterweight triage, and next
   move in the caller artifact. This is recorded in the caller artifact and is
   not an invocation of standalone `critique`.
3. **Substantial slice or bundle** — run standalone `critique` with bounded
   fresh-eye subagents once for the meaningful slice or bundle. This covers
   non-trivial workflow, public-skill, prompt, validator, export, release,
   issue-closeout, compatibility, host-proof, install/update, rename, deletion,
   and design-lock decisions.
4. **Final closeout** — for non-trivial goals, use standalone fresh-eye review
   to check cross-slice drift, generated/export sync, disposition of surfaced
   improvements, and non-claims. Do not redo every slice-level review unless a
   new risk boundary appeared after the last review.

## Review Unit

The commit is not the review unit. A slice may include several cheap commits
before one bounded critique, as long as the slice contract, changed files,
expected invariants, proof already run, non-claims, and reviewer questions stay
coherent. A later commit inside the same slice triggers another fresh-eye pass
only when it changes the risk boundary, such as adding a new public skill
surface, validator family, export path, issue-closeout carrier, release surface,
host-proof claim, or irreversible migration. Mandatory premortem follows the same
rule — it fires once per slice-intent boundary, not per commit; see the single
resolution in
[meaningful-slice-cadence](../../../shared/references/meaningful-slice-cadence.md)
*Review Cadence*.

## Slice Packet

For standalone fresh-eye critique, pass a bounded packet instead of the whole
historical goal by default:

- intent and slice boundary
- changed files and owning/generated surfaces
- expected invariants and known non-claims
- tests or proof already run, including proof intentionally skipped
- specific reviewer questions and out-of-scope lines

Counterweight triage stays mandatory: findings should land in the standard bins
(`Act Before Ship`, `Bundle Anyway`, `Over-Worry`, or `Valid but Defer`), so the
caller does not convert every concern into process cost.
