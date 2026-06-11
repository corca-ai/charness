# Gathered Public URL

- Source: https://youtu.be/haK1KoQWm18
- Access Mode: support/web-fetch public route
- Content Persistence: `none`
- Route: `yt-dlp-metadata`
- Route Family: `binary`
- Route Access Modes: binary, public, degraded
- Disposition: `degraded`
- Final Status: `error`
- Final Confidence: `none`
- Source Identity: `youtube-unavailable`

## Selected Attempt

- Stage: `domain-specific-route`
- Tool: `yt-dlp`
- Status: `error`
- Confidence: `none`

## Acquisition Trace

- `direct-public-fetch` via `direct`: captcha / none
- `domain-specific-route` via `yt-dlp`: error / none (missing-tool) error=missing-tool:yt-dlp
- `archive-or-cache` via `direct`: skipped / none (not-implemented)
- `clean-stop` via `direct`: skipped / none (terminal-state-recorded)

## Open Gaps

- `domain-specific-route` via `yt-dlp`: error / none (missing-tool) error=missing-tool:yt-dlp
- `archive-or-cache` via `direct`: skipped / none (not-implemented)
- `clean-stop` via `direct`: skipped / none (terminal-state-recorded)

## Source Details

- Video Id: `haK1KoQWm18`
- Reason: `missing-tool`

## Trace JSON

```json
{
  "source_url": "https://youtu.be/haK1KoQWm18",
  "route": {
    "input_url": "https://youtu.be/haK1KoQWm18",
    "normalized_host": "youtu.be",
    "route_id": "yt-dlp-metadata",
    "route_family": "binary",
    "summary": "Prefer `yt-dlp` metadata, subtitle, or playlist paths for media sites.",
    "required_tools": [
      "yt-dlp"
    ],
    "access_modes": [
      "binary",
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
        "tool_id": "yt-dlp",
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
      "Use metadata-only paths before any download path.",
      "Subtitle or comment extraction remains route-specific and may fail per site."
    ]
  },
  "disposition": "degraded",
  "attempts": [
    {
      "stage_id": "direct-public-fetch",
      "tool_id": null,
      "status": "captcha",
      "confidence": "none",
      "elapsed_s": 1.032,
      "output_chars": 1390408,
      "classification": {
        "status": "captcha",
        "confidence": "none",
        "text_length": 1357688,
        "matched_signals": [
          "captcha",
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
      "tool_id": "yt-dlp",
      "status": "error",
      "confidence": "none",
      "elapsed_s": 0.0,
      "output_chars": 0,
      "error": "missing-tool:yt-dlp",
      "details": {
        "reason": "missing-tool",
        "video_id": "haK1KoQWm18"
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
    "tool_id": "yt-dlp",
    "status": "error",
    "confidence": "none",
    "elapsed_s": 0.0,
    "output_chars": 0,
    "error": "missing-tool:yt-dlp",
    "details": {
      "reason": "missing-tool",
      "video_id": "haK1KoQWm18"
    }
  },
  "final_status": "error",
  "final_confidence": "none",
  "source_identity": "youtube-unavailable"
}
```
