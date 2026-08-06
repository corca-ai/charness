# Issue #510 Public Markdown Representation Negotiation Contract

Date: 2026-08-06
Source: [Issue #510 causal review](../critique/2026-08-06-issue-510-causal-review.md)

## Problem

The generic public URL route requests an HTML representation only. When a
public Markdown-capable page answers that request with a login wall, gather
stops before trying the same public URL's content-negotiated Markdown form.

## Capability Contract

The public acquisition route must distinguish an inaccessible public source
from a representation that has not yet been tried. After a direct attempt is
classified as `login-wall`, it may retry the same URL with `Accept:
text/markdown`, without credentials, browser actions, or a provider-specific
exception. A successful Markdown response enters the existing success and
persistence path; a failed retry preserves the existing blocked/degraded
disposition and trace.

## Current Slice

Add one content-negotiated Markdown stage between direct fetch and existing
fallbacks, preserve the requested representation and route in its attempt
details, and cover the producer-to-gather roundtrip with deterministic
transport fixtures.

## Fixed Decisions

- Retry only after a direct `login-wall` or when the URL path is explicitly
  Markdown-looking (`.md` or `.markdown`) and direct acquisition is not
  sufficient.
- Do not retry seeded `--direct-response-file` fixtures as if they were a live
  second representation; record the stage as skipped with a deterministic
  reason.
- Keep the existing classifier, disposition, no-credential boundary, and
  fallback order. The new stage is a public representation selection, not an
  authentication or browser bypass.
- Make the stage generic and portable; broader provider discovery remains a
  follow-up rather than a new provider taxonomy.

## Probe Questions

- Does the existing text-attempt path classify a Markdown body and preserve it
  for gather persistence? The focused fixture must answer this.
- Does a failed Markdown retry retain a useful trace and the original blocked
  outcome? The negative fixture must answer this.

## Deferred Decisions

- Response-header/content-type capture beyond the requested representation;
  defer until a consumer needs to distinguish server negotiation from body
  classification.
- Provider-specific Markdown endpoints, browser negotiation, and authenticated
  access; follow-up: `gather-routing-provider-discovery`.

## Non-Goals

- Do not bypass login, submit forms, use credentials, or weaken `login-wall`.
- Do not replace the existing reader, browser, or domain-specific fallback
  stages.
- Do not claim live provider or installed-consumer behavior from local tests.

## Deliberately Not Doing

- No live URL call or Cautilus evaluation is required for this local slice.
- No broad content-negotiation matrix or provider allowlist is introduced.

## Constraints

- Source and plugin support/gather mirrors must remain synchronized.
- Existing direct and seeded fixture semantics must remain stable.
- The new attempt must use the existing classifier and selected-content
  persistence machinery.

## Success Criteria

- A direct login-wall followed by a Markdown success is reported as success,
  selects `content-negotiated-markdown`, and exposes `representation: markdown`
  plus its route in the trace.
- The gather helper persists the selected Markdown body when requested.
- A Markdown retry that remains blocked/degraded leaves the final disposition
  honest and records the retry rather than silently stopping after HTML.
- A seeded direct fixture does not cause a second unobservable read.

## Acceptance Checks

- `python3 -m pytest -q tests/test_web_fetch_route_and_classify.py tests/test_web_fetch_content_persistence.py` (unit/integration: route stage, deterministic transport, classifier, and gather persistence)
- `cmp -s skills/support/web-fetch/scripts/acquire_public_url.py plugins/charness/support/web-fetch/scripts/acquire_public_url.py` (integration: support mirror)
- `cmp -s skills/support/web-fetch/scripts/acquire_public_url_io.py plugins/charness/support/web-fetch/scripts/acquire_public_url_io.py` (integration: IO mirror)
- `cmp -s skills/support/web-fetch/scripts/route_stage_catalog.py plugins/charness/support/web-fetch/scripts/route_stage_catalog.py` (integration: route catalog mirror)
- `python3 scripts/validate_debug_artifact.py --repo-root .` (integration: causal diagnosis remains durable)

## Boundary Ownership

- `preserve`: `acquire_public_url_io.py` owns public request representation;
  `acquire_public_url.py` owns stage ordering and attempt trace.
- `preserve`: classifier and gather own verdict semantics and persistence;
  they must not infer success from the requested header alone.
- `preserve`: the operator/host owns live provider and installed-consumer
  proof; local fixtures do not replace that boundary.

## Critique

- Interrupt Source: gather-510-markdown-representation-selection
- Seam Summary: public provider representation -> acquisition classifier -> gather record
- Chosen Next Step: impl
- Impl Status: allowed
- Impl Status Reason: causal review identified a bounded missing stage; local
  transport fixtures can prove the stage contract without claiming provider
  liveness.
- What Disproving Observation Is Resolved: an alternate Markdown response must
  be selected and persisted, while a failed retry must remain blocked/degraded.
- Critique: delegated causal review completed before this contract; it named
  the missing representation invariant, existing policy stop, detection gap,
  same-class siblings, and provider-discovery follow-up.

## Canonical Artifact

- `charness-artifacts/spec/2026-08-06-issue-510-markdown-negotiation-contract.md`

## First Implementation Slice

Add the stage and route declaration, write a transport fixture that returns a
login wall for HTML and Markdown for `Accept: text/markdown`, then run the
focused tests and update the closeout artifacts with the observed trace.

## Interrupt Carry-Forward (2026-08-06)

The forced `gather-510-markdown-representation-selection` interrupt was
resolved by the completed local implementation and its paired transport and
gather persistence fixtures. This refresh preserves the external-seam
boundary: live provider negotiation, installed-consumer behavior, and remote
CI remain unverified. Future provider-specific discovery remains the named
follow-up; unrelated portability slices may continue without reopening this
resolved contract.

## Interrupt Carry-Forward Refresh (2026-08-06)

The current risk-interrupt planner requires this handoff artifact to be touched
in the slice that resumes ordinary implementation. The resolved observation is
unchanged: paired local transport and gather-persistence fixtures prove the
bounded Markdown stage, while live provider negotiation, installed-consumer
behavior, and remote CI remain non-claims. This refresh authorizes unrelated
local evidence work to continue without reopening issue #510.

## Interrupt Carry-Forward Refresh (Slice 2, 2026-08-06)

Slice 2 is an unrelated local premise-preflight seam. It preserves the same
resolved observation and non-claims; no Markdown negotiation, provider call,
installed-consumer execution, or remote behavior is being added here.

The Slice 2 premise-preflight contract is now the implementation target; this
carry-forward remains a lifecycle binding only and does not reopen the
resolved Markdown work.

## Interrupt Carry-Forward Refresh (Slice 6, 2026-08-06)

The forced `gather-510-markdown-representation-selection` interrupt remains
resolved by the paired local transport and gather-persistence fixtures. Slice 6
is an unrelated local publish-state evidence seam: it does not retry providers,
change Markdown negotiation, claim installed-consumer behavior, or make a
remote write. The existing live-provider and remote-CI non-claims remain in
force while immutable ledger reconciliation proceeds against the captured
post-push manifest.
