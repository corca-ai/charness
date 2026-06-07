# #324 Contract-Gap Analysis — Preserve External-Source Context in Issue Workflows

Tracking analysis for GitHub issue #324 (bug/operations). This is a
**workflow-design gap** (a missing invariant), not a behavior defect, so the
bug-class `debug` falsifiable-hypothesis mandate is satisfied by this explicit
opt-out: `debug: n/a — design-gap`.

Slice: B1a. Feeds B1b (contract + fixture) and B1c (release stage).

## Required Invariant (from #324)

When an issue is filed from an external source (Slack / Notion / Google
Workspace / browser-gathered page / any external conversation source), the issue
artifact must preserve the original user context in **one of two auditable
forms**:

1. relevant **original source text**, verbatim enough that a future resolver
   understands the requested intent without current session memory; **or**
2. a **stable source identity/link plus an explicit obligation** that the
   resolving agent must re-read / verify that source before resolving or
   closing.

Plus: closeout must **check** source preservation before treating the issue as
ready to close; if the source is **inaccessible** during resolution the closeout
must **say so and stop or classify the proof as degraded**; the invariant must be
**portable** (Charness owns it; adapters such as a Ceal Slack gather may satisfy
it).

## Current State

- `references/issue-shaping.md` + `references/closeout-discipline.md` require a
  `## Source` **identity** block (canonical URL, gathered-artifact path, access
  mode, freshness) when the originating context is external.
- `issue_create.py` writes the body and checks **byte-identity** of the stored
  body only. No section/schema is enforced.
- `issue_verify_closeout_body.py::_missing_ledger_fields` checks the
  classification ledgers (jtbd / root_cause / debug_artifact / siblings /
  prevention, etc.), `_missing_close_keywords`, and the resolution-critique
  header. **No source field is consulted.**
- `issue_validate_closeout_draft.py` reuses `verify_closeout`, so it inherits
  the same blind spot.

## Gap Table

| # | Gap | Where | Fix direction (B1b) |
| --- | --- | --- | --- |
| G1 | Schema captures source **identity**, not **preserved intent**. Form (1) verbatim text is actively discouraged ("do not paste the full source content"); form (2) re-read obligation has **no field**. | `issue-shaping.md`, `closeout-discipline.md` | Provider-neutral source-context section encoding **either** preserved text **or** an explicit re-read obligation. |
| G2 | No closeout validator warns/blocks when an external-source issue closes lacking **both** preserved context **and** a re-read obligation. | `issue_verify_closeout_body.py`, `issue_verify_closeout.py`, `issue_validate_closeout_draft.py` | Add a source-preservation check to the closeout body validators (draft + verify). |
| G3 | No degraded-source-proof path: an inaccessible source at resolve time forces nothing. | closeout schema/check | Allow an explicit `degraded` source-proof classification that the closeout must declare (and that the validator recognizes as a named, non-silent state). |
| G4 | The external-vs-internal discriminator is prose-only ("did the originating context live outside this repo"); nothing carries an explicit external-source signal the validator can key on, so the check cannot know when preservation is required. | body/ledger | Explicit external-source marker in the body the validator reads; internal-only issues stay exempt. |
| G5 | The requirement is charness prose tied to `gather`, not a portable invariant an adapter can target. | references | Frame as `axis: external-source-provider`; Slack is one adapter instance, **not** the schema. Charness owns the section + check; adapters satisfy it. |

## Design Implications for B1b

- One provider-neutral **source-context section** (heading + a small set of
  fields) that is satisfied by any of: preserved text (form 1), or a stable
  source identity + a re-read obligation (form 2), or an explicit `degraded`
  declaration (G3) when the source is inaccessible.
- A **closeout body check** (pure, no IO) added to the body-helper layer so both
  `verify-closeout` and `validate-closeout-draft` inherit it; it only triggers
  when the body marks the issue as externally sourced (G4), keeping internal
  issues exempt.
- The check is **warn/block**, matching #324's "treats missing source
  preservation as a workflow risk, not optional prose style."
- Reference prose updated so form (1) is **allowed** (the current "do not paste"
  line is the direct contradiction), the re-read obligation gets a named field,
  and the invariant is stated provider-neutrally.

## Non-Claims (B1a)

- No code written yet; this is the gap map only.
- Slack is named as one example provider, **not** the contract — the schema is
  provider-neutral per G5.
