# Gather Acquisition Repair Contract

- Date: 2026-05-16
- Source critique: [charness-artifacts/critique/2026-05-16-gather-acquisition-repair-plan-critique.md](../critique/2026-05-16-gather-acquisition-repair-plan-critique.md)
- Current implementation: [skills/support/web-fetch/scripts/acquire_public_url.py](../../skills/support/web-fetch/scripts/acquire_public_url.py)
- Test surface: [tests/test_web_fetch_support.py](../../tests/test_web_fetch_support.py)

## Problem

The current `web-fetch` acquisition helper has a useful public-URL fallback
ladder, but the trace can overstate what actually happened. A support skill
may skip `defuddle` or `agent-browser` without recording the skipped stage,
advertise domain routes that were never executed, treat browser network
reconnaissance as acquisition, or let caller proof override blocker signals.
The public `gather` workflow also does not yet make the arbitrary public URL
path clearly reachable through this helper.

## Current Slice

Repair trace/proof correctness while preserving an acquisition-maximizing
fallback ladder:

- reject non-HTTP(S) URLs before acquisition starts
- keep attempting stronger stages when direct fetch is weak, blocked, partial,
  empty, unclear, or proof-required
- record skipped and not-implemented stages from the route plan
- select final disposition from the best acquired-content attempt, not from an
  auxiliary diagnostic attempt
- make public `gather` route arbitrary public URLs through `web-fetch` and
  preserve the helper output in the durable gather asset

This slice does not add raw acquired-content persistence beyond selected
metadata and trace fields.

## Fixed Decisions

1. Non-HTTP(S) URLs are input errors.
   - `file:`, `ftp:`, and other schemes must not reach `urllib`, `defuddle`,
     or `agent-browser`.

2. Invalid `--expect-regex` is invalid proof.
   - It may return `disposition: "error"` or an explicit invalid-proof status,
     but it cannot produce strong success.

3. Blocker signals outrank positive proof.
   - CAPTCHA, login-wall, and error-page classifications may retain proof in
     metadata, but final disposition must be blocked or contested rather than
     success.

4. Browser network reconnaissance is diagnostic-only.
   - It may add candidates to trace metadata, but it cannot be the selected
     acquired-content attempt unless a candidate is fetched and classified in
     the same run.

5. Domain-specific route stages are truthful.
   - If Reddit/HN/Stack Exchange/GitHub/media/Naver routes are not executed in
     this slice, emit skipped or not-implemented attempts with reasons.

6. `defuddle` remains the reader-extraction stage.
   - Use it when installed and the route or prior classification calls for
     reader extraction. Missing binary state must be recorded as a skipped
     attempt, not disappear from the trace.

7. Selector proof is not shipped unless implemented.
   - Either implement `--expect-selector` with tests or remove selector wording
     from public/support docs in the same slice.

## Probe Questions

1. Public `gather` wiring shape:
   - Prefer a small helper or documented support invocation that lets the public
     skill record `web-fetch` output in the gather asset without teaching the
     public skill site-specific routes.

2. Selected-attempt schema:
   - Minimal expected fields are `stage_id`, `tool_id`, `status`,
     `confidence`, `classification`, and `reason`.

3. Contested proof wording:
   - Decide during implementation whether proof-on-blocker is represented as
     `disposition: "blocked"` with proof metadata or
     `disposition: "contested"`.

## Deferred Decisions

- Raw acquired-content persistence, content-size policy, and copyright-safe
  excerpt handling.
- No-site-name / generic-helper lint from the insane-search review.
- Live `defuddle` dogfood on this machine; current machine lacks the binary.
- Archive/cache fallback implementation.

## Non-Goals

- Do not solve private SaaS acquisition in this slice.
- Do not click, submit forms, solve challenges, or persist discovered internal
  API endpoints as reusable site knowledge.
- Do not require live network access for deterministic acceptance tests.
- Do not close #169 until the unpublished local commits are pushed/PR'd and
  accepted upstream.

## Deliberately Not Doing

- Do not force `defuddle` after every weak direct success when no proof is
  requested and the classifier already reports useful article content. That
  latency and policy choice can be revisited after trace/proof correctness is
  reliable.
- Do not treat route plans as completed work. Unexecuted plan stages must be
  visible as skipped or not-implemented attempts.

