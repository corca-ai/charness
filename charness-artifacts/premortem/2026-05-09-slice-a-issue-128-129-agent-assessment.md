# Premortem — Slice A: Issues #128, #129, and Agent Assessment Invariant Propagation

Date: 2026-05-09
Decisions under review:

- **#128** — `issue` skill `preflight`/`resolve_adapter`/`resolve-target`/
  `resolve-invocation`/`select` defaulted `--repo-root` to the script's repo
  root, which equals the installed plugin cache when invoked through
  `$SKILL_DIR`. Defaults flipped to `Path.cwd()` so the consumer repo's
  adapter is searched. SKILL.md preflight bootstrap example now passes
  `--repo-root .` for explicit consistency.
- **#129** — HITL chunk Agent Assessment + Recommended Disposition behavior
  coverage: prose existed but agent regressed mid-session. New self-check lib
  function (`check_chunk_contract` in `scripts/hitl_review_artifact_lib.py`)
  plus `skills/public/hitl/scripts/check_chunk_contract.py` runtime helper.
- **Item 10.4 (handoff Next Session)** — propagate the Agent Assessment +
  Recommended Disposition invariant beyond HITL chunk presentation: new
  shared reference at `skills/shared/references/agent-assessment-invariant.md`,
  cited from `quality` `NON_AUTOMATABLE` HITL Handoff and from `premortem`,
  `spec`, `narrative`, `init-repo`, `hitl` SKILL.md References lists. HITL
  `chunk-contract.md` Applied Rewrite Review extended to require the
  invariant; new Full Target Review subsection added.

## Success Criteria

- `issue_tool.py preflight` invoked from a consumer repo through `$SKILL_DIR`
  reads adapter from the consumer repo, not from the installed cache.
- `check_chunk_contract` blocks chunk text that asks for a decision but lacks
  Agent Assessment or Recommended Disposition markers; passes complete chunks
  and skips informational text without a decision prompt.
- 7 chunk-presentation surfaces cite the new shared invariant ref.
- All quality gates and the full pytest sweep stay green.
- Plugin manifests stay synced (no drift between `skills/public/` and
  `plugins/charness/skills/`).

## Out of Scope

- Marker-set expansion for `check_chunk_contract` to cover decision-shaped
  chunks that use neither `?` nor "Decision Needed" (e.g., "Approve or
  revise."). Recorded as a Valid-but-Defer follow-up.
- Inline anchoring of the invariant into HITL SKILL.md step 12 prose. Cite
  exists in References list; deferred to a future micro-edit.
- Cautilus evaluator scenario for #129 (Cautilus adapter is `disabled`;
  closeout proof is the deterministic test pattern).
- `issue resolve-target`/`resolve-invocation`/`select` were also flipped to
  cwd-default for symmetry with `preflight`. Bundled because the change is
  trivially safe (no in-repo callers depend on the old script-root default,
  SKILL.md examples already pass `--repo-root .` for resolve-invocation).

## Angles + Counterweight

Bounded angle subagent + counterweight delegated to the parent task agent
under the repo `Subagent Delegation` clause. Triage:

- **Act Before Ship**: none.
- **Bundle Anyway**: a one-line scope note in the commit body so the wider
  cwd-default change in `issue_tool.py` (beyond the strict `preflight`
  scope of #128) reads honestly.
- **Over-Worry**: cwd default breaks other callers (no in-repo callers rely
  on the old default); heuristic blocks legitimate informational chunks
  (the helper is an opt-in self-check, not a hard gate); shared ref is
  premature abstraction (it consolidates language repeated across 6 surfaces
  and is enforced by a citation-chain test).
- **Valid but Defer**: marker robustness gap in `check_chunk_contract`
  (missing decision-shaped chunks without `?`/"Decision Needed"); HITL
  SKILL.md step 12 inline citation into the shared ref.

## Recurrence Prevention

- `test_agent_assessment_invariant_is_cited_across_chunk_surfaces` enforces
  the citation across all 7 affected surfaces — prevents prose-only revert.
- `check_chunk_contract.py` gives the HITL agent a concrete self-check it
  can run before presenting a chunk; not a hard gate but a guardrail that
  surfaces the same regression #129 reported instead of silently regressing.
- Plugin manifest sync caught early via `validate_packaging_committed`
  failure during the slice; fixed with `sync_root_plugin_manifests.py`.

## Deliberately Not Doing

- Adding a runtime self-check to every other surface (premortem/spec/etc).
  The shared reference + cite is the contract; runtime enforcement lives on
  the surface that actually stages chunks (HITL).
- Splitting #128 from #129/Item 10.4 into separate commits. They are small
  enough that one commit per slice is cheaper than three commits with
  per-slice premortems.
