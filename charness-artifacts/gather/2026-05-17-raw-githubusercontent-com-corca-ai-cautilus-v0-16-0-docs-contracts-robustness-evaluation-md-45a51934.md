# Gathered Public URL

- Source: https://raw.githubusercontent.com/corca-ai/cautilus/v0.16.0/docs/contracts/robustness-evaluation.md
- Access Mode: support/web-fetch public route
- Route: `direct-then-fallback`
- Route Family: `public`
- Route Access Modes: grant, public, degraded
- Disposition: `success`
- Final Status: `success`
- Final Confidence: `strong`

## Selected Attempt

- Stage: `direct-public-fetch`
- Tool: `direct`
- Status: `success`
- Confidence: `strong`

## Acquisition Trace

- `direct-public-fetch` via `direct`: success / strong
- `defuddle-reader-extraction` via `defuddle`: skipped / none (prior-stage-sufficient)
- `agent-browser-render-recon` via `agent-browser`: skipped / none (prior-stage-sufficient)
- `agent-browser-network-recon` via `agent-browser`: skipped / none (prior-stage-sufficient)
- `archive-or-cache` via `direct`: skipped / none (prior-stage-sufficient)
- `clean-stop` via `direct`: skipped / none (prior-stage-sufficient)

## Open Gaps

- None recorded.

## Trace JSON

```json
{
  "source_url": "https://raw.githubusercontent.com/corca-ai/cautilus/v0.16.0/docs/contracts/robustness-evaluation.md",
  "route": {
    "input_url": "https://raw.githubusercontent.com/corca-ai/cautilus/v0.16.0/docs/contracts/robustness-evaluation.md",
    "normalized_host": "raw.githubusercontent.com",
    "route_id": "direct-then-fallback",
    "route_family": "public",
    "summary": "Try direct public fetch first, then reader, metadata-only, and archive fallback in order.",
    "required_tools": [
      "curl"
    ],
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
        "stage_id": "defuddle-reader-extraction",
        "tool_id": "defuddle",
        "when": "Use for article-like public pages when direct HTML is weak, cluttered, or partial.",
        "proof": "clean markdown plus source URL and classifier confidence"
      },
      {
        "stage_id": "agent-browser-render-recon",
        "tool_id": "agent-browser",
        "when": "Use for JS-rendered pages, empty SPA shells, repeated challenge signals, or weak cleaner output.",
        "proof": "rendered body text/html and access mode"
      },
      {
        "stage_id": "agent-browser-network-recon",
        "tool_id": "agent-browser",
        "when": "Use for list/collection intent to record public-looking /api/, /graphql, or .json request candidates.",
        "proof": "network request candidates; no clicks, form submits, or login bypass"
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
      "Do not skip the direct path when the page may still be readable as plain HTML."
    ]
  },
  "disposition": "success",
  "attempts": [
    {
      "stage_id": "direct-public-fetch",
      "tool_id": null,
      "status": "success",
      "confidence": "strong",
      "elapsed_s": 0.272,
      "output_chars": 8640,
      "classification": {
        "status": "success",
        "confidence": "strong",
        "text_length": 8491,
        "matched_signals": [
          "regex:robustness evaluation"
        ],
        "signals": [
          "positive-proof"
        ],
        "proof": [
          {
            "type": "regex",
            "value": "robustness evaluation"
          }
        ],
        "proof_errors": [],
        "fallback_candidates": [
          "clean-stop"
        ],
        "recommended_next_step": "Use the content as a source and preserve the matched proof."
      }
    },
    {
      "stage_id": "defuddle-reader-extraction",
      "tool_id": "defuddle",
      "status": "skipped",
      "confidence": "none",
      "elapsed_s": 0.0,
      "output_chars": 0,
      "details": {
        "reason": "prior-stage-sufficient"
      }
    },
    {
      "stage_id": "agent-browser-render-recon",
      "tool_id": "agent-browser",
      "status": "skipped",
      "confidence": "none",
      "elapsed_s": 0.0,
      "output_chars": 0,
      "details": {
        "reason": "prior-stage-sufficient"
      }
    },
    {
      "stage_id": "agent-browser-network-recon",
      "tool_id": "agent-browser",
      "status": "skipped",
      "confidence": "none",
      "elapsed_s": 0.0,
      "output_chars": 0,
      "details": {
        "reason": "prior-stage-sufficient"
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
        "reason": "prior-stage-sufficient"
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
        "reason": "prior-stage-sufficient"
      }
    }
  ],
  "selected_attempt": {
    "stage_id": "direct-public-fetch",
    "tool_id": null,
    "status": "success",
    "confidence": "strong",
    "elapsed_s": 0.272,
    "output_chars": 8640,
    "classification": {
      "status": "success",
      "confidence": "strong",
      "text_length": 8491,
      "matched_signals": [
        "regex:robustness evaluation"
      ],
      "signals": [
        "positive-proof"
      ],
      "proof": [
        {
          "type": "regex",
          "value": "robustness evaluation"
        }
      ],
      "proof_errors": [],
      "fallback_candidates": [
        "clean-stop"
      ],
      "recommended_next_step": "Use the content as a source and preserve the matched proof."
    }
  },
  "final_status": "success",
  "final_confidence": "strong"
}
```
