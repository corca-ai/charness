# Boundary Ownership Brief

The reviewer-facing producer/consumer question set for any change that might
cross an ownership boundary. A code/spec reviewer runs it during `critique`, and
an `impl` review pass runs it under its `boundary honesty and ownership` lens.

This brief is portable and **taxonomy-free**: it never names a repo's concrete
owner surfaces. Charness owns the *question* and the *disposition schema*; the
consumer repo owns the *taxonomy, labels, and cross-surface probe* — supplied
through its adapter, never through this brief.

## The Four Questions

Ask these before accepting a change that touches shared, generic, or
cross-surface code:

1. **Producer / consumer.** Who *produces* this fact or state, and who is its
   *final consumer*? Name both.
2. **Render vs. produce.** Does this change *render* an existing fact, or
   *produce / own* new state? If it produces state, is *this* surface the right
   owner of it?
3. **Move vs. encode.** If the behavior belongs to another surface — its state,
   an active commitment, or producer-owned metadata — is the change *moving*
   producer-owned data plus generic rendering, or *encoding* the special case
   locally (e.g. a caller-specific branch baked into a generic reducer or shared
   routine)?
4. **Escalate.** Would this encode consumer- or caller-specific knowledge into
   reusable/shared code? If so, the honest move is an issue/spec, not a local
   point-fix that a passing unit test would make look finished.

A passing unit test at the nearest prompt/reducer/test surface is *not* evidence
the ownership boundary was respected — a symptom can be caught deterministically
in the wrong layer. Question 2/3 is where that failure hides.

## The Disposition It Feeds

The review records a boundary-ownership disposition (its *presence* and typed
*verdict* are floored; its correctness stays reviewer judgment):

- `Producer:` — who owns/produces the fact or state.
- `Consumer:` — the final consumer.
- `Owning surface:` — the surface that should own the change (a repo-defined
  label; this brief does not enumerate them).
- `Verdict:` — one of:
  - `single-surface` — no cross-surface ownership concern arises.
  - `owned-correctly` — crosses surfaces, but each fact is produced/consumed by
    its correct owner.
  - `moved-to-owner` — a misplaced fact was relocated to its producer-owner,
    plus generic rendering.
  - `escalated-to-issue-spec` — the correct owner is out of this change's scope;
    escalated to an issue/spec rather than encoded here.

## Self-Assertion vs. A Configured Probe

Without a repo-owned cross-surface probe, `single-surface` is *self-asserted* —
only as strong as the reviewer's judgment. When the consumer repo declares a
cross-surface probe (adapter-owned paths/globs) and the change matches it, a bare
`single-surface` verdict is rejected: the review must resolve to
`owned-correctly` / `moved-to-owner` / `escalated-to-issue-spec`. The probe is
the objective override for the case where a change *looks* local but touches a
producer-owned surface.
