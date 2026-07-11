# Charness Handoff

## Workflow Trigger

- Pickup with no explicit task invokes `charness:handoff`; a bare `/handoff`
  runs chunked routing over this baton plus live issues.

## Current State

- For #433/#436, distinguish shipped behavior from tracker lifecycle and admit
  new issue-driven work only from a live reproduction or an explicit lifecycle
  decision; unrelated explicit user tasks retain their own authority.
- v0.66.4 is publicly released at commit/tag `233dc25b`; public evidence is
  recorded by `d1a2b92b`. Fresh-checkout probes, release quality, HTTPS content,
  installed version 0.66.4, and 13/13 doctor checks passed.
- The observed SLOC inventory writer is now sync-owned. Mutation coverage emits
  its resolved base/path plus a strict copyable consumer command; final reuse
  proof returned `blocking=[]` without recollection.
- Unfiltered quality runs record mode-specific aggregate runtime best-effort.
  Coverage-selection and aggregate-runtime tests now have cohesive modules.
- Release real-host proof subscribes to `external-tool-control-plane`; unrelated
  derived plugin scripts no longer trigger the seven-step real-host proof
  checklist. This release did not match that host-sensitive trigger, while its
  separate public HTTPS/fresh-checkout/install verification still ran.
- GitHub issues #433 and #436 remain OPEN by explicit non-close boundary.
  #433's carrier preflight behavior was already fixed in `041aa380`; #436's
  observed SLOC writer is fixed, but no exhaustive all-writer claim was made.

## Next Session

1. Read the live bodies/comments for #433 and #436 before choosing work. Treat
   OPEN tracker state and unresolved behavior as separate facts.
2. If continuing #436, audit only concrete remaining tracked writers. Do not
   repeat the completed SLOC phase move or add a generic detector without an
   observed escape.
3. If continuing #433, first reproduce a carrier/preflight failure against the
   shipped helper. Do not duplicate `041aa380` from issue state alone.
4. Closing either issue is a separate irreversible action; require explicit
   authority and issue-workflow behavioral closeout.

## Discuss

- Whether #433/#436 should now move through tracker closeout, remain open for
  broader acceptance, or receive a narrowed residual statement.
- Future host-sensitive tool files must be added explicitly to the narrow
  external-tool surface; current proof does not infer dependencies dynamically.

## References

- [round-three goal](../charness-artifacts/goals/2026-07-12-north-star-autonomous-two-hour-release-round-3.md)
  · [release](../charness-artifacts/release/latest.md)
  · [quality proof](../charness-artifacts/quality/2026-07-12-round3-v0664-release-readiness.md)
  · [retro](../charness-artifacts/retro/2026-07-12-north-star-autonomous-two-hour-release-round-3-retro.md)
  · [recent lessons](../charness-artifacts/retro/recent-lessons.md)

- Refresh kept: #433/#436 lifecycle boundaries and the explicit future-file
  nonclaim for `external-tool-control-plane`.
- Refresh non-claims: no issue closure, exhaustive writer audit, dynamic
  dependency discovery, Cautilus evaluation, or non-GitHub release proof.
