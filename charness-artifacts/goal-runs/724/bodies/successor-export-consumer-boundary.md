# Successor — Exported consumer paths remain self-insufficient

## Origin and disposition

Split from #634 after the shipped bootstrap dependency-contract arm was
verified. The successor owns the remaining consumer-boundary residue; #634 must
not remain an umbrella that makes a partial repair look like full export
self-sufficiency.

## Observed residue

The current #634 inventory identifies three bounded shapes that remain live
after `packaging/bootstrap-python.json` and
`packaging/bootstrap-requirements.txt` began shipping with the installer:

- exported documentation and adapter data still contain consumer-facing
  `python3 scripts/<name>.py` instructions that resolve against the consumer
  repository rather than the plugin layout;
- three exported shell gates do not reject the wrong repository root even though
  sibling gates already do; and
- exported validators read `docs/public-skill-validation.json` and
  `docs/public-skill-dogfood.json`, which are consumer/repo-root data readers
  not shipped in the export.

These are separate from the already-fixed dependency contract and from closed
instances #618, #670, and #679. The remaining bare third-party imports are an
inventory/non-claim here until a documented-entrypoint scope and owner are
chosen.

## Owned acceptance

Define one export/consumer boundary contract for these three shapes, identify
the owning writer or runtime for each path, and make the smallest verifiable
repair or explicit typed advisory. The proof must exercise a clean export-only
consumer fixture, not a repo copy that manufactures `packaging/` or consumer
docs. Export generation and release-time host-layout validation remain separate
surfaces.

## Non-claims

This successor does not claim scheduler behavior, hosted or installed-host
enforcement, consumer repository adoption, remote CI, release publication, or
that every bare import in the full export is a documented entrypoint defect.
The issue is an implementation candidate, not evidence that the residue is
already repaired.

AI-provenance: authored by an agent session.
