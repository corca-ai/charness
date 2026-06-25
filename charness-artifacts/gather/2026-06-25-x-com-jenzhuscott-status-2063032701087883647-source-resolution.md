# Gathered Public URL

- Source: https://x.com/jenzhuscott/status/2063032701087883647/
- Access Mode: support/web-fetch public route
- Content Persistence: `none`
- Route: `twitter-syndication`
- Route Family: `public-api`
- Route Access Modes: grant, public, degraded
- Disposition: `degraded`
- Final Status: `error`
- Final Confidence: `none`
- Source Identity: `exact-unavailable`

## Selected Attempt

- Stage: `domain-specific-route`
- Tool: `twitter-oembed`
- Status: `error`
- Confidence: `none`

## Acquisition Trace

- `direct-public-fetch` via `direct`: captcha / none
- `domain-specific-route` via `twitter-syndication`: error / none (fetch-failed) error=live-fetch-not-enabled
- `domain-specific-route` via `twitter-oembed`: error / none (fetch-failed) error=live-fetch-not-enabled
- `archive-or-cache` via `direct`: skipped / none (not-implemented)
- `clean-stop` via `direct`: skipped / none (terminal-state-recorded)

## Open Gaps

- `domain-specific-route` via `twitter-syndication`: error / none (fetch-failed) error=live-fetch-not-enabled
- `domain-specific-route` via `twitter-oembed`: error / none (fetch-failed) error=live-fetch-not-enabled
- `archive-or-cache` via `direct`: skipped / none (not-implemented)
- `clean-stop` via `direct`: skipped / none (terminal-state-recorded)

## Source Resolution

- Verdict: `exact-unavailable`
- Terminal State: `authenticated-browser-required`
- Required Capability: `operator-approved live X route, authenticated browser/profile, or exact-source provider`
- Next Owner: `Charness gather/browser/provider capability`

## Source Details

- Reason: `fetch-failed`

## Trace JSON

```json
{
  "source_url": "https://x.com/jenzhuscott/status/2063032701087883647/",
  "route": {
    "input_url": "https://x.com/jenzhuscott/status/2063032701087883647/",
    "normalized_host": "x.com",
    "route_id": "twitter-syndication",
    "route_family": "public-api",
    "summary": "Use search for discovery, then prefer Syndication API or oEmbed over raw page fetch.",
    "required_tools": [],
    "access_modes": [
      "grant",
      "public",
      "degraded"
    ],
    "fallback_order": [
      "direct-public-fetch",
      "domain-specific-route",
      "defuddle-reader-extraction",
      "agent-browser-render-recon",
      "agent-browser-network-recon",
      "reader-or-metadata-fallback",
      "archive-or-cache",
      "clean-stop"
    ],
    "acquisition_plan": [
      {
        "stage_id": "direct-public-fetch",
        "tool_id": null,
        "when": "Start here for public URLs unless a stronger domain route is known.",
        "proof": "classify-fetch-response"
      },
      {
        "stage_id": "domain-specific-route",
        "tool_id": null,
        "when": "Use the declared route before generic browser or reader fallbacks.",
        "proof": "route-specific structured output"
      },
      {
        "stage_id": "archive-or-cache",
        "tool_id": null,
        "when": "Use only when a stale or cached source still honestly answers the request.",
        "proof": "archive/cache source identity and freshness caveat"
      },
      {
        "stage_id": "clean-stop",
        "tool_id": null,
        "when": "Stop when access, auth, challenge, or confidence gaps remain.",
        "proof": "recorded failure mode and missing capability"
      }
    ],
    "notes": [
      "Raw fetch is often blocked or incomplete.",
      "Syndication helps for timelines; oEmbed helps when the exact post URL is known."
    ]
  },
  "disposition": "degraded",
  "attempts": [
    {
      "stage_id": "direct-public-fetch",
      "tool_id": null,
      "status": "captcha",
      "confidence": "none",
      "elapsed_s": 0.93,
      "output_chars": 285575,
      "classification": {
        "status": "captcha",
        "confidence": "none",
        "text_length": 263080,
        "matched_signals": [
          "robot"
        ],
        "signals": [
          "captcha"
        ],
        "proof": [],
        "proof_errors": [],
        "fallback_candidates": [
          "agent-browser-render",
          "clean-stop"
        ],
        "recommended_next_step": "Try the next fallback route or stop with the bot-block noted."
      }
    },
    {
      "stage_id": "domain-specific-route",
      "tool_id": "twitter-syndication",
      "status": "error",
      "confidence": "none",
      "elapsed_s": 0.0,
      "output_chars": 0,
      "error": "live-fetch-not-enabled",
      "details": {
        "endpoint": "https://cdn.syndication.twimg.com/tweet-result?id=2063032701087883647&lang=en",
        "kind": "syndication",
        "requested_status_id": "2063032701087883647",
        "reason": "fetch-failed"
      }
    },
    {
      "stage_id": "domain-specific-route",
      "tool_id": "twitter-oembed",
      "status": "error",
      "confidence": "none",
      "elapsed_s": 0.0,
      "output_chars": 0,
      "error": "live-fetch-not-enabled",
      "details": {
        "endpoint": "https://publish.twitter.com/oembed?url=https%3A%2F%2Fx.com%2Fjenzhuscott%2Fstatus%2F2063032701087883647&omit_script=1",
        "kind": "oembed",
        "requested_status_id": "2063032701087883647",
        "reason": "fetch-failed"
      }
    },
    {
      "stage_id": "archive-or-cache",
      "tool_id": null,
      "status": "skipped",
      "confidence": "none",
      "elapsed_s": 0.0,
      "output_chars": 0,
      "details": {
        "reason": "not-implemented"
      }
    },
    {
      "stage_id": "clean-stop",
      "tool_id": null,
      "status": "skipped",
      "confidence": "none",
      "elapsed_s": 0.0,
      "output_chars": 0,
      "details": {
        "reason": "terminal-state-recorded"
      }
    }
  ],
  "selected_attempt": {
    "stage_id": "domain-specific-route",
    "tool_id": "twitter-oembed",
    "status": "error",
    "confidence": "none",
    "elapsed_s": 0.0,
    "output_chars": 0,
    "error": "live-fetch-not-enabled",
    "details": {
      "endpoint": "https://publish.twitter.com/oembed?url=https%3A%2F%2Fx.com%2Fjenzhuscott%2Fstatus%2F2063032701087883647&omit_script=1",
      "kind": "oembed",
      "requested_status_id": "2063032701087883647",
      "reason": "fetch-failed"
    }
  },
  "final_status": "error",
  "final_confidence": "none",
  "source_identity": "exact-unavailable",
  "source_resolution": {
    "verdict": "exact-unavailable",
    "terminal_state": "authenticated-browser-required",
    "required_capability": "operator-approved live X route, authenticated browser/profile, or exact-source provider",
    "next_owner": "Charness gather/browser/provider capability"
  }
}
```
