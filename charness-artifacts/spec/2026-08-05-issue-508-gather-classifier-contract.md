# Issue #508 Gather Classifier Token-Aware Login-Wall Contract

Date: 2026-08-05
Source: [Issue #508 debug review](../debug/2026-08-05-issue-508-gather-classifier-debug.md)

## Problem

The public-URL classifier rejects readable Markdown when the raw character
sequence `sign in` crosses an ordinary word boundary, such as `design intent`.
The gather writer then correctly honors the false blocker and produces no
durable asset, misreporting a classifier precision failure as an auth boundary.

## Capability Contract

The support classifier owns the precision of its supported login-marker
heuristic. Gather owns the disposition and persistence contract after that
classification; this slice does not prove that every matched marker is a real
authentication boundary.

- A standalone supported marker such as `Sign in`, `log in`, `login`, or the
  supported Korean marker remains `login-wall` with blocker precedence.
- An incidental substring inside a larger word, including `design intent`,
  must not become a login marker.
- Hyphenated or whitespace-separated marker phrases remain eligible when their
  tokens are independently bounded in case-folded normalized visible text.
- A genuine `login-wall` remains blocked and is not persisted; a readable
  content-positive response is eligible for the normal success persistence
  path.

## Current Slice

Narrow the login-marker matching in
`skills/support/web-fetch/scripts/classify_fetch_response.py`, add positive and
negative classifier fixtures, and add one seeded gather regression proving that
the corrected content path reaches persistence while a genuine login response
still does not. Keep the support/public gather boundary and source behavior
portable.

## Fixed Decisions

- Use internal token-aware matching against case-folded normalized visible text
  with explicit word boundaries; do not add a new public CLI mode, classifier
  enum, or provider-specific exception.
- Preserve blocker precedence over caller-provided positive proof and preserve
  the existing `login-wall` status, signal, matched-signal vocabulary, and
  no-write behavior for genuine blockers.
- Treat `sign in` and `log in` as token phrases allowing ordinary whitespace or
  a hyphen; treat `login` and `로그인` as independently bounded markers. The
  explicit matrix is: `design intent` and `Design in the AI era` -> content;
  `Sign in`, `Please log in`, `sign-in`, `login`, and exact `로그인` ->
  `login-wall`; marker text embedded inside larger word tokens -> content.
- Keep the first implementation slice classifier-owned. Do not add a broad
  page-quality score or a universal authentication corpus without evidence that
  bounded markers are insufficient.
- The current durable public proof is the local debug artifact, the existing
  gathered control record, and the new checked-in regression tests. The live
  named pages were route-blocked by the gather helper; their full bodies remain
  issue-provided evidence rather than a new live capture claim.

## Probe Questions

- Do existing provider pages require punctuation or markup-aware markers beyond
  bounded token phrases? Answer with deterministic fixtures first, then write
  the answer back into this contract's Fixed Decisions or Deferred Decisions;
  defer live provider expansion unless a real recurrence requires it.
- Does the seeded end-to-end gather path preserve extracted content after the
  classifier changes? The regression must answer this without network access
  and write the observed persistence shape back into this contract's
  Acceptance Checks.

## Deferred Decisions

- A page-level authentication classifier using headings, forms, or response
  metadata; reopen if a recorded public response still yields a false positive
  or false negative after the bounded-marker fixtures pass.
- Provider-specific login vocabularies or a universal public-web auth corpus;
  reopen on a recorded provider response whose required marker is absent from
  the supported vocabulary.
- Browser fallback, credentialed acquisition, and remote/consumer-host
  roundtrips; reopen only when an operator needs a live or installed-host proof
  that local fixtures cannot provide.

## Non-Goals

- Rewriting the gather route ladder, persistence writer, or blocked-record policy.
- Making a blocked page successful because caller proof or response length is
  positive.
- Claiming the two named live URLs are now acquirable from this host.

## Deliberately Not Doing

- Do not restore the old raw substring matcher.
- Do not weaken real login detection to make the two examples pass.
- Do not persist blocked or degraded acquisitions merely to preserve evidence.
- Do not add Cautilus evaluation or a live-browser/authenticated route.

## Constraints

- Keep `classify_fetch_response.py` dependency-free and deterministic.
- Preserve source and plugin classifier/gather parity; the plugin ships the
  support classifier under `plugins/charness/support/web-fetch/` and must not
  retain the false-positive matcher.
- Add both positive and negative cases at the classifier boundary and one
  gather-facing persistence case; do not make live network access a test
  prerequisite.
- Keep the changed-line mutation lane meaningful for the marker and precedence
  branches.

## Success Criteria

- A readable body containing `design intent` is classified as content rather
  than `login-wall`.
- A title/body containing `Design in the AI era` is classified as content.
- A real standalone `Sign in` or `Please log in` response remains
  `login-wall`, with blocker precedence over positive proof.
- A hyphenated standalone marker such as `sign-in` remains a login blocker.
- A standalone `login` and exact `로그인` marker remain blockers, while the
  same marker embedded in a larger token is content.
- A markup-split visible marker such as `Sign <span>in</span>` remains a
  blocker because matching uses normalized visible text.
- The seeded gather helper persists a content-positive body containing the
  former false-positive phrase when `--persist-extracted-content` is requested;
  the written record contains the extracted phrase, while the seeded genuine
  login body remains blocked with no record write.

## Acceptance Checks

- `python3 -m pytest -q tests/test_web_fetch_route_and_classify.py tests/test_web_fetch_support.py`
  (unit/integration: explicit marker matrix, visible-text markup split,
  blocker precedence, and seeded gather persistence/no-write behavior; the
  persistence test must assert `content_persistence: extracted`, written
  extracted text, and no record for the genuine blocker)
- `python3 -m pytest -q tests/test_web_fetch_route_and_classify.py -k token_aware_login_markers`
  (unit: direct positive/negative marker matrix and normalized visible-text
  matching)
- `cmp -s skills/public/gather/scripts/gather_public_url.py plugins/charness/skills/gather/scripts/gather_public_url.py`
  (integration: public gather mirror remains synchronized)
- `cmp -s skills/support/web-fetch/scripts/classify_fetch_response.py plugins/charness/support/web-fetch/scripts/classify_fetch_response.py`
  (integration: shipped source/plugin classifier behavior remains synchronized)
- `python3 scripts/validate_debug_artifact.py --repo-root .`
  (integration: the external-seam diagnosis and interruption remain durable)
- `python3 scripts/plan_risk_interrupt.py --repo-root . --detail`
  (integration: this contract carries the forced interrupt and permits the next
  implementation step only after its required fields are present)
- `python3 scripts/validate_skills.py --repo-root .` and
  `python3 scripts/check_doc_links.py --repo-root .`
  (integration: shipped support/public surfaces remain valid)

## Boundary Ownership

- `preserve`: the classifier owns semantic login-marker precision and blocker
  precedence.
- `preserve`: `gather_public_url.py` owns the final disposition-to-persistence
  mapping and must keep genuine blocked acquisitions non-persistent.
- `preserve`: the operator/host owns any live public-source or authenticated
  route proof; local fixtures do not substitute for that boundary.

## Critique

- Interrupt Source: gather-508-token-aware-login-wall
- Seam Summary: public response classifier -> gather disposition -> durable asset writer
- Chosen Next Step: impl
- Impl Status: allowed
- Impl Status Reason: delegated critique completed; its required repairs are
  recorded above, and the contract now names the bounded implementation and
  acceptance matrix.
- What Disproving Observation Is Resolved: local fixtures reproduce the false
  positive and distinguish it from a real login page; a post-fix genuine-blocker
  readback remains required.
- Critique: delegated fresh-eye review completed before implementation. It
  required this contract to narrow the auth-wall claim to a bounded marker
  heuristic, specify normalized visible-text matching, cover the full marker
  matrix, require extracted persistence/no-write assertions, and include the
  source/plugin classifier mirror.

## Canonical Artifact

- `charness-artifacts/spec/2026-08-05-issue-508-gather-classifier-contract.md`

## First Implementation Slice

Change the classifier's internal marker matching, add the bounded positive and
negative tests plus the seeded gather persistence regression, run source/public
parity and the focused acceptance checks, then update this contract with the
confirmed behavior before closeout.
