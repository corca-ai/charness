# Mutation Validity Fix Critique

Date: 2026-05-16
Scope: Cosmic Ray mutation score validity fix for issue 167.
Fresh-eye status: blocked by host-level delegation policy in this session.

## Likely Misread

- Treating the new 85.0% score as pure test strength would be misleading unless
  the skipped mutant class is explicit. The skipped class is annotation-only
  function signature unions, not arbitrary survived mutants.
- Broadening to all `tests/control_plane` improves validity but also increases
  scheduled runtime. The runtime remains within the workflow timeout locally,
  but the next GitHub run is still the provider proof.

## Counterweight

- Do not lower the threshold to hide the first-run failure; the local full run
  passes 60% after improving the evaluation surface.
- Do not filter all `BitOr` mutants globally; the implemented filter is scoped
  to function annotation union lines so future real bitwise behavior mutants
  can still count.

## Closeout

- Keep issue 167 open until a scheduled or manual GitHub Actions run on main
  verifies the pushed workflow.
