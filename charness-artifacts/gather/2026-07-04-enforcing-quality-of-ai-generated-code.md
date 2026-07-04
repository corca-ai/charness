# Gathered Public URL

- Source: https://wiki.g15e.com/pages/Enforcing%20the%20quality%20of%20AI-generated%20code.md
- Access Mode: support/web-fetch public route
- Content Persistence: `none`
- Route: `direct-then-fallback`
- Route Family: `public`
- Route Access Modes: grant, public, degraded
- Disposition: `success`
- Final Status: `success`
- Final Confidence: `weak`
- Source Identity: `not-applicable`

## Selected Attempt

- Stage: `direct-public-fetch`
- Tool: `direct`
- Status: `success`
- Confidence: `weak`

## Acquisition Trace

- `direct-public-fetch` via `direct`: success / weak
- `impersonated-public-fetch` via `curl_cffi`: skipped / none (prior-stage-sufficient)
- `defuddle-reader-extraction` via `defuddle`: skipped / none (prior-stage-sufficient)
- `patchright-render-recon` via `patchright`: skipped / none (prior-stage-sufficient)
- `patchright-network-recon` via `patchright`: skipped / none (prior-stage-sufficient)
- `agent-browser-render-recon` via `agent-browser`: skipped / none (prior-stage-sufficient)
- `agent-browser-network-recon` via `agent-browser`: skipped / none (prior-stage-sufficient)
- `archive-or-cache` via `direct`: skipped / none (prior-stage-sufficient)
- `clean-stop` via `direct`: skipped / none (prior-stage-sufficient)

## Open Gaps

- None recorded.

## Trace JSON

```json
{
  "source_url": "https://wiki.g15e.com/pages/Enforcing%20the%20quality%20of%20AI-generated%20code.md",
  "route": {
    "input_url": "https://wiki.g15e.com/pages/Enforcing%20the%20quality%20of%20AI-generated%20code.md",
    "normalized_host": "wiki.g15e.com",
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
      "impersonated-public-fetch",
      "defuddle-reader-extraction",
      "patchright-render-recon",
      "patchright-network-recon",
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
        "stage_id": "impersonated-public-fetch",
        "tool_id": "curl_cffi",
        "when": "Retry public HTML with browser-like TLS/HTTP impersonation before paying browser-render cost.",
        "proof": "classify-fetch-response plus impersonation profile"
      },
      {
        "stage_id": "defuddle-reader-extraction",
        "tool_id": "defuddle",
        "when": "Use for article-like public pages when direct HTML is weak, cluttered, or partial.",
        "proof": "clean markdown plus source URL and classifier confidence"
      },
      {
        "stage_id": "patchright-render-recon",
        "tool_id": "patchright",
        "when": "Use a headless Patchright Chromium render when fetch/reader paths are blocked, JS-rendered, or unclear.",
        "proof": "headless rendered body text and access mode"
      },
      {
        "stage_id": "patchright-network-recon",
        "tool_id": "patchright",
        "when": "For collection intent, record public-looking /api/, /graphql, or .json requests seen by headless Patchright.",
        "proof": "network request candidates; no clicks, form submits, or login bypass"
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
      "confidence": "weak",
      "elapsed_s": 0.466,
      "output_chars": 2890,
      "classification": {
        "status": "success",
        "confidence": "weak",
        "text_length": 2858,
        "matched_signals": [],
        "signals": [
          "long-text"
        ],
        "proof": [],
        "proof_errors": [],
        "fallback_candidates": [],
        "recommended_next_step": "Use the content as a source and preserve the retrieval method."
      }
    },
    {
      "stage_id": "impersonated-public-fetch",
      "tool_id": "curl_cffi",
      "status": "skipped",
      "confidence": "none",
      "elapsed_s": 0.0,
      "output_chars": 0,
      "details": {
        "reason": "prior-stage-sufficient"
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
      "stage_id": "patchright-render-recon",
      "tool_id": "patchright",
      "status": "skipped",
      "confidence": "none",
      "elapsed_s": 0.0,
      "output_chars": 0,
      "details": {
        "reason": "prior-stage-sufficient"
      }
    },
    {
      "stage_id": "patchright-network-recon",
      "tool_id": "patchright",
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
    "confidence": "weak",
    "elapsed_s": 0.466,
    "output_chars": 2890,
    "classification": {
      "status": "success",
      "confidence": "weak",
      "text_length": 2858,
      "matched_signals": [],
      "signals": [
        "long-text"
      ],
      "proof": [],
      "proof_errors": [],
      "fallback_candidates": [],
      "recommended_next_step": "Use the content as a source and preserve the retrieval method."
    }
  },
  "final_status": "success",
  "final_confidence": "weak"
}
```

## Captured Content (2026-07-04, direct fetch)

Source article: "Enforcing the quality of AI-generated code" (wiki.g15e.com). Key claims, preserved for quality-gate design decisions:

1. Agentic/vibe coding degrades code quality; quality still matters in the AI era. Compose quantitative quality tools so the AI's cognitive niche (the harness) auto-manages quality.
2. Endorsed tool combination (JS examples; analogues per language): strict static type checks; linter constraints including MAX FILE LENGTH, MAX FUNCTION LENGTH, max statements, cognitive-complexity limits, switch exhaustiveness, no magic numbers; dependency-boundary enforcement (dependency-cruiser, import limits); CODE DUPLICATION as an error (jscpd; nose also catches behavioral clones); TEST COVERAGE floors; DEAD CODE detection (knip) because agents rarely delete code; TEST-TO-PRODUCTION CODE RATIO caps (e.g. 100-120%, tokei) because AI overproduces duplicate-path tests; MUTATION TESTING on a schedule (e.g. 12h, recent files), ratcheting the score up gradually.
3. COMBINATION IS THE POINT: coverage without a test/prod ratio cap -> unbounded test count; dedup pressure without cognitive-complexity limits -> unbounded logic complexity. Tools must counterbalance each other's evasion modes.
4. Adopt gradually: not every tool at once; start thresholds loose and ratchet.

Implication recorded for charness gate policy: deterministic quality floors of these classes (length caps, duplication, coverage, dead code, test/prod ratio, mutation score) are operator-endorsed teeth against AI-specific failure modes even on reversible work — a P1 demotion of such a gate requires operator sign-off, not just the reversible-work default.
