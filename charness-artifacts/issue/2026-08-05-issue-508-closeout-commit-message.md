fix: make gather login markers token-aware

Closes #508
Classification: bug
Carrier: direct-commit; this message is the proposed issue-resolution carrier.

Jtbd: A gather operator must be able to persist a valid public Markdown source
whose prose contains ordinary text such as `design intent`, without the
classifier reporting a false login wall and suppressing content persistence.

Observed problem: `gather_public_url.py` classified two valid public Markdown
responses as `login-wall` because the raw substring `sign in` occurred inside
legitimate source text. The control source succeeded through the same route.

Root Cause: The classifier searched raw visible content for unbounded
substrings instead of matching supported login markers as standalone,
case-folded tokens. `design intent` therefore contained a false `sign in`
match, and the classifier emitted a blocker before gather could persist the
captured document.

Debug Artifact: charness-artifacts/debug/2026-08-05-issue-508-gather-classifier-debug.md

Implementation: `skills/support/web-fetch/scripts/classify_fetch_response.py`
and its checked-in plugin mirror now normalize visible text and match the
supported `sign in`, `log in`, `login`, and `로그인` markers with explicit token
boundaries. The gather route preserves the corrected valid content while real
login markers remain blockers.

Siblings: Decision: same bug, fix now — the `sign in`, `log in`, `login`,
`로그인`, and markup-split visible-marker forms share the classifier's
marker-boundary contract. Proof: the focused route/classifier and
gather-support suites passed 39 tests, including matched-signal and persistence
assertions. Decision: intentional plain-content boundary, diagnostic-only for
this slice — larger embedded tokens and repeated or spaced hyphen forms remain
content-positive. Proof: `tests/test_web_fetch_route_and_classify.py` covers
those negative fixtures. No provider-specific vocabulary, browser fallback, or
live-source sibling is claimed or bundled.

Prevention: Keep the source/plugin classifier mirrors synchronized; retain
positive and negative marker fixtures, exact `matched_signals` assertions, and
gather persistence/no-write coverage in the focused suites; run the changed
line mutation consumer before publish.

Boundary: owned-correctly — classifier marker precision and precedence remain
owned by the classifier, gather disposition-to-persistence remains owned by
the gather consumer, and source/plugin equality remains the packaging seam.
Critique: charness-artifacts/critique/2026-08-05-issue-508-resolution-critique.md

Behavior #508: local-only-by-contract — the distinct local focused-test
channel (`python3 -m pytest -q tests/test_web_fetch_route_and_classify.py
tests/test_web_fetch_support.py`, 39 passed) exercises the false-positive,
real-marker, precedence, parity, and persistence boundaries. This is not a
GitHub-state, remote-CI, provider-roundtrip, live-URL, or installed-host
confirmation; those remain pending the final publish boundary.

AI-provenance: Agent-authored direct-commit carrier; the live issue read,
causal/debug records, implementation and resolution critique, synchronized
source/plugin proof, final closeout and changed-line mutation evidence are
recorded in the referenced artifacts. The issue was still OPEN when this
carrier was prepared; do not report CLOSED until the single final push and a
distinct GitHub adapter readback with `verify-closeout --expect-state CLOSED`.
