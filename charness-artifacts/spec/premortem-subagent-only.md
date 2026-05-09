# Problem

`charness` currently says that `critique` is subagent-canonical and that
same-agent fallback must not replace it, but some checked-in caller/core text
still leaves a cheaper local interpretation available. That ambiguity makes the
agent more likely to skip or relabel the real fresh-eye review instead of
actually running it.

# Current Slice

Lock `critique` to one meaning in the checked-in public contract:

- `critique` means a fresh bounded subagent review only
- there is no local/same-agent `critique` variant
- caller skills must report `Critique: executed|skipped|blocked`
- repo-owned validation must fail if the local-variant wording drifts back in

# Fixed Decisions

- `critique` is definitionally subagent-only.
- `bounded` constrains scope and time box, not execution mode.
- routine slices do not need critique at all; if critique is needed, it must
  use the canonical subagent path.
- blocked subagent capability stays blocked; caller skills must not rewrite that
  state as a local substitute review.
- this slice updates `critique`, `impl`, and `release` first.
- this slice adds validator coverage for the locked wording.

# Probe Questions

- Should `spec`, `quality`, `handoff`, and `narrative` converge on the same
  `executed|skipped|blocked` reporting language in the next slice?
- Should a repo-owned planner decide when `critique` is required before closeout?
- Should `run_slice_closeout.py` eventually gate on a critique planner the same
  way it already gates on cautilus proof?

# Deferred Decisions

- blanket rule: "every review-worth-doing must become critique"
- global review taxonomy cleanup beyond the first caller skills
- critique artifact schema and planner integration

# Non-Goals

- redesigning all public skills in one pass
- introducing a full critique-required trigger planner in this slice
- changing the standing validation tier assignments

# Deliberately Not Doing

- keeping a "local critique" escape hatch for cheap fallback
- renaming same-agent review to another euphemism inside `critique`
- waiting for planner work before removing the contradictory local wording

# Constraints

- keep the public-core language concise
- prefer validator-backed wording over chat-only policy
- do not claim actual host-side critique execution proof that this slice does
  not add yet

# Success Criteria

- `skills/public/critique/SKILL.md` no longer allows a local/same-agent
  critique reading
- `skills/public/impl/SKILL.md` and `skills/public/release/SKILL.md` report
  critique as `executed`, `skipped`, or `blocked`
- repo-owned validation fails if the locked contract wording drifts
- reviewed dogfood evidence reflects the changed public contract

# Acceptance Checks

- `python3 scripts/check_skill_contracts.py --repo-root .`
- `python3 scripts/validate_skills.py --repo-root .`
- `python3 scripts/validate_public_skill_dogfood.py --repo-root .`
- `python3 scripts/check_doc_links.py`

# Critique

- Likely wrong next move: delete the local wording but leave caller closeout
  ambiguous, so future edits reintroduce the same loophole under a new name.
- Tightening move for this slice: lock both the core definition and caller
  reporting language, then pin them in validation.

# Canonical Artifact

- `charness-artifacts/spec/critique-subagent-only.md`

# First Implementation Slice

1. Rewrite `critique` core wording so the concept is subagent-only.
2. Update `impl` and `release` to report `Critique: executed|skipped|blocked`.
3. Extend repo-owned validation to pin the new contract and forbid the old
   local-variant wording.
4. Refresh reviewed dogfood evidence for `critique`, `impl`, and `release`.
