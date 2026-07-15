# Gathered Public URL

- Source: https://raw.githubusercontent.com/gitleaks/gitleaks/master/go.mod
- Access Mode: support/web-fetch public route
- Content Persistence: `extracted`
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

## Extracted Content

- Source Stage: `direct-public-fetch`
- Format: `text`
- Chars: `3466`
- Original Chars: `3466`
- Truncated: `False`

```text
module github.com/zricethezav/gitleaks/v8 go 1.24.11 require ( github.com/BobuSumisu/aho-corasick v1.0.3 github.com/Masterminds/sprig/v3 v3.3.0 github.com/charmbracelet/lipgloss v0.5.0 github.com/fatih/semgroup v1.2.0 github.com/gitleaks/go-gitdiff v0.9.1 github.com/google/go-cmp v0.7.0 github.com/h2non/filetype v1.1.3 github.com/hashicorp/go-version v1.7.0 github.com/mholt/archives v0.1.5 github.com/rs/zerolog v1.33.0 github.com/spf13/cobra v1.9.1 github.com/spf13/viper v1.19.0 github.com/stretchr/testify v1.10.0 golang.org/x/exp v0.0.0-20250218142911-aa4b98e5adaa ) require ( dario.cat/mergo v1.0.1 // indirect github.com/Masterminds/goutils v1.1.1 // indirect github.com/Masterminds/semver/v3 v3.3.0 // indirect github.com/STARRY-S/zip v0.2.3 // indirect github.com/andybalholm/brotli v1.2.0 // indirect github.com/aymanbagabas/go-osc52/v2 v2.0.1 // indirect github.com/bodgit/plumbing v1.3.0 // indirect github.com/bodgit/sevenzip v1.6.1 // indirect github.com/bodgit/windows v1.0.1 // indirect github.com/dsnet/compress v0.0.2-0.20230904184137-39efe44ab707 // indirect github.com/google/uuid v1.6.0 // indirect github.com/hashicorp/golang-lru/v2 v2.0.7 // indirect github.com/huandu/xstrings v1.5.0 // indirect github.com/klauspost/compress v1.18.0 // indirect github.com/klauspost/pgzip v1.2.6 // indirect github.com/lucasb-eyer/go-colorful v1.2.0 // indirect github.com/mattn/go-colorable v0.1.14 // indirect github.com/mattn/go-isatty v0.0.20 // indirect github.com/mattn/go-runewidth v0.0.14 // indirect github.com/mikelolasagasti/xz v1.0.1 // indirect github.com/minio/minlz v1.0.1 // indirect github.com/mitchellh/copystructure v1.2.0 // indirect github.com/mitchellh/reflectwalk v1.0.2 // indirect github.com/muesli/reflow v0.2.1-0.20210115123740-9e1d0d53df68 // indirect github.com/muesli/termenv v0.15.1 // indirect github.com/nwaples/rardecode/v2 v2.2.0 // indirect github.com/pelletier/go-toml/v2 v2.2.3 // indirect github.com/pierrec/lz4/v4 v4.1.22 // indirect github.com/rivo/uniseg v0.2.0 // indirect github.com/sagikazarmark/locafero v0.7.0 // indirect github.com/sagikazarmark/slog-shim v0.1.0 // indirect github.com/shopspring/decimal v1.4.0 // indirect github.com/sorairolake/lzip-go v0.3.8 // indirect github.com/sourcegraph/conc v0.3.0 // indirect github.com/tetratelabs/wazero v1.9.0 // indirect github.com/ulikunitz/xz v0.5.15 // indirect github.com/wasilibs/wazero-helpers v0.0.0-20240620070341-3dff1577cd52 // indirect go.uber.org/multierr v1.11.0 // indirect go4.org v0.0.0-20230225012048-214862532bf5 // indirect golang.org/x/crypto v0.35.0 // indirect ) require ( github.com/davecgh/go-spew v1.1.2-0.20180830191138-d8f796af33cc // indirect github.com/fsnotify/fsnotify v1.8.0 // indirect github.com/hashicorp/hcl v1.0.0 // indirect github.com/inconshreveable/mousetrap v1.1.0 // indirect github.com/lucasjones/reggen v0.0.0-20200904144131-37ba4fa293bb github.com/magiconair/properties v1.8.9 // indirect github.com/mitchellh/mapstructure v1.5.0 // indirect github.com/pmezard/go-difflib v1.0.1-0.20181226105442-5d4384ee4fb2 // indirect github.com/spf13/afero v1.15.0 // indirect github.com/spf13/cast v1.7.1 // indirect github.com/spf13/pflag v1.0.6 // indirect github.com/subosito/gotenv v1.6.0 // indirect github.com/wasilibs/go-re2 v1.9.0 golang.org/x/sync v0.17.0 // indirect golang.org/x/sys v0.30.0 // indirect golang.org/x/text v0.29.0 // indirect gopkg.in/ini.v1 v1.67.0 // indirect gopkg.in/yaml.v3 v3.0.1 // indirect )
```

## Trace JSON

```json
{
  "source_url": "https://raw.githubusercontent.com/gitleaks/gitleaks/master/go.mod",
  "route": {
    "input_url": "https://raw.githubusercontent.com/gitleaks/gitleaks/master/go.mod",
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
      "confidence": "weak",
      "elapsed_s": 0.365,
      "output_chars": 3543,
      "classification": {
        "status": "success",
        "confidence": "weak",
        "text_length": 3466,
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
    "elapsed_s": 0.365,
    "output_chars": 3543,
    "classification": {
      "status": "success",
      "confidence": "weak",
      "text_length": 3466,
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
