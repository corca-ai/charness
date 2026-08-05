fix: normalize auto-derived gather slugs

Closes #509
Classification: bug
Carrier: direct-commit; this message is the proposed issue-resolution carrier.

Jtbd: A gather operator must be able to persist a public URL record when the
URL path contains uppercase, percent-encoded spaces, or non-ASCII characters,
without supplying a manual slug or receiving a writer-validation failure.

Observed problem: When `--slug` was omitted, the URL
`https://wiki.g15e.com/pages/AOP%20and%20CSS.md` produced the auto-derived slug
`wiki-g15e-com-pages-AOP-20and-20CSS-md-e0a17463`. The dated-record writer
rejects uppercase and percent-encoded characters, while the explicit slug
`g15e-aop-css` path succeeded.

Root Cause: `gather_public_url.py` preserved URL-path case and percent escapes
when deriving the implicit slug, then passed that value to the writer's strict
lowercase ASCII slug validator. The producer and consumer accepted different
alphabets, so the default path could fail after acquisition had succeeded.

Debug Artifact: charness-artifacts/issue/2026-08-06-issue-509-causal-review.md

Implementation: `skills/public/gather/scripts/gather_public_url.py` and its
checked-in plugin mirror now percent-decode and lowercase the URL path before
the safe ASCII transform. URL-derived path segments that are not ASCII
alphanumeric become hyphens, while the URL SHA-256 digest remains unchanged,
so the writer receives a valid stable slug without changing source identity.

Siblings: Decision: same bug, fix now — the source helper and checked-in plugin
mirror share the auto-slug producer and must remain byte-identical. Proof:
`cmp -s` passed, and the focused gather/web-fetch suite executed both the
reported uppercase/encoded URL and an encoded non-ASCII URL without an explicit
`--slug`, then read both dated records back. Decision: intentional writer
boundary, diagnostic-only for this slice — explicit user slugs remain governed
by the writer's existing validator, and the URL digest remains the collision
identity. Proof: the premise check accepted the normalized slug through the
writer before implementation; no writer policy change was needed.

Prevention: Keep auto-derived slug producers aligned with the dated-record
writer's accepted alphabet; retain omitted-slug execute/readback fixtures for
encoded uppercase and non-ASCII paths; keep source/plugin equality and the
focused mutation-covered route suite in the local closeout.

Boundary: owned-correctly — URL identity and default-slug production remain in
the public gather helper, strict filename validation remains in the dated
record writer, and source/plugin equality remains the packaging seam.

Critique: charness-artifacts/critique/2026-08-06-issue-509-resolution-critique.md

Behavior #509: local-only-by-contract — a separate direct CLI execute/readback
run, seeded with a pre-captured response, wrote
`2026-05-16-wiki-g15e-com-pages-aop-and-css-md-e0a17463.md` without `--slug`,
and the record read back with `Final Status: success`. This is not a GitHub
state, remote-CI, provider-roundtrip, live-network, or installed-host
confirmation; those remain pending the final publish boundary.

AI-provenance: Agent-authored direct-commit carrier; the live issue read, causal
review, premise verification, implementation, source/plugin sync, focused
behavior proof, mutation proof, and locked local closeout are recorded in the
referenced artifacts. The issue remains OPEN while this carrier is local; do
not report CLOSED until the single final push and a distinct GitHub adapter
readback with `verify-closeout --expect-state CLOSED`.
