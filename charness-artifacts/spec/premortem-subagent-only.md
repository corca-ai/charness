# Problem

`charness` currently says that `premortem` is subagent-canonical and that
same-agent fallback must not replace it, but some checked-in caller/core text
still leaves a cheaper local interpretation available. That ambiguity makes the
agent more likely to skip or relabel the real fresh-eye review instead of
actually running it.

# Current Slice

Lock `premortem` to one meaning in the checked-in public contract:

- `premortem` means a fresh bounded subagent review only
- there is no local/same-agent `premortem` variant
- caller skills must report `Premortem: executed|skipped|blocked`
- repo-owned validation must fail if the local-variant wording drifts back in

# Fixed Decisions

- `premortem` is definitionally subagent-only.
- `bounded` constrains scope and time box, not execution mode.
- routine slices do not need premortem at all; if premortem is needed, it must
  use the canonical subagent path.
- blocked subagent capability stays blocked; caller skills must not rewrite that
  state as a local substitute review.
- this slice updates `premortem`, `impl`, and `release` first.
- this slice adds validator coverage for the locked wording.

# Probe Questions

- Should `spec`, `quality`, `handoff`, and `narrative` converge on the same
  `executed|skipped|blocked` reporting language in the next slice?
- Should a repo-owned planner decide when `premortem` is required before closeout?
- Should `run-slice-closeout.py` eventually gate on a premortem planner the same
  way it already gates on cautilus proof?

# Deferred Decisions

- blanket rule: "every review-worth-doing must become premortem"
- global review taxonomy cleanup beyond the first caller skills
- premortem artifact schema and planner integration

# Non-Goals

- redesigning all public skills in one pass
- introducing a full premortem-required trigger planner in this slice
- changing the standing validation tier assignments

# Deliberately Not Doing

- keeping a "local premortem" escape hatch for cheap fallback
- renaming same-agent review to another euphemism inside `premortem`
- waiting for planner work before removing the contradictory local wording

# Constraints

- keep the public-core language concise
- prefer validator-backed wording over chat-only policy
- do not claim actual host-side premortem execution proof that this slice does
  not add yet

# Success Criteria

- `skills/public/premortem/SKILL.md` no longer allows a local/same-agent
  premortem reading
- `skills/public/impl/SKILL.md` and `skills/public/release/SKILL.md` report
  premortem as `executed`, `skipped`, or `blocked`
- repo-owned validation fails if the locked contract wording drifts
- reviewed dogfood evidence reflects the changed public contract

# Acceptance Checks

- `python3 scripts/check-skill-contracts.py --repo-root .`
- `python3 scripts/validate-skills.py --repo-root .`
- `python3 scripts/validate-public-skill-dogfood.py --repo-root .`
- `python3 scripts/check-doc-links.py`

# Premortem

- Likely wrong next move: delete the local wording but leave caller closeout
  ambiguous, so future edits reintroduce the same loophole under a new name.
- Tightening move for this slice: lock both the core definition and caller
  reporting language, then pin them in validation.

# Canonical Artifact

- `charness-artifacts/spec/premortem-subagent-only.md`

# First Implementation Slice

1. Rewrite `premortem` core wording so the concept is subagent-only.
2. Update `impl` and `release` to report `Premortem: executed|skipped|blocked`.
3. Extend repo-owned validation to pin the new contract and forbid the old
   local-variant wording.
4. Refresh reviewed dogfood evidence for `premortem`, `impl`, and `release`.