## Constraints

- Keep `web-fetch` a support skill. Public `gather` owns durable asset shape and
  source identity; support `web-fetch` owns public-web retrieval tactics.
- Sync plugin exports before validators after touching skill/support scripts.
- Deterministic tests must cover missing external binaries through stubbed
  `PATH` fixtures rather than requiring local `defuddle` or `agent-browser`.

## Success Criteria

1. Unsafe URL schemes cannot be acquired.
2. Invalid proof input cannot promote a response to success.
3. Missing or disabled fallback stages are explicit in `attempts`.
4. Domain route plan stages are either executed or truthfully skipped.
5. Recon-only browser network data cannot determine success.
6. Blocker classifications prevent success even when caller proof matches.
7. Final disposition and confidence are derived from `selected_attempt`.
8. Public `gather` can record web-fetch route, attempts, selected proof,
   remaining gaps, and access mode in a durable asset for an arbitrary public
   URL.

## Acceptance Checks

- Add focused tests in [tests/test_web_fetch_support.py](../../tests/test_web_fetch_support.py):
  non-HTTP rejection, invalid regex, missing `defuddle`, missing
  `agent-browser`, skipped route stages, recon-only non-success,
  blocker-before-proof, selected-attempt final status, and selector-doc cleanup
  or selector implementation.
- Add or update a gather-facing test proving arbitrary public URL routing
  records the `web-fetch` trace in the gather asset.
- Run:
  - `pytest -q tests/test_web_fetch_support.py`
  - `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
  - `python3 scripts/validate_skills.py --repo-root .`
  - `python3 scripts/validate_packaging.py --repo-root .`
  - `python3 scripts/validate_packaging_committed.py --repo-root .`
  - `python3 scripts/check_doc_links.py --repo-root .`
  - `./scripts/check-markdown.sh`

## Implementation Status

Implemented locally in the current unpublished slice:

- non-HTTP(S) rejection
- invalid-regex invalid-proof handling
- blocker-before-proof classification
- skipped domain/fallback attempts for not-implemented or missing-tool routes
- diagnostic-only browser network reconnaissance
- `selected_attempt` based final status/confidence
- selector-proof wording cleanup
- public `gather_public_url.py` helper that writes durable gather records with
  embedded `web-fetch` trace JSON

Still deferred: raw acquired-content persistence, archive/cache fallback, and
live `defuddle` proof on this machine.

Public-skill scenario review: `gather` remains `evaluator-required`, but this
slice did not mutate [evals/cautilus/scenarios.json](../../evals/cautilus/scenarios.json).
The maintained scenario currently covers gather adapter bootstrap; the changed
consumer contract is narrower and deterministic, so it is frozen in
[docs/public-skill-dogfood.json](../../docs/public-skill-dogfood.json) instead
of adding a live Cautilus scenario without a log-backed behavior failure.

## Critique

- Interrupt Source: none; this is a planned repair contract from the prior
  gather critique.
- Seam Summary: the main risk is overclaiming acquisition success from a trace
  helper that is not yet public-gather-reachable.
- Chosen Next Step: implement trace/proof correctness first, while keeping the
  support ladder acquisition-maximizing where the route and installed tools
  allow it.
- Impl Status: implemented locally for the trace/proof correctness slice.
- Impl Status Reason: focused tests now exercise the named failure modes and
  the gather-facing durable trace helper.
- What Disproving Observation Is Resolved: network recon alone no longer yields
  success; blocker pages with matching proof no longer become success; invalid
  regex no longer becomes strong proof; skipped fallback stages are visible.
- Fresh-eye status: the prior repair-plan critique already reviewed the shape.
  A new fresh-eye review was not spawned for this contract because the current
  host tool contract only permits `spawn_agent` when the current task asks for
  subagent delegation.

## Canonical Artifact

This file remains the canonical repair contract for residual gather acquisition
work. The trace/proof correctness slice is locally implemented; keep this file
synchronized if future raw-content persistence or live `defuddle` proof changes
the contract.

## First Implementation Slice

Next implementation work is optional proof expansion rather than a required
repair: add live `defuddle` dogfood when the binary is installed, then decide
whether raw acquired-content persistence belongs in a separate contract.
