# Retro Phase-Aware Efficiency Design

Date: 2026-05-25

## Scope

Implement #217 in upstream Charness: `retro` must not label broad exploration as
waste until it has checked phase intent and the transition from exploration into
triage, implementation, and verification.

#218 is relevant evidence but not the first implementation target. Its Codex log
cost map should be treated as a host-specific evidence producer that feeds the
portable interpretation rules, not as the rule that decides waste.

## Fixed Decisions

- Add portable phase-aware efficiency rules to `retro`.
- Keep session retros ergonomic: host-log or cost-map evidence can sharpen a
  claim, but ordinary session retros do not require it.
- Keep per-run scope in the retro narrative or command flags. Do not add
  session-specific narrowing policy to adapters.
- Defer upstreaming the Codex cost-map analyzer until the interpretation
  contract is in place.

## Acceptance Checks

- A retro with user-intended broad discovery does not recommend premature
  narrowing as the main fix solely because exploration was broad.
- Waste attribution names the phase where effort was lost and marks inferred
  phase claims with confidence when evidence is not direct.
- Exploration output is a candidate list; triage output is a locked list of
  `fix now`, `deferred`, `needs user call`, and `false positive`.
- After triage lock, new findings are treated as scope reopen decisions or
  deferred notes unless the user changes scope.
- Host-specific audit signals remain evidence pointers and preserve
  measured/proxy/unavailable semantics.

## Deliberately Not Doing

- No full machine-readable phase schema in this slice.
- No automatic Codex analyzer invocation on token-waste prompts in this slice.
- No adapter field for one session's intended breadth or thread selection.
