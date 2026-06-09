# Critique Review
Date: 2026-06-09

## Decision Under Review

Resolution critique for GitHub issue 338 (feature): gather's X/Twitter
exact-source fallback. The slice implements the `twitter-syndication`
`domain-specific-route` stage (previously a `not-implemented` skip) with
identity-keyed endpoints (Syndication CDN by status id, then oEmbed),
source-identity proof before accepting a result as the original, a visible
failed-attempt trace, an honest no-substitution stop, and a `source_identity`
verdict on the answer path. The original 338 failure was silent source
substitution — a merely-similar public source passed off as the original.

## Failure Angles

- Source substitution survives: a non-identical/similar source is accepted as the
  original. Checked — `returned == requested_id` is the only gate to `success`;
  `invalid-proof` maps to a terminal non-success disposition; no `similar-source`
  acceptance branch exists.
- oEmbed echoes the requested URL, so a 200 response could "verify" a deleted or
  nonexistent post by echoing the requested id without proving existence.
- Live X network fetch happening autonomously (against the no-live-by-default
  contract). Checked — the module has zero network primitives; fetching is
  injected and gated behind `--live-domain-route`.
- Behavior regression for non-X gather sources. Checked — `source_identity` is
  emitted only for the `twitter-syndication` route; other acquisitions unchanged.

## Counterweight Pass

- Real blocker: none. The identity gate is a hard, terminal check and the answer
  path carries an explicit verdict; a future edit that accepted a fallback would
  have to add a new enum + acceptance branch, making any regression loud.
- The oEmbed URL-echo gap is safe against the 338 threat (an echo can never match
  a *different* post), and the body-keyed Syndication endpoint is tried first.
  Folded anyway as cheap hardening rather than deferred.
- Over-worry: `parse_status_url` not covering `/i/web/status` or `/intent/*` is a
  coverage gap, not a correctness bug — those skip honestly to `exact-unavailable`
  and never substitute.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: bundle-anyway | evidence: moderate | ref: skills/support/web-fetch/scripts/twitter_exact_source.py returned_status_id | action: fix | note: oEmbed URL-echo proved requested-id match not existence; applied — require a rendered body (html/author_name) and make the oEmbed branch terminal so the raw-text fallback cannot reintroduce the echo; covered by a deleted-post test.
- F2 | bin: valid-but-defer | evidence: weak | ref: skills/support/web-fetch/scripts/twitter_exact_source.py make_fetcher | action: defer | note: a live syndication/oEmbed smoke test is worth a future operator-authorized lane; out of scope for the no-live-by-default contract (deferred — docs/handoff.md Next Session).

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: bounded fresh-eye subagent (general-purpose), read-only in the shared parent worktree.
- Requested spawn fields: issue 338 problem + acceptance criteria, changed files, six invariants, four adversarial questions.
- Host exposure state: applied
- Application state: host-confirmed: subagent a09cf56e2b3b14ebe ran (21 tool uses) and returned an end-to-end SHIP verdict, verifying invariants live (mismatch → invalid-proof/degraded, non-twitter omits source_identity).

## Fresh-Eye Satisfaction

tool signal: bounded subagent a09cf56e2b3b14ebe ran read-only (21 tool uses) and
returned an end-to-end SHIP verdict for issue 338.

The fresh-eye reviewer returned SHIP with no blockers, after verifying (not just
reading) every invariant: a different-post id yields `invalid-proof` →
non-success → `exact-blocked`; all-blocked/not-enabled yields
`exact-blocked`/`exact-unavailable`; `gather` never emits `similar-source`; no
network primitives in the module; and `source_identity` is omitted for non-X
sources. The single bundle-anyway finding (oEmbed existence proof) was folded
into this slice with a covering test.
