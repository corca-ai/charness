# Resolution Critique — #324 Source-Preservation Contract

Binds the bounded fresh-eye critique to the resolution of GitHub issue #324
("Preserve original external-source context in issue workflows"). Carrier:
the release-stage commit (#324 closeout). Classification: feature (a missing
invariant / new portable contract, not a behavior defect — `debug: n/a —
design-gap`).

## Reviewer Provenance

Bounded fresh-eye `critique` subagent (general-purpose, read-only), run this
session in the shared parent worktree against the staged slice. Base
(pre-slice) commit `feeeac99`. The reviewer probed the parser empirically
(10+ markdown shapes), the external-source discriminator, the degraded-form
bypass, portability, and prose/code consistency.

## Verdict

**Ship-as-is.** No blockers. The check is correct, provider-neutral, inherits
the established `_body_fields` parser conventions (not a novel trap), and the
prose contract matches the code behavior.

## Blockers

None.

## Over-Worry (raised, probed, ruled non-blocking)

- **Fenced-code excerpt is a false negative.** `_strip_code_fences` deletes
  fenced content before `_body_fields` parses, so a `Source text:` followed by
  a ```` ```text ```` block parses empty. Non-blocking: pre-existing parser
  convention shared by every ledger field (JTBD/Root cause/…), and the prose
  actively steers to `>`-quoted blockquote (`closeout-discipline.md`
  "Quote it with `>` prefixes …" + the `Source text: |` indented format
  suggestion), not fences.
- **Bold field names (`- **Source origin:** slack`) parse as non-fields.**
  Pre-existing `_FIELD_RE` behavior shared with all ledger fields; no repo
  example uses bold for these fields. Low incidence.
- **Degraded form (G3) is trivially declarable.** An agent could always
  declare `Source degraded reason:` to dodge real preservation. Non-blocking by
  design: this is the explicit presence-gate philosophy (a presence gate, not a
  content classifier; reviewer/human judges substance). A degraded declaration
  is auditable and visible — exactly #324's "say so and classify as degraded"
  bar. Making it a classifier would contradict the design intent.
- **Discriminator evasion: a real external issue with no `Source origin:` is
  silently exempt.** Accepted by design (invariant #1): externality is
  self-declared; forcing every issue to prove non-externality would over-block
  the internal majority. The creation-side `--require-external` flag is where an
  operator asserts externality.
- **Over-block of a legitimate internal issue:** none found. No-marker → no-op
  is the dominant path; internal closeout tests stay green (32/32).

## Consistency / Portability

Prose (`closeout-discipline.md`, `issue-shaping.md`, `SKILL.md`) matches code:
three forms, `Source origin:` marker, `axis: external-source-provider`,
blockquote guidance. No issue-number anchor leaks into the standing skill
package (ergonomics gate clean). Mirror surfaces are byte-identical to owning
source. Slack appears only as a fixture/example, never in the schema.

## Prevention

The repeat trap this resolution itself avoided — baking the issue number into
the standing skill prose — is already enforced by `validate_skill_ergonomics`
(`issue_anchor_in_core` / `portable_package_issue_anchor`). Provenance is kept
in tracking docs (this critique, the dogfood freeze, the commit body), not in
the portable skill surface.
