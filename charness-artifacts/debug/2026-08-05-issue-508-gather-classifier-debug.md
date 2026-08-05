# Issue #508 Gather Classifier Debug
Date: 2026-08-05

## Problem

`gather_public_url.py` classifies valid public Markdown containing `design
intent` or the title `Design in the AI era` as `login-wall`, so no durable
asset is written.

## Correct Behavior

Given a readable public Markdown response whose prose contains the character
sequence `sign in` only across an ordinary word boundary, when the gather
classifier evaluates it, it must return a content verdict rather than an
authentication refusal. Given an actual login page, it must retain the
`login-wall` refusal and its fallback trace.

## Observed Facts

- Issue #508 was read through the GitHub adapter on 2026-08-05 with
  `comments_read: true`, state OPEN, and no comments.
- The issue's exact source URLs are public Markdown paths. `gather_public_url.py`
  independently returned `blocked` / `final_status: login-wall`, matched
  `sign in`, and `content_persistence: none` for both named pages.
- The named control source was fetched through the same gather route with weak
  success and extracted content; its current gathered record is
  `charness-artifacts/gather/2026-08-05-g15e-aop-and-css.md`.
- The classifier defines `LOGIN_PATTERNS` as raw substrings and checks
  `pattern in lowered` before long-content success.

## Reproduction

- Direct classifier fixture: `design intent` in a 1,638-character readable
  body returns `login-wall` with `matched_signals: ["sign in"]`.
- The title-shaped `Design in the AI era` fixture returns the same false
  `login-wall`; an actual `Sign in` page also returns `login-wall`.
- A long control fixture without the sequence returns `success` / `weak`.
- The live failed pages were not persisted by gather because the public fetch
  route classified them as blocked; the issue's captured-body evidence is the
  source for the reported byte counts, not a new local live-source claim.

## Candidate Causes

- The classifier uses a raw substring instead of token-aware authentication
  markers, so `design intent` crosses the boundary between `de` and `sign in`.
- The login signal is evaluated before long-content success, so response length
  cannot rescue a false positive.
- Gather persists only after the classifier's final disposition, so a
  classifier false positive becomes a durable-record omission and is reported
  as an auth boundary.

## Hypothesis

- If authentication markers are matched as tokens/phrases with real boundary
  evidence, then `design intent` and `Design in the AI era` become content while
  a real `Sign in` page remains `login-wall` | disconfirmer: run the classifier
  against positive word-boundary controls, a real-login fixture, and the same
  gather helper with a seeded direct response before changing persistence.

## Verification

- confirmed as the leading hypothesis — the smallest local fixtures reproduce
  the exact false positive while the control and real-login fixtures separate
  content from authentication. No fix has been applied yet.

## Root Cause

The current classifier treats `sign in`, `log in`, and `login` as unconstrained
raw substrings. The producer therefore emits `login-wall` for legitimate prose.
This is a bounded marker-precision failure, not proof that every standalone
marker is a real authentication wall; the gather writer correctly honors the
typed verdict, so the visible persistence failure is downstream of the
classification error.

## Invariant Proof

- Invariant: when the response classifier emits `login-wall`, the gather writer
  must refuse persistence; the classifier must emit that signal only for a
  supported independently bounded marker, not an incidental substring. This
  local invariant does not prove a real authentication wall on every page.
- Producer Proof: the classifier fixture returns `login-wall` for `design intent`
  and for real `Sign in` input; the same route returns success for the control.
- Final-Consumer Proof: `gather_public_url.py` returns blocked with
  `content_persistence: none` for the live failed URLs; source inspection and
  existing blocked-acquisition tests bind that verdict to no record write.
- Interface-Shape Sibling Scan: classifier signal patterns, acquisition trace
  status selection, and gather writer persistence were searched; sibling
  decisions preserve blocker precedence and typed blocked outcomes.
- Non-Claims: the live source bodies, installed plugin behavior, provider
  roundtrip, and remote CI are not proven by this local diagnosis.

## Detection Gap

- `tests/test_web_fetch_route_and_classify.py` covers a real login phrase and
  blocker precedence but has no false-positive word-boundary controls; add
  positive `design intent` / title controls and keep a real-login negative.
- Existing gather blocked-write tests protect persistence semantics, not the
  classifier's semantic precision; add a seeded end-to-end gather regression.

## Sibling Search

- Mental model: a producer's broad text heuristic controls a typed acquisition
  boundary and a downstream durable writer.
- same interface: `classify_fetch_response.py` signal precedence | decision:
  keep real blockers authoritative while narrowing the marker | proof: local
  classifier tests and current implementation.
- cross-file: `gather_public_url.py` plus blocked-acquisition tests | decision:
  preserve no-write behavior for genuine blockers and add a content-positive
  path for false-positive controls | proof: source inspection and fixtures.

## Seam Risk

- Interrupt ID: gather-508-token-aware-login-wall
- Risk Class: external-seam
- Seam: public response classifier -> gather disposition -> durable asset writer
- Disproving Observation: a real login page must still be classified and
  persisted as blocked/no-write after the marker is narrowed.
- What Local Reasoning Cannot Prove: the named live pages' full bodies and
  behavior in installed or consumer environments; gather recorded the live
  route as blocked, while the issue supplied captured-body evidence.
- Generalization Pressure: monitor
  need explicit negative fixtures beyond one phrase.

## Interrupt Decision

- Resolution: open
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-08-05-issue-508-gather-classifier-contract.md

## Prevention

Define authentication markers as bounded semantic signals, retain explicit
positive and negative fixtures at both classifier and gather persistence seams,
and keep live-source/installed-host gaps visible instead of treating a local
classifier green as external acquisition proof.
