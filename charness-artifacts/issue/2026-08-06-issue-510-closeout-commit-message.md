fix: negotiate public markdown representations

Closes #510
Classification: bug
Carrier: direct-commit; this message is the proposed issue-resolution carrier.

JTBD: A gather operator must be able to persist a public Markdown-capable URL
when its HTML-oriented representation is a login wall, without credentials,
browser actions, or a provider-specific bypass.

Observed problem: The generic public URL route sent only an HTML-oriented
`Accept` header. When the provider offered readable Markdown for the same
public URL, acquisition classified the HTML response as `login-wall` and
stopped without trying the public Markdown representation.

Root Cause: The acquisition plan had no representation-selection stage between
the direct public request and fallback/terminal disposition. The direct IO
header, classifier, policy, and gather consumer therefore treated one failed
representation as a complete access refusal. The first implementation review
also found that a domain-route attempt could hide the direct attempt; the
repaired implementation captures direct attempt identity explicitly and runs
the generic/domain order as direct -> Markdown -> domain.

Debug Artifact: charness-artifacts/debug/2026-08-06-issue-510-markdown-negotiation-debug.md

Implementation: Added the `content-negotiated-markdown` stage and explicit
`Accept: text/markdown` request after an eligible direct login wall or
Markdown-looking URL. The stage reuses the existing classifier and selected
content persistence path, records `representation: markdown` and
`route: content-negotiated-markdown`, leaves failed retries blocked/degraded,
and visibly skips seeded direct fixtures. Added a cohesive negotiation module,
route-plan entry, deterministic HTTP transport fixture, domain-route ordering
regression, and synchronized source/plugin support mirrors.

Siblings: Decision: same-class plain GET in impersonated fetch is diagnostic-
only for this slice; proof: static sibling scan and the deferred follow-up
`gather-routing-provider-discovery`. Decision: the route catalog is the
abstraction-up owner and the generic acquisition stage is the repair owner;
proof: route-plan and domain-route failure tests. Decision: gather persistence
remains an intentional final-consumer boundary; proof: local HTTP fixture
selected Markdown, read the selected trace, and persisted the body.

Prevention: Keep representation selection explicit in the acquisition plan and
attempt trace; require paired success/failure transport fixtures and direct-
attempt identity when adding a new representation or fallback; keep provider,
browser, credentialed, installed-host, and remote proof claims separate from
local deterministic evidence.

Critique: charness-artifacts/critique/2026-08-06-issue-510-markdown-negotiation-resolution-critique.md
Boundary: owned-correctly — public request representation and ordered trace
remain in support/web-fetch, while classifier semantics and gather persistence
remain their existing owners.

Behavior #510: local-only-by-contract — the distinct local HTTP-server
roundtrip first returned an HTML login wall, then observed `Accept:
text/markdown`, selected `content-negotiated-markdown`, and wrote/read back
the extracted Markdown body. The focused route/content/trace suite passed 55
tests, including failed-retry and domain-route-order regressions. No live
provider, installed-consumer, remote CI, or GitHub state is claimed here.

Fresh-Eye Satisfaction: parent-delegated; round 1 found the direct-attempt and
plan-order blocker, round 2 read the repaired surface and returned clean; both
reviewer boundary fingerprints verified clean before parent writes.

AI-provenance: Agent-authored direct-commit carrier; causal review, seam spec,
two bounded fresh-eye rounds, source/plugin sync, focused HTTP roundtrip, and
pre-commit gates are recorded above and in the linked artifacts. The issue
remains OPEN until the one final push and distinct GitHub closeout readback.
