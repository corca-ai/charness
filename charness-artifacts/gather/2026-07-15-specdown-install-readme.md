# Gathered Public URL

- Source: https://raw.githubusercontent.com/corca-ai/specdown/main/README.md
- Access Mode: support/web-fetch public route
- Content Persistence: `extracted`
- Route: `direct-then-fallback`
- Route Family: `public`
- Route Access Modes: grant, public, degraded
- Disposition: `success`
- Final Status: `success`
- Final Confidence: `strong`
- Source Identity: `not-applicable`

## Selected Attempt

- Stage: `direct-public-fetch`
- Tool: `direct`
- Status: `success`
- Confidence: `strong`

## Acquisition Trace

- `direct-public-fetch` via `direct`: success / strong
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

## Extracted Content

- Source Stage: `direct-public-fetch`
- Format: `text`
- Chars: `1474`
- Original Chars: `1474`
- Truncated: `False`

````text
# specdown Executable specifications in Markdown. One document is both a readable spec and a runnable test suite. ## Quick Start ```sh specdown init # scaffold a new project specdown run # execute specs and generate reports ``` ## Install ### Binary (recommended) ```sh curl -sSfL https://raw.githubusercontent.com/corca-ai/specdown/main/install.sh | sh ``` Installs to `/usr/local/bin`, or `~/.local/bin` if `/usr/local/bin` is not writable. Ensure the install directory is on your `PATH`. Or download directly from [Releases](https://github.com/corca-ai/specdown/releases/latest). ### go install ```sh go install github.com/corca-ai/specdown/cmd/specdown@latest ``` ### Homebrew ```sh brew install corca-ai/tap/specdown ``` ### From source ```sh go build -o bin/specdown ./cmd/specdown ``` ### Verify installation ```sh specdown version ``` ## Documentation - [Overview](specs/overview.md) — install, first spec, and why specdown exists - [Self-Spec](specs/index.md) — the executable reference - [Live Report](https://corca-ai.github.io/specdown/) — self-spec execution results - [Best Practices](specs/best-practices.md) — patterns, pitfalls, and anti-patterns - [Build & Run](docs/build.md) — building from source - [Agent Guide](AGENTS.md) — project layout, working rules, and conventions ## Example See [examples/pocket-board/](examples/pocket-board/) for a working project that uses shell blocks and Alloy models without any custom adapters. ## License [MIT](LICENSE)
````

## Trace JSON

```json
{
  "source_url": "https://raw.githubusercontent.com/corca-ai/specdown/main/README.md",
  "route": {
    "input_url": "https://raw.githubusercontent.com/corca-ai/specdown/main/README.md",
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
      "confidence": "strong",
      "elapsed_s": 0.016,
      "output_chars": 1512,
      "classification": {
        "status": "success",
        "confidence": "strong",
        "text_length": 1474,
        "matched_signals": [
          "text:go install github.com/corca-ai/specdown/cmd/specdown@latest"
        ],
        "signals": [
          "positive-proof"
        ],
        "proof": [
          {
            "type": "text",
            "value": "go install github.com/corca-ai/specdown/cmd/specdown@latest"
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
    "confidence": "strong",
    "elapsed_s": 0.016,
    "output_chars": 1512,
    "classification": {
      "status": "success",
      "confidence": "strong",
      "text_length": 1474,
      "matched_signals": [
        "text:go install github.com/corca-ai/specdown/cmd/specdown@latest"
      ],
      "signals": [
        "positive-proof"
      ],
      "proof": [
        {
          "type": "text",
          "value": "go install github.com/corca-ai/specdown/cmd/specdown@latest"
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
