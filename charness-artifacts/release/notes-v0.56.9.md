# charness v0.56.9

**Scope: additive review doctrine + inventory refresh. No behavior change, no migration.**

## Quality / critique review doctrine (resolves #405)

The `quality` Behavior lens gains two named review lenses, and the shared
fresh-eye review reference gains a delegation-design note. These are advisory
review prompts — no new command, adapter, gate, or install surface.

- **verification-channel fitness** (`quality` Behavior lens): a runtime "proof"
  only counts when collected in a channel that can actually *exhibit* the failure
  under review. A charset/encoding/rendering bug is invisible to a UTF-8 terminal,
  so prove it in a charset-respecting client or by rendering as a user would, and
  read each response field (`status`, `content-type`, `charset`, `cache`) against
  the spec instead of pattern-matching "looks right."
- **guard-propagation across seams** (`quality` Behavior lens): when a fix
  escapes/guards/converts/sets-a-header at one boundary crossing, enumerate
  *every* sibling crossing of that hazard class in the diff and apply the guard as
  an invariant, not a local patch.
- **Distinct Named Lenses** (`fresh-eye-subagent-review`): when spawning more than
  one bounded reviewer over the same artifact, assign each a distinct,
  explicitly-named lens rather than N generic reviewers — lens diversity catches
  failure modes reviewer redundancy cannot.

## Inventory refresh

- Regenerated the `find-skills` canonical inventory artifact (support-skill list
  count corrected 7 → 4) that a prior session left uncommitted.

## Upgrade

No migration required. Update via the adapter path (`charness update`). Because
this is additive review doctrine, the change surfaces the next time `quality` or a
fresh-eye review runs; there is no runtime/behavior change to adopt.
