## Resolution — route declared specialized release lanes

JTBD: prevent generic release planning from turning a missing generic route
into a false repository verdict when a repository has an explicit specialized
release lane.

Boundary: Charness owns the repo-declared lane contract and the planner's
read-only routing output. Hosted workflow/tag topology, release approval, and
publication remain outside this issue.

Resolution brief: add one structured adapter input and route through its exact
lane identity while preserving the existing generic behavior when no lane is
declared.

Implementation: `3101eeceae0640cc7f36418293c0e45c08bf6197` adds
`specialized_release_lanes` to the release adapter contract, validates its
four required string fields, and emits `route_specialized_release_lane` for a
single lane or `select_specialized_release_lane` for multiple lanes. The
planner reports the declared command and performs no release mutation.

Prevention: keep specialized release routing explicit and structured. Do not
infer hosted workflow or tag behavior from a generic adapter failure, and do
not let an unrecognized declaration become a silently inert key.

## Behavior #667

Behavior #667: `local-only-by-contract` — the clean named-branch proof
returned `28 passed`
through the standing runner and `34 passed` in the direct focused suite. The
specialized fixture returned the exact route action with its id, workflow,
tag pattern, and command; it emitted no publish packet and left the manifest
unchanged. The no-lane fixture retained the generic planner behavior.

Probe record #667: local-only-by-contract

## Resolution critique

The repair keeps ownership narrow: a local declaration makes the route legible,
but the planner does not pretend that the workflow exists on a hosted service,
that its tag trigger is active, or that the release is approved. Multiple
declared lanes remain an explicit operator choice instead of a hidden guess.

## Explicit non-claims

This closeout does not claim hosted workflow discovery or enforcement, tag
execution, release approval or publication, consumer-repository adoption,
remote CI, push, tag, installed-host behavior, or fresh-eye review. Changed-line
proof was not used as a universal blocking gate. Forced fresh-eye, handoff, and
micro-slice rituals were omitted by operator direction.

Implementation carrier: `3101eeceae0640cc7f36418293c0e45c08bf6197`.
The issue body was updated through the #724 Goal Run provider and must be read
back as `body_verified: true` before close.

AI-provenance: authored by an agent session.

Manual fallback reason: operator-directed-manual-close.

Critique: blocked operator-directed implementation path omits forced fresh-eye
review; the bounded local contract evidence and explicit external non-claims
are the intended closeout scope.
