# Gathered Public URL

- Source: https://wiki.g15e.com/pages/Capabilities%20over%20features.md
- Access Mode: support/web-fetch public route
- Content Persistence: `none`
- Route: `direct-then-fallback`
- Route Family: `public`
- Route Access Modes: grant, public, degraded
- Disposition: `success`
- Final Status: `success`
- Final Confidence: `weak`
- Source Identity: `not-applicable`

## Captured Content (2026-06-18, direct fetch)

> 제품이 할 수 있는 일의 범위 또는 가능성(capabilities)과 제품의 기능이 얼마나
> 많은지(features)는 별개다.

**기능과 가능성.** 좋은 제품은 최소한의 기능으로 최대한의 가능성을 만들어야 한다.
한 가지 방법은 기능을 되도록 **직교적(orthogonal)**으로 만들고 기능 간 **조합
가능성(composability)**을 높이는 것. 기획자들이 "기능"을 끝없이 추가하기보다
**가능성에 집중**하면 배우기 쉬운(learnable) 제품을 만들 수 있다 — 뛰어난 사용성의
필수 요소.

**기능 때문에 훼손되는 사용성.** 기능은 사용성을 해치는 주범:

- 새 기능 추가는 쉽지만 제거는 어렵다 — 기능은 사용자와의 **약속**이기 때문. 따라서
  기능 추가는 극도로 신중하게.
- 기능이 많을수록 배울 게 많아져 **학습가능성이 낮아진다**.
- 만드는 사람은 기존 기능에 익숙해 새 기능 추가를 가볍게 보지만, 처음 접하는
  사용자는 **압도된다** (고인물 게임의 극악 난이도가 신규 진입을 막는 현상).
- 직교성 낮은 기능이 쌓이면 사용자는 같은 과업에 **여러 방법 중 무엇을 쓸지
  고민**하고 잘못 선택해 구렁텅이에 빠진다 (옵시디언의 폴더+태그+링크 공존 비판).
  이는 **디자인의 단조성(one obvious way)**에 위배.

**참고:** Donald Norman, *"Simplicity is not the answer"* — 단순함 자체가 답이
아니라, **가능성(capability) + 학습가능성**이 목표.

## Selected Attempt

- Stage: `direct-public-fetch`
- Tool: `direct`
- Status: `success`
- Confidence: `weak`

## Acquisition Trace

- `direct-public-fetch` via `direct`: success / weak
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
  "source_url": "https://wiki.g15e.com/pages/Capabilities%20over%20features.md",
  "route": {
    "input_url": "https://wiki.g15e.com/pages/Capabilities%20over%20features.md",
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
      "confidence": "weak",
      "elapsed_s": 0.461,
      "output_chars": 1528,
      "classification": {
        "status": "success",
        "confidence": "weak",
        "text_length": 1508,
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
    "confidence": "weak",
    "elapsed_s": 0.461,
    "output_chars": 1528,
    "classification": {
      "status": "success",
      "confidence": "weak",
      "text_length": 1508,
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
