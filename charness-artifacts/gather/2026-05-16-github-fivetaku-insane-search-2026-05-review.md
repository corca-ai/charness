# Gather: fivetaku/insane-search latest review for charness gather

## Source

- Issue: https://github.com/corca-ai/charness/issues/169
- Upstream repo: https://github.com/fivetaku/insane-search
- Default branch: `main`
- Latest inspected commit: `b4ab9384399a8df58503268764ba43ed5520156d`
- Commit date: 2026-05-03T15:36:13Z
- Plugin version observed: `0.4.1`
- Access mode: authenticated `gh` CLI against public GitHub metadata and contents
- Freshness: inspected 2026-05-16 KST / 2026-05-15 UTC from GitHub source of truth

## Upstream Delta Since Charness' Prior Review

`charness` already had an `insane-search` provenance note under `skills/support/web-fetch/references/provenance.md` from 2026-04-13. The upstream repo changed materially after that point:

- 2026-04-22: `insane-search` added an `engine/` Python package with a single fetch entrypoint, explicit attempt tracing, WAF profile detection, URL transforms, validation, Playwright fallback routing, and tests.
- 2026-04-22: upstream rewrote the skill contract around rules R1-R7: CLI-first for blocked URLs, no success declaration on first HTTP 200, no site-name hardcoding in engine/profile code, runtime-only hints, official/public API precedence, exhaustive grid before failure, and an API-first branch for early WAF detection during list/collection tasks.
- 2026-05-04: upstream released 0.4.1 and surfaced the R7 branch decision in result metadata.

## Current Charness State

Current `charness` web-fetch support is intentionally smaller:

- `skills/support/web-fetch/references/provenance.md` records `insane-search` as a design reference, not a runtime dependency.
- `skills/support/web-fetch/references/runtime-contract.md` owns a route ladder and response classes.
- `skills/support/web-fetch/references/routing-table.md` has domain-family routes for X/Twitter, Reddit, Hacker News, Stack Exchange, GitHub, media sites, Naver, reader-style pages, and generic public URLs.
- `skills/support/web-fetch/scripts/route_public_fetch.py` returns route recommendations only; it does not execute a fetch grid.
- `skills/support/web-fetch/scripts/classify_fetch_response.py` classifies raw content as success, partial, login wall, CAPTCHA, empty SPA, error page, or unclear.

## Useful Ideas To Carry Forward

1. Attempt trace schema

`insane-search` models each attempt with phase, executor, transformed URL, impersonation target, referer strategy, status, body size, verdict, reasons, elapsed time, and error. This would improve charness gather artifacts because a failed or degraded fetch could preserve why a route was accepted, skipped, or rejected instead of only naming a selected route.

2. Positive-proof validation

Upstream treats HTTP 200 as insufficient and distinguishes strong success from weak success. Charness already classifies partial responses, but it does not accept caller-supplied positive proof such as expected selectors, JSON fields, or content markers. A charness-sized version should be generic and source-owned: `gather` can pass expected proof, while `web-fetch` classifies the response without embedding site-specific knowledge.

3. WAF/product-class response signals

Upstream's WAF profiles are product-oriented rather than site-oriented. Charness should not import the full bypass engine by default, but a small product-signal classifier could make `blocked`, `captcha`, and `empty-spa` results more actionable. This belongs in `web-fetch`, not the public `gather` workflow.

4. No-site-name invariant

Upstream's strongest reusable policy is the guard against fossilized site-specific logic in engine code. Charness already keeps its routing table intentionally incomplete, but it does not have a validator that prevents new hardcoded brand/domain bypass logic from creeping into generic helpers. A small local lint for `web-fetch` generic helpers is worth considering.

5. R7 as advisory, not automatic runtime

The API-first branch for early WAF detection is useful as an operator hint: when collection/list intent plus repeated WAF challenges appears, try browser/network inspection for public JSON/API endpoints. Charness should keep this as a documented route recommendation or degraded next step. It should not auto-run browser recon or auto-install dependencies from support helpers.

## Ideas Not To Adopt Directly

- Auto-installing `curl_cffi`, `feedparser`, `yt-dlp`, Node, or Playwright dependencies from a gather support path. Charness contracts prefer explicit integration manifests, readiness checks, and operator-visible missing capability states.
- A broad bypass promise such as "try everything until one works." Charness should preserve honest access mode, provenance, and clean stop behavior.
- Site-heavy trigger lists as public gather policy. Charness should keep domain-specific routes only when maintenance ownership is clear and the route is stable.
- Persisting discovered internal API URLs as reusable site knowledge unless the source has a stable public API contract or an explicit owner accepts the route.

## Suggested Follow-up Units

1. Add `web-fetch` attempt/trace schema and artifact guidance.
   - Output: route/fetch proof shape that gather artifacts can preserve.
   - Likely files: `skills/support/web-fetch/references/runtime-contract.md`, `skills/support/web-fetch/SKILL.md`, tests around helper JSON shape.

2. Add positive-proof response validation to `classify_fetch_response.py`.
   - Output: `strong-success` versus `weak-success`/`partial-content`, driven by caller-provided generic selectors or JSON/text markers.
   - Guardrail: no site-specific selectors in the helper.

3. Add a no-site-name or generic-helper lint for `web-fetch` support scripts.
   - Output: prevents generic fetch helpers from hardcoding domains outside the declared routing table or reference docs.
   - This is prevention, not a runtime feature.

4. Add an advisory R7-style next-step in route/classifier output.
   - Output: when repeated challenge/WAF-like signals and collection intent are present, report browser network/API reconnaissance as a possible next step, with access mode and auth/bootstrap caveats.
   - Do not auto-run the browser or auto-install dependencies.

## Review Conclusion For Issue #169

Issue #169 is valid. The latest upstream does contain new ideas that charness had not incorporated in the 2026-04-13 web-fetch extraction. The most compatible carry-forward is not a larger site cookbook; it is a stronger diagnostic contract around route attempts, response validation, generic WAF signals, and anti-fossilization linting.

Recommended classification: `deferred-work` / design follow-up, not an immediate bug. The issue should stay open until the maintainer chooses whether to file the follow-up units above as separate implementation issues or bundle the smallest diagnostic-contract slice into `web-fetch`.

## Scoped Critique

- Likely misread: treating upstream's bypass-engine posture as a mandate for charness to auto-install dependencies or promise access through every blocked site. Counterweight: reject this; charness should keep explicit capability manifests, access modes, and clean stops.
- Opposite risk: rejecting the whole upstream update because the runtime posture is too aggressive. Counterweight: keep the portable pieces that improve evidence quality: attempt trace shape, positive-proof validation, WAF/product signal classification, and no-site-name linting.
- Next move: do not close #169 from this review alone. Either split the follow-up units into implementation issues or pick the smallest `web-fetch` diagnostic-contract slice and run normal implementation/quality closeout.
