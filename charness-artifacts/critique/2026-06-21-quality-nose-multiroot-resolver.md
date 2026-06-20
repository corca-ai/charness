# Code Critique — nose 0.14.0 multi-root clone resolver (chunk-2)

- Target reference: `code-critique` (quality-contract change)
- Fresh-Eye Satisfaction: parent-delegated (3 angle subagents + 1 counterweight, high-leverage)

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=opus (Claude Code host resolution of high-leverage; the critique adapter records the Codex-host mapping model=gpt-5.5, reasoning_effort=medium, service_tier=priority)
- Host exposure state: requested_fields_sent
- Application state: model=opus sent to all 4 bounded subagents (3 angles + counterweight) via the Agent tool; the host does not echo resolved spawn fields, so application is unverified-by-carrier (not claimed host-confirmed)

## Diff Scope

`nose_report_lib.collect_families` switched from a per-root `nose query` loop
(merge+dedup) to a single nose 0.14.0 `--root` multi-root query, so the quality
clone gate + advisory analyze the whole scope as one corpus. `build_query_command`
now takes `paths: list[str]` (emits `--root P` per root). Both id-set baselines
re-baselined 491→525 (Δ+120/-86, `--confirm-baseline-delta`), lockstep. Docstrings,
`references/dup-ratchet.md`, and tests updated.

## Angles

- **Weinberg (diagnostic):** is the cause located; does the 51-span coverage drop hide a regression; is the re-baseline correct?
- **Gawande (operational):** fail-closed contract; single-corpus timeout; empty-paths edge.
- **Jackson (problem framing):** did a "collapse the loop" task quietly become a "change what the gate enforces" change; is it owned/legible?

## Findings → Counterweight four-bin triage

**Act Before Ship (applied):**
- Record the 491→525 / `--confirm-baseline-delta` override rationale durably
  (Jackson) — folded into this commit body + a one-line scope-model note in
  `references/dup-ratchet.md`. Without it a future `git blame` of the 196-id
  baseline churn must reverse-engineer the model switch.

**Bundle Anyway (applied):**
- Note the 51-span / 3-file coverage drop (Weinberg) — benign `main()`/boilerplate
  whose marginal within-root sibling is absorbed into a richer cross-root cluster;
  net is +186 cross-root spans. Recorded in the commit body.
- One-line single-corpus timeout note at `NOSE_TIMEOUT_SECONDS` (demoted Gawande #2).
- `build_query_command(paths=[])` now raises (Gawande #4) — fail loud instead of a
  silent wrong-scope default scan; callers still guard with `or DEFAULT_PATHS`.
- Single-root `--root` + empty-paths tests added (Weinberg #6) — closes the
  untested "single root == positional" docstring claim.

**Over-Worry (no change):**
- Gawande #2 "timeout fail-OPEN regression" — **premise verified FALSE**: the old
  per-root loop also set whole-result `status:"error"` on any single-root error
  (old line 147), degrading the whole gate identically. Behavior unchanged.
- Jackson #5 "global grouping hurts the intentional-vs-new judgment" — the
  cross-root visibility IS the approved goal; per-family intentional text is
  unaffected by clustering scope.

**Valid but Defer:**
- None outstanding (the deferred single-root test was bundled instead).

## Deliberately Not Doing

- A consumer-overridable nose timeout env knob — 180s is ample for realistic
  scopes and the fail mode is advisory (fail-closed), so it stays a documented
  consideration, not new config surface.

## Next Move

Sync, verify, commit direct-to-default with the 491→525 rationale + coverage-drop
note in the body. No GitHub issue (this is an operator-chosen enhancement, not an
issue resolution).
