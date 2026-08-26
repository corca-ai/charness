## Resolution — make artifact preflight export-layout aware

JTBD: let a consumer invoke the artifact-surface preflight and receive the
same scaffold shape after Charness public skills are flattened into an export.

Boundary: #637 owns Charness package-layout resolution for registered artifact
shape producers. The source registry remains canonical at `skills/public/...`;
the exported package resolves its flattened `skills/...` producer. The
consumer's own artifact root is not a producer lookup path.

Resolution brief: close the stale source-layout assumption with one shared
resolver and keep invalid package layouts fail-visible instead of silently
falling back to consumer files.

Root cause: the preflight invoked a canonical `skills/public/...` path relative
to the consumer cwd, although exported plugins flatten public skills to
`skills/...` beside the dispatcher.

Debug artifact: `charness-artifacts/goal-runs/724/observations/goal-run-637-artifact-preflight-20260827.md`
records the reproduction, scope receipt, and clean export-only proof.

Siblings: decision: #684 is the duplicate of this defect; proof: the live issue
comment and the export-only fixture distinguish this from the separately owned
retro-planner surface.

Implementation: commit `3d08c6bb238bcf3c0cb713e40123328a9fc7b79f` updates the
canonical dispatcher and checked-in plugin mirror. It resolves canonical or
flattened shape sources, and returns deterministic missing/ambiguous errors
with the candidate paths named.

Prevention: the exact standing target now includes an export-only consumer
fixture covering positive flattened rendering, a missing producer, and
simultaneous canonical/flattened producers. The fixture does not mutate an
installed host.

## Behavior #637

Behavior #637: local-only-by-contract — clean named proof worktree
`proof/issue-637-artifact-preflight-20260827` at target
`3d08c6bb238bcf3c0cb713e40123328a9fc7b79f` passed the exact standing target
(`62 passed`), compile/Ruff/parity checks, and the export-only positive and
negative fixture. This is source/export-layout proof, not installed-host
adoption proof.

## Resolution critique

The original failure was a real installed-layout defect, not a consumer
configuration problem: the dispatcher selected `skills/public/...` relative to
the consumer cwd even though the export contains only flattened `skills/...`.
Resolving from the dispatcher package fixes the ownership boundary without
adding a second registry or changing validator verdicts. Refusing missing and
ambiguous candidates prevents a future package-shape failure from being hidden
by an unrelated consumer tree.

## Explicit non-claims

This resolution does not claim a real installed-host, marketplace, GitHub, or
remote-CI readback; no installed-host mutation was authorized or performed. It
does not claim retro-planner behavior, hosted enforcement, release, push, tag,
or fresh-eye review. The #684 duplicate and the separately owned retro-planner
surface are not silently folded into this closeout. Forced handoff and
micro-slice rituals were omitted by operator direction.

Implementation carrier: `3d08c6bb238bcf3c0cb713e40123328a9fc7b79f`; the issue
body was updated through the #724 Goal Run provider and read back as
`body_verified: true` before this close operation.

Manual fallback reason: operator-directed-manual-close.

Critique: blocked operator-directed implementation path omits forced fresh-eye
review; the clean export-layout evidence and explicit installed-host non-claim
are the intended closeout scope.

AI-provenance: authored by an agent session.
