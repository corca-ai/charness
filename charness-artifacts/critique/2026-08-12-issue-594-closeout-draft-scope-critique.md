# #594 Consolidated Closeout-Draft Scope Critique

Date: 2026-08-12

## Execution

Two bounded read-only fresh-eye review rounds examined the proof surface. Round
1 found misleading readback timing, an overbroad keyword claim, and a
keyword-free manual self-reference escape; round 2 approved the repair. Its
first worktree window was invalidated by parent artifact writes, so a clean
retry supplied the valid approval. A standalone code critique then ran two
bounded angles and an independent counterweight against the prepared packet.

## Fresh-Eye Satisfaction

parent-delegated — all findings were received directly. Reviewer-boundary
fingerprints were clean for the valid round-2 retry and every critique reviewer.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `fork_turns=none`, `model=gpt-5.6-terra`,
  `reasoning_effort=medium`, `service_tier=priority`.
- Host exposure state: metadata-hidden
- Application state: requested fields sent; the host returned no independent
  provider-tier confirmation.
- Delivery state: findings-received.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-12-110534-packet.md
- Packet path: charness-artifacts/critique/2026-08-12-110534-packet.json
- Packet SHA256: c122bcaca5c9fbf061fed9134efb321f830428b5f33662c11622676cdc18909f
- Identity SHA256: 7ae4fd61e4e0093a755aa9d56f50ba091f48fc1bf35a3ffbd8f781b74bda5f26
- The angle reviewers consumed the earlier 10:56 packet (identity
  `4012dea3…2e038a`). This final packet binds the post-critique repair state;
  it was refreshed by the parent, not a third reviewer, because those repairs
  are accepted-unreviewed under the proof-surface two-round cap.

## Boundary Ownership

- Producer: `issue_consolidated_closeout` owns body grammar and repair claims;
  the close carrier owns invoked issue identity and backend readback.
- Consumer: an author selecting a closeout-draft classification, then the
  manual close-with-comment carrier that mutates GitHub.
- Owning surface: public issue scripts and generated plugin projection.
- Verdict: owned-correctly.

## Decision Under Review

Give an author who selects `consolidated` only a carrier/body guide the live
floor permits, while rejecting a manual self-destination without relying on an
inert comment keyword.

## Findings and Counterweight Triage

- F1 | bin: act-before-ship | evidence: strong | ref:
  `describe_closeout_draft_shape.py` | action: fixed | note: the all-classifications
  catalog still put generic direct/pr and keyword guidance before its exception.
  `--classification consolidated` now renders a selected, non-conflicting guide;
  the catalog tells the author to use it.
- F2 | bin: bundle-anyway | evidence: strong | ref:
  `test_check_artifact_surface_preflight.py` | action: fixed | note: the regression
  now runs the selected renderer and asserts generic carrier/keyword sections are
  absent, rather than only checking exception tokens somewhere in a catalog.
- F3 | bin: act-before-ship | evidence: strong | ref:
  `issue_consolidated_closeout.py` | action: fixed | note: `Fixes: #N` and
  `Resolves: #N` were semantically repair claims but bypassed a whitespace-only
  predicate. Colon and whitespace spellings now share the refusal; colon-form
  `Closes` is also recognized on auto-closing carriers.
- F4 | bin: over-worry | evidence: strong | ref:
  `issue_close_comment_floor.py` | action: document | note: do not extend the
  full resolution ledger to every manual close. The narrow consolidated check
  addresses the observed carrier contradiction without changing unrelated
  established paths.
- F5 | bin: valid-but-defer | evidence: moderate | ref:
  `describe_closeout_draft_shape.py` | action: defer | note: a public
  introspection API for every carrier/claim rule could reduce renderer probing,
  but it is not needed for this bounded repair.

## Defect Class Cross-Link

`charness-artifacts/retro/recent-lessons.md` — repeat trap: author guidance must
derive from the enforcing owner and test equivalent accepted spellings.

## Deliberately Not Doing

- Do not broaden manual-close ledger enforcement beyond `consolidated`.
- Do not claim a live GitHub destination readback, issue closure, provider
  mutation, hosted CI, publication, or release.
- Do not add a generic carrier-rule introspection API in this slice.

## Next Move

Run changed-surface validators and the local pre-commit gate, commit the locally
proven slice, then move to #593. The post-critique representation and selected-
guide repairs are accepted-unreviewed under the two-round proof-surface cap.
